"""Acceptance tests for the FastAPI todo search + sort task (v0.2).

The baseline is the completed v0.1 app (tag filter + pagination).
Each test isolates data with a unique tag/query prefix, so tests can share the
in-memory app.
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


def test_a1_default_shape_and_id_order(client: TestClient) -> None:
    ids = [create(client, f"v02-a1-{i}", ["v02a1"])["id"] for i in range(3)]

    resp = client.get("/todos", params={"tag": "v02a1"})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    for key in ("items", "total", "limit", "offset"):
        assert key in data, f"missing key: {key}"
    assert data["total"] == 3
    assert data["limit"] == 20
    assert data["offset"] == 0
    assert [item["id"] for item in data["items"]] == ids


def test_a2_q_search_case_insensitive(client: TestClient) -> None:
    create(client, "Buy milk", ["v02a2"])
    create(client, "buy bread", ["v02a2"])
    create(client, "Call mom", ["v02a2"])

    resp = client.get("/todos", params={"tag": "v02a2", "q": "BUY"})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2
    for item in data["items"]:
        assert "buy" in item["title"].lower()


def test_a3_sort_title_asc(client: TestClient) -> None:
    for title in ("zeta", "Alpha", "beta"):
        create(client, title, ["v02a3"])

    resp = client.get("/todos", params={"tag": "v02a3", "sort": "title", "order": "asc"})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    titles = [item["title"] for item in data["items"]]
    assert titles == ["Alpha", "beta", "zeta"]
    assert data["total"] == 3


def test_a4_sort_id_desc(client: TestClient) -> None:
    ids = [create(client, f"v02-a4-{i}", ["v02a4"])["id"] for i in range(4)]

    resp = client.get("/todos", params={"tag": "v02a4", "sort": "id", "order": "desc"})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["total"] == 4
    assert [item["id"] for item in data["items"]] == list(reversed(ids))


def test_a5_combined_search_filter_sort_pagination(client: TestClient) -> None:
    for title in ("Alpha task", "beta task", "Gamma task", "delta task"):
        create(client, title, ["v02a5"])
    create(client, "other task", ["v02a5-other"])

    resp = client.get(
        "/todos",
        params={
            "tag": "v02a5",
            "q": "task",
            "sort": "title",
            "order": "desc",
            "limit": 2,
            "offset": 1,
        },
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["total"] == 4
    assert data["limit"] == 2
    assert data["offset"] == 1
    assert [item["title"] for item in data["items"]] == ["delta task", "beta task"]


def test_a6_invalid_params(client: TestClient) -> None:
    create(client, "v02-a6", ["v02a6"])
    for params in (
        {"tag": "v02a6", "sort": "created_at"},
        {"tag": "v02a6", "order": "sideways"},
        {"tag": "v02a6", "q": ""},
    ):
        resp = client.get("/todos", params=params)
        assert resp.status_code == 422, f"params={params} -> {resp.status_code}: {resp.text}"
