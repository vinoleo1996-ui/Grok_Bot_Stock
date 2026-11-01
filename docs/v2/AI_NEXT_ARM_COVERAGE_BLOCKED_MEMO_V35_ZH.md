# V35 下一臂覆盖阻断备忘（无合格提案）

| 项 | 值 |
|---|---|
| 日期 | 2026-10-12 ET |
| 作者 | QuantLab AI |
| 代号 | **V35-COVERAGE-BLOCKED**（无 STOCK-* 提案号） |
| promotion_approved | **false** |
| 状态 | **不开跑**；不交 New Bot 冒烟批（无可批臂） |
| 不交 | Strategy |
| 不开 | v27；**不触碰 V31**（仍 research_observe） |
| 硬禁已遵守 | 披露日历/早披露 · 分红/DY · ocf·应计·质量 · seat · 解禁窗 · ETF tercile · 价叶 · 份额流 · LIMITUP · CB/金 · overnight* · ind_rel_overnight · V31 调样同构 |

窗：**X1 = 2015-06-01 → 2017-12-31**（与 V33/V34 一致）。计数为盘内真读，禁止伪造。

---

## 0. 结论

优先探坑与可替代非公开制度/事件维在 **完整 X1 ∩ 中大盘可交易密度** 上均不合格：要么 **X1=0 / 无表**，要么 **∩float top800 过稀**，要么 **塌入硬禁同构**（解禁 / 披露日历 / 调样）。**本轮不写 `AI_STOCK_ARM_PROPOSAL_V35_*`；等 Data 补齐有 PIT 的 X1 事件源后再提案。**

---

## 1. 优先探坑真计数

| # | 维 | 权威 path | X1 事件数 / 只 | ∩float top800 | 结论 |
|---|---|---|---|---|---|
| 1 | **回购公告/实施** | `data/v2/events/announcements_classified_pit.parquet`（event_type=buyback / subtype repurchase_*） | **0**（全表 ann_date **20180101→20240531**；buyback 全表 19423） | — | **X1 blocked**；cninfo `by_stock` 抽样 200 只 min_date 皆 ≥2018-01-02 |
| 2 | **股权质押·解质押** | （无盘内表） | **0** | — | 无 `pledge.parquet` / `tushare_raw/pledge`；`data/smallcap_info` 未落地；脚本 `smallcap_info.py`/`p2_event_flow.py` 有引用但数据缺 |
| 3a | **定增股份 float** | `data/v2/share_float/share_float_2015_2017.parquet` | float_date 窗 **12891** / 982 只 | （未作主推） | 中位 ann→float lag≈**370** 日 → **解禁窗硬禁**；非独立「增发实施」表 |
| 3b | **公开增发一般股份** | 同上 | float_date 窗 **384** / 274 只 | — | 中位 lag≈**1095** 日 → **解禁硬禁**；配股接口未入库（见 `ALPHA_DATA_REQUESTS_STATUS`） |
| 4a | **ST/*ST 戴帽** | `data/v2/st_events/st_events_from_namechange.parquet` | ann 窗 **119** / 116 只 | **≈3** | 全市场有数，**中大盘过稀**勿硬推 |
| 4b | **ST 摘帽** | 同上 | **104** / 102 只 | **≈3** | 同上 |
| 5 | **业绩预告/快报**（须≠V34 披露日历） | `scripts/collect_baostock_events.py` → 目标 `data/smallcap_events`；`financials_pit/research_em_yjbb_*` | **0** | — | smallcap_events **目录不存在**；em_yjbb seed 仅 **2024+**；`income.report_type` 抽样仅 **1**（无快报类型）；`disclosure_date` raw 自 **end_20180331** → X1=0 |

---

## 2. 其它已盘点非公开/制度事件（仍不合格）

| 维 | path | X1 | ∩top800 | 为何不提案 |
|---|---|---|---|---|
| 增减持 / 问询 | `announcements_classified_pit` | **0** | — | ann 自 2018（与先前盘点一致） |
| 停复牌 | `tushare_raw/suspend_d` | **0** | — | raw 自 **20180102** |
| 大宗折溢价 | — | — | — | **无稳 PIT 表**（V26 已标） |
| 审计非标 | `data/v2/audit/audit_opinion_pit_tushare.parquet` | **119** / 117 只 | **≈14** | 过稀；勿硬推中大盘 N=25 篮 |
| 退市整理期 | `namechange_all` | **3** / 3 | — | 退市路径，不宜主攻 |
| `index_member_events` | `data/v2/index_members/index_member_events.parquet` | **0** | — | ann 自 20180525；且 **V31 同构硬禁** |
| SW L1 再分类 | `sw_l1_pit/industry_members_sw_l1_tushare.parquet` | reclass IN **144** / 139 | **≈28** | 近 **V31 调样/被动再平衡同构**；`available_at≈in_date` 代理；free_hunt 表 NOT_PROMOTION；不主推 |
| 财报重述 rn≥2 | `financials_available_at_tushare` | **1550** / 488 | — | 多数 **lag=0** 同日重复行；且近 **V34 披露日历硬禁** |
| 个股两融明细 | `margin/margin_detail_daily_2018plus.parquet` | **0**（自 2018） | — | 交易所汇总 X1 有，但是市场层非个股事件袖套 |
| 北向个股 hk_hold | `northbound/hk_hold_*` | 日频约自 2018 | — | X1 个股层 blocked |

硬禁维（有 X1 也不开）：分红/DY（V33）、ocf/应计（V32）、seat（V29）、解禁 share_type（V30）、早披露日历（V34）、ETF tercile/价叶/份额流/LIMITUP/overnight/CB·金。

---

## 3. 解阻建议（给 Data；本执行器未拉数、未开跑）

按对 V35 机制匹配度排序（均须 **PIT available_at** + **完整 X1**）：

1. **回购**：Tushare `repurchase` 或 cninfo 标题回补 **2015-06→2017-12**，物化 PIT 后可重开「回购实施/进度短窗」。
2. **业绩预告/快报**：跑通 `scripts/collect_baostock_events.py`（或 Tushare forecast/express）落 `data/smallcap_events`；须能证明事件锚点 ≠ V34 `financials_available_at` 首次披露同构。
3. **股权质押**：落地 pledge 日频/事件表（解质押、质押率跳变）含 X1。
4. **增发/配股实施**（非解禁）：独立发行/配股实施公告表（勿复用 `share_float.float_date`）。
5. ST/审计非标：仅当中大盘事件密度显著上升才值得重估（当前 top800 个位数～十余）。

---

## 4. 约束回执

- **未开跑**任何 V35 冒烟 / 回测 / 调参  
- **未交 Strategy**  
- **未启 v27**  
- **未动 V31**（STOCK-INDEX-REBAL 仍仅 research_observe）  
- `promotion_approved=false`；控峰≤2GB（本备忘仅读计数）

**下一动作**：等 New Bot / Data 指定补源优先级；有 X1 非零且非硬禁的 PIT 事件表后再交 V35 半页提案。
