# API 读时日期过滤 + 大表按月分区方案（第四节）

| 项 | 值 |
|---|---|
| 日期 | 2026-10-12 ET |
| 范围 | `services/local_data_api` 防 OOM + 五张大表分区计划 |
| 服务重启 | **未做**；须 Leo 明确说「现在重启」后才可起 8787 |
| promotion_approved | **不动** |

## 1. 问题

以下五张表一旦按「整表 `pq.read_table` → `to_pandas`」再过滤，极易把 8787 打到内存不足：

| catalog id | 现状路径 | 约行数 | 日期列 | 类型 |
|---|---|---|---|---|
| `daily_basic_full` | `data/v2/valuation/daily_basic_full_tushare.parquet` | ~1229 万 | `trade_date` | timestamp[us] |
| `float_mktcap` | `data/v2/float_mktcap/float_mktcap_daily_tushare.parquet` | ~976 万 | `trade_date` | timestamp[us] |
| `ep_pit_daily` | `data/v2/ep/ep_pit_daily_tushare.parquet` | ~975 万 | `trade_date` | timestamp[us] |
| `margin_detail` | `data/v2/margin/margin_detail_daily_2018plus.parquet` | ~579 万 | `trade_date` | large_string YYYYMMDD |
| `share_float_pit` | `data/v2/share_float/share_float_pit.parquet` | ~645 万 | `float_date` | large_string YYYYMMDD |

旧实现（≤v1.1）：`_load_and_filter` 先整表进内存，再按 start/end 过滤 —— 这正是 OOM 根因。

## 2. 已落地的 API 改造（v1.2.0，代码已改，**进程未重启**）

文件：`services/local_data_api/app.py`、`catalog.json`。

### 2.1 读路径强制下推过滤

| 函数 | 作用 |
|---|---|
| `_scan_to_table` | 统一 query/export 入口：`pyarrow.dataset` + filter，**禁止**大表先 `to_pandas` |
| `_build_filter` | 按列类型把 `YYYYMMDD` 转成 timestamp / string / int scalar，构造 `ds.field` 表达式 |
| `_force_recent_window` | 大表/oom_risk **未给 start/end** 时，用 catalog `date_max` 往前 `force_window_days`（默认 30；解禁 120）自动开窗 |
| `_open_dataset` | 若 catalog `partitioned_path` 目录已有 hive parquet，优先读分区根 |

响应可见性：

- JSON：`filters.auto_window` / `force_window_days` / `oom_safe_read` / `scanned_rows`
- Header：`X-Auto-Window`、`X-Filter-Start`、`X-Filter-End`、`X-Used-Partitioned`、`X-Scanned-Rows`

`/head` 改为 `iter_batches` / `dataset.head`，不再整表加载。

### 2.2 catalog 标记

五张表已加：`oom_risk=true`、`require_date_filter=true`、`force_window_days`、`partitioned_path=data/v2_partitioned/<id>`。

## 3. 按月分区方案（hive）

目标布局（**新目录，不覆盖扁平源表**；分区目录键为 **`ym=YYYYMM`**，避免与文件内 `trade_date`/`float_date` 类型冲突）：

```
data/v2_partitioned/
  daily_basic_full/ym=202610/part-0.parquet
  float_mktcap/ym=YYYYMM/part-0.parquet
  ep_pit_daily/ym=YYYYMM/part-0.parquet
  margin_detail/ym=YYYYMM/part-0.parquet
  share_float_pit/ym=YYYYMM/part-0.parquet
```

### 3.1 迁移脚本

`scripts/partition_oom_tables_to_hive.py`

```bash
# 默认 dry-run：只写 output/partition_oom_plan.json
python3 scripts/partition_oom_tables_to_hive.py

# 真正写入 v2_partitioned（源表不动）
python3 scripts/partition_oom_tables_to_hive.py --apply

# 冒烟：只写某表最近 1 个月
python3 scripts/partition_oom_tables_to_hive.py --apply --only margin_detail --sample-months 1
```

- 默认 **dry-run**
- 只写 `data/v2_partitioned/...`
- 可中断；已存在月份默认跳过（`--force` 覆盖）
- dry-run 结果：`output/partition_oom_plan.json`（五表月份数已探明）

2026-10-12 冒烟：已写出 `data/v2_partitioned/margin_detail/ym=202610/`（6455 行）作样例；其余表未全量迁移（磁盘/内存/与 MF 并存）。

### 3.2 全量迁移建议时机

1. moneyflow remaining → 0，available 内存 ≥ 源表体积余量  
2. `--apply` 逐表（先 margin/share_float，再 ep/float_mktcap，最后 daily_basic_full）  
3. 验收：分区行数合计 ≈ 源 nrows；抽一月对拍  
4. Leo 同意后：**重启 8787** 使 v1.2.0 生效；API 会自动优先 `partitioned_path`

## 4. 与 Leo「第一节 / 第三节小表大多可不必另建」的关系

| 需求 | 分区+读时过滤就绪后 |
|---|---|
| 第一节 daily_basic 9/1→今小窗 | Mac 可直接 `export.parquet?start=20260901&end=...`，**不必**常驻 `windows/daily_basic_*`（现有窗表仍可留作离线缓存） |
| 第三节解禁 m30/p90 | `share_float_pit` + float_date 过滤即可；窗表变为可选加速层 |
| 两融 / EP / 流通市值 | 同理按需 export，不必为研究每次物化全表副本 |

仍建议保留极小窗物化（如 QDII 净值、5 只 ETF）——源本就不是这五张 OOM 表。

## 5. 未做 / 明确禁止（本轮）

- **未**启动或重启 uvicorn / 8787  
- **未**改 `promotion_approved`  
- **未**对源扁平 parquet 做破坏性改写  
- **未**开 sec3 缺源（质押/预告/增减持）拉数  

## 6. 验收清单（重启后）

1. `GET /health` → `version=1.2.0`，`oom_safe_read=true`  
2. `GET /datasets/daily_basic_full/query`（无 start/end）→ 自动窗 + `filters.auto_window=true`，进程 RSS 不飙到整表  
3. `export.parquet?start=20260901&end=20261012` 返回合理行数  
4. 分区全量完成后 `X-Used-Partitioned: 1`
