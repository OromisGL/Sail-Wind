import pytest
import mongomock

@pytest.fixture(autouse=True)
def replace_mongodb(monkeypatch):
    db = mongomock.MongoClient()
    def fake_mongo():
        g.client = db
        g.db = db.test
        return g.db
    monkeypatch.setattr('db.get_db', fake_mongo)