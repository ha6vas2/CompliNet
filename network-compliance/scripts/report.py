from pathlib import Path
from typing import Any, Dict, List



def build_rule_table_rows(results: List[Dict[str, str]]) -> str:
    rows = []
    for result in results:
        status_class = "pass" if result["status"] == "PASS" else "fail"
        rows.append(
            f"<tr><td>{result['rule_id']}</td><td>{result['name']}</td>"
            f"<td>{result['status']}</td><td>{result['severity']}</td>"
            f"<td>{result['remediation']}</td></tr>"
        )
    return "\n".join(rows)


def build_html(report_data: Dict[str, object], diff_text: str) -> str:
    rule_rows = build_rule_table_rows(report_data["results"])
    compliant_text = "Compliant" if report_data["compliant"] else "Non-compliant"
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Compliance Report for {report_data['device_name']}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; }}
    h1 {{ margin-bottom: 0; }}
    .summary {{ margin: 16px 0; }}
    .pass {{ color: green; }}
    .fail {{ color: red; }}
    table {{ border-collapse: collapse; width: 100%; margin-bottom: 24px; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
    th {{ background: #f4f4f4; }}
    pre {{ background: #f8f8f8; padding: 16px; border: 1px solid #ddd; white-space: pre-wrap; }}
  </style>
</head>
<body>
  <h1>Compliance Report: {report_data['device_name']}</h1>
  <div class="summary">
    <p><strong>Score:</strong> {report_data['score']}</p>
    <p><strong>Status:</strong> {compliant_text}</p>
  </div>
  <h2>Rule Results</h2>
  <table>
    <thead>
      <tr><th>ID</th><th>Name</th><th>Status</th><th>Severity</th><th>Remediation</th></tr>
    </thead>
    <tbody>
      {rule_rows}
    </tbody>
  </table>
  <h2>Configuration Drift Diff</h2>
  <pre>{diff_text or 'No diff output available.'}</pre>
</body>
</html>
"""


def save_report(report_data: Dict[str, object], diff_text: str, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(build_html(report_data, diff_text), encoding="utf-8")
    return output_path


def build_daily_summary_html(all_reports: List[Dict[str, Any]]) -> str:
    total_devices = len(all_reports)
    compliant_devices = sum(1 for r in all_reports if r.get("compliant"))
    non_compliant_devices = total_devices - compliant_devices
    avg_score = round(sum(r.get("score", 0) for r in all_reports) / max(total_devices, 1), 1)

    device_rows = []
    failed_rules_summary = []

    for report in all_reports:
        device_name = report.get("device_name", "Unknown")
        score = report.get("score", 0)
        is_compliant = report.get("compliant", False)
        status_badge = '<span style="color: green; font-weight: bold;">Compliant</span>' if is_compliant else '<span style="color: red; font-weight: bold;">Non-Compliant</span>'

        results = report.get("results", [])
        failed_rules = [res for res in results if res.get("status") in ("FAIL", "WARN")]

        device_rows.append(
            f"<tr><td><strong>{device_name}</strong></td><td>{status_badge}</td><td>{score} / 100</td><td>{len(failed_rules)}</td></tr>"
        )

        for failed in failed_rules:
            failed_rules_summary.append(
                f"<tr><td>{device_name}</td><td>{failed.get('rule_id')}</td><td>{failed.get('name')}</td>"
                f"<td><span style='color:{'orange' if failed.get('status')=='WARN' else 'red'};'>{failed.get('status')}</span></td>"
                f"<td>{failed.get('severity')}</td><td>{failed.get('remediation')}</td></tr>"
            )

    failed_table = "\n".join(failed_rules_summary) if failed_rules_summary else "<tr><td colspan='6'>All devices are 100% compliant!</td></tr>"
    device_table = "\n".join(device_rows)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>CompliNet - Daily Compliance Executive Summary</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 32px; background: #f9fafb; color: #111827; }}
    h1 {{ color: #1e293b; margin-bottom: 4px; }}
    .subtitle {{ color: #64748b; margin-bottom: 24px; }}
    .card-grid {{ display: flex; gap: 16px; margin-bottom: 32px; }}
    .card {{ background: white; padding: 20px; border-radius: 8px; border: 1px solid #e5e7eb; flex: 1; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }}
    .card-num {{ font-size: 28px; font-weight: bold; margin-top: 8px; color: #0f172a; }}
    table {{ border-collapse: collapse; width: 100%; margin-bottom: 32px; background: white; border-radius: 8px; overflow: hidden; border: 1px solid #e5e7eb; }}
    th, td {{ padding: 12px 16px; text-align: left; border-bottom: 1px solid #e5e7eb; }}
    th {{ background: #f1f5f9; font-weight: 600; color: #334155; }}
  </style>
</head>
<body>
  <h1>🔍 CompliNet Daily Compliance Summary Report</h1>
  <div class="subtitle">Automated Network Configuration Drift & Compliance Audit Results</div>

  <div class="card-grid">
    <div class="card"><div>Total Devices</div><div class="card-num">{total_devices}</div></div>
    <div class="card"><div>Compliant Devices</div><div class="card-num" style="color:green">{compliant_devices}</div></div>
    <div class="card"><div>Non-Compliant Devices</div><div class="card-num" style="color:red">{non_compliant_devices}</div></div>
    <div class="card"><div>Average Health Score</div><div class="card-num">{avg_score} / 100</div></div>
  </div>

  <h2>Device Summary</h2>
  <table>
    <thead>
      <tr><th>Device Name</th><th>Compliance Status</th><th>Score</th><th>Failed Rules</th></tr>
    </thead>
    <tbody>
      {device_table}
    </tbody>
  </table>

  <h2>Action Required: Rule Violations & Remediations</h2>
  <table>
    <thead>
      <tr><th>Device</th><th>Rule ID</th><th>Rule Name</th><th>Status</th><th>Severity</th><th>Suggested Remediation</th></tr>
    </thead>
    <tbody>
      {failed_table}
    </tbody>
  </table>
</body>
</html>
"""


def save_daily_summary_report(all_reports: List[Dict[str, Any]], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(build_daily_summary_html(all_reports), encoding="utf-8")
    return output_path

