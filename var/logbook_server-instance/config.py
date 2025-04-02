import os

class Config:
    DATABASE = "mongodb://localhost:27017/mydatabase"  # Default local MongoDB
    UPLOAD_PATH = os.environ.get('UPLOAD_PATH')


class TestingConfig(Config):
    TESTING = True
    DATABASE = {}  # Empty dict for mocking DB in tests