## Official API status

- Goodreads publicly states that it *"no longer issues new developer keys for our public developer API and plans to retire the current version of these tools."* [[help.goodreads.com](https://help.goodreads.com/s/article/Does-Goodreads-support-the-use-of-APIs)] This means any new tooling has to rely on scraping, undocumented endpoints, or user-exported data rather than the legacy REST API.
- Secondary sources (Medium, Slashdot, Rollout) repeat the same messaging and note that dormant API keys are revoked after 30 days, so we should not plan around existing keys either. [[Medium](https://shawngrider1.medium.com/goodreads-is-retiring-its-current-api-b961b72225c2)][[Rollout guide](https://rollout.com/integration-guides/goodreads/api-essentials)]

## Unauthenticated data sources we can already use

- `GET https://www.goodreads.com/book/auto_complete?format=json&q=<query>` returns structured JSON for search autocomplete. Example response (abridged):

  ```json
  {
    "bookId": "44767458",
    "title": "Dune (Dune #1)",
    "avgRating": "4.29",
    "ratingsCount": 1619478,
    "author": { "id": 58, "name": "Frank Herbert" },
    "bookUrl": "/book/show/44767458-dune"
  }
  ```

  This is ideal for search results without scraping HTML.

- Public shelves expose an RSS feed at `https://www.goodreads.com/review/list_rss/<user_id>?shelf=<shelf_name>` that includes title, author, rating, review text, tags, read dates, and cover URLs. (Validated with user id `1` — Otis Chandler’s shelf.)

- Standard HTML pages embed machine-readable data:
  - `book/show/<slug-or-id>` pages ship a large `__NEXT_DATA__` JSON blob containing book metadata, aggregated stats, and featured reviews. This can be parsed instead of hand-writing selectors.
  - Shelf pages (`review/list/<user_id>`) include the shelf table in HTML and expose links for each row. Even when signed out we can parse book ids, shelves, ratings, etc.
  - The shelf table HTML contains hidden `date_started` and `date_read` cells with one or more reading sessions (for rereads). These are rendered even when not signed in.

- Shelf RSS payloads already include page counts and reading timestamps:
  - Each `<item>` includes `<book><num_pages>...</num_pages></book>`, which avoids extra book page requests for page counts.
  - Reading dates are available as `<user_read_at>` (finish date), `<user_date_added>` (shelf add date), and `<user_date_created>` (review creation date).
  - A `<user_date_started>` tag is not consistently present in fixtures; parse it if present but plan for it to be missing.
  - If `<num_pages>` is missing, we can fall back to the book page `__NEXT_DATA__` (`details.numPages`) before considering external sources (Open Library / ISBN-based lookups).

- Quotes, Listopia, and other list pages follow predictable patterns (e.g., `list/show/<id>`). These can be scraped later using `selectolax`/`BeautifulSoup` with heuristics similar to RSS.

## Authentication + write-operation notes

- Sign-in is handled via Amazon/Apple/Google single-sign-on pages (`/ap/signin?...`). Automating those flows would require emulating Amazon login, so the more practical approach is to reuse an existing browser session by copying cookies (similar to X’s unofficial tools).
- Visiting any page yields cookies `_session_id2`, `ccsid`, and `locale`, and each page ships a `<meta name="csrf-token">`. POST endpoints will require that token plus the session cookie.
- Book pages render interactive “Want to Read” / “Choose a shelf” controls; when logged in they submit AJAX requests. We’ll need to capture those network calls once (via browser devtools) to reproduce the URLs and payloads. The HTML already hints at endpoints such as `/review/rate/<id>` and `/review/list/<user>?shelf=...`.
- For authenticated exports, Goodreads still offers a CSV export page (`/review_porter/export`) that includes `Date Started`, `Date Read`, and `Number of Pages`. This may be the most complete source for start/finish dates but requires logged-in cookies and asynchronous export handling.

## Existing community projects / patterns

- [`@steipete/bird`](https://github.com/steipete/bird) is a fully fledged X/Twitter CLI. Key takeaways we can reuse:
  - Cookie-first authentication (it resolves `auth_token`/`ct0` from Safari/Chrome/Firefox or accepts manual input).
  - Cached query IDs for private GraphQL endpoints and resilient refresh logic.
  - UX patterns such as `bird whoami`, JSON output toggles, and `--plain` for scriptable output.
  These patterns map directly to a Goodreads CLI (cookie import, optional browser detection, offline cache of parsed metadata).

- [`goodreads-bookshelf-api`](https://github.com/tnmyk/goodreads-bookshelf-api) (TypeScript) scrapes the shelf RSS feed and exposes a simple API returning title, author, image link, rating, etc. It proves the RSS feed is reliable enough for bookshelf exports without needing the legacy developer key.

- [`goodreads-cli`](https://github.com/mjip/goodreads-cli) and similar projects depended on the deprecated API and now fail because new keys can’t be issued. This validates the demand for a scraping-based replacement.

- Commercial scrapers (Apify’s Goodreads Book Search actor, MCP marketplace tools) already sell shelf/search data, which confirms that the HTML/RSS approach works at scale and that the site doesn’t aggressively block bots when requests are throttled.

## CLI visualization options

- [`plotext`](https://github.com/piccolomo/plotext) renders bar and line charts directly in the terminal, returns rendered strings via `build()`, and is pure Python.
- [`termplotlib`](https://github.com/nschloe/termplotlib) is small and MIT-licensed, but focuses on scatter/line plots and uses `numpy` for some features.
- `rich` can be used to build custom bar-like tables, but it requires more manual layout for axes and labels.

Decision: use `plotext` for a minimal dependency that can render bar charts with labels in a single call, while keeping the math and binning logic in our own modules for test coverage.

## Risks and unknowns

- Write operations (adding/removing books, editing reviews) require authenticated requests whose exact endpoints still need to be discovered. Plan: capture requests from the web app or mobile app using browser devtools/mitmproxy, then replicate the minimal set (probably `POST /shelf/add_to_shelf`, `POST /review/edit`, etc.).
- Private shelves might block the RSS endpoint even when logged in; we may need to fall back to scraping `review/list` HTML after authenticating with cookies.
- Goodreads could throttle or block repeated scrapes; we’ll need to build polite defaults (rate limiting, caching, `If-Modified-Since` headers).

These findings drive the implementation strategy outlined in `PLAN.md`.
