# Volleyball Book API

Minimal API-only Python app built with FastAPI.

Architecture proposal:
- `docs/architecture-proposal.md`

## Setup

```bash
cd /Users/alexcomunian/Desktop/playground/AI-stuff/volleyball_book/volleyball_book
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pre-commit install
```

## Run

```bash
uvicorn app.main:app --reload
```

Server URL: `http://127.0.0.1:8000`

## Endpoints

- `GET /health`
- `GET /items/{item_id}`
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
