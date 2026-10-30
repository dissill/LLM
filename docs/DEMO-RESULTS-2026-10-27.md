# Demo 实测记录 · 2026-10-27（runs/demo-004）

> 全部数字来自真实运行，原始 evidence 见 `experiments/2026-10-27-demo-004/evidence/`。
> 模型：DeepSeek API `deepseek-flash`（OpenAI 兼容）；运行时间：2026-10-27 20:05（北京时间，空闲时段）。
> 价格快照：输入 1 元/M、输出 4 元/M（DeepSeek 官网 2026-10-27 抓取）。

## 任务

给已有 FastAPI 待办 API 增加"标签筛选 + 分页"，6 条验收测试（A1–A6）。

## 结果

| 候选 | 提示策略 | 测试 | 失败用例 | 模型耗时 | 测试耗时 | tokens in/out | 费用 |
|---|---|---|---|---|---|---|---|
| A | raw-keyword（只有一句话需求） | **3/6** | A1 默认 limit、A3/A4 响应缺 limit/offset | 12,406 ms | 2,473 ms | 325 / 2,324 | ¥0.0096 |
| B | compiled-srd（SRD+6 条验收+边界） | **6/6** | 无 | 5,732 ms | 2,350 ms | 1,536 / 1,001 | ¥0.0055 |

- 决策卡：`decision.md` 推荐 B（6/6；A 3/6 不满足硬约束）。
- 三次运行对比：demo-002（09:03）A 为 4/6；demo-003（18:48）A 为 3/6；demo-004（20:05）A 为 3/6；B 三次均 6/6。单次运行存在波动，B 稳定全过。
- 费用差异来源：A 输出 2,324 tokens，B 输出 1,001 tokens；编译后的提示词让输出更聚焦，不是"模型更强所以更便宜"。

## 复现

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\dsh work 1\_build\demo\run_demo.ps1" -Out "runs\demo-004"
```

`run_demo.ps1` 会按北京时间自动选择峰时/空闲价（工作日 9-12、14-18 为峰时 2/8，其余 1/4）。

## 数据口径

- 费用 = 真实 token usage × 价格快照；evidence 中 `cost.price_snapshot` 有记录。
- 未配置价格时 `cost.cny` 为 `null`，不得手填。
- 本记录不包含任何 API Key。
