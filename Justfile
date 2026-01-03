set shell := ["bash", "-cu"]

fmt:
    uv run ruff format .

format-check:
    uv run ruff format --check .

lint:
    uv run ruff check .

lint-fix:
    uv run ruff check . --fix

type:
    uv run ty check .

test:
    uv run pytest

test-live:
    GOODREADS_LIVE=1 uv run pytest -m live

fc: fmt lint-fix lint type test

check-all: fc

ci: lint format-check type test
