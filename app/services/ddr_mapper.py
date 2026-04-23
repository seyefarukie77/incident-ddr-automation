# Detect / Diagnose / Recover classification


def map_ddr_phase(text: str) -> str:
    """
    Map message text to Detect / Diagnose / Recover.
    Rule‑based for clarity and testability.
    """
    lower = text.lower()

    if any(word in lower for word in ["alert", "detected", "spike", "error"]):
        return "Detect"

    if any(word in lower for word in ["investigating", "suspect", "analysis", "logs"]):
        return "Diagnose"

    if any(word in lower for word in ["rollback", "restored", "fixed", "resolved"]):
        return "Recover"

    return "Diagnose"
