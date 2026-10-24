你是资深 FastAPI 工程师。请在**只修改** `app/main.py` 的前提下，为待办列表接口增加标签筛选与分页。

## 用户需求

给待办列表接口加标签筛选和分页，支持 limit/offset，返回 total。

## 当前 baseline `app/main.py`

```python
{{BASELINE}}
```

## 验收测试 `tests/test_tags_pagination.py`（不得修改）

```python
{{TESTS}}
```

## 硬性约束

1. 只能修改 `app/main.py`；不得修改测试文件；
2. 保持 `POST /todos` 的创建行为与 201 状态码；
3. `GET /todos` 返回对象：`{"items": [...], "total": int, "limit": int, "offset": int}`；
4. `tag` 可选；`limit` 默认 20，范围 1–100；`offset` 默认 0，最小 0；非法参数由 FastAPI 返回 422；
5. 分页在过滤之后执行，`total` 为过滤后的总数；
6. 只使用标准库 + FastAPI/Pydantic，不引入数据库。

## 输出格式

只输出一个完整的 `app/main.py`，放在一个 ```python 代码块中；不要输出解释或其他文件。
