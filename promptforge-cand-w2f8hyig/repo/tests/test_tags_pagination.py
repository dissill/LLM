"""Acceptance tests for the FastAPI todo tag-filter + pagination task (v0.1).

Each test isolates its data with a unique tag so tests can share the in-memory app.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


def create(client: TestClient, title: str, tags: list[str]) -> dict:
    resp = client.post("/todos", json={"title": title, "tags": tags})
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_a1_default_response_shape(client: TestClient) -> None:
    for i in range(3):
        create(client, f"a1-{i}", ["a1"])

    resp = client.get("/todos", params={"tag": "a1"})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    for key in ("items", "total", "limit", "offset"):
        assert key in data, f"missing key: {key}"
    assert data["total"] == 3
    assert data["limit"] == 20
    assert data["offset"] == 0
    assert len(data["items"]) == 3


def test_a2_tag_filter(client: TestClient) -> None:
    create(client, "a2-1", ["a2x"])
    create(client, "a2-2", ["a2x", "shared"])
    create(client, "a2-3", ["a2y"])

    resp = client.get("/todos", params={"tag": "a2x"})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2
    for item in data["items"]:
        assert "a2x" in item["tags"]


def test_a3_limit_offset(client: TestClient) -> None:
    ids = [create(client, f"a3-{i}", ["a3"])["id"] for i in range(5)]

    resp = client.get("/todos", params={"tag": "a3", "limit": 2, "offset": 2})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["total"] == 5
    assert data["limit"] == 2
    assert data["offset"] == 2
    assert [item["id"] for item in data["items"]] == ids[2:4]


def test_a4_combined_filter_and_pagination(client: TestClient) -> None:
    ids = [create(client, f"a4-{i}", ["a4"])["id"] for i in range(4)]
    for i in range(2):
        create(client, f"a4-other-{i}", ["a4-other"])

    resp = client.get("/todos", params={"tag": "a4", "limit": 2, "offset": 1})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["total"] == 4
    assert data["limit"] == 2
    assert data["offset"] == 1
    assert [item["id"] for item in data["items"]] == ids[1:3]


def test_a5_empty_result(client: TestClient) -> None:
    resp = client.get("/todos", params={"tag": "a5-none"})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["items"] == []
    assert data["total"] == 0


def test_a6_invalid_pagination(client: TestClient) -> None:
    for params in ({"limit": 0}, {"limit": 101}, {"offset": -1}):
        resp = client.get("/todos", params=params)
        assert resp.status_code == 422, f"params={params} -> {resp.status_code}: {resp.text}"
