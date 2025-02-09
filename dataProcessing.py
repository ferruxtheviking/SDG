import os
import json
from pathlib import Path
from datetime import datetime
from parameters import validation_functions, formats, savemode

def process_data(metadata, data):
    # Search in metadata the transformations to do
    validation_transformation = None
    for flow in metadata.get("dataflows", []):
        for transformation in flow.get("transformations", []):
            if transformation.get("type") == "validate_fields":
                validation_transformation = transformation
                break
        if validation_transformation:
            break

    # Get the validations
    if validation_transformation:
        validations = validation_transformation["params"]["validations"]
    else:
        validations = []

    standard_ok = []
    standard_ko = []

    # Check each record
    for record in input_data:
        errors = {}
        # Check if there's any validation in this field
        for rule in validations:
            field = rule["field"]
            for validation_name in rule["validations"]:
                validate_func = validation_functions.get(validation_name)
                if validate_func:
                    # Apply validation in field
                    if not validate_func(record.get(field)):
                        errors.setdefault(field, []).append(f"Fail validation: {validation_name}")
                else:
                    errors.setdefault(field, []).append(f"Unknown validation: {validation_name}")
        # Clasify records
        if errors:
            # Record KO, adding error field
            record["arraycoderrorbyfield"] = errors
            standard_ko.append(record)
        else:
            # Record OK, adding current_timestamp
            record["dt"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            standard_ok.append(record)

    return standard_ok, standard_ko

def saveStandard(ok_data, ko_data, metadata):
    # Get and validate necessary parameters to save the OK and KO outputs
    # TODO Check uppercase and lowercase in format and saveMode
    for flow in metadata.get('dataflows', []):
        for sink in flow.get('sinks', []):
            if sink.get('input') == 'ok_with_date':
                ok_filename = sink.get('name')     if isinstance(sink.get('name')    , str)  else 'raw_ok'
                ok_paths    = sink.get('paths')    if isinstance(sink.get('paths')   , list) else ['/data/output/events/person'])
                ok_format   = sink.get('format')   if isinstance(sink.get('format')  , str)  else 'JSON'
                ok_savemode = sink.get('saveMode') if isinstance(sink.get('saveMode'), str)  else 'OVERWRITE'
            elif sink.get('input') == 'validation_ko':
                ko_filename = sink.get('name')     if isinstance(sink.get('name')    , str)  else 'validation_ko'
                ko_paths    = sink.get('paths')    if isinstance(sink.get('paths')   , list) else ['/data/output/discards/person'])
                ko_format   = sink.get('format')   if isinstance(sink.get('format')  , str)  else 'JSON'
                ko_savemode = sink.get('saveMode') if isinstance(sink.get('saveMode'), str)  else 'APPEND'

    # Save OK data in all paths
    for ok_path in ok_paths:
        ok_file = Path(ok_path) / f'{ok_filename}{formats.get(ok_format)}'
        os.makedirs(Path(ok_path), exist_ok=True)
        with open(ok_file, savemode.get(ok_savemode)) as f: # TODO Encodings? UTF-8
            json.dump(ok_data, f, indent=4)

    # Save KO data in all paths
    for ko_path in ko_paths:
        ko_file = Path(ko_path) / f'{ko_filename}{formats.get(ko_format)}'
        os.makedirs(Path(ko_path), exist_ok=True)
        with open(ko_file, savemode.get(ko_savemode)) as f:
            json.dump(ko_data, f, indent=4)

if __name__ == '__main__':
    # Read metadata
    with open('metadata.json', 'r') as file:
        metadata = json.load(file)

    # Input data
    with open('inputData.json', 'r') as file:
        input_data = json.load(file)

    ok_data, ko_data = process_data(metadata, input_data)

    # Save output
    saveStandard(ok_data, ko_data, metadata)
