# 侧稿说明：引擎 `load_merged_panel` 窗口化（P2，不改生产）

- 目标（将来）：`quantlab/data/v2_readers.py` :: `load_merged_panel`；可选 `quantlab/platform/execution.py` :: `load_execution_panels`
- 本轮：**无** `.py` 补丁落地（避免误触生产）；只写杠杆说明
- await Arch code_change；禁抬帽；不跑

## 现状（证据）

- `load_merged_panel` L1769/L1784：`pd.read_parquet(path)` 整文件，再按 cutoff 切 D0/extend，**无** caller 的 `[start,end]` 下推。
- `load_execution_panels` L1257–1269：先拿全历史 `frame`，再 `loc[(et>=lo)&(et<=hi)]`。
- D0 panels≈1.3GB / 6026 文件；单文件均≈227KB —— 逐标的峰值通常可控，但与父进程大对象叠加时树峰破帽。

## 建议杠杆（实现级提纲）

1. API：`load_merged_panel(..., session_start=None, session_end=None)`；有界时对 parquet 使用 pyarrow `filters`（若列是 `event_time`/`trade_date`）或按年分文件只读触及年。  
2. `columns=` 白名单：OHLCV + limit_* + factor/open_status 等执行所需。  
3. 可选 `memory_map=True`（注意生命周期与多进程）。  
4. `load_execution_panels`：把 `[lo,hi]` 传入 merged 加载；循环内 `del fr; gc.collect()` 每 N 码。  
5. **不做**：抬 RSS 帽；改定价语义；默认可变 panel policy。

BOOK-only ≤2GB **不依赖**本引擎补丁作为第一刀；第一刀是 diag 侧消灭 359 万行 trunk 整表读 / reuse-blended。
