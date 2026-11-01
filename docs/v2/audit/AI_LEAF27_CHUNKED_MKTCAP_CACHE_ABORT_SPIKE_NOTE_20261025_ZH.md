# 叶27 Gate A mktcap_cache ABORT · 短笔记（交主对照下一票）

- **角色**：QuantLab AI
- **时刻**：2026-10-25T20:47:00-04:00（America/New_York；墙钟 2026-10-25 20:47 ET）
- **对照**：RUN_RECEIPT sha8 **`f0f94c9e`**；ET_TS=`20261025_204028`；日志 `…mktcap_cache/_logs/run_20261025_204028.log`；VOID **`e107383f`**（Arch 回执 `ff0394d0`；QUIET lift）；脚本 **`27aae6db`**；prev 尖峰笔记 **`dd193511`** / Arch 闸 A 草案 **`a2307c8b`**
- **性质**：**诊断笔记 only** · **非 COVER/CMD/HAND** · **禁改脚本** · **禁申 `.ok`** · **禁抬帽** · **禁自开跑** · live=false · ≠X2

## 一句话

Gate A **已生效**（miss-only + pyarrow `trade_date in […]`，不再 12-RG 全表重扫），但块末 `drop_before` 把跨块 store 压到 **`mktcap_cache_days=2`** → 下一块 **hit≈1 / miss≈40**，仍要装 ~40 日新表；叠在 **HWM 不回落** 的基线上，chunk6 只需 **+10MB**（1497→1507）就破 1500。峰相对 hist-prune 1518 仅降约 **11MB**，**不够过帽**。

## 实测 ladder（摘自 `f0f94c9e`）

| chunk | mktcap 后 rss | hist_pruned rss | hit / miss / load_n | cache_days@prune |
|---|---:|---:|---|---|
| 0 | 883 | 883 | 0 / 40 / 40 | 2 |
| 1 | 1286 | 1286 | 1 / 40 / 40 | 2 |
| 2 | 1333 | 1333 | 1 / 40 / 40 | 2 |
| 3 | 1381 | 1381 | 1 / 40 / 40 | 2 |
| 4 | 1425 | 1425 | 1 / 40 / 40 | 2 |
| 5 | 1497 | **1497**（Δ=0） | 1 / 40 / 40 | 2 |
| 6 | **ABORT 1507** | — | （members/capadv 仍 1497） | — |

破帽：`ABORT_RSS_OVER_LIMIT stage=chunk6_mktcap rss=1507MB limit=1500`。sampler peak=`898968`KB（未先杀进程）。

## 为何 cache hit≈1（不是实现 bug）

1. **Gate A 故意保留**跨块 `DayFloatMap`（块末 **不** `mktcap.clear()`）。
2. 日循环 **`drop_before`（T-1 语义不变）** 在块内持续丢掉过期日；块末日志固定 **`mktcap_cache_days=2`**。
3. 下一块 `want`≈该块 40 个 `trade_date`；与残留 2 日的交集通常只有 **边界 1 日** → 日志 **hit=1 miss=40 load_n=40**，装完后 `days=42`（2 残留 + 40 新，或等价边界算术）。
4. 因此「跨块缓存」**避免的是全表 RG 扫描**，**不是**「40 日 miss 的 pandas 物化」。冷启动后几乎每块仍 `pq.read_table(filters=40日) → to_pandas → put_day×40`。

## 为何 HWM 不回落

与 `dd193511` 同构，Gate A 下更明显：

| 层 | 现象 |
|---|---|
| A. 逻辑持有 | `ret_hist`/`eps_hist`（prune 后仍数千键）、`lim_cache`、`mkt_hist`、α 行列表跨块增长；**另** `mktcap` store 按设计跨块保留（虽被 drop 到 2 日） |
| B. 假释放 | 块末 `members/suspended/cap.clear()+gc` 后，`hist_pruned+freed` **与 prune 前同值**（chunk0..5 皆 Δ=0）→ pymalloc/pyarrow 页未还 OS |
| C. 基线锁死 | chunk5 末已 **1497**/1500，余量仅 **3MB**；任何下一块装载尖峰都会破帽 |

## 为何 chunk6 只 +10MB 就破帽

- chunk6：`members_loaded=1497`、`capadv=1497`（分配器复用，Δ≈0）→ 尖峰仍落在 **`chunk6_mktcap`**。
- 该阶仍执行 miss≈40 的 filter 读 + `to_pandas` + 按日 `put_day`；瞬时 +**10MB**（1497→1507）越过软门。
- 对照：hist-prune 全表扫 +33MB@chunk6（1485→1518）；Gate A 尖峰幅度变小，但 **起点更高/余量更窄**，结果同为 ABORT。

## 给 Arch/主合并用的结构标签（非票）

1. `CACHE_HIT_BOUND_BY_DROP_BEFORE` — hit≈1 因 T-1 drop 只留 ~2 日，非计数错误  
2. `MISS40_FILTER_STILL_MATERIALIZES` — miss-only filters 仍每块物化 ~40 日  
3. `BASELINE_NO_RSS_DROP_AFTER_CHUNK_FREE` — clear+gc 不降 RSS（续）  
4. `GATE_A_PEAK_RELIEF_INSUFFICIENT` — 1518→1507，仍破 1500  
5. `CHUNK6_PLUS10_OVER_3MB_SLACK` — 余量 3MB vs 装载 +10MB

## 非结论（本笔记不做）

- **不**申请抬 `rss_limit`
- **不**写 COVER/CMD/HAND、**不**改脚本、**不**申 `.ok`、**不**自开跑
- **不**静默改 chunk-mode / ndays
- 下一工程票由 **Arch 草案 + 主闸**；AI 停等主令

live=false。
