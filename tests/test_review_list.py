from pathlib import Path

from goodreads_tools.public.review_list import parse_review_list_html


def test_parse_review_list_html_sessions() -> None:
    fixture_path = Path(__file__).parent / "fixtures" / "review_list_page.html"
    html = fixture_path.read_text(encoding="utf-8")
    entries = parse_review_list_html(html, shelf="read")

    assert len(entries) == 2
    first, second = entries
    assert first.title == "Test Book"
    assert first.book_id == "123"
    assert first.pages == 300
    assert first.started_at == "2024-01-02"
    assert first.finished_at == "2024-01-10"
    assert first.shelves == ["read"]

    assert second.started_at == "2025-08-01"
    assert second.finished_at == "2024-02-14"
