from __future__ import annotations

from typing import List, Optional

from fastapi import FastAPI, Query
from pydantic import BaseModel

app = FastAPI(title="Todo API", version="0.1.0")

# In-memory store for the demo (reset by process restart)
_TODOS: List[dict] = []


class TodoCreate(BaseModel):
    title: str
    tags: List[str] = []


class Todo(TodoCreate):
    id: int


class TodoPage(BaseModel):
    items: List[Todo]
    total: int
    limit: int
    offset: int


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/todos", response_model=Todo, status_code=201)
def create_todo(payload: TodoCreate) -> dict:
    item = {"id": len(_TODOS) + 1, "title": payload.title, "tags": list(payload.tags)}
    _TODOS.append(item)
    return item


@app.get("/todos", response_model=TodoPage)
def list_todos(
    tag: Optional[str] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> dict:
    filtered = _TODOS
    if tag is not None:
        filtered = [todo for todo in _TODOS if tag in todo["tags"]]

    total = len(filtered)
    items = filtered[offset : offset + limit]

    return {
        "items": items,
        "total": total,
        "limit": limit,
        "offset": offset,
    }