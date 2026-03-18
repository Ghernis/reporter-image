"""
Data contract and builder for the Microsoft licensing summary report.
"""
from pathlib import Path
from typing import TypedDict

from app.charts import (
    build_top10_assignments_removals_chart,
    build_top10_consumption_barchart,
    build_top10_evolution_matrix,
)
from app.report import OUTPUT_DIR, build_report


class LicenseSnapshot(TypedDict):
    """One row per license (top 10). pct = consumed/total*100 when total > 0. May include assignments_90d, removals_90d."""
    name: str
    consumed: int
    total: int
    pct: float


def license_snapshot(name: str, consumed: int, total: int) -> LicenseSnapshot:
    """Build a LicenseSnapshot with pct derived from consumed/total."""
    pct = (consumed / total * 100.0) if total > 0 else 0.0
    return LicenseSnapshot(name=name, consumed=consumed, total=total, pct=pct)


# Evolution: dates = list of "YYYY-MM-DD", series = dict license_name -> list of pct (same length as dates)


def build_licensing_report(
    top10: list[LicenseSnapshot],
    dates: list[str],
    series: dict[str, list[float]],
    *,
    title: str = "Microsoft licensing summary",
    subtitle: str | None = None,
    content: str | None = None,
    table_html: str | None = None,
    output_html_path: str | None = None,
    output_pdf_path: str | None = None,
    html_only: bool = False,
) -> tuple[str, str | None]:
    """
    Build the licensing report: generate bar chart and evolution chart, then render
    report_licensing.html. Returns (path_to_html, path_to_pdf or None).
    """
    out_dir = Path(output_html_path).parent if output_html_path else OUTPUT_DIR
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    bar_path = out_dir / "chart_top10_bar.png"
    matrix_path = out_dir / "chart_top10_evolution_matrix.png"
    names = [s["name"] for s in top10]

    chart_imgs = [
        build_top10_consumption_barchart(top10, bar_path),
        build_top10_evolution_matrix(names, dates, series, matrix_path),
    ]

    has_activity_90d = any(
        s.get("assignments_90d") is not None or s.get("removals_90d") is not None
        for s in top10
    )
    if has_activity_90d:
        ar_path = out_dir / "chart_top10_assignments_removals.png"
        chart_imgs.append(build_top10_assignments_removals_chart(top10, ar_path))
    extra = {
        "top10": top10,
        "evolution_dates": dates,
        "evolution_series": series,
        "has_activity_90d": has_activity_90d,
    }

    return build_report(
        title=title,
        subtitle=subtitle or "Top 10 licencias — consumo y evolución",
        content=content,
        chart_imgs=chart_imgs,
        table_html=table_html,
        output_html_path=output_html_path,
        output_pdf_path=output_pdf_path,
        html_only=html_only,
        template_name="report_licensing.html",
        extra_context=extra,
    )
