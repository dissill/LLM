# 任务：给 FastAPI 待办 API 加「标签筛选 + 分页」（v0.1）

> 这是 PromptForge Demo v0.1 的评测任务。baseline 代码在 `repo/`，6 条验收测试在 `repo/tests/test_tags_pagination.py`；`reference/` 仅用于自检测试 harness，不参与候选生成。

## 用户需求（一句话）

> 给待办列表接口加标签筛选和分页，支持 limit/offset，返回 total。

## 现状（baseline）

`repo/app/main.py` 是 FastAPI + 内存存储的待办 API：

- `POST /todos`：创建待办，字段 `title`、`tags`。
- `GET /todos`：返回**全量列表**（没有筛选、没有分页、响应不是对象）。

## 验收标准（6 条，全部可执行）

| ID | 需求 | 测试断言 |
|---|---|---|
| A1 | 默认响应结构 `{items,total,limit,offset}`；无参数时 `limit=20, offset=0` | 创建 3 条带唯一 tag 的数据，GET `?tag=a1`，检查结构、`total`、`limit`、`offset` |
| A2 | `tag` 过滤：只返回 `tags` 中包含该标签的记录 | 构造 2 条 `a2x` + 1 条 `a2y`，GET `?tag=a2x`，断言 `total=2` 且每条 tags 含 `a2x` |
| A3 | `limit`/`offset` 分页；`total` 为过滤后的总数 | 创建 5 条 `a3`，GET `?tag=a3&limit=2&offset=2`，断言 `total=5`、items 为第 3、4 条 |
| A4 | `tag` + `limit` + `offset` 组合生效，顺序正确 | 4 条 `a4` + 2 条 `a4-other`，GET `?tag=a4&limit=2&offset=1`，断言 `total=4`、items 为第 2、3 条 |
| A5 | 空结果：tag 无匹配时返回 200 + `items=[]、total=0` | GET `?tag=a5-none` |
| A6 | 非法参数：`limit=0`、`limit=101`、`offset=-1` 返回 422 | 三个请求逐一断言 `status_code == 422` |

## 约束

- **只能修改 `app/main.py`**；不得修改 `tests/`、不得新增测试、不得改测试数据。
- 保持 `POST /todos` 的创建行为与 201 状态码。
- 响应字段命名严格为 `items/total/limit/offset`。
- 默认 `limit=20`，允许范围 1–100；`offset>=0`。
- 不要求数据库；内存存储即可。
- Python 3.11+，依赖见 `repo/requirements.txt`。

## 运行测试

```bash
cd tasks/fastapi-todo/v0.1/repo
python -m pip install -r requirements.txt
python -m pytest -q
```

## 评测规则（交给 PromptForge）

1. 每条候选生成完整 `app/main.py`，替换到 baseline 的临时副本；
2. 真实执行 `pytest -q`，记录 `passed/total/failed_cases/耗时`；
3. 硬约束：6/6 才可被推荐；否则进「观察/次优」；
4. 决策卡输出推荐 + 证据引用 + 次优 + 成本（token 费用来自 API usage）。

## 数据说明

- 本任务不提供任何"预期结果"作为结论；`reference/` 只用于验证测试本身可运行（自检）。
- 候选真实生成结果与测试输出必须写入 `experiments/`，不允许手改。
