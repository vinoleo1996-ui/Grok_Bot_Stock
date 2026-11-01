# 日线降级备用方案 r2：东财 / 腾讯公开日线 —— 仅作影子披露轨（SHADOW），不喂纸面（仅方案，待 Arch 审）

- 作者：QuantLab Data；起草：2026-10-18 ET；状态：DRAFT r2，未写代码、未运行、未联网、未读 parquet、未 import 项目代码
- 取代：r1 `docs/v2/plans/DATA_DAILY_FALLBACK_PUBLIC_SOURCE_PLAN_ZH.md`（sha256 92ceae2dd4122ed80435f7bcae38616866acf7816c9638ec8f07f87c6de1251c，冻结未改）
- 依据：主 Agent 2026-10-18 07:07 ET 裁定 ②③④；Arch 对 r1 审阅结论「需修改」（P1-a / P1-b / P1-c 及 §10 四问答复）
- 起草方式：只用 rg / Read 读 .py/.md 源码；行号以 2026-10-18 09:xx ET 工作区为准，实施前须按 sha 复核
- promotion_approved=false；live=false；strategy_promotion=false

## 0. r2 核心变化（一句话）

公开源数据**永远不进入**纸面持仓 / NAV / 信号。选项 B 在 r2 中被重新定义为「影子披露轨」：10-19 纸面要么按 A 顺延、要么按 C（Leo 当面同意）拿到 Tushare 数据正常跑；B 只产出对照与披露材料，供 Leo 和团队了解 10-19 行情与持仓的大致状况。

## 1. 触发条件与升级路径（Data 不做选择）

1. 中转 `https://pcd.mobcvb.cn/tushare/pro` 自 10-18 起不通；按裁定 ② 每小时只读小接口探测（到 10-19 14:30 ET，叶 eval 在跑时不探），证据存 `10-19-14-30` 目录。
2. 若 10-19 14:30 ET 中转仍不通：Data 报主 Agent；主 Agent 把以下选项带给 Leo，**Leo 决定**：
   - **A**：10-19 纸面顺延一天（纸面不读任何非 Tushare 数据）。
   - **B**：影子披露轨（本方案）。纸面本身仍然缺 10-19，等同 A 的纸面状态；额外产出公开源对照/披露。B 可与 A 或 C 并行。
   - **C**：Mac 代理（Leo 的电脑上的代理，需 Leo 当面同意）；纸面正常走 Tushare。
3. Data 不默认任何选项；未收到主 Agent 书面转达的「Leo 选 B」前，不拉任何公开源数据。中转在拉取前恢复则放弃本方案，走正常 nightly。
4. 时间窗：ET 10-19 16:40–18:40 不运行；data_freshness ok 的期限 10-19 17:40 ET **只能由 Tushare 数据满足**，B 不能让 freshness 变 ok。

## 2. P1-a：为什么 B 只能是影子轨

- 冻结纸面代码（capacity_adv / B4 / S6，经 `quantlab/portfolio/b4_paper.py`、`quantlab/portfolio/paper_track.py` 与 scripts_eng 书本引擎）只读 Tushare 衍生表（见 §3），没有任何读取 `_fallback` 路径的入口。
- 让纸面读到公开源只有两条路：(a) 改主线代码加 opt-in 参数；(b) 把公开源数据写进 Tushare 表 / asof 面板。两条都被禁止（冻结代码 + Tushare 表只能由 Tushare 写）。
- 因此 r1 §4「读取端 `--data-source fallback:` / `QL_DAILY_FALLBACK`」整节**作废**；r1 §9 中「读取端 opt-in 参数」与「启用 fallback 的纸面运行 .ok」也作废。
- 影子轨的产物只允许：对照表、披露报告、持仓的「影子估值」（明确标 SHADOW_NOT_NAV）。任何产物不得被 b4_paper / paper_track / scorecard / promotion_gate / forward 读取；文件名与 manifest 均带 `shadow` 与 `not_for_paper=true`。
- 纸面回执中 10-19 的状态由纸面自身决定（A：顺延；C：正常）；B 只可在回执外附一段披露链接，不改 NAV、不改持仓、不改信号。

## 3. P1-b：纸面实际读取的表与列（只读源码核对）

### 3.1 读取链路

| 环节 | 文件:行 | 读取内容 |
|---|---|---|
| 纸面配置/权重 | `quantlab/portfolio/b4_paper.py:24-25` | 冻结权重 `output/small_aum_concentration/v2/B_B4_50_25_25_topN_{60w,100w}.parquet`（列 session, instrument_id, weight，见 :242） |
| B4 事件腿 | `quantlab/portfolio/b4_paper.py:35-36` | `output/ai_factory/g1g5_earnings_event_*_20261014_005430.parquet`、`g1g5_insider_increase_*_20261014_011841.parquet`（冻结权重，非实时读 events 表） |
| S6 | `quantlab/portfolio/paper_track.py:9-12` | `output/strategy_wf_combo/weights_S6_{60w,100w}.parquet`；事件腿 earnings_event、equity_incentive |
| 书本引擎 | `quantlab/portfolio/b4_paper.py:187-196` | `scripts_eng` 书本，X2/BOOK actual_weights、FWD 前推 |
| 行情面板 | `quantlab/platform/execution.py:1197-1352` `load_exec_panels` | 经 `quantlab/data/v2_readers.py` 合并 D0 + `data/v2/asof_extend_tushare_202610/`（:17, :89） |
| 基准/ETF | `quantlab/platform/strategy_feed.py:558`；`execution.py:1213,1359` | `data/v2/etf_510300` 面板；`data/v2/etf/etf_daily_adj.parquet`；`data/v2/etf/raw/fund_div.parquet`（:1510） |
| 分红/送转 | `execution.py:1569-1600`；`v2_readers.py:95` | `data/v2/corporate_actions/dividend_tushare.parquet` 及 `dividend_by_exdate_tushare.parquet`（:1576）；列 cash_div_tax（税前每股）、送转比例 |
| 退市/SD1 | `quantlab/platform/execution_sd1.py:315,519`；`delist_accounting.py:44` | `data/v2/ref/delist_consideration.parquet`；`data/v2/st_events/namechange_all.parquet`；halt_extra（suspend_d S 记录） |
| 可交易性 | `quantlab/platform/tradability.py:27,51` | resume_announced（suspend_d R 记录，t 09:00 PIT） |

### 3.2 asof 面板（`asof_extend_tushare_202610`）的列与来源

由 `scripts/acquire/eng_daily_panels.py`（:4, :71-98）与 `scripts/acquire/tier1_materialize.py`（:40-132）从本地 tushare_raw 生成：

| 面板列 | 来源 Tushare 表.列 | 生成处 | 纸面使用处 |
|---|---|---|---|
| open/high/low/close | daily.open/high/low/close（元） | eng_daily_panels.py:94 | execution.py:1226 fields |
| volume / volume_shares | daily.vol（手）×100 → 股；volume_unit=lot_100sh | eng_daily_panels.py:94-98；tier1_materialize.py:40 | execution.py:1271-1294 |
| amount | daily.amount（千元）×1000 → 元 | eng_daily_panels.py:94；tier1_materialize.py:41 | execution.py:1226；U30/参与率 |
| limit_up / limit_down | **stk_limit**.up_limit / down_limit（元） | eng_daily_panels.py:76,96；tier1_materialize.py:53-61 | execution.py:753-755（涨跌停拒单）；v2_lean_panels.py:148,163 |
| limit_ratio_at_open | up_limit/pre_close-1 | eng_daily_panels.py:92,97 | 研究诊断 |
| open_status / tradestatus | **suspend_d**（suspend_type==S） | eng_daily_panels.py:80；tier1_materialize.py:64 | execution.py:1300（suspended）、748；v2_lean_panels.py:150-184 |
| is_st_at_open | **stock_st**（ts_code, trade_date） | eng_daily_panels.py:71,97 | v2_lean_panels.py:152,189-190；v2_readers.py:1715,1851 |
| turnover | daily_basic.turnover_rate（%） | eng_daily_panels.py:76,96 | 流动性过滤 |
| factor | adj_factor（10-12 起增量为 NaN，由 adj 表补） | eng_daily_panels.py:97；execution.py:1260-1265 | 复权收益 |

### 3.3 r1 漏列的表（本次补齐）

| 表 | 纸面是否读 | 公开源能否给 | 影子轨处理 |
|---|---|---|---|
| asof 面板（上表） | 是（全部行情经它） | 部分（见 §4） | 影子轨自建独立面板 `shadow_panel.parquet`，不写 asof 目录 |
| stk_limit | 是（涨跌停拒单） | 否（无官方价）；可派生 | §4.3 派生并标 derived |
| suspend_d | 是（停牌/复牌门） | 否；可推断 | §4.4 |
| stock_st | 是（ST 过滤） | 否；可由名称推断 | §4.5 |
| dividends（dividend_tushare / by_exdate；fund_div） | 是（除权日现金/送股） | 否 | §5 |
| events（data/v2/events/*） | 纸面事件腿用 10-14 冻结权重；events 表本身不在 10-19 纸面读取链上（rg 未见 b4_paper/paper_track 直接读取） | 否 | 不覆盖；开放问题 Q1 请 Arch/Strategy 确认 |
| adj_factor、daily_basic 估值列、etf_daily_adj hfq/分红、510300 分红、mid_large 沿用 | 是 | 否 | 见 §8 不覆盖清单 |

## 4. P1-c：单位与缺失字段

### 4.1 Tushare 原生单位（以 Tushare 为准，影子面板统一到「股 / 元」= asof 面板口径）

| Tushare 表.列 | 原生单位 | 面板口径 |
|---|---|---|
| daily.vol | 手（100 股） | 股（×100） |
| daily.amount | 千元 | 元（×1000） |
| fund_daily.vol / amount | 手 / 千元 | 股 / 元 |
| index_daily.vol / amount | 手 / 千元 | 股 / 元（仅对照） |
| daily_basic.total_mv / circ_mv | 万元 | 元（×10000，tier1_materialize.py:337-338） |
| stk_limit.up_limit / down_limit | 元 | 元 |
| 价格列 | 元（股票 0.01；ETF 0.001） | 元 |

### 4.2 公开源换算

| 源字段 | 原始单位 | 换算到面板 |
|---|---|---|
| 东财 f56 成交量 | 手 | ×100 → 股 |
| 东财 f57 成交额 | 元 | 不变（元）；与 Tushare 对照时 Tushare 千元 ×1000 |
| 腾讯 day 第 6 列成交量 | 手 | ×100 → 股 |
| 腾讯成交额 | 无 | 缺失，不派生 |
| 东财 f61 换手率 | % | 不变，仅 warn |

r1 §3.3 曾把对照口径写成「东财元 /1000 → 千元」，r2 改为统一换到元（与 asof 面板一致），只在一处换算，避免双向混用。

### 4.3 涨跌停价（stk_limit 缺）

- 派生：limit = round_half_up(pre_close × (1 ± r), 0.01)，pre_close 取 Tushare 10-16 close（§5 检测通过者）；r：主板 10%，ST 5%，创业板/科创板 20%，新股上市前 5 日无限制 → 标 unavailable。
- 标记：`limit_source=derived_rule`；不等于官方 stk_limit；ST 判定不确定（§4.5）或除权可疑（§5）时 limit=NaN、`limit_status=unavailable`。
- 只用于影子估值的「是否触板」披露，不用于任何成交判断。

### 4.4 停牌（suspend_d 缺）

- 推断：东财当日无 kline 行或 vol=0 → `suspended_inferred=true`；腾讯同步无行则加强。
- 复牌公告（R 记录）无法获取 → `resume_announced=unavailable`。
- 标记 `suspend_source=inferred_no_bar`；不得冒充 suspend_d。

### 4.5 ST（stock_st 缺）

- 推断：沿用 Tushare 10-16 stock_st 名单（`st_source=carried_from_20261016`）；若东财名称含 ST/*ST 但不在名单，或反之 → `st_conflict=true`，该代码涨跌停价置 unavailable。
- 不使用 enrich_asof_extend_em_seq.py:77 的「名称含 ST」单独判定作为最终值。

### 4.6 除权（dividends / adj_factor 缺）：见 §5。

## 5. 除权处理（采纳 Arch §10 答复）

- 只用不复权价（东财 fqt=0，腾讯复权位留空）；禁止公开源前/后复权价。
- 除权可疑集合 = (公开源 pre_close 与 Tushare 10-16 close 差 > 最小价位) ∪ (盘上 dividend_tushare / dividend_by_exdate 中 ex_date=20261019 的代码) ∪ (fund_div 中 ex_date=20261019 的 ETF)。
- 处理（Arch 裁定）：**冻结可疑代码的持仓，NAV 标 PROVISIONAL**。在影子轨中即：影子估值对这些代码用 10-16 收盘价冻结计价，影子报告整体标 PROVISIONAL，清单与数量列出。纸面本身不受影响（纸面不读影子数据）。

## 6. 对照与校验（采纳 Arch §10 答复）

对最近 5 个交易日（按 trade_cal）用同接口同字段拉取，与盘上 Tushare 比较；实施时才读数据，读前确认无叶 eval 在跑、94322 状态与 Arch 对齐。

| 字段 | 规则 | 结果 |
|---|---|---|
| open/high/low/close | 必须**精确等于**到最小价位（股票 0.01 元，ETF 0.001 元） | 任何不等 → 该代码 FAIL |
| volume（股） | 相对差 ≤ 0.1% 或绝对差 ≤ 1 手(100 股) → 仅 warn；任一持仓或候选代码相对差 > 1% → FAIL | |
| amount（元） | 统一换算到元；相对差 ≤ 0.5%，且绝对宽限 ≥ 1 元 | 超出 → warn；持仓/候选超出 → 列出 |
| turnover_rate | 仅 warn | |
| 覆盖率 | Tushare 有行代码中公开源覆盖 ≥ 99.5%；指数与 510300 每日必须精确匹配 | 不达标 → 影子轨整体标 FAIL，仅披露，不再产出影子估值 |

- 北交所（.BJ）**暂时排除**（Arch 裁定），清单列入披露。
- 腾讯只作 OHLC/vol 交叉校验；两源 OHLC 不一致 → `source_conflict`，剔除。
- 结果写 `recon_5d.json`（逐字段统计、不匹配清单、命令、时间、sha）。

## 7. 产物与写入

- 目录：`data/v2/_shadow_public/20261019/`（新建；已存在即退出）。不使用 r1 的 `_fallback` 名，避免被误认为可替代数据。
- 文件：shadow_daily_eastmoney.parquet、shadow_daily_tencent.parquet、shadow_index_eastmoney.parquet、shadow_etf_raw.parquet、recon_5d.json、corp_action_check.json、shadow_valuation_report.md、manifest.json。
- manifest：shadow=true、not_for_paper=true、degraded=true、source（逐文件）、trade_date、pulled_at（ET/UTC）、各文件 sha/行数/代码数、HTTP 汇总、所读 Tushare 文件 sha、单位声明（volume=股、amount=元）、excluded_bj、promotion_approved=false、live=false。
- 写入：tmp → 校验 sha → os.replace。任何 Tushare 表与 asof 面板、data_freshness_status.json 都不写。
- 影子估值报告：用冻结纸面 10-16 持仓（只读输出文件）× 公开源 10-19 收盘做估算，标 SHADOW_NOT_NAV / PROVISIONAL；不报绩效、不报收益率结论，只列「估算区间与不可用项」。

## 8. 不覆盖清单（沿用 r1）

- adj_factor（无 Tushare 口径；不沿用进任何纸面计算）
- daily_basic 估值/股本列（total_mv、pe/pb/ps、total_share/float_share/free_share）
- etf_daily_adj 的 close_hfq / adj_factor 及 ETF 分红
- 510300 分红（dividend_by_exdate）
- mid_large_universe（r1 拟沿用 10-16 成员；r2 中仅在影子报告里披露，不生成任何成员文件）
- sw_pit / hsgt / cyq / tier3 / events

## 9. Tushare 恢复后

1. 正常 nightly 重拉 10-19，纸面按正常流程补跑（A/C 路径）。
2. 生成 `post_recon.json`：影子数据与 Tushare 全量差异（含涨跌停派生价 vs stk_limit、停牌推断 vs suspend_d、ST 沿用 vs stock_st、除权可疑 vs 实际分红）。
3. 影子目录保留审计，manifest 追加 reconciled_at / reconciled_sha；纸面回执无需更正（纸面从未读影子数据）。

## 10. 运行限制

- 不碰 8787、moneyflow、data/v2/events；94322 是否停到 T 先与 Arch 对齐。
- 一次只跑一个重任务；叶 eval 在跑时不拉不读；ET 16:40–18:40 不运行。
- nice -n 10；RSS ≤ 1.5GB；MemAvailable < 2GB 暂停；请求串行 ≤ 5 次/秒，重试 ≤ 3。
- 只按确切 PID kill，禁止 pkill/killall；可能等 stdin 的命令加 </dev/null。

## 11. 后续 .ok 要求

- code-change .ok：新增独立脚本（拟 `scripts/acquire/daily_shadow_public.py`），入口先调用 `ok_runner_pin.enforce(script, ok_paths, modes, deps)`；写路径白名单仅 `data/v2/_shadow_public/`；**不改任何主线/纸面代码**；附 selftest（scope=selftest、allow_real_data=false、out_dir 在 /tmp、expires_et；覆盖单位 ×100/×1000、后缀、fqt=0、目录已存在拒绝、精确 OHLC 比较、BJ 排除）。
- run .ok：引用主 Agent 转达的 Leo 选 B 裁定；范围仅 20261019 + 5 日对照；允许外部域名仅 push2his.eastmoney.com、web.ifzq.gtimg.cn；列出所读 Tushare 文件 sha。
- 不再需要 r1 的「纸面启用 fallback .ok」（该路径已取消）。

## 12. 开放问题

- Q1：events 表是否在 10-19 纸面链上被间接读取（例如事件腿权重在 10-14 之后是否会重算）？源码 rg 未见 b4_paper/paper_track 直接读取，请 Arch/Strategy 确认。
- Q2：scripts_eng 书本引擎内部是否另读其他行情表（本文按 load_exec_panels 链路列出，scripts_eng 内部尚未逐行核对，实施前补）。
- Q3：影子估值报告是否允许出现估算 NAV 数字（即使标 SHADOW_NOT_NAV）？若 Arch 认为有误导风险，改为只列持仓价格变动与不可用项。
- Q4：涨跌停派生规则对注册制新股（上市前 5 日）以外的特殊情形（风险警示板、退市整理期 10%）是否一律置 unavailable。

## 13. 审阅回应表（Arch r1 审阅 → r2 章节）

| Arch 条目 | 要求 | r2 处理 | 章节 |
|---|---|---|---|
| P1-a | 冻结纸面不能读 _fallback；B 只能影子披露 | 全文改为影子轨；r1 §4 读取端参数与 §9 纸面 .ok 作废；产物 not_for_paper | §0, §1, §2, §7, §9, §11 |
| P1-b | 补 asof 面板、stk_limit、suspend_d、stock_st、dividends、events；列各纸面轨读的列 | 读取链路与列逐行引用 | §3.1–§3.3 |
| P1-c | 手→股、千元→元一致；说明涨跌停/停牌/ST/除权 | 原生单位表 + 统一换算到股/元；四项派生或标 unavailable | §4, §5 |
| §10-1 | OHLC 精确到最小价位；vol ≤0.1% 或 ≤1 手 warn，持仓/候选 >1% FAIL；amount 元、0.5%、宽限 ≥1 元 | 采纳 | §6 |
| §10-2 | 除权可疑：冻结持仓、NAV PROVISIONAL | 采纳（影子估值冻结计价，报告 PROVISIONAL） | §5 |
| §10-3 | daily_basic / mid_large 沿用 | 不进入纸面；仅披露 | §8 |
| §10-4 | 北交所暂排除 | 采纳 | §6 |
| r1 不覆盖清单 | 保留 | 保留 | §8 |
| 升级背景 | 14:30 仍断 → 主 Agent 带 A/B/C 给 Leo | 保留，B 重定义为影子 | §1 |
