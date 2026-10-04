import pytest
from app import create_app
from app.config import TestConfig
from app.extensions import db


@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_client(client):
    """A test client with a registered user and a valid JWT."""
    client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "password123",
    })
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "password123",
    })
    token = response.get_json()["access_token"]
    client.environ_base["HTTP_AUTHORIZATION"] = f"Bearer {token}"
    return client