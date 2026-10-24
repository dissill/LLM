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
