# 任务：给 FastAPI 待办 API 加「搜索 + 排序」（v0.2）

> 这是 PromptForge 的第二个评测任务，用来验证方法不只对单个 A/B demo 有效。baseline 是 **v0.1 已完成标签筛选 + 分页的版本**；本次只新增搜索与排序，并保持旧行为。

## 用户需求（一句话）

> 给待办列表加搜索和排序，能和标签、分页一起用；搜索按标题包含、不区分大小写，排序支持 id/title 和 asc/desc，非法参数返回 422。

## 现状（baseline）

`repo/app/main.py` 已支持：

- `POST /todos`：创建待办，字段 `title`、`tags`；
- `GET /todos`：`tag` 过滤、`limit/offset` 分页，返回 `{items,total,limit,offset}`。

**还没有**：`q` 搜索、`sort` 排序、`order` 方向。

## 验收标准（6 条，全部可执行）

| ID | 需求 | 测试断言 |
|---|---|---|
| A1 | 默认响应结构 `{items,total,limit,offset}`；`limit=20/offset=0`；默认按 id 升序 | 创建 3 条带唯一 tag 的数据，GET `?tag=...`，检查结构与顺序 |
| A2 | `q` 按标题包含搜索，不区分大小写；`total` 为过滤后总数 | 3 条标题中 2 条含 `buy`（其中一条大写），GET `?tag=...&q=BUY`，断言 total=2 |
| A3 | `sort=title&order=asc` 按标题升序（大小写不敏感） | 三条 `zeta/Alpha/beta`，断言返回 `Alpha,beta,zeta` |
| A4 | `sort=id&order=desc` 按 id 降序 | 创建 4 条，断言 ids 逆序 |
| A5 | `tag + q + sort + order + limit/offset` 组合生效，先过滤再排序再分页 | 4 条 `task` + 1 条干扰，GET 组合参数，断言 total=4、第 2 页内容 |
| A6 | 非法 `sort/order` 或空 `q` 返回 422 | `sort=created_at`、`order=sideways`、`q=` 逐一断言 |

## 约束

- 只能修改 `app/main.py`；不得修改 `tests/`、不得新增测试。
- 保持 `POST /todos` 创建行为与 201。
- 保持响应字段 `items/total/limit/offset`；默认 `limit=20, offset=0`。
- 过滤顺序：tag → q → sort → pagination；`total` 是过滤后的总数。
- 只使用标准库 + FastAPI/Pydantic；不引入数据库。
- Python 3.11+，依赖见 `repo/requirements.txt`。

## 运行

```bash
cd tasks/fastapi-todo/v0.2/repo
python -m pytest -q          # baseline：预期 1/6（A1 通过，A2-A6 失败）
```

## 交给 PromptForge

```bash
cd _build/demo/repo/LLM
python -m promptforge.cli --task tasks/fastapi-todo/v0.2 --self-check
python -m promptforge.cli --task tasks/fastapi-todo/v0.2 --out runs/second-task-001
```

`reference/` 只用于自检，不参与候选生成；真实结果必须写入 `runs/` 和 `experiments/`，不允许手改。
