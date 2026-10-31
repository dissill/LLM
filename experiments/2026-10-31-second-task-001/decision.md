# PromptForge Demo v0.1 — 决策卡

**推荐：候选 B（deepseek-flash / compiled-srd）** — 测试 6/6 通过（硬约束满足）。

| 候选 | 模型 | 策略 | 测试 | 耗时 | token 费用 | 结论 |
|---|---|---|---|---|---|---|
| B | deepseek-flash | compiled-srd | 6/6 | 1691ms | ¥0.0078 | 推荐 |
| A | deepseek-flash | raw-keyword | 4/6 | 1924ms | ¥0.031 | 观察/不推荐 |

证据引用：pytest 输出、候选代码、耗时与 token usage 均在 `evidence/` 与 `candidates/` 下。

> 说明：Demo v0.1 仅做单任务单轮决策，样本少，结论仅用于演示；不宣称统计显著性。