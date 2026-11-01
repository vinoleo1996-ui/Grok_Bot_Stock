# WEIGHT RECEIPT · accrual_quality（研究级）

| 项 | 值 |
|---|---|
| 日期 | 2026-10-13 ≈02:24 ET |
| 作者 | QuantLab AI（执行器） |
| Leo | 本聊天确认卡「开下一正交叶（禁十灭+容量+两融同构）」 |
| mechanism_tag | `g1g5_ashare_accrual_quality_v1` |
| 叶名 | `accrual_quality` |
| promotion_approved | **false** |
| strategy_promotion | **false** |
| 不交 | Strategy；不下单；不开 GP；不密封；**不自跑** Book-Smoke |
| who_pays 预注册 | `docs/v2/AI_G1G5_ACCRUAL_QUALITY_WHO_PAYS_PREREG_ZH.md`（镜像 `output/ai_factory/`） |
| 脚本 | `research/g1g5_accrual_quality_weights.py` |
| 权重 | `output/ai_factory/g1g5_accrual_quality_daily_weights_20261013_022400.parquet` |
| run meta | `output/ai_factory/g1g5_accrual_quality_run_meta_20261013_022400.json` |
| G6 proof | `output/ai_factory/debate_ledger_g1g5_accrual_quality_20261013_022400_g6_proof.jsonl` |
| verify JSON | `output/alpha/AI_G1G5_ACCRUAL_QUALITY_WEIGHT_VERIFY_STATS_20261013_022400.json` |

---

## 1. 谁付钱（一句）

投资者过度依赖应计盈余、低估低应计/资产负债表盈余的对手盘——主臂=**PIT BS 营运资本应计/总资产**（Sloan 代理，**无 Dep**）→ 申万一级 demean → log(流通市值) 残差分位；**低应计优先**。主叙事=**非 OCF 应计质量（资产负债表）**。

应计公式（写死）：
`WC_ACC=(ΔCA−ΔCash)−(ΔCL−ΔSTD−ΔTP)`；`accrual_ratio=WC_ACC/max(TA,1e6)`；`available_at.normalize()≤session`；合并报表 report_type=1。

---

## 2. 机制差（尤其 vs OCF / 估值 / 容量 / 北向 / 两融）

| 对照 | 对方主轴 | 本叶机制差 |
|---|---|---|
| **indcap_momneut_ocf** | **ocf_to_profit** 现金流兑现 | 本叶 **不读 ocf_to_profit**；主臂=**资产负债表应计** |
| **d1_val_resid** | D1 EP 估值残差 | 残差对象=**accrual_ratio** 非 pe |
| **capacity_adv** | ADV 流动性分位 | **不**按 ADV 选股；容量仅单名顶≤4%+硬排除 |
| **northbound_flow** | hk_hold Δratio | **不读** hk_hold |
| **margin_delta** | 两融 Δrzye | **不读** margin；信号=BS 应计 |

Jaccard（活跃个股集，样例再平衡月）：

| 对照 | mean | max | frac≥0.7 | 硬拒同构？ |
|---|---|---|---|---|
| indcap_momneut_ocf | **0.128** | **0.194** | **0.0** | 否 |
| d1_val_resid | **0.149** | **0.216** | **0.0** | 否 |
| capacity_adv | **0.163** | **0.220** | **0.0** | 否 |
| northbound_flow | **0.130** | **0.212** | **0.0** | 否 |
| margin_delta | **0.174** | **0.289** | **0.0** | 否 |
| 十灭其余 | 均 max≤0.37；frac=0 | — | 0.0 | 否 |

→ 与 OCF/估值/容量/北向/两融 **显著分离**（未触发 ≥0.7∧近等权硬拒）。个股侧再平衡为预算内近似等权，但 Jaccard 远低于 0.7。

---

## 3. 计数与日历

| 项 | 值 | 自检 |
|---|---|---|
| rows | **52772** | ✅ |
| dates / sessions | **668** | ✅ 非 stub（>10） |
| instruments | **79**（含压舱） | ✅ |
| 日历 | **2024-01-02 → 2026-10-09** | ✅ |
| stub_forward_fill | **false** | ✅ |
| reaches_x2_end | **true** | ✅ |
| 日 Σw | min=**1.0** max=**1.0** | ✅ |
| 再平衡 | 35 次；`month_end_plus_first_last` | ✅ |
| 无负权 | 是 | ✅ |
| 评分池 | mid_large top≈80（金融缺 CA 跳过评分；可评分≈57） | ✅ |

---

## 4. 结构 / 硬约束

| 项 | 值 | 自检 |
|---|---|---|
| 宇宙 | mid_large PIT ∩ D0 panel；评分池≈80；活跃 topN=25 | ✅ |
| 行业硬顶 | ≤28% | ✅ |
| 单名上限 | ≤4%；实测 max=**0.032** | ✅ |
| 硬排除 | `600519.SH`=**0.0**；`002371.SZ`=**0.0** | ✅ |
| 压舱 | 510300 日均≈**0.200**；个股日均≈**0.800** | ✅ 落在 0.15–0.25；**禁** etf_core 0.70 overlay |
| 主数据 | `balancesheet_pit_tushare`（available_at PIT）；**未**用 ocf_to_profit；**未**用 D2 moneyflow | ✅ |
| 辅 | D1 仅 `float_mktcap` 作残差协变量；**非** ADV 选股 | ✅ |
| PIT | `available_at.normalize()≤session` | ✅ |
| G6 | **pass** | ✅ |
| peak_rss_mb | **2079.3** | ⚠ 目标 ≤1.5GB 未达（与同厂叶 margin≈1978 / northbound 同量级）；已分块读 BS、早释 D1；主因共享 `build_daily_weights_expand` |

---

## 5. 冲击 / 容量双读说明（60万∧100万）

- 单票上限 **4%**；绑定研究不自跑 Smoke。
- 硬排除成交缺口巨头 `600519`/`002371`。
- **不**按 ADV 分位选股；容量仅为硬约束。
- 主腿=BS 应计（非 OCF、非 moneyflow）。
- 请 Alpha ACCEPT 后由父代理派 **Book-Smoke @60万∧100万 vs 510300** 做冲击/容量双读（本 RECEIPT 不自跑）。

---

## 6. Alpha 验收自检表（落盘即裁 · 含叶专硬点）

| # | 标准 | 结果 |
|---|---|---|
| 1 | 权重长表 date,instrument,target_weight；完整日更；日 Σw=1；禁 stub；无负权；附计数 | ✅ rows=52772 / dates=668 / n_inst=79；Σw=1；stub_ff=false |
| 2 | mid_large PIT；BS available_at 不前视；600519/002371=0 | ✅ |
| 3 | vs 十灭+capacity+margin+OCF/估值/北向 Jaccard；硬拒 ≥0.7∧近等权 | ✅ 全 frac=0；vs OCF max=0.194；vs margin max=0.289；vs capacity max=0.220 |
| 4 | 证明≠OCF 换皮：禁 ocf_to_profit；机制差=BS 应计 vs OCF | ✅ §1–2；预注册已落 |
| 5 | 正交残差说明 + who_pays | ✅ |
| 6 | 冲击/容量 @60∧100万说明 + 单票上限 | ✅ §5；单票≤4% |
| 7 | G6 + peak_rss | ✅ G6=pass；peak=2079.3MB（软标超，见上） |
| 8 | D2 moneyflow 未作满样本主腿 | ✅ 主腿=balancesheet_pit |
| — | 禁 GP / live=false / 不交 Strategy | ✅ |
| — | 不自跑 Book-Smoke | ✅ |

**可派 Alpha 研究级 ACCEPT**：自检硬项全绿；软项 peak_rss 请 Alpha 知悉，不阻断派单（与同厂叶一致）。ACCEPT 后再派 Smoke。

---

## 7. 明确未做

- 未开 GP；未交 Strategy；未下单；未密封
- 未读 ocf_to_profit；未用 moneyflow 主腿；未用 ADV 分位选股；未读 margin/hk_hold
- **未自跑** Book-Smoke
