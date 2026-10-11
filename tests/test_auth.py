from app.models import User


def test_register_creates_user(client):
    response = client.post("/auth/register", json={
        "email": "new@example.com",
        "password": "password123",
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data["email"] == "new@example.com"
    assert "id" in data
    assert "password" not in data
    assert "password_hash" not in data


def test_register_rejects_missing_fields(client):
    response = client.post("/auth/register", json={"email": "a@example.com"})
    assert response.status_code == 422


def test_register_rejects_short_password(client):
    response = client.post("/auth/register", json={
        "email": "a@example.com",
        "password": "short",
    })
    assert response.status_code == 422


def test_register_rejects_duplicate_email(client):
    payload = {"email": "a@example.com", "password": "password123"}
    client.post("/auth/register", json=payload)
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 409


def test_login_returns_token(client):
    client.post("/auth/register", json={
        "email": "a@example.com",
        "password": "password123",
    })
    response = client.post("/auth/login", json={
        "email": "a@example.com",
        "password": "password123",
    })
    assert response.status_code == 200
    assert "access_token" in response.get_json()


def test_login_rejects_wrong_password(client):
    client.post("/auth/register", json={
        "email": "a@example.com",
        "password": "password123",
    })
    response = client.post("/auth/login", json={
        "email": "a@example.com",
        "password": "wrongpassword",
    })
    assert response.status_code == 401


def test_login_rejects_unknown_email(client):
    response = client.post("/auth/login", json={
        "email": "nobody@example.com",
        "password": "password123",
    })
    assert response.status_code == 401

def test_password_is_hashed_not_stored(client, app):
    client.post("/auth/register", json={
        "email": "hash@example.com",
        "password": "password123",
    })

    with app.app_context():
        user = User.query.filter_by(email="hash@example.com").first()
        assert user is not None
        assert user.password_hash != "password123"
        assert user.password_hash.startswith("pbkdf2:sha256") or user.password_hash.startswith("scrypt")
        assert user.check_password("password123") is True
        assert user.check_password("wrongpassword") is False
