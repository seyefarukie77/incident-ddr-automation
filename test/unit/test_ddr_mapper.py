from app.services.ddr_mapper import map_ddr_phase

def test_detect_phase():
    text = "Alert triggered due to error spike"
    assert map_ddr_phase(text) == "Detect"

def test_diagnose_phase():
    text = "Investigating logs to identify root cause"
    assert map_ddr_phase(text) == "Diagnose"

def test_recover_phase():
    text = "Rollback completed and service restored"
    assert map_ddr_phase(text) == "Recover"

def test_default_phase():
    text = "General discussion message"
    assert map_ddr_phase(text) == "Diagnose"
