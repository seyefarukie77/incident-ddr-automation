from datetime import datetime
from app.models import ChatMessage
from app.services.timeline import extract_timeline

def test_timeline_extraction_order():
    messages = [
        ChatMessage(id="2", timestamp=datetime(2026, 2, 5, 9, 5), author="B", text="Second"),
        ChatMessage(id="1", timestamp=datetime(2026, 2, 5, 9, 1), author="A", text="First"),
    ]

    timeline = extract_timeline(messages)

    assert timeline[0].summary == "First"
    assert timeline[1].summary == "Second"
