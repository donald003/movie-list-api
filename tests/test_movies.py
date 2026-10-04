def _auth_client(client, email="a@example.com"):
    """Register a user and return a client with their JWT set."""
    client.post("/auth/register", json={
        "email": email,
        "password": "password123",
    })
    response = client.post("/auth/login", json={
        "email": email,
        "password": "password123",
    })
    token = response.get_json()["access_token"]
    client.environ_base["HTTP_AUTHORIZATION"] = f"Bearer {token}"
    return client


def test_list_movies_requires_auth(client):
    response = client.get("/movies")
    assert response.status_code == 401


def test_create_movie(client):
    auth = _auth_client(client)
    response = auth.post("/movies", json={
        "title": "Inception",
        "director": "Nolan",
        "year": 2010,
        "rating": 9,
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data["title"] == "Inception"
    assert data["director"] == "Nolan"
    assert data["year"] == 2010
    assert data["rating"] == 9
    assert data["watched"] is False


def test_create_movie_rejects_missing_fields(client):
    auth = _auth_client(client)
    response = auth.post("/movies", json={"title": "Inception"})
    assert response.status_code == 400


def test_create_movie_rejects_invalid_rating(client):
    auth = _auth_client(client)
    response = auth.post("/movies", json={
        "title": "Inception",
        "director": "Nolan",
        "year": 2010,
        "rating": 11,
    })
    assert response.status_code == 400


def test_list_movies_returns_only_own(client):
    auth = _auth_client(client)
    auth.post("/movies", json={
        "title": "Inception", "director": "Nolan", "year": 2010, "rating": 9,
    })
    response = auth.get("/movies")
    assert response.status_code == 200
    movies = response.get_json()
    assert len(movies) == 1
    assert movies[0]["title"] == "Inception"


def test_get_movie(client):
    auth = _auth_client(client)
    created = auth.post("/movies", json={
        "title": "Inception", "director": "Nolan", "year": 2010, "rating": 9,
    }).get_json()
    response = auth.get(f"/movies/{created['id']}")
    assert response.status_code == 200
    assert response.get_json()["title"] == "Inception"


def test_update_movie(client):
    auth = _auth_client(client)
    created = auth.post("/movies", json={
        "title": "Inception", "director": "Nolan", "year": 2010, "rating": 9,
    }).get_json()
    response = auth.put(f"/movies/{created['id']}", json={"watched": True})
    assert response.status_code == 200
    assert response.get_json()["watched"] is True


def test_delete_movie(client):
    auth = _auth_client(client)
    created = auth.post("/movies", json={
        "title": "Inception", "director": "Nolan", "year": 2010, "rating": 9,
    }).get_json()
    response = auth.delete(f"/movies/{created['id']}")
    assert response.status_code == 204
    # Confirm it's gone
    response = auth.get(f"/movies/{created['id']}")
    assert response.status_code == 404


def test_user_cannot_access_other_users_movie(client):
    # User A creates a movie
    a = _auth_client(client, email="a@example.com")
    created = a.post("/movies", json={
        "title": "Inception", "director": "Nolan", "year": 2010, "rating": 9,
    }).get_json()

    # User B tries to access it
    b = _auth_client(client, email="b@example.com")
    response = b.get(f"/movies/{created['id']}")
    assert response.status_code == 404


def test_user_cannot_update_other_users_movie(client):
    a = _auth_client(client, email="a@example.com")
    created = a.post("/movies", json={
        "title": "Inception", "director": "Nolan", "year": 2010, "rating": 9,
    }).get_json()

    b = _auth_client(client, email="b@example.com")
    response = b.put(f"/movies/{created['id']}", json={"title": "Hacked"})
    assert response.status_code == 404


def test_user_cannot_delete_other_users_movie(client):
    a = _auth_client(client, email="a@example.com")
    created = a.post("/movies", json={
        "title": "Inception", "director": "Nolan", "year": 2010, "rating": 9,
    }).get_json()

    b = _auth_client(client, email="b@example.com")
    response = b.delete(f"/movies/{created['id']}")
    assert response.status_code == 404


def test_list_movies_excludes_other_users(client):
    a = _auth_client(client, email="a@example.com")
    a.post("/movies", json={
        "title": "Inception", "director": "Nolan", "year": 2010, "rating": 9,
    })

    b = _auth_client(client, email="b@example.com")
    response = b.get("/movies")
    assert response.status_code == 200
    assert response.get_json() == []
    
def test_update_movie_partial_fields(client):
    auth = _auth_client(client)
    created = auth.post("/movies", json={
        "title": "Inception", "director": "Nolan", "year": 2010, "rating": 9,
    }).get_json()
    response = auth.put(f"/movies/{created['id']}", json={
        "title": "Inception 2",
        "director": "Nolan 2",
        "year": 2011,
        "rating": 8,
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["title"] == "Inception 2"
    assert data["director"] == "Nolan 2"
    assert data["year"] == 2011
    assert data["rating"] == 8


def test_update_movie_rejects_invalid_year(client):
    auth = _auth_client(client)
    created = auth.post("/movies", json={
        "title": "Inception", "director": "Nolan", "year": 2010, "rating": 9,
    }).get_json()
    response = auth.put(f"/movies/{created['id']}", json={"year": "not-a-year"})
    assert response.status_code == 400
    
def test_update_movie_rejects_invalid_rating(client):
    auth = _auth_client(client)
    created = auth.post("/movies", json={
        "title": "Inception", "director": "Nolan", "year": 2010, "rating": 9,
    }).get_json()
    response = auth.put(f"/movies/{created['id']}", json={"rating": 99})
    assert response.status_code == 400