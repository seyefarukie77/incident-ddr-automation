# Pydantic models
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

class ChatMessage(BaseModel):
    id: str
    timestamp: datetime
    author: Optional[str]
    text: str


class ChatPullRequest(BaseModel):
    start_time: datetime
    end_time: datetime


class TimelineEvent(BaseModel):
    timestamp: datetime
    summary: str
    ddr_phase: Optional[str] = None


class TimelineExtractRequest(BaseModel):
    messages: List[ChatMessage]


class PromptRequest(BaseModel):
    timeline: List[TimelineEvent]


class DDRPromptResponse(BaseModel):
    detect: str
    diagnose: str
    recover: str
