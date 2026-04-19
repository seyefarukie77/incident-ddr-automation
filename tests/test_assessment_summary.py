# tests/test_assessment_summary.py
from app import run_ddr_assessment, MOCK_INCIDENTS, CheckStatus

def test_good_sev1_overall_pass():
    result = run_ddr_assessment(MOCK_INCIDENTS["INC13089493"])
    assert result.overallStatus == CheckStatus.PASS

def test_bad_sev2_overall_fail():
    result = run_ddr_assessment(MOCK_INCIDENTS["INC13092020"])
    assert result.overallStatus == CheckStatus.FAIL

# tests/test_assessment_summary.py
from app import run_ddr_assessment, MOCK_INCIDENTS, CheckStatus

def test_good_sev1_overall_pass():
    result = run_ddr_assessment(MOCK_INCIDENTS["INC13089493"])
    assert result.overallStatus == CheckStatus.PASS

def test_bad_sev2_overall_fail():
    result = run_ddr_assessment(MOCK_INCIDENTS["INC13092020"])
    assert result.overallStatus == CheckStatus.FAIL

from app import generate_executive_summary, run_ddr_assessment, MOCK_INCIDENTS

def test_executive_summary_contains_severity_and_readiness():
    incident = MOCK_INCIDENTS["INC13089493"]
    assessment = run_ddr_assessment(incident)

    summary = generate_executive_summary(incident, assessment)

    assert incident.severity.value in summary
    assert "PIR readiness:" in summary