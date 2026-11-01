# who_pays 机制预注册 · 应计质量叶（研究级）

| 项 | 值 |
|---|---|
| 日期 | 2026-10-13 ET（America/New_York） |
| 作者 | QuantLab AI（执行器） |
| Leo 指令 | 本聊天确认卡「开下一正交叶（禁十灭+容量+两融同构）」→ 叶名 **accrual_quality** |
| mechanism_tag | `g1g5_ashare_accrual_quality_v1`（叶名标识；**非**教科书 quality 因子主轴） |
| promotion_approved | **false** |
| strategy_promotion | **false** |
| 状态 | 预注册 → 产完整 X2 → WEIGHT RECEIPT（**不自跑** Book-Smoke；由父代理派 Alpha ACCEPT） |
| 不交 | Strategy；不下单；不开 GP；不密封 |
| 主数据 | `data/v2/financials_pit/balancesheet_pit_tushare.parquet`（`available_at` PIT；合并报表 report_type∈{1}） |
| 辅数据 | D1 `daily_basic` 仅取 `float_mktcap` 作对数流通市值残差协变量；申万一级 PIT；mid_large PIT |
| **禁** | **ocf_to_profit / OCF 主信号**；D2 moneyflow 主腿；ADV 流动性分位选股；两融/北向资金流主臂；EP/BM 估值残差主轴；教科书相对强弱主轴 |

---

## 1. 谁付的钱（一句）

**投资者过度依赖应计盈余、低估低应计/高质量资产负债表盈余的对手盘**——以 PIT 资产负债表构建 **营运资本应计/总资产**（Sloan 风格代理，缺折旧字段则不加 Dep），经 **申万一级 demean + log 流通市值残差** 后分位；**低应计优先**。主叙事=**非 OCF 应计质量（资产负债表）**，明确 **不是** ocf_to_profit、不是 EP/BM 估值残差、不是 ADV 容量、不是两融/北向资金流、不是相对强弱/四臂/调仓/ETF-core。

---

## 2. 应计公式（写死可检验）

资产负债表无独立折旧/摊销累计字段 → **采用营运资本应计代理（不含 Dep）**，公式写死：

对每只股票，在 `available_at.normalize()≤session` 下取最近一期合并 BS（report_type∈{1}）与上一期同口径报告：

```
ΔCA   = total_cur_assets_t − total_cur_assets_{t−1}
ΔCash = money_cap_t − money_cap_{t−1}          # 货币资金代理现金
ΔCL   = total_cur_liab_t − total_cur_liab_{t−1}
ΔSTD  = st_borr_t − st_borr_{t−1}              # 缺失按 0
ΔTP   = taxes_payable_t − taxes_payable_{t−1}  # 缺失按 0

WC_ACC = (ΔCA − ΔCash) − (ΔCL − ΔSTD − ΔTP)
# 本叶不加 Dep（字段不可得；非用 OCF/利润表补）

accrual_ratio = WC_ACC / max(total_assets_t, ε)   # ε=1e6
```

| 项 | 口径 |
|---|---|
| 行业 demean | 当日可评分集按申万一级：`a_ind = accrual_ratio − mean_ind` |
| 市值残差 | 对 `a_ind` 对 `log(float_mktcap)` 截面 OLS，取残差 `r`；名过少时退化为仅 demean |
| 选股方向 | **`r` 升序（低应计=高质量优先）**；优先 `r<0` 侧；不足时填入全体可评分 |
| PIT | **仅** `available_at.normalize()≤session`；禁偷看未到 available_at 的 BS/D1 行 |
| 与 OCF 差 | 本叶分子=**资产负债表营运资本变动**；**不读** `ocf_to_profit`、不读利润表 OCF |

---

## 3. 可检验预测

1. 再平衡后持有窗内，低 `r`（低应计残差）组相对 510300 有正超额倾向（研究级，非保证）。
2. 与 **indcap_momneut_ocf**（OCF 兑现主轴）活跃个股集显著分离：机制差=BS 应计 vs OCF/利润兑现。
3. 与 **d1_val_resid**（EP 估值残差）、**capacity_adv**（ADV 分位）、**northbound_flow**、**margin_delta**（两融 Δrzye）显著分离。
4. 应计普遍抬升/会计制度冲击期，叶应缩权抬压舱，而非硬扛巨头名义。

---

## 4. 失效条件

1. 日 Σw 显著偏离 1，或未达 `WEIGHT_END≥2026-10-09` 却 stub 前推 → 拒收。
2. 用未到 `available_at` 的 BS/D1 行 → PIT 违规，自拒。
3. 主轴退化为 ocf_to_profit / EP/BM / ADV 分位 / 两融/北向 / 相对强弱 / 四臂 / 调仓 / moneyflow → 自拒。
4. 任一日个股侧单行业名义 **>0.28+ε**，或单名权重 **>0.04+ε** → 硬顶失败，自拒。
5. `600519.SH` / `002371.SZ` 出现正权重 → 自拒。
6. 与十灭+容量+两融+OCF/估值/北向活跃个股集样例月 Jaccard **≥0.7 ∧ 近等权** → 换皮，自拒。
7. Book-Smoke @60万∧100万 vs 510300 未进门锁 → any_pass=false，入 WATCH，**不交** Strategy（本单不自跑烟测）。

---

## 5. 相对已灭/WATCH/容量/两融的正交表

| 包 | 其机制要点 | 本叶正交点 |
|---|---|---|
| expand | 截面超额收益排序 | **禁**相对强弱作选股主轴 |
| lowturn / nontextbook | 四臂制度摩擦 | **无**四臂 |
| resid_etf | 残差×ETF 份额流 | **禁**份额流叠乘 |
| etf_core | ETF≈0.70 直接持有 | 主仓**个股**；压舱 510300≈0.15–0.25；**禁** etf_core overlay |
| friction_cost_redesign | 解禁+份额流+半月 | **禁**解禁/份额流 |
| idx_rebal_flow | CSI 调入事件窗 | **禁**调样事件 |
| **margin_delta**（已灭） | 全窗两融 Δrzye | **不读** margin；信号=BS 应计 |
| **indcap_momneut_ocf**（WATCH） | OCF/利润兑现 | **禁** ocf_to_profit；信号=BS 营运资本应计 |
| **d1_val_resid**（WATCH） | D1 EP 行业+市值残差 | **禁**估值/EP 主轴；残差对象是 **accrual_ratio** 非 pe |
| northbound_flow（WATCH） | hk_hold Δratio | **不读** hk_hold |
| **capacity_adv**（paper_active） | ADV 流动性分位 | **不**按 ADV 分位选股；容量仅硬约束 |

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
| peak | **目标 ≤1.5GB**；分块读 BS；禁叠 uvicorn |

---

## 7. 明确不做

- 不开 GP；不交 Strategy；不下单；不密封；不自跑 Book-Smoke
- **不以 ocf_to_profit / OCF 作主信号**；不用 D2 moneyflow 作主腿
- 不以估值残差 / ADV 分位 / 两融 / 北向 / 相对强弱 / 四臂 / 解禁 / 份额流 / 调仓 / ETF-core 作主信号
- 禁小盘主线；禁 CB/金主；禁 stub 前推
- `who_pays_zh` / 机制叙述 **禁「动量」字样**；tag 中 `accrual_quality` 仅为叶名标识

---

## 8. 产物约定

| 项 | 路径 / 口径 |
|---|---|
| 本预注册 | `docs/v2/AI_G1G5_ACCRUAL_QUALITY_WHO_PAYS_PREREG_ZH.md`（可镜像 `output/ai_factory/`） |
| 脚本 | `research/g1g5_accrual_quality_weights.py` |
| 权重 | `output/ai_factory/g1g5_accrual_quality_daily_weights_*.parquet` + meta / jsonl / G6 proof |
| RECEIPT | `docs/v2/AI_G1G5_ACCRUAL_QUALITY_WEIGHT_RECEIPT_ZH.md` |
| verify | `output/alpha/AI_G1G5_ACCRUAL_QUALITY_WEIGHT_VERIFY_STATS_*.json` |

---

## 9. 请父代理 / Alpha

预注册通过并产表后：派 **Alpha 研究级 ACCEPT**（对照 RECEIPT 自检表，含 vs OCF/估值/容量/北向/两融 Jaccard）→ 再派 Book-Smoke @60万∧100万 vs 510300。  
本预注册 **不授权** promotion / 密封 / Strategy / GP / 自跑烟测。
