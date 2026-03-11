"""
Single entrypoint to run any report inside the Docker image (or locally).
Usage:
  python run_reports.py [report_type] [data_path]
  python run_reports.py all                    # run all four reports (each with default data)
  python run_reports.py licensing             # licensing report (demo data if no path)
  python run_reports.py licensing /data/licensing.json
  python run_reports.py company               # company report (example data)
  python run_reports.py company /data/by-company.json
  python run_reports.py sharepoint            # SharePoint report (example data)
  python run_reports.py sharepoint /data/sharepoint.json
  python run_reports.py activity             # Activity per user (example data)
  python run_reports.py activity /data/activity.json

Report type defaults to 'licensing'. Data path defaults to DATA_PATH env or example file per report.
"""
import os
import sys
from pathlib import Path

REPORT_TYPES = ("licensing", "company", "sharepoint", "activity", "all")
DATA_DIR = Path(__file__).parent / "data"
DEFAULT_DATA = {
    "licensing": None,  # use demo data
    "company": DATA_DIR / "example-licensing-by-company.json",
    "sharepoint": DATA_DIR / "example-sharepoint-by-company.json",
    "activity": DATA_DIR / "example-activity-by-user.json",
}


def _run_licensing(data_path: str | None) -> None:
    if data_path is not None:
        os.environ["DATA_PATH"] = data_path
    from main import main as run_licensing
    run_licensing()


def _run_company(data_path: str | None) -> None:
    if data_path is not None:
        os.environ["DATA_PATH"] = data_path
    elif (DEFAULT_DATA["company"] and DEFAULT_DATA["company"].exists()):
        os.environ["DATA_PATH"] = str(DEFAULT_DATA["company"])
    from main_company import main as run_company
    run_company()


def _run_sharepoint(data_path: str | None) -> None:
    if data_path is not None:
        os.environ["DATA_PATH"] = data_path
    elif (DEFAULT_DATA["sharepoint"] and DEFAULT_DATA["sharepoint"].exists()):
        os.environ["DATA_PATH"] = str(DEFAULT_DATA["sharepoint"])
    from main_sharepoint import main as run_sharepoint
    run_sharepoint()


def _run_activity(data_path: str | None) -> None:
    if data_path is not None:
        os.environ["DATA_PATH"] = data_path
    elif (DEFAULT_DATA["activity"] and DEFAULT_DATA["activity"].exists()):
        os.environ["DATA_PATH"] = str(DEFAULT_DATA["activity"])
    from main_activity import main as run_activity
    run_activity()


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
    if data_path is None and report_type in DEFAULT_DATA and report_type != "all":
        default = DEFAULT_DATA[report_type]
        if default and default.exists():
            data_path = str(default)

    # So that mains don't treat argv[1] (e.g. "licensing") as a file path when invoked via run_reports.py
    if report_type == "licensing" and data_path is None:
        os.environ["DATA_PATH"] = ""
    elif data_path is not None:
        os.environ["DATA_PATH"] = data_path

    if report_type == "all":
        # Run all four; each uses its own default data (ignore single data_path)
        for name, data_env in [
            ("licensing", ""),  # "" = use demo data
            ("company", str(DEFAULT_DATA["company"]) if DEFAULT_DATA["company"] and DEFAULT_DATA["company"].exists() else None),
            ("sharepoint", str(DEFAULT_DATA["sharepoint"]) if DEFAULT_DATA["sharepoint"] and DEFAULT_DATA["sharepoint"].exists() else None),
            ("activity", str(DEFAULT_DATA["activity"]) if DEFAULT_DATA["activity"] and DEFAULT_DATA["activity"].exists() else None),
        ]:
            if "DATA_PATH" in os.environ:
                del os.environ["DATA_PATH"]
            if data_env is not None:
                os.environ["DATA_PATH"] = data_env
            print(f"\n--- {name} ---")
            if name == "licensing":
                _run_licensing(None)
            elif name == "company":
                _run_company(None)
            elif name == "sharepoint":
                _run_sharepoint(None)
            else:
                _run_activity(None)
        return

    if data_path is not None:
        os.environ["DATA_PATH"] = data_path

    if report_type == "licensing":
        _run_licensing(data_path)
    elif report_type == "company":
        _run_company(data_path)
    elif report_type == "sharepoint":
        _run_sharepoint(data_path)
    elif report_type == "activity":
        _run_activity(data_path)
    else:
        print(f"Unknown report type: {report_type}. Use one of: {', '.join(REPORT_TYPES)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
