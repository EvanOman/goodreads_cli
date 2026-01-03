from pathlib import Path

from goodreads_cli.public.book import parse_book_details


def test_parse_book_details() -> None:
    fixture_path = Path(__file__).parent / "fixtures" / "book_dune.html"
    html = fixture_path.read_text(encoding="utf-8")
    details = parse_book_details(html)

    assert details.book_id == "44767458"
    assert details.title == "Dune"
    assert details.author_name == "Frank Herbert"
    assert details.avg_rating is not None
    assert details.ratings_count is not None
    assert details.url.startswith("https://www.goodreads.com/book/show/")
