from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from goodreads_tools.public.reading_stats import PagesBin, format_bin_label


def render_pages_per_day_chart(
    bins: Iterable[PagesBin],
    *,
    width: int = 12,
    height: int = 6,
    title: str | None = None,
    output: Path | None = None,
) -> str | None:
    """Render a pages-per-day bar chart using matplotlib.

    Args:
        bins: Iterable of PagesBin objects with pages_per_day data
        width: Figure width in inches (default 12)
        height: Figure height in inches (default 6)
        title: Chart title
        output: Path to save PNG. If None, returns ASCII fallback.

    Returns:
        Path to saved PNG as string if output provided, else ASCII representation.
    """
    import matplotlib.dates as mdates
    import matplotlib.pyplot as plt

    bins_list = list(bins)
    if not bins_list:
        return "No data to chart."

    # Use seaborn style for clean, modern look
    plt.style.use("seaborn-v0_8-whitegrid")

    fig, ax = plt.subplots(figsize=(width, height))

    # Prepare data - convert dates to matplotlib format
    dates = [mdates.date2num(bin_item.start) for bin_item in bins_list]
    values = [bin_item.pages_per_day for bin_item in bins_list]

    # Calculate bar width based on bin size (dates are already in numeric format)
    if len(dates) > 1:
        bar_width = (dates[1] - dates[0]) * 0.8
    else:
        bar_width = 0.8

    # Create bar chart with nice styling
    bars = ax.bar(
        dates,
        values,
        width=bar_width,
        color="#4C72B0",
        edgecolor="#2E4A6E",
        linewidth=0.5,
        alpha=0.85,
    )

    # Styling
    ax.set_xlabel("Date", fontsize=11, fontweight="medium")
    ax.set_ylabel("Pages per Day", fontsize=11, fontweight="medium")

    if title:
        ax.set_title(title, fontsize=13, fontweight="bold", pad=15)

    # Format x-axis dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.xticks(rotation=45, ha="right")

    # Grid styling (background grid as requested)
    ax.set_axisbelow(True)
    ax.grid(True, axis="y", linestyle="-", alpha=0.7, color="#E0E0E0")
    ax.grid(True, axis="x", linestyle="--", alpha=0.3, color="#E0E0E0")

    # Remove top and right spines for cleaner look
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#888888")
    ax.spines["bottom"].set_color("#888888")

    # Add subtle value labels on top of bars if not too many
    if len(bars) <= 31:
        for bar, val in zip(bars, values):
            if val > 0:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + max(values) * 0.01,
                    f"{val:.0f}",
                    ha="center",
                    va="bottom",
                    fontsize=8,
                    color="#555555",
                )

    plt.tight_layout()

    if output:
        output_path = Path(output)
        fig.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        return str(output_path)
    else:
        # Return ASCII fallback using plotext if no output path
        plt.close(fig)
        try:
            import plotext as plx

            labels = [format_bin_label(bin_item) for bin_item in bins_list]
            plx.clear_figure()
            plx.plotsize(100, 20)
            if title:
                plx.title(title)
            plx.xlabel("Date")
            plx.ylabel("Pages/day")
            plx.bar(labels, values)
            return plx.build()
        except ImportError:
            return f"Chart has {len(bins_list)} bins. Use --output to save as PNG."
