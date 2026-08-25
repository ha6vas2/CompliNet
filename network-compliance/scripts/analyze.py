import difflib
from pathlib import Path
from typing import Any, Dict, List

import yaml


SEVERITY_SCORE_PENALTIES = {
    "critical": 30,
    "high": 20,
    "medium": 10,
    "low": 5,
    "warning": 5,
}


def load_rules(rules_path: Path) -> List[Dict[str, Any]]:
    with rules_path.open("r", encoding="utf-8") as rules_file:
        rules_document = yaml.safe_load(rules_file)
    return rules_document.get("rules", [])


def read_config(config_path: Path) -> List[str]:
    text = config_path.read_text(encoding="utf-8")
    return [line.strip() for line in text.splitlines() if line.strip()]


def evaluate_rule(rule: Dict[str, Any], config_lines: List[str]) -> Dict[str, Any]:
    rule_id = rule.get("id")
    name = rule.get("name")
    config_match = rule.get("config", "")
    rule_type = rule.get("type", "required")
    severity = rule.get("severity", "medium")
    remediation = rule.get("remediation", "")

    pattern = config_match.strip()

    if rule_type == "required":
        status = "PASS" if pattern in config_lines else "FAIL"
    elif rule_type == "forbidden":
        status = "PASS" if pattern not in config_lines else "FAIL"
    elif rule_type == "exact-match":
        status = "PASS" if pattern in config_lines else "FAIL"
    elif rule_type == "warning":
        status = "PASS" if pattern in config_lines else "WARN"
    else:
        status = "PASS" if pattern in config_lines else "FAIL"

    return {
        "rule_id": rule_id,
        "name": name,
        "status": status,
        "severity": severity,
        "remediation": remediation,
        "type": rule_type,
        "config": config_match,
    }



def calculate_score(rule_results: List[Dict[str, Any]]) -> int:
    score = 100
    for result in rule_results:
        if result["status"] == "FAIL":
            penalty = SEVERITY_SCORE_PENALTIES.get(result["severity"], 10)
            score -= penalty
        elif result["status"] == "WARN":
            penalty = SEVERITY_SCORE_PENALTIES.get(result["severity"], 5)
            score -= penalty
    return max(score, 0)



def analyze_config(config_path: Path, rules_path: Path) -> Dict[str, Any]:
    config_lines = read_config(config_path)
    rules = load_rules(rules_path)
    results = [evaluate_rule(rule, config_lines) for rule in rules]
    total_score = calculate_score(results)
    compliant = all(result["status"] == "PASS" for result in results)

    return {
        "device_name": config_path.parent.name,
        "config_path": str(config_path),
        "score": total_score,
        "compliant": compliant,
        "results": results,
    }


def generate_diff(baseline_path: Path, current_path: Path) -> str:
    baseline_lines = baseline_path.read_text(encoding="utf-8").splitlines(keepends=True)
    current_lines = current_path.read_text(encoding="utf-8").splitlines(keepends=True)
    diff = difflib.unified_diff(
        baseline_lines,
        current_lines,
        fromfile=str(baseline_path.name),
        tofile=str(current_path.name),
        lineterm="",
    )
    return "\n".join(diff)
