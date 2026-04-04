from fastapi import FastAPI, HTTPException
from app.models import (
    ChatMessage,
    ChatPullRequest,
    TimelineExtractRequest,
    PromptRequest,
    TimelineEvent,
    DDRPromptResponse,
)
from app.services.timeline import extract_timeline
from app.services.ddr_mapper import map_ddr_phase
from app.services.prompts import generate_ddr_prompts
from datetime import datetime
from typing import List

app = FastAPI(
    title="Incident DDR Automation API",
    description="Post‑Incident Review Automation Tool aligned to Detect → Diagnose → Recover (DDR)",
    version="1.0.0",
)

# --- Mock chat store (for assessment/testing purposes)
MOCK_CHAT_DATA = [
    ChatMessage(
        id="1",
        timestamp=datetime.fromisoformat("2026-02-05T09:01:00"),
        author="SRE",
        text="Alert triggered: API error rate spike detected",
    ),
    ChatMessage(
        id="2",
        timestamp=datetime.fromisoformat("2026-02-05T09:05:00"),
        author="Engineer",
        text="Investigating logs, suspect recent deployment",
    ),
    ChatMessage(
        id="3",
        timestamp=datetime.fromisoformat("2026-02-05T09:15:00"),
        author="Engineer",
        text="Rolling back deployment to previous version",
    ),
    ChatMessage(
        id="4",
        timestamp=datetime.fromisoformat("2026-02-05T09:25:00"),
        author="Incident Manager",
        text="Service restored, monitoring stable",
    ),
]


@app.post("/chats/pull", response_model=List[ChatMessage])
def pull_chats(request: ChatPullRequest):
    """
    Retrieve chat messages for a given incident time window.
    In production this would integrate with Microsoft Teams / Slack.
    """
    messages = [
        msg
        for msg in MOCK_CHAT_DATA
        if request.start_time <= msg.timestamp <= request.end_time
    ]

    if not messages:
        raise HTTPException(status_code=404, detail="No messages found")

    return messages


@app.post("/timeline/extract", response_model=List[TimelineEvent])
def extract_incident_timeline(request: TimelineExtractRequest):
    """
    Extract a normalized incident timeline and classify DDR phases.
    """
    events = extract_timeline(request.messages)

    for event in events:
        event.ddr_phase = map_ddr_phase(event.summary)

    return events


@app.post("/prompts", response_model=DDRPromptResponse)
def generate_prompts(request: PromptRequest):
    """
    Generate Detect / Diagnose / Recover prompts for PIR facilitation.
    """
    return generate_ddr_prompts(request.timeline)
