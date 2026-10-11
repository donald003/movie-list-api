# Movie List API

A REST API demonstrating ownership-based access control, relational
data modeling, and stateless authentication.

Each user's movie collection is isolated at the query layer, so users
can only access their own data.

## What this project demonstrates

- **Relational data modeling** — Users and movies with foreign keys
  and indexes on frequently queried columns
- **Authentication and authorization** — JWT-based auth with ownership
  enforced at the query level rather than the route level
- **API design** — RESTful endpoints, consistent error shapes, proper
  HTTP status codes, input validation
- **Schema management** — Versioned migrations, so every schema change
  is a reviewable file rather than a manual SQL script
- **API documentation** — OpenAPI 3.0 spec with interactive Swagger UI at `/docs`
- **Testing** — Integration tests covering auth flows, CRUD behavior,
  and authorization edge cases
- **Reliability** — Health check that queries the database, connection
  pool configuration for self-healing after DB restarts
- **Security** — Password hashing, rate limiting on auth endpoints

## Stack

- Flask (app factory + blueprints)
- PostgreSQL
- SQLAlchemy + Flask-Migrate
- Flask-Smorest (OpenAPI / Marshmallow schemas)
- JWT (Flask-JWT-Extended)
- Flask-Limiter
- Docker (Postgres container)

## Endpoints

| Method | Path             | Auth | Description                    |
|--------|------------------|------|--------------------------------|
| GET    | /health          | No   | Health check (queries DB)                   |
| POST   | /auth/register   | No   | Create a user                  |
| POST   | /auth/login      | No   | Get a JWT                      |
| GET    | /movies          | Yes  | List current user's movies     |
| POST   | /movies          | Yes  | Add a movie                    |
| GET    | /movies/{id}     | Yes  | Get one movie (own only)       |
| PUT    | /movies/{id}     | Yes  | Update a movie (own only)      |
| DELETE | /movies/{id}     | Yes  | Delete a movie (own only)      |

## API Documentation

Interactive API docs are available at `/docs` when the server is running.
The OpenAPI spec is served at `/openapi.json`.

## Running Locally

### Prerequisites

- Python 3.11+
- Docker

### Setup

1. Clone and install:

```bash
git clone git@github.com:donald003/movie-list-api.git
cd movie-list-api
py -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

2. Start PostgreSQL:

```bash
docker run --name movielist-db -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=password -e POSTGRES_DB=movielist -p 5432:5432 -v movielist-data:/var/lib/postgresql/data -d postgres:16-alpine
```

3. Configure environment:

```bash
cp .env.example .env
```

Then edit `.env` with your database credentials.

4. Run migrations and start:

```bash
flask db upgrade
python run.py
```

5. Verify:

`http://localhost:5000/health` → `{"status": "ok"}`

6. Explore the API:

Open `http://localhost:5000/docs` for interactive API documentation.

## Testing

Run the test suite:

```bash
pytest --cov=app --cov-report=term-missing
```

## Design Decisions

- **Ownership at the query level** — every movie query filters by the
  authenticated user's ID. If another user requests it, the query returns
  nothing and we respond 404 — not 403 — so we don't leak whether the
  resource exists.
- **Schema-based validation** — request shapes are declared as Marshmallow
  schemas rather than hand-written `if` checks. The same schema validates
  input, documents the API, and drives Swagger UI.
- **Migrations instead of `create_all()`** — schema changes are versioned
  and reviewable. Production deployments run `flask db upgrade`, not a
  drop-and-recreate.
