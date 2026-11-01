# Data：叶26 宽基 ETF↔指数映射草案（**DRAFT 非 Arch 钉**）

- 角色：QuantLab Data 执行器
- 时刻：2026-10-26 01:17 ET (America/New_York)
- 约束：研究级；CSV 仅在审计目录；**非** Arch FROZEN

---

## 1. 硬编码主规格（与 r2 / aaf84d66 一致）

| etf_ts_code | index_code | 说明 |
|---|---|---|
| 510300.SH | 000300.SH | 华泰柏瑞沪深300ETF |
| 510500.SH | 000905.SH | 南方中证500ETF |

r2 **默认剔除**：512100.SH / 000852.SH（本草案 CSV 中标注 `r2_excluded_DRAFT`，扩池用）。

---

## 2. 建议列（对齐 aaf84d66）

`etf_ts_code, index_code, index_name, role(primary|secondary|feeder), is_feeder, feeder_of, valid_from, valid_to, source, promotion_approved`

落地文件（本回合）：

| 文件 | 说明 |
|---|---|
| `docs/v2/audit/leaf26_20261026/DATA_LEAF26_BROAD_ETF_INDEX_MAP_DRAFT.csv` | 主两对 + 512100 候选 + 若干联接 |

---

## 3. fund_basic 联接候选（名称含「联接」共 24；宽基相关摘录）

来源：`data/v2/etf/raw/fund_basic_E.parquet` sha `07e01516…`（复测 MATCH）。

### 沪深300 相关联接

| ts_code | name |
|---|---|
| 160615.SZ | 鹏华沪深300ETF联接(LOF)-A |
| 160706.SZ | 嘉实沪深300ETF联接(LOF)-A |
| 161211.SZ | 国投瑞银沪深300金融地产ETF联接（主题，非宽基主轴） |

### 中证500 相关联接

| ts_code | name |
|---|---|
| 160119.SZ | 南方中证500ETF联接(LOF)-A |
| 162711.SZ | 广发中证500ETF联接(LOF)-A |
| 501036.SH | 汇添富中证500ETF联接(LOF)-A |
| 501037.SH | 汇添富中证500ETF联接(LOF)-C |

### 去重规则建议（草案）

1. `name` 含「联接」或产品说明书标明联接 → `is_feeder=true`，**不进**叶26 主信号。  
2. 主信号只保留母 ETF 份额流（`etf_share_flow_pit_major` 事实已不含上述联接码，但非契约）。  
3. 扩到 `etf_share_flow_pit_all` 前必须落地本映射表并由 Arch 钉 sha。

---

## 4. 状态

**仍 PARTIAL**。推进：审计目录 DRAFT CSV + 联接清单；**等待 Arch 钉路径/sha** 后方可称官方映射。  
研究级 r2 两对硬编码可继续，**不硬阻塞**主规格。
