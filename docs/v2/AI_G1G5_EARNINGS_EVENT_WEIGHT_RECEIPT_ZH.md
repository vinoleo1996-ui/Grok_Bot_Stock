# WEIGHT RECEIPT · 业绩信息事件叶 `g1g5_ashare_earnings_event_v1`（研究级）

| 项 | 值 |
|---|---|
| 预注册 | `docs/v2/AI_G1G5_EARNINGS_EVENT_WHO_PAYS_PREREG_ZH.md`（先于本次运行落盘） |
| 脚本 | `research/g1g5_earnings_event_weights.py` |
| 权重包 | `output/ai_factory/g1g5_earnings_event_daily_weights_20261014_005430.parquet`（+ `.meta.json`） |
| run meta | `output/ai_factory/g1g5_earnings_event_run_meta_20261014_005430.json`；日志 `g1g5_earnings_event_run.log/.time.log` |
| G6 | `debate_ledger_g1g5_earnings_event_20261014_005430_g6_proof.jsonl` → **pass** |
| promotion / live | **false / false**；未自跑 Book-Smoke；无 GP；未起 uvicorn |

## 1. 一句话机制
业绩预告/快报公告（PIT `available_at`，剔除预减/预亏类）后首个交易日 **行业相对隔夜跳空 ≥+1%** 确认超预期，**T2 入场**（不吃公告日与跳空日）持有 40 交易日；≤20 名×4%，申万一级≤28%，余额 510300 压舱。

## 2. 数据与 PIT
- 事件：`data/v2/events/announcements_classified_pit*.parquet`，`available_at = ann_date 23:59`（无时钟→次交易日可交易），标题含「业绩预/业绩快报」。
- **缺口**：`forecast_1y` / `express_1y`（含 p_change、快报数值、available_at）仅覆盖 2025-10-13 起一年，满窗无幅度/一致预期 → 超预期度量改用「标题方向 + 跳空确认」代理。需 Data 补 ≥3 年 forecast/express PIT 才能做幅度版 v2。
- 价格：D0 ∪ asof_extend（X2 stitch，raw close）。

## 3. 满窗 X2 结构
| 项 | 值 |
|---|---|
| 行 / 日 / 票 | **57,448 / 668 / 86**（85 只个股 + 510300） |
| 窗口 | 2024-01-02 → 2026-10-09（到 X2 末日；无 stub） |
| Σw | 每日 1.0000（min=max=1）；最小权重 0（无负权） |
| 池 | mid_large PIT 锚 2024-06-28 流通市值前 300（有 panel），决策日须仍为 mid_large 成员 |
| 事件 | 原始 886 → 确认 126（标题 earnings_beat 36 + 中性标题 90）；按入场年 2024:41 / 2025:40 / 2026:43 |
| 持股数 | 日均 7.4 名，最多 20；**82 天零个股（全压舱）** |
| 压舱 510300 | **均值 70.5%**，min 20%，max 100% |
| 单名 / 行业 | max 4.0% / max 20% |
| 换手 | 单边日均 1.44%，非零调仓日 143 |

⚠ 压舱均值 70.5% 远高于前叶 ~20%（事件稀疏是机制本身决定，未用其它资产填充）。叶表现大部分是 510300 β；Alpha 审时需判断是否接受此结构（或作为卫星而非主干）。

## 4. 正交（活跃股 Jaccard，抽样月末）
对 expand / friction / lowturn / resid_etf / etf_core / friction_cost_redesign / idx_rebal_flow / indcap_momneut_ocf / d1_val_resid / northbound / capacity_adv / margin_delta / accrual_quality / moneyflow_resid：**均值 0–0.024，最大值 ≤0.107，≥0.7 占比全部 0** → 无同构硬拒。

## 5. 去β残差自检（预注册门；非正式 Book-Smoke，close-to-close、无成本）
| 项 | 本叶 | capacity_adv |
|---|---|---|
| β vs 510300 | 1.07 | 0.69 |
| 残差年化 α | **+2.83%** | +5.06% |
| 毛 CAGR | 12.96% | 12.07% |
| 510300 同期 | 9.45% | |

- **ρ_excess（去β残差相关）= −0.27** ＜0.5 ✅；残差 α>0 ✅ → **预注册门通过**。原始超额相关 −0.34。
- 分年 α：2024 +1.7%，2025 +2.5%，2026 +6.9%（三年均正）。
- 解读：α 绝对值小（个股仅约 30% 仓位；按个股仓位折算约 +9%/年），且未扣成本；负相关意味着与 capacity_adv 叠加有分散价值，但单叶过 12% 门大概率不够，**更适合作 capacity_adv 的卫星候选**（判定路线②）。

## 6. 资源与约束
- peak_rss **≈723 MB**（/usr/bin/time 740 MB）≤1.5 GB；墙钟 5m48s。
- 600519.SH / 002371.SZ：硬排除，权重恒 0（沿前叶 ADV/冲击与整手约束口径；本叶本就无需它们）。
- 禁 GP / 小盘 / 杠杆 / 教科书动量价值主线；live/promotion=false。

## 7. 诚实披露
预注册前跑过一次可行性探针（事件计数与跳空分档 40 日超额汇总），阈值 1%/40 日未据此调整，但属"已见过样本"，应视作弱样本外。raw close 未复权，分红日略低估收益。

## 8. 建议
建议父代理派 **Alpha ACCEPT → Eng Book-Smoke（510300，60/100 万）**，并请 Eng 额外跑「capacity_adv 主干 + 本叶卫星」组合读数（路线②）。
