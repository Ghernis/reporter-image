"""
Build the "SharePoint drive usage by company" report: stacked storage, table, efficiency bars, archive ratio, trend.
"""
from pathlib import Path
from typing import Any

from app.charts import (
    build_sharepoint_archive_ratio_bars,
    build_sharepoint_efficiency_bars,
    build_sharepoint_stacked,
    build_sharepoint_trend,
)
from app.report import OUTPUT_DIR, build_report


def build_sharepoint_report(
    companies: list[str],
    company_data: list[dict[str, Any]],
    trend_dates: list[str],
    trend_series: dict[str, list[float]],
    *,
    title: str = "SharePoint drive usage by company",
    subtitle: str | None = None,
    content: str | None = None,
    output_html_path: str | None = None,
    output_pdf_path: str | None = None,
    html_only: bool = False,
) -> tuple[str, str | None]:
    """
    Build the SharePoint report: 4 charts + table, then render report_sharepoint.html.
    company_data: list of {company, storage_used, e5_entitlement, archive, billable_storage, cost, archive_cost}.
    trend_series: { company_name: [values] } same length as trend_dates.
    Returns (path_to_html, path_to_pdf or None).
    """
    out_dir = Path(output_html_path).parent if output_html_path else OUTPUT_DIR
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    chart_imgs = [
        build_sharepoint_stacked(companies, company_data, out_dir / "sharepoint_chart_stacked.png"),
        build_sharepoint_efficiency_bars(companies, company_data, out_dir / "sharepoint_chart_efficiency.png"),
        build_sharepoint_archive_ratio_bars(companies, company_data, out_dir / "sharepoint_chart_archive_ratio.png"),
        build_sharepoint_trend(companies, trend_dates, trend_series, out_dir / "sharepoint_chart_trend.png"),
    ]

    extra = {
        "companies": companies,
        "company_data": company_data,
        "trend_dates": trend_dates,
        "trend_series": trend_series,
    }

    default_html = str(out_dir / "report_sharepoint.html")
    default_pdf = str(out_dir / "report_sharepoint.pdf")
    return build_report(
        title=title,
        subtitle=subtitle or "Almacenamiento por empresa — facturable, E5, archive",
        content=content,
        chart_imgs=chart_imgs,
        table_html=None,
        output_html_path=output_html_path or default_html,
        output_pdf_path=output_pdf_path or default_pdf,
        html_only=html_only,
        template_name="report_sharepoint.html",
        extra_context=extra,
    )
