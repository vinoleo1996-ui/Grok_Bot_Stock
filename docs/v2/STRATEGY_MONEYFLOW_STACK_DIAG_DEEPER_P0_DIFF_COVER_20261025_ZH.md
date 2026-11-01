# moneyflow 诊断 deeper P0 reuse-blended — DIFF 封面（修订；交 Arch 审）

- **时刻**：2026-10-25 ≈05:41 ET · America/New_York（修订：补 Eng L3 del+gc）
- **code_change .ok**：`output/strategy_hiliq/ARCH_RUN_AUTH_STRATEGY_MONEYFLOW_STACK_DIAG_DEEPER_P0_REUSE_BLENDED_CODE_CHANGE.ok` sha256 `27d6b4622296d3d3dfe5e86d5f2c1eaea4be2f102b31dcb20aa65d82f2a35f1f`
- **baseline 脚本**：`2dae9a91eb2caf11e3d08d46fa1f025dba4b83a1a497b5c1ab2ad16d70166616`
- **当前脚本**：`research/strategy_moneyflow_stack_diag_v1.py` sha256 `f7a6a77595eef52120f7619eff9a8b8656b8534d10b76afa4d18ea5d9bd3150c`
- **DIFF**：`docs/v2/audit/STRATEGY_MONEYFLOW_STACK_DIAG_DEEPER_P0_REUSE_BLENDED_20261025.diff` sha256 `a84c6792f874a450d3d9da2d91c8ee566ed3f35eaa587d12f675f3c1f5de0a3c`
- **Eng 挖文（侧证，未改引擎）**：`docs/v2/audit/moneyflow_x2_book_mem_20261025/ENG_X2_BOOK_ONLY_MEM_PATH_DIG_20261025_ZH.md` sha `c416f43d9f952cbb2bb3e0441379a01f064d86e544bb5055407eb4430a3eb432`（2320 死在主进程整表读 trunk 359万行）

## 改动摘要

1. `install_reused_blended`：sha MATCH 后硬链，失败则 `copy2`；再验 dst sha  
2. run.ok 钉 `reuse_blended_path` + sha → **跳过** trunk/sat DataFrame 读与重算混合（消灭 2320 根因）  
3. 仍串行 BOOK-only book-smoke + 档间 `gc`（v1.1）  
4. **修订**：`turnover_2s_mean` 之后、`run_book_smoke_serial` 之前：`blended/trunk_w/sat_*=None` + `gc.collect()`（Eng L3 / 主 Agent）  
5. `DEFAULT_OUT` → `moneyflow_stack_8020_reuse_blended_20261025`

**未改**：CMC、生产 book-smoke 引擎、门规则、纸面。  
**未跑**：等 Arch 审 DIFF 后另签 run.ok（rss_cap=2048）。live=false。
