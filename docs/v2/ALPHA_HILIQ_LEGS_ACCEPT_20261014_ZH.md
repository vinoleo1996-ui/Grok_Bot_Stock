# HI_LIQ_V1.1 纸面腿正式验收（Alpha）— v4：§8 读法勘误后重报（取代 v3）

- **落盘**：2026-10-18 00:53 ET（v3 原文另存 `docs/v2/ALPHA_HILIQ_LEGS_ACCEPT_20261014_v3_ZH.md`）
- 依据：Arch N4（`docs/v2/audit/AUDIT_20261018_0016_ET_ZH.md`）、AI 对账（`docs/v2/AI_EQINC_SEC8_RECONCILE_ZH.md`）、Alpha 独立复核与勘误（`docs/v2/ALPHA_EQUITY_SIGN_RECON_20261018_ZH.md` §6）。**阈值不变**；数据 `output/alpha/recon_eqinc/step_c_s8_errata_sparse_ic.json`、`step_d_fullsleeve_b.json`；JSON v4。

## v4 勘误读法逐腿（HI_LIQ，X2 样本内，h=20；t = naive/neff/HAC 仅披露）

| 腿 | A(i) 0/1 vs 原始 fwd20（HAC t） | A(ii) 残差 z vs 中性 fwd（HAC t） | A′(i) / A′(ii) | CMC(ii) ΔIC（HAC t）/ ΔICIR 全,滚 | B 全袖净 冻结风格 / AI 风格 | v3 → **v4** |
|---|---|---|---|---|---|---|
| equity_incentive | +0.0098（3.23） | +0.0092（2.55） | +0.0073 / +0.0103 | +0.0026（3.59）/ +0.092,+0.106 | +8.9%（1.66）/ −8.9% | WATCH → **WATCH** |
| earnings_event | +0.0053（1.31） | +0.0190（3.93） | +0.0030 / +0.0189 | +0.0014（2.14）/ +0.034,−0.003 | −9.6% / −16.5% | WATCH/DONE_FAIL → **WATCH** |
| insider_increase | +0.0042（1.30） | −0.0189（−6.68） | −0.0032 / −0.0183 | −0.0013（−2.77）/ −0.030,−0.035 | −12.5%（−2.32）/ −23.4% | WATCH/DONE_FAIL → **WATCH/DONE_FAIL** |
| insurer_surv（调研） | +0.0010（0.32） | +0.0130（3.11） | −0.0071 / +0.0138 | +0.0010（2.10）/ +0.033,+0.037 | +3.4% / −5.3% | WATCH/DONE_FAIL → **WATCH**（封顶） |
| report_rc_allup（研报） | −0.0026（−0.65） | +0.0097（2.30） | +0.0017 / +0.0093 | +0.0007（1.12）/ +0.029,+0.051 | +3.6% / −13.3% | WATCH → **WATCH**（封顶） |
| 参照 capacity_adv | −0.0104（−1.71） | +0.0090（1.72） | — | — | +8.2% / −48.7%（待核） | 核心对照 |

- 包级：**NO_ACCEPT**。五腿 A′ 仍全部不过：CMC ΔIC 都低于 +0.003，最高是 equity_incentive 的 +0.0026。不进 GATE_V3、不派 Eng、不进纸面。
- 状态变更：earnings_event 和 insurer_surv **撤销 DONE_FAIL**，原因是 v3 的「ΔIC 显著拖累」来自测量缺陷，勘误后 ΔIC 为正但不到阈值。insider_increase 在勘误后 A 和 CMC 都显著为负，**维持 DONE_FAIL**。
- capacity_adv 自身在 v3 的残差 IC 0.050，大部分也是稀疏全池 RankIC 带来的风格溢价。勘误后（ii）只有 +0.009（HAC 1.72），（i）为负。B 在 AI 风格下 −48.7%，这个幅度需要核实。这对 B4/Core 的参照有影响，见回执。
- 所有 B 都是近似值：滞后 2 日权重 × 中性残差收益 − 成本，不是 Eng X2，也不按手取整。

---
（以下为 v3 原文，保留备查）

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


---
> **v4.1r（2026-10-18 01:21 ET 写入）**：01:05 ET 重启丢失原 v4.1 节，按主 Agent 01:21 指示由 _recovery/alpha 重写版以新版本号 v4.1r 写入；数字照对话记录，未重算，待 step_e 重算逐项核对与 Arch 审查。

> RECONSTRUCTED from Alpha chat record 2026-10-18; numbers as recorded, not recomputed

# HI_LIQ 五腿 v4 / v4.1 裁定（恢复副本）

## v4 表（A(ii) IC20 (HAC t) / CMC ΔIC (HAC t) / B 中性化净超额：冻结风格集 vs AI 风格集）
| 腿 | A(ii) | CMC ΔIC | B 冻结 | B AI | 裁定 |
|---|---|---|---|---|---|
| equity_incentive | +0.0092 (2.55) | +0.0026 (3.59) | +8.9% | −8.9% | WATCH |
| earnings_event | +0.0190 (3.93) | +0.0014 (2.14) | −9.6% | −16.5% | DONE_FAIL→WATCH |
| insider_increase | −0.0189 (−6.68) | −0.0013 (−2.77) | −12.5% | −23.4% | 维持 DONE_FAIL |
| insurer_surv | +0.0130 (3.11) | +0.0010 (2.10) | +3.4% | −5.3% | →WATCH（类型上限） |
| report_rc | +0.0097 (2.30) | +0.0007 (1.12) | +3.6% | −13.3% | WATCH（类型上限） |

## v4.1（AI 风格集列作废：同日 logmv 回归同日收益的 bug；改前一日 logmv 重算）
| 腿 | B 冻结 | B AI(修正) | 读数 | 裁定 |
|---|---|---|---|---|
| equity_incentive | +8.9% (t 1.66) | +8.7% (t 1.60) | PASS-weak | WATCH（CMC 0.0026 < 0.003） |
| earnings_event | −9.6% | −2.0% | FAIL | WATCH |
| insider_increase | −12.5% (t −2.32) | −12.8% (t −2.42) | FAIL | WATCH/DONE_FAIL |
| insurer_surv | +3.4% | +6.3% | PASS-weak | WATCH（类型上限） |
| report_rc | +3.6% | +4.1% | PASS-weak | WATCH（类型上限） |
| capacity_adv（参照） | +8.2% | −1.3% | PASS* | 参照 |

- 前一日池（A3）每腿变动 ≤1pp。整包 NO_ACCEPT。
- 勘误第 3 条（两套风格集符号相反记 PASS*）保留，对后续叶生效。
- 叶22 rd_innov：AI 自评 WATCH，未提交验收，仅记档。
- 冻结风格集使用 t−1 暴露，不受影响；AI 修正已复现：capadv −1.32%（AI −1.35%），equity +8.73%（AI +8.80%）。

> **已核对（2026-10-18 01:46 ET，重启后重建）**：step_e 复现（旧 cs_panel，非新证据，阈值不变）逐项与本节记录数字一致；step_e_fullsleeve_b_v41.json sha256=367556b4180c6afb78a10b19817f07be2ef27e6d62cf60ddf186dc5d5b0c087e；step_c sha256=fdd911ff…（未重跑，cap (ii)/(i) 一致）；依据 Arch .ok d0816a37…。

> **披露（Arch 裁定 VALID_WITH_DISCLOSURE，10-18 01:48 ET）**：① 01:37 首跑峰值 RSS 1,573,940KB 超 1.5GB 被看门狗杀、无产物；② 01:44 重跑仅加 MALLOC_ARENA_MAX=2 / MALLOC_TRIM_THRESHOLD_=0，峰值 RSS 未记录；③ nice 19 串行；④ .ok d0816a37 已用尽，不得再用。后续：e88b88e7 须改按年分块读取并自记峰值 RSS 后方可新跑。step_e=367556b4…，step_c=fdd911ff…

> **补录（10-18 01:53 ET）**：重跑峰值 RSS 未记录。唯一记录为首跑（01:37）peak_VmHWM 1,573,940KB，见 output/alpha/recon_eqinc/step_e_v41_regen.log 第 11–12 行；未为测内存重跑。
