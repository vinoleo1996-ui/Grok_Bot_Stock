# Intel：sw_pit 过期检查 + 申万成分按时点取（只出 diff，待 Arch 审）
- 时间：2026-10-18 05:1x ET。依据：主 Agent 10-18 05:06 ET 裁定（Arch 转达）。正式 research/intel 文件**未改**；改动只在临时副本 /tmp/qlrev 上做过并测试。
- diff：`_review/intel_sw_pit_freshness_20261018.diff`（sha256 见 `.diff.sha256`）。Arch 签 .ok 后才落地。live=false。

## 1. 读取点核对（rg research/intel，sw_pit|cyq|tier3）
| 文件:行 | 读的表 | 原取法 |
|---|---|---|
| intel_common.py:172（industry_stocks） | sw_pit l1 | `out_date.isna()`，即表内最新成分 |
| intel_event_study.py:39（使用在 :52） | sw_pit l1 | 交易日 d 用 `in_date <= d & (out_date 空 or out_date > d)` |
| intel_c1_gap_split.py:25（使用在 :35） | sw_pit l1 | 同上 |
- cyq、tier3：research/intel 下**没有读取点**（rg 为空）。函数里没有登记这两张表，没有编造路径。

## 2. sw_pit manifest 的实际字段（data/v2/sw_pit/manifest.json）
- 顶层：`l1`、`l2`、`source`、`available_at`（"in_date 18:00 Asia/Shanghai (Tushare 未提供公告时间, 近似)"）、`note`、`promotion_approved`、`built`（"2026-10-14T04:00:19.995930"，没带时区）、`sha256`、`sha256_at`。
- `l1` / `l2` 子项：`path`、`rows`、`instruments`、`n_codes`、`in_date_range`（l1 为 ["1984-05-09","2026-09-24"]）、`current_members`。
- 表的列：instrument_id、l1_code、ts_code、name、l1_name、in_date、out_date、is_new、available_at、source、promotion_approved。
- 没有"最后一次成功拉取时间"字段，所以 built 是唯一能代表数据新旧的时刻。
- 另外：`data/v2/_quarantine/sw_pit_INCOMPLETE_20261018/` 存在（10-16 那次 sw 刷新没完成就被终止），INCOMPLETE.md 记录 classify 两表的 sha 与 manifest 不一致，且这个不一致在那次运行之前就已存在。

## 3. 改动点
1. **intel_common.py**
   - 新增 `FRESHNESS_TABLES` 登记表（目前只登记 sw_pit）和 `STALE_LAG_TRADING_DAYS = 3`。
   - 新增 `check_table_freshness(table, asof)`，返回 {table, max_date, built, covered_through, lag_days, status, disclosure}：
     - max_date 取 manifest 的 `in_date_range[1]`，没有就读 parquet 的实际最大值。它只代表"最后一次成分变动"，成分表本来就稀疏，所以不单独用它判过期。
     - covered_through 由 built 推算：18:00 之前构建，就算覆盖到前一个交易日。
     - lag_days 是 (covered_through, asof 当日或之前最近的交易日] 内的交易日数。交易日以 data/v2/tushare_raw/daily 的文件名为准。
     - 有隔离目录（quarantine）时写进 disclosure。
   - 新增 `require_fresh()`：过期时默认 SystemExit，`allow_stale=True` 才放行。
   - 新增 `sw_members_asof(sw, d)`：交易日 d 只用 `in_date < d` 的成分（available_at = in_date 18:00，收盘后才可用），出表的成员到 `out_date >= d` 为止。
   - `industry_stocks()` 先跑过期检查，结果存入 `SW_FRESHNESS`；成分从"最新"改为按今天的上海日期取（18:00 以后含当天的变动）。
2. **intel_run.py**：过期时**不停跑**。`source_status.tables.sw_pit` 写入检查结果，md 的"新闻源状态"下方加一行"数据表新鲜度"；过期时注明"行业归属可能未反映最新成分变动，结论照常输出"。
3. **intel_event_study.py、intel_c1_gap_split.py**：
   - 新增 `--allow-stale` 参数。默认在过期时停跑；加参数放行时，检查结果写进回执（`event_study_hitrate.json`、`c1_gap_split_meta.json` 的 `sw_pit_freshness` 字段）。
   - 成分改用 `sw_members_asof`。
4. 新增测试 `test_sw_freshness.py`（10 条）。

## 4. 阈值建议（待 Arch 定）
- **建议：lag_days ≥ 3 个交易日就判 stale。**
- 理由：
  - 正常情况是每晚拉取，lag 为 0 到 1。
  - 漏 1 到 2 次可能只是中继（relay）偶发的 5xx，属于容忍范围。
  - 连续 3 个交易日没成功，相当于本周 10-14 到 10-16 三次都失败的情形，应当显式披露或停跑。
  - 申万成分通常在月度或季度调整，3 个交易日内漏掉一次调整的概率较低，但仍应提示。
- 也可以选 5（一周）。不建议用 max_date 判过期，因为成分表本来就稀疏，最后一次变动 09-24 不代表数据旧。
- **按建议值，sw_pit 现在是 stale**：built 是 10-14 04:00，覆盖到 10-13，asof 10-18 时最近交易日是 10-16，lag 3，并且存在 quarantine 目录。若阈值取 5 则为 ok。

## 5. 行业归属的时点
- intel_common 原来用的是表内最新成分（out_date 为空）。对实时预警来说，这和按今天取的结果一致，实测 10-18 差异为 0。改成显式按时点取，是为了以后表中出现未来日期的变动时也不会提前使用。
- 两个事件研究原本已经按日期取，但用的是 `in_date <= d`。成分在 in_date 18:00 才可用，所以 d 当天的收益会用到收盘后才公开的成分，存在 1 天的前视。改为 `in_date < d`，出表一侧相应改为 `out_date >= d`。
- 对现有输出的影响：X2 共 574 个交易日，其中 132 天的（股票, 行业）集合有差异，合计 738 对，涉及 501 只股票。这是在 mid_large 过滤**之前**的统计，主要来自新上市股票的首日（is_new 的 in_date 就是上市日）。mid_large 池一般不含上市首日的股票，预计对行业等权收益影响很小，但需要落地后重跑才能确认。我没有看任何收益数字。

## 6. 对现有输出的影响
- ALERTS：当前判 stale，source_status 和 md 会多一行披露，行业分数和个股不变（as-of 和最新成分差异为 0）。
- event_study_hitrate.json、c1_gap_split：落地后，不加 `--allow-stale` 会停跑。加参数重跑后，结果可能因上市首日的口径变化有微小差异。intel_run 的历史命中率降级依赖 event_study_hitrate.json；在重跑之前，沿用旧文件。

## 7. 测试计划与结果（临时副本 /tmp/qlrev，data 和 output 为只读软链）
- 分类器 29/29、merge 11/11、新增 freshness 10/10 全部通过：
  - 字段齐全；max_date = 09-24；10-18 判 stale，10-15 判 ok；
  - 过期默认停跑，`--allow-stale` 放行；
  - 变动当天不可用、次日生效；
  - 两个研究脚本不加参数时停跑。
- intel_run 用 `--out-dir /tmp/qlrev_dry` 做了 dry-run，RSS 209MB；JSON 和 md 都有 sw_pit stale 的披露。
- 落地后：在正式目录再跑一遍三组测试，并做一次 intel_run preopen 加 alert-ingest。是否带 `--allow-stale` 重跑 event_study，由主 Agent 决定（属于满窗任务，需先用 ps 确认没有其他重任务在跑）。
