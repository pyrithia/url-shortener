from fastapi import status
from fastapi.testclient import TestClient

from tests.helpers import create_test_url


def test_create_url(client: TestClient):
    response = client.post(
        "/urls",
        json={
            "real_url": "https://example.com/test-page",
            "expires_at": "2026-11-02T12:30:00",
        },
    )
    data = response.json()
    assert response.status_code == status.HTTP_201_CREATED
    assert data["real_url"] == "https://example.com/test-page"


def test_read_urls(client: TestClient):
    create_test_url(client)
    response = client.get("/urls")
    data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert data[0]["real_url"] == "https://example.com/test-page"


def test_read_url(client: TestClient):
    test_url = create_test_url(client)
    url_id = test_url["id"]
    response = client.get(f"/urls/{url_id}")
    data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert data["id"] == url_id


def test_delete_url(client: TestClient):
    test_url = create_test_url(client)
    url_id = test_url["id"]
    response = client.delete(f"/urls/{url_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    response = client.get(f"/urls/{url_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
