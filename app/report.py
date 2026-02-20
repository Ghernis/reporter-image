"""
Build HTML from Jinja2 (with optional matplotlib charts and pandas tables),
then render to PDF via WeasyPrint.
"""
import os
import tempfile
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML, CSS


# Paths: assume we run from /app in the container
APP_DIR = Path(os.environ.get("APP_DIR", "/app"))
TEMPLATES_DIR = APP_DIR / "templates"
STATIC_DIR = APP_DIR / "static"
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", "/output"))


def build_report(
    title: str = "Report",
    subtitle: str | None = None,
    content: str | None = None,
    chart_imgs: list[str] | None = None,
    table_html: str | None = None,
    output_html_path: str | None = None,
    output_pdf_path: str | None = None,
) -> tuple[str, str]:
    """
    Render Jinja2 template with given data, then generate PDF with WeasyPrint.
    Returns (path_to_html, path_to_pdf).
    """
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(("html", "xml")),
    )
    template = env.get_template("report.html")
    html_string = template.render(
        title=title,
        subtitle=subtitle,
        content=content or "",
        chart_imgs=chart_imgs or [],
        table_html=table_html,
    )

    html_path = output_html_path or str(OUTPUT_DIR / "report.html")
    pdf_path = output_pdf_path or str(OUTPUT_DIR / "report.pdf")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    # Write HTML for debugging or standalone use
    Path(html_path).parent.mkdir(parents=True, exist_ok=True)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_string)

    # WeasyPrint: base_url so /static/... resolves to /app/static/...
    html_doc = HTML(string=html_string, base_url=str(APP_DIR) + "/")
    # Optional: attach print.css again for certainty (already in template)
    print_css = STATIC_DIR / "css" / "print.css"
    stylesheets = [CSS(filename=str(print_css))] if print_css.exists() else []
    html_doc.write_pdf(pdf_path, stylesheets=stylesheets)

    return html_path, pdf_path


def main() -> None:
    """Example entrypoint: generate a minimal report (optionally with a chart)."""
    import sys

    # Optional: use matplotlib to add a sample chart
    chart_imgs = []
    if "with-chart" in sys.argv:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(["A", "B", "C"], [10, 20, 15])
        ax.set_title("Sample chart")
        chart_path = Path(tempfile.gettempdir()) / "chart.png"
        fig.savefig(chart_path, bbox_inches="tight", dpi=100)
        plt.close()
        chart_imgs.append(f"file://{chart_path}")

    build_report(
        title="Sample Report",
        subtitle="Generated with WeasyPrint + Jinja2 + Bulma",
        content="<p>This is a minimal report. Use <code>build_report()</code> with your own data, charts, and tables.</p>",
        chart_imgs=chart_imgs if chart_imgs else None,
    )
    print("Report written to", OUTPUT_DIR)


if __name__ == "__main__":
    main()
