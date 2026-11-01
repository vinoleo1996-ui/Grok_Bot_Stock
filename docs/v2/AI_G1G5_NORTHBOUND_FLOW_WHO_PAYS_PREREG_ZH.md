# who_pays 机制预注册 · 北向持股变化流（研究级）

| 项 | 值 |
|---|---|
| 日期 | 2026-10-13 ET（America/New_York） |
| 作者 | QuantLab AI（执行器） |
| Leo 指令 | **A、B同时展开调研**（t198u）→ 本线：叶 B · 全新正交机制 |
| mechanism_tag | `g1g5_ashare_northbound_flow_v1` |
| promotion_approved | **false** |
| 状态 | 预注册 → 产完整 X2 →（由 New Bot 派）Beta Book-Smoke |
| 不交 | Strategy；不下单；不开 GP；不密封 |
| 主数据 | `data/v2/northbound/hk_hold_ashare_daily_2018plus.parquet`（ratio/vol + available_at） |
| 辅数据 | `data/v2/northbound/moneyflow_hsgt_daily_2018plus.parquet`（市场北向净流入，仅日志/门控参考） |
| 断档补窗 | `data/v2/margin/margin_detail_daily_2018plus.parquet`（融资余额 Δrzye；**仅** hk_hold asof 断档时） |
| 禁主轴 | OCF（叶A indcap 已败）；估值残差（d1_val_resid 已败） |

---

## 1. 谁付的钱（一句）

**北向配置流**：沪深港通北向对个股的边际增持 / 持股占比上升，由境外配置与被动跟踪资金支付相对 510300 的持有窗；本叶吃 **持股变化 / 流入** 的对手盘，**不是**相对强弱截面排序、**不是**估值残差、**不是** OCF、**不是**调仓事件、**不是**份额流×残差。

**覆盖说明（写死）**：`hk_hold` 在权重窗内密窗约至 2024-08、其后稀疏至 **2025-06-30**，其后无个股持股行。断档再平衡日改用 **两融融资余额 Δrzye** 作同族「外部杠杆/配置资金边际变化」补窗，并在 arm 日志标 `source=margin_fallback`；**不**把两融升格为独立主叶名（tag 仍 `…northbound_flow…`）。

---

## 2. 相对已败九包的正交点

| 已败包 | 其机制要点 | 本叶正交点 |
|---|---|---|
| expand | 截面超额收益排序 | **北向持股变化**主轴；禁相对强弱作唯一 token |
| friction / nontextbook | 四臂月频 | **无**四臂 |
| lowturn | 四臂+季末粘性 | **无**粘性参数 |
| resid_etf | 收益残差×ETF 份额流 | **禁**份额流叠乘；信号=持股/融资余额变化 |
| etf_core | ETF≈0.70 直接持有 | 主仓**个股**；压舱 510300≤0.25 |
| friction_cost_redesign | 解禁+份额流+半月 | **禁**解禁/份额流 |
| idx_rebal_flow | CSI 调入事件窗 | **禁**指数调样事件 |
| indcap_momneut_ocf | OCF/利润 + 行业硬顶+暴露走廊 | **禁 OCF 主轴**；本叶=北向/两融资金流 |
| d1_val_resid | D1 EP 行业+市值残差 | **禁估值残差主轴**；本叶=持股变化流 |

另禁：CB/金主；小盘主线；stub 前推；假跑 V35；教科书相对强弱/价值 token。

---

## 3. 本叶结构（写死可证伪）

| 项 | 口径 |
|---|---|
| 主信号 | 北向 `ratio`（持股占流通比）PIT asof 变化：密窗优先 ≈20 交易日 Δratio；稀疏窗取 asof 下最近两观测点 Δratio；取 **增持侧**（Δratio>0） |
| 断档补窗 | 若最近 hk_hold 观测距 session >45 日 → `Δrzye / max(lag_rzye,ε)`（约 20 日），取融资余额上升侧 |
| PIT | `available_at.normalize()≤session`（hk_hold 约 trade_date 18:00 Asia/Shanghai；与月频收盘后再平衡一致；禁开盘前偷看未到 available_at 行） |
| 宇宙 | Data mid_large PIT ∩ D0 panel；评分池 top≈50；活跃 top **N=20** |
| 持仓 | 增持侧 topN **等权**；**行业硬顶 ≤30%**；不做空 |
| 压舱 | 个股预算 ≈0.80；余 **510300.SH**；n=0 → 100% 510300 |
| 日历 | `WEIGHT_START=2024-01-02` → `WEIGHT_END=2026-10-09`；月频 + 首末日；`reaches_x2_end=true`；`stub_forward_fill=false` |
| 列 | `date,instrument,target_weight`（+ 契约别名） |

---

## 4. 明确不做

- 不开 GP；不交 Strategy；不下单；不密封
- 不以 OCF / 估值残差 / 相对强弱截面 / 调仓事件 / ETF 份额流作主信号
- 禁小盘主线；禁 CB / 金主候选
- 禁 stub 前推；禁假跑 V35
- `mechanism_tag` 禁 momentum / value / quality / 动量 / 价值 主线 token
- `who_pays_zh` 禁「动量」字样（叙事用相对强弱代替）
- 不交 Strategy；Book-Smoke 由 New Bot / Beta 派

---

## 5. 可证伪 / 失败条件

1. 日权重合计显著偏离 1，或日历未达 ≥2026-10-09 却 stub 前推 → 拒收。
2. 用未到 `available_at` 的行 → PIT 违规，自拒。
3. 主轴退化为 OCF / 裸估值 / 相对强弱唯一 token → 自拒。
4. 任一日个股侧单行业名义 **>0.30+ε** → 行业硬顶失败，自拒。
5. ETF 腿日均名义长期 **>0.40** 且活跃个股≈0 → 叶塌，自拒。
6. 与九败包活跃个股集样例月 Jaccard≥0.7 **且** 机制叙事仍像九败 → 换皮，自拒。
7. Book-Smoke @60万∧100万 vs 510300 未进门锁 → any_pass=false，入 WATCH，**不交** Strategy。

---

## 6. 产物约定

| 项 | 路径 / 口径 |
|---|---|
| 权重 | `output/ai_factory/g1g5_northbound_flow_daily_weights_*.parquet` |
| 列 | `date,instrument,target_weight` + 契约别名 |
| 回执 | `docs/v2/AI_G1G5_NORTHBOUND_FLOW_WEIGHT_RECEIPT_ZH.md` |
| peak | **尽量 ≤1.5GB** |
| 脚本 | `research/g1g5_northbound_flow_weights.py` |
| 本预注册 | `docs/v2/AI_G1G5_NORTHBOUND_FLOW_WHO_PAYS_PREREG_ZH.md` |

---

## 7. 请 New Bot / Beta

预注册通过并产表后：Alpha 研究级 ACCEPT → 派 **Book-Smoke @60万∧100万 vs 510300**。  
本预注册 **不授权** promotion / 密封 / Strategy / GP。
