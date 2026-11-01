# Data 回执：fund_basic 场外满窗 + 主动权益过滤集（20261027）

- 角色：QuantLab Data（执行器）
- 时刻：2026-10-27 20:45 ET (America/New_York)
- 任务：补 `fund_basic` market=O 满窗；落主动权益过滤集；供 AI fund_portfolio 计数附录重跑前置
- 参照：AI 附录 `docs/v2/audit/AI_FUND_PORTFOLIO_COUNT_APPENDIX_RECEIPT_20261027_ZH.md` sha8 **`f36d0a04`**；WHO **`5393a769`**；ALLA **`8ef304f5`**
- `live=false`；`promotion=false`；`leo_notify=false`
- **未**改任何 FROZEN 条款；**未**读价格/收益；**未**混叶38；**未**申 `.ok`；**未**挂 QUIET；**未**动 nightly/leaf37；**未**改 trade_cal PIN；**未**动 `fund_basic_E`；**未**碰 fund_portfolio 生产合并；**未**消费 `9e4359f9`；**未** git commit

## 结论

| 项 | 值 |
|---|---|
| **status** | **PASS**（满窗 COVER 2018→2026） |
| source | datahub `fund_basic`（直连；offset 翻页 limit=15000） |
| market | **O**（场外） |
| 全量行数 | **29630**（L=25283 / D=4347 / I=0） |
| 主动权益行数 | **14241**（L=11957 / D=2284；market 仅 O） |
| found_date 窗 | **20010921 → 20261026**（COVER 2018→2026） |
| issue_date 窗 | 20010911 → 20261116 |

## 落盘钉

| 文件 | 行数 | sha8 | 全长 sha256 |
|---|---:|---|---|
| `data/v2/etf/raw/fund_basic_O.parquet` | 29630 | **`50b32700`** | `50b32700ae819f85d531bbd95c4ca7cd7af3f516fa14ad4a3ce81c1db4aa39b2` |
| `data/v2/etf/raw/fund_basic_O_manifest.json` | — | **`bbde0fff`** | `bbde0fff23dc723d8594ff7d2e3b35a63fdb95ab8c137b466be032b728fb66e4` |
| `data/v2/ref/fund_basic_active_equity.parquet` | 14241 | **`d96b83e1`** | `d96b83e12951bf53b76016927bd7417dae1a0e41f6c748a69860c710e52390f8` |
| `data/v2/ref/fund_basic_active_equity_manifest.json` | — | **`eeb0f489`** | `eeb0f4894e26c44a1a8f767d8506990bec32a07e4690829757879a4233597f9b` |

对照：`data/v2/etf/raw/fund_basic_E.parquet` **未改**（mtime 2026-10-25；sha256 `07e0151624b02eefd11c88c0a1de31e6a70db8736c5dd019a73aaab902b66d8f`）。

## 拉数过程

1. `datahub('fund_basic', market='O', status=st, offset=…, limit=15000)`；status ∈ {L, D, I}
2. L：offset=0 → 15000；offset=15000 → 10283；合计 25283
3. D：单页 4347（未触顶）
4. I：空页 0（无增量）
5. 合并后按 `ts_code` 去重（L/D 无交叉）；保留全部原始字段 + `status_q`
6. 临时页：`data/v2/etf/raw/_pull/fund_basic_O_{L,D}_off*.parquet`（可留档）

## 主动权益过滤规则（写死）

原文口径（供 AI 计数复用；不得用 ETF-only 冒充）：

1. **纳入** `market == 'O'`
2. **纳入** `fund_type ∈ {股票型, 混合型}`（权益向；不纳入债券型/货币型/短期理财债券型/REITs/其他）
3. **剔除** `invest_type ∈ {被动指数型, 增强指数型}`；另列防御别名 `增强型`（本批在 fund_type 过滤后命中 **0**，实质剔除仅前两者）
4. **剔除** 名称含：`ETF`（大小写不敏感）/ `联接` / `指数`（中文必剔）
5. **保留** `status ∈ {L, D}`（满窗需历史退市/清盘）
6. **去重键** `ts_code`

一句话摘要：**场外 O ∩（股票型|混合型）− 被动/增强指数 − 名含 ETF/联接/指数，保留 L+D。**

## 剔除计数（阶梯）

| 步骤 | 剩余行数 | 本步剔除 | 明细 |
|---|---:|---:|---|
| 输入 market=O | 29630 | — | L 25283 + D 4347 |
| fund_type 过滤 | 18913 | 10717 | 债券型 9458；货币型 1023；短期理财债券型 151；其他 76；REITs 9 |
| invest_type 剔除 | 14604 | 4309 | 被动指数型 **3292**；增强指数型 **1017**；（增强型 0） |
| 名称剔除（并集） | 14241 | 363 | 命中 ETF **181** / 联接 **180** / 指数 **182**（可重叠） |
| 最终主动权益 | **14241** | — | 混合型 12861；股票型 1380；status L 11957 / D 2284 |

## 窗覆盖

- `found_date` min/max：**20010921 / 20261026** → **COVER** 2018→2026
- `issue_date` min/max：20010911 / 20261116
- 主动权益集同样 found_date **20010921 → 20261026**（COVER）

## 禁项回执

- 未改 FROZEN 条款文件
- 未读价格/收益
- 未混叶38 / 未申 `.ok` / 未挂 QUIET
- 未动 nightly / leaf37 / trade_cal PIN
- 未动 `fund_basic_E` / 未碰 fund_portfolio 生产合并 / 未消费 `9e4359f9`
- 未 git commit；未推 Leo；`live=false`

下一跳：主裁 AI 可凭本回执 + `fund_basic_active_equity.parquet` 重跑两份 FROZEN 文末「计数附录」（仍禁读收益）。
