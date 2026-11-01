# AI v23 `etf_timing_price` — Beta 纸深度复核

更新：2026-10-12 08:22 ET（America/New_York）  
来源包：`output/ai_factor/gp_reopen_hardgate_v23_track_b_etf_price/`  
说明：`BETA_NOTE_ZH.md`；包：`beta_etf_timing_price_package.json`；`pit_asof_meta.json`；`dual_icir_summary.json`；`label_definition.json`  
复核方：QuantLab Beta。`promotion_approved=false`。**不交 Strategy**。  
冒烟 runner：`output/v3/run_etf_timing_v23_price_smoke.py`；诊断：`output/v3/etf_timing_v23_price/diagnostics.json`；batch：`output/v3/pretest_batch_20261012_etf_timing_v23_price.json`。

---

## 0. 一句话裁决

**reject。**  
价叶包（无 flow）PIT≡LEAK 属可预期（无份额 asof 差），**勿用高双 ICIR 冒充进度**。包窗 PIT ICIR 最高≈1.60，但全样本多塌缩；60万∧100万 X1 真持行业 ETF **P1–P15 全 fail_precheck**（Sharpe≤0）。多臂实质为相对动量/波动拥挤近亲（已 fail 族）。handoff: **NO**。

---

## 1. 包内容摘要

| 项 | 内容 |
|---|---|
| sleeve | `etf_timing_price`（`for_beta=true`，不进 Alpha） |
| evals / GATE_OK_PIT | 120 / **37**；peak≈450MB；explore `2024-06-03→2025-06-30` |
| 叶子 X（11，**无 flow**） | `bm_ret_lag1/ts_mean_5/ts_std_10`；`ind_excess_lag1/lag5/ts_mean_5/ts_std_10`；`ind_ret_lag1/lag5/ts_mean_5/ts_std_10` |
| 标签 y | **fwd_1d_excess_vs_510300**（主）；fwd_5d（副）；AUM 加权申万一级行业 ETF hfq pct_change − 510300 |
| PIT 规则（价） | 滞后面板：lag1=`shift(1)`、lag5=`shift(5)`；ts_* 叶子在 `shift(1)` 上滚动。**无**份额 `available_at`。禁止把当日未收盘价当已知。 |
| 闸门 | **只认 PIT ICIR**；成本 25bp；冲击 60∧100万；禁 CB/金 |
| 双 ICIR（包） | PIT median≈**−0.313** max≈**1.604**；LEAK median≈**−0.313** max≈**1.604**（**完全相同**） |
| Top1 | `ts_mean_20(div(ts_delta_5(ind_excess_ts_mean_5), ts_mean_20(ind_excess_lag5)))` ICIR_PIT≈1.60 |
| fail_top | PIT_ICIR1_LE_0×79；IMPACT_60_OR_100_FAIL×4 |

---

## 2. 价叶 / 双 ICIR 虚高核验

### 2.1 为何 PIT median ≡ LEAK median？

| 检验 | 结果 |
|---|---|
| 包 `dual_icir_summary` PIT vs LEAK | median/mean/max **逐位相同** |
| Beta 复算 15 臂 | 全样本与包窗 `pit_eq_leak=True`（差 <1e-9） |
| 根因 | 价叶无份额 asof；PIT 面板 ≡ trade_date 对齐面板 → 双 ICIR **必然重合** |
| 误读风险 | **不可**把「PIT≈LEAK 且都高」当成 asof 过关或可交易证据；那只是同面板自我对照 |

### 2.2 包窗 vs 全样本（fwd1d excess）

| 现象 | 解读 |
|---|---|
| 包窗 PIT 常接近包内 ICIR（P1≈1.87 vs 包 1.60；P3≈1.21 vs 1.22） | 探索窗可复现 |
| 全样本 PIT 大幅塌缩（P1 1.87→0.45；P2 1.09→0.17；P4 1.34→**−0.34**） | **包窗虚高**，外推失败 |
| P6/P7/P9/P12/P14 全样本 ≤0 或近 0 | 波动/混合变换无稳定超额预测 |

### 2.3 near_relative / 已 fail 近亲风险

| tag | 臂 | 说明 |
|---|---|---|
| **near_relative** | P2, P3, P10, P11, P15 | `neg(ind_ret_*)` / `neg(ind_excess_ts_mean_*)` — 行业相对反转/动量形态，贴近已 fail 的 REL-MOM |
| **vol_crowd** | P4–P7, P13 | `ind_ret_ts_std` / `bm_ret_ts_std` × abs(ret) — 波动拥挤，贴近已 fail 的价量/PXVOL 近亲 |
| mixed_price | P1, P8, P9, P12, P14 | 仍以 excess/ret 变换为主，非新信息源 |

**仍跑完 NAV**（按任务要求）；tag 仅作风险标注，不替代净值闸门。

### 2.4 价叶滞后口径（诊断）

- 决策：月频再平衡，用截至再平衡日的**最后可得**滞后得分（开盘前已知 = 前收及更早）。
- `ind_ret_lag1` / `bm_ret_lag1` / `*_ts_mean_*` / `*_ts_std_*`：底层均先 `shift(1)` 再滚动（与 AI `add_pit_price_leaves` + v23 扩叶一致）。
- `*_lag5`：`shift(5)`。
- **无** flow/share_chg 叶子；runner 断言面板名不含 `flow`/`share_chg`。

---

## 3. 对照 Beta 约束

| 约束 | 判定 |
|---|---|
| 禁小盘 | amt20≥2000 + list≥60d ✅ |
| 禁 CB/金主仓 | 残差 **510300**（非 GOLD）✅ |
| 禁份额流叶子 | ✅ 11 价叶，无 `etf_*_flow` / `ind_etf_share_flow` / `share_chg` |
| 容量 | 报告 **60万∧100万** ✅（同窗对照；权重表同构，差异来自冲击/最小成交） |
| X1 Sharpe≤0 → fail_precheck | ✅ 全臂触发；**未开 X2** |
| 行业 ETF 时序袖套 | 形态 ✅ |
| 必须预测组合收益且可交易 | **不满足** — 包窗 ICIR 不稳；X1 组合全败 |
| promotion / Strategy | `false` / **不交** ✅ |

### 3.1 X1 覆盖（如实）

| 项 | 数值 |
|---|---|
| X1 会话 | 634（2015-06-01→2017-12-29） |
| 行业收益面板 nonempty | ≈**28.0%**；曾现 SW≈11；日均 SW≈7.6 |
| 液态映射（amt20≥2000∧list≥60d） | 日均液态 SW≈**3.7**；ETF≈17 只累计 |
| 组合 avg_names | ≈**1.16**（顶 tercile；覆盖薄但仍 >0，故失败主因是 Sharpe≤0 而非空仓） |

覆盖不足会抬高噪声与压舱占比，但 **不足以单独解释全负 Sharpe**——同窗液态篮上得分排序仍系统亏钱。

---

## 4. 真实收益冒烟（60万∧100万 X1；扣成本引擎）

规则：月频；GP 得分→液态行业 ETF **顶 tercile 等权**；空仓→510300；X1 Sharpe≤0 或 avg_names=0 → **fail_precheck**（不开 X2）。AUM 100万与 60万共用同一权重表。

| arm | 表达式（摘） | 全样本/包窗 PIT ICIR | tag | X1@60万 CAGR/MDD/Sharpe | X1@100万 C/M/S | avg | 处置 / 一句原因 |
|---|---|---|---|---|---|---|---|
| **P1** | `mean20(Δ5(ex_ts5)/mean20(ex_lag5))` | 0.45 / **1.87** | mixed | −15.6%/−45.9%/ **−0.31** | −15.2%/−45.0%/−0.31 | 1.16 | **fail_precheck** — X1@60万 Sharpe≤0 |
| **P2** | `−std10(ret)×mean20(ret_lag1)` | 0.17 / 1.09 | near_rel | −27.2%/−59.3%/ **−0.68** | −28.1%/−60.3%/−0.71 | 1.16 | **fail_precheck** — Sharpe≤0；近 REL-MOM |
| **P3** | `−ex_ts5 + max20(bm_std10)` | 0.60 / 1.21 | near_rel | −23.9%/−56.8%/ **−0.53** | −24.8%/−57.9%/−0.57 | 1.16 | **fail_precheck** — Sharpe≤0；近 REL-MOM |
| **P4** | `mean10(\|std10\|/\|ret_lag1\|)` | **−0.34** / 1.34 | vol | −10.3%/−45.4%/ **−0.12** | −11.6%/−45.6%/−0.16 | 1.16 | **fail_precheck** — Sharpe≤0；全样本 ICIR 已负 |
| **P5** | `mean10(bm_std)×\|ret_lag5\|` | 0.42 / 0.72 | vol | −26.6%/−59.0%/ **−0.67** | −27.9%/−60.9%/−0.72 | 1.16 | **fail_precheck** — Sharpe≤0；vol 拥挤 |
| **P6** | `std10(ret_ts_std10)` | −0.02 / 0.65 | vol | −19.5%/−51.5%/ **−0.42** | −20.6%/−52.8%/−0.46 | 1.16 | **fail_precheck** — Sharpe≤0 |
| **P7** | `abs(std10(ret_ts_std10))` | −0.02 / 0.65 | vol | −19.5%/−51.5%/ **−0.42** | −20.6%/−52.8%/−0.46 | 1.16 | **fail_precheck** — 与 P6 同构 |
| **P8** | `mean20(max20(ret_lag1)/mean5(ex_lag1))` | 0.18 / 0.65 | mixed | −17.7%/−48.7%/ **−0.42** | −20.2%/−51.8%/−0.51 | 1.16 | **fail_precheck** — Sharpe≤0 |
| **P9** | `\|mean20(ret_lag5)−mean20(bm_std)\||` | −0.13 / 0.37 | mixed | −14.7%/−53.8%/ **−0.23** | −16.6%/−54.1%/−0.30 | 1.16 | **fail_precheck** — Sharpe≤0 |
| **P10** | `−max20(ret_lag1)` | 0.20 / 0.46 | near_rel | −8.2%/−42.3%/ **−0.10** | −9.6%/−43.0%/−0.15 | 1.16 | **fail_precheck** — Sharpe≤0（相对最轻负） |
| **P11** | `mean10(−ret_lag1)` | 0.35 / 0.39 | near_rel | −26.8%/−58.9%/ **−0.66** | −27.4%/−59.5%/−0.69 | 1.16 | **fail_precheck** — Sharpe≤0；纯反转近亲 |
| **P12** | `\|std10 × Δ5(ret_ts5)\||` | −0.24 / 0.98 | mixed | −21.4%/−52.5%/ **−0.43** | −22.5%/−53.8%/−0.47 | 1.16 | **fail_precheck** — 包窗虚高、全样本负 |
| **P13** | `Δ5(ret_std)×std10(ret_lag1)` | 0.01 / 0.50 | vol | −25.5%/−66.8%/ **−0.64** | −24.7%/−65.7%/−0.62 | 1.16 | **fail_precheck** — Sharpe≤0；MDD 最深 |
| **P14** | `\|mean10(ex_lag5)+mean5(bm_lag1)\||` | −0.33 / 0.43 | mixed | −23.1%/−57.8%/ **−0.61** | −23.3%/−57.8%/−0.62 | 1.16 | **fail_precheck** — Sharpe≤0 |
| **P15** | `−mean10(ex_ts_mean5)` | 0.16 / 0.17 | near_rel | −25.2%/−56.5%/ **−0.60** | −25.2%/−56.2%/−0.60 | 1.16 | **fail_precheck** — Sharpe≤0；经典 −excess 动量 |

†100万与60万同权同构；数值接近，个别臂因冲击略差。未开 X2 / S / 密封。

---

## 5. 相对 v20–v22

| 版 | 特征 | 标签 | 包 ICIR 问题 | X1 冒烟 |
|---|---|---|---|---|
| v20 | 份额流（trade_date） | 次日流延续 | 自相关虚高 ≈10 | 全 fail |
| v21 | 份额流（trade_date **泄漏**） | fwd excess | PIT≈−0.1；泄漏≈+1.6 | 全 fail |
| v22 | 份额流 **PIT asof ✅** | fwd excess | 包窗高 PIT（尤 abs(flow)）不可外推 | 全 fail |
| **v23** | **价/波动 only**（流暂停） | fwd excess | PIT≡LEAK（价叶无 asof）；**包窗虚高、全样本塌缩**；近 REL-MOM/PXVOL | **全 fail** |

v23 正确停掉份额流，但价叶短窗 GP 仍产出「包内好看、X1 不可交易」的截面 ICIR；与已 fail 的行业相对动量/波动拥挤同构风险明确。

---

## 6. 处置

- **裁决：reject**（非 research_observe：无臂 X1 Sharpe>0；非 explore-pass）
- `promotion_approved=false`；**handoff: NO**；**不交 Strategy**；不进 Alpha 短名单
- 容量结论：60万∧100万 X1 同败（同构）
- 建议 AI / New Bot：
  1. 勿再磨 V20–V22 份额流；亦勿把 v23 高 PIT（因 PIT≡LEAK）当进度
  2. 勿另开 REL-MOM / 宽基价量近亲（本包 Top 已大量撞车）
  3. 若续价叶：须包窗外（含 X1 或更长 OOS）真超额 ICIR 稳健 **且** 真 NAV X1 Sharpe>0∧avg_names>0，方可谈 observe
