"""
Build the "licenses by company" report: 4 charts (stacked counts, heatmap, movement stacked, scatter).
"""
from pathlib import Path
from typing import Any

from app.charts import (
    build_company_assignments_removals_stacked,
    build_company_heatmap_pct,
    build_company_license_stacked,
    build_company_scatter_assignments_removals,
)
from app.report import OUTPUT_DIR, build_report


def build_company_report(
    companies: list[str],
    licenses: list[str],
    company_data: list[dict[str, Any]],
    *,
    title: str = "Licenses by company",
    subtitle: str | None = None,
    content: str | None = None,
    table_html: str | None = None,
    output_html_path: str | None = None,
    output_pdf_path: str | None = None,
    html_only: bool = False,
) -> tuple[str, str | None]:
    """
    Build the company report: 4 charts then render report_company.html.
    company_data: list of {company, license_counts [10], license_pct [10], assignments_90d, removals_90d}.
    Returns (path_to_html, path_to_pdf or None).
    """
    out_dir = Path(output_html_path).parent if output_html_path else OUTPUT_DIR
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    chart_imgs = [
        build_company_license_stacked(companies, licenses, company_data, out_dir / "company_chart_stacked.png"),
        build_company_heatmap_pct(companies, licenses, company_data, out_dir / "company_chart_heatmap.png"),
        build_company_assignments_removals_stacked(companies, company_data, out_dir / "company_chart_movement.png"),
        build_company_scatter_assignments_removals(company_data, out_dir / "company_chart_scatter.png"),
    ]

    extra = {
        "companies": companies,
        "licenses": licenses,
        "company_data": company_data,
    }

    default_html = str(out_dir / "report_company.html")
    default_pdf = str(out_dir / "report_company.pdf")
    return build_report(
        title=title,
        subtitle=subtitle or "Top 10 licenses across companies",
        content=content,
        chart_imgs=chart_imgs,
        table_html=table_html,
        output_html_path=output_html_path or default_html,
        output_pdf_path=output_pdf_path or default_pdf,
        html_only=html_only,
        template_name="report_company.html",
        extra_context=extra,
    )
