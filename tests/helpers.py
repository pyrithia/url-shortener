from datetime import UTC, datetime, timedelta

from fastapi import status
from fastapi.testclient import TestClient


def create_test_url(
    client: TestClient,
    real_url: str = "https://example.com/test-page",
    expires_at: str = (datetime.now(UTC) + timedelta(days=1)).isoformat(),
):
    response = client.post(
        "/urls",
        json={
            "real_url": real_url,
            "expires_at": expires_at,
        },
    )

    assert response.status_code == status.HTTP_201_CREATED
    return response.json()
