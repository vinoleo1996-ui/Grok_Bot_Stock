# 主 · 叶27 X2 selfcheck_v2 MATCH+GO

| 项 | 值 |
|---|---|
| 角色 | 主 Agent |
| 时刻 | `2026-10-26T01:02:39-04:00`（America/New_York） |
| 窗令 | `f268d120` **00:55–01:40 ET** expires **01:42** |
| 审阅 | `46526394` PASS_WITH_CONDITIONS |
| Arch SIGNED | `b5484e5a` @ `2026-10-26T01:01:52-04:00` |
| 结论 | **MATCH+GO** — 令 AI prelaunch 单次 PRIMARY `--execute` |

## 盘证 MATCH

| 项 | sha8 |
|---|---|
| `.ok` | `3c19dd7d`（∉ forbid 八票含 `0f50daf7`） |
| QUIET | `69cd9d8e`（8795 quiet=true；勿 lift） |
| 脚本 | `a40d7069` |
| 构建 UNCHANGED | `585ba746` |
| 审阅 | `46526394` |
| 窗令 | `f268d120` |
| alpha | `652b8a68` |
| meta | `85c2dc78` |
| summary | `80596bff` |
| MemAvailable | ≈6.6Gi（软地板已过；prelaunch 可开） |

## PRIMARY CLI（单次）

```
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf27_x2_selfcheck_v2.py --universe HILIQ --window x2 --alpha-path output/ai_factory/leaf27_on_minus_id_idio_ivol/alpha_HILIQ_x2_20261025_224033.parquet --execute
```

## 硬钉

- rss 软帽 **1500** MB 禁抬；峰＞1500→停+上报；peak_proof **REQUIRED**
- ≠ X2 ACCEPT；禁 Book-Smoke；禁改构建 `585ba746`；禁覆写钉盘 alpha/meta/summary
- forbid 八票含 `0f50daf7`；baseline_evac CONSUMED 不解阻本票以外 X2
- FALLBACK **无**；完后交 RUN_RECEIPT（权重 sha + selfcheck_v2.json sha + peak）
- Arch 不代跑不 lift；live=false

## 下一跳

AI 交回执 → Arch CONSUMED+lift → 主收口。**不推 Leo**（等 DONE/ABORT 再报）。
