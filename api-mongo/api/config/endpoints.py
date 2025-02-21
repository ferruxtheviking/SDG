from fastapi import APIRouter
from Handlers.mongo import MongoHandler

# Initialize APIRouter
endpoints = APIRouter()

# Mongo endpoints
mongo = MongoHandler()
endpoints.add_api_route(path = '/collection_ok', endpoint = mongo.collection_ok, methods = ['GET'])
endpoints.add_api_route(path = '/collection_ko', endpoint = mongo.collection_ko, methods = ['GET'])
endpoints.add_api_route(path = '/history'      , endpoint = mongo.history      , methods = ['GET'])
