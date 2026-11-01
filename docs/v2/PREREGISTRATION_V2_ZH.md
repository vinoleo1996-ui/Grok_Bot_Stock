# QuantLab V2 预注册（策略层）

- 状态：研究级 · `promotion_approved=false`
- 写入时间：2026-10-10 22:34 ET（Leo 在主聊天确认四条拍板后落盘）
- 来源：`QuantLab-V2_REBUILD_PLAN_ZH.md` 第 5 节建议项 1–4，Leo 于 2026-10-10 22:34 ET 全部确认
- 本文件只记录策略晋升相关的预注册约束；数据层验收见 `docs/v2/PROMOTION_ACCEPTANCE.md`
- **未改** `docs/v2/QuantLab-MANDATE_V2.json` / `QuantLab-MANDATE_V2.json`；第 2 条仅登记为晋升前待修订项

---

## Leo 拍板（2026-10-10 22:34 ET）

### 1. 实盘与研究名义本金

- **实盘账户 ¥60 万**：小盘 β 袖套持有 **20–30 只**，并为每只设**最低权重**（避免 50 只等权时单票名义过低、最低佣金占比过高）。
- **研究口径名义本金 ¥500 万**（容量曲线、冲击与对照一律按此报，另可附 50 万 / 200 万 / 1000 万敏感性）。
- 归因：Leo · 2026-10-10 22:34 ET

### 2. Mandate 修订（晋升前必须完成；当前 JSON 未改）

晋升前须修订 Mandate，使小盘 β 袖套：

- 使用流通市值排名带 **3001–5000**；
- 施加**风险剔除**（含 ST、低价、审计非标等，细则以修订后 Mandate 为准）；
- 袖套权重**上限 20%**。

研究阶段可按上述口径跑对照，但 **Mandate JSON 保持不动**，直至晋升前正式修订。  
归因：Leo · 2026-10-10 22:34 ET · 状态：`pending_mandate_amendment`

### 3. 封存与样本分段

| 区间 | 用途 |
|---|---|
| 2018 – 2024-05 | 开发与验证 |
| 2024-06 – 写入当日（探索窗） | **仅探索**，不作最终晋升证据 |
| 2026-11 起 | **前向纸面交易封存**，持续 **6–12 个月**；封存段只在最终晋升时使用一次 |

归因：Leo · 2026-10-10 22:34 ET

### 4. 「证据不足」时的处置与 15% 目标

- 若块 bootstrap / DSR 等判定为**证据不足**，但策略仍**跑赢两个静态小盘对照臂**（方案中的 C2、C3），且**回撤可控**，则可进入**小资金前向纸面交易**，**不直接上实盘**。
- **15% 年化**只作报告考核指标，**不作晋升硬门槛**。

归因：Leo · 2026-10-10 22:34 ET

---

## 与试验台账的关系

- 全局试验计数仍走 `docs/trial_ledger.csv`（`quantlab/research_trials.py`）。
- 本文件约束 V2 组合改造与晋升判定；各因子/事件族另写独立预注册并计入试验次数。
- 策略层晋升台账见 `output/promotion_ledger.json`。

---

## 描述性观察（不作晋升证据）

> **警告**：以下各行仅为研究描述，**不是**晋升证据；`promotion_approved` 仍为 `false`。不得据此上线或修改 Mandate。

### cb10 BOOK（mbook L≤1.5，全规则 CB1，可转债权重 10%）— 2026-10-11 23:21 ET

- 来源：`output/strategy_mbook_L15_cb1full/compare_table.json` → `BOOK_by_cb_weight.cb10`
- 配比：MA-RP ≈51.4% · CB1（全规则）10% · X-D ≈38.6%（剩余按 4:3）
- 窗口（仅探索；密封窗未用于判定）：

| 窗口 | CAGR | 最大回撤 | 夏普 |
|---|---|---|---|
| X1 2015-06→2017-12 | 4.03% | -18.3% | 0.34 |
| X2 2024-06→2026-10-09 | 14.12% | -8.4% | 1.21 |

- 背景：CB1 全规则在探索窗历史上**未过线**（见 `docs/v2/CB_PREREG.md` §12–13）；本行只登记 mbook 敏感性结果。
- 台账条目：`output/promotion_ledger.json` → `descriptive_research_rows[id=descriptive_cb10_BOOK_L15_fullrules]`

### CIB2-EW（全规则 CB2 + IC≤0.5 + 压舱等权）— 2026-10-11T23:46:09-04:00 · 仅描述

- **不作晋升证据**：探索窗过线 + Strategy 两引擎对账通过；`promotion_approved=false`；不得据此上线或修改 Mandate。
- 来源：`output/strategy_futures_recon/cib2_ew/`（`results.json` / `metrics_zh.csv`）
- 预注册：`docs/v2/V3_CIB2_PREREG.md`
- 构成：全规则 CB2 + IC 名义≤0.5 + 压舱资金，等权；**无小盘**
- 窗口（仅探索；密封窗不作晋升判定）：

| 窗口 | CAGR | 最大回撤 | 夏普 |
|---|---|---|---|
| X1 2015-06→2017-12 | 2.30% | −20.78% | 0.23 |
| X2 2024-06→2026-10-09 | 14.27% | −7.66% | 1.14 |

- 对账：引擎 A / B / Beta 一致（`pass_nav=true`，`pass_metrics=true`）。
- 台账条目：`output/promotion_ledger.json` → `descriptive_research_rows[id=descriptive_CIB2_EW_reconcile]`

### TCarry-G（国债期货 carry + 黄金，L≤1.5，无股指）— 2026-10-12T00:15:30-04:00 · fail_explore · 无交接

- **不作晋升证据**：探索不通过；`promotion_approved=false`；不得据此上线或修改 Mandate。
- 来源：`output/v3/tcarry_g/`（`results.json` / `SHORT_ZH.md`）
- 预注册：`docs/v2/V3_TCARRY_G_PREREG.md`
- 判定：X2 CAGR 8.5% < 12%；未抬杠杆；可作压舱零件，**不交接** Strategy（无 `handoff_strategy/tcarry_g`）。
- 窗口（仅探索；密封只描述）：

| 窗口 | CAGR | 最大回撤 | 夏普 |
|---|---|---|---|
| X1 2015-06→2017-12 | 5.2% | −7.4% | 0.82 |
| X2 2024-06→2026-10-09 | 8.5% | −2.9% | 2.06 |

- 台账：`docs/trial_ledger.csv` → `tcarry_g/TCarry-G`（Beta）+ `TCarry-G_strategy_note`（Strategy）；`output/promotion_ledger.json` → `descriptive_TCarry_G_fail_explore`
- 禁小盘。

### CIB2-NOIC（全规则 CB2 + 债金压舱，无 IC）AUM 60万/100万 — 2026-10-12T00:15:30-04:00 · fail_explore · 无交接

- **不作晋升证据**：两档 AUM 探索均不通过；`promotion_approved=false`。
- 来源：`output/v3/cib2_noic/`（`results.json` / `SHORT_ZH.md`）
- 预注册：`docs/v2/V3_CIB2_NOIC_PREREG.md`
- 构成：CB2 50% + 511010/518880 逆波压舱 50%；**无 IC、无 510500、无小盘**。
- 主结论口径：**AUM=60万 / 100万**；大资金（5M）仅附录。
- 判定：X2≈8% < 12%；**无交接**（无 `handoff_strategy/cib2_noic`）。
- 摘要：

| AUM | X1 | X2 |
|---|---|---|
| 60万 | 3.2% / −6.4% / 0.52 | 8.0% / −7.0% / 1.11 |
| 100万 | 3.2% / −6.5% / 0.51 | 8.1% / −7.2% / 1.12 |

- 台账：`docs/trial_ledger.csv` → `CIB2-NOIC_600000` / `CIB2-NOIC_1000000` + `CIB2-NOIC_strategy_note`；`descriptive_CIB2_NOIC_fail_explore`

### CB3-IC（条款事件转债 + IC≤0.5 + 压舱）— 2026-10-12T00:15:30-04:00 · fail_explore · 无交接

- **不作晋升证据**：两臂探索均不通过；`promotion_approved=false`。
- 来源：`output/v3/cb3ic/`（`results_CB3IC-RP_CB3IC-EW.json` / `SHORT_ZH.md`）
- 预注册：`docs/v2/V3_CB3_IC_PREREG.md`
- 判定：X2 CAGR 均 <12%；事件腿 X2 负贡献；与 CB2 转债相关 0.86；**无交接**（`handoff_strategy/cb3ic/` 为空目录，不是有效交接包）。
- 摘要：

| 臂 | X1 | X2 |
|---|---|---|
| CB3IC-RP | 1.0% / −14.3% / 0.17 | 7.7% / −7.7% / 1.51 |
| CB3IC-EW | 2.4% / −21.1% / 0.25 | 6.8% / −12.4% / 0.59 |

- 台账：`docs/trial_ledger.csv` → `CB3IC-RP` / `CB3IC-EW` + `CB3-IC_strategy_note`；`descriptive_CB3_IC_fail_explore`
- 禁小盘。

### CB3-BALLAST（条款事件转债 + 债金压舱，无 IC）AUM 60万/100万 — 2026-10-12T00:58:37-04:00 · fail_explore · 无交接

- **不作晋升证据**：两档 AUM 探索均不通过（X2≈0.5%）；`promotion_approved=false`。
- 来源：`output/v3/cb3_ballast/`（`results.json` / `SHORT_ZH.md`）
- 预注册：`docs/v2/V3_CB3_BALLAST_PREREG.md`
- 构成：条款事件转债 + 511010/518880 债金压舱；**无 IC、无 510500、无小盘**。
- 主结论口径：**AUM=60万 / 100万**；大资金仅附录。
- 判定：X2≈0.5% < 12%；**无交接**（无 `handoff_strategy/cb3_ballast`）。
- 摘要：

| AUM | X1 | X2 |
|---|---|---|
| 60万 | 2.4% / −5.0% / 0.70 | 0.6% / −10.4% / 0.11 |
| 100万 | 2.4% / −5.0% / 0.70 | 0.5% / −10.4% / 0.10 |

- 台账：`docs/trial_ledger.csv` → `CB3-BALLAST_600000` / `CB3-BALLAST_1000000` + `CB3-BALLAST_strategy_note`；`output/promotion_ledger.json` → `descriptive_CB3_BALLAST_fail_explore`
- 禁小盘。继续盯 `output/v3/handoff_strategy/`。

### SHARE-AC（510300 份额流反拥挤调 β + 压舱）AUM 60万/100万 — 2026-10-12T00:59:40-04:00 · fail_explore · 无交接

- **不作晋升证据**：两档 AUM 探索均不通过（X2≈6.6%，弱于静态 60/40；X1≈−2% / MDD≈−28%）；`promotion_approved=false`。
- 来源：`output/v3/share_ac/`（`results.json` / `SHORT_ZH.md`）
- 预注册：`docs/v2/V3_SHARE_AC_PREREG.md`
- 构成：510300 份额流反拥挤调 β + 511010/518880 债金压舱；**无 IC、无小盘**。
- 主结论口径：**AUM=60万 / 100万**。
- 判定：X2≈6.6% < 12% 且弱于静态 60/40（Δ≈−2.7pct）；X1 MDD≈−28%>25%、夏普<0；**无交接**（无 `handoff_strategy/share_ac`）。
- 摘要：

| AUM | X1 | X2 | vs静态 X2 Δ年化 |
|---|---|---|---|
| 60万 | −2.0% / −28.2% / −0.03 | 6.6% / −8.8% / 0.65 | ≈−2.6pct |
| 100万 | −2.0% / −28.2% / −0.04 | 6.6% / −8.8% / 0.65 | ≈−2.7pct |

- 台账：`docs/trial_ledger.csv` → `SHARE-AC_600000` / `SHARE-AC_1000000` + `SHARE-AC_strategy_note`；`output/promotion_ledger.json` → `descriptive_SHARE_AC_fail_explore`
- 禁小盘。继续盯 `output/v3/handoff_strategy/`。

### CB-DUAL（CB1 25%+CB2 25%+压舱 50%，无 IC）AUM 60万/100万 — 2026-10-12T01:01:20-04:00 · fail_explore · 无交接

- **不作晋升证据**：两档 AUM 探索均不通过（X2≈10.5%；X1 Sharpe<0；CB1↔CB2相关≈0.95）；`promotion_approved=false`。
- 来源：`output/v3/cb_dual/`（`results.json` / `SHORT_ZH.md`）
- 预注册：`docs/v2/V3_CB_DUAL_PREREG.md`
- 构成：全规则 CB1 25% + 全规则 CB2 25% + 511010/518880 债金压舱 50%；**无 IC、无小盘**。
- 主结论口径：**AUM=60万 / 100万**。
- 判定：X2≈10.5% < 12%；X1 夏普 < 0；CB1↔CB2 日收益相关 ≈0.95（几乎无分散）；**无交接**（无 `handoff_strategy/cb_dual`）。
- 摘要：

| AUM | X1 | X2 | CB1↔CB2 相关 |
|---|---|---|---|
| 60万 | −3.8% / −14.4% / −0.41 | 10.5% / −4.8% / 1.41 | ≈0.95 |
| 100万 | −3.9% / −14.5% / −0.42 | 10.6% / −4.9% / 1.38 | ≈0.95 |

- 台账：`docs/trial_ledger.csv` → `CB-DUAL_600000` / `CB-DUAL_1000000` + `CB-DUAL_strategy_note`；`output/promotion_ledger.json` → `descriptive_CB_DUAL_fail_explore`
- 禁小盘。继续盯 `output/v3/handoff_strategy/`。

### CB2-DYN（全规则 CB2 + 动态逆波压舱，无 IC）AUM 60万/100万 — 2026-10-12T01:03:18-04:00 · fail_explore · 无交接

- **不作晋升证据**：两档 AUM 探索均不通过（X2≈6.8–7.0%）；`promotion_approved=false`。
- 来源：`output/v3/cb2_dyn/`（`results.json` / `SHORT_ZH.md`）
- 预注册：`docs/v2/V3_CB2_DYN_PREREG.md`
- 构成：全规则 CB2 + 动态逆波压舱（511010/518880）；**无 IC、无小盘**。
- 主结论口径：**AUM=60万 / 100万**。
- 判定：X2≈6.8–7.0% < 12%；\(w_{cb}\) 在 X2 钉在下限 0.30；**无交接**（无 `handoff_strategy/cb2_dyn`）。
- 摘要：

| AUM | X1 | X2 |
|---|---|---|
| 60万 | 3.1% / −5.6% / 0.67 | 6.8% / −3.9% / 1.50 |
| 100万 | 3.1% / −5.5% / 0.67 | 7.0% / −4.1% / 1.53 |

- 台账：`docs/trial_ledger.csv` → `CB2-DYN_600000` / `CB2-DYN_1000000` + `CB2-DYN_strategy_note`；`output/promotion_ledger.json` → `descriptive_CB2_DYN_fail_explore`
- 禁小盘。继续盯 `output/v3/handoff_strategy/`。

### CB-MATPREM（转股期×期限[1,3]年低溢价+压舱，无 IC）AUM 60万/100万 — 2026-10-12T01:07:13-04:00 · pass_explore + Strategy两引擎对账 · 有交接

- **不作晋升证据**：探索通过且 Strategy 两引擎对账与 Beta 一致；`promotion_approved=false`。
- 来源：`output/v3/cb_matprem/`（Beta）+ `output/strategy_recon/cb_matprem/`（Strategy 对账）
- 预注册：`docs/v2/V3_CB_MATPREM_PREREG.md`
- 构成：转股期 ∩ 剩余期限[1,3]年 × 低溢价 50% + 511010/518880 压舱 50%；**无 IC、无小盘**。
- 主结论口径：**AUM=60万 / 100万**。密封窗未作为新证据重跑。
- **X1 日历池极浅**（空仓日约 **81.7%**，日均 CB≈0.18）→ **X1 主要靠压舱**；前向纸面须盯池深。
- 判定：X2≈12.8–13.2%（落在 12–15%）；双窗 MDD≤25%、夏普>0；两引擎 vs Beta NAV 浮点噪声内一致；**有交接** `handoff_strategy/cb_matprem/`。
- 摘要：

| AUM | X1（年化/回撤/夏普） | X2 | 日历池空仓日（X1） |
|---|---|---|---|
| 60万 | 3.25% / −5.03% / 0.80 | 12.81% / −5.41% / 1.32 | ≈81.7% |
| 100万 | 3.17% / −5.04% / 0.78 | 13.22% / −5.42% / 1.33 | ≈81.7% |

- 台账：`docs/trial_ledger.csv` → `CB-MATPREM_600000` / `CB-MATPREM_1000000` + `CB-MATPREM_strategy_recon`；`output/promotion_ledger.json` → `descriptive_CB_MATPREM_explore_pass_recon`
- 禁小盘。继续盯 `output/v3/handoff_strategy/`。

### NAV-DISC（510300 折溢价反拥挤调 β + 压舱）AUM 60万/100万 — 2026-10-12T01:20:30-04:00 · fail_explore · 无交接

- **不作晋升证据**：Beta 探索不通过；`promotion_approved=false`。
- 来源：`output/v3/nav_disc/`（Beta）；**无** Strategy 交接包。
- 预注册：`docs/v2/V3_NAV_DISC_PREREG.md`
- 构成：510300 价/净值折溢价 z 调 β + 511010/518880 压舱；**无 IC、无期货、无小盘**；**≠ SHARE-AC**（非份额 Δ）。
- 主结论口径：**AUM=60万 / 100万**。密封窗仅描述。
- 判定：X1 MDD≈−28%>25%；X2≈5.8%<12% 且弱于静态60/40（Δ≈−3.5pct）→ **fail_explore**；**无交接**。
- 摘要：

| AUM | X1（年化/回撤/夏普） | X2 | vs 静态 X2 |
|---|---|---|---|
| 60万 | −1.3% / −28.2% / 0.00 | 5.8% / −9.4% / 0.56 | Δ≈−3.5pct |
| 100万 | −1.4% / −28.2% / −0.00 | 5.8% / −9.4% / 0.56 | Δ≈−3.5pct |

- 台账：`docs/trial_ledger.csv` → `NAV-DISC_600000` / `NAV-DISC_1000000` + `NAV-DISC_strategy_note`；`output/promotion_ledger.json` → `descriptive_NAV_DISC_fail_explore`
- 含宽基股腿 → **不进 NOIC 债金骨架**。禁小盘。继续盯 `output/v3/handoff_strategy/`。


### CB1-FLOOR（CB1 双低 ∩ 价∈[95,115] + 债金压舱，无 IC）AUM 60万/100万 — 2026-10-12T01:23:06-04:00 · fail_explore · 无交接

- **不作晋升证据**：Beta 探索不通过；`promotion_approved=false`。
- 来源：`output/v3/cb1_floor/`（Beta）；**无** Strategy 交接包。
- 预注册：`docs/v2/V3_CB1_FLOOR_PREREG.md`
- 构成：全规则 CB1 双低 ∩ 价∈[95,115] 50% + 511010/518880 债金压舱 50%；**无 IC、无小盘**。
- 主结论口径：**AUM=60万 / 100万**。密封窗仅描述。
- 判定：X2≈2.5% < 12%（价格带过滤后股性不足）；X1 池偏浅（空仓≈33%）→ **fail_explore**；**无交接**（无 `handoff_strategy/cb1_floor`）。
- 摘要：

| AUM | X1（年化/回撤/夏普） | X2 |
|---|---|---|
| 60万 | 1.8% / −6.9% / 0.44 | 2.5% / −15.3% / 0.36 |
| 100万 | 1.8% / −7.0% / 0.42 | 2.5% / −15.4% / 0.35 |

- 台账：`docs/trial_ledger.csv` → `CB1-FLOOR_600000` / `CB1-FLOOR_1000000` + `CB1-FLOOR_strategy_note`；`output/promotion_ledger.json` → `descriptive_CB1_FLOOR_fail_explore`
- 禁小盘。继续盯 `output/v3/handoff_strategy/`。


### LIQ-TV（55% 510300 + 时变货币/国债压舱）AUM 60万/100万 — 2026-10-12T01:24:01-04:00 · fail_explore · 无交接

- **不作晋升证据**：Beta 探索不通过；`promotion_approved=false`。
- 来源：`output/v3/liq_tv/`（Beta）；**无** Strategy 交接包。
- 预注册：`docs/v2/V3_LIQ_TV_PREREG.md`
- 构成：55% 510300 + 时变货币/国债压舱；**无 IC、无小盘**。
- 主结论口径：**AUM=60万 / 100万**。密封窗仅描述。
- 判定：X1 MDD≈−26%>25%、夏普<0；X2≈7.7%<12%，相对全国债压舱无增量 → **fail_explore**；**无交接**（无 `handoff_strategy/liq_tv`）。
- 摘要：

| AUM | X1（年化/回撤/夏普） | X2 | vs 全国债压舱 X2 |
|---|---|---|---|
| 60万 | −2.1% / −26.0% / −0.07 | 7.7% / −8.6% / 0.75 | 对照≈8.1%（无增量） |
| 100万 | −2.1% / −26.0% / −0.07 | 7.7% / −8.6% / 0.75 | 对照≈8.1%（无增量） |

- 台账：`docs/trial_ledger.csv` → `LIQ-TV_600000` / `LIQ-TV_1000000` + `LIQ-TV_strategy_note`；`output/promotion_ledger.json` → `descriptive_LIQ_TV_fail_explore`
- 禁小盘。继续盯 `output/v3/handoff_strategy/`。


### MIX-FROZEN（冻结 50/35/15 510300/511010/518880）AUM 60万/100万 — 2026-10-12T01:26:23-04:00 · fail_explore · 无交接

- **不作晋升证据**：Beta 探索不通过；`promotion_approved=false`。
- 来源：`output/v3/mix_frozen/`（Beta）；**无** Strategy 交接包。
- 预注册：`docs/v2/V3_MIX_FROZEN_PREREG.md`
- 构成：冻结 50% 510300 + 35% 511010 + 15% 518880；**无 IC、无小盘**。
- 主结论口径：**AUM=60万 / 100万**。密封窗仅描述。
- 判定：X1 Sharpe<0；X2≈10.8–10.9%<12%（虽相对静态60/40 有约 +1.5~2.3pct 年化增量）→ **fail_explore**；**无交接**（无 `handoff_strategy/mix_frozen`）。
- 摘要：

| AUM | X1（年化/回撤/夏普） | X2 | vs 静态60/40 X2 |
|---|---|---|---|
| 60万 | −1.2% / −23.6% / −0.02 | 10.8% / −8.2% / 0.99 | Δ≈+2.3pct（对照≈8.5%） |
| 100万 | −1.2% / −23.6% / −0.02 | 10.9% / −8.2% / 0.99 | Δ≈+2.3pct（对照≈8.5%） |

- 台账：`docs/trial_ledger.csv` → `MIX-FROZEN_600000` / `MIX-FROZEN_1000000` + `MIX-FROZEN_strategy_note`；`output/promotion_ledger.json` → `descriptive_MIX_FROZEN_fail_explore`
- 禁小盘。继续盯 `output/v3/handoff_strategy/`。未触碰 NOIC smoke。


### MP-NEAR（MATPREM变体 ytm[0.5,1.5]+低溢价top10+单券帽8%，无 IC）AUM 60万/100万 — 2026-10-12T01:31:04-04:00 · pass_explore + Strategy两引擎对账 · 有交接

- **不作晋升证据**：探索通过且 Strategy 两引擎对账与 Beta 一致；`promotion_approved=false`。
- 来源：`output/v3/mp_near/`（Beta）+ `output/strategy_recon/mp_near/`（Strategy 对账）
- 预注册：`docs/v2/V3_MP_NEAR_PREREG.md`
- 构成：转股期 ∩ ytm∈[0.5,1.5]年 × 低溢价 top10 + 单券帽 8%（差额进压舱）+ 511010/518880 压舱；**无 IC、无小盘**。母臂 = CB-MATPREM（[1,3]/top20/无帽）。
- 主结论口径：**AUM=60万 / 100万**。密封窗未作为新证据重跑。
- **X1 近端日历池 EMPTY**（空仓日 **100%**，日均 CB=0）→ **X1 纯压舱**；前向纸面须盯池深。
- 判定：X2≈14.5–14.8%（落在 12–15%）；双窗 MDD≤25%、夏普>0；两引擎 vs Beta NAV 浮点噪声内一致；**有交接** `handoff_strategy/mp_near/`。
- 相对母臂：X2 年化更高（~14.5–14.8% vs ~12.8–13.2%），回撤略深（~−7.6% vs ~−5.4%）。**MATPREM 仍为 pass 候选**；MP-NEAR 为额外 explore-pass。
- 摘要：

| AUM | X1（年化/回撤/夏普） | X2 | 日历池空仓日（X1） |
|---|---|---|---|
| 60万 | 2.71% / −5.03% / 0.80 | 14.50% / −7.57% / 1.27 | **100%（EMPTY）** |
| 100万 | 2.70% / −5.04% / 0.80 | 14.84% / −7.57% / 1.29 | **100%（EMPTY）** |

- 台账：`docs/trial_ledger.csv` → `MP-NEAR_600000` / `MP-NEAR_1000000` + `MP-NEAR_strategy_recon`；`output/promotion_ledger.json` → `descriptive_MP_NEAR_explore_pass_recon`
- 禁小盘。继续盯 `output/v3/handoff_strategy/`。

### CB-SIZEPREM（remain_size 20日收缩×低溢价秩和 Top15 + 压舱，无 ytm 日历）AUM 60万/100万 — 2026-10-12T01:35:55-04:00 · fail_explore · 无交接

- **不作晋升证据**：Beta 探索不通过；`promotion_approved=false`。
- 来源：`output/v3/cb_sizeprem/`（Beta）；**无** Strategy 交接包。
- 预注册：`docs/v2/V3_CB_SIZEPREM_PREREG.md`
- 构成：remain_size 20日收缩 × 低溢价秩和 Top15 + 债金压舱；**无 ytm 日历**；**无 IC、无小盘**。
- 主结论口径：**AUM=60万 / 100万**。密封窗仅描述。
- 判定：X2≈15.8–16.2% 且 MDD≈−8% 过线，但 **X1 Sharpe&lt;0**（≈−0.41/−0.42）→ **fail_explore**；**无交接**（无 `handoff_strategy/cb_sizeprem`）。
- 摘要：

| AUM | X1（年化/回撤/夏普） | X2 |
|---|---|---|
| 60万 | −3.8% / −11.5% / -0.41 | 15.8% / −8.1% / 1.27 |
| 100万 | −3.9% / −11.6% / -0.42 | 16.2% / −8.2% / 1.28 |

- 台账：`docs/trial_ledger.csv` → `CB-SIZEPREM_600000` / `CB-SIZEPREM_1000000` + `CB-SIZEPREM_strategy_note`；`output/promotion_ledger.json` → `descriptive_CB_SIZEPREM_fail_explore`
- 禁小盘。继续盯 `output/v3/handoff_strategy/`。pass 臂仍为 CB-MATPREM + MP-NEAR。未触碰 MP-NEAR recon。

### MP-FAR（MATPREM 远端变体 ytm[2.5,5]+低溢价 top15 + 压舱）AUM 60万/100万 — 2026-10-12T01:35:55-04:00 · fail_explore · 无交接

- **不作晋升证据**：Beta 探索不通过；`promotion_approved=false`。
- 来源：`output/v3/mp_far/`（Beta）；**无** Strategy 交接包。
- 预注册：`docs/v2/V3_MP_FAR_PREREG.md`
- 构成：MATPREM 远端变体：转股期 ∩ ytm[2.5,5]年低溢价 top15 + 债金压舱；**无 IC、无小盘**。
- 主结论口径：**AUM=60万 / 100万**。密封窗仅描述。
- 判定：X2≈14.0% 过 12%，但 **X1 Sharpe&lt;0**（≈−0.31）→ **fail_explore**；**无交接**（无 `handoff_strategy/mp_far`）。
- 摘要：

| AUM | X1（年化/回撤/夏普） | X2 |
|---|---|---|
| 60万 | −4.1% / −15.3% / -0.31 | 14.0% / −9.5% / 1.06 |
| 100万 | −4.2% / −15.5% / -0.31 | 14.0% / −9.9% / 1.04 |

- 台账：`docs/trial_ledger.csv` → `MP-FAR_600000` / `MP-FAR_1000000` + `MP-FAR_strategy_note`；`output/promotion_ledger.json` → `descriptive_MP_FAR_fail_explore`
- 禁小盘。继续盯 `output/v3/handoff_strategy/`。pass 臂仍为 CB-MATPREM + MP-NEAR。未触碰 MP-NEAR recon。

### CB-LISTAGE（上市龄[1,3]年×低溢价 Top15 + 压舱，无 ytm 带）AUM 60万/100万 — 2026-10-12T01:35:55-04:00 · fail_explore · 无交接

- **不作晋升证据**：Beta 探索不通过；`promotion_approved=false`。
- 来源：`output/v3/cb_listage/`（Beta）；**无** Strategy 交接包。
- 预注册：`docs/v2/V3_CB_LISTAGE_PREREG.md`
- 构成：上市龄[1,3]年 × 低溢价 Top15 + 债金压舱；**无 ytm 带**；**无 IC、无小盘**。
- 主结论口径：**AUM=60万 / 100万**。密封窗仅描述。
- 判定：X1 Sharpe&lt;0；X2≈11.8–12.0% 未稳过 12%（60万≈11.8%、100万≈12.0%）→ **fail_explore**；**无交接**（无 `handoff_strategy/cb_listage`）。
- 摘要：

| AUM | X1（年化/回撤/夏普） | X2 |
|---|---|---|
| 60万 | −0.7% / −8.1% / -0.10 | 11.8% / −10.1% / 0.89 |
| 100万 | −0.7% / −8.2% / -0.10 | 12.0% / −10.2% / 0.89 |

- 台账：`docs/trial_ledger.csv` → `CB-LISTAGE_600000` / `CB-LISTAGE_1000000` + `CB-LISTAGE_strategy_note`；`output/promotion_ledger.json` → `descriptive_CB_LISTAGE_fail_explore`
- 禁小盘。继续盯 `output/v3/handoff_strategy/`。pass 臂仍为 CB-MATPREM + MP-NEAR。未触碰 MP-NEAR recon。

### CB-CONVACT（Δacc_convert_ratio 20日>0×低溢价 Top15 + 压舱）AUM 60万/100万 — 2026-10-12T01:40:47-04:00 · fail_explore · 无交接

- **不作晋升证据**：Beta 探索不通过；`promotion_approved=false`。
- 来源：`output/v3/cb_convact/`（Beta）；**无** Strategy 交接包。
- 预注册：`docs/v2/V3_CB_CONVACT_PREREG.md`
- 构成：Δacc_convert_ratio 20日>0 × 低溢价 Top15 + 债金压舱；**≠ remain_size 收缩**；**无 IC、无小盘**。
- 主结论口径：**AUM=60万 / 100万**。密封窗仅描述。
- 判定：X2≈15.3–15.8% 过线，但 **X1 Sharpe&lt;0**（≈−0.45）→ **fail_explore**；**无交接**（无 `handoff_strategy/cb_convact`）。
- 摘要：

| AUM | X1（年化/回撤/夏普） | X2 |
|---|---|---|
| 60万 | −4.2% / −12.2% / -0.45 | 15.3% / −8.6% / 1.24 |
| 100万 | −4.3% / −12.4% / -0.45 | 15.8% / −8.7% / 1.26 |

- 台账：`docs/trial_ledger.csv` → `CB-CONVACT_600000` / `CB-CONVACT_1000000` + `CB-CONVACT_strategy_note`；`output/promotion_ledger.json` → `descriptive_CB_CONVACT_fail_explore`
- 禁小盘。继续盯 `output/v3/handoff_strategy/`。pass 臂仍为 CB-MATPREM + MP-NEAR。未触碰 MP-NEAR recon。

### CB-LARGEISS AUM 60万/100万 — 2026-10-12T01:40:47-04:00 · fail_explore · 无交接

- **不作晋升证据**：Beta 探索不通过；`promotion_approved=false`。
- 来源：`output/v3/cb_largeiss/`（Beta）；**无** Strategy 交接包。
- 预注册：`docs/v2/V3_CB_LARGEISS_PREREG.md`
- 构成：issue_size>=CS median × low premium; NOT calendar sleeve；**无 IC、无小盘**。
- 主结论口径：**AUM=60万 / 100万**。密封窗仅描述。
- 判定：X1 Sharpe≈-0.71；X2≈9.8–10.0%&lt;12% → **fail_explore**；**无交接**（无 `handoff_strategy/cb_largeiss`）。
- 摘要：

| AUM | X1（年化/回撤/夏普） | X2 |
|---|---|---|
| 60万 | −9.3% / −29.9% / -0.71 | 9.8% / −7.0% / 1.00 |
| 100万 | −9.5% / −30.1% / -0.72 | 10.0% / −6.9% / 1.00 |

- 台账：`docs/trial_ledger.csv` → `CB-LARGEISS_600000` / `CB-LARGEISS_1000000` + `CB-LARGEISS_strategy_note`；`output/promotion_ledger.json` → `descriptive_CB_LARGEISS_fail_explore`
- 禁小盘。继续盯 `output/v3/handoff_strategy/`。pass 臂仍为 CB-MATPREM + MP-NEAR。未触碰 MP-NEAR recon。

### CB-CALLTV（强赎邻近价区[110,128]锚120 + 中位价时变袖套 + 压舱）AUM 60万/100万 — 2026-10-12T01:45:56-04:00 · fail_explore · 无交接

- **不作晋升证据**：Beta 探索不通过；`promotion_approved=false`。
- 来源：`output/v3/cb_calltv/`（Beta）；**无** Strategy 交接包。
- 预注册：`docs/v2/V3_CB_CALLTV_PREREG.md`
- 构成：价∈[110,128] 取 |close−120| 最小 Top15；袖套随截面中位价时变 0.30/0.40/0.50 + 债金压舱；**无 IC、无小盘**。
- 主结论口径：**AUM=60万 / 100万**。密封窗仅描述。
- 判定：X1 预检过线（Sharpe≈0.60）后正式双窗；**X2≈7.3–7.4%&lt;12%** → **fail_explore**；**无交接**（无 `handoff_strategy/cb_calltv`）。
- 摘要：

| AUM | X1（年化/回撤/夏普） | X2 |
|---|---|---|
| 60万 | 3.2% / −5.4% / 0.60 | 7.4% / −4.0% / 1.34 |
| 100万 | 3.1% / −5.4% / 0.58 | 7.3% / −4.0% / 1.32 |

- 台账：`docs/trial_ledger.csv` → `CB-CALLTV_600000` / `CB-CALLTV_1000000` + `CB-CALLTV_strategy_note`；`output/promotion_ledger.json` → `descriptive_CB_CALLTV_fail_explore`
- 禁小盘。继续盯 `output/v3/handoff_strategy/`。pass 臂仍为 CB-MATPREM + MP-NEAR。


### TS-CURVE（ETF-only 利率曲线 / Shibor slope）— 2026-10-12T01:45:56-04:00 · fail_precheck · 无交接

- **不作晋升证据**：X1 Sharpe 预检失败；`promotion_approved=false`。
- 来源：`output/v3/ts_curve/x1_sharpe_pretest.json`；同批 `pretest_batch_20261012.json`。
- 预注册构想：`docs/v2/BETA_NEXT_AUM_ARMS_ZH.md`（无独立 V3 预注册；预检关闭）。
- 判定：X1 Sharpe≈**−0.06**（CAGR≈−2.0%；MDD≈−26.4%）→ **fail_precheck**；**未开正式双窗**；**无交接**。
- 台账：`docs/trial_ledger.csv` → `TS-CURVE_X1_pretest` + `TS-CURVE_strategy_note`；`output/promotion_ledger.json` → `descriptive_TS_CURVE_fail_precheck`
- 禁小盘。pass 臂仍为 CB-MATPREM + MP-NEAR。


### CB-LOWBETA（对 510300 最低 |β| 转债袖套）— 2026-10-12T01:45:56-04:00 · fail_precheck · 无交接

- **不作晋升证据**：X1 Sharpe 预检失败；`promotion_approved=false`。
- 来源：`output/v3/cb_lowbeta/x1_sharpe_pretest.json`；同批 `pretest_batch_20261012.json`。
- 预注册构想：`docs/v2/BETA_NEXT_AUM_ARMS_ZH.md`（无独立 V3 预注册；预检关闭）。
- 判定：X1 Sharpe≈**−0.21**（CAGR≈−2.0%；MDD≈−10.5%）→ **fail_precheck**；**未开正式双窗**；**无交接**。
- 台账：`docs/trial_ledger.csv` → `CB-LOWBETA_X1_pretest` + `CB-LOWBETA_strategy_note`；`output/promotion_ledger.json` → `descriptive_CB_LOWBETA_fail_precheck`
- 禁小盘。pass 臂仍为 CB-MATPREM + MP-NEAR。


### VT-EQ（510300 波动目标 10% 权益敞口 + 债金压舱）AUM 60万/100万 — 2026-10-12T01:52:53-04:00 · fail_explore · 无交接

- **不作晋升证据**：Beta 探索不通过；`promotion_approved=false`。
- 来源：`output/v3/vt_eq/`（Beta）；**无** Strategy 交接包。
- 预注册：`docs/v2/V3_VT_EQ_PREREG.md`
- 构成：月末 \(w_{eq}=\mathrm{clip}(0.10/\sigma_{60},0.20,0.55)\)→510300；其余 511010/518880 逆波；**无 IC、无期货、无小盘**。
- 主结论口径：**AUM=60万 / 100万**。密封窗仅描述。
- 判定：X1 预检过线（Sharpe≈0.37）；正式 **X2≈11.7%&lt;12%** → **fail_explore**；**无交接**（无 `handoff_strategy/vt_eq`）。
- 摘要：

| AUM | X1（年化/回撤/夏普） | X2 |
|---|---|---|
| 60万 | 2.9% / −14.2% / 0.37 | 11.7% / −6.8% / 1.16 |
| 100万 | 2.9% / −14.2% / 0.37 | 11.7% / −6.8% / 1.16 |

- 台账：`docs/trial_ledger.csv` → `VT-EQ_600000` / `VT-EQ_1000000` + `VT-EQ_strategy_note`；`output/promotion_ledger.json` → `descriptive_VT_EQ_fail_explore`
- 禁小盘。继续盯 `output/v3/handoff_strategy/`。pass 臂仍为 CB-MATPREM + MP-NEAR。


### CB-LIQTOP（价区[100,115]+回售回避×高 ADV Top15 + 50%袖套）AUM 60万/100万 — 2026-10-12T01:52:53-04:00 · fail_explore · 无交接

- **不作晋升证据**：Beta 探索不通过；`promotion_approved=false`。
- 来源：`output/v3/cb_liqtop/`（Beta）；**无** Strategy 交接包。
- 预注册：`docs/v2/V3_CB_LIQTOP_PREREG.md`
- 构成：价∈[100,115]；排除近 60 日回售提示/公告；按 **ADV 最高** Top15（**非溢价**）；袖 50%+压舱；**无 IC、无小盘**。
- 主结论口径：**AUM=60万 / 100万**。密封窗仅描述。
- 判定：X1 预检过线（Sharpe≈0.49）；正式 **X2≈4.9–5.0%&lt;12%** → **fail_explore**；**无交接**（无 `handoff_strategy/cb_liqtop`）。
- 摘要：

| AUM | X1（年化/回撤/夏普） | X2 |
|---|---|---|
| 60万 | 2.1% / −6.9% / 0.49 | 5.0% / −4.9% / 0.99 |
| 100万 | 2.0% / −7.0% / 0.47 | 4.9% / −5.0% / 0.98 |

- 台账：`docs/trial_ledger.csv` → `CB-LIQTOP_600000` / `CB-LIQTOP_1000000` + `CB-LIQTOP_strategy_note`；`output/promotion_ledger.json` → `descriptive_CB_LIQTOP_fail_explore`
- 禁小盘。继续盯 `output/v3/handoff_strategy/`。pass 臂仍为 CB-MATPREM + MP-NEAR。


### CB-DISP（截面离散度定时袖 + remain_size 最大 Top15）AUM 60万/100万 — 2026-10-12T01:52:53-04:00 · fail_explore · 无交接

- **不作晋升证据**：Beta 探索不通过；`promotion_approved=false`。
- 来源：`output/v3/cb_disp/`（Beta）；**无** Strategy 交接包。
- 预注册：`docs/v2/V3_CB_DISP_PREREG.md`
- 构成：价≥95；取 remain_size 最大 15；截面 20 日收益离散度高→袖 25%/低→50% + 压舱；**非溢价**；**无 IC、无小盘**。
- 主结论口径：**AUM=60万 / 100万**。密封窗仅描述。
- 判定：X1 预检过线（Sharpe≈0.43）；正式 **X2≈3.4–3.5%&lt;12%** → **fail_explore**；**无交接**（无 `handoff_strategy/cb_disp`）。
- 摘要：

| AUM | X1（年化/回撤/夏普） | X2 |
|---|---|---|
| 60万 | 1.8% / −6.9% / 0.43 | 3.4% / −5.4% / 0.80 |
| 100万 | 1.9% / −6.9% / 0.45 | 3.5% / −5.4% / 0.82 |

- 台账：`docs/trial_ledger.csv` → `CB-DISP_600000` / `CB-DISP_1000000` + `CB-DISP_strategy_note`；`output/promotion_ledger.json` → `descriptive_CB_DISP_fail_explore`
- 禁小盘。继续盯 `output/v3/handoff_strategy/`。pass 臂仍为 CB-MATPREM + MP-NEAR。


### RATE-LEVEL（Shibor 1m 水平体制）— 2026-10-12T01:52:53-04:00 · fail_precheck · 无交接

- **不作晋升证据**：X1 Sharpe 预检失败；`promotion_approved=false`。
- 来源：`output/v3/rate_level/x1_sharpe_pretest.json`；同批 `pretest_batch_20261012_b.json` / `pretest_batch_20261012_roundC.json`。
- 预注册构想：`docs/v2/BETA_NEXT_AUM_ARMS_ZH.md`（无独立 V3 预注册；预检关闭）。
- 判定：X1 Sharpe≈**−0.10**（CAGR≈−2.4%；MDD≈−25.8%）→ **fail_precheck**；**未开正式双窗**；**无交接**。
- 台账：`docs/trial_ledger.csv` → `RATE-LEVEL_X1_pretest` + `RATE-LEVEL_strategy_note`；`output/promotion_ledger.json` → `descriptive_RATE_LEVEL_fail_precheck`
- 禁小盘。pass 臂仍为 CB-MATPREM + MP-NEAR。


### GOLD-MR（金/债 20 日相对均值回归）— 2026-10-12T01:52:53-04:00 · fail_precheck · 无交接

- **不作晋升证据**：X1 Sharpe 预检失败；`promotion_approved=false`。
- 来源：`output/v3/gold_mr/x1_sharpe_pretest.json`；同批 `pretest_batch_20261012_b.json` / `pretest_batch_20261012_roundC.json`。
- 预注册构想：`docs/v2/BETA_NEXT_AUM_ARMS_ZH.md`（无独立 V3 预注册；预检关闭）。
- 判定：X1 Sharpe≈**−0.05**（CAGR≈−1.7%；MDD≈−25.0%）→ **fail_precheck**；**未开正式双窗**；**无交接**。
- 台账：`docs/trial_ledger.csv` → `GOLD-MR_X1_pretest` + `GOLD-MR_strategy_note`；`output/promotion_ledger.json` → `descriptive_GOLD_MR_fail_precheck`
- 禁小盘。pass 臂仍为 CB-MATPREM + MP-NEAR。

### VOL-TERM（20/60 波动比缩放权益 + 纯债压舱）AUM 60万/100万 — 2026-10-12T02:02:40-04:00 · fail_explore · 无交接

- **不作晋升证据**：Beta 探索不通过；`promotion_approved=false`。
- 来源：`output/v3/vol_term/`（Beta）；**无** Strategy 交接包。
- 预注册：`docs/v2/V3_VOL_TERM_PREREG.md`
- 构成：月末 \(w_{eq}=\mathrm{clip}(0.45/\max(\sigma_{20}/\sigma_{60},0.5),0.20,0.55)\)→510300；其余 511010；**无黄金、无 IC、无期货、无小盘**。≠VT-EQ / ≠DD-BALLAST。
- 主结论口径：**AUM=60万 / 100万**。密封窗仅描述。
- 判定：X1 预检过线（Sharpe≈0.03）；正式 **X2≈9.8%&lt;12%** → **fail_explore**；**无交接**（无 `handoff_strategy/vol_term`）。
- 摘要：

| AUM | X1（年化/回撤/夏普） | X2 |
|---|---|---|
| 60万 | −0.3% / −18.1% / 0.03 | 9.8% / −6.1% / 1.10 |
| 100万 | −0.3% / −18.1% / 0.03 | 9.8% / −6.1% / 1.10 |

- 台账：`docs/trial_ledger.csv` → `VOL-TERM_600000` / `VOL-TERM_1000000` + `VOL-TERM_strategy_note`；`output/promotion_ledger.json` → `descriptive_VOL_TERM_fail_explore`
- 禁小盘。继续盯 `output/v3/handoff_strategy/`。pass 臂仍为 CB-MATPREM + MP-NEAR（MERGE/RELAX/DD recon 另处）。
- **未触碰** `output/strategy_recon/{dd_ballast,mp_merge,mp_relax}/`。

### CASH-FLOOR（硬性货币底30% + 逆波300/债）AUM 60万/100万 — 2026-10-12T02:02:40-04:00 · fail_explore · 无交接

- **不作晋升证据**：Beta 探索不通过；`promotion_approved=false`。
- 来源：`output/v3/cash_floor/`（Beta）；**无** Strategy 交接包。
- 预注册：`docs/v2/V3_CASH_FLOOR_PREREG.md`
- 构成：月末 511880 **≥30%**；剩余对 510300/511010 60 日逆波；**无黄金、无 IC、无期货、无小盘**。≠DD-BALLAST。
- 主结论口径：**AUM=60万 / 100万**。密封窗仅描述。
- 判定：X1 预检过线（Sharpe≈0.81）；正式 **X2≈3.7%&lt;12%** → **fail_explore**；**无交接**（无 `handoff_strategy/cash_floor`）。
- 摘要：

| AUM | X1（年化/回撤/夏普） | X2 |
|---|---|---|
| 60万 | 2.0% / −3.1% / 0.81 | 3.7% / −0.8% / 2.55 |
| 100万 | 2.0% / −3.1% / 0.80 | 3.7% / −0.8% / 2.55 |

- 台账：`docs/trial_ledger.csv` → `CASH-FLOOR_600000` / `CASH-FLOOR_1000000` + `CASH-FLOOR_strategy_note`；`output/promotion_ledger.json` → `descriptive_CASH_FLOOR_fail_explore`
- 禁小盘。继续盯 `output/v3/handoff_strategy/`。pass 臂仍为 CB-MATPREM + MP-NEAR（MERGE/RELAX/DD recon 另处）。
- **未触碰** `output/strategy_recon/{dd_ballast,mp_merge,mp_relax}/`。

### CB-PAR（近面值[95,102] 高 ADV Top15 + 债压舱）AUM 60万/100万 — 2026-10-12T02:02:40-04:00 · fail_explore · 无交接

- **不作晋升证据**：Beta 探索不通过；`promotion_approved=false`。
- 来源：`output/v3/cb_par/`（Beta）；**无** Strategy 交接包。
- 预注册：`docs/v2/V3_CB_PAR_PREREG.md`
- 构成：每10日 FULLCB；价∈[95,102]；ADV Top15；袖45%+511010；**非双低/非溢价**；**无 IC、无小盘**。≠CB1-FLOOR / ≠MATPREM。
- 主结论口径：**AUM=60万 / 100万**。密封窗仅描述。
- 判定：X1 预检过线（Sharpe≈0.56；空仓≈89%）；正式 **X2≈7.5%&lt;12%** → **fail_explore**；**无交接**（无 `handoff_strategy/cb_par`）。
- 摘要：

| AUM | X1（年化/回撤/夏普） | X2 |
|---|---|---|
| 60万 | 1.6% / −4.9% / 0.56 | 7.5% / −8.4% / 1.16 |
| 100万 | 1.6% / −4.9% / 0.55 | 7.5% / −8.4% / 1.15 |

- 台账：`docs/trial_ledger.csv` → `CB-PAR_600000` / `CB-PAR_1000000` + `CB-PAR_strategy_note`；`output/promotion_ledger.json` → `descriptive_CB_PAR_fail_explore`
- 禁小盘。继续盯 `output/v3/handoff_strategy/`。pass 臂仍为 CB-MATPREM + MP-NEAR（MERGE/RELAX/DD recon 另处）。
- **未触碰** `output/strategy_recon/{dd_ballast,mp_merge,mp_relax}/`。

### CORR-CUT（股金相关高时削减黄金）— 2026-10-12T02:02:40-04:00 · fail_precheck · 无交接

- **不作晋升证据**：X1 Sharpe 预检失败；`promotion_approved=false`。
- 来源：`output/v3/corr_cut/x1_sharpe_pretest.json`；同批 `pretest_batch_20261012_f.json` / roundF。
- 预注册构想：`docs/v2/BETA_NEXT_AUM_ARMS_ZH.md`（无独立 V3 预注册；预检关闭）。
- 判定：X1 Sharpe≈**−0.06**（CAGR≈−1.7%；MDD≈−24.7%）→ **fail_precheck**；**未开正式双窗**；**无交接**。
- 台账：`docs/trial_ledger.csv` → `CORR-CUT_X1_pretest` + `CORR-CUT_strategy_note`；`output/promotion_ledger.json` → `descriptive_CORR_CUT_fail_precheck`
- 禁小盘。pass 臂仍为 CB-MATPREM + MP-NEAR。

### DUR-MR（久期均值回归 货币/债）— 2026-10-12T02:02:40-04:00 · fail_precheck · 无交接

- **不作晋升证据**：X1 Sharpe 预检失败；`promotion_approved=false`。
- 来源：`output/v3/dur_mr/x1_sharpe_pretest.json`；同批 `pretest_batch_20261012_f.json` / roundF。
- 预注册构想：`docs/v2/BETA_NEXT_AUM_ARMS_ZH.md`（无独立 V3 预注册；预检关闭）。
- 判定：X1 Sharpe≈**−0.07**（CAGR≈−2.2%；MDD≈−25.9%）→ **fail_precheck**；**未开正式双窗**；**无交接**。
- 台账：`docs/trial_ledger.csv` → `DUR-MR_X1_pretest` + `DUR-MR_strategy_note`；`output/promotion_ledger.json` → `descriptive_DUR_MR_fail_precheck`
- 禁小盘。pass 臂仍为 CB-MATPREM + MP-NEAR。

### EQ-CROSS（300vs050 相对均值回归）— 2026-10-12T02:02:40-04:00 · fail_precheck · 无交接

- **不作晋升证据**：X1 Sharpe 预检失败；`promotion_approved=false`。
- 来源：`output/v3/eq_cross/x1_sharpe_pretest.json`；同批 `pretest_batch_20261012_f.json` / roundF。
- 预注册构想：`docs/v2/BETA_NEXT_AUM_ARMS_ZH.md`（无独立 V3 预注册；预检关闭）。
- 判定：X1 Sharpe≈**−0.07**（CAGR≈−1.9%；MDD≈−23.6%）→ **fail_precheck**；**未开正式双窗**；**无交接**。
- 台账：`docs/trial_ledger.csv` → `EQ-CROSS_X1_pretest` + `EQ-CROSS_strategy_note`；`output/promotion_ledger.json` → `descriptive_EQ_CROSS_fail_precheck`
- 禁小盘。pass 臂仍为 CB-MATPREM + MP-NEAR。

### CB-BONDVAL（纯债价值/收盘价最大）— 2026-10-12T02:02:40-04:00 · fail_precheck · 无交接

- **不作晋升证据**：X1 Sharpe 预检失败；`promotion_approved=false`。
- 来源：`output/v3/cb_bondval/x1_sharpe_pretest.json`；同批 `pretest_batch_20261012_f.json` / roundF。
- 预注册构想：`docs/v2/BETA_NEXT_AUM_ARMS_ZH.md`（无独立 V3 预注册；预检关闭）。
- 判定：X1 Sharpe≈**−0.84**（CAGR≈−10.9%；MDD≈−28.2%）→ **fail_precheck**；**未开正式双窗**；**无交接**。
- 台账：`docs/trial_ledger.csv` → `CB-BONDVAL_X1_pretest` + `CB-BONDVAL_strategy_note`；`output/promotion_ledger.json` → `descriptive_CB_BONDVAL_fail_precheck`
- 禁小盘。pass 臂仍为 CB-MATPREM + MP-NEAR。

### SHIBOR-ON（隔夜利率水平→权益）— 2026-10-12T02:02:40-04:00 · fail_precheck · 无交接

- **不作晋升证据**：X1 Sharpe 预检失败；`promotion_approved=false`。
- 来源：`output/v3/shibor_on/x1_sharpe_pretest.json`；同批 `pretest_batch_20261012_f.json` / roundF。
- 预注册构想：`docs/v2/BETA_NEXT_AUM_ARMS_ZH.md`（无独立 V3 预注册；预检关闭）。
- 判定：X1 Sharpe≈**−0.19**（CAGR≈−3.5%；MDD≈−25.8%）→ **fail_precheck**；**未开正式双窗**；**无交接**。
- 台账：`docs/trial_ledger.csv` → `SHIBOR-ON_X1_pretest` + `SHIBOR-ON_strategy_note`；`output/promotion_ledger.json` → `descriptive_SHIBOR_ON_fail_precheck`
- 禁小盘。pass 臂仍为 CB-MATPREM + MP-NEAR。

### PAIR-35（35/65 股债风险预算）— 2026-10-12T02:02:40-04:00 · fail_precheck · 无交接

- **不作晋升证据**：X1 Sharpe 预检失败；`promotion_approved=false`。
- 来源：`output/v3/pair_35/x1_sharpe_pretest.json`；同批 `pretest_batch_20261012_f.json` / roundF。
- 预注册构想：`docs/v2/BETA_NEXT_AUM_ARMS_ZH.md`（无独立 V3 预注册；预检关闭）。
- 判定：X1 Sharpe≈**−0.02**（CAGR≈−0.7%；MDD≈−16.7%）→ **fail_precheck**；**未开正式双窗**；**无交接**。
- 台账：`docs/trial_ledger.csv` → `PAIR-35_X1_pretest` + `PAIR-35_strategy_note`；`output/promotion_ledger.json` → `descriptive_PAIR_35_fail_precheck`
- 禁小盘。pass 臂仍为 CB-MATPREM + MP-NEAR。


### SHIBOR-dON（隔夜利率20日差分→权益 + 债压舱）AUM 60万/100万 — 2026-10-12T02:24:21-04:00 · fail_explore · 无交接

- **不作晋升证据**：Beta 探索不通过；`promotion_approved=false`。
- 来源：`output/v3/shibor_don/`（Beta）；**无** Strategy 交接包。
- 预注册：`docs/v2/V3_SHIBOR_DON_PREREG.md`
- 构成：Shibor ON 20 日差分调节 510300 权重（升息→降仓）；压舱 511010；**无 IC、无期货、无小盘**。≠SHIBOR-ON（水平）/ ≠RATE-LEVEL。
- 主结论口径：**AUM=60万 / 100万**。密封窗仅描述。
- 判定：X1 预检过线（Sharpe≈0.16）；正式 **X2≈6.8%&lt;12%** → **fail_explore**；**无交接**（无 `handoff_strategy/shibor_don`）。
- 摘要：

| AUM | X1（年化/回撤/夏普） | X2 |
|---|---|---|
| 60万 | 1.0% / −15.6% / 0.16 | 6.8% / −5.4% / 0.92 |
| 100万 | 1.0% / −15.6% / 0.16 | 6.8% / −5.4% / 0.92 |

- 台账：`docs/trial_ledger.csv` → `SHIBOR-dON_600000` / `SHIBOR-dON_1000000` + `SHIBOR-dON_strategy_note`；`output/promotion_ledger.json` → `descriptive_SHIBOR_DON_fail_explore`
- 禁小盘。继续盯 `output/v3/handoff_strategy/`。pass 臂仍为 CB-MATPREM + MP-NEAR + MP-MERGE + MP-RELAX + DD-BALLAST + GOLD-BETA；**DD×GOLD≈0.97**。
- **未触碰** `output/strategy_recon/{dd_ballast,mp_merge,mp_relax,gold_beta,cb_matprem,mp_near}/`。

### DEF35-RP（三资产逆波 + 权益上限35%）AUM 60万/100万 — 2026-10-12T02:24:21-04:00 · fail_explore · 无交接

- **不作晋升证据**：Beta 探索不通过；`promotion_approved=false`。
- 来源：`output/v3/def35_rp/`（Beta）；**无** Strategy 交接包。
- 预注册：`docs/v2/V3_DEF35_RP_PREREG.md`
- 构成：510300/511010/511880 60日逆波动；**权益上限 35%**；**无 IC、无期货、无小盘**。≠RP-3 无上限；≠GOLD-BETA。
- 主结论口径：**AUM=60万 / 100万**。密封窗仅描述。
- 判定：X1 预检过线（伪夏普≈5.2，超低波）；正式 **X2≈1.5%&lt;12%** → **fail_explore**；**无交接**（无 `handoff_strategy/def35_rp`）。
- 摘要：

| AUM | X1（年化/回撤/夏普*） | X2 |
|---|---|---|
| 60万 | 2.7% / −0.4% / ~5.2 | 1.5% / −0.2% / ~5.5 |
| 100万 | 2.8% / −0.4% / ~5.2 | 1.6% / −0.2% / ~5.5 |

\*低波伪夏普（货币/债主导），非真实 α。
- 台账：`docs/trial_ledger.csv` → `DEF35-RP_600000` / `DEF35-RP_1000000` + `DEF35-RP_strategy_note`；`output/promotion_ledger.json` → `descriptive_DEF35_RP_fail_explore`
- 禁小盘。继续盯 `output/v3/handoff_strategy/`。pass 臂仍为 CB-MATPREM + MP-NEAR + MP-MERGE + MP-RELAX + DD-BALLAST + GOLD-BETA；**DD×GOLD≈0.97**。
- **未触碰** `output/strategy_recon/{dd_ballast,mp_merge,mp_relax,gold_beta,cb_matprem,mp_near}/`。

### EQ-RP500（300+500 逆波 RP 于50%袖 + 债压舱）— 2026-10-12T02:24:21-04:00 · fail_precheck · 无交接

- **不作晋升证据**：X1 Sharpe 预检失败；`promotion_approved=false`。
- 来源：`output/v3/eq_rp500/x1_sharpe_pretest.json`；同批 `pretest_batch_20261012_h.json` / roundH。
- 预注册构想：`docs/v2/BETA_NEXT_AUM_ARMS_ZH.md`（无独立 V3 预注册；预检关闭）。
- 判定：X1 Sharpe≈**−0.21**（CAGR≈−4.2%；MDD≈−25.4%）→ **fail_precheck**；**未开正式双窗**；**无交接**。
- 台账：`docs/trial_ledger.csv` → `EQ-RP500_X1_pretest` + `EQ-RP500_strategy_note`；`output/promotion_ledger.json` → `descriptive_EQ_RP500_fail_precheck`
- 禁小盘。pass 臂仍为 CB-MATPREM + MP-NEAR + MP-MERGE + MP-RELAX + DD-BALLAST + GOLD-BETA；**DD×GOLD≈0.97**。

### BOND-VOL（债实现波动体制→货币/债；权益固定）— 2026-10-12T02:24:21-04:00 · fail_precheck · 无交接

- **不作晋升证据**：X1 Sharpe 预检失败；`promotion_approved=false`。
- 来源：`output/v3/bond_vol/x1_sharpe_pretest.json`；同批 `pretest_batch_20261012_h.json` / roundH。
- 预注册构想：`docs/v2/BETA_NEXT_AUM_ARMS_ZH.md`（无独立 V3 预注册；预检关闭）。
- 判定：X1 Sharpe≈**−0.01**（CAGR≈−0.7%；MDD≈−18.9%）→ **fail_precheck**；**未开正式双窗**；**无交接**。
- 台账：`docs/trial_ledger.csv` → `BOND-VOL_X1_pretest` + `BOND-VOL_strategy_note`；`output/promotion_ledger.json` → `descriptive_BOND_VOL_fail_precheck`
- 禁小盘。pass 臂仍为 CB-MATPREM + MP-NEAR + MP-MERGE + MP-RELAX + DD-BALLAST + GOLD-BETA；**DD×GOLD≈0.97**。

### REL500（300vs500 相对均值回归 + 债压舱）— 2026-10-12T02:24:21-04:00 · fail_precheck · 无交接

- **不作晋升证据**：X1 Sharpe 预检失败；`promotion_approved=false`。
- 来源：`output/v3/rel500/x1_sharpe_pretest.json`；同批 `pretest_batch_20261012_h.json` / roundH。
- 预注册构想：`docs/v2/BETA_NEXT_AUM_ARMS_ZH.md`（无独立 V3 预注册；预检关闭）。
- 判定：X1 Sharpe≈**−0.19**（CAGR≈−3.9%；MDD≈−24.0%）→ **fail_precheck**；**未开正式双窗**；**无交接**。
- 台账：`docs/trial_ledger.csv` → `REL500_X1_pretest` + `REL500_strategy_note`；`output/promotion_ledger.json` → `descriptive_REL500_fail_precheck`
- 禁小盘。pass 臂仍为 CB-MATPREM + MP-NEAR + MP-MERGE + MP-RELAX + DD-BALLAST + GOLD-BETA；**DD×GOLD≈0.97**。

### ETF-FLOW-NET（双ETF份额净流顺流调权益）— 2026-10-12T02:24:21-04:00 · fail_precheck · 无交接

- **不作晋升证据**：X1 Sharpe 预检失败；`promotion_approved=false`。
- 来源：`output/v3/etf_flow_net/x1_sharpe_pretest.json`；同批 `pretest_batch_20261012_i.json` / roundI。
- 预注册构想：`docs/v2/BETA_NEXT_AUM_ARMS_ZH.md`（无独立 V3 预注册；预检关闭）。
- 判定：X1 Sharpe≈**−0.17**（CAGR≈−3.1%；MDD≈−23.6%）→ **fail_precheck**；**未开正式双窗**；**无交接**。≠SHARE-AC（反拥挤）。
- 台账：`docs/trial_ledger.csv` → `ETF-FLOW-NET_X1_pretest` + `ETF-FLOW-NET_strategy_note`；`output/promotion_ledger.json` → `descriptive_ETF_FLOW_NET_fail_precheck`
- 禁小盘。pass 臂仍为 CB-MATPREM + MP-NEAR + MP-MERGE + MP-RELAX + DD-BALLAST + GOLD-BETA；**DD×GOLD≈0.97**。

### CASH-TRIG25（波动触发可变货币25%/10% + 固定60/40债股）— 2026-10-12T02:24:21-04:00 · fail_precheck · 无交接

- **不作晋升证据**：X1 Sharpe 预检失败；`promotion_approved=false`。
- 来源：`output/v3/cash_trig25/x1_sharpe_pretest.json`；同批 `pretest_batch_20261012_i.json` / roundI。
- 预注册构想：`docs/v2/BETA_NEXT_AUM_ARMS_ZH.md`（无独立 V3 预注册；预检关闭）。
- 判定：X1 Sharpe≈**−0.02**（CAGR≈−0.5%；MDD≈−15.7%）→ **fail_precheck**；**未开正式双窗**；**无交接**。≠CASH-FLOOR（硬底30%）。
- 台账：`docs/trial_ledger.csv` → `CASH-TRIG25_X1_pretest` + `CASH-TRIG25_strategy_note`；`output/promotion_ledger.json` → `descriptive_CASH_TRIG25_fail_precheck`
- 禁小盘。pass 臂仍为 CB-MATPREM + MP-NEAR + MP-MERGE + MP-RELAX + DD-BALLAST + GOLD-BETA；**DD×GOLD≈0.97**。

### CB-PREMRESID（溢价对平价残差×期限带；≠MATPREM 近亲切片）AUM 60万/100万 — 2026-10-12T02:44:56-04:00 · fail_explore · 无交接

- **不作晋升证据**：正式双窗探索失败；`promotion_approved=false`。
- 来源：`output/v3/cb_premresid/results.json` / `SHORT_ZH.md`；同批 `pretest_batch_20261012_p0.json` / Beta P0。
- 预注册：`docs/v2/V3_CB_PREMRESID_PREREG.md`
- 构成：`cb_over_rate` 对 `cb_value`（平价）十分位中位残差；`score=−prem_resid`；转股期∩期限[1,3]年 top20；CB 50% + 单压舱 511010；**无 IC、无期货、无小盘**。≠MATPREM 原始低溢价排序；P0-4 不叠 GOLD。
- 判定：X1 预检过线（Sharpe≈0.60）但 **avg_names=0（空仓→纯债）**；正式 **X2≈10.5–10.6%&lt;12%** → **fail_explore**；**无交接**（无 `handoff_strategy/cb_premresid`）。
- 主表（60万 / 100万）X2 CAGR≈**10.52% / 10.56%**；MDD≈−5.9/−6.0%；Sharpe≈1.55/1.53；X1 CAGR≈1.65%、avg_names=**0.0**。
- 台账：`docs/trial_ledger.csv` → `CB-PREMRESID_600000` / `CB-PREMRESID_1000000` + `CB-PREMRESID_strategy_note`；`output/promotion_ledger.json` → `descriptive_CB_PREMRESID_fail_explore`
- 禁小盘。P0-3 方向失败 → 禁止再扩 MATPREM 近亲切片。WATCH 压舱：GOLD 主表 / DD watch_only。pass=MATPREM+NEAR+MERGE+RELAX+GOLD(+DD watch_only)。

### SECT-FLOW-DISP（行业流离散；裸/离散流）— 2026-10-12T02:44:56-04:00 · fail_precheck · CLOSED · 无交接

- **不作晋升证据**：X1 Sharpe 预检失败；`promotion_approved=false`。
- 来源：`output/v3/sect_flow_disp/x1_sharpe_pretest.json` / `SHORT_ZH.md`；同批 `pretest_batch_20261012_p0.json` / Beta P0。
- 预注册构想：`docs/v2/BETA_NEXT_AUM_ARMS_ZH.md`（无独立 V3 预注册；预检关闭）。
- 判定：X1 Sharpe≈**−0.072**（CAGR≈−1.3%；MDD≈−19.1%）→ **fail_precheck**；**status=CLOSED_after_pretest_superseded_by_P0-5_crowding**；**未开正式双窗**；**无交接**。P0 停止裸份额流扩臂，改拥挤→扩散。
- 台账：`docs/trial_ledger.csv` → `SECT-FLOW-DISP_X1_pretest` + `SECT-FLOW-DISP_strategy_note`；`output/promotion_ledger.json` → `descriptive_SECT_FLOW_DISP_fail_precheck`
- 禁小盘。WATCH 压舱：GOLD 主表 / DD watch_only。pass=MATPREM+NEAR+MERGE+RELAX+GOLD(+DD watch_only)。

### IND-CROWD-REV（行业拥挤广度→降510300；≠裸净流）— 2026-10-12T02:44:56-04:00 · fail_precheck · 无交接

- **不作晋升证据**：X1 Sharpe 预检失败；`promotion_approved=false`。
- 来源：`output/v3/ind_crowd_rev/x1_sharpe_pretest.json` / `SHORT_ZH.md`；同批 `pretest_batch_20261012_p0.json` / Beta P0。
- 预注册：`docs/v2/V3_IND_CROWD_REV_PREREG.md`
- 判定：X1 Sharpe≈**−0.050**（CAGR≈−1.2%；MDD≈−19.0%）→ **fail_precheck**；**未开正式双窗**；**无交接**。拥挤广度≠裸流入；≠SECT-FLOW-DISP。
- 台账：`docs/trial_ledger.csv` → `IND-CROWD-REV_X1_pretest` + `IND-CROWD-REV_strategy_note`；`output/promotion_ledger.json` → `descriptive_IND_CROWD_REV_fail_precheck`
- 禁小盘。WATCH 压舱：GOLD 主表 / DD watch_only。pass=MATPREM+NEAR+MERGE+RELAX+GOLD(+DD watch_only)。


### LPR-LEVEL（LPR1Y绝对水平z分档调510300+GOLD）— 2026-10-12T04:44:55-04:00 · near_relative · research_observe · 有交接

- **不作晋升证据**：对账通过但族内近亲；`promotion_approved=false`；**非独立 explore-pass**。
- 来源：`output/strategy_recon/lpr_level/`；交接 `output/v3/handoff_strategy/lpr_level/`；ortho5。
- 预注册：`docs/v2/V3_LPR_LEVEL_PREREG.md`
- 判定：`pass_all=true`；vs IND-RATE-DIFF 日≈**0.978**、GOLD-BETA≈**0.913**、PARITY≈**0.898** → **near_relative**。
- 主表 60/100万：X2≈**18.11%/18.13%**、MDD≈−19.0%、Sharpe≈1.07；**X1 Sharpe≈0.08 / MDD≈−24.45%（近25%闸）**。
- 台账：`descriptive_LPR_LEVEL_near_relative_research_observe`；trial `LPR-LEVEL_strategy_recon`。
- GOLD only；禁小盘。主表试配草案：MATPREM 族唯一 primary + GOLD-BETA。

### CB-MATWALL-MID（ytm[2,5]日历墙ADV等权+GOLD）— 2026-10-12T04:44:55-04:00 · recon A–B gap · research_observe · 有交接

- **不作晋升证据**：EngA≡Beta 但 pass_all=false；`promotion_approved=false`；**非独立 explore-pass**。
- 来源：`output/strategy_recon/cb_matwall_mid/`；交接 `output/v3/handoff_strategy/cb_matwall_mid/`；ortho5。
- 预注册：`docs/v2/V3_CB_MATWALL_MID_PREREG.md`
- 判定：EngA≡Beta；EngA–EngB 绝对阈未过；全部 |ρ_daily|≤0.85（最大 vs PARITY≈**0.825**）。
- 主表 60/100万：X2≈**20.51%/21.28%**、MDD≈**−22.6/−22.7%**；**X1 avg_names≈3.55**（空仓≈34.4%；黄金≈67.2%）。
- 台账：`descriptive_CB_MATWALL_MID_recon_AB_gap_research_observe`；trial `CB-MATWALL-MID_strategy_recon`。
- GOLD only；禁小盘；full panel。

### EQBOND-CORR（股债60d滚动相关调510300+GOLD）— 2026-10-12T04:44:55-04:00 · fail_precheck · 无交接

- **不作晋升证据**：X1 Sharpe 预检失败；`promotion_approved=false`。
- 来源：`output/v3/eqbond_corr/x1_sharpe_pretest.json`；ortho5。
- 预注册：`docs/v2/V3_EQBOND_CORR_PREREG.md`
- 判定：X1 Sharpe≈**−0.04**（avg_names=**1.00**）→ **fail_precheck**；未开正式双窗；无交接。
- 台账：`descriptive_EQBOND_CORR_fail_precheck`；trial `EQBOND-CORR_strategy_note`。
- GOLD only；禁小盘。


### CB-PUTFLOOR-NEAR — 2026-10-12T05:07:26-04:00 · near_relative · research_observe · 有交接
- 对账 OK；vs PARITY≈0.958 / COV≈0.927 → 非独立 explore-pass。X1 avg_names≈0.46 黄金主导。台账：`descriptive_CB_PUTFLOOR_NEAR_near_relative_research_observe`。GOLD only。`promotion_approved=false`。

### BOND-NAV-MR — 2026-10-12T05:07:26-04:00 · near_relative · research_observe · 有交接
- 对账 OK；vs GOLD≈0.57（压舱OK）；vs DIFF≈0.89 → 非独立 explore-pass。无510300。台账：`descriptive_BOND_NAV_MR_near_relative_research_observe`。`promotion_approved=false`。

### CB-SEASON-NEW — 2026-10-12T05:07:26-04:00 · tier_fail + near_relative · research_observe · 有交接
- EngA≡Beta；pass_all=false；**100万 X2 MDD≈−25.19% 未过**；vs PARITY≈0.88。台账：`descriptive_CB_SEASON_NEW_tier_fail_near_relative_research_observe`。`promotion_approved=false`。


### SHIBOR-ROLL-BOND — 2026-10-12T05:14:31-04:00 · near_relative · research_observe · 有交接
- pass_all=true；vs BOND-NAV≈0.999 / DIFF≈0.89；X2≈12.3%贴闸。台账：`descriptive_SHIBOR_ROLL_BOND_near_relative_research_observe`。`promotion_approved=false`。

### CB-MIDCONVEX — 2026-10-12T05:14:31-04:00 · near_relative · research_observe · 有交接
- EngA≡Beta；pass_all=false；vs PARITY≈0.980 / COV≈0.904；X1 avg≈2.19。台账：`descriptive_CB_MIDCONVEX_near_relative_research_observe`。`promotion_approved=false`。

### TF-T-CURVE — 2026-10-12T05:14:31-04:00 · fail_explore · 无交接
- X2 MDD≈−25.2%。台账：`descriptive_TF_T_CURVE_fail_explore`。`promotion_approved=false`。


### CB-CLAUSE-MISPR — 2026-10-12T05:16:44-04:00 · recon A–B gap · research_observe · 有交接
- EngA≡Beta；pass_all=false；X1 avg≈0.04 几乎全GOLD；S MDD≈−27%（Beta）；CB/利率 ρ&lt;0.85。台账：`descriptive_CB_CLAUSE_MISPR_recon_AB_gap_research_observe`。`promotion_approved=false`。

### CB-PR-NEUT-R9 — 2026-10-12T05:16:44-04:00 · fail_precheck · 无交接
- avg_names=0；Sharpe≈0.46。与 PREMRESID-COV 同族，重开必测 ρ。台账：`descriptive_CB_PR_NEUT_R9_fail_precheck`。`promotion_approved=false`。

## 附录（2026-10-12 Strategy 对账备忘，非晋升）

- **CB-PREMRESID-COV**：引擎自洽（A≡B）但 vs Beta 未过阈 → `pass_all=false`；短报 `output/strategy_recon/cb_premresid_cov/SHORT_ZH.md`；不作晋升证据。
- **IND-RATE-DIFF**：对账通过（A≡B≡Beta）；X1 软风险 Sharpe≈0.12 / MDD≈−22%；短报 `output/strategy_recon/ind_rate_diff/SHORT_ZH.md`；不作晋升证据。
- 压舱 P0-4：GOLD 主表 / DD watch_only；禁双压舱叠满。`promotion_approved=false`；禁小盘。
