# Movie List API

A REST API for managing a personal movie watchlist, built with Flask and PostgreSQL.
Work in progress — currently at Phase 1 (foundation).

## Stack

- Flask (app factory pattern)
- PostgreSQL
- SQLAlchemy + Flask-Migrate
- Docker

## Current Status

- [x] Flask app factory + config
- [x] PostgreSQL connection via SQLAlchemy
- [x] Flask-Migrate setup
- [x] `/health` endpoint
- [ ] JWT auth
- [ ] Movie CRUD
- [ ] Tests

## Running Locally

### Prerequisites

- Python 3.11+
- Docker (for PostgreSQL)

### Setup

1. Clone and install:

```bash
git clone <your-repo-url>
cd movie-list-api
py -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

On Windows, activate with `venv\Scripts\activate` instead.

2. Start PostgreSQL:

```bash
docker run --name movielist-db -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=yourpassword -e POSTGRES_DB=movielist -p 5432:5432 -v movielist-data:/var/lib/postgresql/data -d postgres:16-alpine
```

3. Configure environment:

```bash
cp .env.example .env
```

Then edit `.env` with your database credentials.

4. Run migrations and start the app:

```bash
flask db upgrade
py run.py
```

5. Verify:

Open `http://localhost:5000/health` in your browser. It should return:

```json
{"status": "ok"}
```