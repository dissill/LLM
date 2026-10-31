你是资深 FastAPI 工程师。请先在心里列出这个需求的边界条件，再实现；**只修改** `app/main.py`。

## 用户需求

在已有 FastAPI 待办服务（已支持 tag 筛选 + limit/offset 分页）上，增加标题搜索 `q` 与排序 `sort/order`，并保持与 tag、分页组合时正确。

## 当前 baseline `app/main.py`

```python
from __future__ import annotations

from typing import List, Optional

from fastapi import FastAPI, Query
from pydantic import BaseModel

app = FastAPI(title="Todo API", version="0.1.1")

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
def list_todos(
    tag: Optional[str] = Query(default=None, description="按标签精确过滤"),
    limit: int = Query(default=20, ge=1, le=100, description="每页数量"),
    offset: int = Query(default=0, ge=0, description="偏移量"),
) -> dict:
    items = _TODOS
    if tag is not None:
        items = [item for item in items if tag in item["tags"]]
    total = len(items)
    page = items[offset: offset + limit]
    return {"items": page, "total": total, "limit": limit, "offset": offset}

```

## 验收测试 `tests/test_search_sort.py`（不得修改）

```python
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

```

## 实现前必须逐条检查的边界

- [ ] 默认行为不变：响应 `{items,total,limit,offset}`；`limit=20`、`offset=0`；默认按 id 升序；
- [ ] `q`：标题包含匹配，**大小写不敏感**；`q` 为空字符串时返回 422（`min_length=1`）；
- [ ] `sort` 只接受 `id` / `title`；`order` 只接受 `asc` / `desc`；非法值由 FastAPI 返回 422；
- [ ] `sort=title` 用大小写不敏感的标题排序；`sort=id` 用 id 排序；
- [ ] 过滤顺序：tag → q → sort → pagination；`total` 是过滤后的总数，不是当前页长度；
- [ ] 组合查询：tag + q + sort + order + limit + offset 同时生效；
- [ ] 空结果：返回 200 + `items=[]、total=0`，不要 404；
- [ ] 保持 `POST /todos` 创建行为与 201 状态码。

## 硬性约束

1. 只能修改 `app/main.py`；不得修改测试文件；
2. 只使用标准库 + FastAPI/Pydantic，不引入数据库；
3. 保持响应字段名严格为 `items/total/limit/offset`。

## 输出格式

只输出一个完整的 `app/main.py`，放在一个 ```python 代码块中；不要输出解释或其他文件。
