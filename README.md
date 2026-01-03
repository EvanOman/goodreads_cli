## Goodreads Tools (unofficial)

A pragmatic, scriptable CLI that turns your Goodreads shelves into dashboard-ready data. It exports clean JSONL for your reading timeline (including rereads), estimates pages per day, and renders a text-based bar chart you can use in a terminal or CI logs.

### What it does

- Export your reading timeline with start/end dates and page counts.
- Generate pages-per-day charts from that timeline (even with overlapping reads).
- Pull book metadata and public shelf data without needing API keys.
- Keep everything scriptable with JSON/CSV output.

### How it works

- Public data comes from Goodreads RSS feeds and book pages.
- For read-start/end dates, the CLI scrapes the public review list HTML (the `read` shelf exposes those fields).
- Page counts come from RSS when available and fall back to book pages if needed.
- Auth helpers exist for future write operations, but are not required for read-only features.

### Sample: last 10 finished books (read shelf)

| Title | Started | Finished | Pages | Book ID |
| --- | --- | --- | --- | --- |
| A Christmas Carol | 2025-12-22 | 2025-12-30 | 184 | 5326 |
| A Philosophy of Software Design | 2025-08-01 | 2025-12-30 | 184 | 58665335 |
| The Wright Brothers | 2025-10-13 | 2025-10-14 | 320 | 22609391 |
| The Secret of Our Success: How Culture Is Driving Human Evolution, Domesticating Our Species, and Making Us Smarter | 2025-09-15 | 2025-10-10 | 456 | 25761655 |
| Kill It with Fire: Manage Aging Computer Systems | 2025-09-27 | 2025-10-07 | 248 | 54716655 |
| The Almanack of Naval Ravikant: A Guide to Wealth and Happiness | 2025-09-25 | 2025-10-05 | 244 | 54898389 |
| The Thinking Machine: Jensen Huang, Nvidia, and the World's Most Coveted Microchip | 2025-09-05 | 2025-09-12 | 272 | 211399783 |
| Influence: The Psychology of Persuasion | 2025-07-30 | 2025-09-06 | 320 | 28815 |
| Think Again: The Power of Knowing What You Don't Know | 2025-06-12 | 2025-07-22 | 307 | 55539565 |
| Getting Naked: A Business Fable about Shedding the Three Fears That Sabotage Client Loyalty | 2025-07-01 | 2025-07-07 | 240 | 7717531 |

More sample outputs live in `samples/README.md`.

### Quick start

```bash
# search titles
uv run goodreads-tools public search "Dune" -n 5

# export a reading timeline as JSONL
uv run goodreads-tools public shelf timeline --user <user-id> --shelf read --source html --format jsonl

# render a pages/day chart for a date range
uv run goodreads-tools public shelf chart --user <user-id> --shelf read --source html --from 2023-01-01 --to 2025-12-30 --bin-days 14
```

### Development

```bash
# create / activate the project environment
uv sync

# run the dev CLI
uv run goodreads-tools

# run via uvx (local)
uvx --from . goodreads-tools --help

# run via uvx (git)
uvx --from git+https://github.com/EvanOman/goodreads-tools goodreads-tools --help

# run unit tests
uv run pytest

# run live tests (network)
GOODREADS_LIVE=1 uv run pytest -m live

# justfile helpers (lint/type/test)
just lint
just type
just test
```

### Releases

Releases use release-please with conventional-commit PR titles. It maintains a single
release PR on `master`; when you merge that PR, it creates the tag and GitHub Release.
The PyPI publish job runs on the GitHub Release (best-effort until OIDC is configured).
See `docs/RELEASE.md` for the full flow and examples.

The project targets Python 3.13 (via `.python-version`). Use `uv` for dependency management and execution.
