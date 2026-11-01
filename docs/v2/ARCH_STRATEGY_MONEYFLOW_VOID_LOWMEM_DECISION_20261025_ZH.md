# moneyflow 诊断 VOID 后裁定（Arch）

- 时刻（America/New_York）：2026-10-25T05:08:36-04:00
- 依据：主 Agent 05:03 P0；Strategy 回执 sha `12a095bf…`；降内存方案 `STRATEGY_MONEYFLOW_STACK_DIAG_LOWMEM_RERUN_PLAN_20261025_ZH.md`
- live=false；禁 paper / live / 抬帽硬跑

## 1. 作废（已完成）

| 项 | 值 |
|---|---|
| 旧 run.ok sha | `68c04741cbabd8cd3821146168ed262bf22672f327646a8ab7139c37bd411514` |
| 归档 | `output/strategy_hiliq/_consumed/ARCH_RUN_AUTH_STRATEGY_MONEYFLOW_STACK_DIAG_RUN.VOID.20261025T050726ET.ok` |
| 旁证 | `…/ARCH_RUN_AUTH_STRATEGY_MONEYFLOW_STACK_DIAG_RUN.VOID_MARKER.txt` sha `bb66d823…` |
| 原因 | book-smoke VmHWM≈4511.5MB > rss_cap 1536；无 summary / 门B / GATE_V3 |

## 2. 重跑路径裁定：**采纳推荐 v1.1（降内存）**

| # | 裁定 |
|---|---|
| 脚本 | **同路径补丁** `research/strategy_moneyflow_stack_diag_v1.py`（DIFF 仅 `run_book_smoke` 调用环及相关汇总） |
| 分档 | 600000、1000000 **串行**各调一次；`--capitals` 单档 |
| 臂 | `--arms BOOK`（去掉 C0）；对照仍用钉死的 trunk_ref_nav_* |
| 子目录 | `book_smoke/aum_600000/`、`book_smoke/aum_1000000/`；主进程汇总 `summary.json` |
| 内存帽 | 新 run.ok **`rss_cap_mb=2048`**（主目标 ≤2GB；**禁止**抬到 4.5GB） |
| out_dir | **新** `output/strategy_hiliq/moneyflow_stack_8020_lowmem_20261025/` |
| 旧 out_dir | 移 `_recovery/strategy/20261025T0502ET_moneyflow_stack_void/` |
| blended 复用 | **允许**：pin sha `3f8a2b33a995f381ee9e7060858a2029c1a8854a31a32b48ab4842281f188103`（跳过再剥舱混合） |
| decay | 仍钉 `REJECT`（只披露；GATE_V3 预期仍不过） |
| 窗 | 避叶25 `10:00–10:45 ET` |
| Eng | 可选并行查 book-smoke 12s 内 VmHWM≈4.5GB（不挡 Strategy v1.1） |

**不做**：抬帽硬跑；并行双档；改 CMC；改 Eng book-smoke 内核（除非另开）。

## 3. 签发顺序

1. **本轮**：签 **code_change .ok**（v1.1 补丁）→ Strategy 交 DIFF。
2. Arch 审 DIFF → 再签 **run .ok**（新 out_dir / rss_cap=2048 / pin blended / 避叶25）。
3. Strategy **在新 run.ok 前不跑**。

## 4. 一句话

旧 `68c04741` 已 VOID；走分档+BOOK-only 降内存，帽 2048MB；先 code_change，后 run。
