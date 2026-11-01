# Data 回执：AI 叶26 三项缺口盘点（研究级）

- 角色：QuantLab Data 执行器
- 时点：2026-10-25 约 04:50 ET（America/New_York）
- 范围：只读盘点 `/workspace/QuantLab/data`、`data/v2`、`docs/v2`、manifest / schema 注释
- 禁：写生产、外网/中转拉取、import 需 Arch `.ok` 的生产写路径
- live=false；promotion_approved=false；research_only=true

---

## 0. 草稿核对

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/AI_LEAF26_BROAD_ETF_FLOW_STOCK_WHO_PAYS_DRAFT_ZH.md` |
| 任务期望 sha256 | `5fd1a4a78c4024013baecc1abcd23f8c5dda111fa00e5a54766d930e87c1f3bc` |
| **实测 sha256** | `34c1540f50452b7fbc60dcbf2c7cdfeb0820b09ddf5a8b1342833ca200f88926` |
| 结论 | **不匹配**。本回执按盘面实测文件盘点；请主/AI 复核草稿是否已覆写或期望钉过期。 |

草稿 §7 缺数清单与本回执三项对齐：`index_weight` PIT；中证1000 权重可用范围；宽基 ETF↔指数官方映射（含联接去重）。

---

## 1) `index_weight` 的 PIT / available_at / asof 规则

### 现状（有表、无 PIT 列）

| 资产 | 路径 | sha256 | 说明 |
|---|---|---|---|
| 合并权重表 | `data/v2/index_members/index_weight_csi300_500_1000.parquet` | `d543a485959d6b579a2c5a26e18c3f7afea7a1047e308367588729c1f69bbd39` | 189,000 行；`trade_date` 20180131→20260930 |
| 原始月度片 | `data/v2/tushare_raw/index_weight/{000300,000905,000852}_SH_YYYYMM.parquet` | （目录级；三指数各 106 文件，201801–202610） | 构建源；202610 三指数文件均为 **0 行占位** |
| 调样事件（旁路） | `data/v2/index_members/index_member_events.parquet` | `2c54bfc90e136c48d589caf1e5ac122941a93253c44ee3789ef53f3371272d15` | **有** `available_at`；禁作本叶主轴（调样事件） |
| 调样日历 | `data/v2/index_members/csi_review_calendar.parquet` | `9f42ab3ac4baae83b0d489fbea51c8091d8b4c52e9f03bf41d3c4359aad00ca7` | 有 `available_at`（ann_date 20:00 SH）；非权重表 |
| D5 manifest | `data/v2/index_members/manifest_d5.json` | `8484b6c03bcdcc535f6d9acdc836e17669c316c825c9da9dfcc0b128a807e087` | 写明成分来自 tushare `index_weight` **月末快照** |

**列名（合并表 / 非空原始月片）**：`index_code, con_code, trade_date, weight`  
- **无** `available_at` / `available_at_tz` / `asof` / `ann_date` / `effective_date`  
- 每月一片：`trade_date` 为当月月末交易日一点（如 `20260930`）；权重和≈100  
- 指数代码仅：`000300.SH` / `000905.SH` / `000852.SH`

### 既有「asof」消费惯例（非正式契约）

研究脚本普遍写法：对 session `t` 取 `trade_date ≤ t` 的**最近月末快照**（`index_weight_asof`）。见如 `output/v3/run_stock_etf_smoke.py`、`V3_EVT_DT_INST_STOCK_PREREG.md`、`anns_coverage_csi.py` 注释「PIT 近似」。

文档旁证：
- `docs/v2/ALPHA_DATA_REQUESTS_STATUS.md`（sha `2bc889f8…`）：「Tushare 没有公告日；生效日只能界定在相邻两次快照之间」
- `docs/v2/ALPHA_DATA_D5D6_DELIVERY_ZH.md`（sha `34b39b97…`）：D5 事件有 `available_at=ann_date 20:00`；**权重表本身未赋 available_at**
- 叶26 草稿已写明：合并表「月末点；**无 available_at**」

### 缺口

1. **权重表无 `available_at` 列，亦无 Arch 冻结的 PIT 规则文档**（相对财务/份额流等表）。  
2. 月末 `trade_date` ≠ 披露可得时点：Tushare 月度权重大多滞后于月末；用「当日月末点」asof 可能**前视**（研究级风险未钉阈值）。  
3. 调样窗内（尤其 6/12 月）成员变更日与月末点错位；`index_member_events` 有 PIT 但不能替代日度权重。  
4. 无上证50 / 创指 / 科创50 权重表（见 §2 旁注）→ 草稿主规格外扩 ETF 阻塞。

### 建议来源（研究级；未拉中转）

- **规则草案（待 Arch 审）**：`available_at` = 该月末快照在中证官网/基金公司披露后的保守时点；若无披露时刻证据，可采用「下一自然月首个交易日 09:00 Asia/Shanghai」或「月度片拉取完成时刻 floor」二选一，写进 Data 契约 + 列落地。  
- **证据源**：中证指数公司调样/权重公告（与 D5 同源思路）；Tushare `index_weight` 仅作数值，不单独当 PIT。  
- **短期研究绕行（须在预注册披露）**：继续 `trade_date≤session` 最近月末 asof，并标注 `pit_basis=month_end_snapshot_no_available_at`；**不得**静默当严格 PIT。

---

## 2) 中证1000（000852）权重表

### 现状：本地可取

| 层 | 路径 | 日期范围 | 规模 | sha / 备注 |
|---|---|---|---|---|
| 合并 | `data/v2/index_members/index_weight_csi300_500_1000.parquet`（`index_code=000852.SH`） | 20180131→20260930 | 105 个月末点；105,000 行；`con_code` 唯一约 2435 | 表级 sha 见 §1 |
| 原始 | `data/v2/tushare_raw/index_weight/000852_SH_YYYYMM.parquet` | 201801→202609 非空；**202610 空文件** | 非空 105 片 × 约 1000 行/月；月序列无空洞 | 样例 `weight_sum≈100` |
| 行情面板（非权重） | `data/v2/asof_extend_202610/panels/sz.000852.parquet` 等 | — | 指数日行情，**非**成分权重 | 勿与权重表混淆 |

抽检：`201801/202006/202212/202606/202609` 各 1000 行、单日 `trade_date`、权重和≈100。

### 缺口

1. **同 §1**：无 `available_at`；研究 asof 非严格 PIT。  
2. **202610**：原始片存在但 0 行；合并表止于 20260930 → 当前窗最新月末权重未落地。  
3. 目录内**无** `000016`（上证50）/ `399006`（创指）/ 科创50 对应权重文件（叶26 草稿缺数 #2；主三件套 000852 **本身有数**）。  
4. `promotion_approved`：合并表未在 D5 manifest 中单独钉晋级；按库存惯例视为 **研究级**。

### 建议来源

- 续补：Tushare `index_weight`（index_code=`000852.SH`）月度片 → 重建合并表（需 Arch `.ok` 后方可写生产；本回执不执行）。  
- PIT：与 §1 同规则一并钉，避免 1000 单独口径。

---

## 3) 宽基 ETF↔指数官方映射（含联接基金去重）

### 现状：无 Arch 钉表；仅有文本/benchmark 旁证

| 资产 | 路径 | sha256 | 与宽基映射关系 |
|---|---|---|---|
| 叶26 草稿拟映射（未钉） | `docs/v2/AI_LEAF26_BROAD_ETF_FLOW_STOCK_WHO_PAYS_DRAFT_ZH.md` | `34c1540f…`（见 §0） | 文本：`510300↔000300`、`510500↔000905`、`512100↔000852` |
| `fund_basic`（场内 E） | `data/v2/etf/raw/fund_basic_E.parquet` | `07e0151624b02eefd11c88c0a1de31e6a70db8736c5dd019a73aaab902b66d8f` | 有 `benchmark` 中文串；**无** `index_code` / `tracking_index_code` |
| `etf_basic` | `data/v2/etf/etf_basic.parquet` | `3820cb8683bb00743021d15251f586eb1ce4752700b5e0d0d14c5be5cfdf3122` | `category=宽基` 可筛；仍无官方指数代码列 |
| SW L1 ETF 映射 | `data/v2/etf/sw_l1_etf_map_pit.parquet` | `08cb9b7a702ec6d1b9678f542e8f0aad58546eb1aee42a2aa17b189ed3d899aa` | **行业 L1**；`510300/510500/512100/510050/159915/588000` **均不在表内** |
| 份额流 major | `data/v2/etf/share_pit/etf_share_flow_pit_major.parquet` | `a3eac35b91ae78a9cd152a7e68fb75a9274c6a32a1bfa7550f6ada88c45232bf` | 含 7 只宽基 ETF 代码；**无**映射列；已是 ETF 非联接产品层 |

`fund_basic` / `etf_basic` 中主规格三只的 benchmark 旁证（研究可读，非官方钉）：

| ts_code | name | benchmark（原文） | 拟 index_code |
|---|---|---|---|
| 510300.SH | 华泰柏瑞沪深300ETF | 沪深300指数×100% | 000300.SH |
| 510500.SH | 南方中证500ETF | 中证小盘500指数×100% | 000905.SH |
| 512100.SH | 南方中证1000ETF | 中证1000指数×100% | 000852.SH |

联接基金：`fund_basic_E` 内名称含「联接」且 benchmark/名称触及沪深300/中证500 等约 **7** 条（如 `160706.SZ` 嘉实沪深300ETF联接、`160119.SZ` 南方中证500ETF联接等）。**无**独立「联接→母 ETF / 指数」去重表；major 份额流未纳入这些联接代码（事实排除，非契约）。

全盘未发现 `*broad*etf*map*` / `*etf*index*map*` 落地文件；无 Arch FROZEN 宽基映射。

### 缺口

1. **缺少 Arch 审签的宽基 ETF↔`index_code` 官方映射表**（路径级缺口）。  
2. `benchmark` 为自由文本，不能当唯一键；同指数多 ETF（如 510300 vs 159919）需「主代表 + 是否双计」规则。  
3. **联接去重无契约**：仅靠 major 名单碰巧不含联接；扩到 `etf_share_flow_pit_all` 时会混入联接份额流 → 与母 ETF 双计风险。  
4. SW L1 映射不可复用为宽基映射。

### 建议来源

1. 新建研究表（待 Arch 钉路径/sha），建议列：  
   `etf_ts_code, index_code, index_name, role(primary|secondary), is_feeder, feeder_of, valid_from, valid_to, source, promotion_approved`  
2. 初值：草稿三件套 + 可选 510050↔000016、159915↔399006、588000↔000688（权重表就绪后）；`is_feeder=true` 一律不进叶26 主信号。  
3. 去重规则建议：`name` 含「联接」或 `invest_type`/产品说明书标明联接 → 剔除；或 `is_feeder` 指向母 ETF 后只留母侧份额流。  
4. 证据：基金合同/招募说明书跟踪指数条款 + `fund_basic.benchmark` 交叉校验；中证/上交所产品页。

---

## 4) 汇总

| # | 项 | 本地有数？ | 核心缺口 | 阻塞叶26？ |
|---|---|---|---|---|
| 1 | `index_weight` PIT / available_at / asof | 有月末权重表；**无** available_at 列与冻结规则 | 正式 PIT 契约 + 列落地 | **是**（严格 PIT）；研究 asof 可暂用但须披露 |
| 2 | 中证1000（000852）权重 | **是**（20180131–20260930） | 无 PIT；202610 空；非晋级 | 主三件套**数值不阻塞**；PIT 同 #1 |
| 3 | 宽基 ETF↔指数官方映射 + 联接去重 | 无钉表；仅有 benchmark/草稿文本 | Arch 映射表 + 联接契约 | **是**（冻结前） |

未写生产、未调中转、未改 FROZEN / `.ok`。

---

## 5) 交付

- 本回执路径：`docs/v2/audit/leaf26_20261025/DATA_LEAF26_GAP_INVENTORY_ZH.md`  
- 原子写：先写临时文件再 `mv` 就位。  
