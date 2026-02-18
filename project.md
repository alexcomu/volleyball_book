# Project Guide

## Purpose

`volleyball_book` is an API-first backend to manage volleyball exercises and training sessions, designed to support a future React frontend.

## Tech Stack

- Language: Python 3.13
- API: FastAPI
- Validation/Schemas: Pydantic v2
- Database: PostgreSQL
- ORM: SQLAlchemy 2.x
- Migrations: Alembic
- Testing: Pytest
- Lint/Format: Ruff (format + lint), Black-compatible formatting
- Type checking: mypy
- Git hooks: pre-commit
- Observability:
  - Structured JSON logging
  - Request/correlation IDs
  - OpenTelemetry-ready metrics/tracing hooks
- Feature flags: application-layer flag provider abstraction (local/in-memory first)

## Project Conventions

- Architecture: clean architecture (API, application, domain, infrastructure, shared).
- API versioning: all business endpoints under `/api/v1`.
- Trunk-based development: small, frequent merges to `main`.
- Continuous delivery mindset: `main` must stay production-ready.
- Feature flags:
  - Incomplete features must be behind flags.
  - Default behavior must be safe when a flag is disabled.
- TDD required:
  - Write failing test first.
  - Implement minimum code to pass.
  - Refactor while tests remain green.
  - Add regression tests for bug fixes when feasible.
- Quality gates (local + CI):
  - `ruff format`
  - `ruff check`
  - `mypy`
  - `pytest`
- Logging conventions:
  - Use structured logs with stable event names.
  - Include request ID, route, status, and latency where relevant.

## Current Repository Structure

```text
/Users/alexcomunian/Desktop/playground/AI-stuff/volleyball_book
  app/
    __init__.py
    main.py
  docs/
    architecture-proposal.md
  .gitignore
  .pre-commit-config.yaml
  AGENTS.md
  Makefile
  README.md
  pyproject.toml
  requirements.txt
  requirements-dev.txt
  project.md
```

## Target Application Structure

```text
app/
  main.py
  api/
    routers/
    schemas/
    dependencies/
  application/
    services/
    use_cases/
    dto/
  domain/
    models/
    rules/
    repositories/
  infrastructure/
    db/
      models/
      repositories/
      migrations/
    observability/
    flags/
  shared/
    config/
    logging/
    errors/
tests/
  unit/
  integration/
  api/
```

## Core Domain (MVP)

- Exercise:
  - Name, description, tags, active status, timestamps.
- TrainingSession:
  - Date, title, pre/post notes, duration, timestamps.
- TrainingExercise:
  - Link between training and exercise, order/position, exercise notes.

## API Scope (MVP)

- Exercise CRUD.
- Training CRUD.
- Assign/remove/reorder exercises in a training.
- Dashboard summary endpoint.
- Operational endpoints: `/health`, `/readiness`.
