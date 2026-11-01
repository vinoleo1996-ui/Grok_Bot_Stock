# Arch：叶26 契约预告（宽基 ETF 资金流→个股 who_pays；**不签 .ok**）

- 角色：QuantLab Arch
- 时刻（America/New_York）：2026-10-25T07:04:08-04:00
- 主规格（**DRAFT r2，未冻结**）：`docs/v2/AI_LEAF26_BROAD_ETF_FLOW_STOCK_WHO_PAYS_DRAFT_r2.md` sha256 `0b55bfeb3b033da4715e4dbc5c996e92b954fc10e385c10b308da992d87a60b5` **MATCH**
- Data 缺口回执：`docs/v2/audit/DATA_LEAF26_ETF_FLOW_GAP_RECEIPT_20261025_ZH.md` sha256 `aaf84d66ececa313a371020cd0ae0f4ce5092902849b89b5b6dea79867b4e859` **MATCH**
- Strategy 袖套：`docs/v2/STRATEGY_ETF_FLOW_SLEEVE_PLAN_20261025_ZH.md` sha256 `7722efec9f750ec89b2047d5890a39a119771eb86c8fb35bc265217b82286091` **MATCH**
- 旧盘点旁证（不覆写）：`docs/v2/audit/leaf26_20261025/DATA_LEAF26_GAP_INVENTORY_ZH.md` sha256 `c03a9f0e4c9c7622cd0dc0be36de2aaada70f9dacc48921156c89f640125b305` **MATCH**
- Intel 清单：`output/intel/ETF_FLOW_PIT_CANDIDATES_latest.md` sha256 `ca0351595f7a2ae4bd0c2367a510cd2012626a1d76613db517df7108937d886c` **MATCH**
- **本轮不签任何 .ok**（叶26 / 叶25 / 叶27 / 补跑 / moneyflow 新签一律不签）
- **不挡叶25**：窗 10:00–10:45 ET；现盘 `.ok` sha8 `7b279d47`（全长 `7b279d4731760de3c6b194b1d5d93e47acfc5607fa5d05f1defbd5dce07e31a7`）
- **叶27**：窗前仍不签 `.ok`（条件3路径 sha 另窗）；与本预告正交
- live=false；`promotion_approved=false`；research_only=true
- **本预告 ≠ 授权跑 / 授权预注册 / 授权 IMPL**

## 0. 研究边界（对照 r2；Arch **不改**主规格正文）

| 项 | 研究级边界（摘 r2 / Strategy） |
|---|---|
| mechanism_tag | `g1g5_ashare_broad_etf_flow_stock_v1`（叶26） |
| who_pays | 宽基 ETF 产品层份额流→篮子权重→个股冲击对手；**不是**个股 `net_mf_amount` / moneyflow_resid；不是 etf_core 持仓差 |
| 主规格 ETF 池 | **仅** `510300.SH→000300.SH` 与 `510500.SH→000905.SH` |
| **默认剔除** | `512100.SH` / `000852.SH`（与 Strategy 袖套默认池对齐） |
| 禁 | 个股 moneyflow 主轴；etf_core 双计；静默称严格 PIT；擅自扩池至 512100 |
| 残差（预告级） | SW L1 + log 流通市值 +（披露）vs capacity_adv / moneyflow_resid；主交付 α 向量 |
| 敏感性支路 | 000852/512100 / premium / hk_hold / 美 ETF：**另签**；不得 silently 并入主规格 |

## 1. 数据契约表（OK / PARTIAL / GAP；研究级允许路径）

依据：Data 回执 `aaf84d66ececa313a371020cd0ae0f4ce5092902849b89b5b6dea79867b4e859`；r2 `0b55bfeb3b033da4715e4dbc5c996e92b954fc10e385c10b308da992d87a60b5`。**签 `.ok` 前须重钉路径 full sha**（本预告只钉研究推荐，不钉实现 sha）。

| # | 项 | 状态 | 研究级允许路径 / 绕行 | 签 `.ok` 前 |
|---|---|---|---|---|
| 1 | 宽基份额流（主输入） | **OK**（研究级） | `data/v2/etf/share_pit/etf_share_flow_pit_major.parquet`（含 510300/510500；`available_at`；份额次日 09:00 规则见 manifest） | 重钉表 sha + asof 规则 |
| 2 | `index_weight` PIT / `available_at` | **GAP** | 合并表 `data/v2/index_members/index_weight_csi300_500_1000.parquet` 有数值至 20260930；列无 `available_at`；研究可 `trade_date≤session` 最近月末 + 披露 `pit_basis=month_end_snapshot_no_available_at` | 正式 PIT 须 Arch+Data 共签落列；或预注册明示接受 `pit_basis` 披露 |
| 3 | 000852 / 512100 权重 | **PARTIAL**（主规格剔除） | 合并表内 000852 至 20260930；202610 空；**r2 默认不依赖** | 敏感性支路须 Strategy+Data 共签 + 预注册 bump |
| 4 | 宽基 ETF↔指数映射 | **PARTIAL**（无钉表） | **硬编码** `510300.SH↔000300.SH`、`510500.SH↔000905.SH`（对齐 r2/Strategy）；`fund_basic` 仅旁证 | 扩池/联接去重须 Arch 映射表（建议列见 Data 回执 §3.2） |
| 5 | 北向市场净流入（生态） | **OK**（研究级；非主轴） | `data/v2/northbound/moneyflow_hsgt_daily_2014plus.parquet`（有 `available_at`） | 非 r2 主轴；若入对照须重钉 sha |
| 6 | `hk_hold` 密窗 | **GAP** | 表有 `available_at`；密日频止 **20240816**；其后仅季末点；**2024-08-16 后勿当日频** | 续密窗须 Arch `.ok` 后方可写生产；**不阻塞** r2 主规格 |
| 7 | premium PIT | **GAP** | 无现成 premium 表；可研究拼装 `etf_daily_adj` ⋈ share `unit_nav`（asof=两表 `available_at` max）；**本预告不落地** | Intel/敏感性另裁；非 r2 主轴 |
| 8 | 美 ETF PIT | **GAP** | `data/v2` 未见带 `available_at` 的美股 ETF parquet；仅 ALERTS 快照旁路 | 另签时区规则后落表；非 r2 主轴 |
| 9 | `hsgt_top10` catalog | **PARTIAL** | 文件至 20261016 可用；manifest `date_range`/内嵌 sha **漂移**；消费侧以**文件**为准 | catalog 校准不阻塞主规格 |

### 1.1 明确 GAP（签正式预注册 / `.ok` 前须面对）

1. **`index_weight` 无 `available_at`** — 阻塞「严格 PIT」声称；研究级可绕（披露 `pit_basis`），正式冻结前须 Arch 接受披露或落列。  
2. **宽基映射无 Arch 钉表** — 研究级两对硬编码可绕；**扩池硬阻塞**。  
3. **`hk_hold` 密窗** — 阻塞 Intel `nb_hold_*` 当日频特征；**不**阻塞 r2 主轴。  
4. **premium PIT 无** — Intel P0；r2 主推份额流非折溢价。  
5. **美 ETF PIT 无** — Intel 可选外生；非 r2 主轴。

**GAP 计数（契约表明确 GAP 行）**：**4**（#2 index_weight PIT；#6 hk_hold；#7 premium；#8 美 ETF）。另 3 项 PARTIAL（000852/映射/hsgt_top10 catalog）。

## 2. Arch 条件（预告级；非授权）

1. **正式 PIT / 扩池映射另裁**：权重 `available_at` 规则、ETF↔指数官方映射表、联接去重契约 —— 须独立 Arch+Data（±Strategy）裁示后落盘；**本预告不代替**。  
2. **本预告 ≠ 授权跑**：不授权预注册冻结、不授权脚本 DIFF/IMPL、不授权实数据/生产写、不授权 X2/Book-Smoke。  
3. **禁消费补跑** `.ok` sha8 `9e4359f9`（全长以现盘为准；Arch CONSUME_SUSPEND 仍有效）。  
4. **禁复用**叶25 / 叶27 `.ok` 钉签本叶。  
5. 研究级主规格推进若开：预注册首页必须 MATCH 本预告 + Data 回执 full sha，并披露 `pit_basis`；默认池不得 silent 纳入 512100/000852。

## 3. 非动作（本预告）

- **不签**叶26 / 叶25 / 叶27 任何 `.ok`；不签自检 / X2 / Book-Smoke  
- **不挡**叶25（`7b279d47` @ 10:00–10:45 ET）；**不挡**叶27 窗后另窗签  
- 不改 `research/`；不改 r2 正文；不 git commit；不写 `data/v2`  
- 不消费补跑 `9e4359f9`；不拉外网/中转  
- live=false

## 4. 下一步（供主裁，非本轮执行）

1. **主裁**：是否开叶26 预注册 / IMPL 窗（建议：叶25 闭后；与叶27 `.ok` 窗错开）。  
2. **AI**：等主裁开窗后再交预注册 r1（须钉池=仅 510300/510500；披露 `pit_basis`；首页引 Data `aaf84d66…` + 本预告 sha）。  
3. **Data**：权重 `available_at` 规则草案 / catalog 校准按需；**禁**本预告触发拉数。  
4. **Arch**：预注册/DIFF 另窗审；**本轮仍不签 .ok**。  
