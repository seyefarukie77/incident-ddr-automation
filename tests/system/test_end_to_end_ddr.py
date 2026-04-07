from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_end_to_end_ddr_workflow():
    chats = client.post(
        "/chats/pull",
        json={
            "start_time": "2026-02-05T09:00:00",
            "end_time": "2026-02-05T09:30:00"
        }
    ).json()

    timeline = client.post(
        "/timeline/extract",
        json={"messages": chats}
    ).json()

    prompts = client.post(
        "/prompts",
        json={"timeline": timeline}
    ).json()

    assert "DETECT" in prompts["detect"]
    assert "DIAGNOSE" in prompts["diagnose"]
    assert "RECOVER" in prompts["recover"]
