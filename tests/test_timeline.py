import json
from pathlib import Path

from goodreads_cli.public.shelf import parse_shelf_rss
from goodreads_cli.public.timeline import build_reading_timeline, timeline_entries_to_jsonl


def test_build_reading_timeline_jsonl() -> None:
    fixture_path = Path(__file__).parent / "fixtures" / "shelf_1_all.xml"
    xml_text = fixture_path.read_text(encoding="utf-8")
    items = parse_shelf_rss(xml_text)

    entries = build_reading_timeline(items)
    assert entries
    first = entries[0]
    assert first.title == "Circle of Days"
    assert first.pages == 697
    assert first.started_at == "2025-12-27T00:05:57-08:00"
    assert first.finished_at == "2025-12-27T00:00:00+00:00"

    jsonl = timeline_entries_to_jsonl(entries[:2])
    lines = jsonl.splitlines()
    assert len(lines) == 2
    payload = json.loads(lines[0])
    assert payload["title"] == "Circle of Days"
    assert payload["pages"] == 697
