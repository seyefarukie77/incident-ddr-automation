# tests/test_pir_readiness.py
from app import evaluate_pir_readiness, SEVERITY_RULES, Severity, MOCK_INCIDENTS, CheckStatus

def test_missing_end_time_fails_pir_readiness():
    incident = MOCK_INCIDENTS["INC13090001"]
    rules = SEVERITY_RULES[Severity.SEV2.value]

    checks = evaluate_pir_readiness(incident, rules)

    end_time_check = next(c for c in checks if c.checkName == "EndTime Present & Valid ISO")
    assert end_time_check.status == CheckStatus.FAIL

def test_out_of_order_timeline_fails_chronological_check():
    incident = MOCK_INCIDENTS["INC13091010"]
    rules = SEVERITY_RULES[Severity.SEV1.value]

    checks = evaluate_pir_readiness(incident, rules)

    chrono = next(c for c in checks if c.checkName == "Timeline Chronological Order")
    assert chrono.status == CheckStatus.FAIL