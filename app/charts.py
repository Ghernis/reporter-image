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


# Palette for 10 licenses (theme-like, readable)
_COMPANY_LICENSE_PALETTE = [
    "#0451e4",  # primary
    "#009fda",  # secondary-1
    "#48c0b9",  # secondary-2
    "#27ae60",  # green
    "#2ecc71",  # light green
    "#f39c12",  # amber
    "#e67e22",  # orange
    "#e74c3c",  # red
    "#9b59b6",  # purple
    "#34495e",  # dark slate
]


def build_company_license_stacked(
    companies: list[str],
    licenses: list[str],
    company_data: list[dict[str, Any]],
    out_path: Path,
    *,
    max_license_len: int = 18,
    dpi: int = 120,
) -> str:
    """
    Stacked bar chart: X = companies, each bar = 10 segments (license counts).
    Returns path (file://) to the saved image.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    n_companies = len(companies)
    n_licenses = len(licenses)
    license_labels = [s[:max_license_len] + ("…" if len(s) > max_license_len else "") for s in licenses]
    colors = _COMPANY_LICENSE_PALETTE[:n_licenses]
    data = np.array([row["license_counts"][:n_licenses] for row in company_data], dtype=float)
    if data.shape[1] < n_licenses:
        pad = np.zeros((n_companies, n_licenses - data.shape[1]))
        data = np.hstack([data, pad])
    x = np.arange(n_companies)
    width = 0.7
    bottom = np.zeros(n_companies)
    fig, ax = plt.subplots(figsize=(10, 5))
    for i in range(n_licenses):
        ax.bar(x, data[:, i], width, label=license_labels[i], bottom=bottom, color=colors[i])
        bottom += data[:, i]
    ax.set_xticks(x)
    ax.set_xticklabels(companies, rotation=30, ha="right", fontsize=9)
    ax.set_ylabel("License count (consumed)")
    ax.set_title("Licenses by company — stacked count per license type")
    ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1), fontsize=7, ncol=1)
    fig.tight_layout(rect=[0, 0, 0.85, 1])
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight", dpi=dpi)
    plt.close(fig)
    return f"file://{out_path.resolve()}"


def build_company_heatmap_pct(
    companies: list[str],
    licenses: list[str],
    company_data: list[dict[str, Any]],
    out_path: Path,
    *,
    max_license_len: int = 22,
    dpi: int = 120,
) -> str:
    """
    Heatmap: rows = licenses, columns = companies, color = % consumed (0–100).
    Returns path (file://) to the saved image.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    n_licenses = len(licenses)
    license_labels = [s[:max_license_len] + ("…" if len(s) > max_license_len else "") for s in licenses]
    data = np.array([[row["license_pct"][i] for i in range(n_licenses)] for row in company_data]).T
    fig, ax = plt.subplots(figsize=(max(8, len(companies) * 1.8), max(5, n_licenses * 0.45)))
    im = ax.imshow(data, aspect="auto", cmap="RdYlGn_r", vmin=0, vmax=100)
    ax.set_xticks(np.arange(len(companies)))
    ax.set_yticks(np.arange(n_licenses))
    ax.set_xticklabels(companies, rotation=30, ha="right")
    ax.set_yticklabels(license_labels, fontsize=8)
    for i in range(n_licenses):
        for j in range(len(companies)):
            v = data[i, j]
            text = f"{v:.0f}" if v == v else "—"
            ax.text(j, i, text, ha="center", va="center", color="black", fontsize=7, fontweight="bold")
    plt.colorbar(im, ax=ax, label="Consumption %", shrink=0.8)
    ax.set_title("Licenses by company — consumption % (heatmap)")
    fig.tight_layout()
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight", dpi=dpi)
    plt.close(fig)
    return f"file://{out_path.resolve()}"


def build_company_assignments_removals_stacked(
    companies: list[str],
    company_data: list[dict[str, Any]],
    out_path: Path,
    *,
    dpi: int = 120,
) -> str:
    """
    Stacked bar: X = companies, green = assignments (90d), red = removals (90d).
    Returns path (file://) to the saved image.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    assignments = [row.get("assignments_90d") or 0 for row in company_data]
    removals = [row.get("removals_90d") or 0 for row in company_data]
    x = np.arange(len(companies))
    width = 0.6
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(x, assignments, width, label="Assignments (90d)", color="#27ae60")
    ax.bar(x, removals, width, bottom=assignments, label="Removals (90d)", color="#c0392b")
    ax.set_xticks(x)
    ax.set_xticklabels(companies, rotation=30, ha="right")
    ax.set_ylabel("Count")
    ax.set_title("Movement by company — assignments and removals (90d)")
    ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight", dpi=dpi)
    plt.close(fig)
    return f"file://{out_path.resolve()}"


def build_company_scatter_assignments_removals(
    company_data: list[dict[str, Any]],
    out_path: Path,
    *,
    dpi: int = 120,
) -> str:
    """
    Scatter: X = assignments (90d), Y = removals (90d), one point per company.
    Returns path (file://) to the saved image.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    companies = [row["company"] for row in company_data]
    x = np.array([row.get("assignments_90d") or 0 for row in company_data])
    y = np.array([row.get("removals_90d") or 0 for row in company_data])
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.scatter(x, y, color="#0451e4", s=120, alpha=0.8, edgecolors="white", linewidths=1.5)
    for i, name in enumerate(companies):
        ax.annotate(name, (x[i], y[i]), xytext=(6, 6), textcoords="offset points", fontsize=8, ha="left")
    ax.set_xlabel("Assignments (90d)")
    ax.set_ylabel("Removals (90d)")
    ax.set_title("Movement by company — assignments vs removals")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight", dpi=dpi)
    plt.close(fig)
    return f"file://{out_path.resolve()}"


# SharePoint report colors: orange = billable, blue = E5 entitlement, dark grey = archive
_SHAREPOINT_BILLABLE = "#e67e22"
_SHAREPOINT_E5 = "#0451e4"
_SHAREPOINT_ARCHIVE = "#34495e"


def build_sharepoint_stacked(
    companies: list[str],
    company_data: list[dict[str, Any]],
    out_path: Path,
    *,
    dpi: int = 120,
) -> str:
    """
    Stacked bar: X = companies, 3 segments = billable (orange), E5 entitlement (blue), archive (dark grey).
    Returns path (file://) to the saved image.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    billable = np.array([row.get("billable_storage") or 0 for row in company_data])
    e5 = np.array([row.get("e5_entitlement") or 0 for row in company_data])
    archive = np.array([row.get("archive") or 0 for row in company_data])
    x = np.arange(len(companies))
    width = 0.6
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(x, billable, width, label="Billable", color=_SHAREPOINT_BILLABLE)
    ax.bar(x, e5, width, bottom=billable, label="E5 Entitlement", color=_SHAREPOINT_E5)
    ax.bar(x, archive, width, bottom=billable + e5, label="Archive", color=_SHAREPOINT_ARCHIVE)
    ax.set_xticks(x)
    ax.set_xticklabels(companies, rotation=30, ha="right")
    ax.set_ylabel("Storage (GB)")
    ax.set_title("SharePoint storage by company — billable, E5 entitlement, archive")
    ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight", dpi=dpi)
    plt.close(fig)
    return f"file://{out_path.resolve()}"


def build_sharepoint_efficiency_bars(
    companies: list[str],
    company_data: list[dict[str, Any]],
    out_path: Path,
    *,
    dpi: int = 120,
) -> str:
    """
    Horizontal bar chart: each company, % efficiency = storage_used / entitlement.
    Returns path (file://) to the saved image.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    pcts = []
    for row in company_data:
        ent = row.get("e5_entitlement") or 1
        used = row.get("storage_used") or 0
        pcts.append(100.0 * used / ent if ent else 0)
    y_pos = np.arange(len(companies))
    colors = ["#e74c3c" if p > 100 else "#27ae60" for p in pcts]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.barh(y_pos, pcts, color=colors)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(companies, fontsize=9)
    ax.set_xlabel("Efficiency % (storage used / entitlement)")
    ax.axvline(x=100, color="gray", linestyle="--", linewidth=0.8)
    ax.set_title("Storage efficiency by company")
    fig.tight_layout()
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight", dpi=dpi)
    plt.close(fig)
    return f"file://{out_path.resolve()}"


def build_sharepoint_archive_ratio_bars(
    companies: list[str],
    company_data: list[dict[str, Any]],
    out_path: Path,
    *,
    dpi: int = 120,
) -> str:
    """
    Horizontal bar chart: each company, archive_ratio % = archive_storage / total_storage.
    Returns path (file://) to the saved image.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    pcts = []
    for row in company_data:
        total = row.get("storage_used") or 1
        arch = row.get("archive") or 0
        pcts.append(100.0 * arch / total if total else 0)
    y_pos = np.arange(len(companies))
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.barh(y_pos, pcts, color=_SHAREPOINT_ARCHIVE)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(companies, fontsize=9)
    ax.set_xlabel("Archive ratio % (archive / total storage)")
    ax.set_xlim(0, 100)
    ax.set_title("Archive ratio by company")
    fig.tight_layout()
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight", dpi=dpi)
    plt.close(fig)
    return f"file://{out_path.resolve()}"


def build_sharepoint_trend(
    companies: list[str],
    dates: list[str],
    trend_series: dict[str, list[float]],
    out_path: Path,
    *,
    dpi: int = 120,
) -> str:
    """
    Multi-line chart: X = dates, one line per company (storage over time).
    Returns path (file://) to the saved image.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import numpy as np
    from datetime import datetime

    x_dt = [datetime.strptime(d, "%Y-%m-%d") for d in dates]
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = ["#0451e4", "#009fda", "#48c0b9", "#27ae60", "#e67e22", "#34495e"]
    for i, name in enumerate(companies):
        vals = trend_series.get(name)
        if vals and len(vals) == len(x_dt):
            ax.plot(x_dt, vals, label=name, linewidth=1.5, color=colors[i % len(colors)])
    ax.set_xlabel("Date")
    ax.set_ylabel("Storage used (GB)")
    ax.set_title("SharePoint storage trend by company")
    ax.legend(loc="best", fontsize=8)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    plt.xticks(rotation=45, ha="right")
    fig.tight_layout()
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight", dpi=dpi)
    plt.close(fig)
    return f"file://{out_path.resolve()}"


def build_activity_buckets_barchart(
    buckets: list[dict[str, Any]],
    out_path: Path,
    *,
    dpi: int = 120,
) -> str:
    """
    Horizontal bar chart: labels = bucket names (Active, Low usage, Inactive), x = count.
    Colors: active = green, low = orange, inactive = red.
    Returns path (file://) to the saved image.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    labels = [b["label"] for b in buckets]
    counts = [int(b["count"]) for b in buckets]
    colors = ["#27ae60", "#e67e22", "#c0392b"][: len(labels)]  # green, orange, red
    if len(colors) < len(labels):
        colors = colors + ["#34495e"] * (len(labels) - len(colors))
    y_pos = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.barh(y_pos, counts, color=colors)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=10)
    ax.set_xlabel("Number of users")
    ax.set_title("User activity (E5 / E3 / F3) — active, low usage, inactive")
    fig.tight_layout()
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight", dpi=dpi)
    plt.close(fig)
    return f"file://{out_path.resolve()}"


def build_activity_breakdown_barchart(
    activity_breakdown: list[dict[str, Any]],
    out_path: Path,
    *,
    dpi: int = 120,
    max_label_len: int = 22,
) -> str:
    """
    Vertical bar chart: x = activity labels (mail, teams, etc.), y = count of users.
    Returns path (file://) to the saved image.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    labels = [b["label"][:max_label_len] + ("…" if len(b["label"]) > max_label_len else "") for b in activity_breakdown]
    counts = [int(b["count"]) for b in activity_breakdown]
    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(x, counts, color="#0451e4", width=0.6)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=35, ha="right")
    ax.set_ylabel("Number of users")
    ax.set_title("Usage breakdown — users with each activity type")
    fig.tight_layout()
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight", dpi=dpi)
    plt.close(fig)
    return f"file://{out_path.resolve()}"
