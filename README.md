# PromptForge Demo v0.2 — FastAPI 方案竞演（DeepSeek 实测）

> 首届 openJiuwen 智能体创新大赛 · Coding 赛道 ｜ 团队：**deforoout**
> 仓库：https://github.com/dissill/LLM

本仓库是 PromptForge 的 **Demo v0.1/v0.2（A 路线：最小真实闭环）**：把一句话业务需求变成可执行验收标准，让同一模型按两种提示策略各写一版 FastAPI 实现，真实跑 pytest，用证据选方案。

## 创意提交材料（2026-10-30，v1.2）

- 创意 PPT：`docs/PromptForge_Creative_PPT_v1.2.pptx`（6 页：P1–P4 + 机制/机机联动两页附页，无未来计划页）
- 设计文档 v1.2：`docs/PromptForge_设计文档_v1.2.md` / `.pdf`（新增 §3.11 机机联动层、§7.6 演进路线）
- 机机联动：规划机 / 执行机 / 评审机 + IAOV 协议；L0 单机回读已由 demo-004 实测，L1/L2 为设计目标，未冒充已实现。
- 机机联动协议草案：`spec/iaov/`（JSON Schema + Intent→Action→Observation→Verdict 示例 + 零依赖校验）
- 第二个评测任务：`tasks/fastapi-todo/v0.2/`（在 v0.1 已完成版上增加 q 搜索 + sort/order；baseline 1/6，reference 6/6）

## 实测结果（2026-10-27）

任务：给已有 FastAPI 待办 API 增加"标签筛选 + 分页"。同一个 `deepseek-flash`：

| 候选 | 提示策略 | 测试 | 失败用例 | 模型耗时 | token 费用 |
|---|---|---|---|---|---|
| A | raw-keyword（只有一句话需求） | **3/6** | A1 默认 limit、A3/A4 响应缺 limit/offset | 12.4s | ¥0.0096 |
| B | compiled-srd（SRD + 6 条验收 + 边界清单） | **6/6** | 无 | 5.7s | ¥0.0055 |

> 结论：同样的模型、同样的任务，提示词编译后 6/6 通过，而且更快、更便宜。
> 证据原文：`experiments/2026-10-27-demo-004/`（evidence JSON、decision.md、候选代码）；三次运行 A 为 4/6、3/6、3/6，B 三次均 6/6。
> 费用口径：DeepSeek 官方空闲时段价（输入 1 元/M、输出 4 元/M），由真实 token usage 计算。

## 第二个任务（2026-10-31，复现）

任务：在 v0.1 已完成版上增加 `q` 标题搜索 + `sort/order` 排序，并与 tag/分页组合。baseline 保留旧行为，因此 A1 通过（1/6）；reference 6/6。

| 候选 | 策略 | 测试 | 失败用例 | 模型耗时 | token 费用 |
|---|---|---|---|---|---|
| A | raw-keyword | **4/6** | A5 组合查询、A6 非法参数 | 39.2s | ¥0.0310 |
| B | compiled-srd | **6/6** | 无 | 8.4s | ¥0.0078 |

> 结论：两个任务里 B 均为 6/6；A 为 3/6、4/6，raw 提示方差更大，第二次输出 7,634 tokens，费用更高。
> 证据：`experiments/2026-10-31-second-task-001/`；样本仍小，不宣称统计显著。

## 快速开始（本地）

需要 Python 3.11+。

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
# source .venv/bin/activate

pip install -r requirements.txt
```

### 1) 自检（不需要模型 key）

```bash
python scripts/check_harness.py
# 预期：baseline 6 failed → reference 6 passed
```

### 2) 真实运行（需要 DeepSeek API Key）

```bash
# PowerShell 示例（key 只在当前窗口，不要写进仓库）
$env:MODEL_BASE_URL = "https://api.deepseek.com"
$env:MODEL_API_KEY  = "<你的 DeepSeek Key>"
$env:MODEL_PRICE_IN_CNY_PER_M = "1"    # 空闲时段；高峰改为 2
$env:MODEL_PRICE_OUT_CNY_PER_M = "4"   # 空闲时段；高峰改为 8

python -m promptforge.cli --task tasks/fastapi-todo/v0.1 --out runs/demo-001
```

> 若使用华为云 MaaS：把 `MODEL_BASE_URL` 换成 TokenHub 地址、模型名换成对应 MaaS 模型；注意 API 网关 IP 白名单（APIG.0402）。

## 目录结构

```text
.
├─ tasks/fastapi-todo/v0.1/     # 任务：TASK.md + baseline + 6 条验收测试 + reference + prompts
├─ promptforge/                 # CLI：模型调用、执行测试、证据包、决策卡
├─ scripts/check_harness.py     # harness 自检（baseline 失败 / reference 通过）
├─ experiments/2026-10-27-demo-004/  # 真实运行证据（evidence/decision/候选代码）
├─ docs/DemoBrief_v0.2.*        # 官方模板 Demo Brief（PPT/PDF/MD）
├─ docs/PromptForge_设计文档_v1.1.md
└─ .github/workflows/ci.yml     # CI：安装依赖 + harness 自检
```

## 两类证据

| 证据 | 来源 | 用途 |
|---|---|---|
| pytest 通过率 / 失败用例 | 真实执行 `pytest -q` | 硬约束：6/6 才推荐 |
| 执行耗时 | 子进程墙钟时间 | 方案对比 |
| token 用量 / 费用 | 模型 API `usage` × 价格快照 | 成本账单（未配置价格时为 null） |

## 与比赛材料的关系

- 设计文档：`docs/PromptForge_设计文档_v1.1.md`
- Demo Brief：`docs/DemoBrief_v0.2.md`（含 60 秒/3 分钟分镜）
- 创意 PPT：`docs/DemoBrief_v0.2.pptx`（基于官方模板填写）

## 合规与数据

- 模型调用仅使用官方 API / 本地部署；仓库不含任何密钥。
- `experiments/` 下为真实运行记录；不伪造、不手填。
- 不使用大赛评测集训练/调参/设计提示词。

## License

Apache-2.0，见 `LICENSE`。
