# Volleyball Book API

Minimal API-only Python app built with FastAPI.

Architecture proposal:
- `docs/architecture-proposal.md`
- `docs/tasks/TASK-001-create-exercise-api.md`

Environment configuration:
- `config/development.json`
- `config/production.json`

## Setup

```bash
cd volleyball_book
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pre-commit install
```

## Run

```bash
cd volleyball_book
source .venv/bin/activate
uvicorn app.main:app --reload
```

Server URL: `http://127.0.0.1:8000`

## Endpoints

- `GET /health`
- `POST /api/v1/exercises`
- `GET /api/v1/exercises`
- `GET /api/v1/exercises/{id}`
- `PATCH /api/v1/exercises/{id}`
- `DELETE /api/v1/exercises/{id}`
- Swagger UI: `http://127.0.0.1:8000/docs`

## Exercise Categories Configuration

Configured categories are stored in:
- `config/development.json`
- `config/production.json`

Environment selection:
- set `APP_ENV=development` or `APP_ENV=production`
- default is `development`

Current values:
- `warmup`
- `ricezione`
- `servizio`
- `rigiocata`
- `difesa`

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

## Exercise API CLI

With the app running on localhost:

```bash
python3 scripts/exercise_api_cli.py create
```

Create with custom values:

```bash
python3 scripts/exercise_api_cli.py create \
  --name "Blocking Drill" \
  --description "Two blockers timing" \
  --tags '["block","timing"]' \
  --categories '["difesa","rigiocata"]'
```

List/get/update/delete:

```bash
python3 scripts/exercise_api_cli.py list
python3 scripts/exercise_api_cli.py get <exercise_id>
python3 scripts/exercise_api_cli.py update <exercise_id> --name "Updated name"
python3 scripts/exercise_api_cli.py delete <exercise_id>
```
