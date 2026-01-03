from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from goodreads_cli.auth.csrf import fetch_csrf_token
from goodreads_cli.auth.session import (
    SESSION_PATH,
    create_session_from_browser,
    create_session_from_cookie_string,
    load_session,
    save_session,
)
from goodreads_cli.auth.user import get_current_user
from goodreads_cli.http_client import GoodreadsClient
from goodreads_cli.public.book import get_book_details
from goodreads_cli.public.search import search_books
from goodreads_cli.public.shelf import (
    get_shelf_items,
    shelf_items_to_csv,
    shelf_items_to_json,
)

app = typer.Typer(help="Unofficial Goodreads CLI (see docs/PLAN.md).")
public_app = typer.Typer(help="Public (no-auth) commands.")
public_book_app = typer.Typer(help="Public book commands.")
public_shelf_app = typer.Typer(help="Public shelf commands.")
auth_app = typer.Typer(help="Authenticated session helpers.")
console = Console()


def _print_docs_message() -> None:
    console.print(
        "[bold]Docs[/bold]\n"
        "- [green]Research[/green]: docs/RESEARCH.md\n"
        "- [green]Plan[/green]: docs/PLAN.md\n"
        "\n"
        "Implementation is in progress. See the docs for the current roadmap."
    )


@app.callback(invoke_without_command=True)
def root(ctx: typer.Context) -> None:
    """Top-level callback. Prints docs when no subcommand is supplied."""
    if ctx.invoked_subcommand is None:
        _print_docs_message()


app.add_typer(public_app, name="public")
app.add_typer(auth_app, name="auth")
public_app.add_typer(public_book_app, name="book")
public_app.add_typer(public_shelf_app, name="shelf")
app.add_typer(auth_app, name="auth")


@public_app.command()
def search(
    query: str,
    limit: int = typer.Option(10, "--limit", "-n", min=0),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """Search Goodreads titles via the public autocomplete endpoint."""
    items = search_books(query)
    if limit:
        items = items[:limit]

    if json_output:
        console.print_json(json.dumps([item.model_dump(by_alias=True) for item in items]))
        return

    table = Table(title=f'Results for "{query}"')
    table.add_column("Title", style="bold")
    table.add_column("Author")
    table.add_column("Avg", justify="right")
    table.add_column("Ratings", justify="right")
    table.add_column("Book ID", justify="right")
    table.add_column("URL")

    for item in items:
        table.add_row(
            item.title,
            item.author.name if item.author else "",
            f"{item.avg_rating:.2f}" if item.avg_rating is not None else "",
            f"{item.ratings_count}" if item.ratings_count is not None else "",
            item.book_id,
            item.book_url,
        )

    console.print(table)


@auth_app.command("login")
def login(
    cookie_string: str | None = typer.Option(None, "--cookie-string"),
    browser: str | None = typer.Option(
        None,
        "--browser",
        help="One of: chrome, chromium, firefox, edge, safari",
    ),
    session_path: Path = typer.Option(SESSION_PATH, "--session-path"),
    check: bool = typer.Option(True, "--check/--no-check"),
) -> None:
    """Store a Goodreads session from browser cookies or a cookie string."""
    if cookie_string:
        session = create_session_from_cookie_string(cookie_string)
    else:
        session = create_session_from_browser(browser)

    save_session(session, session_path)
    console.print(f"Saved session to {session_path} ({len(session.cookies)} cookies).")

    if check:
        client = GoodreadsClient(cookies=session.cookies)
        user = get_current_user(client)
        client.close()
        if user is None:
            console.print("[yellow]Session saved, but whoami failed.[/yellow]")
        else:
            console.print(f"Logged in as {user.name} ({user.user_id}).")


@auth_app.command("whoami")
def whoami(session_path: Path = typer.Option(SESSION_PATH, "--session-path")) -> None:
    """Show the current user based on stored session cookies."""
    session = load_session(session_path)
    client = GoodreadsClient(cookies=session.cookies)
    user = get_current_user(client)
    client.close()
    if user is None:
        raise typer.Exit(code=1)
    console.print(f"{user.name} ({user.user_id})")


@auth_app.command("check")
def auth_check(session_path: Path = typer.Option(SESSION_PATH, "--session-path")) -> None:
    """Check session validity and CSRF extraction."""
    session = load_session(session_path)
    client = GoodreadsClient(cookies=session.cookies)
    user = get_current_user(client)
    token = fetch_csrf_token(client)
    client.close()

    if user is None:
        console.print("[red]Session invalid or not signed in.[/red]")
        raise typer.Exit(code=1)
    console.print(f"User: {user.name} ({user.user_id})")
    if token:
        console.print("CSRF: ok")
    else:
        console.print("[yellow]CSRF token not found.[/yellow]")


@public_book_app.command("show")
def book_show(
    book: str,
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """Show book details from a Goodreads URL or book id."""
    details = get_book_details(book)
    if json_output:
        console.print_json(details.model_dump_json())
        return

    table = Table(title=details.title)
    table.add_column("Field", style="bold")
    table.add_column("Value")
    table.add_row("Book ID", details.book_id)
    table.add_row("Author", details.author_name or "")
    table.add_row("Avg Rating", f"{details.avg_rating:.2f}" if details.avg_rating else "")
    table.add_row("Ratings", f"{details.ratings_count}" if details.ratings_count else "")
    table.add_row("Pages", f"{details.pages}" if details.pages else "")
    table.add_row("Format", details.format or "")
    table.add_row("Publisher", details.publisher or "")
    table.add_row("ISBN", details.isbn or "")
    table.add_row("ISBN13", details.isbn13 or "")
    table.add_row("Language", details.language or "")
    table.add_row("URL", details.url)
    if details.description:
        table.add_row(
            "Description",
            details.description[:300] + ("..." if len(details.description) > 300 else ""),
        )
    console.print(table)


@public_shelf_app.command("list")
def shelf_list(
    user: str = typer.Option(..., "--user"),
    shelf: str = typer.Option("all", "--shelf"),
    limit: int = typer.Option(20, "--limit", "-n", min=0),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """List shelf items using the public RSS feed."""
    items = get_shelf_items(user, shelf)
    if limit:
        items = items[:limit]

    if json_output:
        typer.echo(shelf_items_to_json(items))
        return

    table = Table(title=f"Shelf {shelf} for user {user}")
    table.add_column("Title", style="bold")
    table.add_column("Author")
    table.add_column("Rating", justify="right")
    table.add_column("Shelves")
    table.add_column("Added")
    for item in items:
        table.add_row(
            item.title,
            item.author or "",
            f"{item.rating}" if item.rating is not None else "",
            ",".join(item.shelves),
            item.date_added or "",
        )
    console.print(table)


@public_shelf_app.command("export")
def shelf_export(
    user: str = typer.Option(..., "--user"),
    shelf: str = typer.Option("all", "--shelf"),
    fmt: str = typer.Option("json", "--format", "-f"),
    output: Path | None = typer.Option(None, "--output", "-o"),
) -> None:
    """Export shelf items to JSON or CSV."""
    items = get_shelf_items(user, shelf)
    fmt_lower = fmt.lower()
    if fmt_lower not in {"json", "csv"}:
        raise typer.BadParameter("format must be 'json' or 'csv'")

    content = shelf_items_to_json(items) if fmt_lower == "json" else shelf_items_to_csv(items)
    if output:
        output.write_text(content, encoding="utf-8")
        return
    typer.echo(content)
