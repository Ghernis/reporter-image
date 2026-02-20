from app import report

report.build_report(
    title="Sample Report",
    subtitle="Generated with WeasyPrint + Jinja2 + Bulma",
    content="<p>This is a minimal report. Use <code>build_report()</code> with your own data, charts, and tables.</p>",
)
