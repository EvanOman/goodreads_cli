from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime, timedelta

from goodreads_cli.models import ReadingTimelineEntry


@dataclass(frozen=True)
class DailyPagesResult:
    daily_pages: dict[date, float]
    skipped_missing_pages: int = 0
    skipped_missing_dates: int = 0
    skipped_invalid_ranges: int = 0
    coerced_invalid_ranges: int = 0


@dataclass(frozen=True)
class PagesBin:
    start: date
    end: date
    pages_per_day: float
    total_pages: float
    days: int


def parse_iso_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value).date()
    except ValueError:
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None


def estimate_daily_pages(
    entries: Iterable[ReadingTimelineEntry],
    *,
    coerce_invalid_ranges: bool = False,
) -> DailyPagesResult:
    daily_pages: dict[date, float] = {}
    skipped_missing_pages = 0
    skipped_missing_dates = 0
    skipped_invalid_ranges = 0
    coerced_invalid_ranges = 0

    for entry in entries:
        if entry.pages is None or entry.pages <= 0:
            skipped_missing_pages += 1
            continue
        start = parse_iso_date(entry.started_at)
        end = parse_iso_date(entry.finished_at)
        if start is None or end is None:
            skipped_missing_dates += 1
            continue
        if end < start:
            if coerce_invalid_ranges:
                coerced_invalid_ranges += 1
                start = end
            else:
                skipped_invalid_ranges += 1
                continue
        days = (end - start).days + 1
        pages_per_day = entry.pages / days
        current = start
        while current <= end:
            daily_pages[current] = daily_pages.get(current, 0.0) + pages_per_day
            current += timedelta(days=1)

    return DailyPagesResult(
        daily_pages=daily_pages,
        skipped_missing_pages=skipped_missing_pages,
        skipped_missing_dates=skipped_missing_dates,
        skipped_invalid_ranges=skipped_invalid_ranges,
        coerced_invalid_ranges=coerced_invalid_ranges,
    )


def clip_daily_pages(
    daily_pages: dict[date, float],
    start: date,
    end: date,
) -> dict[date, float]:
    return {day: value for day, value in daily_pages.items() if start <= day <= end}


def bin_daily_pages(
    daily_pages: dict[date, float],
    start: date,
    end: date,
    bin_days: int = 1,
) -> list[PagesBin]:
    if bin_days <= 0:
        raise ValueError("bin_days must be >= 1")
    if end < start:
        raise ValueError("end date must be >= start date")

    bins: list[PagesBin] = []
    current = start
    while current <= end:
        bin_end = min(current + timedelta(days=bin_days - 1), end)
        total_pages = 0.0
        day = current
        while day <= bin_end:
            total_pages += daily_pages.get(day, 0.0)
            day += timedelta(days=1)
        days = (bin_end - current).days + 1
        pages_per_day = total_pages / days if days else 0.0
        bins.append(
            PagesBin(
                start=current,
                end=bin_end,
                pages_per_day=pages_per_day,
                total_pages=total_pages,
                days=days,
            )
        )
        current = bin_end + timedelta(days=1)
    return bins


def format_bin_label(bin_item: PagesBin) -> str:
    if bin_item.start == bin_item.end:
        return bin_item.start.isoformat()
    return f"{bin_item.start.isoformat()}..{bin_item.end.isoformat()}"
