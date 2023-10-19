import pytest
import mongomock

@pytest.fixture(autouse=True)
def replace_mongodb(monkeypatch):
    db = mongomock.MongoClient()
    def fake_mongo():
        return db
    monkeypatch.setattr('db.getdb', fake_mongo)