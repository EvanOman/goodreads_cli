## Milestones

Each milestone is a small, testable deliverable. Run unit tests with:

```bash
uv run pytest
```

Live tests (network) are opt-in:

```bash
GOODREADS_LIVE=1 uv run pytest -m live
```

### Milestone 1: Search CLI (read-only)

Status: complete (search command + unit/live tests).

Deliverables:

- `goodreads-cli public search "<query>"` fetches autocomplete JSON and prints results.
- Shared HTTP client with basic rate limiting and error handling.
- Unit tests for the search parser + models.
- Live test that hits the Goodreads autocomplete endpoint.

### Milestone 2: Book details (read-only)

Status: complete (book show command + unit/live tests).

Deliverables:

- `goodreads-cli public book show <id|url>` parses `__NEXT_DATA__` for title/author/rating.
- Book parser unit tests with saved HTML fixtures.
- Live test that fetches a known book page and validates core fields.

### Milestone 3: Shelf export (read-only)

Status: complete (shelf list + export, unit/live tests).

Deliverables:

- `goodreads-cli public shelf list --user <id> --shelf <name>` reads RSS when public.
- CSV/JSON export support.
- Unit tests for RSS parser and CSV output.
- Live test against a public shelf (e.g., user id `1`).

### Milestone 4: Auth + write flows

Status: in progress (auth scaffolding + whoami + csrf helper complete; write flows pending).

Deliverables:

- `goodreads-cli auth login` stores browser cookies and confirms `whoami`.
- Write commands (shelve/rate/review) based on captured POST flows.
- Unit tests for auth/session loading + mocked POST handling.
- Live test for a safe write (opt-in and user-confirmed).
