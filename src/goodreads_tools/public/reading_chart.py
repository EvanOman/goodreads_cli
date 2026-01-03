from __future__ import annotations

from collections.abc import Iterable

from goodreads_tools.public.reading_stats import PagesBin, format_bin_label


def render_pages_per_day_chart(
    bins: Iterable[PagesBin],
    *,
    width: int = 100,
    height: int = 20,
    title: str | None = None,
) -> str:
    import plotext as plt

    labels = [format_bin_label(bin_item) for bin_item in bins]
    values = [round(bin_item.pages_per_day, 2) for bin_item in bins]

    plt.clear_figure()
    plt.plotsize(width, height)
    if title:
        plt.title(title)
    plt.xlabel("Date")
    plt.ylabel("Pages/day")
    plt.bar(labels, values)
    return plt.build()
