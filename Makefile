PYTHON := .venv/bin/python

.PHONY: format lint typecheck check

format:
	.venv/bin/ruff format .

lint:
	.venv/bin/ruff check .

typecheck:
	.venv/bin/mypy app

check: lint typecheck
