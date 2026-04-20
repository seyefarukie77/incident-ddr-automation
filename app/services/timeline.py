# Timeline extraction logic
from typing import List
from app.models import ChatMessage, TimelineEvent


def extract_timeline(messages: List[ChatMessage]) -> List[TimelineEvent]:
    """
    Convert raw chat messages into a chronological timeline.
    """
    events = []

    for msg in sorted(messages, key=lambda m: m.timestamp):
        events.append(
            TimelineEvent(
                timestamp=msg.timestamp,
                summary=msg.text,
            )
        )

    return events
