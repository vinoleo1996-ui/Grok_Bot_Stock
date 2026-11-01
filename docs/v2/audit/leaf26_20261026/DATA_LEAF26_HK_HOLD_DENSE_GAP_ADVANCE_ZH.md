# Data：叶26 hk_hold 密窗缺口推进（研究级；不拉取）

- 角色：QuantLab Data 执行器
- 时刻：2026-10-26 01:17 ET (America/New_York)
- 对照：aaf84d66 / Intel `ETF_FLOW_PIT_CANDIDATES_latest.md` `ca035159…`
- 约束：live=false；**禁外网/中转拉取**；禁写生产

---

## 1. 复测（与 aaf84d66 **无 DELTA**）

| 项 | 值 |
|---|---|
| 路径 | `data/v2/northbound/hk_hold_ashare_daily_2018plus.parquet` |
| sha256 | `edf3f438a5b079263eca4e8b9005a27c0f602bf393641db3daa76caf0099ee69` |
| 行数 | 3715734 |
| 唯一交易日 | 1569 |
| `trade_date` | 20180102 → **20250630** |
| `available_at` | 有；max≈2025-06-30 18:00（Asia/Shanghai 规则侧） |
| 列要点 | `code,trade_date,ts_code,name,vol,ratio,exchange,available_at,available_at_tz,promotion_approved` |

### 密窗止点

- 202408 有数交易日 **12** 天：20240801–20240816（含周末跳过的交易日序列）。  
- **密日频止点：20240816**（确认）。

### 密窗之后稀疏点（完整列表）

| trade_date | 性质 |
|---|---|
| 20240930 | 季末点 |
| 20241231 | 季末点 |
| 20250331 | 季末点 |
| 20250630 | 季末点（当前 max） |

月度天数旁证（2024H2+）：202408=12；202409=1；202410–202411=0；202412=1；2025Q1–Q2 仅季末各 1。

---

## 2. 续密 / 替代源建议（**不拉取**）

| 优先级 | 建议 | 说明 |
|---|---|---|
| P0 | Tushare `hk_hold`（或文档别名 `hk_hold` / 沪深港通持股）按日续拉 20240819→今 | 接口名以盒上 `DATA_PROVIDERS_*` / 既有 ingest 脚本为准；本回合**不调用** |
| P1 | 核对 vendor_empty：若源头已改为「仅季报/月末」，则改特征定义为季频，勿假日频 | 与 Intel `nb_hold_dratio_20d` 失效条件对齐 |
| P2 | 官方替代：交易所/港交所披露的北向持股明细（若有稳定 API） | 须另签时区与 available_at |

排队包（待中转 + Arch `.ok` 后）：

1. 探测 20240819–20241031 是否仍有日频返回。  
2. 若有：续写 raw 片 → 重建 `hk_hold_ashare_daily_2018plus`（streaming；注意内存）。  
3. 若无：落 `DATA_HK_HOLD_SPARSE_CONTRACT` 并通知 Intel 特征降频。

**禁消费**补跑 `.ok` `9e4359f9`。

---

## 3. 与叶26 r2 关系

- `nb_hold_dratio_20d` 属 Intel 生态 / 敏感性，**非** r2 主轴（主轴=宽基 ETF 份额流→权重暴露）。  
- **不阻塞**叶26 r2 研究级推进；**阻塞** Intel 密窗持股特征。  
- 修密窗 ≠ 解阻叶25。

---

## 4. 状态

**仍 GAP**。本回合推进：止点复测确认、稀疏点完整列表、续密/替代源排队说明（零拉取）。
