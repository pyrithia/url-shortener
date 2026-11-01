from fastapi import status
from fastapi.testclient import TestClient

from tests.helpers import create_test_url


def test_create_url(client: TestClient):
    response = client.post(
        "/urls",
        json={
            "real_url": "https://example.com/test-page",
            "expires_at": "2099-12-31T23:59:59",
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["real_url"] == "https://example.com/test-page"
    assert data["code"]


def test_read_urls(client: TestClient):
    create_test_url(client)
    response = client.get("/urls")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data[0]["real_url"] == "https://example.com/test-page"


def test_read_url(client: TestClient):
    test_url = create_test_url(client)
    url_id = test_url["id"]
    response = client.get(f"/urls/{url_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == url_id


def test_delete_url(client: TestClient):
    test_url = create_test_url(client)
    url_id = test_url["id"]
    response = client.delete(f"/urls/{url_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    response = client.get(f"/urls/{url_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_url_collison(client: TestClient, monkeypatch):
    existing_url = create_test_url(client)
    codes = iter([existing_url["code"], "x7k9p"])
    monkeypatch.setattr("routes.code_generator", lambda: next(codes))
    response = client.post(
        "/urls",
        json={
            "real_url": "https://example.com/test-page",
            "expires_at": "2099-12-31T23:59:59",
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["code"] == "x7k9p"


def test_create_url_max_collisions(client: TestClient, monkeypatch):
    existing_url = create_test_url(client)
    monkeypatch.setattr("routes.code_generator", lambda: existing_url["code"])
    response = client.post(
        "/urls",
        json={
            "real_url": "https://example.com/test-page",
            "expires_at": "2099-12-31T23:59:59",
        },
    )
    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
