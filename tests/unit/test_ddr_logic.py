from app.main import run_ddr_assessment, MOCK_INCIDENTS, CheckStatus

def test_ddr_pass_scenario():
    result = run_ddr_assessment(MOCK_INCIDENTS["INC13089493"])
    assert result.overallStatus == CheckStatus.PASS

def test_ddr_fail_scenario():
    result = run_ddr_assessment(MOCK_INCIDENTS["INC13092020"])
    assert result.overallStatus == CheckStatus.FAIL