PYTHON := .venv/bin/python

.PHONY: format lint typecheck check run

format:
	.venv/bin/ruff format .

lint:
	.venv/bin/ruff check .

typecheck:
	.venv/bin/mypy app

check: lint typecheck

run:
	.venv/bin/uvicorn app.main:app --reload
