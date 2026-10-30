# PromptForge Demo Brief v0.2（A 路线 · FastAPI 实测版）

> 参赛赛事：首届 openJiuwen 智能体创新大赛 · Coding 赛道 ｜ 团队：**deforoout** ｜ 日期：2026-10-27
> 对应模板：官方创意 PPT 模板（P1–P6 保留，新增 2 页 Demo 补充页）
> 数据规则：本文件所有测试结果、token 与费用均来自 **2026-10-27 的真实运行**（`runs/demo-004`），不是预期值；原始 evidence 随仓库提交。

---

## 0. 一页版（PPT P2–P4 的内容来源）

**创意名称**：PromptForge（提示词锻造台）
**所属主题**：Coding
**一句话**：把"一句话需求"编译成可验收的方案，让多个候选真实跑一遍，用证据（而不是感觉）告诉你选哪个。

**Demo 已证明的一件事**：同一个 `deepseek-flash`，候选 A 只给一句话需求，候选 B 给 PromptForge 编译后的 SRD（6 条验收标准 + 边界清单）：

| | A：raw-keyword | B：compiled-srd |
|---|---|---|
| 测试 | **3/6** | **6/6** |
| 失败用例 | A1 默认 limit=10（期望 20）；A3/A4 响应缺 limit/offset | 无 |
| 模型耗时 | 12.4s | 5.7s |
| 测试耗时 | 2.5s | 2.4s |
| token 费用 | **¥0.0096** | **¥0.0055** |

> 结论：**同样的模型、同样的任务，提示词编译后 6/6 通过，而且更快、更便宜。** 这是 PromptForge 的核心价值，也是本轮 Demo 的主线。

---

## 1. 场景与输入（已确认）

**场景**：给已有的 FastAPI 待办 API 增加"标签筛选 + 分页"。

| 项 | 内容 |
|---|---|
| 用户输入（一句话） | "给待办列表接口加标签筛选和分页，支持 limit/offset，返回 total。" |
| 任务载体 | `repo/app/main.py`（FastAPI + 内存存储，baseline 只有 POST /todos 和全量 GET /todos） + `repo/tests/test_tags_pagination.py`（6 条验收用例） |
| 为什么选它 | 业务真实（列表筛选/分页高频）、代码量小、运行快、边界清晰（默认值/tag/limit/offset/空结果/非法参数） |

**SRD 验收标准（6 条，全部可执行）**

| ID | 验收标准 |
|---|---|
| A1 | 响应结构 `{items,total,limit,offset}`；无参数时 `limit=20、offset=0` |
| A2 | `tag` 过滤：只返回 tags 中包含该标签的记录 |
| A3 | `limit/offset` 分页，`total` 为过滤后总数 |
| A4 | `tag + limit + offset` 组合生效，顺序正确 |
| A5 | 空结果：200 + `items=[]、total=0` |
| A6 | 非法参数：`limit=0/101`、`offset=-1` 返回 422 |

---

## 2. 候选与实测结果

| 候选 | 模型 | 提示策略 | 实测结果（`runs/demo-004`） |
|---|---|---|---|
| A | deepseek-flash | raw-keyword：只给一句话需求 + baseline 代码，不给验收测试 | **3/6**；失败 A1/A3/A4；12.4s；¥0.0096 |
| B | deepseek-flash | compiled-srd：给 SRD + 6 条验收测试 + 边界清单 | **6/6**；5.7s；¥0.0055 |

**A 的具体失败原因（真实 evidence）**

- A1：A 把 `limit` 默认值写成 10，测试要求 20；
- A3/A4：A 的响应模型只返回 `items/total`，缺少 `limit/offset`，测试断言响应结构失败；
- A6：A 加了 `le=100`，这一条通过。

> 三次运行波动：demo-002（09:03）A 为 4/6；demo-003（18:48）A 为 3/6；demo-004（20:05）A 为 3/6（失败 A1/A3/A4）；B 三次均 6/6。结论按最新一次 demo-004 引用，并在材料中说明单次运行的波动性。

---

## 3. 证据与决策（Demo v0.1 规则）

**决策规则**：硬约束（测试 6/6）→ 通过者按耗时/费用排序；未全过只能作"观察/次优"。

**本次决策卡**：推荐 B（6/6）；A 3/6 不满足硬约束。费用来自 DeepSeek 官方价（空闲时段 1/4 元每百万 token，2026-10-27 20:05 运行），由真实 token usage 计算：

- A：325 输入 / 2324 输出 → ¥0.0096
- B：1536 输入 / 1001 输出 → ¥0.0055

> v0.1 不启用 LLM 评委；决策只用测试通过 + 耗时 + 费用，避免"多评委"在早期 Demo 中引入噪声。

---

## 4. 分镜：60 秒创意版 / 3 分钟 DEMO 版

### 4.1 60 秒创意版（11-10 前）

| 时间 | 画面 | 台词/字幕 |
|---|---|---|
| 0–5s | 黑底白字 | "AI 写的接口，你敢直接合并吗？" |
| 5–15s | 输入一句话需求 | "给待办列表加标签筛选和分页，返回 total。" |
| 15–30s | 同一模型两个候选并行生成 | "同一个 DeepSeek，两份提示词：一份只有一句话，一份编译成 6 条验收标准。" |
| 30–45s | pytest 红绿 | "raw 版 3/6，漏了默认 limit 和响应字段；compiled 版 6/6。" |
| 45–55s | 决策卡 | "推荐 compiled 版：6/6、4.6 秒、不到 1 分钱；raw 版更慢还更贵。" |
| 55–60s | Slogan | "PromptForge：一次选对，少返工。" |

### 4.2 3 分钟 DEMO 版（12-27）

| 时间 | 内容 |
|---|---|
| 0:00–0:20 | 问题：提示词质量方差大、单模型自评不可靠、返工贵 |
| 0:20–0:50 | 输入需求 + 编译器回显 SRD（6 条验收标准） |
| 0:50–1:40 | 同一模型两候选并行生成；沙箱执行；测试红绿滚动 |
| 1:40–2:20 | 证据对比：失败用例（A1/A3/A4）、耗时、token 费用 |
| 2:20–2:45 | 决策卡：推荐 B + 证据链 + 成本 |
| 2:45–3:00 | 可复现与扩展：evidence 可回放；下一步接 openJiuwen WorkSwarm |

---

## 5. 技术栈与实测环境

| 层 | 方案 | 状态 |
|---|---|---|
| 模型 | DeepSeek API（`deepseek-flash`，OpenAI 兼容） | 已实测 |
| 任务载体 | FastAPI + pytest（6 条验收用例） | 已实测 |
| 执行 | 本机 venv + subprocess（Python 3.13 / FastAPI 0.162 / pytest 9.1） | 已实测 |
| 证据 | `evidence.json` + pytest 原始输出 | 已实测 |
| 展示 | v0.1 CLI 输出；v0.2 Streamlit 看板 | v0.2 |
| 生态 | openJiuwen WorkSwarm/AgentOS（S6） | 待接入 |

> 华为云 MaaS 的 TokenHub 端点因 API 网关 IP 白名单（APIG.0402）暂不可达，已切换 DeepSeek；后续如账号管理员放开 IP ACL，可恢复 MaaS 的 glm/openpangu 候选。

---

## 6. 风险与兜底

| 风险 | 影响 | 兜底 |
|---|---|---|
| 模型调用失败/限流 | 演示卡住 | 缓存真实结果回放；备用模型 |
| 单次运行波动 | A 的失败用例数变化 | 展示最新一次完整 evidence；说明多次运行结论一致（B 均 6/6） |
| 费用价格口径 | 峰时/空闲价不同 | 运行时按官方时段设置价格；evidence 记录 price_snapshot |
| 现场断网 | 无法调用模型 | 本地录屏 + evidence 回放，不假装实时 |

---

## 7. 任务状态（截至 2026-10-27）

| ID | 任务 | 状态 |
|---|---|---|
| T-101 | 冻结 FastAPI 任务 + 6 条验收测试 + reference | ✅ 完成 |
| T-102 | CLI 最小闭环（模型调用 → 测试 → evidence → decision） | ✅ 完成 |
| T-103 | 真实跑通并记录原始日志 | ✅ 完成（demo-002 / demo-003 / demo-004） |
| T-104 | 更新官方模板 PPT（DeepSeek / deforoout / 实测数据） | 进行中 |
| T-105 | 离线回放与彩排 | 待做 |
| T-106 | 11-10 前提交创意材料 | 待做 |

---

## 8. 与官方 PPT 模板的对应关系

| 模板页 | 本 Brief 内容 |
|---|---|
| P1 封面 | 创意名称 + 团队 deforoout + 赛道 |
| P2 创意名称/描述/主题/场景 | §0 一页版 + §1 场景 |
| P3 方案构想 | §0 最小闭环 + §3 决策规则 + §5 技术栈 |
| P4 DEMO/用户路径 | §4 分镜 + Demo 流程图 |
| 补充页 1 | §4 分镜（60 秒/3 分钟） |
| 补充页 2 | §3 证据与兜底（真实数据规则） |

---

## 9. 实测记录（可复现）

- 运行时间：2026-10-27 20:05（北京时间，空闲时段）
- 模型：`deepseek-flash`（DeepSeek API，OpenAI 兼容）
- 价格快照：输入 1 元/M、输出 4 元/M
- 证据目录：`runs/demo-004/evidence/{baseline,A,B}.json`
- 决策卡：`runs/demo-004/decision.md`
- 候选代码：`runs/demo-004/candidates/{A,B}/main.py`
- 复现命令：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\dsh work 1\_build\demo\run_demo.ps1"
```

> 本 Brief 为内部工作稿；对外提交以官方 PPT 模板填好的 v0.2 版本为准。所有数字以 evidence 原文为准，不手改。
