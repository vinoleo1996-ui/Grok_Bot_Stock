# moneyflow 剥舱+80/20 诊断 — run .ok 已签

- 时刻：2026-10-25T04:58:18-04:00（America/New_York）
- 审阅：`docs/v2/ARCH_STRATEGY_MONEYFLOW_STACK_DIAG_V1_REVIEW_ZH.md` sha `befdaa46…` → **PASS_WITH_CONDITIONS**
- live=false；研究级单次；勿混叶25/补跑/enable/纸面

## 授权

- `.ok`：`output/strategy_hiliq/ARCH_RUN_AUTH_STRATEGY_MONEYFLOW_STACK_DIAG_RUN.ok`
- sha256：`68c04741cbabd8cd3821146168ed262bf22672f327646a8ab7139c37bd411514`
- `allow_run=true`；`single_use=true`；expires `2026-10-26T04:58:18-04:00`
- **避开**叶25：`2026-10-25T10:00:00-04:00`–`10:45:00-04:00`
- `decay_outcome=REJECT`（依据 `ALPHA_DECAY_GATE_REJUDGE_20261014`：moneyflow_resid=DECAY_DOWNGRADE → 映射 REJECT；GATE_V3 将因非 KEEP 而不过，属预期披露）
- out_dir：`output/strategy_hiliq/moneyflow_stack_8020_20261025`（须事先不存在/空）

## Strategy 开跑前

1. 确认 `output/loop/RESEARCH_QUIET.lock` 不存在（脚本只查仓库根锁）。
2. 勿在叶25 窗内开跑；建议外挂 RSS≤1536MB 或回执披露 peak。
3. 消费本 .ok 后交 summary / ARTIFACT_MANIFEST 路径+sha。
