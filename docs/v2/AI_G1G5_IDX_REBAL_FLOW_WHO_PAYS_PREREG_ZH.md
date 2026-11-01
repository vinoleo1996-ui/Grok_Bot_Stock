# who_pays 机制预注册 · 指数调仓迁移流（研究级）

| 项 | 值 |
|---|---|
| 日期 | 2026-10-12 ET（America/New_York） |
| 作者 | QuantLab AI（执行器） |
| Leo 指令 | **全部并行做** → 本线：非动量新叶（t186u） |
| mechanism_tag | `g1g5_ashare_idx_rebal_flow_v1` |
| promotion_approved | **false** |
| 状态 | 预注册 → 产完整 X2 →（由 New Bot 派）Beta Book-Smoke |
| 不交 | Strategy；不下单；不开 GP；不密封 |
| 数据源 | `data/v2/index_members/index_member_events.parquet`（PIT `available_at`）+ `csi_review_calendar.parquet` |
| 接线前身 | V31 STOCK-INDEX-REBAL（`docs/v2/AI_STOCK_ARM_PROPOSAL_V31_INDEX_REBAL_ZH.md`） |

---

## 1. 谁付的钱（一句）

**CSI300/CSI500 成分调入公告后、生效日前后，被动指数跟踪与量化对标的强制再平衡买卖需求**支付本叶相对 510300 的持有窗；本叶做多**公告已到、尚未/刚过生效**的调入个股篮，吃被动流冲击的对手盘——**不是**截面动量排序，**不是**估值/quality 主轴，**不是**解禁/席位/份额流同构，**不是** ETF-core 0.70 直接持有，**不是** friction 四臂换皮。

---

## 2. 相对已败六包的正交点

| 已败包 | 其机制要点 | 本叶正交点 |
|---|---|---|
| expand | 截面动量；月频等权 mid_large top50 | **事件驱动**调入流；**无**动量 token；宇宙为调入事件名∩mid_large（非 top50 扁平动量篮） |
| friction/nontextbook | 四臂月频（含 T+1/涨跌停） | **无**四臂；信号仅指数调样 in |
| lowturn | 同四臂 + 季末粘性 | **无**季末+进12/出28；cadence=调样审查窗 |
| resid_etf | 残差×ETF 份额 | **禁**残差主轴；**禁**份额流主线 |
| etf_core | ETF 直接持有 ≈0.70 | 主仓为**调入个股**；压舱宽基 ≤0.30（名义）；**禁** etf_core overlay |
| friction_cost_redesign | 解禁+ETF 份额流→成分股 + 半月 | **禁**再叠解禁/份额流；本叶唯一主信号=指数调入事件 |

另禁：resid×份额同构；SEAT-SPLIT/UNLOCK 磨同叶作唯一主线；小盘；CB/金主；stub；假跑 V35；教科书 mom/value/quality 主线 token。

---

## 3. 本叶结构（写死可证伪）

| 项 | 口径 |
|---|---|
| 信号 | `event=in` ∧ `index_code∈{000300.SH,000905.SH}`；按表内 `available_at` 入日；**排除** 000852.SH |
| PIT | `available_at.normalize()` → **下一开盘**可交易；持有窗锚 `effective_date`；**K=10** 交易日（写死）；null `available_at` 弃用；**不可前移** |
| 宇宙 | 调入事件涉及名 ∩ mid_large PIT ∩ D0 panel（中大盘 by construction）；**诚实说明**：expand 式 mid_large **top50** 与 X2 窗调入重叠≈0，硬套会塌成纯压舱，故本叶不用 top50 扁平篮 |
| 持仓 | 窗内活跃调入 top **N=25** 等权；排序：**CSI300 优先** → 同级按 mid_large `float_mktcap_basis` asof（容量，非收益）→ `available_at`；**不做空**调出 |
| 权重 | `w_stock=min(0.70, 0.028*n)`；余 **510300.SH**；n=0 → 100% 510300 |
| 日历 | `WEIGHT_START=2024-01-02` → `WEIGHT_END≥2026-10-09`；`reaches_x2_end=true`；`stub_forward_fill=false` |
| 覆盖 | X2 窗内约 5 次审查（2024-06/12、2025-06/12、2026-06）；窗间无活跃调入时为纯压舱（诚实，非 stub） |

---

## 4. 明确不做

- 不开 GP（禁 v27/v29 同构）
- 不叠 etf_core overlay；不持有行业 ETF 作 0.70 主仓
- 不投 resid×份额同构；不以 UNLOCK/SEAT 作本叶主信号
- 禁小盘主线；禁 CB / 金主候选
- 禁 stub 前推；禁假跑 V35；禁伪造 X1 早年调样
- `mechanism_tag` / `who_pays_zh` **禁**「动量 / momentum / 价值 / value / quality」主线 token
- 不交 Strategy；不下单；不密封

---

## 5. 可证伪 / 失败条件

1. 日权重合计显著偏离 1，或日历未达 ≥2026-10-09 却 stub 前推 → 拒收。
2. 用未到 `available_at` 的行 / 前移公告 → PIT 违规，自拒。
3. 持仓主轴变为截面动量排序或 friction 四臂换皮 → 自拒。
4. ETF 腿（含压舱）在**有活跃调入窗**内日均名义长期 **>0.40** 且活跃个股≈0 → 叶塌，自拒。
5. 与六败包活跃个股集样例月 Jaccard≥0.7 **且** 机制叙事仍像动量/四臂/解禁流 → 换皮，自拒。
6. Book-Smoke @60万∧100万 vs 510300 未进门锁 → any_pass=false，入 WATCH，**不交** Strategy。

---

## 6. 产物约定

| 项 | 路径 / 口径 |
|---|---|
| 权重 | `output/ai_factory/g1g5_idx_rebal_flow_daily_weights_*.parquet` |
| 列 | `date,instrument,target_weight` + 契约别名 |
| 回执 | `docs/v2/AI_G1G5_IDX_REBAL_FLOW_WEIGHT_RECEIPT_ZH.md` |
| peak | ≤1.0–1.5GB（尽量） |
| 脚本 | `research/g1g5_idx_rebal_flow_weights.py` |
| 本预注册 | `docs/v2/AI_G1G5_IDX_REBAL_FLOW_WHO_PAYS_PREREG_ZH.md` |

---

## 7. 请 New Bot / Beta

预注册通过并产表后：Alpha 研究级 ACCEPT → 派 **Book-Smoke @60万∧100万 vs 510300**。  
本预注册 **不授权** promotion / 密封 / Strategy / GP。
