import pytest
from datetime import datetime

# IMPORTANT: import from the actual module
# If your file is app/main.py, this is correct
from app.main import (
    parse_iso_datetime,
    is_non_trivial_text,
    run_ddr_assessment,
    evaluate_detect,
    evaluate_pir_readiness,
    MOCK_INCIDENTS,
    CheckStatus,
    Severity,
)


def test_parse_iso_datetime_valid():
    result = parse_iso_datetime("2026-04-08T01:16:00")
    assert isinstance(result, datetime)


def test_parse_iso_datetime_with_z_suffix():
    result = parse_iso_datetime("2026-04-08T01:16:00Z")
    assert isinstance(result, datetime)


def test_parse_iso_datetime_invalid_returns_none():
    assert parse_iso_datetime("not-a-date") is None


def test_non_trivial_text_passes():
    assert is_non_trivial_text("Customers could not log in to the service")


def test_non_trivial_text_fails_for_empty():
    assert not is_non_trivial_text("")


def test_good_incident_passes_overall_ddr():
    incident = MOCK_INCIDENTS["INC13089493"]
    result = run_ddr_assessment(incident)
    assert result.overallStatus == CheckStatus.PASS


def test_bad_incident_fails_overall_ddr():
    incident = MOCK_INCIDENTS["INC13092020"]
    result = run_ddr_assessment(incident)
    assert result.overallStatus == CheckStatus.FAIL