import os
import json
from typing import Tuple, List
from pymongo import MongoClient
from pathlib import Path
from datetime import datetime
from parameters import validation_functions, formats, savemode

def load_input_data(metadata: dict) -> list:
    '''
    Gets the input data from metadata. It's located in one or more files.

    Args:
        metadata (dict): Dictionary containing metadata.

    Returns:
        input_data (list): Records in JSON format
    '''
    input_data = []
    for flow in metadata.get('dataflows', []):
        print(flow.get('sources'))
        for source in flow.get('sources', []):
            file_path = Path(source.get('path','')) / f'{source.get("name","")}'
            try:
                with open(file_path, 'r') as f: # TODO Other types of formats??
                    input_data.extend(json.loads(line.strip()) for line in f if line.strip())
            except (json.JSONDecodeError, FileNotFoundError) as e:
                        print(f'Error processing file {file_path}: {e}')

    return input_data

def load_input_data_parameters(input_data_raw: dict) -> list:
    '''
    Gets the input data from parameters in DAG config.

    Args:
        input_data_raw (dict): Dictionary containing JSON records

    Returns:
        input_data (list): Records in JSON format
    '''
    print(input_data_raw)
    print(type(input_data_raw))
    try:
        input_data = input_data_raw.get('source')
        if input_data and not isinstance(input_data, list):
            raise TypeError('The input is not a list')
        for idx, record in enumerate(input_data):
             if not isinstance(record, dict):
                raise TypeError(f"The element [{idx}] it's not JSON")
    except json.JSONDecodeError as e:
        raise TypeError(f'Error in JSON decoding: {e}')
    except TypeError as e:
        raise TypeError(f'Error: {e}')
         
    return input_data


def process_data(metadata: dict, input_data: dict) -> Tuple[List, List]:
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
            record['datetime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            valid_records.append(record)
            
    return valid_records, invalid_records


def save_data_mongo(valid_data: list, invalid_data: list) -> None:
    '''
    Connect to the MongoDB server and update both the valid and invalid data

    Args:
        valid_data (list): Records that passed validations.
        invalid_data (list): Records that failed validations.
    '''
    mongo_cli           = os.getenv('MONGO_CLIENT_DB')
    mongo_db_name       = os.getenv('MONGO_DATABASE')
    mongo_collection_ok = os.getenv('MONGO_COLLECTION_OK')
    mongo_collection_ko = os.getenv('MONGO_COLLECTION_KO')
    mongo_historic      = os.getenv('MONGO_HISTORIC')

    # Connect to Mongo Database
    client = MongoClient(mongo_cli)

    # Select Database
    db = client[mongo_db_name]

    # Get both collections # TODO Duplicated data
    collection_ok = db[mongo_collection_ok]
    collection_ko = db[mongo_collection_ko]
    if valid_data:
        collection_ok.insert_many(valid_data)
    if invalid_data:
        collection_ko.insert_many(invalid_data)

    # Insert historic data 
    historic_record = {
        'total_records'  : len(valid_data) + len(invalid_data),
        'valid_records'  : len(valid_data),
        'invalid_records': len(invalid_data),
        'datetime'       : datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    historic = db[mongo_historic]
    historic.insert_one(historic_record)
    
    return None


def save_data_disk(valid_data: list, invalid_data: list, metadata: dict) -> None:
    '''
    Saves processed data based on metadata configuration.

    Args:
        valid_data (list): Records that passed validations.
        invalid_data (list): Records that failed validations.
        metadata (dict): Dictionary containing metadata.
    '''
    valid_config   = get_sink_config(metadata, 'ok_with_date')
    invalid_config = get_sink_config(metadata, 'validation_ko')

    # Save valid records in all configured paths
    for path in valid_config['paths']: # TODO problems saving lists. If there was other data, there are going to be more lists in just one file
        file_path = Path(path) / f'{valid_config["filename"]}{formats.get(valid_config["format"])}'
        os.makedirs(Path(path), exist_ok=True)
        with open(file_path, savemode.get(valid_config['save_mode'])) as f:
            json.dump(valid_data, f, indent=4)

    # Save invalid records in all configured paths
    for path in invalid_config['paths']:
        file_path = Path(path) / f'{invalid_config["filename"]}{formats.get(invalid_config["format"])}'
        os.makedirs(Path(path), exist_ok=True)
        with open(file_path, savemode.get(invalid_config['save_mode'])) as f:
            json.dump(invalid_data, f, indent=4)


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