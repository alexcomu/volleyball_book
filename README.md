# Volleyball Book API

Minimal API-only Python app built with FastAPI.

Architecture proposal:
- `docs/architecture-proposal.md`
- `docs/tasks/TASK-001-create-exercise-api.md`

## Setup

```bash
cd /Users/alexcomunian/Desktop/playground/AI-stuff/volleyball_book
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pre-commit install
```

## Run

```bash
cd /Users/alexcomunian/Desktop/playground/AI-stuff/volleyball_book
source .venv/bin/activate
uvicorn app.main:app --reload
```

Server URL: `http://127.0.0.1:8000`

## Endpoints

- `GET /health`
- `POST /api/v1/exercises`
- Swagger UI: `http://127.0.0.1:8000/docs`

## Coding Standards

- Formatter: `ruff format` (Black-compatible style)
- Linter: `ruff check`
- Type checks: `mypy`
- Pre-commit hooks: `pre-commit`

Run all checks:

```bash
make check
```

Format code:

```bash
make format
```
