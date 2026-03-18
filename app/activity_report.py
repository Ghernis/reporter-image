"""
Build the "activity / usage per user" report: buckets chart, savings table, breakdown chart, top 50 table.
"""
from pathlib import Path
from typing import Any

from app.charts import (
    build_activity_breakdown_barchart,
    build_activity_buckets_barchart,
)
from app.report import OUTPUT_DIR, build_report


def build_activity_report(
    buckets: list[dict[str, Any]],
    activity_breakdown: list[dict[str, Any]],
    top_low_score_users: list[dict[str, Any]],
    cost_per_inactive_user_per_month: float,
    *,
    title: str = "Actividad por usuario (E5 / E3 / F3)",
    subtitle: str | None = None,
    content: str | None = None,
    output_html_path: str | None = None,
    output_pdf_path: str | None = None,
    html_only: bool = False,
) -> tuple[str, str | None]:
    """
    Build the activity report: 2 charts + savings + top users table, then render report_activity.html.
    buckets: [{ label, count }] e.g. Active (3-5), Low (1-2), Inactive (0).
    activity_breakdown: [{ label, count }] per activity type.
    top_low_score_users: [{ user_id, display_name, score, day_since_last_activity }] (up to 50).
    cost_per_inactive_user_per_month: used for potential savings = inactive_count * this.
    Returns (path_to_html, path_to_pdf or None).
    """
    out_dir = Path(output_html_path).parent if output_html_path else OUTPUT_DIR
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    chart_imgs = [
        build_activity_buckets_barchart(buckets, out_dir / "activity_chart_buckets.png"),
        build_activity_breakdown_barchart(activity_breakdown, out_dir / "activity_chart_breakdown.png"),
    ]

    inactive_count = next(
        (int(b["count"]) for b in buckets if "inactive" in b["label"].lower() or "inactivo" in b["label"].lower()),
        0,
    )
    potential_savings = inactive_count * cost_per_inactive_user_per_month

    extra = {
        "buckets": buckets,
        "activity_breakdown": activity_breakdown,
        "top_low_score_users": top_low_score_users,
        "cost_per_inactive_user_per_month": cost_per_inactive_user_per_month,
        "inactive_count": inactive_count,
        "potential_savings": potential_savings,
    }

    default_html = str(out_dir / "report_activity.html")
    default_pdf = str(out_dir / "report_activity.pdf")
    return build_report(
        title=title,
        subtitle=subtitle or "Actividad de usuarios y ahorro potencial",
        content=content,
        chart_imgs=chart_imgs,
        table_html=None,
        output_html_path=output_html_path or default_html,
        output_pdf_path=output_pdf_path or default_pdf,
        html_only=html_only,
        template_name="report_activity.html",
        extra_context=extra,
    )
