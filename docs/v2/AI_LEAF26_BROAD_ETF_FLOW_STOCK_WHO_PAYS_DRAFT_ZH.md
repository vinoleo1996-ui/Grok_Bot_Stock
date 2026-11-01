# 【DRAFT — NOT FROZEN】叶26 who_pays：ETF 资金流（宽基→成分暴露）· 填 Alpha「叶候选 1」空位

- 起草/对齐：QuantLab AI，2026-10-25 约 04:41 ET（America/New_York）。
- **对齐权威**：`docs/v2/ALPHA_NEXT_ORTHO_LEAF_DEFS_20261025_ZH.md`（文件 sha256 `20c031c911c46e7e61d09f9f811616f066b93a0122900f3b85ce2076f6a14605`；正文尾栏自报 `d8672752…`）。本文件填写其中 **「叶候选 1 · ETF 资金流」who_pays 空位**；定义所有权仍在 Alpha。
- 状态：**DRAFT**。未冻结、未开叶、未消费任何 `.ok`、未读收益、未跑 X2。live=false；promotion_approved=false；research_only=true。
- 叶号：台账至叶25；占用 **叶26**。与叶25 抢资源时 **叶25 优先**（本任务只交预研文档）。
- 禁：卖方/金股/一致预期/调研；禁 GP；禁空头腿；**禁个股 moneyflow 换皮**；禁 etf_core overlay 双计；禁无 PIT 成分；禁改 FROZEN。

---

## 0. Alpha 空位填写（交 Alpha 用·可整段摘抄）

> **mechanism_tag**：`g1g5_ashare_broad_etf_flow_stock_v1`（叶26）  
> **who_pays（一句）**：付钱的是在宽基 ETF 大额申赎日、忽视「ETF 产品层份额流→篮子权重」传导而承接 AP 机械买卖冲击的个股定价对手——**不是**个股 `net_mf_amount` / moneyflow_resid 对手盘，也不是直接持有 ETF-core 的配置差对手盘。  
> **可检验预测**：在 HIT 口径下，经 §3 残差化后的 ETF 流量暴露 α，对次日（T+1）特质收益的截面 IC 符号在预注册冻结时写死（本 DRAFT 不读收益选号）；且活跃集 vs moneyflow_resid / etf_core / resid_etf / idx_rebal_flow / capacity_adv 的 Jaccard 均 ≪0.7 且 frac(J≥0.7)=0。  
> **失效条件**：主信号一旦混入个股 D2 moneyflow；或退化成直接持有 ETF≈0.70；或与 moneyflow_resid 近等权（Jaccard≥0.7）；或无 PIT 成分/权重；或 A/A′ 不过 → DONE_FAIL / 拒开 X2。  
> **交 Alpha 时点**：正式预注册冻结 + Arch 审过脚本 + 新窗 `.ok` 跑完 X2 回执之后；**现在**只交本 DRAFT 供 Alpha 确认空位已填，不申请 ACCEPT。

---

## 1. 机制（对齐 Alpha「机制一句话」）

ETF **份额增减 / ETF 端资金流**刻画**产品层再配置压力**向成分股的传导；对手盘是忽视 ETF 被动/半被动流量的个股定价。

展开（本叶主规格）：默认用宽基 ETF（`510300.SH`↔`000300.SH`，`510500.SH`↔`000905.SH`，`512100.SH`↔`000852.SH`）的 PIT `d_share_wan` / `flow_est_wan_yuan`，经指数权重 as-of 映射为个股暴露，再按 §3 残差化 → 日度 **α 向量**（非 Top-N 主交付）。

**明确不是**：
- 个股 `data/v2/moneyflow/moneyflow_stock_daily_pit.parquet` 主轴（= moneyflow_resid 换皮 → **硬拒**）
- 直接持有行业/宽基 ETF≈0.70（= etf_core_sleeve）
- 行业 ETF 申赎流交易 ETF 本身（叶4 FAIL；叶8a 同构 FAIL）——本叶评分对象是**股票暴露**
- 调样公告事件窗（idx_rebal_*）
- 份额流×旧残差构（resid_etf）
- 应计/质量（叶19 / 叶25；Alpha 候选 3 不派本轮产权）

行业 ETF 流量→行业/成分映射：Alpha 槽位允许「宽基/**行业** ETF」，但行业 ETF→**持有 ETF** 路径已败；若后续扩行业臂，必须仍是**流量→股票/行业暴露 α**，不得回到持有 ETF-core。本 DRAFT 主规格先钉**宽基三件套**，降低同构风险。

---

## 2. who_pays（正文）

在宽基 ETF 净创设（赎回）冲击日，AP 按官方权重机械买（卖）篮子；个股侧若仍按「无产品层流量」定价，则高权重名承受非信息性冲击。本叶 α 试图系统性站在该冲击的可预测一侧。付钱的是上述误定价/流动性承接对手，**不是**财报应计对手，**不是**个股主力净流入叙事对手。

---

## 3. 残差化清单（逐条对齐 Alpha 候选 1）

同日截面，缺任一层记 **GAP**，不得静默跳过：

1. **原始**：ETF 份额 Δ 或资金流强度（`available_at≤session`）→ 映射到股票暴露  
   `α_raw,i = Σ_etf w(i, index(etf), asof) × z_etf`  
   `z_etf` = trailing 标准化的 `d_share_wan` 或 `flow_est_wan_yuan`（主规格只留一个；窗长冻结时钉）
2. **SW L1 demean**
3. **vs log 流通市值 OLS 残差**
4. **vs 滚动β**（市场或 510300；定义冻结时钉）
5. **vs capacity_adv 暴露/活跃指示**再正交一层
6. **披露** vs moneyflow_resid / etf_core / resid_etf / idx_rebal_flow 的 Jaccard 与残差 ρ（不作调参）

方向（高申购暴露优先 vs 高赎回后反转优先）**仅在预注册冻结时写死**；禁止用密封/X2 挑方向。

---

## 4. 正交硬闸（Alpha 共用 + 本叶）

- 相对 capacity_adv 与已 RESEARCH_ACCEPT/WATCH 腿：活跃集 Jaccard **均≪0.7** 且 **frac(Jaccard≥0.7)=0**；须报残差 ρ；伪耦合（ρ 高且叠加≈加权和）→ CMC 不得 PASS。
- vs **moneyflow_resid**：机制必须是 **ETF 产品层**；个股 moneyflow **不得进主信号**（可作披露对照）。
- vs **etf_core**：不得退化成直接持有 ETF≈0.70。
- vs **resid_etf / idx_rebal_flow**：禁份额流×残差旧构、禁调样事件窗换皮。
- vs 叶4 / 8a：禁「交易行业 ETF / 同数据同方向少过滤」。

---

## 5. Universe 双轨与快慢标签

| 口径 | 角色 |
|---|---|
| FULLA_V1 | 研究 |
| HI_LIQ_V1.1 | 纸面主闸 |

掩码意图：`output/strategy_fulla/universe_mask_fulla_v1.parquet`、`output/strategy_hiliq/universe_mask_hiliq_v1.parquet`。

**快慢标签（验收门 C）**：ETF 份额流多为 **日/周（偏快）**；与 moneyflow_resid 慢袖错配检查必做（Alpha 门 C）。主交付仍为 α 向量。

验收路径意图：A/A′（ETF 流量残差 IC/ICIR + 特质α）→ B（中性后相对 capacity_adv）→ C（快慢）→ CMC / GATE_V3；过门后才可议 Book-Smoke。研究级至少 A+A′。

---

## 6. 数据可用性（只读 schema；未跑全量因子）

| 路径 | 存在 | 角色 | 列名级要点 |
|---|---|---|---|
| `data/v2/etf/share_pit/etf_share_flow_pit_major.parquet` | 是 | 宽基份额流主表 | `ts_code,trade_date,fd_share,unit_nav,adj_nav,share_wan,d_share_wan,flow_est_wan_yuan,*_available_at,available_at`；含 510050/300/500、512100、159915、588000、159919 |
| `data/v2/etf/share_pit/etf_share_flow_pit_all.parquet` | 是 | 扩样本/校验 | 同上；manifest：share `available_at`≈次交易日 09:00 |
| `data/v2/index_members/index_weight_csi300_500_1000.parquet` | 是 | 成分权重 as-of | `index_code,con_code,trade_date,weight`；仅 000300/000905/000852；**月末点**；**无 available_at** |
| `data/v2/etf/share_pit/ind_etf_share_flow_by_sw_l1.parquet` | 是 | **不作主轴**（叶4/8a 对照） | 行业聚合流 |
| `data/v2/moneyflow/moneyflow_stock_daily_pit.parquet` | 是 | **禁主轴**；仅正交披露 | `net_mf_amount` 等 |
| `data/v2/index_members/index_member_events.parquet` | 是 | **禁主轴**（调样） | 含 `available_at` |
| `data/v2/tushare_raw/daily/*.parquet` | 是 | 非本叶主轴（属候选 2） | open/pre_close/close 可拆隔夜日内 |
| `data/v2/bars/daily_ohlcv_raw_pit.parquet` | 是但仅约 12 日 | 不可用全历史 OHLC | — |
| float_mktcap / SW L1 / 双宇宙 mask | 是 | 残差与宇宙 | 消费须沿用近叶 asof |

多表 `promotion_approved=false` → 研究可用，非晋级授权。

---

## 7. 缺数清单（问 Data；阻塞冻结不阻塞本 DRAFT）

1. `index_weight_*` **PIT / available_at** 规则（现仅月末 `trade_date`）。  
2. 上证50 / 创指 / 科创50 权重 PIT（否则 510050/159915/588000 不进主规格）。  
3. ETF↔指数映射表是否 Arch 已钉（拟 510300↔000300、510500↔000905、512100↔000852；联接基金去重）。  
4. major 与 all 的 `available_at` 时区/次日 09:00 约定是否同源。

---

## 8. 密封窗 / X2 意图

- 密封 / X2 日期对齐近叶习惯，**冻结时硬钉**；密封窗只在 X2 全硬闸通过后读 **一次**。  
- 不复用叶25 窗；本叶另申 Arch `.ok`。  
- 输出：**α 向量**；Top-N 仅披露。

---

## 9. 预计进度（相对时钟）

| 里程碑 | 预计 |
|---|---|
| 本 DRAFT（填 Alpha 空位） | **已完成** |
| Data 答复 §7 | 发出后 +0.5～1 工作窗 |
| 正式预注册 r1 → Arch | 缺数补齐后 +1 工作窗 |
| 交 Alpha 验收闸 | 冻结 + 新窗 `.ok` + X2 回执后；叶25 优先 |

---

## 10. 备选（不立项、不填 Alpha 候选 2/3 产权）

- 候选 2 overnight−intraday：价量公式可做，但与叶18/18v/24 同族、试验预算紧；且须禁「精神/情绪」叙事。  
- 候选 3 质量应计：Alpha 默认叶25 未出闸前 **不派 AI 产权**。

---

## 11. 阻塞

§7 缺数 1–3；叶25 10:00 窗优先；本叶无 `.ok`。未更新 TEAM_STATE；无 git commit。

---

## 12. FROZEN

（空 — DRAFT）
