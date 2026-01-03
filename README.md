## Goodreads CLI (unofficial)

This project aims to provide a modern, scriptable Goodreads command-line client powered by `uv` and Python. The official Goodreads API is no longer issuing keys, so the tool relies on scraping publicly available endpoints plus authenticated requests made with the user’s existing browser session.

### Overview

- Read-only: search titles, fetch book details, list/export public shelves via RSS.
- Auth helpers: store cookies, `whoami`, and CSRF extraction checks for upcoming write flows.
- Built for automation: JSON/CSV output and `uvx`-friendly execution.

### Usage summary

```bash
# search titles
uv run goodreads-cli public search "Dune" -n 5

# fetch book details
uv run goodreads-cli public book show 44767458

# list a public shelf
uv run goodreads-cli public shelf list --user 1 --shelf all -n 5

# export a shelf
uv run goodreads-cli public shelf export --user 1 --shelf all --format json
```

### Current status

- Research on available endpoints, scraping strategies, and prior art lives in [`docs/RESEARCH.md`](docs/RESEARCH.md).
- The implementation roadmap (phased plan, architecture, and near-term tasks) is tracked in [`docs/PLAN.md`](docs/PLAN.md).
- Milestones and testable deliverables are listed in [`docs/MILESTONES.md`](docs/MILESTONES.md).
- A `typer`-based CLI and supporting modules will live under `src/goodreads_cli/`.

### Development

```bash
# create / activate the project environment
uv sync

# run the dev CLI (placeholder command for now)
uv run goodreads-cli

# run via uvx (local)
uvx --from . goodreads-cli --help

# run via uvx (git)
uvx --from git+https://github.com/EvanOman/goodreads_cli goodreads-cli --help

# search titles
uv run goodreads-cli public search "Dune" -n 5

# fetch a book by id or url
uv run goodreads-cli public book show 44767458

# list a public shelf via RSS
uv run goodreads-cli public shelf list --user 1 --shelf all -n 5

# export a shelf to JSON or CSV
uv run goodreads-cli public shelf export --user 1 --shelf all --format json

# store cookies from browser or manual cookie string
uv run goodreads-cli auth login --browser chrome
uv run goodreads-cli auth login --cookie-string "_session_id2=...; ccsid=...; locale=en"

# show the current authenticated user
uv run goodreads-cli auth whoami

# validate session + csrf extraction
uv run goodreads-cli auth check

# run unit tests
uv run pytest

# run live tests (network)
GOODREADS_LIVE=1 uv run pytest -m live

# run live auth test (requires a valid cookie string)
GOODREADS_LIVE=1 GOODREADS_COOKIE="_session_id2=...; ccsid=...; locale=en" uv run pytest -m live -k whoami

# run live csrf test (requires the same cookie string)
GOODREADS_LIVE=1 GOODREADS_COOKIE="_session_id2=...; ccsid=...; locale=en" uv run pytest -m live -k csrf

# justfile helpers (lint/type/test)
just lint
just type
just test

# pre-commit hook (runs just check-all)
uv run pre-commit run --all-files
```

The project targets Python 3.13 (via `.python-version`). Use `uv` for dependency management and execution.
