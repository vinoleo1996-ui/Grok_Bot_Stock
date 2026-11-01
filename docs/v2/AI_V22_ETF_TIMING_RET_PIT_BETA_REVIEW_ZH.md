# AI v22 `etf_timing_ret_pit` — Beta 纸深度复核

更新：2026-10-12 19:59 ET（America/New_York）  
来源包：`output/ai_factor/gp_reopen_hardgate_v22_etf_timing_pit/`  
说明：`BETA_NOTE_ZH.md`；包：`beta_etf_timing_ret_pit_package.json`；`pit_asof_meta.json`；`dual_icir_summary.json`；`label_definition.json`  
复核方：QuantLab Beta。`promotion_approved=false`。**不交 Strategy**。  
冒烟 runner：`output/v3/run_etf_timing_v22_pit_smoke.py`；诊断：`output/v3/etf_timing_v22_pit/diagnostics.json`；batch：`output/v3/pretest_batch_20261012_etf_timing_v22_pit.json`。

---

## 0. 一句话裁决

**reject / research_observe。**  
PIT asof 接线属实（`available_at ≤ D 09:00`，非固定 lag1；≈76% 次日开盘 / ≈24% 当日开盘可用）。标签仍是 **fwd excess vs 510300**。但：①叶子份额流 **自相关仍极强**（PIT ICIR vs 次日流 ≈**+14.4**）；②包内高 PIT ICIR（max≈2.71）在包窗上对真超额 **不可稳健复现**（全样本大多≈0 或负；`abs(flow)` 类包窗 PIT≈2.9 而 LEAK≈−0.8——**高 PIT 虚高风险，方向与 v21 泄漏相反**）；③60万 X1 真持行业 ETF **P1–P10 全 fail_precheck**（Sharpe≤0）。无交接。

---

## 1. 包内容摘要

| 项 | 内容 |
|---|---|
| sleeve | `etf_timing_ret_pit`（`for_beta=true`，不进 Alpha） |
| evals / GATE_OK_PIT | 120 / **45**；peak≈629MB；seed=20261105；explore `2024-06-03→2025-06-30` |
| 叶子 X | flow：`ind_etf_share_flow` / `etf_all_flow` / `etf_share_chg_major` / `etf_share_chg_theme`；价：`ind_ret_lag1` / `ind_excess_lag1` / `ind_ret_ts_mean_5` / `ind_excess_ts_mean_5` |
| 标签 y | **fwd_1d_excess_vs_510300**（主）；fwd_5d（副）；**NOT flow_continuation** |
| PIT 规则 | `available_at ≤ decision_time(D)`；`DECISION_CLOCK=open` → D 09:00；禁止固定 lag1 / trade_date 同日 |
| 闸门 | **只认 PIT ICIR**；`icir_leak_*` 诊断不过闸；成本 25bp；冲击 60∧100万 |
| 双 ICIR（包） | PIT median≈−0.03 max≈**2.71**；LEAK median≈−0.33 max≈2.00 |
| 典型 Top | `ts_mean_10(sub(ts_std_10(major), ts_mean_20(ind_ret_lag1)))`；`abs(ind_etf_share_flow)`；价叶子 `neg(ind_excess_ts_mean_5)` 等 |

---

## 2. PIT asof 核验 + flow 自相关残差

### 2.1 asof 是否真按墙钟？

| 检验 | 结果 |
|---|---|
| `pct_usable ≥ available_date` | **1.0** ✅ |
| 日历 lag≥1（≈23:59→次日开盘） | **≈76.2%**（包称 ~75%）✅ |
| 当日可用（≈09:00→同日开盘） | **≈23.8%**（包称 ~25%）✅ |
| PIT≠LEAK | `|PIT−LEAK|` 均值 ≈**11588** 万元流 ✅ 非同一面板 |
| 相对 v21 | v21 用 `normalize()+1d`（固定 lag1）❌；v22 墙钟 asof ✅ |

### 2.2 流自相关 / 真超额（防再踩 v20/v21）

| 检验 | 数值 | 解读 |
|---|---|---|
| 裸流 PIT vs 次日流 ICIR | **+14.39** | 叶子仍强自相关（甚于 v20/v21） |
| 裸流 LEAK vs 次日流 | +10.70 | 泄漏路径同构自相关 |
| 截面均值 lag1 / lag5 | **0.57 / 0.24** | 流持续 |
| 裸流 PIT vs fwd1d excess | **−0.52** | 对价格偏负 |
| `abs(flow)` PIT vs excess | **−0.20** | abs 也不预测超额（全样本） |
| `abs(flow)` **包窗** PIT / LEAK vs excess | **+2.93 / −0.82** | **包窗 PIT 虚高、LEAK 反向**——高 PIT 风险（v21 泄漏虚高的反面） |

**结论：** asof 接线过关；流自相关未解。包内 Top 高 PIT 不可当作可交易证据——须看真净值。

---

## 3. 对照 Beta 约束

| 约束 | 判定 |
|---|---|
| 禁小盘 | amt20≥2000 + list≥60d ✅ |
| 禁 CB/金主仓 | 残差 **510300**（非 GOLD）✅ |
| 行业 ETF 时序袖套 | 形态 ✅ |
| 非 IND-RATE 削仓皮 | 真持行业篮顶 tercile ✅ |
| 必须预测组合收益且可交易 | **不满足** — 包窗 ICIR 不稳；X1 组合全败 |

---

## 4. 真实收益冒烟（60万 X1；扣成本引擎）

规则：月频；GP 得分取液态行业 ETF **顶 tercile 等权**；空仓→510300；X1 Sharpe≤0 或 avg_names=0 → **fail_precheck**（不开 X2）。AUM 100万未开。

| arm_id | 表达式（摘） | 全样本 PIT/LEAK excess | 包窗 PIT/LEAK | 去流残差 | X1 CAGR/MDD/Sharpe | avg | 处置 |
|---|---|---|---|---|---|---|---|
| **P1** | `ts_mean10(std10(major)−mean20(ret_lag1))` | 0.11 / 0.05 | 0.50 / 0.48 | 0.19 | −6.9%/−45.3%/ **−0.11** | **0.0** | **fail_precheck**（major X1 空） |
| **P2** | `−theme − mean20(excess_lag1)` | 0.06 / 0.06 | 0.98 / 0.98 | −0.19 | −24.6%/−57.5%/ **−0.56** | 1.09 | **fail_precheck** |
| **P3** | `abs(ind_flow)` | −0.20 / −0.68 | **2.93 / −0.82** | −0.22 | −20.2%/−48.2%/ **−0.51** | 1.16 | **fail_precheck** |
| **P4** | `ts_mean10(mean10(major)−abs(ex_ts5))` | 0.00 / −0.17 | 0.47 / 0.37 | −0.22 | −6.9%/−45.3%/ **−0.11** | **0.0** | **fail_precheck** |
| **P5** | `mean5(theme)/mean10(ret_lag1)` | 0.60 / 0.68 | 1.57 / 1.78 | 0.50 | −15.9%/−48.5%/ **−0.35** | 1.09 | **fail_precheck** |
| **P6** | `−ex_ts5 / std10(ind_flow)` | 0.11 / −0.11 | 2.00 / 1.90 | 0.04 | −24.3%/−57.6%/ **−0.59** | 1.13 | **fail_precheck** |
| **P7** | `−abs(ret_ts5)/mean5(ret_lag1)` | 0.26 / 0.26 | 1.03 / 1.03 | 0.22 | −18.2%/−46.7%/ **−0.46** | 1.16 | **fail_precheck** |
| **P8** | `mean20(mean5(all)/mean5(ret_ts5))` | −0.21 / −0.32 | 0.45 / −0.63 | −0.08 | −27.4%/−58.2%/ **−0.79** | 1.09 | **fail_precheck** |
| **P9** | `abs(Δ5(ind_flow))` | −0.29 / −0.64 | 1.84 / 0.34 | −0.05 | −19.0%/−46.0%/ **−0.43** | 1.16 | **fail_precheck** |
| **P10** | `abs(Δ5(ind)−mean20(ex_lag1))` | −0.34 / −0.71 | 1.76 / 0.32 | −0.15 | −22.1%/−51.5%/ **−0.54** | 1.09 | **fail_precheck** |

†P1/P4：`etf_share_chg_major` 在 X1 几乎无液态行业映射 → avg_names=0，NAV≈纯 510300（Sharpe 仍≤0）。

---

## 5. 相对 v20 / v21

| 版 | 标签 | 特征对齐 | 包 ICIR 问题 | X1 冒烟 |
|---|---|---|---|---|
| v20 | 次日流延续 | trade_date | 自相关虚高 ≈10 | 全 fail |
| v21 | fwd excess | trade_date **泄漏** | PIT≈−0.1；泄漏≈+1.6 | 全 fail |
| **v22** | fwd excess | **PIT asof ✅** | 包窗高 PIT（尤 `abs(flow)`）**不可外推**；流自相关仍在 | **全 fail** |

v22 修了 v21 的 trade_date 泄漏接线，但 **未解决「流叶子 + 短探索窗 → 虚高截面 ICIR」**；真持仓仍不过闸。

---

## 6. 处置

- **裁决：reject**；`promotion_approved=false`；**handoff: NO**
- 不交 Strategy；不进 Alpha 短名单
- 建议 AI：若续 Track B，须 (a) 去流残差后 PIT ICIR 仍>0；(b) 包窗外（至少含 X1 或更长 OOS）真超额 ICIR 稳健；(c) 禁止以 `abs(flow)` / 强自相关变换单独过闸
