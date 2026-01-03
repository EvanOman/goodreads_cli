## Project goal

Build a Python CLI (packaged with `uv`) that can read and write Goodreads data without the deprecated public API. The CLI should feel similar to `bird`: a fast text-first tool that works with existing browser cookies, exposes JSON for scripting, and can be extended into automation/agent workflows.

Milestones with testable deliverables are tracked in `docs/MILESTONES.md`.

## High-level phases

1. **Foundations**
   - Finalize packaging (`pyproject`, `typer` entry point, `rich` logging).
   - Build shared utilities: HTTP client (`httpx`), retry + rate limiter, config directory (`~/.config/goodreads-cli`), and structured logging.
   - Implement cookie acquisition: use [`browser-cookie3`](https://pypi.org/project/browser-cookie3/) to read Safari/Chrome/Firefox cookies or accept a manual session string; persist encrypted cookies locally.
2. **Read-only features**
   - `gr search "<query>"` → call `book/auto_complete`.
   - `gr book show <book-id-or-url>` → fetch `book/show/...`, parse `__NEXT_DATA__` for metadata + top reviews.
   - `gr shelf list [--user] [--shelf read]` → fetch shelf RSS when public; if private use authenticated HTML scrape.
   - `gr export shelves --format json|csv` → dump data with caching + rate limiting.
3. **Write features**
   - Reverse-engineer the POST flows for:
     - Marking a book as want-to-read / currently-reading / read.
     - Rating + reviewing a book.
     - Adding/removing custom shelves.
   - Each write command should grab the latest `authenticity_token`, submit the POST, and validate HTML/JSON responses.
   - Add `gr whoami` to confirm the authenticated user (by hitting `/user/show` or parsing the shelf header).
4. **Automation / agent hooks**
   - Provide a thin Python API (`goodreads_cli.client`) so agent frameworks can script actions.
   - Optional background tasks: e.g., sync Goodreads shelves to a local SQLite DB, export to Obsidian/Notion.

## Technical plan

### CLI + packaging

- Stick with `uv` workflows (`uv run`, `uv pip install`, `uv lock`) so dependencies stay reproducible.
- Use `typer` for the CLI, `rich` for tabular/colored output, `pydantic` for response models, and `httpx` for HTTP.
- Set `ruff` + `mypy` configs once we add linting (later task).

### Authentication workflow

1. `gr login`:
   - Attempt to extract cookies from available browsers via `browser-cookie3`. If multiple profiles are found, prompt the user.
   - Alternatively accept a pasted cookie string (`_session_id2=...; ccsid=...`).
   - Store cookies + metadata in `~/.config/goodreads-cli/session.json` (consider keyring for encryption).
2. Every request loads cookies, injects `User-Agent`, and, for writes, fetches the CSRF token by calling a lightweight endpoint (home page or the target page itself).
3. Implement automatic refresh when a 302 to `/user/sign_in` is detected.

### Scraping modules

- `goodreads_cli/http.py`: wrappers around `httpx.AsyncClient`, throttle, caching, error translation.
- `goodreads_cli/parsers/search.py`: parse autocomplete JSON.
- `goodreads_cli/parsers/book.py`: load `__NEXT_DATA__` and map to dataclasses.
- `goodreads_cli/parsers/shelf.py`: RSS + HTML parser (use `selectolax` for speed).
- `goodreads_cli/auth.py`: cookie management + CSRF extraction.

### Testing strategy

- Unit tests for parsers using saved fixtures (`tests/fixtures/book_dune.html`, `shelf_rss.xml`, etc.).
- CLI smoke tests via `pytest` + `typer.testing.CliRunner` to ensure commands wire up correctly.

### Agent story

- Expose a Python API surface (`from goodreads_cli import Client`) that the CLI and agents share.
- Later we can wrap commands as MCP skills or other agent-toolkits so the user can ask for “plan my January TBR” and the agent orchestrates CLI commands.

## Completed setup tasks (historical)

1. Flesh out `README.md` with goals, install instructions, and usage examples.
2. Wire `typer` into `src/goodreads_cli/__init__.py`, add `cli.py`, and create commands.
3. Implement unauthenticated search + book detail parsing.
4. Add `docs/flow-write.md` notes (write flows remain future work).
5. Set up tests + CI.

## Progress log

- Milestone 1 complete: search command, HTTP client, and unit/live tests. See `docs/MILESTONES.md`.
- Milestone 2 complete: book show command, HTML parser for `__NEXT_DATA__`, and unit/live tests.
- Milestone 3 complete: shelf RSS parsing, list/export commands, and unit/live tests.
- Milestone 4 deferred: write flows are not started (auth helpers exist, but no write commands).
- Milestone 5 complete: reading timeline export for dashboard data (pages + start/end dates + chart).
- Write-flow capture instructions live in `docs/flow-write.md` for future work.

## Current status

The initial dashboard spec (public timeline export + pages/day chart) is complete. No work is in progress; future write/automation features remain planned but not started.
