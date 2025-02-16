import os
import json
from pathlib import Path
from datetime import datetime
from parameters import validation_functions, formats, savemode

def process_data(metadata: dict, input_data: dict) -> tuple[list, list]:
    '''
    Processes records by applying validations defined in the metadata.

    Args:
        metadata (dict): Dictionary containing metadata.
        input_data (list): List of records (dictionaries) to process.

    Returns:
        tuple: (valid_records, invalid_records)
            valid_records (list): Records that passed validations, with a timestamp.
            invalid_records (list): Records that failed validations, with error details.
    '''
    # Find validation transformation in metadata
    validation_transformation = next(
        (
            transformation
            for flow in metadata.get('dataflows', [])
            for transformation in flow.get('transformations', [])
            if transformation.get('type') == 'validate_fields'
        ),
        None
    )

    validations = (
        validation_transformation.get('params', {}).get('validations', [])
        if validation_transformation
        else []
    )

    valid_records = []
    invalid_records = []

    for record in input_data:
        errors = {}
        for rule in validations:
            field = rule['field']
            for validation_name in rule['validations']:
                validate_func = validation_functions.get(validation_name)
                if validate_func:
                    # Apply validation to field
                    if not validate_func(record.get(field)):
                        errors.setdefault(field, []).append(f'Validation failed: {validation_name}')
                else:
                    errors.setdefault(field, []).append(f'Unknown validation: {validation_name}')

        if errors:
            record['error_details'] = errors
            invalid_records.append(record)
        else:
            record['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            valid_records.append(record)

    return valid_records, invalid_records

def get_sink_config(metadata: dict, input_type: str) -> dict:
    '''
    Retrieves sink configuration from metadata for the specified input type.

    Args:
        metadata (dict): Dictionary containing metadata.
        input_type (str): Input type ('ok_with_date' or 'validation_ko').

    Returns:
        dict: Configuration with keys: filename, paths, format, and save_mode.
    '''
    for flow in metadata.get('dataflows', []):
            for sink in flow.get('sinks', []):
                if sink.get('input') == input_type:
                    return {
                        'filename': sink.get('name', ''),
                        'paths': sink.get('paths', []),
                        'format': sink.get('format', 'JSON'),
                        'save_mode': sink.get('saveMode', 'OVERWRITE')
                    }
    return None

def save_data(valid_data: list, invalid_data: list, metadata: dict) -> None:
    '''
    Saves processed data based on metadata configuration.

    Args:
        valid_data (list): Records that passed validations.
        invalid_data (list): Records that failed validations.
        metadata (dict): Dictionary containing metadata.
    '''
    valid_config = get_sink_config(metadata, 'ok_with_date')
    invalid_config = get_sink_config(metadata, 'validation_ko')

    # Save valid records in all configured paths
    for path in valid_config['paths']:
        file_path = Path(path) / f'{valid_config['filename']}{formats.get(valid_config['format'])}'
        os.makedirs(Path(path), exist_ok=True)
        with open(file_path, savemode.get(valid_config['save_mode'])) as f:
            json.dump(valid_data, f, indent=4)

    # Save invalid records in all configured paths
    for path in invalid_config['paths']:
        file_path = Path(path) / f'{invalid_config['filename']}{formats.get(invalid_config['format'])}'
        os.makedirs(Path(path), exist_ok=True)
        with open(file_path, savemode.get(invalid_config['save_mode'])) as f:
            json.dump(invalid_data, f, indent=4)

def get_input_data(metadata: dict) -> list:
    input_data = []
    for flow in metadata.get('dataflows', []):
        for source in flow.get('sources', []):
            file_path = Path(source.get('path','')) / f'{source.get('name','')}'
            try:
                with open(file_path, 'r') as f: # TODO Other types of formats??
                    input_data.extend(json.loads(line.strip()) for line in f if line.strip())
            except (json.JSONDecodeError, FileNotFoundError) as e:
                        print(f'Error processing file {file_path}: {e}')

    return input_data

def load_metadata():
    with open('metadata.json', 'r') as file:
        return json.load(file)
    
if __name__ == '__main__':
    # Load metadata
    with open('metadata.json', 'r') as file:
        metadata = json.load(file)

    # Load input data
    input_data = get_input_data(metadata)

    valid_data, invalid_data = process_data(metadata, input_data)
    # Save output data
    save_data(valid_data, invalid_data, metadata)
