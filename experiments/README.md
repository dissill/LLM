# experiments/

真实运行记录目录。每次 Demo 运行后，把 `runs/<run-id>/` 下的内容复制或归档到这里（保留原始日志，不复写）。

建议结构：

```text
experiments/
└─ 2026-10-30-fastapi-todo-001/
   ├─ evidence/
   │  ├─ baseline.json
   │  ├─ A.json
   │  └─ B.json
   ├─ candidates/
   │  ├─ A/main.py
   │  └─ B/main.py
   ├─ decision.md
   ├─ env.json          # 模型名、价格快照、Python 版本、日期
   └─ raw/              # 原始 pytest 输出（可选）
```

规则：

1. 只追加、不覆盖；每次运行一个新目录。
2. 费用/token 必须来自模型 API `usage`，价格快照写入 `env.json`；缺失字段写 `null`。
3. 对外材料引用任何数字，必须能指向这里的具体文件。
4. 不提交任何 API Key / Token / 隐私数据。
