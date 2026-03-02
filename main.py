"""Generate the licensing summary report with demo data (replace with real Graph/Azure data)."""
from datetime import datetime, timedelta
import random

from app.licensing import (
    build_licensing_report,
    license_snapshot,
)

# Demo: top 10 licenses (name, consumed, total)
DEMO_TOP10_RAW = [
    ("Microsoft 365 E3", 480, 500),
    ("Microsoft 365 E5", 220, 250),
    ("Office 365 E1", 1200, 1500),
    ("Power BI Pro", 85, 100),
    ("Project Plan 3", 42, 50),
    ("Visio Plan 2", 28, 35),
    ("Windows 10/11 E3", 600, 650),
    ("EMS E3", 180, 200),
    ("EMS E5", 95, 120),
    ("Azure AD P1", 350, 400),
]


def _demo_evolution_dates(days: int = 30) -> list[str]:
    end = datetime.utcnow().date()
    return [(end - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days - 1, -1, -1)]


def _demo_series(top10_pcts: list[float], days: int = 30) -> dict[str, list[float]]:
    """Fake daily evolution: slight random walk around initial pct."""
    names = [r[0] for r in DEMO_TOP10_RAW]
    series = {}
    for i, name in enumerate(names):
        base = top10_pcts[i]
        values = []
        for _ in range(days):
            base = max(0, min(100, base + random.uniform(-2, 2)))
            values.append(round(base, 1))
        series[name] = values
    return series


def main() -> None:
    top10 = [license_snapshot(name, consumed, total) for name, consumed, total in DEMO_TOP10_RAW]
    dates = _demo_evolution_dates(30)
    series = _demo_series([s["pct"] for s in top10], 30)

    html_path, pdf_path = build_licensing_report(
        top10=top10,
        dates=dates,
        series=series,
        title="Microsoft licensing summary",
        subtitle="Top 10 licenses — consumption and evolution (demo data)",
        content=(
            "<p>This report shows consumption of the top 10 licenses as a percentage of available. "
            "Chart 1: current snapshot (bar). Chart 2: daily evolution over the last 30 days.</p>"
        ),
        html_only=False
    )
    print("HTML:", html_path)
    if pdf_path:
        print("PDF:", pdf_path)


if __name__ == "__main__":
    main()
