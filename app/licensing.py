"""
Data contract and builder for the Microsoft licensing summary report.
"""
from pathlib import Path
from typing import TypedDict

from app.charts import build_top10_consumption_barchart, build_top10_evolution_chart
from app.report import OUTPUT_DIR, build_report


class LicenseSnapshot(TypedDict):
    """One row per license (top 10). pct = consumed/total*100 when total > 0."""
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
    evolution_path = out_dir / "chart_top10_evolution.png"

    chart_imgs = [
        build_top10_consumption_barchart(top10, bar_path),
        build_top10_evolution_chart(dates, series, evolution_path),
    ]

    extra = {
        "top10": top10,
        "evolution_dates": dates,
        "evolution_series": series,
    }

    return build_report(
        title=title,
        subtitle=subtitle or "Top 10 licenses — consumption and evolution",
        content=content,
        chart_imgs=chart_imgs,
        table_html=table_html,
        output_html_path=output_html_path,
        output_pdf_path=output_pdf_path,
        html_only=html_only,
        template_name="report_licensing.html",
        extra_context=extra,
    )
