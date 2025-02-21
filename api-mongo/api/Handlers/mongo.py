from fastapi import Request
from fastapi.responses import JSONResponse
from pymongo import MongoClient
import os

class MongoHandler():
    def __init__(self) -> None:
        # Get needed env variables
        mongo_cli           = os.getenv('MONGO_CLIENT_DB')
        mongo_db_name       = os.getenv('MONGO_DATABASE')
        mongo_collection_ok = os.getenv('MONGO_COLLECTION_OK')
        mongo_collection_ko = os.getenv('MONGO_COLLECTION_KO')
        mongo_historic      = os.getenv('MONGO_HISTORIC')

        # Connect to Mongo Database
        client = MongoClient(mongo_cli)

        # Select Database
        db = client[mongo_db_name]

        # Get all collections
        self.collec_ok       = db[mongo_collection_ok]
        self.collec_ko       = db[mongo_collection_ko]
        self.collec_historic = db[mongo_historic] 


    def collection_ok(self) -> dict:
        cursor = self.collec_ok.find({}, {'_id': 0})
        return {'data': list(cursor)}
    
    def collection_ko(self) -> dict:
        cursor = self.collec_ko.find({}, {'_id': 0})
        return {'data': list(cursor)}
    
    def history(self) -> dict:
        cursor = self.collec_historic.find({}, {'_id': 0})
        return {'data': list(cursor)}