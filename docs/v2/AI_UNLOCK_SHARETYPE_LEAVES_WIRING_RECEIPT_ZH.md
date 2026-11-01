# 解禁 share_type 叶接线回执（STOCK-UNLOCK-SHARETYPE / V30）

| 项 | 值 |
|---|---|
| 日期 | 2026-10-12 ET |
| PID | 2828718 |
| peak_rss_MB | 1048.8 |
| 窗 | 2024-04-01 → 2025-06-30 |
| promotion_approved | **false** |
| NAV / 回测 / GP / v27 | **未跑**（仅接线） |
| Strategy | **不交** |
| Beta | 主跑 STOCK-UNLOCK-SHARETYPE X1；本侧只交叶 |

## 叶名

- `unlock_private_place_share_20` — nonempty=0.0052; mean_names/day=31.49
- `unlock_private_place_ratio_20` — nonempty=0.0049; mean_names/day=29.94
- `unlock_strategic_share_20` — nonempty=0.0055; mean_names/day=33.61
- `unlock_incentive_share_20` — nonempty=0.0100; mean_names/day=60.67
- `unlock_private_place_frac_20` — nonempty=0.0052; mean_names/day=31.49

## available_at 规则（硬）

- available_at.normalize()+1d → searchsorted(cal, left); ann_date 18:00 Asia/Shanghai → next session open; never forward-shift
- **不可前移** available_at。

## 路径

- 模块：`research/ai_factor_unlock_sharetype_panels.py` → `build_unlock_sharetype_panels`
- 样例面板：`output/ai_factor/unlock_sharetype_leaves_v1/*.parquet`
- JSON：`output/ai_factor/unlock_sharetype_leaves_v1/wiring_receipt.json`
- 源表：`data/v2/share_float/share_float_pit.parquet`

## 其它

- 不磨 seat；不启 v27；不交 Strategy。
- 覆盖如实（解禁事件稀），勿降 θ。
