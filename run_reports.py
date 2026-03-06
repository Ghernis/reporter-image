"""
Single entrypoint to run any report inside the Docker image (or locally).
Usage:
  python run_reports.py [report_type] [data_path]
  python run_reports.py licensing              # licensing report (demo data if no path)
  python run_reports.py licensing /data/licensing.json
  python run_reports.py company               # company report (example data)
  python run_reports.py company /data/by-company.json
  python run_reports.py sharepoint             # SharePoint report (example data)
  python run_reports.py sharepoint /data/sharepoint.json

Report type defaults to 'licensing'. Data path defaults to DATA_PATH env or example file per report.
"""
import os
import sys
from pathlib import Path

REPORT_TYPES = ("licensing", "company", "sharepoint")
DATA_DIR = Path(__file__).parent / "data"
DEFAULT_DATA = {
    "licensing": None,  # use demo data
    "company": DATA_DIR / "example-licensing-by-company.json",
    "sharepoint": DATA_DIR / "example-sharepoint-by-company.json",
}


def main() -> None:
    argv = [a for a in sys.argv[1:] if not a.startswith("-")]
    report_type = "licensing"
    data_path = os.environ.get("DATA_PATH")

    if argv:
        first = argv[0]
        if first in REPORT_TYPES:
            report_type = first
            data_path = data_path or (argv[1] if len(argv) > 1 else None)
        else:
            data_path = data_path or first
    if data_path is None and report_type in DEFAULT_DATA:
        default = DEFAULT_DATA[report_type]
        if default and default.exists():
            data_path = str(default)

    if data_path is not None:
        os.environ["DATA_PATH"] = data_path

    if report_type == "licensing":
        from main import main as run_licensing
        run_licensing()
    elif report_type == "company":
        from main_company import main as run_company
        run_company()
    elif report_type == "sharepoint":
        from main_sharepoint import main as run_sharepoint
        run_sharepoint()
    else:
        print(f"Unknown report type: {report_type}. Use one of: {', '.join(REPORT_TYPES)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
