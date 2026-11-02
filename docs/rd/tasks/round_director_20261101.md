# 算法总监书面审核（2026-11-01）

岗位：算法总监。只读上一轮四份备忘录和当前源码。没有改那四份备忘录，没有改选股代码，没有改测试断言，没有生成行情，没有重跑密封窗，没有把 `strategy_promotion_approved` 写成 true，没有改 Mandate 门。

架构备忘录写于不含 `f391191` 的检出。当前分支 `cursor/float-mktcap-pit-5dc3`，HEAD `0fb0cbc`，历史上有 `f391191`（对齐已落地的列名，不改源表）。下面分红路径按当前文件重读。

## 1. 四份备忘录：核过的句子，以及不符的句子

### 股票池 `docs/rd/tasks/round_universe_bj_20261101.md`

核过，与当前文件一致：

- 书面不打分仍是 `docs/rd/experiments/factors.md:11`。这一行仍是「池内按代码稳定排序取 Mandate 的 30 到 60 只，权重相等。」
- `research/rd_ablation_20261101.py:115` 的 `stable_book` 在 `:121` 直接 `raise ValueError("code_order_book_retired: excludes neither bj nor a real unscored sample")`。调用点 `:201`（宽篮）和 `:220`（mid-large）还在。
- `docs/rd/experiments/universe.md:11` 只有「决策日前 60 日成交额为正、先排名、第 3001 到第 5000 名。不足 3001 只则当日不买。」`:12`、`:13` 也没有剔除北交所，也没有一条不是代码序、收到约 30–60 只的取样句。
- `docs/v2/MANDATE_UNIFIED_STOCK_ETF_20261012_ZH.md:68` 是个股侧持股约 30–60。`:69` 是流动性 U30、上市至少 120 日、剔 ST / 退市整理 / 默认北交所。
- `quantlab/smallcap/universe.py:79` 是绝对名次带 `ordered.iloc[RANK_START - 1:RANK_END]`，`:82` 只再要求成交额。这段没有 `startswith("bj.")`。
- `quantlab/universe/d1_masks.py` 全文没有 `bj.`。`:108` 只留 `stock` 与 `equity_etf`。`:586` 把剩下的 `instrument_id` 作为成员。
- `quantlab/mandate_v2.py:46` 定义 `exclude_bse_default`，`:270` 读入。全库 Python 只有这两处。

抽查范围内没有不符。`scripts/extend_2018_band.py:72`、`quantlab/broad.py:25`、`scripts/stable_book.py`、`scripts/full_pool.py` 这轮没有重开，不记成已核。

### 成本 `docs/rd/tasks/round_cost_20261101.md`

核过，与当前文件一致：

- `quantlab/platform/execution.py:343-351` 的 `strategy_v1` 写入 `impact_k`，不写入 `slippage`。`:347-349` 的字典里没有 `slippage`。
- `:312` 的类默认是 `slippage: float = 0.0`。`:308-311` 仍是佣金 `0.00025`、最低 `5.0`、印花税 `0.001` / `0.0005`。`:313` 的 `impact_k` 类默认是 `0.0`，被 `:343` 与 `:347` 写成 `1.0`。
- `research/rd_ablation_20261101.py:151` 是 `ExecConfig.strategy_v1()`，没有 overrides。
- Mandate `:70` 原文仍是「成本：佣金 2.5bp+最低 5 元；滑点 5bp；印花税历史卖出；`ExecConfig.strategy_v1`」。5bp 没有写进 `strategy_v1`。
- 组合 B 的字段还在：`docs/v2/QuantLab-MANDATE_V2.json:240` 是 `slippage_bps_one_way` = 5.0，`:235-236` 是佣金 2.5bp 与最低 5 元；`:328-330` 另有 `commission_bps` 2.5、`commission_min_cny` 5、`slippage_bps` 5。`quantlab/mandate_v2.py:349` 在缺键时把 `slippage_bps_one_way` 默认成 5.0。`quantlab/portfolio/v2_execution_costs.py:330-331` 用这个 bp 除以 10000 再乘买卖名义金额。
- 扣费行 `:764`、`:778`、`:779`、`:784`、`:796`、`:799` 与备忘录一致。`STAMP_CUT` 在 `:28`，是 `2023-08-28`。

抽查范围内没有不符。`tests/test_rd_contracts.py` 与 `tests/test_execution_costs_platform.py` 没有逐行重读。仓库 `tests/` 里没有 `strategy_v1().slippage` 或 `slippage=0.0005` 的字面量。

### ST 与退市 `docs/rd/tasks/round_st_delist_20261101.md`

核过，与当前文件一致：

- `stable_book` 在第 121 行抛 `ValueError`。
- 消融第 189–191 行只向 `instruments.parquet` 要 `instrument_id` 和 `asset_type`，并去掉 `sh.510300`。第 132 行行情列是 `event_time`、`open`、`close`、`volume`、`amount`、`turnover`。全文件没有读取 `is_st`、`delist` 或 `st_flag`。
- `quantlab/platform/delist_accounting.py:41-43` 把三个来源分别绑到 `delist_events_v1.parquet`、`stock_delisted_v2.parquet`、`stock_delisted.parquet`。`:162-163` 在文件不存在时抛 `FileNotFoundError`。消融脚本不在 `:54-61` 的 `_ALLOWED_CALLERS` 里。研究脚本若直接调用，`:87` 先抛 `StrategyLayerDelistAccess`。
- 消融第 26 行用的是 `quantlab.platform.execution.run_weight_schedule`。该函数 `:623-625` 的参数里没有 `delist_events`。
- 盘上是文件的有：`data/v2/st_flags/is_st_daily_2018_2026.parquet`、`data/v2/st_flags/st_intervals_tushare.parquet`、`data/v2/ref/stock_delisted.parquet`、`data/v2/ref/stock_delisted_v2.parquet`、`data/v2/st_events/namechange_all.parquet`、`data/v2/meta/stock_basic_incl_delisted.parquet`，以及 D0 的 `instruments.parquet`。`data/v2/delisted/delisted_is_st_daily_from2015.parquet` 与 `data/v2/ref/delist_events_v1.parquet` 不在。
- `quantlab/universe/d1_masks.py:420` 取面板行的 `is_st_at_open`，`:438` 在缺失时把 `st_flag` 写成 False，`:529` 用 `~st_flag`。消融没有调用这条掩码。

行数和 `is_st` 的 Arrow 类型这轮没有重读 schema，不把备忘录里的行数再写成我数过的，也不因此标成不符。

### 架构 `docs/rd/tasks/round_adj_20261101.md`

核过，仍成立：

- `quantlab/smallcap/panel.py:94` 仍是 `factor = column('factor').ffill().bfill()`。`:95` 仍是 `out['adj_close'] = out['close'] * factor`。bfill 那一句成立。
- `tests/test_rd_contracts.py:150` 仍是预期失败，`strict=True`，原因写着 `panel.py:94`。`:152-153` 仍读源码第 94 行并断言该行不含 `bfill`。`docs/rd/bugs/adj_factor_bfill.md` 仍写状态 open。
- 消融第 132 行只读原始行情列。`:254`、`:283`、`:330`、`:415` 的 `field_frame` 用的是 `"close"`。全文没有 `adj_close`，也没有调用 `load_corporate_action_panels`。
- `docs/rd/messages.jsonl` 里 `architect-002` 的 status 仍是 `open`，evidence 仍是 `quantlab/smallcap/panel.py:94`。

与当前源码不符：

- 备忘录写 `DEFAULT_DIVIDENDS` 在 `quantlab/data/v2_readers.py` 第 27 行，路径是 `data/v2/dividends/dividends.parquet`。当前第 29 行是 `ROOT / "data" / "v2" / "corporate_actions" / "dividend_tushare.parquet"`。第 30 行 `DEFAULT_DIVIDENDS_BY_EXDATE` 是同目录的 `dividend_by_exdate_tushare.parquet`。第 74 行 `dividend_path` 默认等于 `DEFAULT_DIVIDENDS`。
- 备忘录写 `load_dividends` 在第 574–576 行，`path is None` 时只读 `DEFAULT_DIVIDENDS`，`roots` 不参与选文件。当前函数在第 756–762 行。候选依次是 `roots.dividend_path`、`DEFAULT_DIVIDENDS_BY_EXDATE`、`DEFAULT_DIVIDENDS`，以及旧路径 `data/v2/dividends/dividends.parquet`。
- 备忘录把 `cand = dividend_path.with_name(...)` 记在 `execution.py` 第 1576 行，并由此认为先找 `data/v2/dividends/dividend_by_exdate_tushare.parquet`。当前这行在第 1580 行：`cand = Path(getattr(roots, "dividend_path", "")).with_name("dividend_by_exdate_tushare.parquet")`。默认 `dividend_path` 已在 `corporate_actions/` 下，所以 `with_name` 得到的是 `data/v2/corporate_actions/dividend_by_exdate_tushare.parquet`。
- 「分红默认路径打不开已落地表」，以及结论里「默认执行路径现在还打不开 `corporate_actions` 下已经落地的两张表」，与当前源码不符。两张表都是文件。`data/v2/dividends/dividends.parquet` 与 `data/v2/dividends/dividend_by_exdate_tushare.parquet` 不在。
- 「当前 `load_dividends` 不把 `ts_code` 转成 `instrument_id`。即便把落地文件显式传进去，第 1583 行读取 `instrument_id` 会是 `KeyError`」与当前源码不符。第 764 行先调用 `_with_instrument_id`。第 480–485 行：列里没有 `instrument_id` 且有 `ts_code` 时，在内存里加上 `instrument_id`。盘上两张表的 schema 有 `ts_code`、`cash_div`、`cash_div_tax`、`stk_div`、`ex_date`、`div_proc`，没有 `instrument_id`、`share_ratio`、`adj_factor`。列名与备忘录一致；「读出来仍没有 `instrument_id`」与第 480–485 行不符。过滤 `instrument_id` 的代码在当前第 1587 行，不在备忘录写的第 1583 行。源表没有改。

## 2. 不批准落地

不批准落地。下一张账仍然不能开跑。

缺的是 `docs/rd/experiments/universe.md` 里承接北交所、又不是代码序的那一句。第 11 行现在只有成交额名次带。Mandate 第 69 行的「默认北交所」和第 68 行的「约 30–60」没有接到这句上。`factors.md` 第 11 行的代码序已被 `stable_book` 第 121 行拒绝，不能拿来顶上。本审核不补排序公式。

成本是组合 A 还是组合 B 还没有选。组合 A 是 `ExecConfig.strategy_v1()` 无 overrides：`slippage` 为 0.0，`impact_k` 为 1.0。组合 B 是 Mandate 成本对象里的滑点 5bp，没有 `impact_k`。第 70 行把这两句并列。测试岗没有选定，总监也不选定。

ST 与退市表在盘上，消融脚本没读。日表、区间表、`stock_delisted.parquet`、`stock_delisted_v2.parquet` 都是文件。`research/rd_ablation_20261101.py` 不读这些列，`run_weight_schedule` 也不接收退市事件。

走 `adj_close` 仍会碰到 bfill。`quantlab/smallcap/panel.py:94` 先 `ffill().bfill()`，第 95 行乘进 `adj_close`。

`strategy_promotion_approved` 保持 false。不改 Mandate 门。不重跑密封窗。

## 3. 原始价时，分红默认路径能不能打开

下一张账若走原始价，分红按当前源码默认路径能打开已落地表。只记读到的行：

- `quantlab/data/v2_readers.py:29`：`DEFAULT_DIVIDENDS = ROOT / "data" / "v2" / "corporate_actions" / "dividend_tushare.parquet"`
- `:30`：`DEFAULT_DIVIDENDS_BY_EXDATE = ROOT / "data" / "v2" / "corporate_actions" / "dividend_by_exdate_tushare.parquet"`
- `:74`：`dividend_path: Path = DEFAULT_DIVIDENDS`
- `:756-764`：传入路径是文件就用它；否则在 `dividend_path`、除息表、`DEFAULT_DIVIDENDS` 和旧的 `data/v2/dividends/dividends.parquet` 里取第一个存在的文件，再 `_require_file`，再 `_with_instrument_id`
- `quantlab/platform/execution.py:1579-1582`：缺省时用 `default_v2_roots()`。`:1580` 对 `dividend_path` 做 `with_name("dividend_by_exdate_tushare.parquet")`。该路径是文件时，`:1582` 把它交给 `load_dividends`

`data/v2/corporate_actions/dividend_tushare.parquet` 与 `dividend_by_exdate_tushare.parquet` 都是文件。Parquet 元数据能打开：前者 268204 行，后者 15540 行，列名见第 1 节。因此 `:1580` 的 `cand` 指向已落地的除息表。

消融脚本现在仍不调用 `load_corporate_action_panels`。这一节只说明默认路径能打开这两张表，不表示下一张账已经接上分红。

## 4. 不批准的改动

不批准改 `quantlab/strategy/experts.py`、宽篮公式或构造器默认帽。不批准重跑已作废的代码序账（记录里的 81.66%）。该数字不写成收益，也不写成可引用的年化。不改选股代码，不改测试断言，不生成行情。

## 5. architect-002

`architect-002` 保持 open。证据仍是 `quantlab/smallcap/panel.py:94` 的 `ffill().bfill()`。预期失败样例不改成通过。
