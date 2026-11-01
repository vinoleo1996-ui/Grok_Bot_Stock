# HI_LIQ_V1.1 纸面腿正式验收（Alpha）— v3：§8 范式材料补齐后重判

- **更新**：2026-10-18 00:10 ET（取代 v2 2026-10-14 08:34 ET，v2 原文另存 `docs/v2/ALPHA_HILIQ_LEGS_ACCEPT_20261014_v2_ZH.md`）
- 读法：`docs/v2/ALPHA_HILIQ_S8_PARADIGM_RULES_20261014_ZH.md`，2026-10-14 09:13:34 ET 冻结，冻结时还没算任何 §8 数字。范式见 `ALPHA_ACCEPT_PARADIGM_RESID_NEUT_ZH.md`，清单见 `ALPHA_HILIQ_GATEV3_ACCEPT_CHECKLIST_ZH.md` §2.1/§8。
- 数据：`output/alpha/hiliq_s8/ALPHA_HILIQ_S8_run20261017.json`；脚本 `research/alpha_hiliq_s8_paradigm.py`（nice，与 AI 串行）；JSON `output/alpha/ALPHA_HILIQ_LEGS_ACCEPT_20261014.json`（v3）
- 口径：股票池 HI_LIQ_V1.1；窗口 X2 2024-06-03→2026-10-09（样本内）；h=20；风格 = 申万一级 + log 流通市值 + β120 + 动量(t−120→t−20) + log ADV20；17.5bp；年化按 244 日。t 值有 naive / neff / HAC(lag 19) 三种，**只作披露**。
- 不改 FROZEN，不动纸面；promotion/live=false；禁 GP；不派 Eng。

## 1. 逐腿 §8

| 腿 | A 残差 RankIC / ICIR(全/滚) / t(naive/neff/HAC) | A′ 特质 IC（对 cap 正交） | CMC ΔIC / ΔICIR(全/滚) / ΔIC HAC t | B 中性净超额 60万 / 100万（HAC t） | C ρ / 持有期比 / 正交截距 vs cap | §8 | 终判 |
|---|---|---|---|---|---|---|---|
| equity_incentive 202436 | −0.0049 / −0.05,−0.08 / −1.08,−0.24,−0.31 | −0.0045 | −0.0012 / +0.001,−0.001 / −1.33 | **+17.3% (1.77) / +17.2% (2.27)** | 0.003 / 0.71 / +16.9% (t 1.74) | A✗ A′✗ B✓ C✓ | **WATCH**（IC 与收益口径分歧，待核） |
| earnings_event 202822 | +0.0030 / 0.02,0.05 / 0.56,0.12,0.16 | +0.0002 | −0.0023 / −0.018,−0.014 / **−2.80** | −7.7% / −7.2% | 0.005 / 0.65 / −9.8% | A✓ A′✗ B✗ C✓ | **WATCH/DONE_FAIL** |
| insider_increase 202928 | −0.0137 / −0.11,−0.19 / −2.51,−0.56,−0.77 | −0.0135 | −0.0018 / +0.006,+0.001 / −1.16 | −13.1% / −5.0%（换手 0.31/日） | −0.006 / 0.25 / −13.2% | A✗ A′✗ B✗ C✓ | **WATCH/DONE_FAIL** |
| insurer_surv 203108（调研类） | +0.0056 / 0.05,0.004 / 1.13,0.25,0.35 | +0.0052 | −0.0011 / −0.001,+0.005 / −1.42 | +1.4% / −3.1% | 0.004 / 0.49 / +1.4% | A✓ A′✗ B✗ C✓ | **WATCH/DONE_FAIL**（类型封顶 WATCH） |
| report_rc_allup 203201（研报类） | **+0.0304 / 0.25,0.24 / 5.74,1.28,1.63** | +0.0310 | +0.0010 / +0.021,+0.027 / +0.85 | −6.9% / −1.2% | 0.008 / 1.20 / −7.4% | A✓ A′✗ B✗ C✓ | **WATCH**（类型封顶，不走新叶路径） |
| 参照 capacity_adv 195620 | +0.0497 / 0.47,0.48 / 11.06,2.47,3.06 | — | — | Top-25 袖 +8.2% (1.04) | — | — | 核心对照（不变） |

- A′ 的 PASS 条件是特质 IC>0、CMC ΔIC ≥ +0.003、ΔICIR 两种读法都 ≥ +0.05，五腿全部不过。叠加 0.2·z_leaf 后，IC 都没超过 capacity_adv 单独的 IC。
- C 五腿都过。残差 ρ 都接近 0，也没有伪耦合。所谓「叠加 IC 高于加权和」，只是因为腿自身 IC 低，不是正交增量。
- naive t 和 HAC t 普遍差 3–4 倍（cap 是 11.1 对 3.1），说明重叠窗口确实会虚高 t，这也是两周后提议闸门改用 HAC 的依据。

## 2. 包级裁决
- **NO_ACCEPT**：§8 A/A′/B/C 已补齐，五腿都没全过，没有 RESEARCH_ACCEPT，不进 GATE_V3、不派 Eng、不进纸面。§2.1 行业硬闸仍维持 INDUSTRY_PASS；隔离区的 195* 仍判 REJECT_IND_CAP。
- earnings_event / insider_increase 的 DONE_FAIL 只针对它们作为「HI_LIQ 新腿候选」，**不改**现 top300 纸面轨（B4 / capacity_adv），也不替 Leo 决定 earnings_event 走不走纸面。HI_LIQ B4 合成里这两条腿的 25% 权重值得 Strategy 复看（只是提议）。
- equity_incentive 保持 WATCH：IC 读法（全池 RankIC）为负，收益读法（中性化后 top-N 净超额、对 cap 正交截距）为正，而且 AI 的 09:11 补充包（`output/ai_factory/hiliq_sec8/sec8_supplement.json`，风格集不同）给出的符号刚好相反（残差 IC 为正、中性净为负）。需要 AI 按同一风格集交叉核对后再判；核对完之前不派烟。

## 3. 披露 / 局限
- B 的计算：腿股票袖按权重取 top-N（6/10）、归一化，用滞后 2 日的权重乘中性化残差收益来近似 T+1，再扣成本·换手。这不是 Eng X2 撮合，也没有按手取整。
- capacity_adv 两档都用 Top-25 袖作为快慢参照。
- 全部是样本内结果，密封窗 N/A（腿从 2024-01 开始）。
