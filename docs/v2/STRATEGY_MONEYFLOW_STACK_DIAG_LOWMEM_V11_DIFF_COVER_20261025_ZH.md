# moneyflow 诊断 lowmem v1.1 — DIFF 封面（交 Arch 审）

- **时刻**：2026-10-25 ≈05:13 ET · America/New_York
- **code_change .ok**：`output/strategy_hiliq/ARCH_RUN_AUTH_STRATEGY_MONEYFLOW_STACK_DIAG_LOWMEM_V11_CODE_CHANGE.ok` sha256 `b2340c67ab78e526ba65894be2182d0c54885441b8fe7f6e2578ecd196b1c81a`
- **baseline 脚本**：`c2ff60451ef1a20b74c287863762a8c78d8b616443e1cfeb188761c106694c63`
- **当前脚本**：`research/strategy_moneyflow_stack_diag_v1.py` sha256 `2dae9a91eb2caf11e3d08d46fa1f025dba4b83a1a497b5c1ab2ad16d70166616`
- **DIFF**：`docs/v2/audit/STRATEGY_MONEYFLOW_STACK_DIAG_LOWMEM_V11_20261025.diff` sha256 `e5e0b6da101f3dc7b7c6c9b6d8d39959f309a146ac0c3909916d1ee3cc2d5739`（相对 baseline 可 `patch -p1` 干净落地）

## 改动摘要（仅 book-smoke 调用环）

1. `--capitals` **单档**；`run_book_smoke_serial` 对 tiers **串行**子进程  
2. `--arms BOOK`（去掉 C0）  
3. 输出 `book_smoke/aum_<tier>/` + 汇总 `book_smoke_summary_agg.json`  
4. 每档后 `gc.collect()`；`smoke_dir.mkdir` 后再写 `serial.log`  
5. nav 路径兼容 `aum_t/aum_t/X2/BOOK` 与 `aum_t/X2/BOOK`

**未改**：CMC、权重混合逻辑、门B/GATE_V3 规则、禁止纸面。  
**未跑**：`allow_run=false`；等 Arch 审 DIFF 后另签 run .ok（计划 out_dir `moneyflow_stack_8020_lowmem_20261025`，rss_cap=2048，复用 blended `3f8a2b33…`）。live=false。
