import os

class Config:
    DATABASE = "mongodb://localhost:27017/mydatabase"  # Default local MongoDB

class TestingConfig(Config):
    TESTING = True
    DATABASE = {}  # Empty dict for mocking DB in tests