# tests/test_utils.py
from datetime import datetime
from app import parse_iso_datetime

def test_parse_valid_iso():
    dt = parse_iso_datetime("2026-04-08T01:16:00")
    assert isinstance(dt, datetime)

def test_parse_iso_with_z_suffix():
    dt = parse_iso_datetime("2026-04-08T01:16:00Z")
    assert dt is not None

def test_parse_invalid_iso_returns_none():
    assert parse_iso_datetime("not-a-date") is None

def test_parse_none_returns_none():
    assert parse_iso_datetime(None) is None

from app import is_non_trivial_text

def test_non_trivial_text_passes():
    assert is_non_trivial_text("Customers could not log in")

def test_trivial_text_fails():
    assert not is_non_trivial_text("")

def test_whitespace_only_fails():
    assert not is_non_trivial_text("     ")