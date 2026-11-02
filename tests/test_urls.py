import time
from datetime import UTC, datetime, timedelta

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from models import Url
from tests.helpers import create_test_url


def test_create_url(client: TestClient):
    response = client.post(
        "/urls",
        json={
            "real_url": "https://example.com/test-page",
            "expires_at": (datetime.now(UTC) + timedelta(days=1)).isoformat(),
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["real_url"] == "https://example.com/test-page"
    assert data["code"]


def test_create_url_default_expiry(client: TestClient):
    response = client.post(
        "/urls",
        json={
            "real_url": "https://example.com/test-page",
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["real_url"] == "https://example.com/test-page"
    assert data["expires_at"]
    assert data["code"]


def test_create_url_past_expiry(client: TestClient):
    response = client.post(
        "/urls",
        json={
            "real_url": "https://example.com/test-page",
            "expires_at": (datetime.now(UTC) - timedelta(minutes=1)).isoformat(),
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_create_url_naive_expiry(client: TestClient):
    response = client.post(
        "/urls",
        json={
            "real_url": "https://example.com/test-page",
            "expires_at": (datetime.now() + timedelta(days=1)).isoformat(),
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


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
    test_url = create_test_url(client)
    codes = iter([test_url["code"], "x7k9p"])
    monkeypatch.setattr("routes.code_generator", lambda: next(codes))
    response = client.post(
        "/urls",
        json={
            "real_url": "https://example.com/test-page",
            "expires_at": (datetime.now(UTC) + timedelta(days=1)).isoformat(),
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["code"] == "x7k9p"


def test_create_url_max_collisions(client: TestClient, monkeypatch):
    test_url = create_test_url(client)
    monkeypatch.setattr("routes.code_generator", lambda: test_url["code"])
    response = client.post(
        "/urls",
        json={
            "real_url": "https://example.com/test-page",
            "expires_at": (datetime.now(UTC) + timedelta(days=1)).isoformat(),
        },
    )
    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE


def test_redirect_url(client: TestClient):
    test_url = create_test_url(client, real_url="https://example.com/test-page")
    code = test_url["code"]
    response = client.get(f"/{code}", follow_redirects=False)
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert response.headers["location"] == test_url["real_url"]


def test_redirect_url_invalid(client: TestClient):
    response = client.get("/invalid", follow_redirects=False)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_redirect_url_expired(client: TestClient, session: Session):
    session.add(
        Url(
            real_url="https://example.com",
            expires_at=int(time.time()) - 1,
            code="abcde",
        )
    )
    session.commit()
    response = client.get("/abcde", follow_redirects=False)
    assert response.status_code == status.HTTP_410_GONE
