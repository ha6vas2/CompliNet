from pathlib import Path
from typing import Dict, List


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
