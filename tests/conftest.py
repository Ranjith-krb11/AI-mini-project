import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.database import Base, get_db
from main import app

# Use isolated SQLite test database
TEST_DB_PATH = os.path.join(os.getcwd(), "data", "test_app.db")
TEST_DB_URL = f"sqlite:///{TEST_DB_PATH}"

test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    # Create all tables before tests run
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield
    # Cleanup after test session completes
    Base.metadata.drop_all(bind=test_engine)
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except Exception:
            pass


@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def user1_auth(client):
    res = client.post("/api/auth/register", json={
        "name": "Alice Tester",
        "email": "alice.test@university.edu",
        "password": "Password123!"
    })
    if res.status_code == 201:
        token = res.json()["access_token"]
    else:
        login_res = client.post("/api/auth/login", json={
            "email": "alice.test@university.edu",
            "password": "Password123!"
        })
        token = login_res.json()["access_token"]
    
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    return {
        "headers": {"Authorization": f"Bearer {token}"},
        "user": me_res.json(),
        "token": token
    }


@pytest.fixture
def user2_auth(client):
    res = client.post("/api/auth/register", json={
        "name": "Bob Tester",
        "email": "bob.test@university.edu",
        "password": "Password123!"
    })
    if res.status_code == 201:
        token = res.json()["access_token"]
    else:
        login_res = client.post("/api/auth/login", json={
            "email": "bob.test@university.edu",
            "password": "Password123!"
        })
        token = login_res.json()["access_token"]
        
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    return {
        "headers": {"Authorization": f"Bearer {token}"},
        "user": me_res.json(),
        "token": token
    }


@pytest.fixture
def valid_pdf_bytes():
    """Generates a minimal valid PDF byte sequence with text stream."""
    return (
        b"%PDF-1.4\n"
        b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n"
        b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n"
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj\n"
        b"4 0 obj << /Length 72 >> stream\n"
        b"BT /F1 12 Tf 100 700 Td (Virtual Memory and Process Scheduling Operating Systems) Tj ET\n"
        b"endstream\nendobj\n"
        b"5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n"
        b"xref\n0 6\n0000000000 65535 f \n0000000010 00000 n \n0000000060 00000 n \n0000000117 00000 n \n0000000242 00000 n \n0000000364 00000 n \n"
        b"trailer << /Size 6 /Root 1 0 R >>\nstartxref\n439\n%%EOF"
    )
