import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import tempfile

from ..main import app
from ..database import get_db
from ..models import Base

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(test_db):
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c

def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.json() == {"message": "Secure File Sharing System API"}

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "healthy"}

def test_ops_login_invalid(client):
    r = client.post("/ops/login", json={"username": "nope", "password": "bad"})
    assert r.status_code == 401

def test_client_signup(client):
    r = client.post("/client/signup", json={"username": "a", "email": "a@a.com", "password": "a", "user_type": "client"})
    assert r.status_code == 200

def test_client_signup_duplicate(client):
    client.post("/client/signup", json={"username": "b", "email": "b@b.com", "password": "b", "user_type": "client"})
    r = client.post("/client/signup", json={"username": "b", "email": "c@c.com", "password": "b", "user_type": "client"})
    assert r.status_code == 400

def test_client_signup_invalid_type(client):
    r = client.post("/client/signup", json={"username": "c", "email": "c@c.com", "password": "c", "user_type": "ops"})
    assert r.status_code == 400

def test_client_login_unverified(client):
    client.post("/client/signup", json={"username": "d", "email": "d@d.com", "password": "d", "user_type": "client"})
    r = client.post("/client/login", json={"username": "d", "password": "d"})
    assert r.status_code == 403

def test_file_upload_unauth(test_db):
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
        tmp.write(b"hi")
        tmp_path = tmp.name
    with TestClient(app) as c:
        try:
            with open(tmp_path, "rb") as f:
                r = c.post("/ops/upload", files={"file": f})
            assert r.status_code == 401
        finally:
            os.unlink(tmp_path)

def test_list_files_unauth(test_db):
    with TestClient(app) as c:
        r = c.get("/client/files")
    assert r.status_code == 401

def test_download_unauth(test_db):
    with TestClient(app) as c:
        r = c.post("/client/download/1")
    assert r.status_code == 401 