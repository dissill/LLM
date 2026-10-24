你是资深 FastAPI 工程师。请先在心里列出这个需求的边界条件，再实现；**只修改** `app/main.py`。

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
