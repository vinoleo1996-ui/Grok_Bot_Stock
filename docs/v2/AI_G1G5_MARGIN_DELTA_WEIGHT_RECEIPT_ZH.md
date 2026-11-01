# WEIGHT RECEIPT · margin_delta（研究级）

| 项 | 值 |
|---|---|
| 日期 | 2026-10-13 ≈02:08 ET |
| 作者 | QuantLab AI（执行器） |
| Leo | 本聊天确认卡「开工下一正交叶」 |
| mechanism_tag | `g1g5_ashare_margin_delta_v1` |
| 叶名 | `margin_delta` |
| promotion_approved | **false** |
| strategy_promotion | **false** |
| 不交 | Strategy；不下单；不开 GP；不密封；**不自跑** Book-Smoke |
| who_pays 预注册 | `docs/v2/AI_G1G5_MARGIN_DELTA_WHO_PAYS_PREREG_ZH.md`（镜像 `output/ai_factory/`） |
| 脚本 | `research/g1g5_margin_delta_weights.py` |
| 权重 | `output/ai_factory/g1g5_margin_delta_daily_weights_20261013_020825.parquet` |
| run meta | `output/ai_factory/g1g5_margin_delta_run_meta_20261013_020825.json` |
| G6 proof | `output/ai_factory/debate_ledger_g1g5_margin_delta_20261013_020825_g6_proof.jsonl` |
| verify JSON | `output/alpha/AI_G1G5_MARGIN_DELTA_WEIGHT_VERIFY_STATS_20261013_020825.json` |

---

## 1. 谁付钱（一句）

国内两融/杠杆资金边际加仓与去杠杆压力下的错误定价对手盘——全窗主臂=**融资余额 Δrzye**（asof `available_at`）→ 申万一级 demean → log(流通市值) 残差分位；高 Δ（融资净增）优先。

---

## 2. 机制差（vs northbound / capacity_adv）

| 对照 | 对方主轴 | 本叶机制差 |
|---|---|---|
| **northbound_flow** | 主臂 **hk_hold Δratio**；两融仅 hk 断档补窗且 tag 仍 northbound | 本叶 **全窗主臂=两融**；**不读 hk_hold**；tag=`…margin_delta…` |
| **capacity_adv** | 主信号=**ADV 流动性分位**；容量硬约束 | **不**按 ADV 分位选股；容量仅单名顶≤4% + 硬排除；信号=杠杆资金流 |

Jaccard（活跃个股集，样例再平衡月）：

| 对照 | mean | max | frac≥0.7 | 硬拒同构？ |
|---|---|---|---|---|
| capacity_adv | **0.315** | **0.400** | **0.0** | 否 |
| northbound_flow | **0.378** | **0.667** | **0.0** | 否（max&lt;0.7；frac=0） |
| 十灭其余 | 均 max≤0.43；frac=0 | — | 0.0 | 否 |

→ 与北向/容量 **显著分离**（未触发 ≥0.7∧近等权硬拒）。

---

## 3. 计数与日历

| 项 | 值 | 自检 |
|---|---|---|
| rows | **32732** | ✅ |
| dates / sessions | **668** | ✅ 非 stub（&gt;10） |
| instruments | **49**（含压舱） | ✅ |
| 日历 | **2024-01-02 → 2026-10-09** | ✅ |
| stub_forward_fill | **false** | ✅ |
| reaches_x2_end | **true** | ✅ |
| 日 Σw | min=**1.0** max=**1.0**（容差内） | ✅ |
| 再平衡 | 35 次；`month_end_plus_first_last` | ✅ |
| 无负权 | 是 | ✅ |

---

## 4. 结构 / 硬约束

| 项 | 值 | 自检 |
|---|---|---|
| 宇宙 | mid_large PIT ∩ D0 panel；评分池≈50；活跃 topN=25 | ✅ |
| 行业硬顶 | ≤28% | ✅（抽样复核无破） |
| 单名上限 | ≤4%；实测 max=**0.032** | ✅ |
| 硬排除 | `600519.SH`=**0**；`002371.SZ`=**0** | ✅ |
| 压舱 | 510300 日均≈**0.264**；个股日均≈**0.736** | ⚠ 压舱略高于 0.15–0.25 目标带（覆盖不足日抬升）；仍 ≪0.40 etf_core 漂移线；**禁** etf_core 0.70 overlay |
| 主数据 | `margin_detail_daily_2018plus`（rzye+available_at）；**未**用 D2 moneyflow 主腿 | ✅ |
| 辅 | D1 仅 `float_mktcap` 作残差协变量；**非** ADV 选股 | ✅ |
| PIT | `available_at.normalize()≤session` | ✅ |
| G6 | **pass** | ✅ |
| peak_rss_mb | **1978.5** | ⚠ 软标 ≤1.0GB 未达；与同厂叶（northbound≈2017 / capacity 同量级）一致，主因共享 `build_daily_weights_expand` 路径；已分块读 parquet、早释 D1 |

---

## 5. 冲击 / 容量双读说明（60万∧100万）

- 单票上限 **4%**；绑定研究不自跑 Smoke。
- 硬排除成交缺口巨头 `600519`/`002371`。
- **不**按 ADV 分位选股；容量仅为硬约束。
- 请 Alpha ACCEPT 后由父代理派 **Book-Smoke @60万∧100万 vs 510300** 做冲击/容量双读（本 RECEIPT 不自跑）。

---

## 6. Alpha 验收自检表（落盘即裁）

| # | 标准 | 结果 |
|---|---|---|
| 1 | 权重长表 date,instrument,target_weight；完整日更；日 Σw=1；禁 stub；无负权；附计数 | ✅ rows=32732 / dates=668 / n_inst=49；Σw=1；stub_ff=false |
| 2 | mid_large PIT；available_at 不前视；600519/002371 按规则=0 | ✅ |
| 3 | vs 十包+capacity_adv Jaccard；硬拒 ≥0.7∧近等权；报 mean/max/frac | ✅ 全 frac=0；vs capacity max=0.40；vs northbound max=0.667 |
| 4 | 正交残差说明 + who_pays | ✅ 见 §1–2；预注册已落 |
| 5 | 冲击/容量 @60∧100万说明 + 单票上限 | ✅ §5；单票≤4% |
| 6 | G6 + peak_rss | ✅ G6=pass；peak=1978.5MB（软标超，见上） |
| 7 | D2 moneyflow 未作满样本主腿 | ✅ 主腿=margin_detail |
| — | 禁 GP / live=false / 不交 Strategy | ✅ |
| — | 不自跑 Book-Smoke | ✅ |

**可派 Alpha 研究级 ACCEPT**：自检硬项全绿；软项 peak_rss 与压舱略偏请 Alpha 知悉，不阻断派单（与同厂叶一致）。ACCEPT 后再派 Smoke。

---

## 7. 明确未做

- 未开 GP；未交 Strategy；未下单；未密封
- 未读 hk_hold；未用 ADV 分位选股；未用 moneyflow 主腿
- **未自跑** Book-Smoke

