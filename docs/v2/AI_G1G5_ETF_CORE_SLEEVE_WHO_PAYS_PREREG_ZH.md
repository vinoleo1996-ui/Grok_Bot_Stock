# who_pays 机制预注册 · ETF-core + 个股袖套混合（研究级）

| 项 | 值 |
|---|---|
| 日期 | 2026-10-12 ET（America/New_York） |
| 作者 | QuantLab AI |
| Leo 确认卡 | **ETF-core+个股袖套混合**（t176s767） |
| mechanism_tag | `g1g5_ashare_etf_core_sleeve_v1` |
| promotion_approved | **false** |
| 状态 | 预注册 → 产完整 X2 → 派 Beta Book-Smoke |
| 不交 | Strategy；不下单；不开 GP；不密封 |

---

## 1. 谁付的钱（一句）

**ETF 创设/赎回份额流对手盘**支付行业 ETF-core 相对宽基（510300）的配置差；**流入行业内的流动性承接/冲击吸收对手盘**支付有限个股袖套——不是教科书相对强弱排序，不是估值/PE·PB 主线，不是残差×份额流 100% 股票满仓，不是解禁/T+1/涨跌停四臂摩擦包复刻。

---

## 2. 组合结构（相对已败四包的正交点）

| 腿 | 名义仓位 | 持仓形态 | 信号 |
|---|---:|---|---|
| **ETF-core** | **0.70** | **直接持有**液态行业 ETF + 510300 压舱 | 申万一级行业 ETF 份额流 PIT（trailing 可见 `flow_est_wan_yuan`）→ 顶 K 行业 → `sw_l1_etf_map_pit_daily` 液态代表 ETF |
| **个股袖套** | **0.30** | 中大盘 top 宇宙内 **有限名**等权 | 流入行业成分 ∩ D1 换手 asof（流动性承接）；**禁止** PE/PB/EP 估值排序作主轴；**禁止** trailing 收益残差主轴 |

已败四包均为 **100% 股票满仓**（expand / nontextbook / lowturn / resid_etf）。本叶主仓为 **ETF 本身**，个股仅为袖套 → 结构正交，非换皮。

---

## 3. 明确不做

- 不开 GP（v28 GATE_OK=0；禁 v29 同构）
- 不投残差×份额流同构四臂 / resid_etf 复刻
- 不磨 SEAT-SPLIT / UNLOCK 同叶作主线
- 禁小盘主线；禁 CB / 金主候选
- 禁 stub 前推；禁假跑 V35（回购/预告/质押 X1 未就绪）
- `mechanism_tag` / `who_pays_zh` **禁**「动量 / momentum / 价值 / value / quality」主线 token
- D1 估值 ACCEPT_FULL **仅**研究 asof（换手等）；**不是**晋级/GP/promotion 授权

---

## 4. 可证伪 / 失败条件

1. 日权重合计显著偏离 1，或日历未达 ≥2026-10-09 却 stub 前推 → 拒收。
2. 持仓仍近似 100% 股票（ETF-core 名义权重失效）→ 结构失败，非本叶。
3. 与 resid_etf / friction 活跃集长期 Jaccard≥0.7 且工具几乎全为个股 → 换皮，自拒。
4. Book-Smoke @60万∧100万 vs 510300 未进门锁（12–18% / MDD≥−28%）→ any_pass=false，入 WATCH，不交 Strategy。

---

## 5. 产物约定

| 项 | 路径 / 口径 |
|---|---|
| 权重 | `output/ai_factory/g1g5_etf_core_sleeve_daily_weights_*.parquet` |
| 列 | `date,instrument,target_weight` + 契约别名 |
| 回执 | `docs/v2/AI_G1G5_ETF_CORE_SLEEVE_WEIGHT_RECEIPT_ZH.md` |
| peak | ≤1.5GB（尽量） |
| 脚本 | `research/g1g5_etf_core_sleeve_weights.py` |

---

## 6. 请 New Bot / Beta

预注册通过后：产表 → Alpha ACCEPT（研究级）→ 派 **Book-Smoke @60万∧100万 vs 510300**。  
本预注册 **不授权** promotion / 密封 / Strategy。
