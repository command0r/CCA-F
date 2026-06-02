"""Tests for the users-api endpoints."""

import pytest

from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config.update(TESTING=True)
    with app.test_client() as c:
        yield c


def test_healthz(client):
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}


def test_list_users(client):
    resp = client.get("/users")
    assert resp.status_code == 200
    users = resp.get_json()
    assert len(users) >= 2
    assert {"id", "email", "name", "roles"} <= set(users[0].keys())


def test_get_user_found(client):
    resp = client.get("/users/1")
    assert resp.status_code == 200
    assert resp.get_json()["email"] == "ada@example.com"


def test_get_user_missing(client):
    resp = client.get("/users/9999")
    assert resp.status_code == 404


def test_create_user_requires_fields(client):
    resp = client.post("/users", json={"email": "only@example.com"})
    assert resp.status_code == 400


def test_create_user_success(client):
    resp = client.post(
        "/users",
        json={"email": "grace@example.com", "name": "Grace Hopper", "roles": ["admin"]},
    )
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["email"] == "grace@example.com"
    assert body["roles"] == ["admin"]
