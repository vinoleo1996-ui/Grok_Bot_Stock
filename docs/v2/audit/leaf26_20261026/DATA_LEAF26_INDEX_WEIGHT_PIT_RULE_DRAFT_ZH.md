# Data：叶26 index_weight PIT / available_at 规则草案（研究级）

- 角色：QuantLab Data 执行器
- 时刻：2026-10-26 01:17 ET (America/New_York)
- 对照：`DATA_LEAF26_ETF_FLOW_GAP_RECEIPT_20261025_ZH.md` sha `aaf84d66…`；盘点 `c03a9f0e…`
- 约束：live=false；**禁写生产**；本文件仅为规则草案，**须 Arch+Data 共签后**方可落列到 `data/v2`
- promotion_approved=false

---

## 1. 现状（2026-10-26 复测，与 aaf84d66 **无 DELTA**）

| 项 | 值 |
|---|---|
| 路径 | `data/v2/index_members/index_weight_csi300_500_1000.parquet` |
| sha256 | `d543a485959d6b579a2c5a26e18c3f7afea7a1047e308367588729c1f69bbd39` |
| 行数 | 189000 |
| 列 | `index_code, con_code, trade_date, weight` |
| `available_at` | **ABSENT** |
| `trade_date` | 20180131 → 20260930 |
| 指数 | 000300.SH 31500/105；000905.SH 52500/105；000852.SH 105000/105 |

202610 原始月片三指数均为 **0 行**（sha 同占位 `e5feded3…`）。

旁路（有 PIT，**禁作本叶主轴**）：

| 表 | sha | 说明 |
|---|---|---|
| `index_member_events.parquet` | `2c54bfc9…` | 调样事件；有 `available_at` |
| `csi_review_calendar.parquet` | `9f42ab3a…` | 调样日历；`available_at=ann_date 20:00 SH` |
| `manifest_d5.json` | `8484b6c0…` | 写明成分来自 tushare `index_weight` **月末快照** |

---

## 2. 建议 `available_at` 规则（二选一；**默认推荐 A**）

### 方案 A（默认推荐）：下一自然月首日 09:00 Asia/Shanghai（保守）

- 定义：对月末快照 `trade_date=YYYYMMDD`（该月最后一个交易日编码），令  
  `available_at = 下一自然月 1 日 09:00 Asia/Shanghai`。  
- 生产落地时须再映射为 **该日及之后首个 SSE 交易日 09:00**（若 1 日非交易日则顺延）。  
- 理由：Tushare 月度权重通常滞后于月末；无中证官网披露时刻证据时，用「下一月初开盘前」避免把当月末点当日内可得。  
- 风险：偏保守 → 研究窗口略短；调样窗（6/12 月）仍可能与真实公告日错位。

### 方案 B（激进，不推荐默认）：月末 `trade_date` 当日 20:00 Asia/Shanghai

- 对齐 D5 调样「盘后公告」习惯。  
- 风险：**前视**——若数据实际于次月才入库/披露，会把不可得权重当可得。  
- 仅当有中证/基金公司披露时刻证据链时，再考虑升级为默认。

**本草案默认采用方案 A。** 正式冻结前须 Arch 批注选择。

---

## 3. 建议列 schema（研究表；未落地）

| 列 | 类型 | 说明 |
|---|---|---|
| `index_code` | string | 如 `000300.SH` |
| `con_code` | string | 成分 |
| `trade_date` | string YYYYMMDD | 月末快照日（数值有效日） |
| `weight` | float64 | 权重（和≈100） |
| `available_at` | timestamp(tz=Asia/Shanghai) | 方案 A/B |
| `available_at_tz` | string | `Asia/Shanghai` |
| `available_at_rule` | string | 如 `next_calendar_month_day1_09:00_SH_v1` |
| `promotion_approved` | bool | 默认 false |

路径建议（**待 Arch 钉**，本回合不建）：  
`data/v2/index_members/index_weight_csi300_500_1000_pit.parquet`  
或原表原地加列（破坏性更大，须单独 `.ok`）。

---

## 4. 与 D5 events 关系

- D5（`index_member_events` / `csi_review_calendar`）刻画 **调入/调出事件** 的 PIT，**不能**替代月度权重数值。  
- 权重表 PIT 与 D5 同源思路（公告/可得时点），但是 **独立契约**。  
- 消费侧：严格 PIT 用本表 `available_at`；调样窗敏感性可交叉 D5，勿混为一表。

---

## 5. 研究绕行（当前可继续）

```
pit_basis = month_end_snapshot_no_available_at
asof(session) = max{ trade_date | trade_date ≤ session }  # 最近月末快照
```

- 预注册 / r2 须 **披露** 上述 `pit_basis`；**不得**静默称严格 PIT。  
- 与 aaf84d66 §6、AI r2 `0b55bfeb` 对齐：研究级主规格可推进；正式冻结前须 Arch 接受披露或落列。

---

## 6. /tmp 合成样例（≤3 月末点；**未**写回 data/v2）

| 项 | 值 |
|---|---|
| 路径 | `/tmp/leaf26_20261026_samples/index_weight_available_at_sample_3months.parquet` |
| sha256 | `c596e938595b8a49ab3d91796b6435e4cc056ea0bdf8bcc527fdda5b43d52c7d` |
| 内容 | 000300/000905 × {20241231,20250630,20260930}；2400 行 |
| 规则标签 | `next_calendar_month_day1_09:00_SH_DRAFT` |

---

## 7. 落地步骤（须 Arch 共签；本回合不执行）

1. Arch 批注采用方案 A 或 B；钉 `available_at_rule` 字符串与 schema。  
2. Eng/Data 写转换脚本：读现合并表 → 赋 `available_at` → 写新 parquet（或加列）。  
3. 续补 202610 月片（依赖中转 + `.ok`；**本回合禁拉**）。  
4. 更新 D5/权重相关 manifest；`promotion_approved` 仍 false 直至另签。  
5. **不**消费补跑 `.ok` `9e4359f9`；SUSPEND 维持。

**本项状态：仍 GAP**（严格 PIT）；已推进 = 规则草案 + /tmp 样例 + 绕行口径钉死。
