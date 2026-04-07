from fastapi.testclient import TestClient
from app.main import app
from datetime import datetime

client = TestClient(app)

def test_chat_pull_endpoint():
    response = client.post(
        "/chats/pull",
        json={
            "start_time": "2026-02-05T09:00:00",
            "end_time": "2026-02-05T09:30:00"
        }
    )
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_timeline_extract_endpoint():
    response = client.post(
        "/timeline/extract",
        json={
            "messages": [
                {
                    "id": "1",
                    "timestamp": "2026-02-05T09:01:00",
                    "author": "SRE",
                    "text": "Alert detected"
                }
            ]
        }
    )
    assert response.status_code == 200
    assert response.json()[0]["ddr_phase"] == "Detect"
