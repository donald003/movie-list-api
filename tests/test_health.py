from app import create_app
from app.config import TestConfig


def test_health_returns_ok_when_db_reachable(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert data["database"] == "ok"


def test_health_returns_503_when_db_unreachable():
    class BadDbConfig(TestConfig):
        SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://bad:bad@localhost:9999/nope"

    app = create_app(BadDbConfig)
    client = app.test_client()
    response = client.get("/health")
    assert response.status_code == 503
    data = response.get_json()
    assert data["status"] == "degraded"
    assert data["database"] == "unavailable"
