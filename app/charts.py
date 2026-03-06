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


def _trend_and_pe(values: list[float], period_days: int) -> tuple[str, str]:
    """Return (trend_str e.g. '↑ 3.2% (30d)', pe_str e.g. 'P.E.: 48 days' or 'P.E.: —')."""
    import numpy as np
    if len(values) < 2 or period_days < 1:
        return "—", "P.E.: —"
    n = min(len(values), period_days)
    y = np.array(values[-n:], dtype=float)
    x = np.arange(len(y))
    slope, intercept = np.polyfit(x, y, 1)
    change = float(y[-1] - y[0])
    trend_dir = "↑" if change >= 0 else "↓"
    trend_str = f"{trend_dir} {abs(change):.1f}% ({n}d)"
    last_pct = float(y[-1])
    if slope > 0 and last_pct < 100:
        days_to_100 = (100 - last_pct) / slope
        pe_str = f"P.E.: {int(round(days_to_100))} days"
    else:
        pe_str = "P.E.: —"
    return trend_str, pe_str


def build_top10_evolution_matrix(
    names: list[str],
    dates: list[str],
    series: dict[str, list[float]],
    out_path: Path,
    *,
    period_days: int = 30,
    dpi: int = 120,
    max_title_len: int = 22,
) -> str:
    """
    2×5 matrix of small line charts: one per license, % capacity + regression trend line.
    Each subplot title: "↑ 3.2% (30d) - P.E.: 48 days" (trend and projected exhaustion).
    Returns path (file://) to the saved image.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import numpy as np
    from datetime import datetime

    n_dates = len(dates)
    x_dt = [datetime.strptime(d, "%Y-%m-%d") for d in dates]
    x_numeric = np.arange(n_dates)

    fig, axes = plt.subplots(2, 5, figsize=(14, 6))
    axes_flat = axes.flatten()

    for idx, name in enumerate(names[:10]):
        ax = axes_flat[idx]
        values = series.get(name)
        if not values or len(values) != n_dates:
            ax.set_title(name[:max_title_len] + ("…" if len(name) > max_title_len else ""))
            ax.axis("off")
            continue
        y = np.array(values, dtype=float)
        ax.plot(x_dt, y, color="#0451e4", linewidth=1.2, label="% capacity")
        # Regression line (thin)
        slope, intercept = np.polyfit(x_numeric, y, 1)
        y_reg = slope * x_numeric + intercept
        ax.plot(x_dt, y_reg, color="#e67e22", linewidth=0.8, linestyle="--", alpha=0.9, label="trend")
        ax.set_ylim(0, 105)
        ax.tick_params(axis="both", labelsize=6)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha="right")
        trend_str, pe_str = _trend_and_pe(values, period_days)
        caption = f"{trend_str} - {pe_str}"
        title = f"{name[:max_title_len]}{'…' if len(name) > max_title_len else ''}\n{caption}"
        ax.set_title(title, fontsize=6)

    plt.suptitle("Top 10 licenses — % capacity and trend (P.E. = projected exhaustion)", fontsize=10, y=1.02)
    fig.tight_layout()

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight", dpi=dpi)
    plt.close(fig)

    return f"file://{out_path.resolve()}"


def build_top10_assignments_removals_chart(
    snapshots: list[dict[str, Any]],
    out_path: Path,
    *,
    max_name_len: int = 20,
    dpi: int = 120,
) -> str:
    """
    Stacked vertical bars per license: green = assignments (90d), red = removals (90d).
    Returns path (file://) to the saved image.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    names = [s["name"][:max_name_len] + ("…" if len(s["name"]) > max_name_len else "") for s in snapshots]
    assignments = [s.get("assignments_90d") or 0 for s in snapshots]
    removals = [s.get("removals_90d") or 0 for s in snapshots]
    x = np.arange(len(names))
    width = 0.6

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(x, assignments, width, label="Assignments (90d)", color="#27ae60")
    ax.bar(x, removals, width, bottom=assignments, label="Removals (90d)", color="#c0392b")
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("Count")
    ax.set_title("Top 10 licenses — assignments and removals (past 90 days)")
    ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight", dpi=dpi)
    plt.close(fig)

    return f"file://{out_path.resolve()}"
