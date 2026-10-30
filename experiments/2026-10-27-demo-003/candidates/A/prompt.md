你是一名后端工程师。现有 FastAPI 待办服务代码如下：

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

用户需求：给待办列表接口加上标签筛选和分页，支持 limit/offset，返回 total。

请直接给出修改后的完整 `app/main.py`，放在一个 ```python 代码块中；不要输出解释。
