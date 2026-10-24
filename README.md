# PromptForge Demo v0.1 — FastAPI 方案竞演

> 仓库：https://github.com/dissill/LLM ｜ 团队：deforoout

> 首届 openJiuwen 智能体创新大赛 · Coding 赛道 ｜ 团队：**deforoout**
> 本仓库是 PromptForge 的 **Demo v0.1（A 路线：最小真实闭环）**：把一句话业务需求变成可执行验收标准，让多个模型各写一版 FastAPI 实现，真实跑 pytest，用证据选方案。

## Demo 要证明什么

同样一句需求——**"给待办列表接口加标签筛选和分页，支持 limit/offset，返回 total"**——两个模型/两种提示策略各写一版 `app/main.py`。PromptForge：

1. 先把需求编译成 **6 条可执行验收标准**（`tasks/fastapi-todo/v0.1/TASK.md`）；
2. 生成 2 份候选实现（不同模型 × 不同提示策略）；
3. 在临时副本中真实执行 `pytest`，采集通过率、失败用例、耗时、token 费用；
4. 按"硬约束优先"给出决策卡：推荐 + 证据链 + 次优备选 + 成本。

> 数据规则：仓库里的示例结果、PPT 里的"4/6 / 6/6"都是**预期演示剧情**，会标注"待实测"；真实结果只能来自实际运行日志，不伪造、不手填。

## 快速开始（本地）

需要 Python 3.11+。

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
# source .venv/bin/activate

pip install -r requirements.txt

# 1) 自检：baseline 应失败，reference 应 6/6 通过
python scripts/check_harness.py

# 2) 真实跑 Demo（需要模型 API 配置）
#    MODEL_BASE_URL 形如 https://<your-endpoint>/v2
#    MODEL_API_KEY 为对应 key
python -m promptforge.cli --task tasks/fastapi-todo/v0.1 --out runs/demo-001

# 3) 无模型时可回放已缓存的真实候选结果（会明确标注 source=replay）
python -m promptforge.cli --task tasks/fastapi-todo/v0.1 --out runs/demo-replay --replay
```

## 目录结构

```text
.
├─ tasks/fastapi-todo/v0.1/     # 任务：TASK.md + baseline repo + 6 条验收测试 + reference + prompts
├─ promptforge/                 # CLI：模型调用、执行测试、证据包、决策卡
├─ scripts/check_harness.py     # harness 自检（baseline 失败 / reference 通过）
├─ docs/                        # Demo Brief（md/pptx/pdf）与说明
├─ experiments/                 # 真实运行记录（JSON + 原始日志，随仓库提交）
└─ .github/workflows/ci.yml     # CI：安装依赖 + harness 自检
```

## 两类证据（v0.1）

| 证据 | 来源 | 用途 |
|---|---|---|
| pytest 通过率 / 失败用例 | 真实执行 `pytest -q` | 硬约束：未全过不能推荐 |
| 执行耗时 | 沙箱/子进程墙钟时间 | 质量-成本对比 |
| token 用量 / 费用 | 模型 API `usage` × 价格快照 | 成本账单（未配置价格时写 null） |
| 评委分（可选） | 异构模型盲评 | v0.1 仅解释，不参与硬决策 |

## 与比赛材料的关系

- 设计文档：`PromptForge 设计文档 v1.1`（另附）
- Demo Brief：`docs/DemoBrief_v0.1.md`（含 60 秒/3 分钟分镜）
- 创意 PPT：`docs/DemoBrief_v0.1.pptx`（基于官方模板填写）

## 合规与数据

- 模型调用仅使用官方 API / 本地部署；仓库不含任何密钥。
- `runs/` 下真实运行日志才可作为对外证据；`replay` 结果必须标注来源。
- 不使用大赛评测集训练/调参/设计提示词。

## License

Apache-2.0，见 `LICENSE`。
