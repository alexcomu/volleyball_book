# TASK-002 - Exercise CRUD Remaining Operations

## Objective

Complete the Exercise API CRUD surface by implementing read, update, and delete operations on top of the existing create endpoint.

## User Story

As the coach, I want to list, inspect, edit, and remove exercises so I can keep my exercise catalog accurate and usable over time.

## Scope

In scope:
- `GET /api/v1/exercises` (list)
- `GET /api/v1/exercises/{id}` (detail)
- `PATCH /api/v1/exercises/{id}` (partial update)
- `DELETE /api/v1/exercises/{id}` (soft delete)
- Validation and normalization consistency with create rules
- TDD coverage (API + unit + integration)
- Structured logging for each operation

Out of scope:
- Training session APIs
- Dashboard aggregation logic
- Authentication/authorization

## API Contract

### 1) List Exercises
- Method: `GET`
- Path: `/api/v1/exercises`
- Behavior:
  - Return active exercises by default
  - Optional query param to include inactive later (`include_inactive`, optional)
- Success response: `200 OK`

### 2) Get Exercise By ID
- Method: `GET`
- Path: `/api/v1/exercises/{id}`
- Success response: `200 OK`
- Not found: `404 Not Found`

### 3) Update Exercise
- Method: `PATCH`
- Path: `/api/v1/exercises/{id}`
- Updatable fields:
  - `name`
  - `description`
  - `tags`
  - `categories`
- Validation:
  - same normalization rules as create
  - `categories` must contain at least one valid configured category when provided
  - duplicate name handling with `409 Conflict`
- Success response: `200 OK`
- Errors: `404`, `409`, `422`

### 4) Delete Exercise
- Method: `DELETE`
- Path: `/api/v1/exercises/{id}`
- Behavior:
  - soft delete via `is_active=false`
- Success response: `204 No Content`
- Not found: `404 Not Found`

## Architecture Requirements

Use Hexagonal Architecture:

1. Inbound adapters:
   - Add routers/schemas for list/get/update/delete.
2. Core use-cases:
   - `list_exercises`
   - `get_exercise`
   - `update_exercise`
   - `delete_exercise`
3. Outbound ports/adapters:
   - Extend repository interface and SQLAlchemy adapter.
4. Rules:
   - category allowed values must continue to come from environment config
   - business rules remain in application/domain layers
   - no FastAPI/SQLAlchemy imports in domain layer

## Feature Flags

- Existing: `exercise_create_api_enabled`
- New flags:
  - `exercise_list_api_enabled`
  - `exercise_get_api_enabled`
  - `exercise_update_api_enabled`
  - `exercise_delete_api_enabled`

Default behavior:
- `true` when operation is production-ready
- if disabled, return `404 Not Found`

## Observability Requirements

Log events:
- `exercise_listed`
- `exercise_retrieved`
- `exercise_updated`
- `exercise_deleted`

Include:
- `request_id`
- `exercise_id` (when applicable)
- `route`
- `status_code`
- `latency_ms`

## TDD Execution Plan

1. API tests for each endpoint success path.
2. API tests for key failures (`404`, `409`, `422`).
3. Domain tests for normalization/restrictions reused in update.
4. Application tests for each use-case behavior.
5. Integration tests for repository operations (list/get/update/soft-delete).
6. Refactor while preserving green tests.

## Task Checklist

- [x] Add API schemas and routers for list/get/update/delete.
- [x] Extend repository port and SQLAlchemy adapter for remaining CRUD operations.
- [x] Implement use-cases for list/get/update/delete.
- [x] Enforce create-equivalent validation/normalization rules on update.
- [x] Implement soft delete with `is_active=false`.
- [x] Add feature flags for all new exercise operations.
- [x] Add structured logs for new operations.
- [x] Add and pass unit/integration/API tests.
- [x] Update OpenAPI docs and README endpoint list.

## Acceptance Criteria

1. `GET /api/v1/exercises` returns active exercises with `200`.
2. `GET /api/v1/exercises/{id}` returns exercise details or `404`.
3. `PATCH /api/v1/exercises/{id}` updates supported fields with validation and returns `200`.
4. `DELETE /api/v1/exercises/{id}` performs soft delete and returns `204`.
5. Category rules remain config-driven (`APP_ENV` config files).
6. Feature flags control availability of each operation.
7. Structured logs are emitted for all operation outcomes.
8. `make check` passes with full test coverage updates.

## Definition of Done

1. All checklist items completed.
2. Lint/type/tests pass locally (`make check`).
3. Documentation updated.
4. Commit(s) follow `[TASK-002]` message convention.
