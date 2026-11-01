# WEIGHT RECEIPT · moneyflow_resid（研究级）

| 项 | 值 |
|---|---|
| 日期 | 2026-10-13 ≈05:07 ET |
| 作者 | QuantLab AI（执行器） |
| Leo | 本聊天明示「开下一正交叶」+ New Bot 交叉确认「需要」 |
| mechanism_tag | `g1g5_ashare_moneyflow_resid_v1` |
| 叶名 | `moneyflow_resid` |
| promotion_approved | **false** |
| strategy_promotion | **false** |
| 不交 | Strategy；不下单；不开 GP；不密封；**不自跑** Book-Smoke |
| who_pays 预注册 | `docs/v2/AI_G1G5_MONEYFLOW_RESID_WHO_PAYS_PREREG_ZH.md`（镜像 `output/ai_factory/`） |
| 脚本 | `research/g1g5_moneyflow_resid_weights.py` |
| 权重 | `output/ai_factory/g1g5_moneyflow_resid_daily_weights_20261013_050716.parquet` |
| run meta | `output/ai_factory/g1g5_moneyflow_resid_run_meta_20261013_050716.json` |
| G6 proof | `output/ai_factory/debate_ledger_g1g5_moneyflow_resid_20261013_050716_g6_proof.jsonl` |
| verify JSON | `output/alpha/AI_G1G5_MONEYFLOW_RESID_WEIGHT_VERIFY_STATS_20261013_050716.json` |

---

## 1. 谁付钱（一句）

忽视行业/市值中性后的个股净资金流入强度（相对 ADV）的对手盘——主臂=**PIT Σ net_mf_amount（L≈20）/ ADV** → 申万一级 demean → log(流通市值) 残差分位；**高残差优先**。主叙事=**个股资金流残差（moneyflow/ADV）**。ADV **仅分母**，不作流动性分位选股。

公式（写死）：`S=Σ_{available_at∈[session−20d,session]} net_mf_amount`；`ADV=float_mktcap×turnover_rate/100`；`x=S/max(ADV,1e3)`；`available_at.normalize()≤session`。

---

## 2. 机制差（尤其 vs 容量 / 两融 / 应计 / 北向 / 估值 / OCF）

| 对照 | 对方主轴 | 本叶机制差 |
|---|---|---|
| **capacity_adv** | **log(ADV) 流动性分位选股** | ADV **仅分母**；选股=净流入强度残差 |
| **margin_delta** | 两融 Δrzye | **不读** margin；信号=D2 moneyflow |
| **accrual_quality** | BS 营运资本应计 | **不读** balancesheet；信号=日频资金流 |
| **northbound_flow** | hk_hold Δratio | **不读** hk_hold |
| **d1_val_resid** | D1 EP 估值残差 | 残差对象=**mf/ADV** 非 pe |
| **indcap_momneut_ocf** | ocf_to_profit | **不读** OCF |

Jaccard（活跃个股集，样例再平衡月）：

| 对照 | mean | max | frac≥0.7 | 硬拒同构？ |
|---|---|---|---|---|
| capacity_adv | **0.333** | **0.471** | **0.0** | 否 |
| margin_delta | **0.235** | **0.351** | **0.0** | 否 |
| accrual_quality | **0.175** | **0.351** | **0.0** | 否 |
| northbound_flow | **0.236** | **0.345** | **0.0** | 否 |
| d1_val_resid | **0.284** | **0.448** | **0.0** | 否 |
| indcap_momneut_ocf | **0.294** | **0.406** | **0.0** | 否 |
| resid_etf | 0.377 | 0.500 | 0.0 | 否 |
| expand | 0.352 | 0.571 | 0.0 | 否 |
| 其余十灭侧 | 均 max≤0.375；frac=0 | — | 0.0 | 否 |

→ 与容量/两融/应计/北向/估值/OCF **显著分离**（未触发 ≥0.7∧近等权硬拒）。个股侧再平衡为预算内近似等权，但 Jaccard 远低于 0.7。

### 残差暴露说明（capacity_adv + size/mom/lowvol/value）

- 主信号已做 **申万一级 demean + log(流通市值) OLS 残差**，故意压低对 size 的线性暴露。
- **禁**教科书动量/价值主线选股（不读收益排序、不读 EP/BM）。
- **不读**波动率排序 → 非 lowvol 主轴。
- 相对 **capacity_adv**：对方按 ADV 分位选股；本叶 ADV 只做归一分母，暴露叙事正交。
- 本说明供 ACCEPT 归因，**非**另开选股轴。

---

## 3. 计数与日历

| 项 | 值 | 自检 |
|---|---|---|
| rows | **32732** | ✅ |
| dates / sessions | **668** | ✅ 非 stub（>10） |
| instruments | **49**（含压舱） | ✅ |
| 日历 | **2024-01-02 → 2026-10-09** | ✅ |
| stub_forward_fill | **false** | ✅ |
| reaches_x2_end | **true** | ✅ |
| 日 Σw | min=**1.0** max=**1.0** | ✅ |
| 再平衡 | 35 次；`month_end_plus_first_last` | ✅ |
| 无负权 | 是 | ✅ |
| 评分池 | mid_large top≈50；moneyflow 行加载 **34008** | ✅ |
| 主数据 | D2 `moneyflow_stock_daily_pit` ACCEPT_FULL | ✅ |

---

## 4. 结构 / 硬约束

| 项 | 值 | 自检 |
|---|---|---|
| 宇宙 | mid_large PIT ∩ D0 panel；评分池≈50；活跃 topN=25 | ✅ |
| 行业硬顶 | ≤28% | ✅ |
| 单名上限 | ≤4%；实测 max=**0.032** | ✅ |
| 硬排除 | `600519.SH`=**0.0**；`002371.SZ`=**0.0**（按 ADV/成交缺口） | ✅ |
| 压舱 | 510300 日均≈**0.243**；个股日均≈**0.757** | ✅ 落在 ≈0.15–0.25 软带；**禁** etf_core 0.70 overlay |
| 辅 | D1 `float_mktcap`+`turnover_rate` → ADV **仅分母** + 市值残差；**非** ADV 选股 | ✅ |
| PIT | `available_at.normalize()≤session` | ✅ |
| G6 | **pass** | ✅ |
| peak_rss_mb | **2009.4**（`/usr/bin/time` MaxRSS≈2057592 KB） | ⚠ 目标 ≤1.5GB 未达（与同厂叶 margin≈1978 / accrual≈2079 同量级）；已分块读 moneyflow、早释 D1；主因共享 `build_daily_weights_expand` |

---

## 5. 冲击 / 容量双读说明（60万∧100万）

- 单票上限 **4%**；绑定研究不自跑 Smoke。
- 硬排除成交缺口巨头 `600519`/`002371`。
- **不**按 ADV 分位选股；ADV 仅净流入分母；容量仅为硬约束。
- 主腿=D2 moneyflow 残差。
- 请 Alpha ACCEPT 后由父代理派 **Book-Smoke @60万∧100万 vs 510300** 做冲击/容量双读（本 RECEIPT 不自跑）。

---

## 6. Alpha 验收自检表（落盘即裁 · 含叶专硬点）

| # | 标准 | 结果 |
|---|---|---|
| 1 | 权重长表 date,instrument,target_weight；完整日更；日 Σw=1；禁 stub；无负权；附计数 | ✅ rows=32732 / dates=668 / n_inst=49；Σw=1；stub_ff=false |
| 2 | mid_large PIT；moneyflow available_at 不前视；600519/002371=0 | ✅ |
| 3 | vs 十二灭+capacity Jaccard；硬拒 ≥0.7∧近等权 | ✅ 全 frac=0；vs capacity max=0.471；vs margin max=0.351；vs accrual max=0.351 |
| 4 | 证明≠capacity 换皮：ADV 仅分母；机制差=mf/ADV 残差 vs log(ADV) 分位 | ✅ §1–2；预注册已落 |
| 5 | 正交残差说明 + who_pays（含 size/mom/lowvol/value） | ✅ §2 残差暴露 |
| 6 | 冲击/容量 @60∧100万说明 + 单票上限 | ✅ §5；单票≤4% |
| 7 | G6 + peak_rss | ✅ G6=pass；peak=2009.4MB（软标超，见上） |
| 8 | D2 moneyflow 作满样本主腿（ACCEPT_FULL） | ✅ |
| — | 禁 GP / live=false / 不交 Strategy | ✅ |
| — | 不自跑 Book-Smoke | ✅ |

**可派 Alpha 研究级 ACCEPT**：自检硬项全绿；软项 peak_rss 请 Alpha 知悉，不阻断派单（与同厂叶一致）。ACCEPT 后再派 Eng Book-Smoke。

---

## 7. 明确未做

- 未开 GP；未交 Strategy；未下单；未密封
- 未按 ADV 分位选股；未读 margin/hk_hold/balancesheet/ocf_to_profit
- **未自跑** Book-Smoke；未启 uvicorn
