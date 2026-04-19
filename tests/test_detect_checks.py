# tests/test_detect_checks.py
from app import evaluate_detect, SEVERITY_RULES, Severity, MOCK_INCIDENTS, CheckStatus

def test_detect_checks_pass_for_good_sev1():
    incident = MOCK_INCIDENTS["INC13089493"]
    rules = SEVERITY_RULES[Severity.SEV1.value]

    checks = evaluate_detect(incident, rules)

    assert all(c.status == CheckStatus.PASS for c in checks)

def test_detect_signals_required_for_sev2():
    incident = MOCK_INCIDENTS["INC13092020"]
    rules = SEVERITY_RULES[Severity.SEV2.value]

    checks = evaluate_detect(incident, rules)

    failures = [c for c in checks if c.status == CheckStatus.FAIL]
    assert any(c.checkName == "Detection Signals Present" for c in failures)