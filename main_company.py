"""Generate the licenses-by-company report. Use example data or pass a JSON data file."""
import json
import os
import sys
from pathlib import Path

from app.company_report import build_company_report


def load_company_data(path: str | Path) -> tuple[list[str], list[str], list[dict]]:
    """
    Load company report data from a JSON file.
    Expected shape:
      {
        "companies": ["Company A", ...],
        "licenses": ["Microsoft 365 E3", ...],
        "company_data": [
          {
            "company": "Company A",
            "license_counts": [120, 80, ...],
            "license_pct": [96, 88, ...],
            "assignments_90d": 150,
            "removals_90d": 45
          },
          ...
        ]
      }
    Returns (companies, licenses, company_data).
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {path}")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    companies = list(data["companies"])
    licenses = list(data["licenses"])
    company_data = []
    for row in data["company_data"]:
        company_data.append({
            "company": row["company"],
            "license_counts": [int(x) for x in row["license_counts"]],
            "license_pct": [float(x) for x in row["license_pct"]],
            "assignments_90d": int(row.get("assignments_90d", 0)),
            "removals_90d": int(row.get("removals_90d", 0)),
        })
    return companies, licenses, company_data


def main() -> None:
    data_path = os.environ.get("DATA_PATH") or (sys.argv[1] if len(sys.argv) > 1 else None)
    default_data = Path(__file__).parent / "data" / "example-licensing-by-company.json"
    if data_path:
        companies, licenses, company_data = load_company_data(data_path)
        subtitle = "Top 10 licenses across companies"
    else:
        if not default_data.exists():
            print("No data file. Run: python main_company.py /path/to/company-data.json", file=sys.stderr)
            sys.exit(1)
        companies, licenses, company_data = load_company_data(default_data)
        subtitle = "Top 10 licenses across companies (example data)"

    html_path, pdf_path = build_company_report(
        companies=companies,
        licenses=licenses,
        company_data=company_data,
        title="Licenses by company",
        subtitle=subtitle,
        content=(
            "<p>This report shows license consumption and movement by company: "
            "stacked counts per license type, consumption % heatmap, assignments/removals, and scatter.</p>"
        ),
        html_only=False,
    )
    print("HTML:", html_path)
    if pdf_path:
        print("PDF:", pdf_path)


if __name__ == "__main__":
    main()
