# 多袖套组合账本（Strategy，2026-10-11）— 研究级，promotion_approved=false
> **2026-10-12 架构三条落地**：默认袖套已改为 `core=1.0`（stock/alpha 预留）；Mandate=`MANDATE_UNIFIED_STOCK_ETF_20261012_ZH.md`；事件窗闸=`EVENT_ARM_WINDOW_GATES_ZH.md`；Book-Smoke=`python3 -m quantlab.portfolio.book_smoke`。下文大量 CB/金主表试配段落视为 **HISTORICAL_ONLY**。


> **2026-10-12 主线切换草案**：个股篮子 + ETF 袖套为主书；CB/金仅对照。 Mandate：`docs/v2/MANDATE_DRAFT_STOCK_ETF_MAINLINE_ZH.md`。 下文旧 MATPREM+GOLD 主表试配段落视为历史，待 Leo 确认后整体改写。

## 更新 2026-10-12T19:55:00-04:00（Beta：ortho_relmom_pxvol 两臂 fail_precheck）

- 等 v22；禁份额流同构；残差 510300；禁小盘/CB/金。
- **IND-REL-MOM-RESID** X1 Sh≈−0.60 → **fail_precheck**；**BROAD-ETF-PXVOL-CROWD** X1 Sh≈−0.18 → **fail_precheck**。
- 台账：`descriptive_IND_REL_MOM_RESID_fail_precheck` / `descriptive_BROAD_ETF_PXVOL_CROWD_fail_precheck`。**promotion_approved=false**。无交接。

方向（Leo）：不做小盘；主攻事件驱动+资金结构（Alpha，待接）；常见因子/静态组合只作对照。

代码：`quantlab/portfolio/v2_multisleeve_book.py`
```
python3 -m quantlab.portfolio.v2_multisleeve_book                      # BOOK,C0-C3 × exploration,dev
python3 -m quantlab.portfolio.v2_multisleeve_book --arms BOOK --windows exploration \
   --sleeves '{"core":0.4,"marp":0.25,"e2":0.15,"cb":0.2,"alpha_event":0}' \
   --target-vol 0.10 --leverage 1.0 --cash-target 0.02 [--alpha-event-path x.parquet] --out output/strategy_mbook
```
袖套：core=510300 持有；marp=Beta MA-RP（510300/511010/518880 逆60日波动，月度）；e2=Beta E2（宽基20日动量择一，负动量空仓；默认池去掉 512100=中证1000，按"不碰小盘"）；cb=Beta CB1 双低（前20，ADV≥1000万，剩余期限≥182天，每10日）；alpha_event=占位接口（长表 session,instrument_id,weight），当前为空。
合成：最终权重=Σ袖套权重×袖套内权重（最新信号前向保持），在所有信号日并集上下单；袖套内空仓部分停 511880，闲置现金目标 2%（硬上限 5%）。成本由引擎按最终持仓计算（袖套间对冲净额化）。
引擎：run_weight_schedule + ExecConfig.strategy_v1(impact_k=1.0)，corporate_actions=True，no_limit_codes={'sh.510300'}，min_trade_value=2000，现金按 511880 每日收益计息，record_weights=True。
杠杆：--leverage 默认 1.0（关）。>1 仅研究参数，未获 Mandate 批准；且引擎无融资账户，买入受现金约束，实际总仓位被截在 ~1.0 —— 目前不可执行。
输出（每窗口/每臂）：target_weights.parquet / actual_weights.parquet（长表）、nav.csv（含 idle_cash）、sleeve_weights.csv、summary.json（return_basis、data_hashes、window_label、leverage 说明）；汇总 compare_table.json。
窗口：dev=2018-01-02..2024-05-31（开发验证窗）；exploration=2024-06-03..2026-10-09（只作探索）。

## 更新 2026-10-12T06:55:00-04:00（Beta：ortho_evt_ind3_full 两臂 fail_precheck）

- 修 map-pit 过窄 → **全宇宙** `category==行业` + amt20≥1000 + listed≥60；持仓=行业篮（非 510300 削仓）；GOLD only。
- **IND-CREATE-REV-FULL** / **IND-NAV-CHEAP-FULL**：X1 avg_names≈**3.53**（达标），但 Sharpe≈**−0.36 / −0.67** → **fail_precheck**；无正式、无交接、未报 ρ。
- 台账：`descriptive_IND_CREATE_REV_FULL_fail_precheck` / `descriptive_IND_NAV_CHEAP_FULL_fail_precheck`。**promotion_approved=false**。

## 更新 2026-10-12T05:16:44-04:00（Strategy：ortho_ext1b CLAUSE-MISPR research_observe；PR-NEUT-R9 fail_precheck）

- **CB-CLAUSE-MISPR**：EngA≡Beta；**pass_all=false**（X2 A–B隙）；CB/利率 |ρ|&lt;0.85；X2≈**31.5%**/−14.4%/1.33；**X1 avg≈0.04 几乎全GOLD（ballast_dominated）**；Beta S MDD≈−27%。台账：`descriptive_CB_CLAUSE_MISPR_recon_AB_gap_research_observe`。
- **CB-PR-NEUT-R9**：**fail_precheck**（avg_names=0；Sharpe≈0.46）；无交接；与 PREMRESID-COV 同族近亲风险，重开必测 ρ。台账：`descriptive_CB_PR_NEUT_R9_fail_precheck`。
- **非独立 explore-pass**。压舱/主表试配不变。**promotion_approved=false**；禁小盘。

## 更新 2026-10-12T05:14:31-04:00（Strategy：ortho_ext1 SHIBOR/MIDCONVEX near_relative；TF fail_explore）

- **SHIBOR-ROLL-BOND**：pass_all=true；**vs BOND-NAV≈0.999 / DIFF≈0.89** → near_relative。X2≈**12.3%**（贴12%闸）/−16.7%/1.06；vs GOLD≈0.57。台账：`descriptive_SHIBOR_ROLL_BOND_near_relative_research_observe`。
- **CB-MIDCONVEX**：EngA≡Beta；pass_all=false；**vs PARITY≈0.980 / COV≈0.904** → near_relative。X2≈13.1%/−23.0%/0.95；X1 avg≈2.19。台账：`descriptive_CB_MIDCONVEX_near_relative_research_observe`。
- **TF-T-CURVE**：fail_explore（X2 MDD≈−25.2%）；无交接；台账：`descriptive_TF_T_CURVE_fail_explore`。
- 均**非独立 explore-pass**。压舱/主表试配不变。**promotion_approved=false**；禁小盘。

## 更新 2026-10-12T05:07:26-04:00（Strategy：ortho6 PUTFLOOR/BOND near_relative；SEASON 档位失败）

- **CB-PUTFLOOR-NEAR**：pass_all=true；**vs PARITY≈0.958 / COV≈0.927** → near_relative → research_observe。X2≈13.2%/−22.5%/0.98；**X1 avg_names≈0.46 黄金主导**。台账：`descriptive_CB_PUTFLOOR_NEAR_near_relative_research_observe`。
- **BOND-NAV-MR**：pass_all=true；**vs GOLD≈0.57（压舱近亲闸未触发）**；vs DIFF≈0.89 → near_relative。X2≈14.0%/−18.0%/1.09；无510300。台账：`descriptive_BOND_NAV_MR_near_relative_research_observe`。
- **CB-SEASON-NEW**：EngA≡Beta；pass_all=false；**100万 X2 MDD≈−25.19% 未过**（60万−25.00%贴闸）；vs PARITY≈0.88 → near_relative。台账：`descriptive_CB_SEASON_NEW_tier_fail_near_relative_research_observe`。
- 三臂均**非独立 explore-pass**。压舱/主表试配不变。**promotion_approved=false**；禁小盘。

## 更新 2026-10-12T04:44:55-04:00（Strategy：ortho5 LPR near_relative；MATWALL A–B gap；EQBOND fail_precheck）

- **LPR-LEVEL**：两引擎对账 OK（`pass_all=true`；panel=`full`）；**vs IND-RATE-DIFF≈0.978 / GOLD-BETA≈0.913 / PARITY≈0.898** → **near_relative** → **research_observe**（**勿当独立 explore-pass**）。X2≈**18.11%/18.13%**、MDD≈−19.0%；**X1 Sharpe≈0.08 / MDD≈−24.45%（近25%）**。GOLD only。台账：`descriptive_LPR_LEVEL_near_relative_research_observe`。
- **CB-MATWALL-MID**：EngA≡Beta；**pass_all=false**（A–B 绝对阈）；全部 |ρ|≤0.85（最大 vs PARITY≈0.825）→ **research_observe**（**勿当独立 explore-pass**）。X2≈**20.51%/21.28%**、MDD≈**−22.6%**；**X1 avg_names≈3.55**（空仓≈34.4%；黄金≈67.2%）。台账：`descriptive_CB_MATWALL_MID_recon_AB_gap_research_observe`。
- **EQBOND-CORR**：**fail_precheck**（Sharpe≈**−0.04**；avg_names=1.00）；无交接；ortho5；台账：`descriptive_EQBOND_CORR_fail_precheck`。
- **压舱不变（P0-4）**：主表试配 **GOLD-BETA**；**DD-BALLAST = watch_only**；禁双压舱叠满。
- 主表试配草案：MATPREM 族唯一 primary + GOLD-BETA；近亲只观察。explore-pass 候选**不变**。
- **promotion_approved=false**；禁小盘；密封窗未重跑。

## 更新 2026-10-12T03:12:20-04:00（Strategy：CB-PARITY-BAND 近亲观察；CREDIT/RESET 台账）

- **CB-PARITY-BAND**：EngA≡Beta（宣称对齐）；**pass_all=false**（EngA–EngB 绝对阈未过）；**vs PREMRESID-COV 日/周≈0.897/0.878** + **vs IND-RATE-DIFF≈0.918/0.876** → **near_relative** → **research_observe**（**勿当独立 explore-pass**）。X2≈**16.74%/16.67%**、MDD≈**−22.2%**；**X1 avg_names≈0.53（黄金主导；空仓≈83.9%）**。vs MATPREM≈0.56。GOLD only；panel=full。台账：`descriptive_CB_PARITY_BAND_near_relative_research_observe`。
- **CB-CREDIT-RANK**：**fail_precheck**（X1 Sharpe≈**−0.02**；avg_names≈5.3）；无交接；ortho4；台账：`descriptive_CB_CREDIT_RANK_fail_precheck`。
- **CB-RESET-COOL**：**fail_explore**（X2 MDD≈**−27.4%**>25%；60/100万）；无交接；ortho4；台账：`descriptive_CB_RESET_COOL_fail_explore`。
- **压舱不变（P0-4）**：主表试配 **GOLD-BETA**；**DD-BALLAST = watch_only**；禁双压舱叠满。
- explore-pass 候选**不变**（PARITY-BAND 不进独立列表）。
- **promotion_approved=false**；禁小盘；密封窗未重跑。

## 更新 2026-10-12T03:04:31-04:00（Strategy：CB-CALL-HEAT 近亲观察；MARGIN/PUT 预检失败）

- **CB-CALL-HEAT**：两引擎对账 OK（`pass_all=true`；panel=`full`）；**vs IND-RATE-DIFF 日/周≈0.985/0.976** + **vs CB-PREMRESID-COV≈0.880/0.840** → **near_relative** → **research_observe**（**勿当独立 explore-pass**）。X2≈**20.27%/20.26%**、MDD≈**−24.3%**（近 Mandate 25%）；X1 Sharpe≈0.12 / MDD≈−22.2%。GOLD only。台账：`descriptive_CB_CALL_HEAT_near_relative_research_observe`。
- **MARGIN-DELTA**：**fail_precheck**（X1 Sharpe≈**−0.03**）；无交接；台账：`descriptive_MARGIN_DELTA_fail_precheck`。
- **CB-PUT-AVOID**：**fail_precheck**（X1 Sharpe≈**−0.50**；avg_names≈5.55）；无交接；台账：`descriptive_CB_PUT_AVOID_fail_precheck`。
- **压舱不变（P0-4）**：主表试配 **GOLD-BETA**；**DD-BALLAST = watch_only**；禁双压舱叠满。
- explore-pass 候选**不变**（CALL-HEAT 不进独立列表）。
- **promotion_approved=false**；禁小盘；密封窗未重跑。

## 更新 2026-10-12T02:58:12-04:00（Strategy：COV 全量面板 explore-pass；P90 近亲观察；CONV fail_precheck）

- **CB-PREMRESID-COV**：NAV 缺口修复（全量 `cb_panels`，去 `filter_cb_panels`）后 **pass_all=true** → **explore-pass**（研究级；**非晋级**）。主表 60/100万 X2≈**25.51%/25.72%**、MDD≈**−17.48/−17.23%**；X1 空仓≈**25.8%** / avg_names≈5.19。审计 `output/v3/cb_premresid_cov/NAV_GAP_AUDIT_ZH.md`。台账：`descriptive_CB_PREMRESID_COV_explore_pass_recon_fullpanel`。
- **IND-RATE-P90**：两引擎对账 OK；**vs IND-RATE-DIFF 日/周相关≈0.995/0.993** → **near_relative** → **research_observe / 族内 secondary**（**勿当独立 explore-pass**）。X2≈**24.34%** / −18.63% / 1.31；X1 Sharpe≈0.19 / MDD≈−19.5%。台账：`descriptive_IND_RATE_P90_near_relative_research_observe`。
- **CB-PREMRES-CONV**：**fail_precheck**（X1 Sharpe≈**−0.14**；avg_names≈7.3）；无交接；台账：`descriptive_CB_PREMRES_CONV_fail_precheck`。
- **压舱不变（P0-4）**：主表试配 **GOLD-BETA**；**DD-BALLAST = watch_only**；禁双压舱叠满。
- explore-pass 候选现含：**… + IND-RATE-DIFF + CB-PREMRESID-COV**（研究级；**非晋级**）；P90 不进独立列表。
- **promotion_approved=false**；禁小盘；密封窗未重跑。

## 更新 2026-10-12T02:50:30-04:00（Strategy：IND-RATE-DIFF 两引擎对账通过）

- **IND-RATE-DIFF**（行业 ETF 份额 Δ5 变化率→削 510300 + **GOLD only**；≠裸净流入；≠DD-BALLAST 袖套）：explore-pass + Strategy 对账 OK；主表 60万/100万 X2≈**24.66%/24.65%**、MDD≈−16.52/−16.54%、夏普≈1.34；**X1 软风险 Sharpe≈0.12 / MDD≈−22.2%**。
- 对账 `output/strategy_recon/ind_rate_diff/`（A≡B≡Beta；pass_all=true）。成本/AUM X1≈0.08–0.09%、X2≈0.29–0.31%；年化换手 X1≈0.27 / X2≈1.23。
- **CB-PREMRESID-COV** 仍为引擎自洽 / pass_all=false（研究观察，不进晋级候选）。
- explore-pass 候选现含：**… + IND-RATE-DIFF**（研究级；**非晋级**）；压舱仍 GOLD 主表 / DD watch_only。
- 台账：`descriptive_IND_RATE_DIFF_explore_pass_recon`；`docs/trial_ledger.csv` → `IND-RATE-DIFF_strategy_recon`。
- **promotion_approved=false**；禁小盘；禁 DD×GOLD 叠满。

## 更新 2026-10-12T02:48:57-04:00（Strategy：CB-PREMRESID-COV 两引擎对账 — 引擎自洽 / pass_all=false）

- **CB-PREMRESID-COV**（溢价残差×ytm[0.5,5] + **GOLD only**；≠MATPREM 原低溢价）：Eng A≡B（Δ=0）；**vs Beta NAV 未过阈** → `pass_nav/pass_metrics/pass_all=false`。
- 主表 EngA 60/100万：X2≈**25.20%/25.04%**、MDD≈**−17.78%**；X1≈**2.79%/2.77%**、空仓≈**25.8%**、avg_names≈**5.19**。
- 成本/AUM：X1≈0.32–0.35%；X2≈1.11–1.31%。年化换手(1-way) X1≈1.35 / X2≈4.77。
- vs MATPREM X2 日/周相关≈**0.50 / 0.45**（**非近亲**，阈 0.85）。
- **不进 explore-pass 晋级候选**（研究观察）；压舱仍 **GOLD 主表 / DD watch_only**；禁叠 DD。
- 短报：`output/strategy_recon/cb_premresid_cov/SHORT_ZH.md`；台账：`descriptive_CB_PREMRESID_COV_recon_engine_ok_beta_gap`。
- **promotion_approved=false**；禁小盘；密封窗未重跑。

## 更新 2026-10-12T02:44:56-04:00（Strategy：台账补记 Beta P0 CB-PREMRESID / SECT-FLOW-DISP / IND-CROWD-REV）

- Beta `CB-PREMRESID`：**fail_explore / 无交接**；主表 60万/100万 X2≈**10.5–10.6%**&lt;12%；X1 avg_names=**0**（空仓→纯债夏普）。P0-3 方向失败 → 禁再扩 MATPREM 近亲切片。
- Beta `SECT-FLOW-DISP`：**fail_precheck / CLOSED**（`CLOSED_after_pretest_superseded_by_P0-5_crowding`）；X1 Sharpe≈**−0.072**；未开正式双窗。
- Beta `IND-CROWD-REV`：**fail_precheck**；X1 Sharpe≈**−0.050**；未开正式双窗；拥挤广度≠裸流入。
- **P0-4 压舱不变**：主表试配 **GOLD-BETA**；**DD-BALLAST = watch_only**；**禁 DD×GOLD 双压舱叠满**。
- **explore-pass 候选不变**：CB-MATPREM + MP-NEAR + MP-MERGE + MP-RELAX + GOLD-BETA（主表试配压舱）+ DD-BALLAST（watch_only）（研究级；**非晋级**）。
- 台账：`descriptive_CB_PREMRESID_fail_explore` / `descriptive_SECT_FLOW_DISP_fail_precheck` / `descriptive_IND_CROWD_REV_fail_precheck`。
- `promotion_approved=false`；禁小盘；未触碰 `strategy_recon/`。

## 更新 2026-10-12T02:40:06-04:00（Strategy：P0-4 压舱二选一 + LOO 门槛草案落地）

- **P0-4：** 主表试配压舱优先 **GOLD-BETA**；**DD-BALLAST → watch_only / 对照**（对账记录保留，不删表）。
- **硬闸：** `|ρ_daily(DD,GOLD)|≈0.97 > 0.70` → **禁 DD×GOLD 双压舱叠满**进主表试配；50/50 DD+GOLD 仅历史诊断。
- **LOO / 边际贡献门槛草案：** `docs/v2/STRATEGY_BALLAST_CHOOSE_ONE_AND_LOO_DRAFT_ZH.md`（研究级；附录 60万等权 NAV 插图非闸门证据）。
- Primary 提案（非晋升）：**MATPREM + GOLD-BETA**；NEAR/MERGE/RELAX 默认 secondary。
- **promotion_approved=false**（未改）；禁小盘；未跑重对账 / 未改 Mandate / 未写权重 JSON。
- 审计来源：`output/d1/EXTERNAL_AI_BETA_ALPHA_GAP_AUDIT_ZH.md` §P0-4；overlay：`output/strategy_recon/dd_matprem_overlay/SHORT_ZH.md`。

## 更新 2026-10-12T02:24:21-04:00（Strategy：台账补记 roundH/I SHIBOR-dON/DEF35-RP + 预检关闭臂）

- Beta `SHIBOR-dON`：**fail_explore / 无交接**；主表 60万/100万 X2≈**6.8%**&lt;12%。
- Beta `DEF35-RP`：**fail_explore / 无交接**；主表 60万/100万 X2≈**1.5%**&lt;12%；伪夏普（超低波）。
- Beta `EQ-RP500` / `BOND-VOL` / `REL500`（roundH）与 `ETF-FLOW-NET` / `CASH-TRIG25`（roundI）：**fail_precheck**（未开正式双窗）。
- **explore-pass 候选不变**：CB-MATPREM + MP-NEAR + MP-MERGE + MP-RELAX + DD-BALLAST + GOLD-BETA（研究级；**非晋级**）；**DD×GOLD≈0.97**（分散弱，见 overlay）。
- 台账：`descriptive_SHIBOR_DON_fail_explore` / `descriptive_DEF35_RP_fail_explore` / `descriptive_EQ_RP500_fail_precheck` / `descriptive_BOND_VOL_fail_precheck` / `descriptive_REL500_fail_precheck` / `descriptive_ETF_FLOW_NET_fail_precheck` / `descriptive_CASH_TRIG25_fail_precheck`。
- **勿改 promotion**（`promotion_approved=false`）；禁小盘；继续盯 `output/v3/handoff_strategy/`；**未触碰** `output/strategy_recon/{dd_ballast,mp_merge,mp_relax,gold_beta,cb_matprem,mp_near}/`。

## 更新 2026-10-12T02:02:40-04:00（Strategy：台账补记 roundF VOL-TERM/CASH-FLOOR/CB-PAR + 预检关闭臂）

- Beta `VOL-TERM`：**fail_explore / 无交接**；主表 60万/100万 X2≈**9.8%**&lt;12%。
- Beta `CASH-FLOOR`：**fail_explore / 无交接**；主表 60万/100万 X2≈**3.7%**&lt;12%。
- Beta `CB-PAR`：**fail_explore / 无交接**；主表 60万/100万 X2≈**7.5%**&lt;12%；X1 空仓≈**89%**。
- Beta `CORR-CUT` / `DUR-MR` / `EQ-CROSS` / `CB-BONDVAL` / `SHIBOR-ON` / `PAIR-35`：**fail_precheck**（roundF；未开正式双窗）。
- **本任务口径：explore-pass 候选仍为 CB-MATPREM + MP-NEAR**（研究级；**非晋级**）；MERGE/RELAX/DD recon 另处，本批不改。
- 台账：`descriptive_VOL_TERM_fail_explore` / `descriptive_CASH_FLOOR_fail_explore` / `descriptive_CB_PAR_fail_explore` / `descriptive_CORR_CUT_fail_precheck` / `descriptive_DUR_MR_fail_precheck` / `descriptive_EQ_CROSS_fail_precheck` / `descriptive_CB_BONDVAL_fail_precheck` / `descriptive_SHIBOR_ON_fail_precheck` / `descriptive_PAIR_35_fail_precheck`。
- **勿改 promotion**；禁小盘；**未触碰** `output/strategy_recon/{dd_ballast,mp_merge,mp_relax}/`。

## 更新 2026-10-12T02:02:07-04:00（Strategy：GOLD-BETA 两引擎对账通过）

- **GOLD-BETA**（**正交压舱**；β(金,股) 触发削金；**≠ DD-BALLAST** 回撤触发；≠MATPREM族）：explore-pass + Strategy 对账 OK；主表 60万/100万 X2≈**15.35%/15.36%**、MDD≈−6.31/−6.32%、夏普≈1.40；**X1 软风险 CAGR≈−0.5%、MDD≈−21.6%、Sharpe≈0.03**。对账 `output/strategy_recon/gold_beta/`。
- **explore-pass 候选现为**：CB-MATPREM + MP-NEAR + MP-MERGE + MP-RELAX + DD-BALLAST + **GOLD-BETA**（研究级；**非晋级**）。
- 台账：`descriptive_GOLD_BETA_explore_pass_recon`；`docs/trial_ledger.csv` → `GOLD-BETA_strategy_recon`。
- 与 DD-BALLAST/MATPREM 相关叠加诊断待折叠（不作晋升证据）。
- **勿改 promotion**；禁小盘；无 IC/期货；继续盯 handoff。

## 更新 2026-10-12T01:57:40-04:00（Strategy：DD-BALLAST / MP-MERGE / MP-RELAX 两引擎对账通过）

- **DD-BALLAST**（**正交**）：explore-pass + Strategy 对账 OK；主表 60万/100万 X2≈**12.36%/12.37%**、MDD≈−7.66%；**X1 软风险 MDD≈−24.1%、Sharpe≈0.10**。对账 `output/strategy_recon/dd_ballast/`。
- **MP-MERGE**（**MATPREM 族近亲**）：explore-pass + 对账 OK；X2≈**15.38%/16.09%**；X1 空仓≈**81.7%**；**停止扩族**。对账 `output/strategy_recon/mp_merge/`。
- **MP-RELAX**（**MATPREM 族近亲**）：explore-pass + 对账 OK；X2≈**12.81%/13.22%**（近母臂）；X1 空仓≈**81.7%**；**停止扩族**。对账 `output/strategy_recon/mp_relax/`。
- **explore-pass 候选现为**：CB-MATPREM + MP-NEAR + MP-MERGE + MP-RELAX + DD-BALLAST（研究级；**非晋级**）。
- 台账：`descriptive_DD_BALLAST_explore_pass_recon` / `descriptive_MP_MERGE_explore_pass_recon` / `descriptive_MP_RELAX_explore_pass_recon`；`docs/trial_ledger.csv` → `*_strategy_recon`。
- **勿改 promotion**；禁小盘；MATPREM 族停止扩族；继续盯 handoff。

## 更新 2026-10-12T01:52:53-04:00（Strategy：台账补齐 CALLTV/VT-EQ/LIQTOP/DISP + 预检关闭臂）

- Beta `CB-CALLTV`：**fail_explore / 无交接**；主表 60万/100万 X2≈**7.3–7.4%**（X1 预检过线后仍未过 12%）。
- Beta `VT-EQ`：**fail_explore / 无交接**；主表 60万/100万 X2≈**11.7%**&lt;12%。
- Beta `CB-LIQTOP`：**fail_explore / 无交接**；主表 60万/100万 X2≈**4.9–5.0%**。
- Beta `CB-DISP`：**fail_explore / 无交接**；主表 60万/100万 X2≈**3.4–3.5%**。
- Beta `TS-CURVE` / `CB-LOWBETA` / `RATE-LEVEL` / `GOLD-MR`：**fail_precheck**（未开正式双窗）。
- **explore-pass 候选仍为 CB-MATPREM + MP-NEAR**（研究级；**非晋级**）；两臂 X2 日相关≈**0.77**（分散有限）。
- 台账：`descriptive_CB_CALLTV_fail_explore` / `descriptive_VT_EQ_fail_explore` / `descriptive_CB_LIQTOP_fail_explore` / `descriptive_CB_DISP_fail_explore` / `descriptive_TS_CURVE_fail_precheck` / `descriptive_CB_LOWBETA_fail_precheck` / `descriptive_RATE_LEVEL_fail_precheck` / `descriptive_GOLD_MR_fail_precheck`。
- **勿改 promotion**；禁小盘；继续盯 `output/v3/handoff_strategy/`（含任何 roundD）；新包 → 立刻双引擎对账。

## 更新 2026-10-11 22:20 ET（Leo/New Bot：高杠杆 FUT-RP 暂缓）
- 默认袖套：marp 40% + cb 30% + xd 30%（无 core / 无 E2 / 无 FUT-RP）。
- 总敞口硬上限 `MAX_GROSS=1.5`（现货 + 期货名义）；`--leverage > 1.5` 直接拒绝。期货走现金保证金池，**不用** MarginConfig 融资。
- 行业 ETF 轮动：Beta 无可用交接包（E1/E0 在 ETF_ROTATION_PREREG 探索窗未过线）。可选袖套 `ind_mom` 为 Strategy 自建研究占位（20 日动量、现金兜底），**非** Beta 密封。
- 前向模拟盘 `forward_paper_book.py` 不接 FUT-RP L3/L6（仅留禁用注释）。
- 窗口：仅 X1 / X2 探索窗；2018–2024-05 密封窗拒绝。
- CLI：
```
python3 -m quantlab.portfolio.v2_multisleeve_book \
  --arms BOOK,C0,SA_marp,SA_cb,SA_xd,STATIC --windows X1,X2 \
  --sleeves '{"marp":0.4,"cb":0.3,"xd":0.3}' --leverage 1.0 --max-gross 1.5 \
  --out output/strategy_mbook_L15
# optional industry placeholder:
python3 -m quantlab.portfolio.v2_multisleeve_book --arms SA_ind_mom --windows X2 \
  --sleeves '{"ind_mom":1.0}' --out output/strategy_mbook_ind_mom
```

## 更新 2026-10-12 00:15 ET（Leo：主结论 AUM 60万/100万；无 IC 骨架）

- **主结论按 AUM=60万 / 100万 报告**；大资金（5M）结果**仅作附录**，不得当标题数字。
- 无 IC 诊断骨架：`quantlab/portfolio/v2_multisleeve_book_noic.py` + `docs/v2/STRATEGY_NOIC_AUM_SKELETON_ZH.md`。
- 含 IC 的 L15 账本仍可用，但小资金下 IC 手数归零，主报告改走 NOIC 骨架。
- Beta `fail_explore` / **无交接**：TCarry-G、CIB2-NOIC、CB3-IC（见 `PREREGISTRATION_V2_ZH.md` 描述段）。
- 有 Beta 无 IC 交接包时立刻对账；禁小盘；不跑 Full D1。

## 更新 2026-10-12 01:19 ET（Strategy：MATPREM 入账 + fail 臂同步；NOIC 接线评估）

## 更新 2026-10-12T01:23:06-04:00（Strategy：台账补记 CB1-FLOOR fail_explore）

- Beta `CB1-FLOOR`：**fail_explore / 无交接**；主表 60万/100万 X2≈**2.5%**。
- 台账：`descriptive_CB1_FLOOR_fail_explore`；`docs/trial_ledger.csv` → `CB1-FLOOR_*`。
- **勿改 promotion**；禁小盘；未触碰 NOIC smoke / `strategy_mbook_noic_diag` smoke 产出。

## 更新 2026-10-12T01:24:01-04:00（Strategy：台账补记 LIQ-TV fail_explore）

- Beta `LIQ-TV`：**fail_explore / 无交接**；主表 60万/100万 X2≈**7.7%**；X1 MDD≈−26%。
- 台账：`descriptive_LIQ_TV_fail_explore`；`docs/trial_ledger.csv` → `LIQ-TV_*`。
- **勿改 promotion**；禁小盘；未触碰 NOIC smoke / `strategy_mbook_noic_diag` smoke 产出。

## 更新 2026-10-12T01:26:23-04:00（Strategy：台账补记 MIX-FROZEN fail_explore）

- Beta `MIX-FROZEN`：**fail_explore / 无交接**；主表 60万/100万 X2≈**10.8–10.9%**；X1 Sharpe&lt;0。
- 台账：`descriptive_MIX_FROZEN_fail_explore`；`docs/trial_ledger.csv` → `MIX-FROZEN_*`。
- **勿改 promotion**；禁小盘；未触碰 NOIC smoke / `strategy_mbook_noic_diag` smoke 产出。

**promotion_approved=false** · 研究级 · **禁小盘** · 无 IC 主路径 · 密封窗 2018–2024-05 **不作新证据重跑**。

## 更新 2026-10-12T01:35:45-04:00（Strategy：台账补记 MP-FAR fail_explore）

- Beta `MP-FAR`：**fail_explore / 无交接**；主表 60万/100万 X2≈**14%**，但 X1 Sharpe&lt;0。
- 通过臂仍 **MATPREM + MP-NEAR**；台账：`descriptive_MP_FAR_fail_explore`；`docs/trial_ledger.csv` → `MP-FAR_*`。
- **勿改 promotion**；禁小盘。

## 更新 2026-10-12T01:35:30-04:00（Strategy：MATPREM×MP-NEAR X2 相关/50·50 叠加诊断）

- 研究级诊断：`output/strategy_recon/matprem_mp_near_overlay/`（主表仅 60万/100万；X2）。
- 日相关≈**0.767 / 0.766**，周相关≈**0.744 / 0.736**（同家族低溢价；近端 vs 中端期限）。
- 持仓：全期 unique 重叠 76（J≈0.32）；调仓日均重叠≈4.2 只（约占 MP-NEAR top10 的 42%）；每日均有重叠。
- 50/50 static X2：60万 **13.66%** / MDD −6.13% / 夏普 1.37；100万 **14.04%** / −6.18% / 1.38（落在两单臂之间，夏普轻度提升）。
- **promotion_approved=false**；禁小盘；不作晋升证据。



## 更新 2026-10-12T01:40:47-04:00（Strategy：台账补记 CB-CONVACT / CB-LARGEISS fail_explore）

- Beta `CB-CONVACT`：**fail_explore / 无交接**；主表 60万/100万 X2≈**15.3–15.8%** 但 **X1 Sharpe&lt;0**。
- Beta `CB-LARGEISS`：**fail_explore / 无交接**；主表 60万/100万 X1 Sharpe≈**−0.71**；X2≈**9.8–10.0%**。
- **explore-pass 候选仍为 CB-MATPREM + MP-NEAR**（研究级；**非晋级**）。
- 台账：`descriptive_CB_CONVACT_fail_explore` / `descriptive_CB_LARGEISS_fail_explore`。
- **勿改 promotion**；禁小盘；**未触碰 MP-NEAR recon**。

## 更新 2026-10-12T01:35:55-04:00（Strategy：台账补记 CB-SIZEPREM / MP-FAR / CB-LISTAGE fail_explore）

- Beta `CB-SIZEPREM`：**fail_explore / 无交接**；主表 60万/100万 X2≈**15.8–16.2%** 但 **X1 Sharpe&lt;0**。
- Beta `MP-FAR`：**fail_explore / 无交接**；主表 60万/100万 X2≈**14.0%** 但 **X1 Sharpe&lt;0**。
- Beta `CB-LISTAGE`：**fail_explore / 无交接**；主表 60万/100万 X2≈**11.8–12.0%**；**X1 Sharpe&lt;0**。
- **explore-pass 候选仍为 CB-MATPREM + MP-NEAR**（研究级；**非 sole**；**非晋级**）。
- 台账：`descriptive_CB_SIZEPREM_fail_explore` / `descriptive_MP_FAR_fail_explore` / `descriptive_CB_LISTAGE_fail_explore`。
- **勿改 promotion**；禁小盘；**未触碰 MP-NEAR recon**。

## 更新 2026-10-12T01:31:04-04:00（Strategy：MP-NEAR 探索通过对账；MATPREM 仍为 pass 候选）

- Beta `MP-NEAR`：**explore-pass + 有交接**；Strategy 两引擎对账 **通过**（`output/strategy_recon/mp_near/`）。
- 主表 60万/100万：X2≈**14.50% / 14.84%**，MDD≈−7.57%；**X1 近端日历池 EMPTY（空仓 100%，纯压舱）**。
- **MATPREM 仍为 explore-pass 候选**；MP-NEAR 为额外 explore-pass（对账已通过）；**非晋级**。
- 台账：`descriptive_MP_NEAR_explore_pass_recon`；`docs/trial_ledger.csv` → `MP-NEAR_strategy_recon`。
- **勿改 promotion**；禁小盘；无 IC。

## 更新 2026-10-12T01:28:16-04:00（Strategy：sole explore-pass 候选书签）

> **当前 explore-pass 候选（研究级）**：**CB-MATPREM** + **MP-NEAR** + **MP-MERGE**/**MP-RELAX**（MATPREM族近亲，停止扩族）+ **DD-BALLAST**（**P0-4 watch_only/对照**；正交；与 GOLD corr≈0.97；X1 MDD≈−24%/Sharpe≈0.10）+ **GOLD-BETA**（**P0-4 主表试配压舱**；正交；X1 CAGR≈−0.5%/MDD≈−21.6%/Sharpe≈0.03）  
> - Strategy 两引擎对账 OK（`output/strategy_recon/cb_matprem/`）  
> - NOIC 诊断骨架接线 + 60/100万 cheap smoke OK（`output/strategy_mbook_noic_diag/matprem/`）  
> - **仍非晋级**：`promotion_approved=false`；**不作晋升证据**  
> - 软风险：MATPREM X1 日历池空仓≈**81.7%**（主要靠压舱）；MP-NEAR X1 EMPTY=**100%**（纯压舱）  
> - 两臂 X2 日相关≈**0.77** / 周相关≈**0.74**（分散有限）  
> - **其余近期臂（含 CALLTV / VT-EQ / LIQTOP / DISP 及预检关闭臂）均为 fail_explore 或 fail_precheck / 无交接**（见下表）  
> - **禁小盘** · 无 IC 主路径 · 密封窗不作新证据重跑  
> - 值班：继续盯 `output/v3/handoff_strategy/`（新 Beta 无 IC 袖套 → 立刻 Strategy 对账）

### 臂状态一览（主表仅 AUM 60万 / 100万）— **pass = MATPREM+NEAR+MERGE+RELAX+GOLD-BETA（主表试配压舱）+DD-BALLAST（P0-4 watch_only）+IND-RATE-DIFF+CB-PREMRESID-COV；P90/CALL-HEAT=near_relative 观察；其余 fail**

| 臂 | 状态 | 交接 | 主表要点（60/100万） | 台账 |
|---|---|---|---|---|
| **CB-MATPREM** | **explore-pass 候选**（研究级；对账+NOIC smoke OK；**非晋级**） | `output/v3/handoff_strategy/cb_matprem/`（AUM_600000 / AUM_1000000） | X2≈**12.8% / 13.2%**；MDD≈−5.4%；夏普≈1.3；**X1 日历池空仓≈81.7%**（日均 CB≈0.18，主要靠压舱） | `descriptive_CB_MATPREM_explore_pass_recon`；对账 `output/strategy_recon/cb_matprem/` |
| **MP-NEAR** | **explore-pass 候选**（研究级；Strategy 对账 OK；**非晋级**；MATPREM 变体） | `output/v3/handoff_strategy/mp_near/`（AUM_600000 / AUM_1000000） | X2≈**14.50% / 14.84%**；MDD≈−7.57%；夏普≈1.27–1.29；**X1 近端日历池 EMPTY（空仓 100%，纯压舱）** | `descriptive_MP_NEAR_explore_pass_recon`；对账 `output/strategy_recon/mp_near/` |
| **MP-MERGE** | **explore-pass 候选**（研究级；对账 OK；**非晋级**；**MATPREM 族近亲**；停止扩族） | `output/v3/handoff_strategy/mp_merge/` | X2≈**15.38% / 16.09%**；MDD≈−5.2–−5.4%；**X1 空仓≈81.7%** | `descriptive_MP_MERGE_explore_pass_recon`；对账 `output/strategy_recon/mp_merge/` |
| **MP-RELAX** | **explore-pass 候选**（研究级；对账 OK；**非晋级**；**MATPREM 族近亲**；停止扩族） | `output/v3/handoff_strategy/mp_relax/` | X2≈**12.81% / 13.22%**；MDD≈−5.4%；**X1 空仓≈81.7%** | `descriptive_MP_RELAX_explore_pass_recon`；对账 `output/strategy_recon/mp_relax/` |
| **DD-BALLAST** | explore-pass **对照/watch_only（P0-4；与 GOLD corr≈0.97）**（研究级；对账 OK；**非晋级**；**正交**≠MATPREM族） | `output/v3/handoff_strategy/dd_ballast/` | X2≈**12.36% / 12.37%**；MDD≈−7.66%；**X1 MDD≈−24.1%/Sharpe≈0.10** | `descriptive_DD_BALLAST_explore_pass_recon`；对账 `output/strategy_recon/dd_ballast/` |
| **GOLD-BETA** | **explore-pass 候选 · 主表试配压舱（P0-4 二选一）**（研究级；对账 OK；**非晋级**；**正交压舱** β触发≠DD；≠MATPREM族） | `output/v3/handoff_strategy/gold_beta/` | X2≈**15.35% / 15.36%**；MDD≈−6.31/−6.32%；夏普≈1.40；**X1 CAGR≈−0.5%/MDD≈−21.6%/Sharpe≈0.03** | `descriptive_GOLD_BETA_explore_pass_recon`；对账 `output/strategy_recon/gold_beta/` |
| **IND-RATE-DIFF** | **explore-pass 候选**（研究级；对账 OK；**非晋级**；ETF-only） | `output/v3/handoff_strategy/ind_rate_diff/` | X2≈**24.66%/24.65%**；**X1 Sharpe≈0.12/MDD≈−22.2%** | `descriptive_IND_RATE_DIFF_explore_pass_recon`；对账 `output/strategy_recon/ind_rate_diff/` |
| **CB-PREMRESID-COV** | **explore-pass 候选**（研究级；全量面板对账 OK；**非晋级**） | `output/v3/handoff_strategy/cb_premresid_cov/` | X2≈**25.51%/25.72%**；MDD≈−17.5%；**X1 空仓≈25.8%** | `descriptive_CB_PREMRESID_COV_explore_pass_recon_fullpanel`；对账 `output/strategy_recon/cb_premresid_cov/` |
| CB-CALL-HEAT | research_observe · **near_relative vs DIFF+COV**（**非独立 explore-pass**） | `output/v3/handoff_strategy/cb_call_heat/` | X2≈20.3%；MDD≈−24.3%；vs DIFF ρ≈**0.985**；vs COV≈**0.88**；X1 Sharpe≈0.12 | `descriptive_CB_CALL_HEAT_near_relative_research_observe` |
| CB-PUT-AVOID | fail_precheck | 无 | X1 Sharpe≈−0.50；avg_names≈5.55 | `descriptive_CB_PUT_AVOID_fail_precheck` |
| MARGIN-DELTA | fail_precheck | 无 | X1 Sharpe≈−0.03 | `descriptive_MARGIN_DELTA_fail_precheck` |
| IND-RATE-P90 | research_observe · **near_relative vs DIFF**（**非独立 explore-pass**） | `output/v3/handoff_strategy/ind_rate_p90/` | X2≈24.34%；vs DIFF ρ≈**0.995**；X1 Sharpe≈0.19 | `descriptive_IND_RATE_P90_near_relative_research_observe` |
| CB3-BALLAST | fail_explore | 无 | X2≈0.5% | `descriptive_CB3_BALLAST_fail_explore` |
| SHARE-AC | fail_explore | 无 | X2≈6.6%（弱于静态60/40）；X1≈−2%/MDD≈−28% | `descriptive_SHARE_AC_fail_explore` |
| CB-DUAL | fail_explore | 无 | X2≈10.5%；X1 Sharpe&lt;0；CB1↔CB2 相关≈0.95 | `descriptive_CB_DUAL_fail_explore` |
| CB2-DYN | fail_explore | 无 | X2≈6.8–7.0% | `descriptive_CB2_DYN_fail_explore` |
| TCarry-G | fail_explore | 无 | X2≈8.5%&lt;12% | `descriptive_TCarry_G_fail_explore` |
| CIB2-NOIC | fail_explore | 无 | X2≈8%&lt;12%（同构参考 NOIC 骨架） | `descriptive_CIB2_NOIC_fail_explore` |
| CB3-IC | fail_explore | 无（空目录） | 含 IC，**不进 NOIC** | `descriptive_CB3_IC_fail_explore` |
| NAV-DISC | fail_explore | 无 | X2≈5.8%（弱于静态60/40）；X1≈−1.3%/MDD≈−28%；含股腿不进 NOIC | `descriptive_NAV_DISC_fail_explore` |
| CB1-FLOOR | fail_explore | 无 | X2≈2.5%；X1≈1.8%/MDD≈−7%（价带过滤后股性不足） | `descriptive_CB1_FLOOR_fail_explore` |
| LIQ-TV | fail_explore | 无 | X2≈7.7%；X1≈−2.1%/MDD≈−26% sharpe&lt;0；相对全国债压舱无增量 | `descriptive_LIQ_TV_fail_explore` |
| MIX-FROZEN | fail_explore | 无 | X2≈10.8–10.9%；X1 Sharpe&lt;0；相对静态60/40 有增量仍不达闸门 | `descriptive_MIX_FROZEN_fail_explore` |
| CB-SIZEPREM | fail_explore | 无 | X2≈15.8–16.2% 但 X1 Sharpe&lt;0（闸门失败） | `descriptive_CB_SIZEPREM_fail_explore` |
| MP-FAR | fail_explore | 无 | X2≈14.0% 但 X1 Sharpe&lt;0（闸门失败） | `descriptive_MP_FAR_fail_explore` |
| CB-LISTAGE | fail_explore | 无 | X2≈11.8–12.0% 未稳过12%；X1 Sharpe&lt;0 | `descriptive_CB_LISTAGE_fail_explore` |
| CB-LARGEISS | fail_explore | 无 | X1 Sharpe≈-0.71；X2≈9.8–10.0% | `descriptive_CB_LARGEISS_fail_explore` |
| CB-CONVACT | fail_explore | 无 | X2≈15.3–15.8% 但 X1 Sharpe&lt;0（闸门失败） | `descriptive_CB_CONVACT_fail_explore` |
| CB-CALLTV | fail_explore | 无 | X2≈7.3–7.4%&lt;12%（预检过线后仍失败） | `descriptive_CB_CALLTV_fail_explore` |
| VT-EQ | fail_explore | 无 | X2≈11.7%&lt;12% | `descriptive_VT_EQ_fail_explore` |
| CB-LIQTOP | fail_explore | 无 | X2≈4.9–5.0%&lt;12% | `descriptive_CB_LIQTOP_fail_explore` |
| CB-DISP | fail_explore | 无 | X2≈3.4–3.5%&lt;12%；X1 空仓≈44% | `descriptive_CB_DISP_fail_explore` |
| TS-CURVE | fail_precheck | 无 | X1 Sharpe≈−0.06；未开正式双窗 | `descriptive_TS_CURVE_fail_precheck` |
| CB-LOWBETA | fail_precheck | 无 | X1 Sharpe≈−0.21；未开正式双窗 | `descriptive_CB_LOWBETA_fail_precheck` |
| RATE-LEVEL | fail_precheck | 无 | X1 Sharpe≈−0.10；未开正式双窗 | `descriptive_RATE_LEVEL_fail_precheck` |
| GOLD-MR | fail_precheck | 无 | X1 Sharpe≈−0.05；未开正式双窗 | `descriptive_GOLD_MR_fail_precheck` |
| VOL-TERM | fail_explore | 无 | X2≈9.8%&lt;12% | `descriptive_VOL_TERM_fail_explore` |
| CASH-FLOOR | fail_explore | 无 | X2≈3.7%&lt;12% | `descriptive_CASH_FLOOR_fail_explore` |
| CB-PAR | fail_explore | 无 | X2≈7.5%&lt;12%；X1 空仓≈89% | `descriptive_CB_PAR_fail_explore` |
| CORR-CUT | fail_precheck | 无 | X1 Sharpe≈−0.06；未开正式双窗 | `descriptive_CORR_CUT_fail_precheck` |
| DUR-MR | fail_precheck | 无 | X1 Sharpe≈−0.07；未开正式双窗 | `descriptive_DUR_MR_fail_precheck` |
| EQ-CROSS | fail_precheck | 无 | X1 Sharpe≈−0.07；未开正式双窗 | `descriptive_EQ_CROSS_fail_precheck` |
| CB-BONDVAL | fail_precheck | 无 | X1 Sharpe≈−0.84；未开正式双窗 | `descriptive_CB_BONDVAL_fail_precheck` |
| SHIBOR-ON | fail_precheck | 无 | X1 Sharpe≈−0.19；未开正式双窗 | `descriptive_SHIBOR_ON_fail_precheck` |
| PAIR-35 | fail_precheck | 无 | X1 Sharpe≈−0.02；未开正式双窗 | `descriptive_PAIR_35_fail_precheck` |
| SHIBOR-dON | fail_explore | 无 | X2≈6.8%&lt;12% | `descriptive_SHIBOR_DON_fail_explore` |
| DEF35-RP | fail_explore | 无 | X2≈1.5%&lt;12%；伪夏普 | `descriptive_DEF35_RP_fail_explore` |
| EQ-RP500 | fail_precheck | 无 | X1 Sharpe≈−0.21；未开正式双窗 | `descriptive_EQ_RP500_fail_precheck` |
| BOND-VOL | fail_precheck | 无 | X1 Sharpe≈−0.01；未开正式双窗 | `descriptive_BOND_VOL_fail_precheck` |
| REL500 | fail_precheck | 无 | X1 Sharpe≈−0.19；未开正式双窗 | `descriptive_REL500_fail_precheck` |
| ETF-FLOW-NET | fail_precheck | 无 | X1 Sharpe≈−0.17；未开正式双窗 | `descriptive_ETF_FLOW_NET_fail_precheck` |
| CASH-TRIG25 | fail_precheck | 无 | X1 Sharpe≈−0.02；未开正式双窗 | `descriptive_CASH_TRIG25_fail_precheck` |
| CB-PREMRESID | fail_explore | 无 | X2≈10.5–10.6%&lt;12%；X1 avg_names=0（空仓债底） | `descriptive_CB_PREMRESID_fail_explore` |
| SECT-FLOW-DISP | fail_precheck · CLOSED（P0-5 取代） | 无 | X1 Sharpe≈−0.072；未开正式双窗 | `descriptive_SECT_FLOW_DISP_fail_precheck` |
| IND-CROWD-REV | fail_precheck | 无 | X1 Sharpe≈−0.050；未开正式双窗 | `descriptive_IND_CROWD_REV_fail_precheck` |

### NOIC 骨架接线（研究诊断，非晋级）

- 评估短报：`output/strategy_mbook_noic_diag/MATPREM_NOIC_EVAL_ZH.md`
- 骨架文档：`docs/v2/STRATEGY_NOIC_AUM_SKELETON_ZH.md`
- 接线+smoke：`output/strategy_mbook_noic_diag/matprem/SHORT_ZH.md`（60/100万 X1/X2 OK）
- 状态：**CB-MATPREM + MP-NEAR 为当前 explore-pass 候选**；MATPREM 已研究级接线诊断，**暂不作默认主臂**（X1 池深软风险；MP-NEAR X1 池 EMPTY 更强）；**勿改 promotion**。
- 值班：继续盯 `output/v3/handoff_strategy/`（见同目录 `WATCH_ZH.md`）；新 Beta 袖套立刻 Strategy 对账。

