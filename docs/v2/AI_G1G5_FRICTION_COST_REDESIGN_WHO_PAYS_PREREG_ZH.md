# who_pays 机制预注册 · 摩擦降成本再设计（研究级）

| 项 | 值 |
|---|---|
| 日期 | 2026-10-12 ET（America/New_York） |
| 作者 | QuantLab AI |
| Leo 确认卡 | **摩擦降成本再设计**（t180s789） |
| mechanism_tag | `g1g5_ashare_friction_cost_redesign_v1` |
| promotion_approved | **false** |
| 状态 | 预注册 → 产完整 X2 →（由 New Bot 派）Beta Book-Smoke |
| 不交 | Strategy；不下单；不开 GP；不密封 |

---

## 1. 谁付的钱（一句）

**解禁公告窗内的供给冲击残差对手盘**与**行业 ETF 创设/赎回份额流转映射到成分股的配置对手盘**支付本叶相对 510300 的持有窗；执行路径用 D1 换手/流通市值 asof 做容量匹配与单票硬顶压冲击成本——**不是**再叠季末+进12/出28 的同四臂降频，**不是** T+1/涨跌停高换手臂主线，**不是** ETF-core 0.70/0.30 直接持有结构，**不是**残差×份额流同构，**不是**教科书相对强弱/估值/quality 排序。

---

## 2. 相对已败五包的正交点

| 已败包 | 其机制要点 | 本叶正交点 |
|---|---|---|
| expand | 截面动量对照；月频等权 | **禁**动量主线 token；信号为解禁+份额流→成分股 |
| friction/nontextbook | 四臂月频 top20 等权（含 T+1/涨跌停） | **砍掉/零权** T+1 与涨跌停带宽；仅保留慢制度两臂 |
| lowturn | 同四臂 + **季末 + 进12/出28** 粘性 | **不同 cadence**：半月再平衡；**无** enter12/exit28；权重为流通市值×流动性容量缩放 + **L≤1.5%** 硬顶，非等权 top20 |
| resid_etf | 残差收益 × ETF 份额交互 | **禁** trailing 残差主轴；份额流只映射成分股得分 |
| etf_core | **ETF 直接持有 ≈0.70** + 袖套 ≈0.30 | 主仓为**个股**；压舱宽基 ETF **≤0.20**（仅 510300）；**禁**再叠 etf_core overlay / 0.70·0.30 |

---

## 3. 本叶结构（可微调，已写死可证伪口径）

| 腿 | 名义 | 定义 |
|---|---:|---|
| **慢制度个股袖套** | ≈0.85 | 解禁残差供给冲击（负向回避）+ 行业 ETF 份额流→成分股；候选按综合分取 **top≤20**（打分决定入选，非全宇宙扁平）；权重 ∝ `float_mktcap`×流动性缩放（D1 `turnover_rate` asof）；单票 **L≤5% 等价硬顶**（说明：严格 1.5%∩mid_large top50 会使几乎全员触顶→打分失效；5% 对齐原 friction EW top20 单票量级，但本叶为流通市值×换手×得分倾斜，非等权）；溢出并入压舱 |
| **宽基压舱** | ≈0.15 | 仅 `510300.SH`；**不得**扩成行业 ETF-core 0.70 结构 |
| **再平衡** | — | **半月**（510300 日历约每 10 个交易日 + 首日）；**禁止**复刻 lowturn「季末+进12/出28」 |

臂权名义：`etf_flow≈0.55`，`unlock≈0.45`，`t1=0`，`limit=0`（coverage_gap 时在存活臂内重归一）。

宇宙：中大盘 mid_large top50（expand 同接口）。日历：`WEIGHT_START=2024-01-02` → `WEIGHT_END≥2026-10-09`；`reaches_x2_end=true`；`stub_forward_fill=false`。

---

## 4. 明确不做

- 不开 GP（禁 v27/v29 同构）
- 不叠 etf_core overlay；不持有行业 ETF 作 0.70 主仓
- 不投 resid×份额同构；不磨 SEAT-SPLIT / UNLOCK 同叶作主线
- 禁小盘主线；禁 CB / 金主候选
- 禁 stub 前推；禁假跑 V35
- `mechanism_tag` / `who_pays_zh` **禁**「动量 / momentum / 价值 / value / quality」主线 token
- D1 估值 ACCEPT_FULL **仅**研究 asof（换手/流通市值）；**不是**晋级/GP/promotion 授权
- 不交 Strategy；不下单；不密封

---

## 5. 可证伪 / 失败条件

1. 日权重合计显著偏离 1，或日历未达 ≥2026-10-09 却 stub 前推 → 拒收。
2. 再平衡参数复刻 lowturn（季末 + enter=12 / exit=28）→ 非本叶，自拒。
3. 名义上仍给 T+1/涨跌停主权重（>5% 有效臂权）→ 未完成「砍高换手臂」，自拒。
4. ETF 腿（含压舱）日均名义 **>0.25** 或出现行业 ETF 合计接近 0.70 → 滑向 etf_core，自拒。
5. 与 lowturn / friction 活跃个股集样例月 Jaccard≥0.7 **且** 权重形态仍为等权 top20 → 换皮，自拒。
6. Book-Smoke @60万∧100万 vs 510300 未进门锁 → any_pass=false，入 WATCH，**不交** Strategy。

---

## 6. 产物约定

| 项 | 路径 / 口径 |
|---|---|
| 权重 | `output/ai_factory/g1g5_friction_cost_redesign_daily_weights_*.parquet` |
| 列 | `date,instrument,target_weight` + 契约别名 |
| 回执 | `docs/v2/AI_G1G5_FRICTION_COST_REDESIGN_WEIGHT_RECEIPT_ZH.md` |
| peak | ≤1.0–1.5GB（硬顶尽量 ≤1.5GB） |
| 脚本 | `research/g1g5_friction_cost_redesign_weights.py` |
| 本预注册 | `docs/v2/AI_G1G5_FRICTION_COST_REDESIGN_WHO_PAYS_PREREG_ZH.md` |

---

## 7. 请 New Bot / Beta

预注册通过并产表后：Alpha 研究级 ACCEPT → 派 **Book-Smoke @60万∧100万 vs 510300**。  
本预注册 **不授权** promotion / 密封 / Strategy / GP。
