# 【FROZEN】叶 α 衰减闸门预注册（ALPHA_DECAY_GATE v1，研究级）
- 起草/冻结：2026-10-14 ~05:47 ET（盒子 CST 17:47）。**本文件写成并记 sha256 之后才运行任何衰减计算**；冻结前未读任何叶的滚动 α 结果。冻结后规则不调，任何修改须另立 v2 并重报尝试数。
- 授权来源：New Bot 转述 Leo 已批架构评审 Top2。研究级；promotion_approved=false；live=false；禁 GP/小盘/高杠杆；不派烟测；不自动改任何纸面状态。
- 实现：research/alpha_decay_gate.py（本预注册之后编写，只实现下列规则）。

## 1. 收益口径
- 毛日收益：目标权重 shift(1) × 复权日收益（个股 research/adj_price.py hfq；510300 用 data/v2/etf/etf_daily_adj.parquet close_hfq），与 verify_* 脚本相同。
- 双边日换手 TO_t = Σ|w_t − w_{t−1}|（含 510300 腿）。
- 净日收益 = 毛 − 0.00175 × TO_t（17.5bp/单位换手）。
- 510300 基准净值：买入持有，仅首日扣一次 17.5bp。

## 2. 残差 α（只用过去数据）
- 在评估日 t，取截至 t（含）的最近 252 个交易日净日收益，对 510300 日收益做 OLS（截距+β），残差 α_t = 截距×252。
- 说明：现有 verify 脚本的残差只对 510300 去 β，未做行业/市值残差；本 v1 与之一致（单因子），不另造行业/市值因子。
- 不足 252 日时：≥126 日用全部已有历史并标 SHORT_HISTORY；<126 日不出 α，标 INSUFFICIENT。

## 3. 季度测量
- 季度点 = 每个日历季度最后一个交易日上的 α_t（2024Q4 起只要该点有 ≥126 日历史）；评估日 = 权重文件最后一个交易日（作为“最新”点，若非季末则作为额外最新点计入序列末尾）。
- 「下降」= 本点 α < 上一点 α（严格小于）。连续 N=3 次下降需要 4 个点。

## 4. 硬门（基于最新 252 日窗，不足则全部已有历史）
- H1 换手：窗口内平均双边日换手 > 20% → 失败。
- H2 净收益：窗口内净 CAGR ≤ 510300 买入持有净 CAGR（同窗）→ 失败。

## 5. 结果标签
- **DECAY_DOWNGRADE**：最新 α_t < 0；或季度 α 连续 3 次下降；或 H1/H2 任一失败。
- **DECAY_WATCH**：未触发上条，但（最新 α_t ∈ [0, +1%/年)）或（季度 α 连续 2 次下降）。
- **KEEP**：以上皆否。
- **INSUFFICIENT**：历史 <126 日或找不到权重文件 → 不改任何东西。

## 6. 与现有裁定的合并（只降不升）
- PAPER_ACTIVE_CONFIRMED（capacity_adv）及 B4 纸面轨：**永不自动改**；DECAY_DOWNGRADE/DECAY_WATCH 只写 flag_for_leo=true。
- BOOK_SMOKE_PASS / RESEARCH_CANDIDATE / RESEARCH_ACCEPT：DECAY_DOWNGRADE → effective_label=WATCH（原 verdict 保留）；DECAY_WATCH → 标签不变，加注。
- WATCH / DONE_FAIL / REJECT：不变（闸门不能上调）；只记录 decay_gate 字段。
- KEEP 不会上调任何标签。

## 7. 权重文件选取（事前固定）
- capacity_adv：纸面 output/ai_factory/g1g5_capacity_adv_daily_weights_paper_20261013_r2.parquet。
- 其余叶：output/ai_factory 中该机制名、非 paper/combo/conc 的**最新时间戳**文件；无文件 → INSUFFICIENT。
- B4：不在 alpha_labels 叶表中；本 v1 不计算，只记“未评估/仅可 flag”。

## 8. 尝试数
- 规则集 1 套，参数（252 日、N=3、20%、17.5bp、+1% 预警线）全部事前固定，**0 次调参**；尝试数 = 1 套规则 × 被评估叶数（实际数在重判回执报告）。
