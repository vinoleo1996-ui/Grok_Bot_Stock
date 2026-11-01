# ACCEPT · 业绩信息事件叶 `g1g5_ashare_earnings_event_v1`（研究级）

| 项 | 值 |
|---|---|
| 裁决 | **研究级 ACCEPT**（硬闸过；Book-Smoke **PENDING**） |
| 日期 | 2026-10-13 ET · Alpha |
| promotion_approved / live / handoff / GP | false / false / NO / 禁 |
| 权重 | `output/ai_factory/g1g5_earnings_event_daily_weights_20261014_005430.parquet` |
| 预注册 / RECEIPT | `docs/v2/AI_G1G5_EARNINGS_EVENT_WHO_PAYS_PREREG_ZH.md` / `docs/v2/AI_G1G5_EARNINGS_EVENT_WEIGHT_RECEIPT_ZH.md` |

## 1. 独立核验（parquet）
- 57,448 行 / 668 日 / 86 标的（85 股 + 510300）；2024-01-02 → 2026-10-09
- 日 Σw min=max=1.0；负权 0；无 stub
- 单名 max 4.0%；申万一级 max 20%（≤28% ✅）；600519 / 002371 = 0
- 压舱 510300：均值 70.5%，min 20%，max 100%；全压舱 82 日；日均持股 7.4，最多 20

## 2. PIT
脚本 `research/g1g5_earnings_event_weights.py`：事件日 D=available_at 归一（ann_date 23:59 规则）；T1=严格 >D 首个交易日；gap=open(T1)/close(T1−1)−1，行业中位数去除；T2 起生效（不吃 D/T1）。**无前视** ✅。
软注：池锚 2024-06-28 流通市值前 300（沿前叶口径），2024H1 有轻微成分前视。

## 3. 防同构（逐日活跃股 Jaccard，全部 586 重叠日）
对 capacity_adv / moneyflow_resid / margin_delta×2 / accrual_quality / northbound / d1_val_resid / indcap_ocf / expand×3 / lowturn / friction_cost_redesign / resid_etf / etf_core / idx_rebal / nontextbook：**≥0.7 占比全=0**。最大 0.333（etf_core，小集合偶合）、0.121（accrual）、0.107（expand）；capacity 0.091、moneyflow 0.094。RECEIPT「≤0.107」为月末抽样，逐日略高，软注。

## 4. 去β自检 / G6 / 资源（引用 AI，未复算）
ρ_excess vs capacity_adv = −0.27；残差 α +2.83%/年；β=1.07；G6 pass；peak_rss≈723MB。

## 5. 缺口
- 预注册前可行性探针(全样本) → 弱样本外；阈值1%/40日为取整值、未见调参证据 → 不阻断
- 压舱510300均值70.5%(82天全压舱)；个股袖仅~30%，Book-Smoke 可能近似510300 → 软风险(卫星定位)
- 满窗无预告幅度/一致预期(仅标题+跳空代理)；forecast/express PIT 仅1年
- Jaccard：本侧逐日全样本 max=0.333(vs etf_core，小集合)、0.121(vs accrual)，高于 RECEIPT 月末抽样 ≤0.107；均远<0.7，软注记
- 文件名时间戳20261014_005430 为 +0800 时区(=2026-10-13 12:54 ET)，与盒钟一致，非异常
- 池锚 2024-06-28 流通市值前300(沿前叶口径)，2024H1 存轻微成分前视 → 继承性软注记
- raw close 未复权；去β自检无成本、非正式烟
- 600519/002371 硬排除=0

## 6. 判定理由
探针在预注册前、但阈值 1%/40 日为取整常用值，未见满窗调参证据 → 不降为 CONTINUE，记 GAP「pre-prereg probe → 弱样本外」。压舱 70.5% 为机制所致，定位为 capacity_adv **卫星候选**，仅记录。

## 7. 下一步
Book-Smoke **PENDING**：New Bot → Eng（60/100 万，510300 基准；建议附 capacity_adv 主干+本叶卫星读数）。禁 GP / 晋级 / 主书 / 实盘。

## 8. Book-Smoke 标注（2026-10-13 ET，Alpha 本侧盘面核验）
**状态：ACCEPT → BOOK_SMOKE_PASS / RESEARCH_CANDIDATE**（研究级；promotion_path 未设，需 Leo 本人在 Alpha 聊天明示；handoff=NO；live=false；禁 GP / Strategy / ACTIVE / 主书；不再派烟）

来源：`docs/v2/BOOK_SMOKE_G1G5_EARNINGS_EVENT_X2_RECEIPT_ZH.md`（run_id book_smoke_20261014_010240）· `output/v3/book_smoke_g1g5_earnings_event_x2/book_smoke_summary.json`
权重同文件：`output/ai_factory/g1g5_earnings_event_daily_weights_20261014_005430.parquet` ✅；窗口 X2 2024-06-03→2026-10-09（570 session，与 capacity_adv 同窗）；成本开（佣金/印花/滑点/冲击）；C0=纯 510300。

| AUM | BOOK CAGR | MDD | C0 CAGR | vsC0 | cost/AUM | fill | 门 |
|---|---|---|---|---|---|---|---|
| 60万 | 13.64% | −18.29% | 11.27% | +2.37pp | 1.18% | 0.67 | ✅ |
| 100万 | 13.87% | −19.08% | 11.27% | +2.60pp | 1.32% | 0.76 | ✅ |

本侧计算：any_pass=true，both_aum_pass=true（门：CAGR∈[12%,18%] ∧ MDD≥−28%，两档）。与 Eng 数字一致，无差异。

对照 capacity_adv 主干（同窗）：60万 13.82%/−10.07%；100万 12.23%/−11.62%。本叶 MDD 深约 8pp、Sharpe 0.73 vs 0.88–1.02。组合 70/30、80/20：未优于主干（两档 MDD 更深，60万 CAGR 更低）→ **仅诊断，卫星不对主干增值**。

软注记：
- 压舱：烟内实际 510300 均值≈71.8%；超额 +2.4~2.6pp 全部来自 ~28% 个股袖，粗估个股袖年化≈19–20%（集中度高、MDD 由此加深）。
- 预注册前满窗探针 → 弱样本外，过门不能视为独立 OOS 证据。
- 价格：引擎计入 corporate_action_cash（60万≈3.49万），分红/送转按公司行动处理，raw close 疑虑基本缓解。
- fill_ratio 0.67/0.76 偏低，事件T2入场成交受限。
