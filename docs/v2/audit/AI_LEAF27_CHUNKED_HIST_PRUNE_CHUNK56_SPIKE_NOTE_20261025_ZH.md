# 叶27 hist-prune ABORT · chunk5→chunk6 mktcap 尖峰短笔记（交主）

- **角色**：QuantLab AI
- **时刻**：2026-10-25T17:09:59-04:00（America/New_York；墙钟 2026-10-25 17:09 ET）
- **对照**：回执 sha8 **`d8be85cb`**；日志 `…histprune/_logs/run_20261025_165654.log`；VOID 回执 **`fd159322`**（`.ok` `2be59acd`）；ndays40 对照 `03064d50`
- **性质**：**诊断笔记 only** · **非签票** · **非 DRAFT COVER/CMD** · **禁抬帽** · **禁自开跑** · live=false · ≠X2

## 一句话

破帽点仍是 **`load_mktcap_chunk` 瞬时尖峰叠在「块末 clear+gc 不降 RSS」的跨块基线**上；`hist_prune_r1` 已执行但 **RSS 零回落**，与无 prune 的 ndays40（1514@chunk6）同阶段、同量级（本票 **1518**）。

## chunk5→chunk6 实测路径（hist-prune）

| 阶段 | rss（MB） | Δ |
|---|---:|---:|
| chunk[5] members_loaded | 1394 | — |
| chunk[5] capadv | 1431 | +37 |
| chunk[5] mktcap | 1485 | +54 |
| chunk[5] **hist_pruned+freed** | **1485** | **0**（`ret_hist_n=3875` `eps_hist_n=3124`） |
| chunk[6] members_loaded | 1485 | 0 |
| chunk[6] capadv | 1485 | 0 |
| chunk[6] **mktcap → ABORT** | **1518** | **+33**（limit 1500） |

对照 ndays40（无 hist_prune）：chunk5 freed **1479** → chunk6 mktcap ABORT **1514**（+35）。结构同构。

## 何对象「未释放」（按证据分层）

### A. 跨块逻辑持有（clear 范围外 · 基线主力嫌疑）

| 对象 | 证据 |
|---|---|
| `ret_hist` / `eps_hist` | 块末 prune+删空 deque 后仍 **3875 / 3124** 键；窗口内存活名 deque 保留（因子钉 BETA/IVOL 不可砍） |
| `lim_cache` | 日循环 `limit_hit(..., lim_cache)` 跨块累积；块末**未**清 |
| `mkt_hist` | 市场收益 deque 跨块 append；块末未清 |
| `a_date/a_inst/a_alpha/…` | x2 窗内 α 行列表跨块增长；块末未清 |
| `swm` / `r_mkt` / `mask` 路径句柄 | 进程级常驻（非块地图） |

### B. 块内已 `clear()+del+gc` 但 RSS 不降（假释放 / 分配器滞留）

块末对 `members/suspended/mktcap/cap` 做 `clear→del→gc.collect()`，日志阶 `hist_pruned+freed` **与 prune 前同值**（chunk0..5 皆 Δ=0）。  
含义：引用上已丢，但 **pymalloc/pyarrow 页未归还 OS**，基线锁在 ~1485，给下一块 mktcap 只留 ~15MB 余量。

### C. 破帽瞬时对象（chunk6 的 +33MB）

`load_mktcap_by_session(dates_needed≈41日)`：

1. 打开 **全历史** `float_mktcap_daily_from2015_*.parquet`，**逐 row-group** `read_row_group→to_pandas` 再按 `want` 过滤；
2. 并行 `acc_c/acc_v` 列表累积后压成 `DayFloatMap`；
3. 测峰在 `chunk6_mktcap` 软门——即 **装载瞬时**，不是日循环中段。

（附带）`load_capadv_target_weight` 仍是 **整文件 `pd.read_parquet` 再 slice**；本跳 chunk6 未再抬 RSS（分配器复用），但是早期块（0/1）的主要抬升源之一。

## 非结论（本笔记不做）

- **不**申请抬 `rss_limit`
- **不**自拟 COVER/CMD/HAND / **不**申 `.ok`
- **不**静默改 chunk-mode / ndays
- 工程候选票由 **Arch** 出、**主**合并；AI 仅提供上列结构事实

## 给合并用的结构标签（非票）

1. `BASELINE_NO_RSS_DROP_AFTER_CHUNK_FREE` — clear+gc 不降 RSS  
2. `CROSS_CHUNK_HIST_LIM_ALPHA_HOLD` — ret/eps/lim/a_* 跨块持有  
3. `MKTCAP_FULLSCAN_TRANSIENT_SPIKE` — 全表 RG 扫描式 mktcap 装载尖峰（破帽点）  
4. `HIST_PRUNE_R1_NO_PEAK_RELIEF` — prune 见日志、峰无改善（1514→1518）

live=false。
