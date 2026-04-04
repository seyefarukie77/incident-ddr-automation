import pytest
from datetime import datetime
from app.models import ChatPullRequest

def test_invalid_time_window():
    with pytest.raises(ValueError):
        ChatPullRequest(
            start_time=datetime(2026, 2, 5, 10, 0),
            end_time=datetime(2026, 2, 5, 9, 0)
        )
