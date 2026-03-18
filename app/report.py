"""
Build HTML from Jinja2 (with optional matplotlib charts and pandas tables),
then render to PDF via WeasyPrint when native libs (Pango) are available.
"""
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape


# Paths: assume we run from /app in the container, or project root locally
APP_DIR = Path(os.environ.get("APP_DIR", Path(__file__).resolve().parent.parent))
TEMPLATES_DIR = APP_DIR / "templates"
STATIC_DIR = APP_DIR / "static"
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", APP_DIR / "output"))


def _weasyprint_available() -> bool:
    """True if WeasyPrint's native libs (Pango, etc.) can be loaded."""
    try:
        from weasyprint import HTML  # noqa: F401
        return True
    except OSError:
        return False


def build_report(
    title: str = "Report",
    subtitle: str | None = None,
    content: str | None = None,
    chart_imgs: list[str] | None = None,
    table_html: str | None = None,
    output_html_path: str | None = None,
    output_pdf_path: str | None = None,
    html_only: bool = False,
    template_name: str = "report.html",
    extra_context: dict | None = None,
) -> tuple[str, str | None]:
    """
    Render Jinja2 template with given data, then generate PDF with WeasyPrint if available.
    Returns (path_to_html, path_to_pdf or None if PDF skipped).
    On Windows without Pango, only HTML is written unless you use Docker.
    """
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(("html", "xml")),
    )
    template = env.get_template(template_name)
    context = {
        "title": title,
        "subtitle": subtitle,
        "content": content or "",
        "chart_imgs": chart_imgs or [],
        "table_html": table_html,
        "generated_date": datetime.now().strftime("%Y-%m-%d"),
        "source": "Database",
        "from_type": "Automation | Manual",
    }
    if extra_context:
        context.update(extra_context)
    html_string = template.render(**context)

    html_path = output_html_path or str(OUTPUT_DIR / "report.html")
    pdf_path = output_pdf_path or str(OUTPUT_DIR / "report.pdf")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    Path(html_path).parent.mkdir(parents=True, exist_ok=True)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_string)

    pdf_written: str | None = None
    if not html_only and _weasyprint_available():
        from weasyprint import HTML, CSS
        from weasyprint.text.fonts import FontConfiguration

        font_config = FontConfiguration()
        html_doc = HTML(string=html_string, base_url=str(APP_DIR) + "/")
        # Load Bulma first, then theme (fonts + overrides), then print + report-pdf (WeasyPrint-friendly fallback)
        stylesheets = []
        for name in ("bulma.min.css", "theme.css", "print.css", "report-pdf.css"):
            path = STATIC_DIR / "css" / name
            if path.exists():
                stylesheets.append(CSS(filename=str(path), font_config=font_config))
        html_doc.write_pdf(pdf_path, stylesheets=stylesheets, font_config=font_config)
        pdf_written = pdf_path
    elif not html_only:
        print(
            "PDF skipped (WeasyPrint needs Pango/GObject; not available on this system).\n"
            "HTML written to:", html_path, "\n"
            "To get PDF: run with Docker, or install Pango (e.g. MSYS2 on Windows).",
            file=sys.stderr,
        )

    return html_path, pdf_written


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

    html_path, pdf_path = build_report(
        title="Sample Report",
        subtitle="Generated with WeasyPrint + Jinja2 + Bulma",
        content="<p>This is a minimal report. Use <code>build_report()</code> with your own data, charts, and tables.</p>",
        chart_imgs=chart_imgs if chart_imgs else None,
    )
    print("HTML:", html_path)
    if pdf_path:
        print("PDF:", pdf_path)


if __name__ == "__main__":
    main()
