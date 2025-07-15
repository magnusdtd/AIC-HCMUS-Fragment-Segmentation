import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.database import get_session, User
from sqlmodel import select

@pytest.fixture(scope="function")
def test_client():
    client = TestClient(app)
    yield client

@pytest.fixture(scope="function", autouse=True)
def cleanup_users():
    # This fixture will run after each test
    yield
    # Cleanup code: remove test users
    from sqlmodel import Session
    from app.models.database import engine
    with Session(engine) as session:
        for username in ["testuser1", "testuser2", "testuser3", "testuser4", "nonexistent"]:
            user = session.exec(
                select(User).where(User.username == username)
            ).first()
            if user:
                session.delete(user)
        session.commit()