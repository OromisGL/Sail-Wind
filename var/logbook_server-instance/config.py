import os
from pymongo import MongoClient

print("MONGO_URI:", os.getenv('MONGO_URI'))
class Config:
    DATABASE = "mongodb://root:example@localhost:27017/mydatabase?authSource=admin" # Default local MongoDB mongodb://localhost:27017/
    UPLOAD_PATH = os.environ.get('UPLOAD_PATH')


class TestingConfig(Config):
    TESTING = True
    DATABASE = {}  # Empty dict for mocking DB in tests