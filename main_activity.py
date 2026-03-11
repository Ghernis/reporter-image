"""Generate the activity-per-user report. Use example data or pass a JSON data file."""
import json
import os
import sys
from pathlib import Path

from app.activity_report import build_activity_report


def load_activity_data(path: str | Path) -> tuple[list, list, list, float]:
    """
    Load activity report data from a JSON file.
    Expected shape:
      {
        "cost_per_inactive_user_per_month": 12.5,
        "buckets": [ { "label": "Active (3-5)", "count": 280 }, ... ],
        "activity_breakdown": [ { "label": "Mail (30d)", "count": 420 }, ... ],
        "top_low_score_users": [ { "user_id", "display_name", "score", "day_since_last_activity" }, ... ]
      }
    Returns (buckets, activity_breakdown, top_low_score_users, cost_per_inactive_user_per_month).
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {path}")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    buckets = list(data["buckets"])
    activity_breakdown = list(data["activity_breakdown"])
    top = list(data.get("top_low_score_users", []))[:50]
    cost = float(data.get("cost_per_inactive_user_per_month", 0))
    return buckets, activity_breakdown, top, cost


def main() -> None:
    data_path = os.environ["DATA_PATH"] if "DATA_PATH" in os.environ else (sys.argv[1] if len(sys.argv) > 1 else None)
    default_data = Path(__file__).parent / "data" / "example-activity-by-user.json"
    if data_path:
        buckets, activity_breakdown, top_low_score_users, cost = load_activity_data(data_path)
        subtitle = "User activity and potential savings"
    else:
        if not default_data.exists():
            print("No data file. Run: python main_activity.py /path/to/activity-data.json", file=sys.stderr)
            sys.exit(1)
        buckets, activity_breakdown, top_low_score_users, cost = load_activity_data(default_data)
        subtitle = "User activity (example data)"

    html_path, pdf_path = build_activity_report(
        buckets=buckets,
        activity_breakdown=activity_breakdown,
        top_low_score_users=top_low_score_users,
        cost_per_inactive_user_per_month=cost,
        title="Activity per user (E5 / E3 / F3)",
        subtitle=subtitle,
        content=(
            "<p>This report shows user activity for expensive licenses (E5, E3, F3): "
            "active vs low usage vs inactive, potential savings from inactive users, "
            "usage breakdown by activity type, and top users with lowest score.</p>"
        ),
        html_only=False,
    )
    print("HTML:", html_path)
    if pdf_path:
        print("PDF:", pdf_path)


if __name__ == "__main__":
    main()
