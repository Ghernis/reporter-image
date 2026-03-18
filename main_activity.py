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
        subtitle = "Actividad de usuarios y ahorro potencial"
    else:
        if not default_data.exists():
            print("No hay archivo de datos. Ejecuta: python main_activity.py /ruta/al/datos-actividad.json", file=sys.stderr)
            sys.exit(1)
        buckets, activity_breakdown, top_low_score_users, cost = load_activity_data(default_data)
        subtitle = "Actividad de usuarios (datos de ejemplo)"

    html_path, pdf_path = build_activity_report(
        buckets=buckets,
        activity_breakdown=activity_breakdown,
        top_low_score_users=top_low_score_users,
        cost_per_inactive_user_per_month=cost,
        title="Actividad por usuario (E5 / E3 / F3)",
        subtitle=subtitle,
        content=(
            "<p>Este informe muestra la actividad de usuarios para licencias costosas (E5, E3, F3): "
            "activos vs bajo uso vs inactivos, ahorro potencial por usuarios inactivos, "
            "desglose de uso por tipo de actividad y usuarios con menor puntuación.</p>"
        ),
        html_only=False,
    )
    print("HTML:", html_path)
    if pdf_path:
        print("PDF:", pdf_path)


if __name__ == "__main__":
    main()
