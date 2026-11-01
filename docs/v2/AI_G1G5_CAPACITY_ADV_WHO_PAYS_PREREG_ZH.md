# who_pays 机制预注册 · 容量/ADV 可成交约束叶（研究级）

| 项 | 值 |
|---|---|
| 日期 | 2026-10-13 ET（America/New_York） |
| 作者 | QuantLab AI（执行器 · 叶 A） |
| Leo 指令 | **A、B同时展开调研**（t198u）→ 本线：容量敏感新叶 |
| mechanism_tag | `g1g5_ashare_capacity_adv_v1` |
| promotion_approved | **false** |
| 状态 | 预注册 → 产完整 X2 → 回执（不自跑 Book-Smoke） |
| 不交 | Strategy；不下单；不开 GP；不密封 |
| 触发 | d1_val_resid 百万元端掉约 2pp；`600519`/`002371` 类巨头 target∉actual 成交/冲击缺口 |
| 数据源 | D1 `daily_basic_full_tushare`（`turnover_rate`×`float_mktcap`→ADV 代理，asof `available_at`）+ `sw_l1_pit` + mid_large PIT |

---

## 1. 谁付的钱（一句）

在**可成交容量约束**下，流动性溢价/冲击成本被错误定价的对手盘支付本叶相对 510300 的持有窗——本叶显式优化 **60万与100万同向可成交**，压单名 ADV 参与率与名义冲击；主叙事是**容量/冲击可成交**，**不是**估值残差、**不是** OCF 兑现、**不是**截面相对强弱、**不是**四臂摩擦/解禁/份额流/调仓/ETF-core overlay 换皮。

---

## 2. 相对已败九包的正交点

| 已败包 | 其机制要点 | 本叶正交点 |
|---|---|---|
| expand | 截面超额收益排序 | **禁**相对强弱作选股主轴；**不**加载动量/超额收益排序 |
| lowturn / nontextbook | 四臂制度摩擦 | **无**四臂；信号仅 ADV/换手流动性 |
| resid_etf | 收益残差 × ETF 份额流 | **禁**残差×流；无份额流 |
| etf_core_sleeve | ETF 直接持有 ≈0.70 | 主仓**个股**；压舱宽基 ≤≈0.25；**禁** etf_core overlay |
| friction_cost_redesign | 解禁+份额流主信号 + 容量加权 | 主信号=**ADV 流动性分位本身**；容量为**硬约束**（参与率/单名顶），**无**解禁/份额流主臂 |
| idx_rebal_flow | CSI 调入事件窗 | **禁**调样事件 |
| indcap_momneut_ocf | OCF/利润兑现 + 动量暴露走廊 | **禁** OCF；**禁**动量主轴/暴露倾斜作选股 |
| d1_val_resid | D1 EP 行业+市值残差 | **禁**估值残差/裸 EP/BM；本叶不读 pe_ttm 作排序 |

另禁：CB/金主；小盘主线；stub 前推；假跑 V35；把 ACCEPT 当 GP/promotion。

---

## 3. 本叶结构（写死可证伪）

| 项 | 口径 |
|---|---|
| ADV 代理 | `adv_yuan ≈ float_mktcap × turnover_rate / 100`（D1 asof `available_at.normalize()≤session`） |
| 主信号 | 截面 **log(ADV) 经申万一级行业 demean** 后的流动性分位（高可成交优先）；中大盘液态宇宙 |
| 硬排除 | 已知成交缺口超大名义：`600519.SH`、`002371.SZ`（Book-Smoke 记 target∉actual）；另禁堆同类超大名义（单名顶+参与率双锁） |
| 容量硬约束 | 研究绑定 AUM=`1_000_000`：单名名义 `w×AUM ≤ k×ADV`（默认 **k=2%**）；且 **单名权重 ≤4%**；不满足则跳过/缩权，余量→压舱 |
| 行业硬顶 | 申万一级单行业目标权重 **≤28%** |
| 持仓 | 月频 + 首末日；贪婪 top **N=25**（约束后）；容量比例加权（∝ clip(ADV)）后再硬顶；个股预算 ≈0.80–0.85；余 **510300.SH** |
| 宇宙 | Data mid_large PIT ∩ D0 panel；评分池 top≈50 |
| 日历 | `WEIGHT_START=2024-01-02` → `WEIGHT_END≥2026-10-09`；`reaches_x2_end=true`；`stub_forward_fill=false` |
| 列 | `date,instrument,target_weight`（+ 契约别名） |

---

## 4. 明确不做

- 不开 GP；不交 Strategy；不下单；不密封
- 不叠九败同构（含 d1_val_resid / indcap_momneut_ocf / friction_cost 换皮）
- 不以估值残差 / OCF / 动量 / 解禁 / 份额流 / 调仓作主选股臂
- 不叠 etf_core 0.70 overlay；不持有行业 ETF 作主仓
- 禁 CB/金主；禁小盘主线；禁 stub 前推
- `mechanism_tag` / `who_pays_zh` **禁** momentum / 动量 / value / quality 主线 token

---

## 5. 可证伪 / 失败条件

1. 日权重合计显著偏离 1，或日历未达 ≥2026-10-09 却 stub 前推 → 拒收。
2. 主轴退化为 EP/BM/OCF/动量/四臂/调仓/份额流 → 自拒。
3. 任一日个股侧单行业名义 **>0.28+ε**，或单名权重 **>0.04+ε** → 硬顶失败，自拒。
4. 持仓仍含 `600519.SH` / `002371.SZ` 正权重 → 自拒。
5. ETF 腿（含压舱）日均名义长期 **>0.40** 且活跃个股≈0 → 叶塌，自拒。
6. 与九败活跃个股集样例月 Jaccard≥0.7 **且** 叙事仍像九败之一 → 换皮，自拒。
7. Book-Smoke @60万∧100万 vs 510300 未进门锁 → any_pass=false，入 WATCH，**不交** Strategy（本单不自跑烟测）。

---

## 6. 产物约定

| 项 | 路径 / 口径 |
|---|---|
| 权重 | `output/ai_factory/g1g5_capacity_adv_daily_weights_*.parquet` |
| 脚本 | `research/g1g5_capacity_adv_weights.py` |
| 回执 | `docs/v2/AI_G1G5_CAPACITY_ADV_WEIGHT_RECEIPT_ZH.md` |
| peak | **尽量 ≤1.5GB**（禁叠 uvicorn；不预载全窗收盘价矩阵） |
| 本预注册 | `docs/v2/AI_G1G5_CAPACITY_ADV_WHO_PAYS_PREREG_ZH.md` |

---

## 7. 权限边界

本预注册 **不授权** promotion / 密封 / Strategy / GP。  
`promotion_approved=false`。Alpha D1 ACCEPT_FULL 仅可作 daily_basic asof 研究，**不得**当晋级授权。
