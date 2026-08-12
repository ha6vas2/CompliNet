from pathlib import Path

from scripts.analyze import analyze_config, calculate_score, generate_diff


def write_temp_config(tmp_path: Path, filename: str, contents: str) -> Path:
    path = tmp_path / filename
    path.write_text(contents, encoding="utf-8")
    return path


def test_fully_compliant_configuration(tmp_path: Path):
    config = "service password-encryption\nno ip http server\naaa new-model\nntp server 10.10.10.10\nline vty 0 4\n transport input ssh\n"
    config_path = write_temp_config(tmp_path, "current.cfg", config)
    rules_path = Path(__file__).resolve().parents[1] / "compliance" / "rules.yaml"

    analysis = analyze_config(config_path, rules_path)
    assert analysis["compliant"]
    assert analysis["score"] == 100
    assert all(result["status"] == "PASS" for result in analysis["results"])


def test_missing_required_configuration(tmp_path: Path):
    config = "service password-encryption\nno ip http server\nntp server 10.10.10.10\nline vty 0 4\n transport input ssh\n"
    config_path = write_temp_config(tmp_path, "current.cfg", config)
    rules_path = Path(__file__).resolve().parents[1] / "compliance" / "rules.yaml"

    analysis = analyze_config(config_path, rules_path)
    assert not analysis["compliant"]
    assert any(result["rule_id"] == "AAA-001" and result["status"] == "FAIL" for result in analysis["results"])


def test_forbidden_telnet_configuration(tmp_path: Path):
    config = "service password-encryption\nno ip http server\naaa new-model\nntp server 10.10.10.10\nline vty 0 4\n transport input telnet\n"
    config_path = write_temp_config(tmp_path, "current.cfg", config)
    rules_path = Path(__file__).resolve().parents[1] / "compliance" / "rules.yaml"

    analysis = analyze_config(config_path, rules_path)
    assert not analysis["compliant"]
    assert any(result["rule_id"] == "SEC-002" and result["status"] == "FAIL" for result in analysis["results"])


def test_incorrect_ntp_configuration(tmp_path: Path):
    config = "service password-encryption\nno ip http server\naaa new-model\nntp server 10.10.10.11\nline vty 0 4\n transport input ssh\n"
    config_path = write_temp_config(tmp_path, "current.cfg", config)
    rules_path = Path(__file__).resolve().parents[1] / "compliance" / "rules.yaml"

    analysis = analyze_config(config_path, rules_path)
    assert not analysis["compliant"]
    assert any(result["rule_id"] == "NTP-001" and result["status"] == "FAIL" for result in analysis["results"])


def test_compliance_score_calculation(tmp_path: Path):
    results = [
        {"status": "FAIL", "severity": "critical"},
        {"status": "FAIL", "severity": "high"},
        {"status": "PASS", "severity": "medium"},
    ]
    assert calculate_score(results) == 50


def test_diff_generation(tmp_path: Path):
    baseline = write_temp_config(tmp_path, "baseline.cfg", "line one\nline two\nline three\n")
    current = write_temp_config(tmp_path, "current.cfg", "line one\nline two changed\nline three\n")

    diff_text = generate_diff(baseline, current)
    assert "-line two" in diff_text
    assert "+line two changed" in diff_text
