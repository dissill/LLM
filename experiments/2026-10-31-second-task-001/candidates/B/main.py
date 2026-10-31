from __future__ import annotations

from typing import List, Literal, Optional

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
    q: Optional[str] = Query(default=None, min_length=1, description="标题搜索，大小写不敏感"),
    sort: Literal["id", "title"] = Query(default="id", description="排序字段"),
    order: Literal["asc", "desc"] = Query(default="asc", description="排序方向"),
    limit: int = Query(default=20, ge=1, le=100, description="每页数量"),
    offset: int = Query(default=0, ge=0, description="偏移量"),
) -> dict:
    items = list(_TODOS)

    if tag is not None:
        items = [item for item in items if tag in item["tags"]]

    if q is not None:
        q_lower = q.lower()
        items = [item for item in items if q_lower in item["title"].lower()]

    if sort == "title":
        items.sort(key=lambda item: (item["title"].lower(), item["id"]), reverse=(order == "desc"))
    else:
        items.sort(key=lambda item: item["id"], reverse=(order == "desc"))

    total = len(items)
    page = items[offset: offset + limit]
    return {"items": page, "total": total, "limit": limit, "offset": offset}