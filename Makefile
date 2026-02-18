PYTHON := .venv/bin/python

.PHONY: format lint typecheck test run-test check run

format:
	.venv/bin/ruff format .

lint:
	.venv/bin/ruff check .

typecheck:
	.venv/bin/mypy app

test:
	.venv/bin/pytest tests

run-test: test

check: lint typecheck test

run:
	.venv/bin/uvicorn app.main:app --reload
