"""Generate the SharePoint-by-company report. Use example data or pass a JSON data file."""
import json
import os
import sys
from pathlib import Path

from app.sharepoint_report import build_sharepoint_report


def load_sharepoint_data(path: str | Path) -> tuple[list[str], list[dict], list[str], dict]:
    """
    Load SharePoint report data from a JSON file.
    Expected shape:
      {
        "companies": ["Company A", ...],
        "company_data": [
          {
            "company": "Company A",
            "storage_used": 12000,
            "e5_entitlement": 10000,
            "archive": 2000,
            "billable_storage": 8000,
            "cost": 450,
            "archive_cost": 120
          },
          ...
        ],
        "trend_dates": ["2025-01-01", ...],
        "trend_series": { "Company A": [11000, 11500, ...], ... }
      }
    Returns (companies, company_data, trend_dates, trend_series).
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {path}")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    companies = list(data["companies"])
    company_data = []
    for row in data["company_data"]:
        company_data.append({
            "company": row["company"],
            "storage_used": int(row.get("storage_used", 0)),
            "e5_entitlement": int(row.get("e5_entitlement", 0)),
            "archive": int(row.get("archive", 0)),
            "billable_storage": int(row.get("billable_storage", 0)),
            "cost": float(row.get("cost", 0)),
            "archive_cost": float(row.get("archive_cost", 0)),
        })
    trend_dates = list(data.get("trend_dates", []))
    trend_series = {k: [float(x) for x in v] for k, v in data.get("trend_series", {}).items()}
    return companies, company_data, trend_dates, trend_series


def main() -> None:
    data_path = os.environ.get("DATA_PATH") or (sys.argv[1] if len(sys.argv) > 1 else None)
    default_data = Path(__file__).parent / "data" / "example-sharepoint-by-company.json"
    if data_path:
        companies, company_data, trend_dates, trend_series = load_sharepoint_data(data_path)
        subtitle = "Storage by company — billable, E5, archive"
    else:
        if not default_data.exists():
            print("No data file. Run: python main_sharepoint.py /path/to/sharepoint-data.json", file=sys.stderr)
            sys.exit(1)
        companies, company_data, trend_dates, trend_series = load_sharepoint_data(default_data)
        subtitle = "Storage by company (example data)"

    html_path, pdf_path = build_sharepoint_report(
        companies=companies,
        company_data=company_data,
        trend_dates=trend_dates,
        trend_series=trend_series,
        title="SharePoint drive usage by company",
        subtitle=subtitle,
        content=(
            "<p>This report shows SharePoint storage by company: stacked billable / E5 / archive, "
            "efficiency and archive ratio, and trend over time.</p>"
        ),
        html_only=False,
    )
    print("HTML:", html_path)
    if pdf_path:
        print("PDF:", pdf_path)


if __name__ == "__main__":
    main()
