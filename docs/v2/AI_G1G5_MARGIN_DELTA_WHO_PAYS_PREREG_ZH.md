# who_pays 机制预注册 · 两融融资余额边际变化叶（研究级）

| 项 | 值 |
|---|---|
| 日期 | 2026-10-13 ET（America/New_York） |
| 作者 | QuantLab AI（执行器） |
| Leo 指令 | 本聊天确认卡「开工下一正交叶」→ 叶名 **margin_delta** |
| mechanism_tag | `g1g5_ashare_margin_delta_v1` |
| promotion_approved | **false** |
| strategy_promotion | **false** |
| 状态 | 预注册 → 产完整 X2 → WEIGHT RECEIPT（**不自跑** Book-Smoke；由父代理派 Alpha ACCEPT） |
| 不交 | Strategy；不下单；不开 GP；不密封 |
| 主数据 | `data/v2/margin/margin_detail_daily_2018plus.parquet`（`rzye` + `available_at`；trade_date 至 20261009） |
| 辅数据 | D1 `daily_basic` 仅取 `float_mktcap` 作对数流通市值残差协变量（**不**作 ADV 选股）；申万一级 PIT；mid_large PIT |
| **禁** | D2 moneyflow 作主腿；hk_hold；ADV 流动性分位选股；教科书 EP/BM/相对强弱主轴 |

---

## 1. 谁付的钱（一句）

**国内两融/杠杆资金边际加仓与去杠杆压力下的错误定价对手盘**——以个股 **融资余额 Δrzye**（asof `available_at`）经申万一级行业 demean + 对数流通市值残差后的分位作选股主信号；高 Δ（融资净增）优先；主叙事=**杠杆资金流**，不是北向持股、不是 ADV 容量、不是估值/OCF/相对强弱/四臂摩擦/调仓/ETF-core。

---

## 2. 数学（写死可检验）

| 项 | 口径 |
|---|---|
| Δrzye | 对每只股票，在 `available_at.normalize()≤session` 下取最近观测与约 **L=20 自然日** 前（或更早最近）观测：`δ = (rzye_t − rzye_{t−L}) / max(\|rzye_{t−L}\|, ε)`，ε=1 |
| 行业 demean | 在当日可评分集合内，按申万一级：`δ_ind = δ − mean_ind(δ)` |
| 市值残差 | 对 `δ_ind` 对 `log(float_mktcap)` 做截面 OLS（截距+斜率），取残差 `r`；行业内名过少时退化为仅 demean |
| 选股分位 | 按 `r` 降序（高残差=融资净增相对行业/市值偏强）；优先 `r>0` 侧；不足时填入全体可评分 |
| PIT | **仅** `available_at.normalize()≤session` 行；禁偷看未到 available_at 的 margin/D1 行 |
| 方向预注册 | **多头偏好融资余额上升侧**（杠杆资金净增）；非「相对强弱收益排序」 |

---

## 3. 可检验预测

1. 再平衡后持有窗内，高 `r` 组相对 510300 有正超额的倾向（研究级，非保证）。
2. 信号与 **northbound_flow**（主臂 hk_hold Δratio）活跃个股集 **显著分离**（样例月 Jaccard 均值与 max 显著低于硬拒线；机制差：全窗两融 ≠ hk 断档补窗）。
3. 信号与 **capacity_adv**（ADV 流动性分位）显著分离（不按 ADV 选股；容量仅硬约束）。
4. 去杠杆冲击期（融资余额普遍回落）叶应主动缩权/抬压舱，而非硬扛巨头名义。

---

## 4. 失效条件

1. 日 Σw 显著偏离 1，或未达 `WEIGHT_END≥2026-10-09` 却 stub 前推 → 拒收。
2. 用未到 `available_at` 的 margin/D1 行 → PIT 违规，自拒。
3. 主轴退化为 hk_hold / ADV 分位 / EP/BM / OCF / 四臂 / 调仓 / moneyflow → 自拒。
4. 任一日个股侧单行业名义 **>0.28+ε**，或单名权重 **>0.04+ε** → 硬顶失败，自拒。
5. `600519.SH` / `002371.SZ` 出现正权重（默认硬排除）→ 自拒。
6. 与十灭+容量+北向活跃个股集样例月 Jaccard **≥0.7 ∧ 近等权** → 换皮，自拒。
7. Book-Smoke @60万∧100万 vs 510300 未进门锁 → any_pass=false，入 WATCH，**不交** Strategy（本单不自跑烟测）。

---

## 5. 相对已灭/WATCH/容量/北向的正交表

| 包 | 其机制要点 | 本叶正交点 |
|---|---|---|
| expand | 截面超额收益排序 | **禁**相对强弱作选股主轴 |
| lowturn / nontextbook | 四臂制度摩擦 | **无**四臂 |
| resid_etf | 残差×ETF 份额流 | **禁**份额流叠乘 |
| etf_core | ETF≈0.70 直接持有 | 主仓**个股**；压舱 510300≈0.15–0.25；**禁** etf_core overlay |
| friction_cost_redesign | 解禁+份额流+半月 | **禁**解禁/份额流 |
| idx_rebal_flow | CSI 调入事件窗 | **禁**调样事件 |
| indcap_momneut_ocf（WATCH） | OCF + 暴露走廊 | **禁** OCF 主轴 |
| d1_val_resid（WATCH） | D1 EP 行业+市值残差 | **禁**估值/EP 主轴；残差对象是 **Δrzye** 非 pe |
| northbound_flow（WATCH） | 主臂 **hk_hold Δratio**；两融仅断档补窗且 tag 仍 northbound | 本叶 **全窗主臂=两融 Δrzye**；**不读 hk_hold**；tag=`…margin_delta…` |
| **capacity_adv**（paper_active） | 主信号=**ADV 流动性分位**；容量硬约束 | **不**按 ADV 分位选股；容量仅单名顶≤4% + 硬排除；信号=杠杆资金流 |

另禁：CB/金主；小盘主线；stub 前推；假跑 V35；D2 moneyflow 满样本主腿；把 paper_active/ACCEPT 当 GP/live。

---

## 6. 本叶结构（写死）

| 项 | 口径 |
|---|---|
| 宇宙 | mid_large PIT ∩ D0 panel；评分池 top≈50；活跃 top **N=25** |
| 持仓 | 月频 `month_end_plus_first_last`；贪婪 topN；行业硬顶 **≤28%**；单名 **≤4%**；等权于个股预算 |
| 硬排除 | `600519.SH`、`002371.SZ` 默认权重=0 |
| 压舱 | 个股预算 ≈0.75–0.85；余 **510300.SH**（≈0.15–0.25）；n=0 → 100% 压舱 |
| 日历 | `WEIGHT_START=2024-01-02` → `WEIGHT_END=2026-10-09`；满窗日更；`stub_forward_fill=false`；`reaches_x2_end=true` |
| 列 | `date,instrument,target_weight`（+ 契约别名 session/instrument_id/weight） |
| peak | **≤1.0GB**；分块读 parquet；禁叠 uvicorn |

---

## 7. 明确不做

- 不开 GP；不交 Strategy；不下单；不密封；不自跑 Book-Smoke
- 不读 hk_hold；不以 ADV 分位选股；不用 D2 moneyflow 作主腿
- 不以估值残差 / OCF / 相对强弱 / 四臂 / 解禁 / 份额流 / 调仓 / ETF-core 作主信号
- 禁小盘主线；禁 CB/金主；禁 stub 前推
- `mechanism_tag` / `who_pays_zh` **禁**「动量」字样及 momentum/value/quality 主线 token

---

## 8. 产物约定

| 项 | 路径 / 口径 |
|---|---|
| 本预注册 | `docs/v2/AI_G1G5_MARGIN_DELTA_WHO_PAYS_PREREG_ZH.md` |
| 脚本 | `research/g1g5_margin_delta_weights.py` |
| 权重 | `output/ai_factory/g1g5_margin_delta_daily_weights_*.parquet` + meta / jsonl / G6 proof |
| RECEIPT | `docs/v2/AI_G1G5_MARGIN_DELTA_WEIGHT_RECEIPT_ZH.md` |
| 可选 verify | `output/alpha/AI_G1G5_MARGIN_DELTA_WEIGHT_VERIFY_STATS_*.json` |

---

## 9. 请父代理 / Alpha

预注册通过并产表后：派 **Alpha 研究级 ACCEPT**（对照本 RECEIPT 自检表）→ 再派 Book-Smoke @60万∧100万 vs 510300。  
本预注册 **不授权** promotion / 密封 / Strategy / GP / 自跑烟测。
