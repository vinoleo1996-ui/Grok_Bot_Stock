# 日线降级备用方案：东财 / 腾讯公开日线（仅方案，待 Arch 审）

- 作者：QuantLab Data；起草：2026-10-18 ET；状态：DRAFT，未写代码、未运行、未联网
- 依据：主 Agent 2026-10-18 07:07 ET 裁定 ③（公开日线只做备用；先写方案交 Arch）
- 起草期间约束：叶23 r2.11 / 叶24 正在跑真实数据；本文只读了 .py/.md 源码（rg），未读任何 parquet/数据文件，未 import 项目代码，未发起网络请求
- promotion_approved=false；live=false

## 1. 触发条件（Data 不做选择）

同时满足以下两条才启用：
1. 10-19 14:30 ET 中转仍不通（依据：主 Agent 裁定 ② 的每 60 分钟小接口探测证据，最后一次失败记录在 14:30 前后）。
2. 主 Agent 带选项报 Leo，Leo 选 **B（公开源降级跑）**，主 Agent 书面转达给 Data。

选项：A 当天纸面顺延一天；B 公开源降级，标记降级源，Tushare 恢复后对账；C Mac 代理（Leo 的电脑，需 Leo 当面同意）。Data 不选择、不默认任何选项；未收到 B 的书面裁定前不拉任何公开源数据。若中转在拉取前恢复，立即放弃本方案，走正常 nightly。

## 2. 范围：只拉 2026-10-19 单日

来源：scripts/nightly_update.py steps_for() 与 scripts/acquire/data_freshness_status.py 的表 T（严格闸门）/ W（warn）。

| 表（freshness 名 / 路径） | nightly 步骤 | 纸面/闸门是否需要 | 公开源能否提供 | 说明 |
|---|---|---|---|---|
| daily_ohlcv_raw_pit（data/v2/bars/daily_ohlcv_raw_pit.parquet） | daily_pull + bars | 是（严格） | **能**：东财 push2his kline fqt=0；腾讯 ifzq 不复权 | 主体，OHLC/vol/amount/pre_close(派生) |
| adj_factor（data/v2/adj/adj_factor_2023h2plus.parquet） | adj_factor | 是（严格） | **不能直接提供** | 公开源无 Tushare 口径 adj_factor；只能沿用上一交易日因子（见 §6），除权日无法正确给出 |
| daily_basic（data/v2/valuation/daily_basic_full_tushare.parquet） | daily_basic | 是（严格） | **部分**：东财 f61 换手率；流通市值可按 amount*100/turnover 派生（enrich_asof_extend_em.py:271 已用此式） | total_mv、pe/pb/ps、total_share/float_share/free_share 等无法可靠提供 |
| index_daily_pit（data/v2/index/index_daily_pit.parquet） | index_pull + index | 是（严格） | **能**（主要指数）：东财 secid 1.000300 等 / 腾讯 sh000300 | 需逐一列出纸面用到的指数代码；非主流指数可能不全 |
| etf_daily_adj（data/v2/etf/etf_daily_adj.parquet） | etf_daily_adj | 是（严格） | **部分**：不复权 OHLC 能；close_hfq/adj_factor 只能沿用 | ETF 分红日风险同 §6 |
| etf510300（data/v2/etf_510300/panels/sh.510300.parquet） | eng_panels | 是（严格） | **能**（不复权 OHLCV） | 分红字段（dividend_by_exdate）不能 |
| mid_large_universe | mid_large_universe | 是（严格） | **间接**：依赖 daily_basic 市值；降级值只能用派生流通市值 | 建议沿用 10-16 成员（披露） |
| trade_cal | trade_cal | 是 | 不需要（日历已覆盖 2026） | — |
| sw_pit（warn） / hsgt / cyq / tier3 / events | sw/hsgt/cyq/tier3/events | 不影响严格闸门 | **不覆盖** | RELAY_STEPS 中转不通时按现有逻辑记 partial；本方案不处理 |

**公开源不能覆盖的表**：adj_factor（只能沿用）、daily_basic 的估值/股本列、ETF/股票分红与 hfq 列、sw_pit/hsgt/cyq/tier3。纸面若硬依赖这些列，降级跑只能用 10-16 值并披露。

待办（实施前，Data，只读源码）：逐条列出 capacity_adv / B4 / S6 三条纸面轨实际读取的列，缩小上表为最小集合。

## 3. 数据源与字段映射

### 3.1 东财 push2his（仓库已用：scripts/enrich_asof_extend_em.py:62-74，enrich_asof_extend_em_seq.py:34-37）

- URL：https://push2his.eastmoney.com/api/qt/stock/kline/get
- 参数：fields1=f1..f6；fields2=f51..f61；klt=101（日线）；**fqt=0（不复权，强制）**；secid=市场.代码（1=SH，0=SZ；BJ 待实测确认，仓库注释为问号）；beg=end=20261019（对账时 beg=前5个交易日）
- 头：Referer https://quote.eastmoney.com/
- 字段：f51 日期、f52 开、f53 收、f54 高、f55 低、f56 成交量（**手**）、f57 成交额（**元**）、f58 振幅%、f59 涨跌幅%、f60 涨跌额、f61 换手率%

### 3.2 腾讯 ifzq（仓库已用：scripts/extend_asof_v2.py:30）

- URL：https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={code},day,2026-10-19,2026-10-19,320,
- 复权参数位留空 = 不复权（**必须留空，禁止 qfq/hfq**）；返回 data[code].day 行：[日期, 开, 收, 高, 低, 成交量(手)]，**无成交额**
- 代码：sh600000 / sz000001 / bj430017（extend_asof_v2.to_tx）

### 3.3 映射到 Tushare daily 口径

| Tushare 列 | 单位 | 东财 | 腾讯 | 换算 |
|---|---|---|---|---|
| ts_code | 600000.SH | secid 1.600000 → 600000.SH | sh600000 → 600000.SH | 后缀统一 .SH/.SZ/.BJ；项目内 instrument_id 若为 sh.600000 形式由读取端转换，fallback 文件同时存两列 |
| open/high/low/close | 元 | f52/f54/f55/f53 | 第2/4/5/3列 | 直接 |
| pre_close | 元 | f53-f60 派生 | 不提供 | **主用：Tushare 10-16 close**（见 §6 检测） |
| change / pct_chg | 元 / % | f60 / f59 | — | 以 close-pre_close 重算 |
| vol | **手** | f56（手） | 第6列（手） | 不换算 |
| amount | **千元** | f57（元） | 无 | /1000 |
| turnover_rate | % | f61 | — | 直接 |
| circ_mv | **万元** | 派生 amount_元*100/f61 /1e4 | — | 只做 warn 列，标 derived |

主源：东财（有成交额）；腾讯只作 OHLC/vol 交叉校验，两者 OHLC 不一致 >0.01 元的代码标记 source_conflict 并剔除。

## 4. 输出与显式启用

- 目录：`data/v2/_fallback/20261019/`（新建；已存在即报错退出，不覆盖）
- 文件：daily_raw_eastmoney.parquet、daily_raw_tencent.parquet、index_daily_eastmoney.parquet、etf_daily_raw.parquet、recon_5d.json、corp_action_check.json、manifest.json
- manifest.json：source=eastmoney|tencent（逐文件）、degraded=true、trade_date=20261019、pulled_at（ET 与 UTC 各一）、每个文件 sha256 与行数/代码数、请求命令与 HTTP 状态汇总、输入 Tushare 文件 sha（对账用）、adj_basis="tushare_adj_factor_carried_forward_from_20261016"、promotion_approved=false、live=false
- 写入：tmp → 校验 → os.replace；保护 sha 检查在写入前。**任何 Tushare 表（data/v2/bars、adj、valuation、index、etf 等）不得被写或覆盖**；data_freshness_status.json 也不改写（它会如实显示 stale）。
- 启用：读取端/纸面必须显式传 `--data-source fallback:data/v2/_fallback/20261019/manifest.json`（或环境变量 QL_DAILY_FALLBACK=该路径），默认关闭；没有该参数时一律读 Tushare。启用时校验 manifest sha 与 degraded=true，并把 manifest sha 写进回执。
- 回执披露：纸面回执顶部写明「10-19 行情来自公开源（东财/腾讯）降级，未经 Tushare 校验；adj_factor 沿用 10-16；待对账」，附 manifest sha、recon_5d 结果、被剔除代码数。

## 5. 使用前对账（最近 5 个交易日）

用同一接口、同一字段拉 10-13 至 10-16 及之前共 5 个交易日（按 trade_cal 取），与盘上 Tushare 已有数据比较（实施时才读数据，读前确认无叶 eval 在跑）。

| 字段 | 容差 | 理由 |
|---|---|---|
| open/high/low/close | 差值 ≤ 0.01 元（期望完全相等） | 两源都来自交易所，价格到分；ETF 到 0.001 元，容差 0.001 |
| vol | 相对差 ≤ 0.1%（且绝对差 ≤ 1 手） | 均为手；盘后固定价格交易（科创/创业板）是否计入口径可能不同 |
| amount | 相对差 ≤ 0.5% | 东财元 vs Tushare 千元（四舍五入到 0.001 千元）；盘后固定价格成交口径差 |
| turnover_rate（warn） | 相对差 ≤ 2% | 股本口径不同，仅 warn |

覆盖与通过：
- 每日：Tushare 有行的代码中，公开源覆盖率 ≥ 99.5%；OHLC 四项全部在容差内的代码占比 ≥ 99.9%；vol/amount 在容差内 ≥ 99.5%。
- **失败即整体不可用**：任一天覆盖率或 OHLC 匹配率不达标；或纸面持仓/候选池中任一代码 OHLC 不匹配；或指数/510300 任一日不匹配。失败时不启用 fallback，报主 Agent（回到 A/C）。
- 结果写 recon_5d.json（逐字段统计、不匹配代码清单、命令、时间、sha）。

## 6. 复权口径

- 只用**不复权**原始价（东财 fqt=0，腾讯复权位留空）。禁止使用公开源的前复权/后复权价（其因子算法和 Tushare adj_factor 不同，混用会造成跳变）。
- 复权：adj_factor(10-19) := adj_factor(10-16)（Tushare，沿用）。
- 风险：10-19 为除权除息日的代码，沿用因子会把除息跌幅当成真实收益（错误的负收益），影响动量/收益类信号和纸面损益。
- 检测（corp_action_check.json）：
  1. 公开源当日 pre_close（东财 f53-f60）与 Tushare 10-16 close 比较，|差| > 0.01 元即判定有公司行为；
  2. 交叉核对盘上分红文件（eng_panels 的 dividend_by_exdate，及 collect_corporate_actions.py 的东财分红送转产物）中 ex_date=20261019 的代码；
  3. 两者并集即「除权可疑」集合。
- 处理：可疑代码不做复权推断，当日从纸面信号中剔除或冻结其持仓到 Tushare 恢复（具体由 Arch 定），清单与数量写进回执。

## 7. Tushare 恢复后对账

1. 中转恢复后按正常 nightly 重拉 10-19（daily、adj_factor、daily_basic、index、etf），写正常 Tushare 表。
2. 生成 `data/v2/_fallback/20261019/post_recon.json`：逐代码逐字段列出 fallback 与 Tushare 的全部差异（不只超容差的），及 adj_factor 实际值 vs 沿用值。
3. 回执处理：
   - 差异全在 §5 容差内且无除权差异：原回执追加注记「已与 Tushare 对账一致」+ post_recon sha，不改结果；
   - 有超容差或除权差异：用 Tushare 数据重算 10-19 纸面，出更正回执（原回执保留，标 superseded_by），列明受影响代码、持仓与损益差。
4. fallback 目录保留不删（审计用），manifest 追加 reconciled_at / reconciled_sha。

## 8. 运行限制

- 不碰 8787、moneyflow、data/v2/events、PID 94322。
- 同一时间只跑一个重任务；叶23/叶24 eval 在跑时不拉、不读数据。
- ET 16:40–18:40 之间不运行。
- nice -n 10；RSS ≤ 1.5GB（超出即退出）；请求串行、限速（每秒 ≤ 5 个请求，失败重试 ≤3 次）。
- 只能按确切 PID kill，禁止按模式 pkill。
- promotion_approved=false，live=false。

## 9. 后续代码与运行的 .ok 要求

- code-change .ok：新增独立脚本（拟 scripts/acquire/daily_fallback_public.py）与读取端 opt-in 参数；入口调用 ok_runner_pin.enforce(script, ok_paths, modes, deps)；写路径白名单仅 `data/v2/_fallback/`；附 selftest（单位换算、代码后缀、fqt=0 断言、目录已存在拒绝、保护 sha）。
- run .ok：须引用主 Agent 转达的 Leo 选 B 的裁定；范围仅 trade_date=20261019 + 5 日对账；输出目录仅 data/v2/_fallback/20261019/；列出将读取的 Tushare 文件及其 sha；允许的外部域名仅 push2his.eastmoney.com、web.ifzq.gtimg.cn。
- 读取端启用 fallback 的纸面运行另需一份 .ok，引用 manifest sha 与 recon_5d 通过结果。

## 10. 待 Arch 裁定

1. §5 各容差数值与 99.5%/99.9% 门槛。
2. 除权可疑代码：剔除信号还是冻结持仓。
3. daily_basic/mid_large_universe 是否允许沿用 10-16 值。
4. BJ secid 前缀实测前，北交所代码是否直接排除。
