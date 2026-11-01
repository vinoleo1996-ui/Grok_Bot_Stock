# AI GP 新叶启动回执（v28 friction）

- **时间：** 2026-10-12 11:24 EDT
- **Leo 确认卡：** 「启动降换手+开GP」
- **promotion_approved：** false；**不晋级**；**不交 Strategy**；禁 v27 同构；peak 目标 ≤2GB

## 1) 启动信息

| 项 | 值 |
|---|---|
| version | `v28_newleaf_friction` |
| PID | **3155338**（alive=yes） |
| 脚本 | `research/ai_factor_gp_reopen_hardgate_v28_newleaf_friction.py` |
| 输出目录 | `output/ai_factor/gp_reopen_hardgate_v28_newleaf_friction/` |
| 运行日志 | `output/ai_factor/gp_reopen_hardgate_v28_newleaf_friction_run.log` |
| pid 文件 | `output/ai_factor/gp_reopen_hardgate_v28_newleaf_friction.pid` |
| MEM_CAP_MB | **2000**（SELF_STOP sticky>2100） |
| MAX_EVAL / POP / GEN | 120 / 12 / 10 |
| SEED | 20261128 |
| WINDOW | gp_reopen_hardgate_v28_newleaf_friction_20240603_explore |
| 探索窗 | LOOKBACK 2024-04-01 → PANEL_END 2025-06-30；explore from 2024-06-03 |

## 2) 机制正交（相对 v26/v27）

| 维 | 本批 |
|---|---|
| **主搜叶** | unlock_resid · lu_*/ld_* · etf_share_chg_major/theme · **ind_etf_share_flow** · ann_earn/buyback · dt_x_lu_*（有限交叉） |
| **禁** | v27 **dt_seat** 同构；raw dt_net/dt_flag；rz*×ind_rel 模板；overnight*/fsr/ann_insider/idx_w*；教科书动量/价值 primary 种子；CB/金 |
| **相对接管盘点** | 已读 `output/ai_factor/GP_TAKEOVER_BY_QUANTLAB_AI_ZH.md`；本批 **新开搜**（前批仅盘点未开） |
| **骨架** | 自 v26 TrackA 派生并改 SEARCH/FORCED/UNPAUSE share-flow |

## 3) 状态（落盘时）

- 进程 alive=yes；RSS≈1199640 KB
- 启动后已过 L1b 面板加载；post-load peak 曾见 ~1904MB（贴 2GB 上限，靠 MEM_CAP=2000 + sticky 自停）
- GATE 过程产物写 `output/ai_factor/gp_reopen_hardgate_v28_newleaf_friction/`；完成后另补 done/summary（本回执=**启动**）
- **不晋级**；**不交 Strategy**；不扩 ACTIVE

## 4) 并行主线

降换手权重已落盘，见 `docs/v2/AI_G1G5_LOW_TURNOVER_RECEIPT_ZH.md`。
