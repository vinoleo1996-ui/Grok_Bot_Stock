# moneyflow lowmem v1.1 VOID + 更深降内存 P0 裁定（Arch）

- 时刻（America/New_York）：2026-10-25T05:33:01-04:00
- 依据：主 Agent 05:32 ET P0；Strategy 回执 sha `489978db…` MATCH；更深方案 sha `19b36b00…` MATCH
- live=false；禁 paper / live / 抬帽硬跑

## 1. 作废（已完成）

| 项 | 值 |
|---|---|
| 旧 run.ok sha | `42a163840cf4023d2ddb39471acd7368550025e7db49a1519bf68e1c91faa262` |
| 归档 | `output/strategy_hiliq/_consumed/ARCH_RUN_AUTH_STRATEGY_MONEYFLOW_STACK_DIAG_LOWMEM_V11_RUN.VOID.20261025T0533ET.ok` |
| 旁证 | `output/strategy_hiliq/_consumed/ARCH_RUN_AUTH_STRATEGY_MONEYFLOW_STACK_DIAG_LOWMEM_V11_RUN.VOID_MARKER.txt` sha `6fd37cf5285239a39bb39a244d57735ff1ffb680b141fada62e64600e43850a7` |
| 回执 | `docs/v2/STRATEGY_MONEYFLOW_STACK_DIAG_LOWMEM_V11_RECEIPT_20261025_ZH.md` sha `489978dbeb3a80421244357776903191bb327062cf51d2471ff0672bc21c7729` MATCH |
| 方案 | `docs/v2/STRATEGY_MONEYFLOW_STACK_DIAG_DEEPER_LOWMEM_PLAN_20261025_ZH.md` sha `19b36b00facb9d09b033fbdd8690c12d42a7b0f73f8a14465986549f179e12e5` MATCH |
| 原因 | VmHWM=2320.9 > rss_cap 2048；EXIT=2；out_dir 仅 VOID.json；门B/GATE_V3=null |
| 恢复目录 | `output/strategy_hiliq/_recovery/strategy/20261025T0533ET_moneyflow_stack_lowmem_v11_void/`（含 out_dir + run.log + vmhwm_monitor.log） |
| VOID.json sha | `d90a837a251ed8853e1917eca5c8b201c509d5c7df893e7ae93a9d56ff17a1b4` |

## 2. 更深路径裁定：**采纳 P0（复用 blended，跳过再读腿）**

| # | 裁定 |
|---|---|
| 脚本 | **同路径补丁** `research/strategy_moneyflow_stack_diag_v1.py`（相对 baseline `2dae9a91…`） |
| P0 行为 | run.ok 钉 `reuse_blended_path` + sha MATCH 时：**硬链或拷贝**到 out_dir；**不** `read_parquet` trunk/sat 两腿；**不**重算混合 |
| blended pin | sha `3f8a2b33a995f381ee9e7060858a2029c1a8854a31a32b48ab4842281f188103`；路径 `output/strategy_hiliq/_recovery/strategy/20261025T0502ET_moneyflow_stack_void/blended_weights_8020.parquet` |
| book-smoke | 仍 **串行 BOOK-only**（分档 600000 / 1000000；`--arms BOOK`）；subdir + gc |
| 内存帽 | 将来 run.ok **`rss_cap_mb=2048`**（**禁止**抬帽） |
| out_dir（建议） | **新** `output/strategy_hiliq/moneyflow_stack_8020_reuse_blended_20261025/` |
| decay | 仍钉 `REJECT` |
| 窗 | 避叶25 `2026-10-25T10:00:00-04:00`–`2026-10-25T10:45:00-04:00` |

**本轮不采纳 / 暂不签**：
- **P1**（单档 60 万）：待命——若 P0 DIFF+run 仍破帽再开
- **P2**（Eng 查 book-smoke）：待命——同上
- **P3** 轻量净值：默认不采纳

**禁**：抬帽硬跑；复用废签 `42a16384` 与 `68c04741`；改 CMC；改 `research/alpha_combo_marginal_v1_2.py`；本轮签 run.ok。

## 3. 签发顺序

1. **本轮**：签 **code_change .ok**（DEEPER_P0_REUSE_BLENDED）→ Strategy 交 P0 DIFF。
2. Arch 审 DIFF → 再签 **run .ok**（新 out_dir / rss_cap=2048 / pin reuse_blended / 避叶25）。
3. Strategy **在新 run.ok 前不跑**。
4. 补跑 SUSPEND 不变。

## 4. 一句话

lowmem v1.1 `42a16384` 已 VOID（VmHWM 2320.9>2048）；采纳 P0 复用 blended 跳过再读腿；帽仍 2048；先 code_change，后 run。
