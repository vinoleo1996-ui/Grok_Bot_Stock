# moneyflow VOID + 低内存 code_change 签发回执

- 时刻：2026-10-25T05:08:36-04:00（America/New_York）
- 旧 run.ok `68c04741…` **已 VOID** → `output/strategy_hiliq/_consumed/ARCH_RUN_AUTH_STRATEGY_MONEYFLOW_STACK_DIAG_RUN.VOID.20261025T050726ET.ok`
- 裁定文：`docs/v2/ARCH_STRATEGY_MONEYFLOW_VOID_LOWMEM_DECISION_20261025_ZH.md`
- **code_change .ok**：`output/strategy_hiliq/ARCH_RUN_AUTH_STRATEGY_MONEYFLOW_STACK_DIAG_LOWMEM_V11_CODE_CHANGE.ok`
  - sha256：`b2340c67ab78e526ba65894be2182d0c54885441b8fe7f6e2578ecd196b1c81a`
  - allow_write_code=true；allow_run=false
  - 目标将来 run：`rss_cap_mb=2048`；out_dir `moneyflow_stack_8020_lowmem_20261025`；复用 blended `3f8a2b33…`
- 下一步：Strategy 交 DIFF → Arch 审 → 另签 run.ok（避叶25）。live=false。
