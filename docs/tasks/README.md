# Tasks Guide

This folder stores implementation-ready task definitions.

## Naming Convention

- File name format: `TASK-XXX-short-kebab-title.md`
- Example: `TASK-001-create-exercise-api.md`

## Task Lifecycle

1. Define scope and acceptance criteria before coding.
2. Implement with TDD (Red-Green-Refactor).
3. Keep commits production-ready (trunk-based).
4. Use commit message prefix `[TASK-XXX]` for task-related commits.
5. Use feature flags for incomplete functionality.
6. Keep observability requirements explicit.

Commit message example:
- `[TASK-001] Implement create exercise API`

## Task Template

Copy the structure below for each new task.

```md
# TASK-XXX - <Title>

## Objective
<What this task delivers>

## User Story
As a <role>, I want <goal> so that <benefit>.

## Scope
In scope:
- ...

Out of scope:
- ...

## API Contract (if applicable)
### Endpoint
- Method: `<METHOD>`
- Path: `<PATH>`

### Request Body
```json
{}
```

### Validation Rules
1. ...

### Success Response
- Status: `200/201/...`
```json
{}
```

### Error Responses
1. ...

## Architecture Requirements
1. API layer concerns only.
2. Application use-case orchestration.
3. Domain logic framework-independent.
4. Infrastructure adapters isolated.

## Feature Flag
- Flag key: `<flag_key>`
- Default: `true/false`
- Disabled behavior: `<404/503/etc>`

## Observability Requirements
- Success event(s): `...`
- Failure event(s): `...`
- Required fields: request id, route, latency, etc.

## TDD Execution Plan
1. Failing test for success path.
2. Failing test for validation/error path.
3. Minimal implementation.
4. Refactor with tests green.

## Task Breakdown
1. ...

## Acceptance Criteria
1. ...

## Definition of Done
1. Tests pass.
2. Lint/type checks pass.
3. Production-ready commit.
```
