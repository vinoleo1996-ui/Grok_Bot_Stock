# Beta 下一臂（Leo AUM 60万/100万）

研究级，**promotion_approved=false**。更新：2026-10-12 19:59 ET。

## 硬约束
主表 AUM 只 60万/100万；禁 IC；L≤1.5；无小盘；无教科书动量。  
**ANN-BETA：parked**。HARD GATE：X1 Sharpe 预检≤0 → fail_precheck。  
**FORBID**：MATPREM 族再扩（MERGE/RELAX 已封存）。

## 已通过（勿近亲复制）
MATPREM / MP-NEAR / MP-MERGE / MP-RELAX / **DD-BALLAST**

## 正交新臂 roundG
| 臂 | 机制 | X1 Sharpe | 处置 |
|---|---|---|---|
| **DD-BOND30** | **债券 ETF 回撤**触发货币/债切换；权益固定 30% — ≠ DD-BALLAST（权益回撤+金） | **+0.08** | → 正式 |
| **CB-CLAUSE-SM** | 条款状态机：(回售提示∨下修) ∧ ¬已满足强赎；ADV 选券 — 非溢价 | **+0.83** | → 正式 |
| **TERM-3M30** | Shibor **3m−1w** 斜率 + 30% 权益 — ≠ TS-CURVE(1y−1m) | **+0.04** | → 正式 |
| **CRED30** | `bond_over_rate` 截面离散度抬升→降权益 — 盒上信用代理 | **+0.00** | → 正式 |
| **GOLD-BETA** | β(金,股) 高则降金权重 — ≠ DD 回撤触发 | **+0.03** | → 正式 |
| DD-BOND(45%) / DD-ALT / TERM-3M(40%) / CREDIT-DISP / FTQ | 见 pretest | ≤0 | fail_precheck |

预检：`output/v3/pretest_batch_20261012_g.json`

## 本轮结果（roundG，2026-10-12 01:58 ET）
- **GOLD-BETA → pass_explore + Strategy handoff**（β(金,股) 调节压舱；≠ DD-BALLAST）。
- DD-BOND30 / TERM-3M30 / CRED30 / CB-CLAUSE-SM → fail_explore（X2&lt;12%）。
- MATPREM 族：**仍禁止扩族**。ANN parked。promotion_approved=false。

## 正交新臂 roundH（≠ GOLD-BETA / DD-BALLAST）
| 臂 | 机制 | X1 Sharpe | 处置 |
|---|---|---|---|
| **SHIBOR-dON** | ON 利率 20 日变化→权益；升息降仓 — ≠ 水平/斜率臂 | **+0.16** | 正式 **FAIL** X2 CAGR≈6.8% |
| **DEF35-RP** | 300/债/货币逆波且 **权益帽≤35%** — ≠ RP-3 无帽、≠ GOLD-BETA | **+5.16*** | 正式 **FAIL** X2 CAGR≈1.5%（伪夏普） |
| EQ-RP500 / BOND-VOL / REL500 | 见 pretest json | ≤0 | fail_precheck |

\*DEF35-RP 预检夏普异常高（低波动），正式双窗以闸门为准。  
预检：`output/v3/pretest_batch_20261012_h.json`  
**FORBID** MATPREM 族扩族。

## roundI 低带宽（2026-10-12 02:03 ET）— roundH 全关闭确认
roundH：SHIBOR-dON / DEF35-RP formal FAIL；EQ-RP500 / BOND-VOL / REL500 fail_precheck。已关闭。

### 跳过（近亲失败臂）
| 臂 | 跳过理由 |
|---|---|
| CRED-SLOPE | ≈ CRED30（roundG formal X2&lt;12%）— 同 `bond_over_rate` 信用族 |
| VOL-TERM-EQ | ≈ VOL-TERM（roundF fail）+ BOND-VOL（roundH fail_precheck）— 波动期限结构族 |

### 预检 @60万 X1（仅此两臂）
| 臂 | 机制（正交点） | X1 Sharpe | 处置 |
|---|---|---|---|
| **ETF-FLOW-NET** | 510300+510500 净周份额流入→加仓（顶半）；**顺流双标的** ≠ SHARE-AC 单标反拥挤 | **−0.17** | fail_precheck；无正式 |
| **CASH-TRIG25** | vol60>中位→货币25%否则10%；余60/40债股；**触发可变** ≠ CASH-FLOOR 固定30%+逆波 | **−0.02** | fail_precheck；无正式 |

预检：`output/v3/pretest_batch_20261012_i.json`  
**FORBID** MATPREM。ANN off。promotion_approved=false。AI factory 主战场 — 本轮 scope 小。  
**handoff: NO**（无 pretest passer）。

## P0 加急（2026-10-12 02:42 ET）— 审计 EXTERNAL_AI_BETA_ALPHA_GAP
数据：`data/v2/etf/share_pit/etf_share_flow_pit_all.parquet`（1829 names）

### P0-4 压舱（**采纳 Strategy 决议，不重判**）
| 主表试配压舱 | watch_only | 禁 |
|---|---|---|
| **GOLD-BETA** | DD-BALLAST | 禁止 DD+GOLD 叠满；handoff 只标一条压舱 |
依据：`docs/v2/STRATEGY_BALLAST_CHOOSE_ONE_AND_LOO_DRAFT_ZH.md`；Beta 复核 |ρ|≈0.98 → `output/v3/p0_4_dd_gold_corr.json`

### P0-3 CB-PREMRESID（溢价对平价残差×期限带）
| 预检 X1 Sharpe | 正式 X2 CAGR | 判定 |
|---|---|---|
| **+0.60**（但 avg_names=0，X1 空仓债底） | ≈10.5% | **fail_explore**；无交接 |
机制 ≠ MATPREM/NEAR/MERGE/RELAX 原低溢价排序。单压舱 511010。路径：`output/v3/cb_premresid/`

### P0-5 份额流 → 拥挤（非裸流入）
| 臂 | X1 Sharpe | 处置 |
|---|---|---|
| SECT-FLOW-DISP（行业流离散，已超限裸/离散流） | −0.07 | **关闭** fail_precheck |
| **IND-CROWD-REV**（行业拥挤广度→降 510300） | −0.05 | **fail_precheck**；无正式 |

**FORBID** MATPREM 近亲扩族。ANN park。promotion_approved=false。  
**handoff: NO**（本轮无新 pass）。

## 覆盖修复轮（2026-10-12 02:48 ET）
压舱：**GOLD-BETA / 518880 only**；DD watch_only。ANN park。禁 MATPREM 近亲。

| 臂 | 覆盖 / 预检 | 正式 | 交接 |
|---|---|---|---|
| **CB-PREMRESID-COV** | X1 avg_names≈5.13 | Strategy skip-filter 后 pass_all=true | **WATCH explore-pass**（研究级） |
| **IND-RATE-DIFF** | 行业覆盖≈20.3 Sharpe=+0.12 | Strategy **pass_all=true**；X1 软风险 Sharpe≈0.12 MDD≈−22% | **WATCH explore-pass**（非晋升） |

预检 batch：`output/v3/pretest_batch_20261012_cov.json`  
前版 CB-PREMRESID（[1,3] avg_names=0）保持关闭。

## Strategy 定案回写（2026-10-12 03:00 ET）
| 臂 | 状态 |
|---|---|
| **CB-PREMRESID-COV** | **WATCH explore-pass**（研究级；NAV gap 已关闭；pass_all=true） |
| **IND-RATE-DIFF** | **WATCH explore-pass** |
| **IND-RATE-P90** | **near_relative**（ρ≈0.995 vs DIFF）→ **非独立**；**STOP IND-RATE 族换皮/分位** |
| **CB-PREMRES-CONV** | **fail_precheck**（已入账） |
| 压舱 | **GOLD only**；禁 DD+GOLD 叠满 |

ANN park。`promotion_approved=false`。下一正交批：**禁** IND-RATE 变体、MATPREM 近亲、裸份额流、教科书动量。

## 正交批 ortho3（2026-10-12 03:02 ET）
禁 IND-RATE 变体 / MATPREM 近亲 / 裸流 / 教科书动量；GOLD only。

| 臂 | 机制 | 预检 | 正式 | 交接 |
|---|---|---|---|---|
| **MARGIN-DELTA** | 两融余额 Δ20 z→削 510300 | Sharpe−0.03 | — | fail_precheck |
| **CB-PUT-AVOID** | 剔回售提示后 ADV 等权 CB | avg≈5.5 Sharpe−0.50 | — | fail_precheck |
| **CB-CALL-HEAT** | CB≥128 热度广度→削 510300 | Sharpe+0.12；recon A≡B≡Beta | X2≈20.3% | **research_observe / 非独立 explore-pass**（vs IND-RATE-DIFF \|ρ\|≈0.985）；X2 MDD≈−24.3% 软风险 |

预检：`output/v3/pretest_batch_20261012_ortho3.json`

## CB-CALL-HEAT 对账回写（2026-10-12 03:05 ET）
| 项 | 结论 |
|---|---|
| Eng A≡B≡Beta | **pass_all=true**（执行可复现） |
| vs IND-RATE-DIFF | 日 \|ρ\|≈**0.985** → **near_relative** |
| **状态** | **research_observe / NOT independent explore-pass** |
| 软风险 | X2 MDD≈**−24.3%**（仍≤25% 探索口径） |
| 压舱 | **GOLD only** |

**教训：** 以「市场热度→削减 510300」为核的臂易坍缩到 IND-RATE-DIFF 同族；后续优先机制须与 IND-RATE-DIFF **低相关**（勿再开热度/拥挤→削宽基的换皮）。本任务 **不新开臂**。

## 定案补记（2026-10-12 03:07 ET）
- **CB-CALL-HEAT** = **research_observe only**（near_relative vs IND-RATE-DIFF）。
- **STOP**：CB heat / IND-RATE 近亲 / MATPREM 换皮；禁 510300 热度削仓臂。
- 下一正交批：CB 特异袖套 / 信用·平价带 / 事件冷却；**全量 CB 面板**；GOLD only。

## 正交批 ortho4（2026-10-12 03:08 ET）— CB 特异袖套（禁 510300 热度削仓）
| 臂 | 机制 | 预检 | 正式 | 交接 |
|---|---|---|---|---|
| **CB-CREDIT-RANK** | 低 `bond_over_rate`（≠ cb_over_rate） | avg≈5.3 Sharpe−0.02 | — | fail_precheck |
| **CB-PARITY-BAND** | 平价带[85,105] ADV 等权 | avg≈0.5 Sharpe+0.63 | X2≈16.7% **pass** | **YES** `handoff_strategy/cb_parity_band/`（X1 覆盖极薄） |
| **CB-RESET-COOL** | 下修 60 日冷却后 ADV 等权 | avg≈5.1 Sharpe+0.02 | X2 MDD≈−27% | fail_explore |

**CB-CALL-HEAT** 仍为 **research_observe**（near_relative vs IND-RATE）。GOLD only。全量面板。ANN park。
预检：`output/v3/pretest_batch_20261012_ortho4.json`

## Strategy 对账回写 — CB-PARITY-BAND（2026-10-12 03:11 ET）
| 项 | 结论 |
|---|---|
| EngA ≡ Beta | **是** |
| pass_all | **false** |
| vs CB-PREMRESID-COV | 日 ρ≈**0.90** → near_relative |
| vs IND-RATE-DIFF | 日 ρ≈**0.92** → near_relative |
| **状态** | **research_observe / 非独立 explore-pass** |
| 软风险 | X1 avg_names≈0.53、空仓≈83.9%、黄金≈91.9% |

路径：`output/strategy_recon/cb_parity_band/`  
**STOP**：再扩 COV / DIFF / PARITY 近亲。

## 正交批 ortho5（2026-10-12 04:45 ET）— 股债相关 / LPR水平 / 中期期限墙
硬禁：MATPREM 族、IND-RATE 变体、heat→切 510300、DD×GOLD、PARITY/COV 近亲、教科书动量、小盘、IC。  
压舱 **GOLD only（518880）**。HARD GATE：X1 Sharpe≤0 → fail_precheck。主表仅 60万/100万。`promotion_approved=false`。

| 臂 | 机制（唯一收益来源） | 预检 X1 avg_names / Sharpe | 正式 60万 X1/X2 CAGR/MDD/Sharpe | 处置 |
|---|---|---|---|---|
| **EQBOND-CORR** | 股债60d ρ 升→削510300抬GOLD | 1.0 / **−0.04** | — | **fail_precheck** |
| **LPR-LEVEL** | LPR 1Y 扩展z分档调510300（≠ΔON/斜率） | 1.0 / **+0.08** | X1 0.1%/−24.5%/0.08；X2 **18.1%/−19.0%/1.07** | **YES** `handoff_strategy/lpr_level/` |
| **CB-MATWALL-MID** | ytm∈[2,5] 日历供给 ADV 等权（≠MATPREM/平价带） | **3.52** / **+0.32** | X1 2.9%/−10.5%/0.32；X2 **20.5%/−22.6%/0.96** | **YES** `handoff_strategy/cb_matwall_mid/` |

软风险：LPR-LEVEL 为 510300↔GOLD 体制臂（X1 Sharpe 仅 0.08、MDD≈−24.5% 近闸）；CB-MATWALL-MID X1 池偏浅 avg≈3.5、空仓时黄金主导。  
预检：`output/v3/pretest_batch_20261012_ortho5.json`  
runner：`output/v3/run_ortho_batch5.py`  
**未开**：北向 z（X1 无覆盖）、put 底/近端墙[0.75,2]（avg_names≈0）、remain  shrinkage（X1 仅 2–3 只）。

## Strategy 对账回写 — ortho5（2026-10-12 04:57 ET）
| 臂 | 状态 |
|---|---|
| **LPR-LEVEL** | **near_relative**（高相关 DIFF/GOLD）→ 非独立 explore-pass |
| **CB-MATWALL-MID** | **research_observe**（EngA≡Beta；pass_all=false；非近亲） |
| EQBOND-CORR | fail_precheck（已台账） |

**STOP**：再扩 LPR / IND-RATE / MATWALL 期限墙近亲。

## 正交批 ortho6（2026-10-12 05:05 ET）— 债底带 / 国债折溢价 / 新券季养
硬禁：MATPREM、IND-RATE/LPR/heat→510300/EQBOND、MATWALL、PARITY/COV、DD×GOLD、动量/小盘/IC；另禁 PUT-AVOID/PUTPRESS/BONDVAL、LISTAGE×溢价、NAV-DISC(510300)。  
压舱 **GOLD only（518880）**。HARD GATE：X1 Sharpe≤0 → fail_precheck。主表仅 60万/100万。`promotion_approved=false`。

| 臂 | 机制（唯一收益来源） | 预检 X1 avg_names / Sharpe | 正式 60万 X1→X2 CAGR/MDD/Sharpe | 处置 |
|---|---|---|---|---|
| **CB-PUTFLOOR-NEAR** | close/bond_value∈[0.90,1.15] ADV 等权（债底保护错价） | **0.47** / **+0.35** | X1 3.6%/−12.5%/0.35 → X2 **13.2%/−22.5%/0.98** | **YES** `handoff_strategy/cb_putfloor_near/` |
| **BOND-NAV-MR** | 511010 折溢价扩展z → 国债ETF↔GOLD（无510300） | 1.0 / **+0.63** | X1 4.3%/−8.4%/0.63 → X2 **14.0%/−18.0%/1.09** | **YES** `handoff_strategy/bond_nav_mr/` |
| **CB-SEASON-NEW** | 上市龄∈[0,1]y ADV 等权（≠LISTAGE×低溢价） | **1.41** / **+0.34** | X1 3.5%/−12.6%/0.34 → X2 **17.4%/−25.0%/0.93** | **YES** `handoff_strategy/cb_season_new/`（60万过；**100万 X2 MDD≈−25.2% 未过**） |

软风险：PUTFLOOR X1 池极薄 avg≈0.47（空仓时黄金主导）；SEASON X2 MDD贴闸/−25%、100万破闸；BOND-NAV-MR 可能与 GOLD 压舱高相关（待 Strategy 对账）。  
跳过：北向z（X1 无覆盖）、商品除金（X1=0）、remain 稀缺（X1≈0）。  
预检：`output/v3/pretest_batch_20261012_ortho6.json`  
runner：`output/v3/run_ortho_batch6.py`  
prereg：`V3_CB_PUTFLOOR_NEAR_PREREG.md` / `V3_BOND_NAV_MR_PREREG.md` / `V3_CB_SEASON_NEW_PREREG.md`

## Strategy 对账回写 — ortho6（2026-10-12 05:07 ET）
| 臂 | 状态 |
|---|---|
| **CB-PUTFLOOR-NEAR** | **research_observe**（非独立 explore-pass） |
| **BOND-NAV-MR** | **research_observe**（vs GOLD ρ≈0.57，压舱近亲闸未触发但仍观察） |
| **CB-SEASON-NEW** | **research_observe**（100万 X2 MDD 未过） |

GOLD only；`promotion_approved=false`。禁再扩这三近亲。



## 正交批 ortho_ext1（2026-10-12 05:20 ET）— 外部机制消化落地
依据：`docs/v2/EXTERNAL_BETA_DIGEST_ORTHO_ZH.md`（华泰 PR 中性化公式、arxiv 2409.06496 LSMC、Moreira/Muir VM、他思双低失效）。  
硬禁：MATPREM / IND-RATE/LPR/heat→510300 / MATWALL / PARITY / PREMRESID / PUTFLOOR / BOND-NAV-MR / SEASON / 双低 / 动量 / IC；**禁扩 ortho6 近亲**。  
压舱 **GOLD only**。HARD GATE：X1 Sharpe≤0 → fail_precheck。主表仅 60万/100万。`promotion_approved=false`。

| 臂 | 机制 / 谁付钱 | 预检 X1 avg/Sharpe | 正式 60万 X2 CAGR/MDD/Sharpe | 处置 |
|---|---|---|---|---|
| **SHIBOR-ROLL-BOND** | 1y−1m 扩展z→久期/货币；余GOLD / 远期·久期对冲机构 | 1.0 / **+0.61** | **12.3%/−16.7%/1.06** | **YES** `handoff_strategy/shibor_roll_bond/` |
| **TF-T-CURVE** | TF−T 结算价差z→511010/GOLD / 期货展期流量 | 1.0 / **+0.49** | 18.8%/−**25.2%**/1.03 | **fail_explore**（X2 MDD 破闸） |
| **CB-MIDCONVEX** | 溢价[15,55]∧价[100,130] ADV 中凸性 / 追高Δ抛售者 | **2.16** / **+0.42** | **13.1%/−23.0%/0.95** | **YES** `handoff_strategy/cb_midconvex/` |

软风险：SHIBOR X2 CAGR 仅贴 12% 闸；MIDCONVEX X1 池偏浅 avg≈2.2、换手偏高；TF-T 收益高但 MDD 破闸。  
跳过（消化层）：华泰完整 PR 残差（=PREMRESID 近亲+缺评级）、完整 LSMC、权益 VM→510300、债/金 VM 当 Alpha、双低主线、北向（X1 无覆盖）。  
预检：`output/v3/pretest_batch_20261012_ortho_ext1.json`  
runner：`output/v3/run_ortho_ext1.py`


## 正交批 ortho_ext1b（2026-10-12 05:25 ET）— 消化文档 P0 两臂
兄弟批 `ortho_ext1` 已交接 SHIBOR-ROLL-BOND / CB-MIDCONVEX（TF-T-CURVE fail_explore）；**本批不重做**。  
依据：`docs/v2/EXTERNAL_BETA_DIGEST_ORTHO_ZH.md` §1–2。压舱 **GOLD only**。`promotion_approved=false`。

| 臂 | 机制（唯一收益来源） | 预检 X1 avg/Sharpe | 正式 60万 X1→X2 | 处置 |
|---|---|---|---|---|
| **CB-PR-NEUT-R9** | 中性化 PR 残差第8–9分位（避第10；缺评级简化） | **0.00** / +0.46 | — | **fail_precheck**（X1 `amount≥3000` 下 n_ols 不足十分位） |
| **CB-CLAUSE-MISPR** | 条款态（事件∪close≥125）下相对 max(债底,平价) 低估分 ADV | **0.03** / **+0.49** | X1 5.6%/−12.5%/0.49 → X2 **31.5%/−14.4%/1.33** | **YES** `handoff_strategy/cb_clause_mispr/` |

软风险：CLAUSE X1 池极薄 avg≈0.03（黄金主导）；S 窗 MDD≈−27%（探索闸仅 X1+X2）。  
**PR-NEUT 正交义务**：若日后重开/有覆盖，Strategy 必须测 vs **PREMRESID-COV** 日相关，`|ρ|>0.85` → near_relative（消化文档近亲风险）；SHORT 已写明。  
预检：`output/v3/pretest_batch_20261012_ortho_ext1b.json`  
runner：`output/v3/run_ortho_batch_ext1b.py`  
prereg：`V3_CB_PR_NEUT_R9_PREREG.md` / `V3_CB_CLAUSE_MISPR_PREREG.md`


## smoke_evtflow_indetf（2026-10-12 06:05 ET）— 事件/资金结构 + 行业ETF 冒烟
Leo 当面确认：暂停 CB/利率/GOLD 压舱同族扩臂；两条冒烟；压舱改 **511880**（现金类，非 GOLD）；`promotion_approved=false`。
硬禁：CALL-HEAT / IND-RATE 换皮 / MARGIN-DELTA 近亲 / 教科书动量主线 / 小盘 / IC。

| 臂 | 线 | 机制 / 谁付钱 | X1 | 正式 | vs IND-RATE-DIFF | 处置 |
|---|---|---|---|---|---|---|
| **DT-INST-BREADTH** | 事件 | 龙虎机构净买广度→加510300 / 披露后追热游资 | 无覆盖 | — | — | **coverage_blocked_X1**（龙虎榜自2018） |
| **MARGIN-PX-DIV** | 资金 | 两融Δ20 z×股价背离 / 顺周期融资客 | Sharpe≈0.00 avg=1 | X2 CAGR≈4.4% | X1 ρ≈0.85 / X2≈0.60 | **fail_explore**（+near_relative 软标） |
| **NB-MARGIN-DIV** | 资金 | 北向z vs 两融z 背离 | 无覆盖 | — | — | **coverage_blocked_X1**（北向自2018） |
| **IND-SHARE-REV** | 行业ETF | 份额变化率截面反转轮动 / 高位申购散户 | Sharpe≈−0.34 avg≈2.7 | — | — | **fail_precheck** |
| **E0-IND-EQW** | 对照 | 行业ETF等权对照 | Sharpe≈−0.43 avg≈3.5 | — | — | **fail_precheck**（control） |

**handoff: NO**。runner：`output/v3/run_smoke_evtflow_indetf.py`；预检：`output/v3/pretest_batch_20261012_smoke_evtflow_indetf.json`。  
prereg：`V3_DT_INST_BREADTH_PREREG.md` / `V3_MARGIN_PX_DIV_PREREG.md` / `V3_NB_MARGIN_DIV_PREREG.md` / `V3_IND_SHARE_REV_PREREG.md` / `V3_E0_IND_EQW_PREREG.md`。  
覆盖缺口（冒烟当时）：龙虎/北向曾无 X1；**Data 2026-10-12 已补齐**（见下节重跑）。行业ETF X1 可交易行业日均约 3–4（稀疏属实）。注明 fund_div 缺失保守偏差。

### MARGIN-PX-DIV 重跑（2026-10-12 ~06:30 ET）— merged available_at
Leo：两融 2014–17 本地已有，勿再喊缺数。合并 `data/v2/margin/margin_exchange_daily_merged.parquet`（2014-01-02→2026-10-09；X1 交易日=634）。
- **2014–17 PIT**：`available_at` backfill = 下一 SSE 交易日 09:00 Asia/Shanghai；`promotion_approved=false`。
- **2018+**：as-filed（当前为 T 日 18:00）；runner 按 prereg 傍晚披露→下一开盘可用。
- 压舱 **511880**；AUM 60/100万；禁 CB/利率/GOLD 同族。

| 窗 | 60万 CAGR/MDD/Sharpe | 100万 |
|---|---|---|
| X1 | −0.5%/−19.2%/0.00 | −0.5%/−19.2%/0.00 |
| X2 | 4.4%/−6.8%/0.64 | 4.5%/−6.7%/0.64 |
| S | 2.5%/−12.1%/0.39 | 2.5%/−12.1%/0.39 |

vs IND-RATE-DIFF 日相关：X1 ρ≈0.85 / X2≈0.60 → **near_relative 软标**。  
**处置：fail_explore**（X2 CAGR<12%）；**无交接**。龙虎/北向 X1 补齐后见下节（不磨本臂）。  
runner：`output/v3/run_margin_px_div_rerun.py`；结果：`output/v3/margin_px_div/`。

### DT-INST-BREADTH + NB-MARGIN-DIV X1 重跑（2026-10-12 ~19:15 ET）
Data 回执：`docs/v2/BETA_X1_EVT_FLOW_COVERAGE.md`。龙虎 `top_inst_labeled` 20150105→20261009（seat_type）；北向 `moneyflow_hsgt_daily_2014plus.parquet` date_min=20141117。  
PIT：龙虎 `available_at_alpha_conservative`=T+1 15:00→T+2 开盘；北向/两融 available_at→次一开盘；**不可前移**。压舱 **511880**；AUM 60/100万；`promotion_approved=false`。不磨 MARGIN-PX-DIV；不开行业 ETF / CB/利率同族。

| 臂 | X1（60万）CAGR/MDD/Sharpe | X2（60万） | vs IND-RATE ρ | 处置 |
|---|---|---|---|---|
| **DT-INST-BREADTH** | −0.2%/−17.9%/0.02（signal_days=634） | 3.4%/−7.0%/0.45 | X1≈0.83 / X2≈0.61 | **fail_explore**（X2 CAGR≪12%） |
| **NB-MARGIN-DIV** | −1.6%/−22.3%/−0.11（signal_days=634） | — | — | **fail_precheck**（X1 Sharpe≤0） |

**handoff: NO**。runner：`output/v3/run_dt_nb_x1_rerun.py`；预检：`output/v3/pretest_batch_20261012_dt_nb_x1_rerun.json`；结果：`output/v3/dt_inst_breadth/`、`output/v3/nb_margin_div/`。  
prereg 已修订：`V3_DT_INST_BREADTH_PREREG.md` / `V3_NB_MARGIN_DIV_PREREG.md`（旧 coverage_blocked_X1 作废）。

## stock_etf_smoke（2026-10-12 07:24 ET prereg → 07:27 ET 跑完）— 个股+ETF 主线切换
Leo/New Bot：主线改为 **个股+ETF 袖套**，非 MATPREM+GOLD 主书；**暂停** CB/国债/黄金同族扩臂；DT/NB 宽基择时已 fail 不重复。残差 **510300**（非黄金主仓）。AUM 仅 60/100万；禁小盘；`promotion_approved=false`。

股票池：CSI300∪CSI500（`index_weight` asof，自 20180131）；**X1 权重缺失段**用流通市值 PIT **top800** 近似（已文档化）；滤 ST、价&lt;2。

| 臂 | 机制 / 谁付钱 | X1 | 正式/描述 | 处置 |
|---|---|---|---|---|
| **EVT-DT-INST-STOCK** | 龙虎机构净买强度→中大盘等权 top25；残差510300 / 披露后追席位的游资散户 | Sharpe≈**−0.55** avg_names≈10.0 | 未开正式 | **fail_precheck** |
| **EVT-ANN-POLARITY-STOCK** | 公告正极性(回购/增持/预增)−负过滤→中大盘；残差510300 | 无覆盖 | descriptive S CAGR≈−6.8%/MDD−44%/Sh−0.30；X2 ≈5.6%/−15.8%/0.39 | **coverage_blocked_X1**（公告 PIT 自 20180101） |

vs IND-RATE / MATPREM：预检未过，未算正式 ρ。  
**handoff: NO**。runner：`output/v3/run_stock_etf_smoke.py`；预检：`output/v3/pretest_batch_20261012_stock_etf_smoke.json`；结果：`output/v3/evt_dt_inst_stock/`、`output/v3/evt_ann_polarity_stock/`。  
prereg（跑前）：`V3_EVT_DT_INST_STOCK_PREREG.md` / `V3_EVT_ANN_POLARITY_STOCK_PREREG.md`。

## limitup_unlock_smoke（2026-10-12 07:35 ET prereg → 07:38 ET 跑完）— New Bot 下一指令
Leo/New Bot：勿磨 EVT-DT / EVT-ANN。开 **LIMITUP-FADE-REV** + **UNLOCK-WINDOW-RESID**。  
股票池同 `stock_etf_smoke`（CSI300∪CSI500 asof；X1 用流通市值 top800 近似）；残差 **510300**；禁小盘；禁 CB/金/债同族主仓；AUM 60/100万；`promotion_approved=false`。

| 臂 | 机制 / 谁付钱 | X1 | 正式/描述 | 处置 |
|---|---|---|---|---|
| **LIMITUP-FADE-REV** | 涨停T→T+1开收&lt;0→T+2入场 HOLD=3 等权；限价制度事件≠120d动量 / 打板失败散户游资 | Sharpe≈**-0.68** avg_names≈9.5 | 未开正式 | **fail_precheck** |
| **UNLOCK-WINDOW-RESID** | 解禁前20d相对510300残差&lt;0→解禁窗持有 / 解禁被迫卖盘 | 无覆盖（float_date 自 2018-01-02） | descriptive S CAGR≈-1.0%/MDD-41.2%/Sh0.04；X2 ≈12.9%/-16.1%/0.72（avg≈1.5） | **coverage_blocked_X1** |

数据：`share_float_2018plus.parquet` float_date **2018-01-02→2026-10-30**；raw 无 2015–17 fday → 不解禁 X1。涨停信号来自 local panels `limit_up`（缺则 pct 代理）。  
**handoff: NO**。runner：`output/v3/run_limitup_unlock_smoke.py`；预检：`output/v3/pretest_batch_20261012_limitup_unlock.json`；结果：`output/v3/limitup_fade_rev/`、`output/v3/unlock_window_resid/`。  
prereg（跑前）：`V3_LIMITUP_FADE_REV_PREREG.md` / `V3_UNLOCK_WINDOW_RESID_PREREG.md`。

## etf_timing_v20（2026-10-12 07:47 ET）— AI Track B 交 Beta 复核

包 ICIR 虚高=份额流自相关；真实行业 ETF 收益+60万 X1 冒烟 **T1–T10 全 fail_precheck**。  
残差 511880；禁小盘/CB/金主仓；**无交接**。详见 `docs/v2/AI_V20_ETF_TIMING_BETA_REVIEW_ZH.md`。  
runner：`output/v3/run_etf_timing_v20_smoke.py`；batch：`output/v3/pretest_batch_20261012_etf_timing_v20.json`。

## etf_timing_v21_ret（2026-10-12 07:51 ET）— AI 收益化标签交 Beta 复核

标签已换 fwd excess vs 510300（非流延续），但包 ICIR≈1.6 **≈ trade_date 泄漏**（PIT≈−0.1）；60万 X1 **R1–R10 全 fail_precheck**。  
残差 511880；禁小盘/CB/金主仓；**无交接**。详见 `docs/v2/AI_V21_ETF_TIMING_RET_BETA_REVIEW_ZH.md`。  
runner：`output/v3/run_etf_timing_v21_ret_smoke.py`；batch：`output/v3/pretest_batch_20261012_etf_timing_v21_ret.json`。

## ortho_relmom_pxvol（2026-10-12 19:53 ET prereg → 19:55 ET 跑完）— 等 v22；禁份额流同构

New Bot：等 AI v22 PIT 期间开两探索臂；**禁** IND-CREATE/NAV/share_flow 同构；残差 **510300**（非 GOLD）；禁小盘（宽基池排除 512100）；AUM 60/100万；`promotion_approved=false`。

| 臂 | 机制 / 谁付钱 | X1（60万） | 处置 |
|---|---|---|---|
| **IND-REL-MOM-RESID** | 行业 ETF 20d RS−CS均值 → 顶 tercile 70% + 510300 30% / 分步加仓机构配置盘（探索；教科书动量风险已标） | CAGR≈−18.2%/MDD−52.4%/Sh≈**−0.60** avg≈3.53 | **fail_precheck** |
| **BROAD-ETF-PXVOL-CROWD** | 宽基(510300/510500/159915/510050) turnover_z 拥挤→低拥挤加权 / 晚到流动性追逐者 | CAGR≈−10.8%/MDD−47.1%/Sh≈**−0.18** avg≈3.38 | **fail_precheck** |

**handoff: NO**。未开正式、未算 vs IND-RATE ρ。  
runner：`output/v3/run_ortho_relmom_pxvol.py`；预检：`output/v3/pretest_batch_20261012_ortho_relmom_pxvol.json`；结果：`output/v3/ind_rel_mom_resid/`、`output/v3/broad_etf_pxvol_crowd/`。  
prereg（跑前）：`V3_IND_REL_MOM_RESID_PREREG.md` / `V3_BROAD_ETF_PXVOL_CROWD_PREREG.md`。

## etf_timing_v22_pit（2026-10-12 19:59 ET）— AI PIT asof 交 Beta 复核

PIT asof 接线过关（`available_at≤D 09:00`；≈76%/24% 次日/当日）；标签 fwd excess vs 510300。流自相关仍极强；包窗高 PIT（`abs(flow)` PIT≈2.9 vs LEAK≈−0.8）不可外推。60万 X1 **P1–P10 全 fail_precheck**。  
残差 **510300**；禁小盘/CB/金主仓；**无交接**。详见 `docs/v2/AI_V22_ETF_TIMING_RET_PIT_BETA_REVIEW_ZH.md`。  
runner：`output/v3/run_etf_timing_v22_pit_smoke.py`；batch：`output/v3/pretest_batch_20261012_etf_timing_v22_pit.json`。
