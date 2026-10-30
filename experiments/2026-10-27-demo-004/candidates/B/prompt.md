你是资深 FastAPI 工程师。请先在心里列出这个需求的边界条件，再实现；**只修改** `app/main.py`。

## 用户需求

给待办列表接口加标签筛选和分页，支持 limit/offset，返回 total。

## 当前 baseline `app/main.py`

```python
from __future__ import annotations

from typing import List

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Todo API", version="0.1.0")

# In-memory store for the demo (reset by process restart)
_TODOS: List[dict] = []


class TodoCreate(BaseModel):
    title: str
    tags: List[str] = []


class Todo(TodoCreate):
    id: int


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/todos", response_model=Todo, status_code=201)
def create_todo(payload: TodoCreate) -> dict:
    item = {"id": len(_TODOS) + 1, "title": payload.title, "tags": list(payload.tags)}
    _TODOS.append(item)
    return item


@app.get("/todos")
def list_todos() -> list:
    # Baseline: returns the full list, no tag filter / pagination.
    return _TODOS

```

## 验收测试 `tests/test_tags_pagination.py`（不得修改）

```python
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

```

## 实现前必须逐条检查的边界

- [ ] 无参数时：`limit=20`、`offset=0`，响应仍是 `{items,total,limit,offset}`；
- [ ] `tag` 过滤：精确匹配 tags 数组中的元素；不传 tag 时不过滤；
- [ ] 分页顺序：**先过滤，再分页**；`total` 是过滤后的总数，不是当前页长度；
- [ ] 组合查询：`tag` + `limit` + `offset` 同时生效；
- [ ] 空结果：返回 200 + `items=[]、total=0`，不要 404；
- [ ] 非法参数：`limit=0`、`limit=101`、`offset=-1` 由 FastAPI 返回 422；
- [ ] 不修改 `POST /todos` 的创建行为与 201 状态码。

## 硬性约束

1. 只能修改 `app/main.py`；不得修改测试文件；
2. 只使用标准库 + FastAPI/Pydantic，不引入数据库；
3. 保持响应字段名严格为 `items/total/limit/offset`。

## 输出格式

只输出一个完整的 `app/main.py`，放在一个 ```python 代码块中；不要输出解释或其他文件。
