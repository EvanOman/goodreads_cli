import json
from pathlib import Path

from goodreads_tools.public.shelf import (
    parse_shelf_rss,
    shelf_items_to_csv,
    shelf_items_to_json,
)


def test_parse_shelf_rss() -> None:
    fixture_path = Path(__file__).parent / "fixtures" / "shelf_1_all.xml"
    xml_text = fixture_path.read_text(encoding="utf-8")
    items = parse_shelf_rss(xml_text)

    assert items
    first = items[0]
    assert first.title == "Circle of Days"
    assert first.book_id == "220337985"
    assert first.author == "Ken Follett"
    assert first.pages == 697
    assert first.date_created == "Fri, 28 Mar 2025 02:40:30 -0700"


def test_shelf_export_formats() -> None:
    fixture_path = Path(__file__).parent / "fixtures" / "shelf_1_all.xml"
    xml_text = fixture_path.read_text(encoding="utf-8")
    items = parse_shelf_rss(xml_text)[:2]

    csv_text = shelf_items_to_csv(items)
    assert csv_text.splitlines()[0].startswith("title,author,book_id")

    json_text = shelf_items_to_json(items)
    payload = json.loads(json_text)
    assert isinstance(payload, list)
    assert payload[0]["title"]
