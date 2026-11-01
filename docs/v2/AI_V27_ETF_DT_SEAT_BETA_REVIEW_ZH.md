# AI ETF-DT-SEAT — Beta 纸深度复核（纸拒）

更新：2026-10-12 08:53 ET（America/New_York）  
来源包：`output/ai_factor/gp_reopen_hardgate_etf_dt_seat/`  
说明：`BETA_NOTE_ZH.md`；包：`beta_etf_timing_dt_seat_package.json`；诊断：`diagnostics.json`；回执：`newbot_smoke_receipt.json`  
提案：`docs/v2/AI_ETF_ARM_PROPOSAL_V27_DT_SEAT_ZH.md`；接线：`docs/v2/AI_DT_SEAT_LEAVES_WIRING_RECEIPT_ZH.md`  
复核方：QuantLab Beta。`promotion_approved=false`。**不交 Strategy**。  
冒烟 runner：`output/v3/run_etf_timing_dt_seat_smoke.py`；结果根：`output/v3/etf_timing_dt_seat/`（8 臂子目录 + `diagnostics.json`）。  
**本复核只读既有结果，未重跑冒烟、未改表达式、未另开 runner。**

---

## 0. 一句话裁决

**reject。**  
龙虎 `seat_type`→SW L1→液态行业 ETF 冒烟臂：**S1–S8 全 `fail_precheck`**（60万∧100万 X1 Sharpe 全负；`any_x1_pass=false`）。与滞后 `ind_ret` 的 |ρ|≪0.85（max≈0.006），**未**触发近亲价相关闸；失败主因是真 NAV 不可交易，非塌成 REL-MOM。handoff: **NO**。`promotion_approved=false`。**勿磨同构变体。**

---

## 1. 包 / 机制摘要

| 项 | 内容 |
|---|---|
| sleeve / 族 | `etf_timing_dt_seat` / **ETF-DT-SEAT** |
| 机制 | 个股龙虎席位按 `seat_type` 净买在申万一级截面聚合 → 映射液态行业 ETF；吃「机构/通道已铺开、游资仍追热票」的行业级滞后扩散（**非** ETF 申赎、**非**价叶） |
| 叶子（SW L1） | `dt_inst_net_sw_5`、`dt_retail_net_sw_5`、`dt_nb_channel_net_sw_5`、`dt_inst_breadth_sw`、`dt_inst_breadth_sw_5`（及对应 `_lag1`） |
| 禁叶 | 份额流 / `Δfd_share` / `ind_ret` / `ind_excess` / `bm_ret` / CB / 金 |
| y / 压舱 | 行业 ETF 顶 tercile；空仓 → **sh.510300**（残差宽基，禁小盘主线叙事） |
| PIT | `available_at_alpha_conservative.normalize()+1d` → 首个可达交易日；≈T+1 15:00 Asia/Shanghai → 交易 **T+2 开盘**；**不可前移** |
| 闸门 | 月频；成本研究目标 25bp；容量 **60万∧100万**；X1 Sharpe≤0 或 avg_names=0 → fail_precheck（**不开 X2**） |
| GP | `v27_gp_started=false`（本轮未开 SEARCH） |
| 冒烟元数据 | PID=2796708；peak_rss_MB≈1600.8；elapsed≈16.2s；X1=`2015-06-01→2017-12-29`（634 会话） |

### 1.1 八臂定义（包 note）

| arm | note |
|---|---|
| S1_inst_minus_retail | `cs_z(inst5)-cs_z(retail5)` |
| S2_inst_breadth5 | `cs_z(inst_breadth_5)` |
| S3_nb_channel | `cs_z(nb_channel_net_5)` |
| S4_inst_only | `cs_z(inst_net_5)` |
| S5_inst_minus_nb | `cs_z(inst)-cs_z(nb)` |
| S6_breadth_minus_retail | `cs_z(breadth5)-cs_z(retail5)` |
| S7_inst_plus_breadth | `cs_z(inst5)+cs_z(breadth_daily)` |
| S8_neg_retail | `neg cs_z(retail5)` |

---

## 2. 相对近亲核验（提案失败条件）

提案 §4 可证伪条件对照：

| # | 失败条件 | 本包结果 | 判定 |
|---|---|---|---|
| 1 | 得分 vs 滞后 `ind_ret`/`ind_excess` \|ρ\|≥0.85 → REL-MOM 近亲 | 仅报 **ρ(ind_ret_lag1)**：八臂均 \|ρ\|≤**0.00585**（≪0.85）；`near_relative_reject=false` 全臂。**ρ(ind_excess) 未提供** | **未**触发近亲价相关拒；机制输入确非价叶 |
| 2 | 去掉 `seat_type` 分裂、改笼统 `dt_net_*` 后增量消失 | **未提供**正式 ablation（笼统净买 vs seat 分裂对照表） | 无法用本项单独证伪；见下「间接观察」 |
| 3 | X1@60万∧100万 Sharpe≤0 或 avg_names=0 | **八臂全触发** Sharpe≤0；avg_names∈[0.78, 1.16]（>0） | **fail_precheck**（主裁决依据） |
| 4 | PIT 违规或液态覆盖≈0 | PIT 规则与接线回执一致；日均液态 SW≈**3.69**；avg_names>0 | 覆盖薄但**非**空仓级；**未见** available_at 前移证据 |
| 5 | 全样本 PIT ICIR 塌缩 | 本轮未开 v27 GP / 无包窗 ICIR 表 | 不适用（直接 NAV 闸已全败） |

**间接观察（seat 分裂增量）：** 单 seat 臂（S3/S4/S8）与差分/组合臂（S1/S5/S6/S7）及广度臂（S2）**一律** Sharpe≤0；无「分裂显著优于笼统」的可交易证据。在未做正式 ablation 的前提下，**亦不支持**继续磨同构 seat 变体。

**near_relative 结论：** 按价相关阈 **否**（\|ρ\|≪0.85）；按已 fail 族语义 —— 非份额流、非 v23 价叶；与 DT-INST-BREADTH（市场层抬宽基）/ EVT-DT-INST-STOCK（个股篮）形态不同，但 **真 NAV 同样不可交易** → 纸拒，勿再开同构。

---

## 3. 真 NAV 冒烟（60万∧100万 X1；扣成本引擎）

规则：月频再平衡；seat 得分 → 液态行业 ETF **顶 tercile 等权**；空仓→510300；X1 Sharpe≤0 → **fail_precheck**（不开 X2）。AUM 100万与 60万共用同构权重表。  
**总闸：`any_x1_pass=false`。八臂全 fail。**

| arm | note（摘） | ρ(ind_ret_lag1) | near_rel | X1@60万 CAGR/MDD/Sharpe | X1@100万 C/M/S | avg_names | 处置 / 一句原因 |
|---|---|---|---|---|---|---|---|
| **S1** | inst−retail | 0.0011 | false | −24.5%/−64.2%/ **−0.550** | −24.1%/−63.5%/−0.541 | 1.16 | **fail_precheck** — X1 Sharpe≤0 |
| **S2** | inst_breadth5 | 0.0019 | false | −19.8%/−52.2%/ **−0.456** | −20.5%/−52.0%/−0.484 | 1.16 | **fail_precheck** — Sharpe≤0 |
| **S3** | nb_channel | −0.0012 | false | −15.0%/−50.9%/ **−0.348** | −17.0%/−51.1%/−0.430 | 0.78 | **fail_precheck** — Sharpe≤0 |
| **S4** | inst_only | 0.0056 | false | −15.0%/−56.8%/ **−0.264** | −15.8%/−57.0%/−0.291 | 1.16 | **fail_precheck** — Sharpe≤0（相对最轻负） |
| **S5** | inst−nb | 0.0058 | false | −17.0%/−56.1%/ **−0.397** | −17.3%/−56.4%/−0.408 | 0.78 | **fail_precheck** — Sharpe≤0 |
| **S6** | breadth−retail | −0.0018 | false | −27.7%/−63.6%/ **−0.667** | −27.9%/−63.6%/−0.674 | 1.16 | **fail_precheck** — Sharpe≤0（最差） |
| **S7** | inst+breadth | 0.0048 | false | −20.9%/−56.1%/ **−0.476** | −21.6%/−56.4%/−0.503 | 1.06 | **fail_precheck** — Sharpe≤0 |
| **S8** | −retail | −0.0040 | false | −20.7%/−59.8%/ **−0.482** | −21.8%/−60.4%/−0.523 | 1.16 | **fail_precheck** — Sharpe≤0 |

†100万与60万同权同构；数值接近。未开 X2 / S / 密封。n_rebalance=32；n_sessions=634。

---

## 4. 覆盖 / PIT

| 项 | 数值 / 结论 |
|---|---|
| X1 会话 | 634（2015-06-01→2017-12-29） |
| SW 列 / 液态映射 | n_sw_cols=31；liq_map_n_sw=27 |
| X1 日均液态 SW | ≈**3.69**（与 v23 价叶同量级薄覆盖） |
| 组合 avg_names | **0.78–1.16**（顶 tercile；>0，故失败主因是 Sharpe≤0 而非空仓） |
| PIT / available_at | 诊断与包均写明 conservative+1d→T+2 open；**未见**违规前移记载 |
| 接线回执（TrackA 叶样） | `docs/v2/AI_DT_SEAT_LEAVES_WIRING_RECEIPT_ZH.md`：个股层叶 nonempty 低、mean_names/day 可观；本臂用的是 **SW L1 聚合叶**，再映射 ETF |
| 禁叶断言 | runner/包 `forbidden_features` 含份额流与价叶；臂 pretest 复述禁用 |

覆盖薄会抬高噪声与压舱占比，但 **不足以单独解释全负 Sharpe**——同窗液态篮上 seat 排序仍系统亏钱。

---

## 5. 对照 Beta 约束

| 约束 | 判定 |
|---|---|
| 禁小盘主线 | 液态闸 amt20≥2000 ∧ list≥60d；残差 **510300** ✅ |
| 禁 CB/金主仓 | ✅ |
| 禁份额流 / 价叶作特征 | ✅ |
| 容量主结论只用 60万/100万 | ✅（同败同构） |
| X1 Sharpe≤0 → fail_precheck | ✅ 全臂；**未开 X2** |
| promotion / Strategy | `false` / **不交** ✅ |
| 必须预测组合收益且可交易 | **不满足** — 八臂 X1 全负 Sharpe |

---

## 6. 处置

- **裁决：reject**（非 research_observe：无臂 X1 Sharpe>0；非 explore-pass）
- `promotion_approved=false`；**handoff: NO**；**不交 Strategy**；不进 Alpha 短名单
- `any_x1_pass=false`；八臂全 `fail_precheck`
- \|ρ(ind_ret_lag1)\|≪0.85 → **非** near_relative（价相关）；seat 分裂正式 ablation **未提供**，但各变体均不可交易
- 容量结论：60万∧100万 X1 同败
- 建议 AI / New Bot：
  1. **勿磨** ETF-DT-SEAT 同构变体（改窗/改 cs_z 差分/改广度混合）
  2. 勿把「\|ρ\| 低」当成可交易证据——本包已证明正交于价叶仍可全负 NAV
  3. 若未来再开龙虎席位→ETF：须新机制维（非 seat 截面再排）且 X1@60∧100 Sharpe>0∧avg_names>0，方可谈 observe
