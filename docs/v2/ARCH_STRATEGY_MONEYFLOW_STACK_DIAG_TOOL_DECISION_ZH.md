# moneyflow 剥舱+80/20 诊断工具 — Arch 裁示

- 时刻（America/New_York）：2026-10-25T04:46:23-04:00
- 依据：Strategy REQ `48640e14…`；接口文 `17ac041f…`；主 04:39 研究级诊断
- live=false

## 裁示：**A（新脚本）**

- 采用 `research/strategy_moneyflow_stack_diag_v1.py`（剥舱→80/20→book-smoke/NAV→门B+GATE_V3）。
- **拒绝 B**：扩展 CMC（`alpha_combo_marginal_v1_2.py`）——与剥舱语义相反且动叶验收钉。

## 已签

- code_change .ok：`output/strategy_hiliq/ARCH_RUN_AUTH_STRATEGY_MONEYFLOW_STACK_DIAG_CODE_CHANGE.ok` sha256 `951f3ce2e8f95d73e64c1be111bdf8013ffc3eb8e754762f5d7c93858043e67b`
- **未签** run .ok；Strategy 交 DIFF 后再审签跑窗。
- 避开叶25 10:00–10:45 ET；禁 paper；禁再单独 moneyflow 烟。
