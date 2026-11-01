# 日线降级备用方案 r3：东财 / 腾讯公开日线 —— 仅作影子披露轨（SHADOW），不喂纸面（仅方案，待 Arch 复核）

- 作者：QuantLab Data；起草：2026-10-18 ET；状态：DRAFT r3。没有写代码，没有运行，没有联网，没有读 parquet，没有 import 项目代码
- 取代：r2 `DATA_DAILY_FALLBACK_PUBLIC_SOURCE_PLAN_ZH_r2.md`（sha256 3985730628e3c3d86678e817cfafc1b4f43eabf32da172c344dc74402a94b174）和 r1 `DATA_DAILY_FALLBACK_PUBLIC_SOURCE_PLAN_ZH.md`（92ceae2dd4122ed80435f7bcae38616866acf7816c9638ec8f07f87c6de1251c）。两份都冻结，没有改动
- 依据：主 Agent 2026-10-18 07:07 ET 裁定 ②③④；Arch 对 r1 的审阅；Arch 对 r2 的审阅 `docs/v2/ARCH_DATA_DAILY_FALLBACK_PLAN_REVIEW_ZH.md`（sha256 5072ec5c4f9ffaec3930aaed2896ef4b2b66b96e652a597b45e0d9504e6872c6，结论是有条件通过）
- 起草方式：只用带显式路径的 rg 和 Read 读 .py/.md 源码；行号已在 2026-10-18 约 09:5x ET 用 rg 复核。标「据 Arch」的行号是沿用 Arch 的核对，本轮没有逐行复核
- promotion_approved=false；live=false；strategy_promotion=false

## 0. 核心原则

公开源数据**永远不进入**纸面的持仓、NAV、信号、ledger，也不进入任何 Tushare 表或 asof 目录（包括回退目录）。选项 B 只是影子披露轨：10-19 纸面要么按 A 顺延，要么按 C（需 Leo 当面同意）拿到 Tushare 数据正常跑。B 只产出对照和披露材料。

## 1. 触发条件与升级路径（Data 不做选择）

1. 中转 `https://pcd.mobcvb.cn/tushare/pro` 不通。按裁定 ②，每小时做一次只读小接口探测，持续到 10-19 14:30 ET；叶 eval 在跑时不探测。证据存在 `10-19-14-30` 目录。
2. 如果 10-19 14:30 ET 中转仍不通，Data 报主 Agent，由主 Agent 把下列选项带给 Leo，**Leo 决定**：
   - **A**：10-19 纸面顺延一天。
   - **B**：影子披露轨（本方案）。纸面状态与 A 相同；B 可以和 A 或 C 并行。
   - **C**：Mac 代理（Leo 的电脑，需 Leo 当面同意）。纸面正常走 Tushare。
3. Data 不默认任何选项。没有收到主 Agent 书面转达的「Leo 选 B」之前，不拉任何公开源数据。如果中转在拉取前恢复，就放弃本方案，走正常 nightly。
4. ET 10-19 16:40–18:40 不运行。17:40 ET 前 data_freshness 要达到 ok，这只能由 Tushare 数据满足，B 不能让 freshness 变 ok。

## 2. 为什么 B 只能是影子轨，以及隔离边界

### 2.1 不能喂纸面（r1 P1-a）

- 冻结的纸面代码（capacity_adv、B4、S6）只读 Tushare 衍生表，没有读取影子路径的入口。要让纸面读到公开源，只能改主线代码或者写 Tushare 表，两者都被禁止。r1 的读取端参数（`--data-source fallback:`、`QL_DAILY_FALLBACK`）和「纸面启用 fallback 的 .ok」在 r2 已作废，r3 维持作废。

### 2.2 回退目录入口（r2 审阅 P2-1）

纸面链上确实存在一个回退入口，必须明确隔离：
- `quantlab/data/v2_readers.py` L90 定义 `DEFAULT_ASOF_EXTEND_FALLBACK_DIR = data/v2/asof_extend_202610`；L149 是 `asof_extend_fallback_dir`。
- `load_merged_panel`：某只股票的 tushare 面板不存在时，L1779 会**逐只回退**读取 `asof_extend_202610/panels/<iid>.parquet`，L1781 记下 `extend_panel_fallback=asof_extend_202610`（据 Arch，L1778–1782 一段）。
- 日历：L1678 先找 tushare 目录的 calendar.parquet，L1680 回退到 `asof_extend_202610/calendar.parquet`。
- manifest：L1625 也会读回退目录的 manifest.json。
- 这个目录同时也是东财增强脚本的写入目标：`scripts/enrich_asof_extend_em_seq.py` L12、L15（PANELS、EXT）、L91（写面板）、L135（enrich_manifest.json），并写 `data/v2/float_mktcap`（L13、L120–131）；`scripts/enrich_asof_extend_em.py` L5、L23、L150、L190（st_codes.txt）、L255–292。

因此，影子脚本的写入黑名单（任何一项被写即视为违规，运行中止并上报）：
1. `data/v2/asof_extend_202610/`（panels、calendar.parquet、manifest.json、enrich_manifest.json、st_codes.txt，以及其他任何文件）
2. `data/v2/asof_extend_tushare_202610/`
3. `data/v2/float_mktcap/`
4. `data/v2/acquire_status` 下或其他位置的 `data_freshness_status.json`，以及 `output/daily_update_status.json`
5. 任何 Tushare 表（data/v2/bars、adj、valuation、index、etf、cb、futures、tushare_raw、corporate_actions）
6. `data/v2/events/`（见 §3.4）

禁止调用：`scripts/enrich_asof_extend_em.py`、`scripts/enrich_asof_extend_em_seq.py`，以及任何 `enrich_asof_extend_em*` 脚本；也不 import 它们的函数。

写入白名单只有 `data/v2/_shadow_public/20261019/`。

运行回执必须给出黑名单第 1、2、3 项目录在运行前和运行后的 sha 清单（逐文件 path、size、mtime、sha256，按路径排序后再给一个汇总 sha），并证明两次完全一致。这一份清单是 run .ok 的条件（§11）。计算清单属于读数据文件，只能在 run .ok 允许的运行里做，不在起草阶段做。

## 3. 纸面实际读取的表与列（只读源码核对）

### 3.1 读取链路

| 环节 | 文件:行 | 读取内容 |
|---|---|---|
| 纸面配置和权重 | `quantlab/portfolio/b4_paper.py:24-25` | 冻结权重 `output/small_aum_concentration/v2/B_B4_50_25_25_topN_{60w,100w}.parquet` |
| B4 事件腿 | `b4_paper.py:35-36` | `output/ai_factory/g1g5_earnings_event_*_20261014_005430.parquet`、`g1g5_insider_increase_*_20261014_011841.parquet` |
| S6 | `quantlab/portfolio/paper_track.py:9-12` | `output/strategy_wf_combo/weights_S6_{60w,100w}.parquet`；事件腿 earnings_event、equity_incentive |
| 书本引擎 | `b4_paper.py:94`（`book_smoke.run`）、`:108`（`v2_multisleeve_book`） | 书本引擎是 `quantlab/portfolio/book_smoke.py` 调用 `v2_multisleeve_book.py`，不是 r2 写的 scripts_eng。scripts_eng 只在 monitor 里读输出文件（据 Arch） |
| 个股行情 | `v2_multisleeve_book.py:494-495` 调 `quantlab/platform/execution.py` 的 `load_execution_panels` | 合并 D0、`asof_extend_tushare_202610`，以及逐只回退的 `asof_extend_202610`（§2.2） |
| ETF | `v2_multisleeve_book.py:76` | `data/v2/etf/etf_daily_adj.parquet`（close_hfq、amount） |
| 申万行业 ETF 映射 | `v2_multisleeve_book.py:67` | `data/v2/etf/sw_l1_etf_map_pit_daily.parquet`（with_ind_etf 时） |
| 可转债 | `v2_multisleeve_book.py:82,86` | `data/v2/cb/cb_daily.parquet`、`data/v2/cb/raw/cb_basic_raw.parquet`（with_cb 时） |
| 股指期货 | `v2_multisleeve_book.py:93,98` | `load_index_futures_panels(("IC",))`；`data/v2/futures/raw/index_daily.parquet` |
| 哈希登记 | `v2_multisleeve_book.py:40-43,676` | HASH_FILES：etf_daily_adj、cb_daily、cb_basic_raw、cb_share_raw、fut_basic、futures index_daily 等 |
| 基准 | `quantlab/platform/strategy_feed.py:558`；`research/capacity_adv_paper_extend.py:37,65,71,123` | `data/v2/etf_510300` 面板；`_load_benchmark_closes("510300")`（取自 etf_daily_adj） |
| 分红和送转 | `execution.py:1568-1600`；`v2_readers.py:95` | `data/v2/corporate_actions/dividend_tushare.parquet`、`dividend_by_exdate_tushare.parquet`（L1576）；税前 cash_div_tax、stk_div |
| ETF 分红 | `execution.py:1510` | `data/v2/etf/raw/fund_div.parquet` |
| 退市（SD1） | `quantlab/platform/execution_sd1.py:315,519`；`quantlab/platform/delist_accounting.py:44` | `data/v2/ref/delist_consideration.parquet`；`data/v2/st_events/namechange_all.parquet`；halt_extra（suspend_d 的 S 记录） |
| 可交易性 | `quantlab/platform/tradability.py:27,51` | resume_announced（suspend_d 的 R 记录） |

### 3.2 延长腿权重（extend）步骤额外读取的表

| 读取内容 | 文件:行 |
|---|---|
| `data/v2/tushare_raw/trade_cal.parquet` | `research/capacity_adv_paper_extend.py:75` |
| D1 估值 | `capacity_adv_paper_extend.py:84-85`（据 Arch） |
| `output/daily_update_status.json`（mid_large_universe.last_date） | `capacity_adv_paper_extend.py:44,137` |
| `data/v2/universe/mid_large_members_pit.parquet` | `capacity_adv_paper_extend.py:139-141` |
| X2 拼接面板：D0 加 `asof_extend_tushare_202610/panels` | `research/g1g5_x2_panel_stitch.py:1,16` |
| 510300 基准收盘价 | `capacity_adv_paper_extend.py:65,71,123` |
| events（见 §3.4） | `research/b4_paper_extend.py:160-178` |

### 3.3 asof 面板的列与来源（P3-1、P3-2 更正）

两个目录、两个写入者，要分开写：

| 目录 | 写入者 | 读取顺序 |
|---|---|---|
| `data/v2/asof_extend_tushare_202610/panels`（主） | `scripts/acquire/tier1_materialize.py` L114–115（追加新交易日），manifest 在 L152；`eng_daily_panels.py` 的 asof_ts 步骤（L5、L117）只做校验和刷新 manifest | 默认 |
| `data/v2/asof_extend_202610/panels`（回退） | `scripts/acquire/eng_daily_panels.py` 的 asof_em 步骤（docstring L4，代码 L64–66，行写入 L94–98）；也被 `enrich_asof_extend_em*.py` 写 | 主目录缺某只股票时逐只回退（§2.2） |

| 面板列 | 主目录（tier1_materialize） | 回退目录（eng_daily_panels asof_em） | 纸面使用处 |
|---|---|---|---|
| open/high/low/close | daily（元） | daily（元），L94 | execution.py:1226 |
| volume | daily.vol（手）×100 = 股，L40 | `volume=float(r.vol)`，单位是**手**，`volume_unit=lot_100sh`，另有 `volume_shares=vol×100`（L94、L98） | execution.py:1271-1294：先用 volume_shares，再用 volume_unit，最后才按比值推断 |
| amount | daily.amount（千元）×1000 = 元，L41 | ×1000 = 元，L94 | U30、参与率 |
| limit_up / limit_down | stk_limit up_limit/down_limit，L53–61 | stk_limit，L76、L96 | execution.py:753-755；v2_lean_panels.py:148,163 |
| tradestatus / open_status | suspend_d，L62–71（据 Arch；rg 见 L64） | suspend_d 的 S 记录，L80 | execution.py:748,1300；v2_lean_panels.py:150-184 |
| is_st_at_open | **L124 硬写为 False，不是从 stock_st 来的** | stock_st，L71、L97 | v2_lean_panels.py:152,189-190 |
| turnover | daily_basic.turnover_rate | daily_basic，L76、L96 | 流动性过滤 |
| factor | adj_factor | 新增行是 NaN，L97 | 复权收益 |

ST 口径说明（P3-2）：纸面实际的 ST 值来自 D0 一侧，`v2_readers.py` L1852–1853 把 is_st_at_open 前向填充到 extend 段（标 `is_st_at_open_ffill_research`）；主目录本身恒为 False。§4.5 的影子 ST 判定不变，但对照时，纸面口径按「D0 前向填充」理解，不能当成 stock_st。

### 3.4 events：间接读取（r2 审阅 P2-2，Q1 答复）

- r2 写的「events 不在纸面链上」**不正确**，更正为：**间接读取，是**（条件是纸面运行包含延长腿权重这一步）。
- `research/b4_paper_extend.py` 的 `run_legs()`（L160–168）先跑 `capacity_adv_paper_extend.py`（L163），再按顺序跑事件腿；`run_event_leg()`（L169–178）用 `python -c` 重跑冻结脚本，只改 `WEIGHT_END`（L173–174）。
- 被重跑的 `research/g1g5_earnings_event_weights.py`、`g1g5_insider_increase_weights.py`，以及 S6 的 `g1g5_equity_incentive_weights.py`，都在 L51–52 读 `data/v2/events/announcements_classified_pit.parquet` 和 `announcements_classified_pit_post202406.parquet`。S6 的延长由 `research/s6_paper_extend.py` 执行。
- `b4_paper.py` 本身的 backfill 和 forward 只读冻结权重文件（据 Arch，L99–118）。
- 10-19 纸面流程是否执行 extend，由 Strategy 和 Eng 按运行手册确认（开放问题 Q1）。
- 影子轨**绝不碰 events**：不读、不写、不调用任何事件腿脚本。
- A 和 C 路径：延长到 10-19 需要 10-19 的 events 是新鲜的，events 列入 §3.5。

### 3.5 A/C 路径 10-19 所需的 Tushare 表清单（供主 Agent 和 Leo 判断；B 不提供其中任何一项）

daily、adj_factor、daily_basic、stk_limit、suspend_d、stock_st、trade_cal、dividend（dividend_tushare / by_exdate）、fund_daily 和 etf_daily_adj（含 510300、fund_div）、index_daily（含期货 index_daily 和 fut_basic）、cb_daily 和 cb_basic（with_cb 时）、sw_l1_etf_map_pit_daily（with_ind_etf 时）、D1 估值、mid_large_members_pit 和 daily_update_status、asof_extend_tushare_202610 面板，以及 events（announcements_classified_pit*，extend 时）。

## 4. 单位与缺失字段（r1 P1-c）

### 4.1 Tushare 原生单位（影子面板统一到「股 / 元」，与主目录口径一致）

| Tushare 表.列 | 原生单位 | 面板口径 |
|---|---|---|
| daily.vol | 手（100 股） | 股（×100） |
| daily.amount | 千元 | 元（×1000） |
| fund_daily.vol / amount | 手 / 千元 | 股 / 元 |
| index_daily.vol / amount | 手 / 千元 | 股 / 元（只用于对照） |
| daily_basic.total_mv / circ_mv | 万元 | 元（×10000，tier1_materialize.py:337-338） |
| stk_limit.up_limit / down_limit | 元 | 元 |
| 价格列 | 元（股票最小价位 0.01，ETF 0.001） | 元 |

### 4.2 公开源换算

| 源字段 | 原始单位 | 换算 |
|---|---|---|
| 东财 f56 成交量 | 手 | ×100 = 股 |
| 东财 f57 成交额 | 元 | 不变；与 Tushare 对照时把 Tushare 千元 ×1000 |
| 腾讯 day 第 6 列成交量 | 手 | ×100 = 股 |
| 腾讯成交额 | 无 | 缺失，不派生 |
| 东财 f61 换手率 | % | 不变，只 warn |

影子面板显式带 `volume_unit=share` 和 `volume_shares` 两列（P3-5），避免任何对照代码落进 execution.py L1286 一带的比值推断分支。换算只做一次。

### 4.3 涨跌停价（缺 stk_limit；Q4 答复）

- 只对**状态确定的普通主板、创业板、科创板股票**派生：limit = round_half_up(pre_close × (1 ± r), 0.01)，主板 r=10%，创业板和科创板 r=20%；pre_close 取 Tushare 10-16 close（§5 检测通过的）。标 `limit_source=derived_rule`。
- 以下一律 `limit_status=unavailable`、limit=NaN：
  1. 风险警示板（ST、*ST）
  2. 退市整理期
  3. 注册制新股上市前 5 日（主板、创业板、科创板都包括）
  4. 长期停牌后复牌首日
  5. 北交所（本来已排除）
  6. ST 状态冲突（§4.5）
  7. 除权可疑（§5）
- 派生价只用于「是否触板」的披露，不参与任何成交判断。

### 4.4 停牌（缺 suspend_d）

- 推断：东财当日没有 kline 行，或 vol=0，记 `suspended_inferred=true`；腾讯同样没有行则加强判断。
- 复牌公告（R 记录）拿不到，记 `resume_announced=unavailable`。标 `suspend_source=inferred_no_bar`。

### 4.5 ST（缺 stock_st）

- 沿用 Tushare 10-16 stock_st 名单（`st_source=carried_from_20261016`）。东财名称含 ST 或 *ST 但不在名单里，或者反过来，记 `st_conflict=true`，涨跌停置 unavailable。
- 不把「名称含 ST」单独当作最终值。

## 5. 除权处理（采纳 Arch §10 答复）

- 只用不复权价（东财 fqt=0，腾讯复权位留空），禁止用公开源的前复权或后复权价。
- 除权可疑集合 = （公开源 pre_close 与 Tushare 10-16 close 相差超过最小价位）∪（dividend_tushare / by_exdate 中 ex_date=20261019 的代码）∪（fund_div 中 ex_date=20261019 的 ETF）。
- 处理：冻结可疑代码的持仓，NAV 标 PROVISIONAL。影子估值对这些代码按 10-16 收盘价冻结计价，整份报告标 PROVISIONAL，并列出清单和数量。

## 6. 对照与校验（采纳 Arch §10 答复）

用同一接口、同一字段拉最近 5 个交易日（按 trade_cal），与盘上 Tushare 比较。实施时才读数据；读之前确认没有叶 eval 在跑，并和 Arch 对齐 94322 是否要停到 T。

| 字段 | 规则 |
|---|---|
| open/high/low/close | 必须精确等于，到最小价位（股票 0.01 元，ETF 0.001 元）；不等则该代码 FAIL |
| volume（股） | 相对差 ≤0.1% 或绝对差 ≤1 手（100 股）：只 warn；任一持仓或候选代码相对差 >1%：FAIL |
| amount（元） | 统一换算到元；相对差 ≤0.5%，绝对宽限 ≥1 元；超出则 warn，持仓或候选超出要列出 |
| turnover_rate | 只 warn |
| 覆盖率 | Tushare 有行的代码中，公开源覆盖 ≥99.5%；指数和 510300 每天必须精确匹配；不达标则影子轨整体 FAIL，只披露，不出影子估值 |

- 北交所暂时排除，清单写进披露。
- 腾讯只做 OHLC 和成交量的交叉校验；两源 OHLC 不一致记 `source_conflict` 并剔除。
- 结果写 `recon_5d.json`（逐字段统计、不匹配清单、命令、时间、sha）。

## 7. 产物与写入

- 目录：`data/v2/_shadow_public/20261019/`，新建；已存在就退出。
- 文件：shadow_daily_eastmoney.parquet、shadow_daily_tencent.parquet、shadow_index_eastmoney.parquet、shadow_etf_raw.parquet、recon_5d.json、corp_action_check.json、shadow_valuation_report.md、guard_dirs_before.json、guard_dirs_after.json、manifest.json。
- manifest 字段：shadow=true、not_for_paper=true、degraded=true、逐文件来源、trade_date、pulled_at（ET 和 UTC）、各文件 sha、行数和代码数、HTTP 汇总、所读 Tushare 文件和冻结纸面输出的 sha、单位声明（volume=股，amount=元，volume_unit=share）、excluded_bj、黑名单目录运行前后的汇总 sha 及是否一致、promotion_approved=false、live=false。
- 写入方式：tmp 文件，校验 sha，再原子落盘；目标已存在就拒绝。§2.2 的黑名单全部不写。
- 影子估值（Q3 答复）：
  - 用冻结纸面 10-16 持仓（只读输出文件，sha 钉在 run .ok 里，P3-4）乘公开源 10-19 收盘价估算。
  - 估算 NAV **只能以区间形式**出现，标 SHADOW_NOT_NAV 和 PROVISIONAL；不报收益率，不下绩效结论，并列出不可用项。
  - 永远不写进任何 ledger、nav.csv、actual_weights、scorecard、promotion_gate、forward（FWD），也不进入给 Leo 的 NAV 报告。
  - 如果做不到这一隔离，就退回到只列持仓价格变动和不可用项。

## 8. 不覆盖清单

沿用 r1：
- adj_factor（没有 Tushare 口径；不沿用进任何纸面计算）
- daily_basic 估值和股本列（total_mv、pe/pb/ps、total_share/float_share/free_share）
- etf_daily_adj 的 close_hfq、adj_factor 和 ETF 分红
- 510300 分红（dividend_by_exdate）
- mid_large_universe 和 mid_large_members_pit（不生成任何成员文件，只在影子报告里披露）
- sw_pit、hsgt、cyq、tier3、events

r3 新增（Q2 答复）：
- 申万行业 ETF 映射 sw_l1_etf_map_pit_daily
- cb_daily、cb_basic_raw、cb_share_raw
- 股指期货 futures index_daily、fut_basic、IC 期货面板
- D1 估值
- daily_update_status
- trade_cal（日历已覆盖 2026，不需要）
- asof_extend_tushare_202610 和 asof_extend_202610 面板（影子轨既不读也不写，只算 sha 清单）
- 510300 基准收盘价序列（只在 §6 做对照，不生成基准文件）

## 9. Tushare 恢复后

1. 按正常 nightly 重拉 10-19，纸面按正常流程补跑（A 或 C 路径）。
2. 生成 `post_recon.json`，列出影子数据和 Tushare 的全部差异：涨跌停派生价和 stk_limit 对比、停牌推断和 suspend_d 对比、ST 沿用和 stock_st 对比、除权可疑和实际分红对比。
3. 影子目录保留，供审计；manifest 追加 reconciled_at 和 reconciled_sha。纸面从来没有读过影子数据，所以纸面回执不需要更正。

## 10. 运行限制

- 不碰 8787、moneyflow、data/v2/events；94322 是否停到 T 先和 Arch 对齐。
- 一次只跑一个重任务；叶 eval 在跑时不拉也不读；ET 16:40–18:40 不运行。
- nice -n 10；PYTHONDONTWRITEBYTECODE=1；RSS ≤1.5GB；MemAvailable 低于 2GB 就暂停；请求串行，每秒最多 5 次，最多重试 3 次。
- 只按确切 PID kill，禁止 pkill 和 killall；可能等待 stdin 的命令加 </dev/null。

## 11. 后续 .ok 要求（code .ok 和 run .ok 分开签）

- code-change .ok：
  - 新增独立脚本（拟 `scripts/acquire/daily_shadow_public.py`），入口先调用 `ok_runner_pin.enforce(script, ok_paths, modes, deps)`。
  - 写路径白名单只有 `data/v2/_shadow_public/`；代码里写死 §2.2 的黑名单，写入前检查，命中就中止。
  - 不 import、不调用 `enrich_asof_extend_em*`，不调用任何事件腿或 extend 脚本，**不改任何主线或纸面代码**。
  - 附 selftest（scope=selftest、allow_real_data=false、out_dir 在 /tmp、带 expires_et），覆盖：单位 ×100 和 ×1000、代码后缀、fqt=0、目录已存在时拒绝、OHLC 精确比较、北交所排除、Q4 的 unavailable 情形、黑名单拦截。
- run .ok（联网读取）：
  - 必须附主 Agent 书面转达的「Leo 选 B」。
  - 范围只有 20261019 加 5 日对照；外部域名只允许 push2his.eastmoney.com 和 web.ifzq.gtimg.cn。
  - 列出所读 Tushare 文件和冻结纸面 10-16 持仓输出文件的 sha（P3-4）。
  - 条件：黑名单目录（asof_extend_202610、asof_extend_tushare_202610、float_mktcap）运行前和运行后的 sha 清单写进回执，并证明完全一致（P2-1）。
- r1 的「纸面启用 fallback .ok」已经取消。

## 12. 开放问题

- Q1：10-19 纸面流程是否执行延长腿权重（extend）？请 Strategy 和 Eng 按运行手册确认。这决定 A/C 路径是否需要 10-19 的 events。
- Q2：黑名单目录的 sha 清单要逐文件算，回退目录有几千个面板文件，会带来读 IO。是否允许只对 size 和 mtime 做全量清单，再对 manifest.json、calendar.parquet 和抽样面板算 sha？默认按 Arch 原文做全量 sha。
- Q3：§2.2 黑名单第 4 项里 data_freshness_status.json 的确切路径，我还没用 rg 核对，实施前补上。
- Q4：标「据 Arch」的行号（v2_readers L1778/L1782、tier1_materialize L62–71、b4_paper L99–118、capacity_adv_paper_extend L84–85），实施前要逐行复核。

## 13. 审阅回应表

### 13.1 r1 审阅（r2 已处理，r3 保留）

| 条目 | r3 章节 |
|---|---|
| P1-a 只能是影子轨 | §0、§2.1、§7、§11 |
| P1-b 补全表和列 | §3 |
| P1-c 单位和缺失字段 | §4、§5 |
| §10 四问答复 | §5、§6、§8 |
| r1 不覆盖清单、升级背景 | §8、§1 |

### 13.2 r2 审阅（5072ec5c）

| 5072ec5c 条目 | 要求 | r3 处理 | 章节 |
|---|---|---|---|
| §1 引用核对：eng_daily_panels | asof_em 写回退目录，不写 tushare 目录 | 拆成两个目录、两个写入者；asof_ts 只校验 | §3.3 |
| §1 引用核对：tier1_materialize | L124 硬写 is_st_at_open=False | 已更正，并写明纸面 ST 口径是 D0 前向填充 | §3.3 |
| P2-1 | 回退目录入口；写入黑名单；禁止 enrich_asof_extend_em*；运行前后目录 sha 回执 | 引用 L90/L149/L1625/L1678–1680/L1779–1781；6 项黑名单；禁止调用；sha 清单写进回执和 run .ok | §2.2、§7、§11 |
| P2-2 / Q1 | events 被间接读取；列入 A/C 所需表 | 改为「间接读取：是」；影子轨绝不碰 events；列入 §3.5 | §3.4、§3.5 |
| P3-1 | 生成处拆开；回退目录 volume 是手，另有 volume_shares | 已拆开，写明单位和读取优先级 | §3.3 |
| P3-2 | ST 来源更正 | 已更正 | §3.3、§4.5 |
| P3-3 / Q2 | 补全书本引擎和 extend 读取的表 | 补 v2_multisleeve_book、extend 两张表，并补进不覆盖清单 | §3.1、§3.2、§3.5、§8 |
| P3-4 | 读冻结 10-16 持仓需要 .ok，钉 sha | run .ok 钉住输出文件 sha | §7、§11 |
| P3-5 | 显式带 volume_unit=share 和 volume_shares | 已加 | §4.2、§7 |
| Q3 | 估算 NAV 只能是区间，隔离 | 采纳，列出全部禁止写入位置 | §7 |
| Q4 | 特殊情形一律 unavailable | 采纳，列出 7 类 | §4.3 |
| §4 条件 4 | code .ok 和 run .ok 分开签，run .ok 附「Leo 选 B」 | 采纳 | §11 |
