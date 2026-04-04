#DDR Prompt Generation
from typing import List
from app.models import TimelineEvent, DDRPromptResponse

def generate_ddr_prompts(timeline: List[TimelineEvent]) -> DDRPromptResponse:
    detect_events = [e.summary for e in timeline if e.ddr_phase == "Detect"]
    diagnose_events = [e.summary for e in timeline if e.ddr_phase == "Diagnose"]
    recover_events = [e.summary for e in timeline if e.ddr_phase == "Recover"]

    detect_prompt = (
        "DETECT:\n"
        "What alerts or signals identified the incident?\n"
        f"Evidence:\n- " + "\n- ".join(detect_events)
    )

    diagnose_prompt = (
        "DIAGNOSE:\n"
        "What analysis was performed to identify the cause?\n"
        f"Evidence:\n- " + "\n- ".join(diagnose_events)
    )

    recover_prompt = (
        "RECOVER:\n"
        "What actions restored service and prevented recurrence?\n"
        f"Evidence:\n- " + "\n- ".join(recover_events)
    )

    return DDRPromptResponse(
        detect=detect_prompt,
        diagnose=diagnose_prompt,
        recover=recover_prompt,
    )
