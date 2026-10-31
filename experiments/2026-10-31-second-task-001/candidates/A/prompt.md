你是一名后端工程师。现有 FastAPI 待办服务代码如下（已经有标签筛选和分页）：

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

用户需求：给待办列表加上搜索和排序，能和标签、分页一起用；搜索按标题包含、不区分大小写，排序支持 id/title 和 asc/desc，非法参数返回 422。

请直接给出修改后的完整 `app/main.py`，放在一个 ```python 代码块中；不要输出解释。
