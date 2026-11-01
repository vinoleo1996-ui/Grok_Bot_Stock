# 全场幸存者偏差专项审计（Arch，2026-10-14）

- 时间：2026-10-14 ≈08:00 ET
- 约束：只读 + 只读 smoke；不改主干；`live=false`；`promotion_approved=false`
- 依据：`TEAM_STATE_latest.md`、`docs/v2/BETA_B1_SURVIVORSHIP_ZH.md`、`ARCH_INTERNAL_AUDIT_20261014_ZH.md`、`ARCH_UNIVERSE_ALLA_AUDIT_20261014_ZH.md`
- Smoke 产物：`output/loop/audit_smokes/survivorship_20261014.json`

## 0. 明确结论

**存在幸存者偏差相关机制与数据缺口；不能把 Beta B1 的「偏差约 0」当成全场结论。**

分层说明：

| 路径 | 是否存在幸存者偏差 | 量化量级（本轮 smoke） |
|---|---|---|
| 纸面 capacity_adv / B4（mid_large 静态锚 topN） | 持仓路径：**约 0**（与 Beta 一致：X2 内未持有退市股） | 持仓交叉 = 0 |
| FULLA_V1 / all_a 研究掩码 | **机制上已纳入**后来退市股（非「只用今天 L 列表回溯」） | 2023-12-29 in_universe ∩ 当时在市后来退市 = **61**；2024-06-28 = **28** |
| 主日线 `tushare_raw/daily/{date}` | **有缺口**：部分当时仍应交易的后来退市股缺 bar | 20240603 缺 15；20240628 缺 7（相对 last_trade≥当日） |
| 因子 IC / `leaf_selfcheck` forward return | **有标签丢弃机制**（`f.notna()`） | 日均即将退市样本小（h=20 约 0.6 只/日），但机制成立；单日截面均值差不稳定 |
| 主引擎 `execution.py:645` 个股退市 | **无 terminal mark**（ffill 最后收盘；等同 missing_bar_ret≈0） | 事件腿本轮未持有穿过 last_trade；若 4% 仓位触发 −50% terminal，单票约 −2pp NAV |
| D0 panel ∩ mid_large topN | 锚点 top300：**skipped_no_panel=0**；全局退市股无 panel **81/334** | 当前 topN 路径未触发；扩池/早年锚有风险 |

**一句话：Beta 只证明了「纸面大盘腿没拿到退市股」；没有证明「系统没有幸存者偏差」。FULLA 研究轨、日线缺口、IC dropna、引擎无退市清算，都是真实问题。**

---

## 1. 对 Beta B1「偏差约 0」的质疑

Beta 文档（`BETA_B1_SURVIVORSHIP_ZH.md`）做了：

1. 确认 Data 有退市表（339 只）；
2. 确认 mid_large @2024-06-28 锚点是 PIT；
3. 确认 capacity_adv top50 / 四个 BOOK **target_weights 未持有**退市股。

**不够的地方（本审计补充）：**

| 缺口 | 为何「持仓=0」推不出「偏差=0」 |
|---|---|
| 未查 FULLA / all_a | FULLA 掩码历史日明确包含后来退市股；事件腿 FULLA 权重**曾正权重持有**退市股（在 last_trade 之前卖出） |
| 未查截面/IC 标签 | `leaf_selfcheck_v3.py:98` `ok=f.notna()` 会丢掉无远期价格的票；退市附近 forward return 变 NaN → 截面被清洗 |
| 未查引擎退市清算 | `execution.py:645` 个股无 `terminal_price`（仅可转债有）；退市后 ffill 估值、收益≈0，而非 −50%/−100% |
| 未查主日线是否丢退市 bar | `tushare_raw/daily` 与 `delisted_daily` 在部分交易日对「仍应交易」的退市股同时缺失（多为停牌，但主库未与退市库合并） |
| 未查「今天 L 列表」拉数脚本 | 日线按 `trade_date` 拉全日截面（好）；财务等按 L+D（好）；但仍有独立 `pull_delisted*` 旁路，主路径未合并 |
| 宇宙固定大盘 | 「退市风险低」是选样结果，不是偏差为零的证明；扩到 FULLA/小盘后必须重做 |

**判定：Beta B1 对纸面 mid_large 持仓路径可用；作为全场结论 = 过度推广。负责：Beta（更正文档）+ Arch（本报告）。**

---

## 2. 逐项核查

### 2.1 股票池来源（是否用当前在市列表回溯）

| 组件 | 做法 | 判定 |
|---|---|---|
| FULLA_V1 / all_a 掩码 | `stock_basic` **L+D+P** 取 list_date；底座 = 历史 `tushare_raw/daily` 近 20 日有 bar | **非**「只用今天 L」；历史日含后来退市股 ✅ |
| mid_large_members_pit | 历史 `daily_basic_full` + namechange ST 区间 PIT | PIT ✅；但消费端常再套 **静态锚 2024-06-28 topN** |
| `select_mid_large_topn*` | 锚点一日市值排序 ∩ D0 panel | 非逐日全市场排序；有轻微前视（锚点之前）+ 固定生存集合（见 ARCH 内审 #8） |
| leaf_selfcheck / alpha_combo_marginal | `top_n=300` 静态 mid_large | 验收宇宙偏生存者/大盘 ✅问题 |
| hard_gates `ALLOWED_UNIVERSE` | 仍 mid_large_stock，无 fulla | 政策过时（见全 A 审计），非经典「L 列表回溯」 |

**FULLA 掩码 × 退市表（SSE/SZSE）快照：**

| 日期 | in_universe | 当时在市后来退市 | 进 base | 进 in_universe | 被 ST/停牌/ADV/年轻过滤掉 |
|---|---:|---:|---:|---:|---:|
| 2023-09-01 | 4844 | 101 | 101 | 62 | 39 |
| 2023-12-29 | 4944 | 100 | 100 | 61 | 39 |
| 2024-06-28 | 4950 | 84 | 74 | 28 | 46 |
| 2024-12-31 | 4961 | 48 | 48 | 23 | 25 |
| 2025-06-30 | 4946 | 34 | 30 | 8 | 22 |
| 2025-12-31 | 4968 | 19 | 19 | 2 | 17 |
| 2026-06-30 | 4953 | 7 | 7 | 0 | 7 |
| 2026-10-14 | 4993 | 0 | 0 | 0 | 0 |

→ FULLA **不是**幸存者池；过滤主要来自 ST/停牌/ADV（合理）。2024-06-28 base 比「当时在市后来退市」少 10 只 = 主日线缺口。

### 2.2 行情 / 财务数据

| 项 | 证据 | 判定 |
|---|---|---|
| 日线拉取 | `tier1_pull.cached_day(..., trade_date=d)` 按日拉全市场 | ✅ 非 L-only 遍历 |
| 主日线缺口 | 20240603：should-trade 后来退市 84，主库缺 15；20240628 缺 7 | **P1** 主库不完整；`delisted_daily` 同日也常缺（停牌）或未合并进主路径 |
| 退市旁路 | `data/v2/delisted/delisted_daily_from2015_tushare.parquet`（255 只、42 万行）；`scripts/pull_delisted.py` | 有数据，**未并入** `tushare_raw/daily` 供 FULLA/引擎 |
| daily_basic | 抽查 300630.SZ 有 1909 行至 last_trade | 覆盖退市股 ✅ |
| 财务 | `tier1_pull` balancesheet/cashflow 用 L+D | ✅ |
| stock_basic | L 5573 + D 339 已物化 | ✅ |
| 复权 | `data/v2/delisted/raw_adj_factor` 存在；主 `adj_factor/{day}` 目录本环境未见按日 shard | **待确认** 主引擎复权是否覆盖退市股 |

### 2.3 因子计算

| 项 | 位置 | 判定 |
|---|---|---|
| IC forward `ok=f.notna()` | `research/leaf_selfcheck_v3.py:95-99` | **P1** 退市/停牌导致无 h 日价格 → 丢出截面 |
| 残差/拼接 `dropna` | 多条 `g1g5_*_weights.py` 对 e/c/b 收益 `concat(...).dropna()` | 组合层对齐，可能间接丢掉稀疏票；**待确认**是否系统抬高 IC |
| 截面 rank 宇宙 | leaf_selfcheck 用静态 top300；FULLA 腿用掩码 | top300 路径偏生存者；FULLA 较好 |
| capacity_adv 脚本 | dropna/inner 计数为 0 | 该腿本身无明显「完整历史」苛求 |

**Smoke（IC 相关）：**

- 标签丢弃风险：FULLA in_universe 中，h=1/5/20/60 日内将 last_trade 的日均只数 ≈ 0.03 / 0.11 / 0.60 / 1.77（抽样日）。
- 2024-06-28 截面：28 只 later-delisted 的 20 日收益均值 **+3.4%**，80 只幸存者样本 **−3.3%**（含合并类退市，**不能**外推为「丢掉退市一定抬高 IC」；只证明截面构成会变）。
- **capacity_adv FULLA CAGR 含/不含退市：本轮未重跑 X2（可行但耗时长）→ 标「待确认」。** 持仓上 pos_weights 未正权重持有退市股，预期 CAGR 差接近 0。

### 2.4 回测 / 引擎

| 项 | 位置 | 判定 |
|---|---|---|
| 个股标记 | `quantlab/platform/execution.py:645` `Cm = close.ffill(limit_area="inside").ffill()` | **P1** 退市后仍按最后收盘计价；无强制清算 |
| 可转债 terminal | 同文件 ~1401+ `terminal_price` / `cb_basic.delist_date` | 仅 CB ✅；股票无对等逻辑 |
| 小盘袖套 | `v2_s2_book.py` 有 `delist_mark` −50%/−100% | 研究小盘有；主纸面/FULLA 未接 |
| 退市整理期 | Data `entered_delisting_period` 在 ref 表；引擎未按整理期特殊处理 | **P2** 整理期流动性/涨跌停更严，未建模 |
| 长期停牌 | 停牌 close NaN → 不可买；ffill 估值 | 与内审一致；leaf_selfcheck `fillna(0)` 更糟（内审 #5） |
| 更名/代码变更 | ST 用 namechange 区间；未见统一 code map 合并历史代码 | **待确认**（T 前缀历史码如 T600018 等） |
| 吸收合并 | Beta 已指出合并类退市≠亏损事件；引擎仍无换股对价 | **P2** |

### 2.5 叶 / 纸面 / 闸门 / ST 过滤是否 PIT

| 项 | 判定 |
|---|---|
| ST 过滤 | FULLA/mid_large 均用 `st_events_from_namechange` 区间 + `name` 含 ST；抽查无「已摘帽仍 open-ended ST 名」卡死（stuck-ST candidates=0） | ✅ PIT |
| 停牌 | suspend_d 当日 S + 无 S-1 bar | ✅ |
| 纸面轨 | 仍 mid_large；双轨政策下可接受；**不是**「用今天成分回溯」 | 持仓幸存者风险低 |
| 叶验收 | 仍 top300 / 禁小盘硬闸（全 A 审计） | 宇宙偏小，退市暴露低，但与 Leo 全 A 口径不一致 |
| 事件腿 FULLA | 曾持有退市股，均在 last_trade **之前**减仓（最近 1 个交易日：002505） | 未触发 terminal；接近退市的流动性风险未入闸门 |

---

## 3. 问题清单（可派工）

| # | 级 | 文件:行 / 证据 | 影响 | 修复 | 负责 |
|---|---|---|---|---|---|
| S1 | **P1** | `execution.py:645`；个股无 `terminal_price`；内审 #12 升级 | 若持有至退市，回测少记大额亏损（ffill≈0） | Data 提供退市日/退市价；Eng 股票侧接 terminal（对齐 S2 `delist_mark` −50%/−100% 敏感） | **Eng**（主）/ **Data** |
| S2 | **P1** | `leaf_selfcheck_v3.py:95-99` `ok=f.notna()` | IC/分层在退市、停牌附近丢标签，截面被清洗 | 退市：用 last_trade→terminal 收益填标签；停牌：按规则延期或显式掩码，禁止静默 drop | **AI** / **Alpha** |
| S3 | **P1** | `tushare_raw/daily` 缺部分后来退市股 bar；FULLA base 依赖该目录 | 掩码/ADV 低估或漏票；研究不可复现官方全日截面 | 将 `delisted_daily` 合并进主日线或 FULLA `_daily()` 双源；缺口日报 | **Data** |
| S4 | **P1** | `BETA_B1_SURVIVORSHIP_ZH.md` 结论过度推广 | 团队误以为全场无偏差，FULLA/引擎风险被忽略 | 更正为「纸面 mid_large 持仓路径≈0」；引用本报告；补 FULLA/引擎/IC 三节 | **Beta** |
| S5 | **P1** | 静态锚 `select_mid_large_topn*(anchor=2024-06-28)` + leaf top300 | 非逐日全市场；锚点前轻微前视；固定生存子集 | 研究轨改 FULLA 逐日掩码；纸面按 HI_LIQ 月度/逐日 PIT | **AI** / **Strategy**（已在推 HI_LIQ） |
| S6 | **P2** | D0 panel：退市股 81/334 无 panel | 扩池或更早锚点时 `skipped_no_panel` 可能剔退市股 | 补退市 panel 或 FULLA 路径不依赖 D0 | **Data** / **AI** |
| S7 | **P2** | 退市整理期 / 吸收合并换股未建模 | 整理期交易规则与普通日不同；合并对价未入账 | 引擎增加整理期标志；合并事件表 | **Eng** / **Data** |
| S8 | **P2** | `leaf_selfcheck_common` 停牌 `fillna(0)`（内审 #5） | 抹掉停牌期涨跌，类幸存者 | 改 `close_to_close_returns` | **AI** |
| S9 | **P2** | hard_gates / 叶预注册仍 mid_large | 验收宇宙规避退市，掩盖 FULLA 真实风险 | 与全 A 审计一并改 | **AI** / **主 Agent** |
| S10 | **待确认** | 主路径 adj 是否覆盖退市股；代码更名映射；capacity_adv FULLA CAGR 含/不含退市重跑 | 可能影响复权收益与 IC | Data/Eng 抽查 adj；Strategy/Alpha 可选重跑对照 | **Data** / **Eng** / **Alpha** |

**无 P0：** 未发现「仅用 `list_status=L` 当前列表重建历史宇宙」的主干路径。FULLA/mid_large 构建本身是 PIT 取向。

---

## 4. Smoke 摘要

1. **FULLA 含退市股**：见 §2.1 表；2023 年日均 later-delisted 约占 in_universe **1.25%**（约 62 只）。
2. **主日线缺口**：`survivorship_20261014.json` → `main_daily_gaps`。
3. **纸面 capacity_adv**：正权重 ∩ 退市 = 0（确认 Beta 持仓结论）。
4. **FULLA capacity_adv**：universe 行含 76 只退市代码但 **target_weight 全 0**；pos_weights 无退市。
5. **FULLA 事件腿**：insider 5 / earnings 2 / insurer 2 只曾正权重；均 `after_last_trade=False`。
6. **IC 20d 单日对照**：later-delisted 均值未必更差（含合并）；**CAGR 差待确认**。
7. **ST PIT**：stuck-ST candidates = 0。

---

## 5. 与既有审计关系

- 升级内审 **#12**（execution ffill）为本报告 **S1 P1**（在 FULLA 可能持有退市股的前提下）。
- 全 A 审计：纸面未切 FULLA 反而**降低**了纸面退市暴露；研究轨切 FULLA 后**必须**上 S1–S3，否则偏差从「宇宙规避」变成「持有后不计损失」。

---

## 6. 建议下一步（不改主干，仅派工）

1. Beta 更正 B1 文档措辞（S4）。
2. Data：主日线∪delisted_daily 合并方案 + 缺口清单（S3）。
3. Eng：股票 terminal_price 设计（S1），对齐 S2 敏感度。
4. AI：IC 标签退市填充 + 自检停牌收益（S2/S8）；验收宇宙切 FULLA/HI_LIQ（S5/S9）。
5. Alpha：可选 smoke——capacity_adv FULLA 含/不含退市股的 X2 CAGR/MDD（S10）。

live=false；本轮只写文档 / TEAM_STATE / ql_bus alert。
