你是资深 FastAPI 工程师。请先在心里列出这个需求的边界条件，再实现；**只修改** `app/main.py`。

## 用户需求

在已有 FastAPI 待办服务（已支持 tag 筛选 + limit/offset 分页）上，增加标题搜索 `q` 与排序 `sort/order`，并保持与 tag、分页组合时正确。

## 当前 baseline `app/main.py`

```python
{{BASELINE}}
```

## 验收测试 `tests/test_search_sort.py`（不得修改）

```python
{{TESTS}}
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
