# who_pays 机制预注册 · 个股资金流残差叶（研究级）

| 项 | 值 |
|---|---|
| 日期 | 2026-10-13 ET（America/New_York） |
| 作者 | QuantLab AI（执行器） |
| Leo 指令 | 本聊天明示「开下一正交叶（who_pays→X2）」+ New Bot 交叉确认「需要」→ 叶名 **moneyflow_resid** |
| mechanism_tag | `g1g5_ashare_moneyflow_resid_v1` |
| promotion_approved | **false** |
| strategy_promotion | **false** |
| 状态 | 预注册 → 产完整 X2 → WEIGHT RECEIPT（**不自跑** Book-Smoke；由父代理派 Alpha ACCEPT） |
| 不交 | Strategy；不下单；不开 GP；不密封 |
| 主数据 | `data/v2/moneyflow/moneyflow_stock_daily_pit.parquet`（D2 **ACCEPT_FULL**；`net_mf_amount` + `available_at` PIT） |
| 辅数据 | D1 `daily_basic`：`float_mktcap`（市值残差）+ `turnover_rate`（**仅**作 ADV 分母归一，**不**作 ADV 分位选股）；申万一级 PIT；mid_large PIT |
| **禁** | 应计/两融/容量 ADV 分位选股/OCF/估值残差/北向/idx_rebal/friction/lowturn/indcap_momneut 同构换皮；教科书相对强弱主轴 |

---

## 1. 谁付的钱（一句）

**忽视行业/市值中性后的个股净资金流入强度（相对 ADV）的对手盘**——以 PIT `net_mf_amount` 在约 L=20 自然日窗内累计，除以当日 ADV（`float_mktcap×turnover_rate/100`，仅分母），再经 **申万一级 demean + log 流通市值残差** 后分位；**高残差（相对净流入）优先**。主叙事=**个股资金流残差（moneyflow/ADV）**，明确 **不是** ADV 流动性分位、不是两融 Δrzye、不是北向 hk_hold、不是应计/OCF/估值残差、不是相对强弱/四臂/调仓/ETF-core。

---

## 2. 数学（写死可检验）

| 项 | 口径 |
|---|---|
| 累计净流入 | 对每只股票，在 `available_at.normalize()≤session` 下，取 `available_at` 落在 `[session−L, session]`（L=20 自然日）的 `net_mf_amount` 之和：`S = Σ net_mf_amount` |
| ADV 分母 | 同日 asof D1：`ADV = float_mktcap × turnover_rate / 100`（与 capacity_adv 同公式，**仅作归一**）；ε=1e3 |
| 强度 | `x = S / max(ADV, ε)` |
| 行业 demean | 当日可评分集按申万一级：`x_ind = x − mean_ind(x)` |
| 市值残差 | 对 `x_ind` 对 `log(float_mktcap)` 截面 OLS，取残差 `r`；名过少时退化为仅 demean |
| 选股方向 | **`r` 降序（高残差=相对净流入偏强）**；优先 `r>0` 侧；不足时填入全体可评分 |
| PIT | **仅** `available_at.normalize()≤session`；禁裸用同日 `trade_date` 资金流/D1 |
| 与容量差 | capacity_adv 主轴=**log(ADV) 分位选股**；本叶 ADV **只做分母**，选股对象=**净流入强度残差** |
| 与两融/北向差 | **不读** margin/`rzye`；**不读** `hk_hold`；主臂= D2 moneyflow |

---

## 3. 可检验预测

1. 再平衡后持有窗内，高 `r` 组相对 510300 有正超额倾向（研究级，非保证）。
2. 与 **capacity_adv**（ADV 分位）活跃个股集显著分离：机制差=净流入/ADV 残差 vs log(ADV) 流动性排序。
3. 与 **margin_delta**（Δrzye）、**northbound_flow**（hk_hold）、**accrual_quality**（BS 应计）显著分离。
4. 全市场净流出冲击期叶应缩权抬压舱，而非硬扛巨头名义。

---

## 4. 失效条件

1. 日 Σw 显著偏离 1，或未达 `WEIGHT_END≥2026-10-09` 却 stub 前推 → 拒收。
2. 用未到 `available_at` 的 moneyflow/D1 行 → PIT 违规，自拒。
3. 主轴退化为 ADV 分位选股 / Δrzye / hk_hold / EP/BM / OCF / 应计 / 四臂 / 调仓 / 相对强弱 → 自拒。
4. 任一日个股侧单行业名义 **>0.28+ε**，或单名权重 **>0.04+ε** → 硬顶失败，自拒。
5. `600519.SH` / `002371.SZ` 出现正权重 → 自拒。
6. 与已败十二包+capacity_adv 活跃个股集样例月 Jaccard **≥0.7 ∧ 近等权** → 换皮，自拒。
7. Book-Smoke @60万∧100万 vs 510300 未进门锁 → any_pass=false，入 WATCH，**不交** Strategy（本单不自跑烟测）。

---

## 5. 相对已灭/WATCH/容量的正交表

| 包 | 其机制要点 | 本叶正交点 |
|---|---|---|
| expand | 截面超额收益排序 | **禁**相对强弱作选股主轴 |
| lowturn / nontextbook | 四臂制度摩擦 | **无**四臂 |
| resid_etf | 残差×ETF 份额流 | **禁**份额流叠乘 |
| etf_core | ETF≈0.70 直接持有 | 主仓**个股**；压舱 510300≈0.15–0.25；**禁** etf_core overlay |
| friction_cost_redesign | 解禁+份额流+半月 | **禁**解禁/份额流 |
| idx_rebal_flow | CSI 调入事件窗 | **禁**调样事件 |
| indcap_momneut_ocf（WATCH） | OCF/利润兑现 | **禁** OCF 主轴 |
| d1_val_resid（WATCH） | D1 EP 估值残差 | **禁**估值/EP 主轴；残差对象是 **mf/ADV** 非 pe |
| northbound_flow（WATCH） | hk_hold Δratio | **不读** hk_hold |
| **margin_delta**（已灭） | 全窗两融 Δrzye | **不读** margin；信号=moneyflow |
| **accrual_quality**（已灭） | BS 营运资本应计 | **不读** balancesheet；信号=日频资金流 |
| **capacity_adv**（paper_active） | ADV 流动性分位选股 | ADV **仅分母**；选股=净流入强度残差 |

另禁：CB/金主；小盘主线；stub 前推；假跑 V35；把 D2 ACCEPT / paper_active 当 GP/live。

---

## 6. 本叶结构（写死）

| 项 | 口径 |
|---|---|
| 宇宙 | mid_large PIT ∩ D0 panel；评分池 top≈50；活跃 top **N=25** |
| 持仓 | 月频 `month_end_plus_first_last`；贪婪 topN；行业硬顶 **≤28%**；单名 **≤4%**；等权于个股预算 |
| 硬排除 | `600519.SH`、`002371.SZ` 默认权重=0（按 ADV/成交缺口） |
| 压舱 | 个股预算 ≈0.75–0.85；余 **510300.SH**（≈0.15–0.25）；n=0 → 100% 压舱 |
| 日历 | `WEIGHT_START=2024-01-02` → `WEIGHT_END=2026-10-09`；满窗日更；`stub_forward_fill=false`；`reaches_x2_end=true` |
| 列 | `date,instrument,target_weight`（+ 契约别名 session/instrument_id/weight） |
| peak | **目标 ≤1.5GB**；分块读 moneyflow；禁叠 uvicorn |

---

## 7. 明确不做

- 不开 GP；不交 Strategy；不下单；不密封；不自跑 Book-Smoke
- **不**按 ADV 分位选股；不读 margin/hk_hold/balancesheet/ocf_to_profit
- 不以估值残差 / 相对强弱 / 四臂 / 解禁 / 份额流 / 调仓 / ETF-core 作主信号
- 禁小盘主线；禁 CB/金主；禁 stub 前推
- `mechanism_tag` / `who_pays_zh` **禁**「动量」字样及 momentum/value 主线 token

---

## 8. 产物约定

| 项 | 路径 / 口径 |
|---|---|
| 本预注册 | `docs/v2/AI_G1G5_MONEYFLOW_RESID_WHO_PAYS_PREREG_ZH.md`（可镜像 `output/ai_factory/`） |
| 脚本 | `research/g1g5_moneyflow_resid_weights.py` |
| 权重 | `output/ai_factory/g1g5_moneyflow_resid_daily_weights_*.parquet` + meta / jsonl / G6 proof |
| RECEIPT | `docs/v2/AI_G1G5_MONEYFLOW_RESID_WEIGHT_RECEIPT_ZH.md` |
| verify | `output/alpha/AI_G1G5_MONEYFLOW_RESID_WEIGHT_VERIFY_STATS_*.json` |

---

## 9. 请父代理 / Alpha

预注册通过并产表后：派 **Alpha 研究级 ACCEPT**（对照 RECEIPT 自检表，含 vs capacity/两融/应计/北向/估值/OCF Jaccard + 残差暴露说明）→ 再派 Book-Smoke @60万∧100万 vs 510300。  
本预注册 **不授权** promotion / 密封 / Strategy / GP / 自跑烟测。
