# AGENTS.md

## Project
- Name: `volleyball_book`
- Type: Python API-only app (FastAPI)
- Root: `.`
- App directory: `.`

## Local Setup
```bash
cd volleyball_book
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run
```bash
cd volleyball_book
source .venv/bin/activate
uvicorn app.main:app --reload
```

## Endpoints
- `GET /health`
- `POST /api/v1/exercises`
- Docs: `http://127.0.0.1:8000/docs`

## Conventions
- Keep changes small and focused.
- Prefer `rg` for file/content search.
- Do not remove or overwrite unrelated user changes.
- Commit naming convention:
  - Prefix every commit message with `[TASK-XXX]`.
  - Example: `[TASK-001] Implement create exercise API`.
- Task definition requirement:
  - Every task document must include a `Task Checklist` section with checkbox items.
  - Keep checklist status updated as implementation progresses.

## Testing Policy
- Use TDD for all new code:
  - Write or update a failing test first.
  - Implement the minimum code to make the test pass.
  - Refactor while keeping tests green.
- Bug fixes must include a regression test when feasible.
