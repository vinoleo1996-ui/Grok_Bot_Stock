# 全 A 宇宙落地核查（Arch，2026-10-14）

- 时间：2026-10-14 ≈07:41 ET
- 依据：Leo（经主 Agent）— 主流多因子 = 每个交易日对**全市场可交易股票**统一算因子、排序、按规则选前几名；已取消「只用 mid_large top300 / 禁小盘」。全 A 只剔除不可交易票；小盘贡献仅披露。
- 约束：本审计**只写文档 / TEAM_STATE**，不改业务主干；`live=false`；`promotion_approved=false`。
- 结论一句话：**声明已切全 A，生产纸面轨与绝大多数权重脚本仍硬绑 mid_large / 静态 2024-06-28 top300；全 A 仅在平行研究路径部分落地，未全员落地。**

---

## 1. 总判定

| 层级 | 是否已全 A | 说明 |
|---|---|---|
| Leo / TEAM_STATE 拍板 | ✅ 声明已切 | `TEAM_STATE_latest.md`「07:24 ET 取消禁小盘」；但同文件「Leo 已拍板」仍写「禁 GP/**小盘**/高杠杆」→ **声明自相矛盾** |
| Strategy 宇宙定义 | ✅ FULLA_V1 已冻结 | `docs/v2/STRATEGY_FULLA_UNIVERSE_PREREG_ZH.md` + `output/strategy_fulla/universe_mask_fulla_v1.parquet`（751 日，日均 ≈4952 只） |
| 纸面轨 capacity_adv / B4 / S6 | ❌ 仍 mid_large | 冻结脚本与 FROZEN_CONFIG 仍读 `mid_large_members_pit` + `select_mid_large_topn_light(anchor=2024-06-28)` |
| capacity_adv 研究全 A 腿 | ✅ 平行产物 | Alpha 已生成 `g1g5_capacity_adv_fulla_v1_*`；**未接入** paper extend / FROZEN_CONFIG |
| earnings / insider / equity_incentive | ⚠️ 脚本有 twin，产物未齐 | `*_weights_fulla_v1.py` 存在；`output/strategy_fulla/legs/` 仅见 capacity_adv，未见 earnings/insider 全 A 权重 |
| 叶11–15 / 多数 G1G5 叶 | ❌ 仍 mid_large | 22 个 `g1g5_*_weights.py` 无 fulla twin；自检/组合边际仍 top300 |
| broker_gold_new（叶16） | ✅ 全 A 主口径 | `BGN_POOL` 默认 `all_a`；mid_large 仅对照 |
| 硬闸 / factor_evolve / trading_loop | ❌ 仍禁小盘 / 仅 mid_large_stock | `ALLOWED_UNIVERSE` 不含全 A；stub 文案仍「禁小盘主仓」 |
| Data 池表 | ⚠️ 旧池仍在产且被用 | `mid_large_*` 日更继续；**无**官方全 A PIT 表（掩码在 research 侧） |
| book_smoke | ◯ 中性 | 消费传入权重表，自身不选池；当前纸面权重仍来自 mid_large 腿 |
| alpha_decay_gate | ◯ 中性 | 不直接选池；上游权重/自检宇宙决定口径 |

**总评：未全员落地。** 策略定义与个别新叶已全 A；**生产纸面轨、叶验收自检、硬闸、绝大多数权重脚本**仍违规（相对 Leo 新规矩）。

---

## 2. 仍硬绑 mid_large / top300 / 静态锚 / 禁小盘的代码与配置

### 2.1 生产纸面轨（P1 — 与 Leo 新规矩直接冲突）

| 文件:行 | 问题 | 负责 |
|---|---|---|
| `research/capacity_adv_paper_extend.py:35,135-143` | 导入冻结腿 `g1g5_capacity_adv_weights`；续出依赖 `mid_large_universe` 新鲜度 + `mid_large_members_pit` + `select_mid_large_topn_light` | Eng / AI |
| `research/g1g5_capacity_adv_weights.py:49,61,545` | 纸面核心腿：候选池 = mid_large top-N（非全 A） | AI（腿）/ Eng（纸面接线） |
| `output/loop/capacity_adv_FROZEN_CONFIG.json`（`mid_large_members_pit` 路径与 sha） | 冻结配置钉死 mid_large | Eng |
| `research/b4_paper_extend.py:38-40,258` | TRACK/LEG 脚本列表指向 mid_large capacity_adv；状态带 `mid_large_universe` | Eng / Strategy |
| `research/s6_paper_extend.py:36` | 依赖 `g1g5_capacity_adv_weights` / `earnings_event_weights` / `equity_incentive_weights`（均为 mid_large 原版） | Eng / Strategy |
| `quantlab/portfolio/paper_track.py:18` | 纸面脚本清单含 mid_large 腿 | Eng |
| `quantlab/portfolio/b4_paper.py:33,294` | 同上 | Eng |
| `quantlab/portfolio/research_loop.py:376,398,633` | `REQUIRED_TABLES` / 切片含 `mid_large_universe` / `mid_large_members_pit` | Eng |

### 2.2 静态锚 2024-06-28（P1 — 前视 + 非逐日全市场）

| 文件:行 | 问题 | 负责 |
|---|---|---|
| `research/g1g5_expand_g6.py:56,80-116` | `ANCHOR_SESSION = "2024-06-28"`；`select_mid_large_topn` 按锚点一次取 top-N | AI |
| `research/g1g5_d1_val_resid_weights.py:93-96`（及 accrual/margin/moneyflow/northbound 等同构副本） | `select_mid_large_topn_light(..., anchor="2024-06-28")` 默认静态池 | AI |
| `research/g1g5_earnings_event_weights.py:8,41,84` | docstring + `UNIVERSE_ID=g1g5_mid_large_top300_event` + `select_mid_large_topn_light` | AI |
| `research/g1g5_insider_increase_weights.py:8,41,85` | 同上 insider | AI |
| 多数 `research/g1g5_*_weights.py`（见 §3 清单） | 同源 `mf.select_mid_large_topn_light` / `mid_large_members_on` | AI |

### 2.3 自检 / 组合边际（P1 — 验收口径仍 top300）

| 文件:行 | 问题 | 负责 |
|---|---|---|
| `research/leaf_selfcheck_v3.py:87` | 残差宇宙 `select_mid_large_topn_light(top_n=300)` | AI / Alpha |
| `research/alpha_combo_marginal.py:6,30` | 明确「anchor top300 ∩ mid_large」 | Alpha / AI |

### 2.4 硬闸与 agent 契约仍禁小盘（P1 — 与「取消禁小盘」冲突）

| 文件:行 | 问题 | 负责 |
|---|---|---|
| `quantlab/agents/factor_evolve/hard_gates.py:17,30-31,93` | `ALLOWED_UNIVERSE` 仅 `mid_large_stock`+ETF；`_SMALLCAP_RE` → `smallcap_main_banned` | AI / 主 Agent（政策） |
| `quantlab/agents/factor_evolve/schemas.py:8` | `UniverseKind` 无 `all_a` / `fulla_v1` | AI |
| `quantlab/agents/factor_evolve/run_stub.py:92+` | stub 一律 `universe_kind=mid_large_stock` | AI |
| `quantlab/agents/trading_loop/state_machine.py:69,115` | 「禁小盘主仓」 | Strategy / Beta |
| `quantlab/agents/trading_loop/schemas.py:44,75` | 同上默认文案 | Strategy / Beta |
| `docs/v2/ALPHA_LEAF_ACCEPT_V2_PREREG_ZH.md`（约束段） | 仍写「只做中大盘（mid_large_members_pit）」 | Alpha / 主 Agent |
| `research/g1g5_wiring.py:70-71` | `UNIVERSE_ID/KIND = mid_large_*` | AI |

### 2.5 Data 旧池仍在用（P2 — 对照可留，但不可当主池）

| 文件/表 | 问题 | 负责 |
|---|---|---|
| `data/v2/universe/mid_large_members_pit.parquet` | 日更至 2026-10-14；纸面轨仍**主用** | Data（产）/ Eng+AI（消费） |
| `data/v2/universe/mid_large_month_end_anchor_pit.parquet` | Data 为 Arch #8 交付的月度全成员+rank；**未被纸面主路径切换为全 A** | Data |
| `data/v2/universe/mid_large_top300_monthly_pit.parquet` | 月度 top300；`g1g5_broker_gold_new_weights.py:68` 在 `POOL=mid_large` 对照时读；`broker_gold_new_count.py` 仍读 | Data / AI |
| `scripts/acquire/mid_large_universe_incr.py` + `scripts/nightly_update.py` | 夜间强制 mid_large 增量；新鲜度闸依赖它 | Data / Eng |
| `scripts/acquire/ref_tables_20261014.py:34-49` | 生成 month_end_anchor / top300_monthly | Data |
| `data/v2/ref/stock_delisted.parquet` | Data 已交付；**全 A 掩码未直接消费**（掩码用 stock_basic L/D/P + daily）；Beta 幸存者用 `delisted_master_tushare` | Data / Beta |

---

## 3. 关键路径「实际读哪个池」

| 路径 | 实际宇宙 | 证据 | 是否符合 Leo 全 A |
|---|---|---|---|
| **capacity_adv 纸面** | mid_large 静态锚 top-N + 日度 PIT 成员过滤 | `capacity_adv_paper_extend` → `g1g5_capacity_adv_weights` + FROZEN_CONFIG | ❌ |
| **capacity_adv FULLA 研究腿** | FULLA_V1 掩码 PIT | `g1g5_capacity_adv_weights_fulla.py`；产物在 `output/strategy_fulla/legs/` | ✅（未接纸面） |
| **earnings_event 原版** | mid_large top300 @2024-06-28 | `g1g5_earnings_event_weights.py:8,84` | ❌ |
| **earnings_event fulla_v1** | `select_fulla_v1` | `*_fulla_v1.py` 存在；**未见** strategy_fulla 权重产物 | ⚠️ 脚本✅ 产物❌ |
| **insider_increase** | 同上双轨 | 原版 mid_large；fulla twin 无产物 | ⚠️ |
| **B4 纸面** | 合成 mid_large 腿（50/25/25） | `b4_paper_extend` LEG_SCRIPTS → mid_large capacity 等 | ❌ |
| **S6 影子** | 同上依赖 mid_large 腿列表 | `s6_paper_extend.py:36` | ❌ |
| **leaf_selfcheck** | top300 做残差宇宙 | `leaf_selfcheck_v3.py:87` | ❌ |
| **alpha_decay_gate** | 不选池；吃上游权重/自检 | 无直接 mid_large 硬绑 | ◯（被上游拖累） |
| **book_smoke** | 权重表驱动 | `quantlab/portfolio/book_smoke.py` | ◯（当前输入仍旧池） |
| **权重生成（多数叶）** | mid_large | 见下「MID_LARGE_ONLY」22 个 | ❌ |
| **broker_gold_new** | 默认 `all_a`（`all_a_universe_mask`） | `g1g5_broker_gold_new_weights.py:37,82-83` | ✅ |

### 权重脚本盘点（`research/g1g5_*_weights.py`）

- **已有 fulla twin / 内联全 A（7）**：`capacity_adv`（twin）、`earnings_event`、`insider_increase`、`equity_incentive`、`insurer_surv`、`report_rc_allup`、`broker_gold_new`（内联 `all_a`）。
- **仍仅 mid_large（22）**：`accrual_quality`、`analyst_recoverage`、`block_trade`、`buyback_cancel`、`capacity_adv_negevent`、`d1_val_resid`、`etf_core_sleeve`、`friction_cost_redesign`、`idx_rebal_flow`、`idx_rebal_predict`、`indcap_momneut_ocf`、`industry_etf_rotation`、`interim_div_init`、`low_turnover`、`margin_delta`、`moneyflow_resid`、`nontextbook`、`northbound_flow`、`resid_etf`、`stk_surv`、`tp_rerate`、`unlock_rebound`。

---

## 4. 声明 vs 代码一致性

| 来源 | 声明 | 代码现实 | 一致？ |
|---|---|---|---|
| TEAM_STATE「07:24 取消禁小盘；全A只剔除不可交易」 | 全 A | 纸面/硬闸/多数叶仍 mid_large | ❌ |
| TEAM_STATE「Leo 已拍板」仍列「禁…小盘…」 | 禁小盘 | 与上条冲突 | ❌ 文件内自相矛盾 |
| Strategy 小节 FULLA_V1 冻结 | 研究宇宙已定；**不改** FROZEN/纸面 | 与预注册一致 | ✅（但意味着生产未切） |
| Alpha 小节 capacity_adv FULLA 腿已生成 | 平行产物；FROZEN 未动 | 与代码一致 | ✅ |
| AI 小节 叶16 全 A 主 / mid_large 对照 | 全 A 主 | `BGN_POOL` 默认 all_a | ✅ |
| AI_LEAF_LEDGER 叶16 | 全A 主/mid_large 对照 | 一致 | ✅ |
| ALPHA_LEAF_ACCEPT_V2_PREREG | 只做中大盘 | 与 Leo 新规矩冲突，**过时** | ❌ |
| Data 月度锚回执 | 给 mid_large 月度 top300 | 表存在且被对照路径使用；**不是**全 A 主池 | ✅ 就交付目标而言；❌ 相对新主口径 |

---

## 5. 可交易过滤（ST / 停牌 / 上市<60日 / ADV@100万）

| 过滤 | 是否实现 | 位置 | 备注 |
|---|---|---|---|
| ST/*ST | ✅ | `research/all_a_universe_mask.py:64-73,99`；`strategy_fulla_universe_v1.py` 同源 | namechange 派生区间 |
| 停牌 | ✅ | 同文件：`suspend_d` suspend_type=S 或 S-1 无 bar | |
| 上市不足 60 交易日 | ✅ | `MIN_LIST_SESSIONS=60`；list_date→S-1 | |
| ADV 可交易（100万档） | ⚠️ 两套阈值 | `all_a_universe_mask`：NAME_CAP=**4%** → ADV20≥**200万**元；`strategy_fulla_universe_v1`：NAME_CAP=**6%** → ADV20≥**300万**元 | **P1 口径分裂**；Strategy 预注册以 FULLA_V1=300万为准，broker_gold 默认走 all_a=200万 |
| 北交所剔除 | ✅ | 仅 `.SH/.SZ` | |
| 小盘剔除 | ✅ 已取消 | FULLA/all_a **不**按市值砍 | 符合 Leo |
| mid_large 路径上的过滤 | 部分 | mid_large 规则自带中大盘；**不是**「全市场再过滤」 | 不合新规矩 |

Data `stock_delisted`：Beta 幸存者偏差在用；全 A 掩码靠 daily 有 bar + stock_basic，**未**显式 join `ref/stock_delisted.parquet`（退市票若无近期 bar 会自然不进池，但与官方退市表对齐建议补审计）。

---

## 6. Data 三交付使用状态

| 交付物 | 谁在用 | 是否主路径全 A |
|---|---|---|
| `mid_large_month_end_anchor_pit` | 主要为 Arch #8 / 对照；纸面主腿仍用**单日静态锚** `select_*_light(anchor=2024-06-28)`，**甚至未切到该月度表** | ❌ 旧池；且纸面连月度 PIT 都没用上 |
| `mid_large_top300_monthly_pit` | `broker_gold_new` 对照池；`broker_gold_new_count.py` | ❌ 旧池（对照 OK） |
| `stock_delisted`（`data/v2/ref/` + `delisted/*`） | Beta `survivorship.py`；小盘历史脚本 | 非选股主池；全 A 掩码未直接消费 |

**已切全 A 的消费端**：`research/all_a_universe_mask.py` / `strategy_fulla_universe_v1.py`（自建掩码，不读上述 mid_large 三表）。

---

## 7. 建议（按优先级，不改主干——仅派工）

1. **主 Agent**：统一 TEAM_STATE——删掉「禁小盘」与「取消禁小盘」并存；明确「生产纸面轨切换」是否另需拍板（Strategy 预注册写明暂不改 FROZEN）。
2. **Strategy**：裁定 ADV 阈值（200万 vs 300万）唯一；确认 B4/S6 是否在 FULLA 腿齐后重合成并跑 Eng X2（预注册已规划）。
3. **AI**：  
   - 把 `earnings_event` / `insider_increase` / `equity_incentive` / 叶11+14 的 fulla 脚本**跑出产物**落到 `output/strategy_fulla/legs/`；  
   - 新叶默认 `FULLA_V1` 或 `all_a_universe_mask`，mid_large 仅对照；  
   - 修 `hard_gates` / `UniverseKind` 允许 `fulla_v1`/`all_a_tradable`，去掉与 Leo 冲突的 smallcap 主禁（或改为「仅披露小盘贡献」）。
4. **Eng**：纸面切换需**新冻结包**（勿静默改现行 FROZEN）：`capacity_adv_paper_extend` / freshness `REQUIRED_TABLES` / pin；在切换前保持 mid_large 纸面 + 全 A 研究轨并行。
5. **Alpha**：`leaf_selfcheck_v3` / `alpha_combo_marginal` 残差宇宙改 FULLA 掩码；叶验收预注册去掉「只做中大盘」。
6. **Data**：可选交付 `all_a_tradable_members_pit.parquet`（与 Strategy 掩码同规则），供新鲜度闸与夜间任务；`mid_large_*` 保留作对照；全 A 掩码对齐 `stock_delisted` 做一次交叉审计。
7. **Beta**：trading_loop 文案去「禁小盘主仓」；幸存者继续用 delisted 表。

---

## 8. 已全 A vs 未全 A（汇报摘要）

**已全 A（或平行研究已落地）**  
- Strategy FULLA_V1 定义 + 掩码  
- Alpha capacity_adv FULLA 腿（研究）  
- AI 叶16 broker_gold_new（默认 all_a）  
- 若干 `*_fulla_v1.py` 脚本（earnings/insider/eqincent/insurer/report_rc）— **脚本层**

**未全 A（须修）**  
- 纸面 capacity_adv / B4 / S6 及 FROZEN_CONFIG  
- 原版 capacity/earnings/insider 及 22 个无 twin 的权重脚本  
- leaf_selfcheck / alpha_combo_marginal  
- factor_evolve 硬闸与 trading_loop「禁小盘」  
- ALPHA_LEAF_ACCEPT 预注册文案  
- TEAM_STATE 拍板段自相矛盾  
- Data 无全 A 主池表；月度 mid_large 锚也未接到纸面主腿  

**负责修（主责）**  
- 政策/TEAM_STATE：主 Agent  
- 宇宙口径/ADV/B4 合成：Strategy  
- 腿与硬闸：AI  
- 纸面冻结与新鲜度：Eng  
- 自检/验收预注册：Alpha  
- 可选全 A PIT 表 + 退市对齐：Data  
- 风控文案：Beta  

live=false；本文件仅审计，无代码变更。
