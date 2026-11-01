# 【FROZEN 2026-10-14 08:25:59 ET】G1G5 预注册：隔夜特质波动（g1g5_ashare_overnight_idio_ivol_v1，叶18）
起草/冻结：2026-10-14 08:25:59 ET。扫描：docs/v2/AI_LEAF18_CANDIDATE_SCAN_ZH.md（HARD PIVOT 修订版）。
状态：**FROZEN**。冻结前未读任何用于调参的收益结果。研究级；promotion_approved=false；live=false；禁 GP/高杠杆；不自跑 Book-Smoke。
**主 Agent 08:24**：本叶属 ② 隔夜-日内分解/特质波动；**非**卖方/合同/调研/金股/目标价。原 tech_qual_cert 已 ABORTED。

## 机制与谁付钱（who_pays）
A 股日收益可分解为**隔夜**（`open/pre_close−1`）与**日内**（`close/open−1`）。隔夜承载收盘后信息与流动性冲击；高**特质隔夜波动**名称吸引彩票型/注意力资金并索取溢价。付钱的是追高隔夜噪声的交易者；**低特质隔夜波动**名称被忽视，随后获得补偿。本叶主 α = 低隔夜特质波动（慢，20 日），不是动量、不是 ADV、不是卖方、不是财报事件。

## 双宇宙（看结果前同时冻结）
| 口径 | 掩码 | 角色 | 行业帽 |
|---|---|---|---|
| **HI_LIQ_V1.1**（主） | `output/strategy_hiliq/universe_mask_hiliq_v1.parquet` | 主报密封满窗 + X2 | SW L1 ≤25% |
| **FULLA_V1**（研究对照） | `output/strategy_fulla/universe_mask_fulla_v1.parquet` | X2 对照；密封仅 2023-09→2024-05 重叠 | SW L1 ≤28% |

## 事前规则（冻结后不调）
1. **隔夜收益**：`r_on = open/pre_close − 1`；缺 open/pre_close 或 pre_close≤0 → 当日该票无效。
2. **日内收益**（仅快门辅助，不入 base-α）：`r_in = close/open − 1`。
3. **特质化**：在当日可交易池内，对 `r_on` 截面回归 **SW L1 dummy + log(流通市值)**，取残差 `ε_on`（名过少时仅行业 demean）。
4. **慢 base-α（20 日）**：`ivol = std(ε_on, 20 sessions)`；需要至少 15 个有效残差；**α_raw = −ivol**（低波动 → 高 α）。分域（流通市值 P70/P90：小微/中小盘/大盘）内 rank→[-1,1]；再对行业+log 市值残差一次，得 base-α。
5. **快 trade-gate（1–3 日，不入 α）**：若近 1–3 日 `ε_on` 的最小值落在当日池内 ε_on 的最低 5%（极端隔夜左尾）→ gate=0，禁止开仓/剔除评价权重；否则 gate=1。**禁止**与 base-α 加权合成。
6. **再平衡**：每 **5** 个交易日按当日 base-α 重算评价权重；持有至下一再平衡日。
7. **评价权重约束**：每名 ≤4%、≤20 名；行业帽见上表；余额 510300；硬排除 600519/002371；只在 gate=1 的票中按 α 降序取。
8. **窗口**：密封 2018-01-02→2024-05-31（HI_LIQ 满窗；FULLA 重叠段）；X2 2024-06-03→2026-10-09。AUM 60万/100万。年化 **244 主 / 252 对照**。
9. **主交付**：日度 base-α 向量（instrument→alpha）；不是 Top-N 名单。
10. **数据源**：`data/v2/tushare_raw/daily`（OHLC）；流通市值 PIT；SW L1 PIT。**不用**分钟线、卖方、合同、调研。

## 硬闸（读收益前写死）
1. Jaccard vs capacity_adv、earnings_event、equity_incentive、report_rc_allup、analyst_recoverage、insider_increase、tp_rerate、broker_gold_new、major_contract_growth、accrual_quality：任一日 ≥0.7 → 同构硬拒。
2. ρ_excess vs 上述任一 >0.5 → 只作过滤，不开主叶。
3. 可交易：双边换手 >20%/日，或成本拖累（17.5bp/单位换手）> 毛超额一半 → 不可交易。
4. 衰减门 v1.1 非 KEEP → 不过。
5. Gate A：ρ vs capacity_adv <0.5 且残差 α>0；Gate B：cap80+叶20 两档净 CAGR 均高于 capacity_adv。
6. GATE_V3：MDD≤25% 最大化 CAGR（另报 ≤15%）。
7. **砍线**：密封+X2、60万+100万均报；**跑不赢主干即砍**。
8. 峰值 RSS ≤1.5GB；CMC vs B4 必报；前视检查必报。
9. 密封仅描述性；live/promotion=false。

## 计数/覆盖闸（冻结后、读收益前）
- HI_LIQ：X2 与密封各自 **median 日可算 ivol 名数 ≥200** 且 **≥80% 交易日 ≥200** → 过闸。
- FULLA：X2 **median ≥500** 且 **≥80% 日 ≥500** → 过闸（对照）。
阈值不因结果调整。

## 失败条件
覆盖闸失败；同构硬拒；ρ>0.5；不可交易；衰减非 KEEP；Gate A/B/GATE_V3 不过；跑不赢主干 → WATCH/DONE_FAIL，不派 Book-Smoke。

## FROZEN
- 时间：2026-10-14 08:25:59 ET。
- 覆盖脚本：`research/g1g5_overnight_idio_ivol_coverage.py`（冻结时 sha 见同目录 .sha256 / 计数附录）。
- 方向写死为 **低特质隔夜波动优先（α=−ivol）**；冻结前未用收益调方向。
- Arch TODO（不改 leaf_selfcheck_v3，不阻塞）：退市终值；验收宇宙切 FULLA/HI_LIQ。


## 覆盖附录（2026-10-14 08:27:59 ET；只覆盖计数，未读收益/未调方向）
脚本 sha256 c5ad2caf7922c97625dc8c30cd747d016b38020e45198032599e57e17b5093f2。结果 \`output/ai_factory/overnight_idio_ivol_coverage_20261014.json\`。

| 窗 | median pool | median 可算 ivol | 日≥200 / ≥500 占比 | 闸 |
|---|---|---|---|---|
| HILIQ_sealed | 1797 | 1754 | 0.985 / 0.981 | PASS |
| HILIQ_x2 | 3172 | 3075 | 0.967 / 0.967 | PASS |
| FULLA_x2 | 4960 | 4954 | 0.967 / 0.967 | PASS |
| FULLA_sealed_overlap | 4937 | 4921 | 0.893 / 0.893 | PASS |

**HI_LIQ 与 FULLA 覆盖闸通过 → 进入 α 构建与自检。方向仍为 α=−ivol；阈值未改。**
