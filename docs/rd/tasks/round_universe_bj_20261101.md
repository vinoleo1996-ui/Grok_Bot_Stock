# 不打分名单卡在哪一行（2026-11-01）

岗位：算法 / 股票池。只读代码和文档。没有改选股代码，没有改三份实验设计，没有改 `docs/rd/messages.jsonl`，没有改 `docs/RESEARCH_CONTINUITY.md`，没有跑回测或账户，没有把 `strategy_promotion_approved` 写成 true，没有重跑 2018-01-02 至 2024-05-31。

本轮只回答：下一张可引用的不打分名单规则卡在哪一行。用户不买北交所。代码序前 60 只作废。

## 1. 现状

书面上的不打分规则仍停在 `docs/rd/experiments/factors.md:11`：池内按代码稳定排序，取 Mandate 的 30 到 60 只，权重相等。这句还在。

执行已经拒绝这句。`research/rd_ablation_20261101.py:115` 的 `stable_book` 在 `:121` 直接 `raise ValueError`，文档字符串 `:116-119` 写明代码序会把位子给北交所，不能再当不打分结果。调用点是 `:201`（宽篮）和 `:220`（mid-large 成员）。这两行一执行就停，交不出持仓名单。

仍会把 `bj.` 收进名单的，是进 `stable_book` 之前的池，不是持仓裁剪：

- `research/rd_ablation_20261101.py:111`：`wide_pool` 在名次 3001 到 5000、且成交额不低于 `MIN_ADV` 时 `chosen.append(iid)`。`:101` 的排序键是成交额降序、代码只作并列打破。循环 `:105-111` 不看前缀。`:190-191` 只丢掉 `sh.510300`，`asset_type` 为 stock 或 equity_etf 的 `bj.` 会进成交额库。
- `quantlab/smallcap/universe.py:79`：`pool_on` 的绝对名次带是 `ordered.iloc[RANK_START - 1:RANK_END]`，`:82` 只再要求 `adv >= MIN_ADV`。函数本体没有 `startswith("bj.")`。`:10-13` 的注释说 `cap` 这一路不给没有流通市值的名字排名，并称北交所因此不进 `cap`；这是缺字段，不是按前缀剔除。`adv` 这一路只要有成交额就会进带。
- `scripts/extend_2018_band.py:72`：`liquidity_band` 同样 `chosen.append(symbol)`。`:56-70` 没有前缀条件。
- `quantlab/universe/d1_masks.py`：全文没有 `bj.`。`:108` 只保留 `stock` 与 `equity_etf`。`:528-538` 是上市满 120 日、非停牌、非 ST、可交易、U30、涨停不买、流通市值底部 30%。`:586` 把剩下的 `instrument_id` 原样作为成员。`:1-11` 与 `:619-633` 的步骤里没有北交所。
- `quantlab/smallcap/panel.py:97`：`code.startswith('bj.')` 用来补涨跌停价，不从池里删掉该代码。

`quantlab/broad.py:25` 有 `not code.startswith('bj.')`。`:29-36` 的 `top_pool` 取的是流通市值最大 1500 只，不是这三组对照，也不是 30–60 只的不打分取样。

## 2. 三组对照

书面规则在 `docs/rd/experiments/universe.md:11-13`。三组自己的条文都没有写剔除北交所。

| 组 | 条文 | 是否写明剔除北交所 |
| --- | --- | --- |
| 后排宽篮 | `universe.md:11`：60 日正成交额、先排名、第 3001 到第 5000 名，不足 3001 只当日不买 | 没有 |
| Mandate 中大盘 | `universe.md:12`：点名 `d1_masks.py` 的上市满 120 日、非 ST、20 日成交额中位数至少 3000 万元、剔除流通市值底部 30%，外加申万 `available_at` | 没有。清单停在这几项 |
| 纸面 mid-large | `universe.md:13`：路径字面量 `data/v2/universe/mid_large_members_pit.parquet`，表不在则该臂失败 | 没有 |

Mandate 正文已经有剔除句，但没有写进上面三行。`docs/v2/MANDATE_UNIFIED_STOCK_ETF_20261012_ZH.md:68` 是个股侧持股约 30–60。`:69` 是流动性 U30、上市至少 120 日、剔 ST / 退市整理 / 默认北交所。`docs/v2/QuantLab-MANDATE_V2.json:35-38` 的 `exchanges` 只有 SSE、SZSE。`:39` 是 `exclude_bse_default: true`。`quantlab/mandate_v2.py:270` 把该字段读进 `MandateMarketsV2`。全库 Python 里这个名字只出现在 `quantlab/mandate_v2.py:46` 和 `:270`，没有第二个调用方，也没有进入 `d1_masks` 或 `wide_pool`。

所以：三组对照的书面取样规则都还没有剔除北交所。第 2 组的名字叫 Mandate，容易当成已经继承第 69 行；第 12 行列出的过滤器没有这句，它指向的 `d1_masks.py:586` 也不按前缀丢 `bj.`。

## 3. 不打分取样

没有。

核对过、且对不上「不打分，又不是代码序，又落在 30–60 只」的现成规则：

- `factors.md:11` 落在 30–60，但是代码序。`:121` 拒绝执行它。
- `universe.md:11` 不是代码序，它是成交额名次带。带的宽度是第 3001 到第 5000 名，不是 30–60 只。`wide_pool`（`:95-112`）、`pool_on`（`:76-82`）、`liquidity_band`（`:56-73`）返回的都是这一带，不是 30–60 的持仓。
- `quantlab/smallcap/universe.py:32` 的 `HOLDINGS = 50` 在 30–60 里。`:120` 的 `select` 用的是财务档（`:14-16`、`:114-117`：净利润与市净率）再加种子打乱。这是打分，不是不打分。
- `scripts/stable_book.py:231` 的 `select_liquid_sleeve` 注释写没有打分。`:49` 的 `HOLD_B = 15`，袖套只数 `:48` 为 5，单袖套大小是 15//5。整条腿不是 30–60。
- `scripts/full_pool.py:2-6` 与 `:54` 的 `select_full_pool` 固定 50 只，按流动性名次间隔抽，文件头写明不是按代码字母序。`:2` 同时写明不再使用第 3001 到第 5000 名。`universe.md` 三组没有引用这个函数。`:54-80` 的函数本体也不看 `bj.`。不把它当成三组里的下一条可引用规则，也不另写一条收益规则。

因此，下一张可引用的不打分、非代码序、30–60 只名单：没有。

## 4. 下一张账缺的那一句

缺的不是行情。

缺的是 `docs/rd/experiments/universe.md:11` 里还没有的那一句：后排宽篮在名次带里剔除北交所，并且用一条不是代码序的规则收到约 30–60 只。第 11 行现在只有「60 日正成交额、先排名、第 3001 到第 5000 名，不足 3001 只当日不买」。

已经写在别处、但没有接到这句上的，是 `docs/v2/MANDATE_UNIFIED_STOCK_ETF_20261012_ZH.md:69` 的「默认北交所」，以及同文件 `:68` 的「持股约 30–60」。`:69` 没有取样次序。`factors.md:11` 有 30–60 的只数，次序仍是代码稳定排序，`research/rd_ablation_20261101.py:121` 已经拒绝。不能用第 11 行的代码序顶上，也不能把第 3001–5000 名整段当成 30–60 的持仓。

`quantlab/mandate_v2.py:270` 读到了 `exclude_bse_default`，没有名单函数使用它。所以缺的是把第 69 行接到 `universe.md:11` 的取样句，不是缺一张行情表。本备忘录不补这句的排序公式。

## 5. 结论与行号

1. 不打分的书面定义仍是代码序：`docs/rd/experiments/factors.md:11`。
2. 代码序持仓已被拒绝：`research/rd_ablation_20261101.py:121`。调用：`:201`、`:220`。
3. 仍会选出 `bj.` 的行：`research/rd_ablation_20261101.py:111`。同形态：`quantlab/smallcap/universe.py:79`、`scripts/extend_2018_band.py:72`。D1 成员不剔除：`quantlab/universe/d1_masks.py:108`、`:586`。
4. 三组书面规则都没有剔除北交所：`docs/rd/experiments/universe.md:11`、`:12`、`:13`。Mandate 有这句但未进入三组：`docs/v2/MANDATE_UNIFIED_STOCK_ETF_20261012_ZH.md:69`。字段只被读入：`quantlab/mandate_v2.py:270`。
5. 非代码序且 30–60 的不打分取样：没有。
6. 下一张可引用账缺的是 `docs/rd/experiments/universe.md:11` 里承接第 69 行、且不是代码序的那一句，不是缺行情。

指定段落均已读到。没有「未读到」的必读行。
