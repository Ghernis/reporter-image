"""Generate the licensing summary report. Use demo data or pass a JSON data file."""
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

from app.licensing import (
    build_licensing_report,
    license_snapshot,
)

# Demo: top 10 licenses (name, consumed, total, assignments_90d, removals_90d)
DEMO_TOP10_RAW = [
    ("Microsoft 365 E3", 480, 500, 24, 8),
    ("Microsoft 365 E5", 220, 250, 12, 3),
    ("Office 365 E1", 1200, 1500, 45, 22),
    ("Power BI Pro", 85, 100, 5, 2),
    ("Project Plan 3", 42, 50, 3, 1),
    ("Visio Plan 2", 28, 35, 2, 0),
    ("Windows 10/11 E3", 600, 650, 18, 10),
    ("EMS E3", 180, 200, 8, 4),
    ("EMS E5", 95, 120, 6, 2),
    ("Azure AD P1", 350, 400, 15, 9),
]


def _demo_evolution_dates(days: int = 30) -> list[str]:
    end = datetime.utcnow().date()
    return [(end - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days - 1, -1, -1)]


def _demo_series(top10_pcts: list[float], days: int = 30) -> dict[str, list[float]]:
    """Fake daily evolution: slight random walk around initial pct."""
    import random
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


def load_licensing_data(path: str | Path) -> tuple[list, list[str], dict[str, list[float]]]:
    """
    Load licensing report data from a JSON file.
    Expected shape:
      {
        "top10": [ {"name": "...", "consumed": N, "total": N}, ... ],
        "dates": ["YYYY-MM-DD", ...],
        "series": { "License name": [pct, ...], ... }
      }
    Returns (top10 list of LicenseSnapshot, dates, series).
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {path}")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    top10_raw = data["top10"]
    top10 = []
    for item in top10_raw:
        snap = license_snapshot(
            item["name"],
            int(item["consumed"]),
            int(item["total"]),
        )
        if "assignments_90d" in item:
            snap["assignments_90d"] = int(item["assignments_90d"])
        if "removals_90d" in item:
            snap["removals_90d"] = int(item["removals_90d"])
        top10.append(snap)
    dates = list(data["dates"])
    series = {k: [float(x) for x in v] for k, v in data["series"].items()}
    return top10, dates, series


def main() -> None:
    data_path = os.environ["DATA_PATH"] if "DATA_PATH" in os.environ else (sys.argv[1] if len(sys.argv) > 1 else None)
    if data_path:
        top10, dates, series = load_licensing_data(data_path)
        subtitle = "Top 10 licencias — consumo y evolución"
        content = (
            "<p>This report shows consumption of the top 10 licenses as a percentage of available. "
            "Chart 1: current snapshot (bar). Chart 2: daily evolution.</p>"
        )
    else:
        top10 = []
        for t in DEMO_TOP10_RAW:
            name, consumed, total = t[0], t[1], t[2]
            snap = license_snapshot(name, consumed, total)
            if len(t) >= 5:
                snap["assignments_90d"] = t[3]
                snap["removals_90d"] = t[4]
            top10.append(snap)
        dates = _demo_evolution_dates(30)
        series = _demo_series([s["pct"] for s in top10], 30)
        subtitle = "Top 10 licencias — consumo y evolución (datos demo)"
        content = (
            "<p>Este informe muestra el consumo de las 10 principales licencias como porcentaje de las disponibles. "
            "Gráfico 1: instantánea actual (barras). Gráfico 2: evolución diaria de los últimos 30 días.</p>"
        )

    html_path, pdf_path = build_licensing_report(
        top10=top10,
        dates=dates,
        series=series,
        title="Resumen de licencias Microsoft",
        subtitle=subtitle,
        content=content,
        html_only=False,
    )
    print("HTML:", html_path)
    if pdf_path:
        print("PDF:", pdf_path)


if __name__ == "__main__":
    main()
