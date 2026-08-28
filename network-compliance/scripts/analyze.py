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
    """Load compliance rules from YAML."""

    with rules_path.open("r", encoding="utf-8") as rules_file:
        rules_document = yaml.safe_load(rules_file) or {}

    return rules_document.get("rules", [])


def read_config(config_path: Path) -> List[str]:
    """Read configuration and normalize whitespace."""

    text = config_path.read_text(encoding="utf-8")

    return [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]


def rule_applies_to_device(
    rule: Dict[str, Any],
    device_name: str,
) -> bool:
    """Determine whether a rule applies to this device."""

    scope = rule.get("scope", "all")

    if scope == "all":
        return True

    if isinstance(scope, str):
        return scope.lower() == device_name.lower()

    if isinstance(scope, list):
        return any(
            str(item).lower() == device_name.lower()
            for item in scope
        )

    return False


def pattern_exists(
    pattern: str,
    config_lines: List[str],
    match_mode: str = "exact",
) -> bool:
    """Check whether a configuration pattern exists."""

    pattern = pattern.strip()

    if match_mode == "contains":
        return any(
            pattern in line
            for line in config_lines
        )

    return pattern in config_lines


def evaluate_rule(
    rule: Dict[str, Any],
    config_lines: List[str],
) -> Dict[str, Any]:

    rule_id = rule.get("id")
    name = rule.get("name")
    config_match = rule.get("config", "")
    rule_type = rule.get("type", "required")
    severity = rule.get("severity", "medium")
    remediation = rule.get("remediation", "")
    match_mode = rule.get("match", "exact")

    exists = pattern_exists(
        config_match,
        config_lines,
        match_mode,
    )

    if rule_type in ("required", "exact-match"):
        status = "PASS" if exists else "FAIL"

    elif rule_type == "forbidden":
        status = "PASS" if not exists else "FAIL"

    elif rule_type == "warning":
        status = "PASS" if exists else "WARN"

    else:
        status = "FAIL"

    return {
        "rule_id": rule_id,
        "name": name,
        "status": status,
        "severity": severity,
        "remediation": remediation,
        "type": rule_type,
        "config": config_match,
        "scope": rule.get("scope", "all"),
        "match": match_mode,
    }


def calculate_score(
    rule_results: List[Dict[str, Any]],
) -> int:

    score = 100

    for result in rule_results:

        if result["status"] == "FAIL":
            score -= SEVERITY_SCORE_PENALTIES.get(
                result["severity"],
                10,
            )

        elif result["status"] == "WARN":
            score -= SEVERITY_SCORE_PENALTIES.get(
                result["severity"],
                5,
            )

    return max(score, 0)


def analyze_config(
    config_path: Path,
    rules_path: Path,
) -> Dict[str, Any]:

    device_name = config_path.parent.name

    config_lines = read_config(config_path)
    rules = load_rules(rules_path)

    applicable_rules = [
        rule
        for rule in rules
        if rule_applies_to_device(
            rule,
            device_name,
        )
    ]

    results = [
        evaluate_rule(rule, config_lines)
        for rule in applicable_rules
    ]

    total_score = calculate_score(results)

    compliant = all(
        result["status"] == "PASS"
        for result in results
    )

    return {
        "device_name": device_name,
        "config_path": str(config_path),
        "score": total_score,
        "compliant": compliant,
        "rules_evaluated": len(results),
        "results": results,
    }


def generate_diff(
    baseline_path: Path,
    current_path: Path,
) -> str:

    baseline_lines = baseline_path.read_text(
        encoding="utf-8"
    ).splitlines(keepends=True)

    current_lines = current_path.read_text(
        encoding="utf-8"
    ).splitlines(keepends=True)

    diff = difflib.unified_diff(
        baseline_lines,
        current_lines,
        fromfile=str(baseline_path.name),
        tofile=str(current_path.name),
        lineterm="",
    )

    return "\n".join(diff)
