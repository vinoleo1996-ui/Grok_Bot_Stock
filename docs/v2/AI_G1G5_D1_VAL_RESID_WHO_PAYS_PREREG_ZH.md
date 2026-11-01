# who_pays 机制预注册 · D1 估值残差 asof（研究级）

| 项 | 值 |
|---|---|
| 日期 | 2026-10-12 ET（America/New_York） |
| 作者 | QuantLab AI（执行器） |
| Leo 指令 | **并行展开**（t192u）→ 本线：叶 B · D1 估值残差 |
| mechanism_tag | `g1g5_ashare_d1_val_resid_v1` |
| promotion_approved | **false** |
| 状态 | 预注册 → 产完整 X2 →（由 New Bot 派）Beta Book-Smoke |
| 不交 | Strategy；不下单；不开 GP；不密封 |
| 数据源 | D1 `data/v2/valuation/daily_basic_full_tushare.parquet`（ACCEPT_FULL，仅研究 asof）+ `data/v2/sw_l1_pit/` + mid_large PIT |
| D1 门锁 | ACCEPT_FULL ≠ GP/promotion 授权 |

---

## 1. 谁付的钱（一句）

**错误定价纠偏**：在申万一级行业与流通市值中性后，低估（或高估反向）名相对公允的收敛由边际资金支付；本叶吃 **D1 asof 残差估值修正**，**不是**裸 EP/BM/PE 截面排序，**不是**截面相对强弱主轴，**不是**调仓/摩擦/份额流，**不是**残差×份额流同构。

---

## 2. 相对已败七包的正交点

| 已败包 | 其机制要点 | 本叶正交点 |
|---|---|---|
| expand | 截面超额收益排序；月频 EW topN | **估值残差**主轴；并对 20d 相对宽基超额做正交化压低暴露；**禁**相对强弱作唯一主 token |
| friction/nontextbook | 四臂月频（ETF份额/解禁/T+1/涨跌停） | **无**四臂；信号仅 D1 估值残差 |
| lowturn | 同四臂 + 季末粘性 enter12/exit28 | **无**季末粘性参数；无四臂 |
| resid_etf | 收益残差 × ETF 份额流 + 交互 | **禁**份额流主轴叠乘；本叶残差对象是 **估值倍数**，不是收益残差×流 |
| etf_core | ETF 直接持有 ≈0.70 | 主仓 **个股**；压舱宽基 510300 ≤0.25；**禁** etf_core overlay |
| friction_cost_redesign | 解禁+份额流→成分股 + 半月 + 容量加权 | **禁**解禁/份额流；等权 topN + 行业硬顶 |
| idx_rebal_flow | CSI 调入事件窗 | **禁**指数调样事件；全窗截面残差 |

另禁：CB/金主；小盘主线；stub 前推；假跑 V35；教科书裸 EP/BM/PE 排序作唯一主 token（须行业+市值中性残差或正交化）。

---

## 3. 本叶结构（写死可证伪）

| 项 | 口径 |
|---|---|
| 信号 | D1 `pe_ttm`→EP=1/pe_ttm（pe_ttm>0）；截面内 **SW L1 行业 demean** → **流通市值三分位 demean** → 再对 20d 相对 510300 超额做简单正交（压低暴露） |
| PIT | asof 用 `available_at`（非裸 trade_date）；同日 basic 不作开盘前偷看；`available_at.normalize()≤session`（与同 session 收盘再平衡一致） |
| 宇宙 | Data mid_large PIT ∩ D0 panel（中大盘液态）；评分池 top≈80，活跃 top **N=20** |
| 持仓 | 低估侧（残差 EP 高）topN **等权**；**行业硬顶 ≤30%**（超则跳过次优）；**不做空** |
| 压舱 | 个股预算 ≈0.80；余 **510300.SH**；n=0 → 100% 510300 |
| 日历 | `WEIGHT_START=2024-01-02` → `WEIGHT_END≥2026-10-09`；月频再平衡 + 首末日；`reaches_x2_end=true`；`stub_forward_fill=false` |
| 列 | `date,instrument,target_weight`（+ 契约别名） |

---

## 4. 明确不做

- 不开 GP；不把 D1 ACCEPT 当 promotion/GP 授权
- 不叠 etf_core overlay；不持有行业 ETF 作 0.70 主仓
- 不投 resid×份额同构；不以 UNLOCK/SEAT/调仓流作本叶主信号
- 禁小盘主线；禁 CB / 金主候选
- 禁 stub 前推；禁假跑 V35
- `mechanism_tag` **禁** momentum / value / quality / 动量 / 价值 主线 token（本 tag=`…d1_val_resid…`）
- `who_pays_zh` **禁**「动量」字样；叙事用错误定价纠偏 / 残差估值修正
- 不交 Strategy；不下单；不密封

---

## 5. 可证伪 / 失败条件

1. 日权重合计显著偏离 1，或日历未达 ≥2026-10-09 却 stub 前推 → 拒收。
2. 用未到 `available_at` 的行 / 开盘前偷看同日 basic → PIT 违规，自拒。
3. 主轴退化为裸 EP/BM 排序（无行业+市值中性）或相对强弱唯一主 token → 自拒。
4. 任一日个股侧单行业名义 **>0.30+ε** → 行业硬顶失败，自拒。
5. ETF 腿（含压舱）日均名义长期 **>0.40** 且活跃个股≈0 → 叶塌，自拒。
6. 与七败包活跃个股集样例月 Jaccard≥0.7 **且** 机制叙事仍像动量/四臂/份额流/调仓 → 换皮，自拒。
7. Book-Smoke @60万∧100万 vs 510300 未进门锁 → any_pass=false，入 WATCH，**不交** Strategy。

---

## 6. 产物约定

| 项 | 路径 / 口径 |
|---|---|
| 权重 | `output/ai_factory/g1g5_d1_val_resid_daily_weights_*.parquet` |
| 列 | `date,instrument,target_weight` + 契约别名 |
| 回执 | `docs/v2/AI_G1G5_D1_VAL_RESID_WEIGHT_RECEIPT_ZH.md` |
| peak | ≤1.0–1.5GB（尽量；可分批/降并行） |
| 脚本 | `research/g1g5_d1_val_resid_weights.py` |
| 本预注册 | `docs/v2/AI_G1G5_D1_VAL_RESID_WHO_PAYS_PREREG_ZH.md` |

---

## 7. 请 New Bot / Beta

预注册通过并产表后：Alpha 研究级 ACCEPT → 派 **Book-Smoke @60万∧100万 vs 510300**。  
本预注册 **不授权** promotion / 密封 / Strategy / GP。
