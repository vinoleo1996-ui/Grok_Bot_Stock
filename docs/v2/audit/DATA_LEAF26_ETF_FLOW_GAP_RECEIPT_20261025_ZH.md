# Data：叶26 ETF 资金流缺口回执（研究级；**不签 .ok**）

- 角色：QuantLab Data 执行器
- 时刻（America/New_York）：**2026-10-25T06:54:00-04:00**
- 主令：主 Agent Supervise 06:49 轻催 — 叶26 ETF 资金流缺口盘点落盘（覆盖 index_weight PIT / 000852 / ETF 映射 / hk_hold 密窗及 Intel 清单待 Data 项）
- 禁令：只读盘点；**禁写生产**；**禁消费**补跑 `.ok` `9e4359f9`；禁外网/中转拉取；**不挡叶25@10:00**；不申请本叶 `.ok`；不改 `TEAM_STATE`
- live=false；`promotion_approved=false`；research_only=true
- 方法：只读 `sha256sum` + `pyarrow` schema/行数/日期极值/抽样；未跑策略；未写 `data/v2`；未消费任何 `.ok`

---

## 输入核验（sha MATCH）

| 文件 | 期望前缀 / 全长 | 实测全长 sha256 | 结果 |
|---|---|---|---|
| AI 现行主规格 r2：`docs/v2/AI_LEAF26_BROAD_ETF_FLOW_STOCK_WHO_PAYS_DRAFT_r2.md` | `0b55bfeb…` / `0b55bfeb3b033da4715e4dbc5c996e92b954fc10e385c10b308da992d87a60b5` | `0b55bfeb3b033da4715e4dbc5c996e92b954fc10e385c10b308da992d87a60b5` | **MATCH** |
| 旧盘点（**不覆写**）：`docs/v2/audit/leaf26_20261025/DATA_LEAF26_GAP_INVENTORY_ZH.md` | `c03a9f0e…` / `c03a9f0e4c9c7622cd0dc0be36de2aaada70f9dacc48921156c89f640125b305` | `c03a9f0e4c9c7622cd0dc0be36de2aaada70f9dacc48921156c89f640125b305` | **MATCH** |
| Intel 清单：`output/intel/ETF_FLOW_PIT_CANDIDATES_latest.md` | `ca035159…` / `ca0351595f7a2ae4bd0c2367a510cd2012626a1d76613db517df7108937d886c` | `ca0351595f7a2ae4bd0c2367a510cd2012626a1d76613db517df7108937d886c` | **MATCH** |
| Strategy 袖套（r2 引用）：`docs/v2/STRATEGY_ETF_FLOW_SLEEVE_PLAN_20261025_ZH.md` | `7722efec…`（r2 钉） | `7722efec9f750ec89b2047d5890a39a119771eb86c8fb35bc265217b82286091` | **MATCH** |

旁证表（本次实测，非输入闸）：见各节路径+全长 sha。

---

## 结论表（OK / GAP / PARTIAL）

| # | 项 | 状态 | 一句话 |
|---|---|---|---|
| 1 | `index_weight` PIT / `available_at` / asof | **GAP**（数值有、PIT 无） | 合并表 189000 行至 20260930；列仅 `index_code,con_code,trade_date,weight`；**无** `available_at`；研究可 `trade_date≤session` 最近月末 + 披露 `pit_basis` |
| 2 | 000852 权重 | **PARTIAL**（数值 OK；r2 剔除） | 合并表内 `000852.SH` 105000 行、105 月末点至 **20260930**；202610 原始片 **0 行**；**r2 主规格默认剔除** 512100/000852 |
| 3 | 宽基 ETF↔指数映射 + 联接去重 | **PARTIAL**（无 Arch 钉表；r2 可硬编码绕行） | 无官方映射 parquet；`fund_basic` 仅中文 `benchmark`；联接约 24 条无名契约；r2 硬编码两对可研究级推进 |
| 4 | `hk_hold` 密窗 | **GAP**（密→20240816；后稀疏） | 表有 `available_at`；`trade_date` max=**20250630**；202408 仅 12 天至 **20240816**；其后仅季末点 20240930/20241231/20250331/20250630 |
| 5 | Intel P0：premium PIT 视图 | **GAP** | `etf_daily_adj` 有 close/amount/`available_at` 至 20261016，**无** `unit_nav`/premium 列；share 表有 `unit_nav` 可拼，**无现成 premium PIT 表** |
| 6 | Intel P0：美 ETF PIT | **GAP** | 盒上 `data/v2`（及 `data/`）未见带 `available_at` 的美股 ETF parquet；仅有 `output/intel/ALERTS_*` 快照旁路 |
| 7 | Intel P0：`hsgt_top10` catalog vs 文件 | **PARTIAL**（文件新、manifest 旧） | 文件 max=`20261016`、38364 行；manifest `date_range` 止 **20261013**、rows=38304、内嵌 sha 已过期；`northbound_summary` 与文件对齐 |

### 研究级推荐路径（**不执行拉取**；签 `.ok` 前须重钉 sha）

| 用途 | 推荐路径 | 备注 |
|---|---|---|
| 宽基份额流（叶26 主输入） | `data/v2/etf/share_pit/etf_share_flow_pit_major.parquet` | 含 510300/510500；`available_at` 至 20261009；按 manifest 份额次日 09:00 规则 |
| 指数权重 asof（披露非严格 PIT） | `data/v2/index_members/index_weight_csi300_500_1000.parquet` | `trade_date≤session` 最近月末；钉 `pit_basis=month_end_snapshot_no_available_at` |
| ETF↔指数（主规格） | **硬编码** `510300.SH→000300.SH`、`510500.SH→000905.SH` | 与 r2 / Strategy 袖套一致；扩池须 Arch 映射表 |
| 北向市场净流入（生态） | `data/v2/northbound/moneyflow_hsgt_daily_2014plus.parquet` | 至 20261009；有 `available_at` |
| 北向持股占比（生态） | `data/v2/northbound/hk_hold_ashare_daily_2018plus.parquet` | **2024-08-16 后勿当日频** |
| 折溢价（待拼装） | `etf_daily_adj` ⋈ share `unit_nav` | 派生 `premium≈close/unit_nav−1`；asof=两表 `available_at` 取 max；**本回执不落地** |

---

## 1) `index_weight` PIT / available_at / asof

### 1.1 合并表（实测）

| 项 | 值 |
|---|---|
| 路径 | `data/v2/index_members/index_weight_csi300_500_1000.parquet` |
| sha256 | `d543a485959d6b579a2c5a26e18c3f7afea7a1047e308367588729c1f69bbd39` |
| 行数 | **189000** |
| 列 | `index_code, con_code, trade_date, weight` |
| `available_at` | **ABSENT** |
| `trade_date` | **20180131 → 20260930** |
| 指数 | `000300.SH`（31500 行 / 105 月末）、`000905.SH`（52500 / 105）、`000852.SH`（105000 / 105） |

### 1.2 202610 原始月片

| 文件 | 行数 |
|---|---|
| `data/v2/tushare_raw/index_weight/000300_SH_202610.parquet` | **0** |
| `data/v2/tushare_raw/index_weight/000905_SH_202610.parquet` | **0** |
| `data/v2/tushare_raw/index_weight/000852_SH_202610.parquet` | **0** |

### 1.3 缺口与研究级建议

1. 权重表无 `available_at` / asof 契约 → **不得**静默称严格 PIT。  
2. 月末 `trade_date` ≠ 披露可得时点；用「当日月末点」可能前视。  
3. **建议（不执行）**：Arch+Data 共签 `available_at` 规则后落列；短期预注册披露 `pit_basis=month_end_snapshot_no_available_at` 并继续 `trade_date≤session` 最近月末。

**本项状态：GAP**（阻塞「严格 PIT」声称；**不**硬阻塞 r2 研究级主规格若已披露 `pit_basis`）。

---

## 2) 000852 权重（r2 主规格剔除）

| 项 | 值 |
|---|---|
| 来源 | 同上合并表，滤 `index_code=="000852.SH"` |
| 行数 / 月末点数 | 105000 / **105** |
| 日期 | 20180131 → **20260930** |
| 202610 | 原始片存在且 **0 行**；合并表无 202610 点 |
| r2 口径 | **默认剔除** `512100.SH` / `000852.SH`（与 Strategy 袖套默认池对齐） |

缺口：同 §1 无 PIT；202610 空。敏感性支路若开须 Strategy+Data 共签 + 预注册 bump。

**本项状态：PARTIAL** — 数值不阻塞；**r2 主规格不依赖此项**。

---

## 3) 宽基 ETF↔指数映射 + 联接去重

### 3.1 现状

| 资产 | 路径 | sha256 | 说明 |
|---|---|---|---|
| Arch 钉映射表 | （无） | — | 全盘无 `*broad*etf*map*` / 官方 `index_code` 列落地 |
| `fund_basic`（场内 E） | `data/v2/etf/raw/fund_basic_E.parquet` | `07e0151624b02eefd11c88c0a1de31e6a70db8736c5dd019a73aaab902b66d8f` | 有中文 `benchmark`；**无** `index_code` |
| 份额流 major | `data/v2/etf/share_pit/etf_share_flow_pit_major.parquet` | `a3eac35b91ae78a9cd152a7e68fb75a9274c6a32a1bfa7550f6ada88c45232bf` | 含 510300/510500（及 512100 等）；**无**映射列；至 **20261009** |

`fund_basic` 旁证（研究可读，非官方钉）：

| ts_code | name | benchmark |
|---|---|---|
| 510300.SH | 华泰柏瑞沪深300ETF | 沪深300指数×100% |
| 510500.SH | 南方中证500ETF | 中证小盘500指数×100% |

名称含「联接」约 **24** 条；**无**联接→母 ETF 去重契约。major 名单事实未纳入联接（非契约保证）。

### 3.2 研究级绕行（对齐 r2）

主规格硬编码：

- `510300.SH` ↔ `000300.SH`
- `510500.SH` ↔ `000905.SH`

扩池 / 联接去重须 Arch 映射表（建议列：`etf_ts_code,index_code,role,is_feeder,feeder_of,valid_from,valid_to,source,promotion_approved`）。**本回执不建表、不拉数。**

**本项状态：PARTIAL** — 无钉表；**r2 两对硬编码可研究级绕行，不硬阻塞主规格**。

---

## 4) `hk_hold` 密窗缺口（Intel / 主令覆盖）

| 项 | 值 |
|---|---|
| 路径 | `data/v2/northbound/hk_hold_ashare_daily_2018plus.parquet` |
| sha256 | `edf3f438a5b079263eca4e8b9005a27c0f602bf393641db3daa76caf0099ee69` |
| 行数 | **3715734** |
| 列（要点） | `code,trade_date,ts_code,name,vol,ratio,exchange,available_at,available_at_tz,promotion_approved` |
| `available_at` | **有**；min≈2018-01-02 18:00 → max≈2025-06-30 18:00（Asia/Shanghai 规则侧） |
| `trade_date` | 20180102 → **20250630** |
| 密日频止点 | **20240816**（202408 仅 12 个交易日有数：01–16） |
| 密窗之后 | 仅季末点：**20240930 / 20241231 / 20250331 / 20250630** |

缺口：2024H2 后勿当日频；续密窗或官方替代源须 Arch `.ok` 后方可写生产（**本回执不拉取**）。

与叶26 r2 关系：`nb_hold_dratio_20d` 属 Intel 生态/敏感性，**非** r2 主轴（主轴为宽基 ETF 份额流→权重暴露）。

**本项状态：GAP** — **不阻塞**叶26 r2 主规格；阻塞 Intel `nb_hold_*` 密窗特征。

---

## 5) Intel P0：premium PIT / 美 ETF PIT / hsgt_top10 catalog

### 5.1 premium PIT 视图 — **GAP**

| 表 | 路径 | sha256 | 行数 | 日期 | 与 premium 相关 |
|---|---|---|---|---|---|
| 价量 | `data/v2/etf/etf_daily_adj.parquet` | `48b21e84695b120b8621eff11f31f3e47879bfc05c93d3d979ddab9220ffd74c` | 1564839 | 20150105→**20261016** | 有 `close,amount,available_at`；**无** `unit_nav` / premium |
| 份额+NAV | `…/etf_share_flow_pit_major.parquet` | `a3eac35b…`（见上） | 14258 | →20261009 | 有 `unit_nav` / `nav_available_at` / `available_at` |

盒上 **无** 现成 `*premium*` parquet。研究级拼装建议：`premium≈close/unit_nav−1`，决策 asof = 两表 `available_at` 取 **max**；落地须 Eng/Data 共签（**不执行**）。

### 5.2 美 ETF PIT — **GAP**

- `data/` / `data/v2/` 下按名检索 `premium/us_etf/kweb/sox/spy/qqq`：**0** 命中带 `available_at` 的美 ETF parquet。  
- 现有旁路：`output/intel/ALERTS_*` 快照（非 PIT 主库）。  
- 建议（不执行）：若需要，另签时区规则（US close+缓冲→下一 SSE 09:00）后落 `data/v2` 研究表。

### 5.3 `hsgt_top10` catalog vs 文件 — **PARTIAL**

| 源 | max `trade_date` / 行数 / sha 备注 |
|---|---|
| 文件 `data/v2/northbound/hsgt_top10_daily_2018plus.parquet` | **20261016** / **38364** / sha `c54935e82c8372bb5ac37023a4319ea16eff7f9fbc0aa03ef3106937f59a42f1`；列含 `available_at` |
| `hsgt_top10_manifest.json` sha `4d5e6f5d…` | `date_range` 止 **20261013**；rows=**38304**；内嵌 parquet sha=`94fdb347…`（**≠**当前文件） |
| `northbound_summary.json` sha `85e87ac5…` | range 止 **20261016**；rows=38364（与文件 **对齐**） |

校准建议（不执行）：按当前文件重写 manifest 的 rows/days/`date_range`/内嵌 sha；消费侧以 **文件** max date 为准，勿信过期 manifest。

旁证（生态，非缺口主轴）：

| 表 | 路径 | sha256 | max `trade_date` |
|---|---|---|---|
| moneyflow_hsgt | `data/v2/northbound/moneyflow_hsgt_daily_2014plus.parquet` | `ee1fca152f580b906628b4be5bc67e153e9f48aed3a2d31ffbde72e963b7d369` | **20261009**（有 `available_at`） |

---

## 6) 汇总：阻塞叶26 r2 主规格 vs 仅阻塞 Intel 生态

| # | 项 | 阻塞叶26 r2 主规格？ | 说明 |
|---|---|---|---|
| 1 | index_weight 无 `available_at` | **软阻塞**（严格 PIT）；研究级 **可绕** | r2 已要求披露 `pit_basis`；正式冻结前须 Arch 接受披露或落列 |
| 2 | 000852 / 202610 空 | **否** | r2 **剔除**；数值至 20260930 仅敏感性支路需要 |
| 3 | 映射无 Arch 钉表 | **否**（研究级） | r2 硬编码两对即可；扩池才硬阻塞 |
| 4 | hk_hold 密窗 | **否** | Intel / 北向持股特征；非 r2 主轴 |
| 5 | premium PIT 缺失 | **否** | Intel P0；r2 主推份额流非折溢价 |
| 6 | 美 ETF PIT 缺失 | **否** | Intel 可选外生冲击 |
| 7 | hsgt_top10 manifest 漂移 | **否** | catalog 校准；文件本身可用至 20261016 |

**叶26 r2 主规格研究级结论**：主输入（`etf_share_flow_pit_major` 含 510300/510500 + 权重表 000300/000905）**本地可读**；真正挡「正式预注册 / 严格 PIT / `.ok`」的是 **权重 PIT 契约**（及日后扩池映射）。本回执**不**申请 `.ok`。

**明确声明**：

- **不挡叶25@10:00**。  
- **不申请**本叶 `.ok`；**不消费**补跑 `.ok` `9e4359f9`。  
- Arch 裁示 **SUSPEND**（双测 DUAL_STABLE_FAIL 等）与本回执**无关**；本文件不触碰补数/生产写路径。  
- 未改 `TEAM_STATE`；未发跨 agent 消息；未写生产数据。

---

## 7) 交付

- 本回执路径：`docs/v2/audit/DATA_LEAF26_ETF_FLOW_GAP_RECEIPT_20261025_ZH.md`  
- 原子写：tmp → `mv` 就位。  
- 旧盘点 `docs/v2/audit/leaf26_20261025/DATA_LEAF26_GAP_INVENTORY_ZH.md`（sha `c03a9f0e…`）**保留不覆写**。
