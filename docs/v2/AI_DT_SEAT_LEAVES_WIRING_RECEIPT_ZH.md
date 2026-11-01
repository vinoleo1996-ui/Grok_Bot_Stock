# 龙虎席位叶接线回执（TrackA）

| 项 | 值 |
|---|---|
| 日期 | 2026-10-12 ET |
| PID | 2794244 |
| peak_rss_MB | 1584.7 |
| 窗 | 2024-04-01 → 2025-06-30 |
| promotion_approved | **false** |
| v27 GP / SEARCH | **未启动**（开关关） |

## 叶名

- `dt_inst_net_5` — nonempty=0.0205; mean_names/day=124.35
- `dt_inst_net_10` — nonempty=0.0362; mean_names/day=219.96
- `dt_nb_channel_net_5` — nonempty=0.0114; mean_names/day=68.90
- `dt_nb_channel_net_10` — nonempty=0.0199; mean_names/day=121.01
- `dt_retail_hot_net_5` — nonempty=0.0376; mean_names/day=227.94
- `dt_retail_hot_net_10` — nonempty=0.0629; mean_names/day=381.97
- `dt_inst_breadth` — nonempty=0.0031; mean_names/day=18.58
- `dt_inst_breadth_5` — nonempty=0.0129; mean_names/day=78.23

## available_at 规则（硬）

- available_at_alpha_conservative.normalize()+1d → searchsorted(cal, left); ≈T+1 15:00 SH → trade T+2 open; never forward-shift
- **不可前移** available_at。

## 路径

- 模块：`research/ai_factor_dt_seat_panels.py` → `build_dragon_seat_panels`
- 样例面板：`output/ai_factor/dt_seat_leaves_v1/*.parquet`
- JSON：`output/ai_factor/dt_seat_leaves_v1/wiring_receipt.json`

## 其它

- hk_hold：**条件接线**（日频截断~2024-06/08）；**未**拉全量进工厂。
- hsgt_top10：**BLOCKED**（等 Data 续期）。
- 可进下一轮 SEARCH 的叶名见 receipt `ready_for_next_search_leaves`；**本轮不跑 SEARCH**。
- 不交 Strategy。
