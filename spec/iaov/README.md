# IAOV：机机联动的结构化消息协议（v1.0）

> 这是 PromptForge 设计文档 §3.11 的协议落地样例，不是“完整多智能体系统已实现”的声明。

## 文件

| 文件 | 作用 |
|---|---|
| `iaov.schema.json` | JSON Schema（2020-12）定义消息信封与四类 payload |
| `example.sequence.jsonl` | 一条最小的 Intent → Action → Observation → Verdict 序列 |
| `validate_iaov.py` | 零依赖校验脚本（检查必填字段、枚举、序列顺序） |

## 四类消息

- **Intent**：要达成什么（引用 SRD / 验收标准）；
- **Action**：允许做什么（工具、参数、权限、超时、幂等键）；
- **Observation**：实际发生了什么（Evidence Packet、日志、截图/关键帧、哈希、环境指纹）；
- **Verdict**：如何判定（规则结果、评委分、置信度、下一步建议）。

每个信封都带 `task_id / candidate_id / endpoint_id / trace_id / contract_hash / permission_scope / budget`。自然语言只能作为 Observation 的附件，不能作为决策依据。

## 校验

```bash
python spec/iaov/validate_iaov.py
# 预期：OK: schema JSON valid; 4 IAOV messages valid
```

## 示例说明

`example.sequence.jsonl` 使用 `runs/demo-004` 的真实 A 候选结果（3/6、¥0.0096、12.4s）构造了一条消息序列，用来演示协议；**它不是运行时自动产生的日志**。真实运行日志仍在 `experiments/2026-10-27-demo-004/`。

## 与设计文档的关系

- 设计文档 §3.11：机机联动的概念、层级、难点与边界；
- 设计文档 §7.6：L0–L3 演进路线；
- 本目录：L0/L1 的协议草案与示例，方便后续把执行机、评审机接进来。
