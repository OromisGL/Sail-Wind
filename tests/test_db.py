import pytest
from pymongo.errors import InvalidURI
from logbook_server.db import get_db

def test_init_db_command(runner, monkeypatch, app):
    with app.app_context():
        indexes = get_db().users.list_indexes()
        print(indexes)
        assert next(indexes, None) == None
        result = runner.invoke(args=['init-db'])
        assert 'Initialized' in result.output
        indexes = get_db().users.list_indexes()
        print(indexes)
        assert next(indexes, None) != None

def test_get_db(app):
    with app.app_context():
        db = get_db()
        assert db is get_db()
        db.users.find_one({'user_name': 'test'})