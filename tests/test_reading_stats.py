from datetime import date

from goodreads_cli.models import ReadingTimelineEntry
from goodreads_cli.public.reading_stats import (
    bin_daily_pages,
    estimate_daily_pages,
    format_bin_label,
)


def test_estimate_daily_pages_single_day() -> None:
    entries = [
        ReadingTimelineEntry(
            title="One Day",
            book_id="1",
            pages=120,
            started_at="2024-01-01T00:00:00+00:00",
            finished_at="2024-01-01T23:59:59+00:00",
        )
    ]
    result = estimate_daily_pages(entries)
    assert result.daily_pages[date(2024, 1, 1)] == 120


def test_estimate_daily_pages_multi_day() -> None:
    entries = [
        ReadingTimelineEntry(
            title="Three Days",
            book_id="2",
            pages=90,
            started_at="2024-01-01T00:00:00+00:00",
            finished_at="2024-01-03T00:00:00+00:00",
        )
    ]
    result = estimate_daily_pages(entries)
    assert result.daily_pages[date(2024, 1, 1)] == 30
    assert result.daily_pages[date(2024, 1, 2)] == 30
    assert result.daily_pages[date(2024, 1, 3)] == 30


def test_estimate_daily_pages_overlap_and_reread() -> None:
    entries = [
        ReadingTimelineEntry(
            title="Overlap A",
            book_id="3",
            pages=100,
            started_at="2024-01-01T00:00:00+00:00",
            finished_at="2024-01-02T00:00:00+00:00",
        ),
        ReadingTimelineEntry(
            title="Overlap A reread",
            book_id="3",
            pages=60,
            started_at="2024-01-02T00:00:00+00:00",
            finished_at="2024-01-03T00:00:00+00:00",
        ),
    ]
    result = estimate_daily_pages(entries)
    assert result.daily_pages[date(2024, 1, 1)] == 50
    assert result.daily_pages[date(2024, 1, 2)] == 80
    assert result.daily_pages[date(2024, 1, 3)] == 30


def test_estimate_daily_pages_skips_invalid_entries() -> None:
    entries = [
        ReadingTimelineEntry(
            title="No pages",
            book_id="4",
            pages=None,
            started_at="2024-01-01T00:00:00+00:00",
            finished_at="2024-01-02T00:00:00+00:00",
        ),
        ReadingTimelineEntry(
            title="Missing dates",
            book_id="5",
            pages=10,
            started_at=None,
            finished_at="2024-01-02T00:00:00+00:00",
        ),
        ReadingTimelineEntry(
            title="End before start",
            book_id="6",
            pages=10,
            started_at="2024-01-03T00:00:00+00:00",
            finished_at="2024-01-02T00:00:00+00:00",
        ),
    ]
    result = estimate_daily_pages(entries)
    assert result.daily_pages == {}
    assert result.skipped_missing_pages == 1
    assert result.skipped_missing_dates == 1
    assert result.skipped_invalid_ranges == 1
    assert result.coerced_invalid_ranges == 0


def test_estimate_daily_pages_coerces_invalid_ranges() -> None:
    entries = [
        ReadingTimelineEntry(
            title="Inverted range",
            book_id="7",
            pages=12,
            started_at="2024-01-03T00:00:00+00:00",
            finished_at="2024-01-01T00:00:00+00:00",
        )
    ]
    result = estimate_daily_pages(entries, coerce_invalid_ranges=True)
    assert result.daily_pages[date(2024, 1, 1)] == 12
    assert result.coerced_invalid_ranges == 1


def test_bin_daily_pages() -> None:
    daily_pages = {
        date(2024, 1, 1): 10.0,
        date(2024, 1, 2): 0.0,
        date(2024, 1, 3): 30.0,
        date(2024, 1, 4): 20.0,
        date(2024, 1, 5): 0.0,
    }
    bins = bin_daily_pages(daily_pages, date(2024, 1, 1), date(2024, 1, 5), bin_days=2)
    assert len(bins) == 3
    assert bins[0].total_pages == 10.0
    assert bins[0].pages_per_day == 5.0
    assert bins[1].total_pages == 50.0
    assert bins[1].pages_per_day == 25.0
    assert bins[2].total_pages == 0.0
    assert format_bin_label(bins[2]) == "2024-01-05"
