from pathlib import Path

from scripts.analyze import analyze_config, calculate_score, generate_diff


def write_temp_config(tmp_path: Path, filename: str, contents: str) -> Path:
    path = tmp_path / filename
    path.write_text(contents, encoding="utf-8")
    return path


def make_r1_config(*, hostname: bool = True, syslog: bool = True, ipv6_forwarding: bool = True, ospf: bool = True, area0: bool = True, router_id: str | None = "1.1.1.1") -> str:
    lines = [
        "hostname r1" if hostname else "",
        "log syslog informational" if syslog else "",
        "no ipv6 forwarding" if ipv6_forwarding else "ipv6 forwarding",
        "router ospf" if ospf else "",
        f" ospf router-id {router_id}" if ospf and router_id else "",
        " network 10.0.12.0/30 area 0" if ospf and area0 else "",
    ]
    return "\n".join(line for line in lines if line) + "\n"


def make_r2_config(*, hostname: bool = True, syslog: bool = True, ipv6_forwarding: bool = True, ospf: bool = True, area0: bool = True, router_id: str | None = "2.2.2.2") -> str:
    lines = [
        "hostname r2" if hostname else "",
        "log syslog informational" if syslog else "",
        "no ipv6 forwarding" if ipv6_forwarding else "ipv6 forwarding",
        "router ospf" if ospf else "",
        f" ospf router-id {router_id}" if ospf and router_id else "",
        " network 10.0.12.0/30 area 0" if ospf and area0 else "",
    ]
    return "\n".join(line for line in lines if line) + "\n"


def test_fully_compliant_r1(tmp_path: Path):
    device_dir = tmp_path / "R1"
    device_dir.mkdir()
    config_path = write_temp_config(device_dir, "current.cfg", make_r1_config())
    rules_path = Path(__file__).resolve().parents[1] / "compliance" / "rules.yaml"

    analysis = analyze_config(config_path, rules_path)
    assert analysis["compliant"]
    assert analysis["score"] == 100
    assert all(result["status"] == "PASS" for result in analysis["results"])


def test_fully_compliant_r2(tmp_path: Path):
    device_dir = tmp_path / "R2"
    device_dir.mkdir()
    config_path = write_temp_config(device_dir, "current.cfg", make_r2_config())
    rules_path = Path(__file__).resolve().parents[1] / "compliance" / "rules.yaml"

    analysis = analyze_config(config_path, rules_path)
    assert analysis["compliant"]
    assert analysis["score"] == 100
    assert all(result["status"] == "PASS" for result in analysis["results"])


def test_missing_hostname_fails(tmp_path: Path):
    device_dir = tmp_path / "R1"
    device_dir.mkdir()
    config_path = write_temp_config(device_dir, "current.cfg", make_r1_config(hostname=False))
    rules_path = Path(__file__).resolve().parents[1] / "compliance" / "rules.yaml"

    analysis = analyze_config(config_path, rules_path)
    assert not analysis["compliant"]
    assert any(result["rule_id"] == "SYS-001" and result["status"] == "FAIL" for result in analysis["results"])


def test_missing_syslog_fails(tmp_path: Path):
    device_dir = tmp_path / "R1"
    device_dir.mkdir()
    config_path = write_temp_config(device_dir, "current.cfg", make_r1_config(syslog=False))
    rules_path = Path(__file__).resolve().parents[1] / "compliance" / "rules.yaml"

    analysis = analyze_config(config_path, rules_path)
    assert not analysis["compliant"]
    assert any(result["rule_id"] == "SYS-002" and result["status"] == "FAIL" for result in analysis["results"])


def test_ipv6_forwarding_enabled_fails(tmp_path: Path):
    device_dir = tmp_path / "R1"
    device_dir.mkdir()
    config_path = write_temp_config(device_dir, "current.cfg", make_r1_config(ipv6_forwarding=False))
    rules_path = Path(__file__).resolve().parents[1] / "compliance" / "rules.yaml"

    analysis = analyze_config(config_path, rules_path)
    assert not analysis["compliant"]
    assert any(result["rule_id"] == "SYS-003" and result["status"] == "FAIL" for result in analysis["results"])


def test_ospf_removed_fails(tmp_path: Path):
    device_dir = tmp_path / "R1"
    device_dir.mkdir()
    config_path = write_temp_config(device_dir, "current.cfg", make_r1_config(ospf=False))
    rules_path = Path(__file__).resolve().parents[1] / "compliance" / "rules.yaml"

    analysis = analyze_config(config_path, rules_path)
    assert not analysis["compliant"]
    assert any(result["rule_id"] == "OSPF-001" and result["status"] == "FAIL" for result in analysis["results"])


def test_area_zero_network_removed_fails(tmp_path: Path):
    device_dir = tmp_path / "R1"
    device_dir.mkdir()
    config_path = write_temp_config(device_dir, "current.cfg", make_r1_config(area0=False))
    rules_path = Path(__file__).resolve().parents[1] / "compliance" / "rules.yaml"

    analysis = analyze_config(config_path, rules_path)
    assert not analysis["compliant"]
    assert any(result["rule_id"] == "OSPF-002" and result["status"] == "FAIL" for result in analysis["results"])


def test_r1_router_id_wrong_fails(tmp_path: Path):
    device_dir = tmp_path / "R1"
    device_dir.mkdir()
    config_path = write_temp_config(device_dir, "current.cfg", make_r1_config(router_id="5.5.5.5"))
    rules_path = Path(__file__).resolve().parents[1] / "compliance" / "rules.yaml"

    analysis = analyze_config(config_path, rules_path)
    assert not analysis["compliant"]
    assert any(result["rule_id"] == "OSPF-003" and result["status"] == "FAIL" for result in analysis["results"])


def test_r2_router_id_wrong_fails(tmp_path: Path):
    device_dir = tmp_path / "R2"
    device_dir.mkdir()
    config_path = write_temp_config(device_dir, "current.cfg", make_r2_config(router_id="9.9.9.9"))
    rules_path = Path(__file__).resolve().parents[1] / "compliance" / "rules.yaml"

    analysis = analyze_config(config_path, rules_path)
    assert not analysis["compliant"]
    assert any(result["rule_id"] == "OSPF-004" and result["status"] == "FAIL" for result in analysis["results"])


def test_baseline_drift_without_policy_violation(tmp_path: Path):
    baseline_path = write_temp_config(tmp_path, "baseline.cfg", make_r1_config() + "! note\n")
    current_path = write_temp_config(tmp_path, "current.cfg", make_r1_config() + "! note\n! changed\n")
    rules_path = Path(__file__).resolve().parents[1] / "compliance" / "rules.yaml"

    analysis = analyze_config(current_path, rules_path)
    diff_text = generate_diff(baseline_path, current_path)

    assert analysis["compliant"]
    assert diff_text


def test_policy_violation_without_unrelated_drift(tmp_path: Path):
    device_dir = tmp_path / "R1"
    device_dir.mkdir()
    config_path = write_temp_config(device_dir, "current.cfg", make_r1_config(syslog=False))
    baseline_path = write_temp_config(device_dir, "baseline.cfg", make_r1_config(syslog=False))
    rules_path = Path(__file__).resolve().parents[1] / "compliance" / "rules.yaml"

    analysis = analyze_config(config_path, rules_path)
    diff_text = generate_diff(baseline_path, config_path)

    assert not analysis["compliant"]
    assert not diff_text


def test_compliance_score_calculation():
    results = [
        {"status": "FAIL", "severity": "critical"},
        {"status": "FAIL", "severity": "high"},
        {"status": "PASS", "severity": "medium"},
        {"status": "WARN", "severity": "low"},
    ]
    assert calculate_score(results) == 45


def test_diff_generation(tmp_path: Path):
    baseline = write_temp_config(tmp_path, "baseline.cfg", "line one\nline two\nline three\n")
    current = write_temp_config(tmp_path, "current.cfg", "line one\nline two changed\nline three\n")

    diff_text = generate_diff(baseline, current)
    assert "-line two" in diff_text
    assert "+line two changed" in diff_text


def test_rule_result_includes_expected_actual_and_reason(tmp_path: Path):
    device_dir = tmp_path / "R1"
    device_dir.mkdir()
    config_path = write_temp_config(device_dir, "current.cfg", make_r1_config(router_id="5.5.5.5"))
    rules_path = Path(__file__).resolve().parents[1] / "compliance" / "rules.yaml"

    analysis = analyze_config(config_path, rules_path)
    ospf_result = next(r for r in analysis["results"] if r["rule_id"] == "OSPF-003")

    assert ospf_result["status"] == "FAIL"
    assert ospf_result["expected"] == "ospf router-id 1.1.1.1"
    assert ospf_result["actual"] == "ospf router-id 5.5.5.5"
    assert "does not match" in ospf_result["reason"].lower()
    assert ospf_result["remediation"]

