# who_pays 机制预注册 · 行业硬顶 + 动量暴露中性 · OCF 兑现（研究级）

| 项 | 值 |
|---|---|
| 日期 | 2026-10-13 ET（America/New_York） |
| 作者 | QuantLab AI（执行器 · 叶 A） |
| Leo 指令 | **并行展开** → 本线：行业硬顶 + 动量暴露中性非动量叶 |
| mechanism_tag | `g1g5_ashare_indcap_momneut_ocf_v1` |
| promotion_approved | **false** |
| 状态 | 预注册 → 产完整 X2 → 回执（不自跑 Book-Smoke） |
| 不交 | Strategy；不下单；不开 GP；不密封 |
| 暴露约束来源 | `docs/v2/AI_G1G5_EXPAND_EXPOSURE_DEEPENING_ZH.md` §5 |
| 主信号数据 | `data/v2/financials_pit/ocf_to_profit_pit_daily_tushare.parquet`（PIT `e_available_at` / `trade_date`） |

---

## 1. 谁付的钱（一句）

**经营现金流相对净利润的兑现落差（OCF/利润 PIT）在中大盘液态宇宙内被错误定价的对手盘**，支付本叶相对 510300 的持有窗；持仓另受**申万一级单行业硬顶**与**相对 510300 的 20d 超额动量暴露走廊中性化**约束——**不是**截面动量排序主轴，**不是**教科书 EP/BM 估值主轴，**不是**残差×份额流 / ETF-core overlay / 四臂摩擦 / 指数调仓流换皮。

---

## 2. 相对已败七包的正交点

| 已败包 | 其机制要点 | 本叶正交点 |
|---|---|---|
| expand | 截面动量；月频等权 mid_large top50 | **禁** excess_vs_510300 作选股排序；动量仅作暴露诊断→超阈降权/中性化 |
| friction/nontextbook | 四臂月频（T+1/涨跌停/解禁等） | **无**四臂；信号仅 OCF/利润兑现 |
| lowturn | 同四臂 + 季末粘性 | **无**季末带宽/进出规则 |
| resid_etf | 行业残差 × ETF 份额流 | **禁**残差主轴；**禁**份额流主线 |
| etf_core | ETF 直接持有 ≈0.70 | 主仓为**个股**；压舱宽基仅覆盖缺口；**禁** etf_core overlay |
| friction_cost_redesign | 解禁+份额流→成分股 | **禁**解禁/份额流 |
| idx_rebal_flow | CSI 调入事件流 | **禁**调样事件主轴；日历=月末再平衡，非审查窗 |

另禁：CB/金主；小盘主线；stub 前推；把 ACCEPT 当 GP/promotion。

---

## 3. 本叶结构（写死可证伪）

| 项 | 口径 |
|---|---|
| 主信号 | `ocf_to_profit`（PIT 日表 asof `trade_date≤session`）；排除 `np_negative` / `denom_small`；极值 winsor 后截面排序（高兑现优先） |
| 行业硬顶 | 申万一级单行业目标权重 **≤28%**；日度 HHI 监控目标 **≤0.18**（选股贪婪跳过超顶名） |
| 动量暴露中性 | 持仓权重平均（个股 20d − 510300 20d）目标 **≈0±1.5pp**；超阈则在篮内对高/低超额动量名做有界倾斜，**不**改选股主轴为动量 |
| 市值带 | 再平衡日 mid_large 包内 float_mktcap 分位 **∈[0.35, 0.75]** |
| 宇宙 | Data `mid_large_members_pit` @anchor ∩ D0 panel → top50；再平衡日 PIT 成员过滤 |
| 持仓 | 月频 + 首日；贪婪 top **N=20**（行业顶约束后）；等权后做动量走廊微调；覆盖不足时余量→**510300.SH** |
| 日历 | `WEIGHT_START=2024-01-02` → `WEIGHT_END≥2026-10-09`；`reaches_x2_end=true`；`stub_forward_fill=false` |
| 列契约 | `date,instrument,target_weight` + 别名 |

---

## 4. 明确不做

- 不开 GP；不交 Strategy；不下单；不密封
- 不叠七败同构（expand/lowturn/friction/resid_etf/etf_core/friction_cost/idx_rebal）
- 不以截面动量 / EP/BM / 残差×份额 / 调仓事件作主选股臂
- 禁 CB/金主；禁小盘主线；禁 stub 前推
- `mechanism_tag` 用 `ocf` 指名主信号，**避免**英文 textbook token `quality`/`momentum`/`value` 作 tag 主词

---

## 5. 可证伪 / 失败条件

1. 日权重合计显著偏离 1，或日历未达 ≥2026-10-09 却 stub 前推 → 拒收。
2. 选股主轴退化为 excess_vs_510300 排序或四臂/调仓/份额流 → 自拒。
3. 单行业权重长期系统性 >30% 或日均 HHI >0.18 且无纠偏 → 暴露约束失效，自拒。
4. 相对七败活跃个股集样例月 Jaccard≥0.7 **且** 叙事仍像动量/四臂/调仓流 → 换皮，自拒。
5. Book-Smoke @60万∧100万 vs 510300 未进门锁 → any_pass=false，入 WATCH，**不交** Strategy（本单不自跑烟测）。

---

## 6. 产物约定

| 项 | 路径 / 口径 |
|---|---|
| 权重 | `output/ai_factory/g1g5_indcap_momneut_ocf_daily_weights_*.parquet` |
| 脚本 | `research/g1g5_indcap_momneut_ocf_weights.py` |
| 回执 | `docs/v2/AI_G1G5_INDCAP_MOMNEUT_OCF_WEIGHT_RECEIPT_ZH.md` |
| peak | ≤1.0–1.5GB（尽量） |
| 本预注册 | `docs/v2/AI_G1G5_INDCAP_MOMNEUT_OCF_WHO_PAYS_PREREG_ZH.md` |

---

## 7. 权限边界

本预注册 **不授权** promotion / 密封 / Strategy / GP。  
`promotion_approved=false`。Alpha D1 ACCEPT_FULL 仅可作估值 asof 研究，**不得**当晋级授权。
