"""
Matplotlib chart builders for reports. Charts are saved to file and paths returned for Jinja.
"""
from pathlib import Path
from typing import Any


def build_top10_consumption_barchart(
    snapshots: list[dict[str, Any]],
    out_path: Path,
    *,
    max_name_len: int = 35,
    dpi: int = 120,
) -> str:
    """
    Horizontal bar chart: top 10 licenses, x = consumption % (0-100).
    Bars colored by threshold: >90% red, >70% orange, else green.
    Returns path (file://) to the saved image.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors

    names = [s["name"][:max_name_len] + ("…" if len(s["name"]) > max_name_len else "") for s in snapshots]
    pcts = [s["pct"] for s in snapshots]
    colors = []
    for p in pcts:
        if p >= 90:
            colors.append("#c0392b")  # red
        elif p >= 70:
            colors.append("#e67e22")  # orange
        else:
            colors.append("#27ae60")  # green

    fig, ax = plt.subplots(figsize=(8, 5))
    y_pos = range(len(names))
    ax.barh(y_pos, pcts, color=colors)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=9)
    ax.set_xlim(0, 100)
    ax.set_xlabel("Consumption %")
    ax.set_title("Top 10 licenses — consumption vs available")
    ax.axvline(x=100, color="gray", linestyle="--", linewidth=0.8)
    fig.tight_layout()

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight", dpi=dpi)
    plt.close(fig)

    return f"file://{out_path.resolve()}"


def build_top10_evolution_chart(
    dates: list[str],
    series: dict[str, list[float]],
    out_path: Path,
    *,
    dpi: int = 120,
) -> str:
    """
    Line chart: x = dates, y = consumption %, one line per license (top 10).
    Returns path (file://) to the saved image.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from datetime import datetime

    fig, ax = plt.subplots(figsize=(10, 5))
    # Parse dates for proper x-axis
    x = [datetime.strptime(d, "%Y-%m-%d") for d in dates]
    for label, values in series.items():
        if len(values) == len(x):
            ax.plot(x, values, label=label, linewidth=1.5)
    ax.set_xlabel("Date")
    ax.set_ylabel("Consumption %")
    ax.set_ylim(0, 105)
    ax.set_title("Top 10 licenses — consumption over time")
    ax.legend(loc="best", fontsize=7, ncol=2)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    plt.xticks(rotation=45, ha="right")
    fig.tight_layout()

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight", dpi=dpi)
    plt.close(fig)

    return f"file://{out_path.resolve()}"
