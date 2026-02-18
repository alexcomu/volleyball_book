# Volleyball Book - Architecture Proposal (v1)

## Overview

This document describes the proposed backend architecture for the Volleyball Book app.
The app is API-first, local-first, and designed to support a future React frontend.

Goals:
- Record and manage exercises.
- Record training sessions and associated exercises.
- Keep code production-ready with trunk-based development and continuous delivery in mind.
- Enforce clean architecture, TDD, observability, and feature-flagged incremental delivery.

---

## Product Scope (Current)

- Single-user app (no authentication/authorization for now).
- No sensitive personal data.
- Local usage first.
- Future deployment via containers and CI/CD pipeline.
- Dashboard endpoint to support frontend summaries.

---

## Recommended Technology Stack

- API framework: FastAPI
- Data validation and schemas: Pydantic v2
- Database: PostgreSQL (SQL)
- ORM: SQLAlchemy 2.x
- Migrations: Alembic
- Testing: Pytest
- Static quality: Ruff + mypy + pre-commit
- Logging: structured JSON logs
- Metrics/tracing: OpenTelemetry
- Feature flags: provider abstraction (in-memory provider first)

Why SQL:
- Data is relational (trainings contain ordered exercise entries).
- Dashboard and filtering queries are straightforward.
- Fits cleanly with future growth and reporting.

---

## Architectural Style

Use clean architecture with explicit layers:

1. API Layer (`app/api`)
- FastAPI routers.
- Request/response models.
- Error mapping and HTTP concerns only.

2. Application Layer (`app/application`)
- Use-cases and orchestration.
- Transaction boundaries.
- Feature-flag checks.

3. Domain Layer (`app/domain`)
- Entities, value objects, and business rules.
- Framework-independent logic.

4. Infrastructure Layer (`app/infrastructure`)
- DB models, repository implementations, migrations.
- External adapters (logging, metrics, config providers).

5. Shared/Platform (`app/shared`)
- Cross-cutting concerns: configuration, observability, feature flags, time abstraction.

---

## Proposed Folder Structure

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

---

## Domain Model (Initial)

### Exercise
- `id`
- `name`
- `description`
- `tags` (start simple; evolve to normalized tags table if needed)
- `is_active` (supports soft delete)
- `created_at`
- `updated_at`

### TrainingSession
- `id`
- `date`
- `title`
- `pre_notes`
- `post_notes`
- `duration_minutes`
- `created_at`
- `updated_at`

### TrainingExercise (join entity with ordering)
- `id`
- `training_id`
- `exercise_id`
- `position` (order inside a training)
- `notes`
- `planned_reps`
- `actual_reps`

---

## API Contract (MVP, `/api/v1`)

Exercises:
- `GET /exercises`
- `POST /exercises`
- `PATCH /exercises/{id}`
- `DELETE /exercises/{id}` (soft delete)

Trainings:
- `GET /trainings`
- `POST /trainings`
- `GET /trainings/{id}`
- `PATCH /trainings/{id}`
- `POST /trainings/{id}/exercises`
- `PATCH /trainings/{id}/exercises/{training_exercise_id}`
- `DELETE /trainings/{id}/exercises/{training_exercise_id}`

Dashboard:
- `GET /dashboard/summary`

Operational:
- `GET /health`
- `GET /readiness`

---

## Observability and Logging

Implement from day one:

- Request ID / correlation ID middleware.
- Structured JSON logs including:
  - `timestamp`
  - `level`
  - `event`
  - `request_id`
  - `method`
  - `route`
  - `status_code`
  - `latency_ms`
- Domain event logs:
  - `exercise_created`
  - `exercise_updated`
  - `training_created`
  - `training_exercise_added`
- Metrics:
  - HTTP request count
  - HTTP latency histogram
  - error rate
- OpenTelemetry hooks for future tracing export.

---

## Feature Flags

Rules:
- Incomplete features must be behind flags.
- Evaluate flags in the application layer, not in routers.
- Default to safe-off for production.
- Test both flag-on and flag-off paths for flagged use-cases.

Initial provider:
- In-memory/local config provider (simple and deterministic for local usage/tests).
- Replaceable later with hosted flag service if needed.

---

## TDD and Delivery Workflow

### TDD
- Red: write a failing test first.
- Green: write minimal implementation to pass.
- Refactor: improve code while tests stay green.
- Bug fixes include regression tests when feasible.

### Trunk-based Development
- Small vertical slices.
- Frequent merges to `main`.
- `main` always production-ready.

### Continuous Delivery Readiness

CI quality gates should include:
- format check
- lint check
- type check
- unit/integration/API tests
- migration sanity check

Feature flags are used to merge incomplete work safely.

---

## First Implementation Milestones

1. Foundation
- Create layered folder structure.
- Add DB bootstrap (SQLAlchemy + Alembic).
- Add observability baseline (logging + request ID + metrics hooks).
- Add feature flag abstraction.

2. Vertical Slice 1: Exercise CRUD
- Domain model + repository interface.
- Application use-cases.
- API endpoints.
- Unit + integration + API tests.

3. Vertical Slice 2: Training Session with Exercises
- Create training.
- Attach/reorder/remove exercises.
- Post-training notes.
- Full TDD coverage.

4. Vertical Slice 3: Dashboard Summary
- Aggregated read model for trainings/exercises.
- Dashboard endpoint with API tests.

---

## Out of Scope for Now

- Authentication/authorization.
- Multi-user collaboration.
- Advanced analytics.
- External integrations.

These can be added later without breaking the current architecture.
