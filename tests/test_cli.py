import json
import re

from typer.testing import CliRunner

from goodreads_cli.cli import app
from goodreads_cli.models import BookDetails, ReadingTimelineEntry, SearchItem, ShelfItem

runner = CliRunner()


def _strip_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


def test_cli_search_json(monkeypatch) -> None:
    def fake_search_books(_: str) -> list[SearchItem]:
        return [
            SearchItem.model_validate(
                {
                    "bookId": "1",
                    "title": "Fake Book",
                    "bookUrl": "/book/show/1-fake-book",
                    "avgRating": 4.5,
                    "ratingsCount": 10,
                    "author": {"id": 9, "name": "Test Author"},
                }
            )
        ]

    monkeypatch.setattr("goodreads_cli.cli.search_books", fake_search_books)
    result = runner.invoke(app, ["public", "search", "Fake", "--json"])
    assert result.exit_code == 0

    payload = json.loads(_strip_ansi(result.stdout))
    assert payload[0]["title"] == "Fake Book"
    assert payload[0]["bookId"] == "1"


def test_cli_book_json(monkeypatch) -> None:
    def fake_book_details(_: str) -> BookDetails:
        return BookDetails(
            book_id="123",
            title="Example",
            url="https://www.goodreads.com/book/show/123",
            author_name="Jane Author",
            avg_rating=4.1,
            ratings_count=55,
        )

    monkeypatch.setattr("goodreads_cli.cli.get_book_details", fake_book_details)
    result = runner.invoke(app, ["public", "book", "show", "123", "--json"])
    assert result.exit_code == 0
    payload = json.loads(_strip_ansi(result.stdout))
    assert payload["title"] == "Example"
    assert payload["author_name"] == "Jane Author"


def test_cli_shelf_export_csv(monkeypatch) -> None:
    def fake_shelf_items(_: str, __: str) -> list[ShelfItem]:
        return [
            ShelfItem(
                title="Shelf Book",
                link="https://www.goodreads.com/book/show/1",
                book_id="1",
                author="A Writer",
                rating=5,
                shelves=["read"],
            )
        ]

    monkeypatch.setattr("goodreads_cli.cli.get_shelf_items", fake_shelf_items)
    result = runner.invoke(
        app,
        ["public", "shelf", "export", "--user", "1", "--shelf", "all", "--format", "csv"],
    )
    assert result.exit_code == 0
    assert "title,author,book_id,link" in result.stdout


def test_cli_shelf_timeline_jsonl(monkeypatch) -> None:
    def fake_timeline(_: str, __: str, **___) -> list[ReadingTimelineEntry]:
        return [
            ReadingTimelineEntry(
                title="Timeline Book",
                book_id="42",
                pages=321,
                started_at="2024-01-01T00:00:00+00:00",
                finished_at="2024-01-10T00:00:00+00:00",
                shelves=["read"],
            )
        ]

    monkeypatch.setattr("goodreads_cli.cli.get_reading_timeline", fake_timeline)
    result = runner.invoke(app, ["public", "shelf", "timeline", "--user", "1"])
    assert result.exit_code == 0
    payload = json.loads(_strip_ansi(result.stdout))
    assert payload["title"] == "Timeline Book"
    assert payload["pages"] == 321


def test_cli_shelf_chart(monkeypatch) -> None:
    def fake_timeline(_: str, __: str, **___) -> list[ReadingTimelineEntry]:
        return [
            ReadingTimelineEntry(
                title="Chart Book",
                book_id="99",
                pages=300,
                started_at="2024-01-01T00:00:00+00:00",
                finished_at="2024-01-03T00:00:00+00:00",
            )
        ]

    def fake_chart(*_: object, **__: object) -> str:
        return "CHART"

    monkeypatch.setattr("goodreads_cli.cli.get_reading_timeline", fake_timeline)
    monkeypatch.setattr("goodreads_cli.cli.render_pages_per_day_chart", fake_chart)
    result = runner.invoke(app, ["public", "shelf", "chart", "--user", "1"])
    assert result.exit_code == 0
    assert "CHART" in result.stdout
