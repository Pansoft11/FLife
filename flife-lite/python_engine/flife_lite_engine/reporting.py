from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def render_report_html(report: dict[str, Any]) -> str:
    title = html.escape(report.get("title", "FLIFE Lite Fatigue Report"))
    project = html.escape(report.get("project", "Untitled Project"))
    material = html.escape(report.get("material", "Not specified"))
    method = html.escape(report.get("method", "Dirlik"))
    life = html.escape(str(report.get("life_seconds", "Pending")))
    conclusion = html.escape(report.get("conclusion", "Review fatigue life against project acceptance criteria."))
    assumptions = html.escape(report.get("assumptions", "Linear damage accumulation using configured SN curve parameters."))
    standards = html.escape(report.get("standards", "ASTM E1049 rainflow counting reference; project-specific durability criteria."))
    signature = html.escape(report.get("digital_signature", "Unsigned engineering draft"))
    theme = report.get("theme", "light")
    dark = theme == "dark"
    background = "#0b1118" if dark else "#ffffff"
    foreground = "#d7e1ea" if dark else "#17202a"
    panel = "#111827" if dark else "#f3f6f9"
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    payload = html.escape(json.dumps(report, indent=2))
    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <style>
    body {{ font-family: Arial, sans-serif; color: {foreground}; background: {background}; margin: 42px; }}
    h1 {{ color: #0f4c5c; }}
    .cover {{ border-bottom: 4px solid #4fd1c5; padding-bottom: 24px; margin-bottom: 32px; }}
    .grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }}
    .box {{ border: 1px solid #d8e1e8; padding: 14px; border-radius: 6px; }}
    pre {{ background: {panel}; padding: 16px; white-space: pre-wrap; }}
  </style>
</head>
<body>
  <section class="cover">
    <h1>{title}</h1>
    <p><strong>Project:</strong> {project}</p>
    <p><strong>Generated:</strong> {generated}</p>
  </section>
  <section class="grid">
    <div class="box"><strong>Material</strong><br>{material}</div>
    <div class="box"><strong>Solver</strong><br>{method}</div>
    <div class="box"><strong>Predicted Life</strong><br>{life} seconds</div>
    <div class="box"><strong>Pass/Fail</strong><br>{html.escape(report.get("pass_fail", "Engineering review required"))}</div>
  </section>
  <h2>Executive Summary</h2>
  <p>{html.escape(report.get("summary", "Fatigue analysis completed using configured project settings."))}</p>
  <h2>Methodology</h2>
  <p>FLIFE Lite applies fatigue life prediction using the selected solver, material SN parameters, cycle counting, and damage accumulation assumptions.</p>
  <h2>Simulation Assumptions</h2>
  <p>{assumptions}</p>
  <h2>Standards References</h2>
  <p>{standards}</p>
  <h2>Engineering Conclusions</h2>
  <p>{conclusion}</p>
  <h2>Traceability</h2>
  <p><strong>Digital Signature:</strong> {signature}</p>
  <h2>Trace Data</h2>
  <pre>{payload}</pre>
</body>
</html>"""


def write_report_bundle(output_dir: str | Path, report: dict[str, Any]) -> dict[str, str]:
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    html_path = target / "flife-report.html"
    docx_ready_path = target / "flife-report-docx-ready.json"
    html_path.write_text(render_report_html(report), encoding="utf-8")
    docx_ready_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return {"html": str(html_path), "docx_ready": str(docx_ready_path)}
