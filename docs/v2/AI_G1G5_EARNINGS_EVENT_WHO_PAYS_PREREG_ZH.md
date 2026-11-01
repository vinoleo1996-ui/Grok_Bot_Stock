# who_pays 机制预注册 · 业绩信息事件叶（研究级）

| 项 | 值 |
|---|---|
| 日期 | 2026-10-13 ET（America/New_York），写于满窗 X2 之前 |
| 作者 | QuantLab AI（执行器） |
| Leo 指令 | 2026-10-13 12:51 ET 本聊天确认「连续开新叶（残差来源，避开已灭十三包）」；目标年化向 15% |
| 叶名 / mechanism_tag | `g1g5_ashare_earnings_event_v1` |
| 对应外网候选 | `docs/v2/WEB_RESEARCH_15PCT_PATHS_ZH.md` ②业绩信息事件（预告/快报 + 公告后隔夜跳空） |
| promotion_approved / live | **false / false** |
| 状态 | 预注册 → 满窗 X2 权重 → WEIGHT RECEIPT（含去β残差相关自检）→ 停；**不自跑** Book-Smoke |
| 禁 | GP；小盘；高杠杆；教科书动量/价值主线；uvicorn；已灭十三包同构换皮 |

## 0. 数据源与 PIT（含缺口说明）

| 数据 | 路径 | PIT 字段 | 覆盖 |
|---|---|---|---|
| 公告分类表（主） | `data/v2/events/announcements_classified_pit.parquet` + `..._post202406.parquet` | `available_at`（规则：`ann_date 23:59`，无时钟 → 次交易日起可交易；少量 `ann_time`） | 2018-01 → 2026-10-11，覆盖 X2 全窗 |
| 业绩预告（数值） | `data/v2/events/forecast_1y.parquet`（EM） | `available_at` | **仅 2025-10-13 起一年** → 不足满窗，**本叶不用作主信号** |
| 业绩快报（数值） | `data/v2/events/express_1y.parquet` | `available_at` | **仅 2025-10-14 起一年** → 同上，不用 |
| 价格 | D0 panels ∪ `asof_extend_tushare_202610`（`g1g5_x2_panel_stitch`） | 日线 | 至 2026-10-09 |

**缺口（写明，不编造）**：满窗（2024-01→2026-10）不存在带 `available_at` 的预告幅度（p_change）/快报数值或一致预期；因此「超预期度量」不能用预告幅度或分析师一致预期，改用 **公告标题方向 + 市场隔夜跳空确认** 作为超预期代理（见 §2）。待 Data 补齐 ≥3 年 forecast/express PIT 后可做 v2（幅度版），不在本叶内。

## 1. 谁付的钱（一句）

**对业绩预告/快报信息反应不足（post-announcement drift）的对手盘**：公告次日市场以行业相对隔夜跳空确认"好于预期"，但机构调仓/散户锚定使价格在随后 40 个交易日继续消化；本叶在跳空日**之后**才入场，赚的是确认后的漂移，不赚公告当日/跳空日本身。

## 2. 数学（写死可检验）

| 项 | 口径 |
|---|---|
| 事件 | 公告标题含「业绩预」或「业绩快报」；剔除标题含 更正/补充/取消/延期/摘要/英文；剔除 `event_type=earnings_miss`（预减/预亏/首亏/续亏等）；同票同日去重 |
| 事件日 D | `available_at` 归一日期；T1 = D 之后第一个交易日（严格 >D） |
| 隔夜跳空 | `gap = open(T1)/close(T1−1) − 1` |
| 行业残差 | `gap_ind = gap − median(同申万一级、同 T1、池内全体成员的 gap)`；同业不足 3 名时退化为 `gap − gap(510300)` |
| 确认门 | `gap_ind ≥ +1%`（事前取整阈值，非调参） |
| 入场 | 决策日 = **T2**（T1 之后下一交易日），T2 收盘权重生效；**不吃 D 与 T1 收益** |
| 持有 | 40 个交易日（T2 起），到期退出；同票新事件重置窗口 |
| 选股 | 每日活跃事件按 `gap_ind` 降序，取 ≤20 名；单名 4%；申万一级 ≤28%（≤7 名） |
| 压舱 | `510300.SH` = 1 − 个股权重和（事件稀疏日压舱可高于 20%，照实报，不用其它资产填充） |
| 市值 | 池限 mid_large PIT（锚 2024-06-28 流通市值前 300、有 D0 panel；决策日须仍为 mid_large 成员）——市值暴露由池约束，不另加市值因子 |
| 硬排除 | 600519.SH、002371.SZ（权重恒 0；ADV/冲击原因见 RECEIPT） |

## 3. 正交性

主轴 = 业绩公告事件 + 公告后跳空确认。**不读** ADV 分位（capacity_adv）、资金流（moneyflow_resid）、两融（margin_delta）、应计/OCF（accrual_quality、indcap_momneut_ocf）、估值残差（d1_val_resid）、北向、指数调仓（idx_rebal_flow）、摩擦/低换手/expand、resid_etf/etf_core。硬拒：对任一已灭包或 capacity_adv 活跃股 Jaccard 最大值 ≥0.7 且 ≥50% 抽样日 ≥0.7。

## 4. 预注册门（RECEIPT 必报，不达照实报）

1. 满窗 X2：2024-01-02 → 2026-10-09，日更长表 Σw=1、无 stub、无负权。
2. G6 前视证明 pass；peak_rss ≤1.5GB。
3. **去β残差自检**（非正式 Book-Smoke，按权重逐日 close-to-close 持有收益，无成本）：本叶与 capacity_adv 各自日收益对 510300 回归去β，残差相关 `ρ_excess < 0.5` **且** 本叶残差年化（α×252）**> 0**。

## 5. 诚实披露

预注册前做过一次可行性探针（池 300、事件计数与按跳空分档的 40 日超额汇总，全样本）。看到：全部事件 40 日超额均值≈+0.8%、中位数为负；跳空门 ≥1% 档均值≈+1.9%、中位≈−0.7%。阈值 1%/持有 40 日为事前常用取整值，未在探针后改动；但样本内已"见过"，Alpha 审时应视为弱样本外。
