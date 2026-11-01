# Data：叶26 premium PIT 拼装配方（研究级）

- 角色：QuantLab Data 执行器
- 时刻：2026-10-26 01:17 ET (America/New_York)
- 约束：live=false；配方 + /tmp 小样；**勿**写 `data/v2`

---

## 1. 输入表（复测无 DELTA）

| 表 | 路径 | sha256 | 行数 | 日期 | 关键列 |
|---|---|---|---|---|---|
| 价量 | `data/v2/etf/etf_daily_adj.parquet` | `48b21e84695b120b8621eff11f31f3e47879bfc05c93d3d979ddab9220ffd74c` | 1564839 | 20150105→20261016 | `close,amount,available_at`；**无** unit_nav/premium |
| 份额+NAV | `data/v2/etf/share_pit/etf_share_flow_pit_major.parquet` | `a3eac35b91ae78a9cd152a7e68fb75a9274c6a32a1bfa7550f6ada88c45232bf` | 14258 | →20261009 | `unit_nav,nav_available_at,available_at` |

盒上仍 **无** 现成 `*premium*` parquet。

---

## 2. Join 配方

```
etf_daily_adj ⋈_inner share_pit
  ON ts_code AND trade_date

premium = close / unit_nav - 1

decision_available_at = max(
  etf_daily_adj.available_at,          # 通常 T 15:00 SH
  coalesce(nav_available_at, share.available_at)  # 份额/NAV 常 T+1 09:00
)
```

- 决策 asof：只用 `decision_available_at ≤ decision_ts` 的行。  
- 禁止用 T 未入库 NAV 做 T 开盘信号（与 Intel 清单一致）。  
- `promotion_approved=false`。

### 建议输出 schema

| 列 | 说明 |
|---|---|
| `ts_code` | ETF |
| `trade_date` | YYYYMMDD |
| `close` | 收盘价 |
| `amount` | 成交额 |
| `unit_nav` | 单位净值 |
| `premium` | close/unit_nav−1 |
| `px_available_at` | 价侧 |
| `nav_available_at_used` | NAV/份额侧 |
| `decision_available_at` | max(…) |
| `premium_pit_rule` | 规则标签字符串 |
| `promotion_approved` | false |

建议路径（待 Arch/Eng 共签；**未建**）：  
`data/v2/etf/premium_pit/etf_broad_premium_pit.parquet`

---

## 3. /tmp 小样（510300 / 510500）

| 项 | 值 |
|---|---|
| parquet | `/tmp/leaf26_20261026_samples/premium_pit_sample_510300_510500.parquet` |
| sha256 | `60a8420f32d52ec08c914f84c3ab9b70d5fd88dda29bb23da2ef1ebd4e07831f` |
| 行数 | **4250**（每码 2125） |
| 日期 | 20180102 → 20261009 |
| premium NaN | 0 |
| 中位 premium | 510300≈−0.00046；510500≈−0.00039 |
| 审计目录 CSV head20 | `docs/v2/audit/leaf26_20261026/premium_pit_sample_510300_510500_head20.csv` |

---

## 4. 状态

**仍 GAP**（无生产 PIT 视图）。本回合推进：配方钉死 + 双码全历史可拼小样证明可行性；落地须 Eng/Data 共签 + Arch `.ok`。
