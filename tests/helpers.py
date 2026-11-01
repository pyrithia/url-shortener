from fastapi import status
from fastapi.testclient import TestClient


def create_test_url(
    client: TestClient,
    real_url: str = "https://example.com/test-page",
    expires_at: str = "2099-12-31T23:59:59",
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
