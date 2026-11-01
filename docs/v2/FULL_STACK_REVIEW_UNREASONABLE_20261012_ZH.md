# QuantLab 全仓复盘：不合理之处（2026-10-12）

**作者**：Grok Bot（executor）  
**范围**：`/workspace/QuantLab` 架构文档 + 核心回测/组合/成本/PIT + 策略层 MAINBOOK/袖套/已拒臂模式  
**约束**：对照个股+ETF 主线、禁小盘主仓、L≤1.5（FUT-RP L3 仅对照）、AUM 60万∧100万、`promotion_approved=false` 直至密封；**不建议恢复小盘主线**；不启动冒烟；不改业务代码。  
**状态**：研究级诚实复盘 · 非晋级结论

---

## 0. 一句话总判

平台层（执行引擎、涨跌停「只挡成交不改估值」、E1 对账、PIT `available_at` 纪律）多数方向正确，且 2026-10-10 起修过致命「涨跌停持仓收益记 0」；  
**真正不合理的是：正式 Mandate / 草案 / AGENTS / 默认真书代码彼此打架，主线「个股+ETF」在账本里仍是空袖套，而研究产能被烧在「完整 X1（2015–17）事件臂」上——该闸与多数事件表自 2018 起才有的现实硬冲突，再叠加硬禁同构膨胀，搜索空间自我塌缩（V35 coverage_blocked）。**  
因此近期 V30–V34「全挂」不全是运气差，有系统性流程/目标设计问题。

---

## 1. 严重（会直接毁掉回测可信度，或使密封目标在现行流程下不可达）

### S1. 主线「个股+ETF」与默认真书脱节：`alpha_event` 空心，默认袖套仍是债金/可转债/期货结构

| 项 | 内容 |
|---|---|
| **现象** | Leo 主线草案要求 **个股篮子 + ETF 袖套**；CB/金仅对照。但 `v2_multisleeve_book.py` 默认 `DEFAULT_SLEEVES = {"marp":0.40,"cb":0.30,"xd":0.30,"alpha_event":0.0}`，且 `AlphaEventSleeve` 明确返回 `{}`（权重落入 511880）。交接台账仍大量 CB-MATPREM / GOLD-BETA「explore-pass 候选」叙事。 |
| **证据** | `quantlab/portfolio/v2_multisleeve_book.py`（DEFAULT_SLEEVES、alpha_event 占位注释）；`docs/v2/MANDATE_DRAFT_STOCK_ETF_MAINLINE_ZH.md`；`docs/v2/STRATEGY_MULTISLEEVE_BOOK.md` 文首切换说明 vs 下文历史 MATPREM+GOLD；`output/v3/handoff_strategy/WATCH_ZH.md` |
| **为何不合理** | 没有可接线的个股事件权重长表，再挖多少 STOCK-* 臂也无法进入主书净值路径；对外/对内仍可能把 CB/金对照臂的 X2 数字当成「主线进度」。目标与实现脱节 → **密封 12–15% 在现行默认账本上没有对应载体**。 |
| **建议改法** | (1) 立刻把默认 `--sleeves` 改成「core/行业或主题 ETF + 宽基压舱」，`cb`/`xd`/`gold` 仅显式 `--arms` 对照；(2) 规定：任何 STOCK/ETF 冒烟若不能导出 `date,instrument,target_weight` 并被 `alpha_event`（或新 stock sleeve）消费，一律标 `not_book_consumable`，禁止当主线进度。 |

### S2. 「完整 X1（2015–17）过闸」与事件数据现实冲突 → 事件主线结构性堵死

| 项 | 内容 |
|---|---|
| **现象** | Beta/AI 冒烟以 **X1=2015-06→2017-12** 为硬预检；但回购/增减持/问询/停复牌/预告快报/disclosure_date/cninfo 等关键表 **X1=0 或自 2018**；指数调样 `available_at`≈2018-05+；北向个股/两融明细亦多 2018+。V35 备忘结论：无可写合格 STOCK 提案。 |
| **证据** | `docs/v2/AI_NEXT_ARM_COVERAGE_BLOCKED_MEMO_V35_ZH.md`；`docs/v2/BETA_X1_EVT_FLOW_COVERAGE.md`（龙虎等虽补了 X1，但其它制度事件仍缺）；`docs/v2/AI_V31_STOCK_INDEX_REBAL_BETA_REVIEW_ZH.md`（标准 X1 coverage_blocked） |
| **为何不合理** | 密封研究窗写的是 **2018–2024-05 开发 / 2024-06+ 探索**（Mandate 草案），却用 **2015–17 事件密度** 一票否决绝大多数「非公开制度」臂。结果：要么 coverage_blocked，要么只能硬磨已有 X1 的近亲（seat/解禁/披露日历）→ 连续自拒。这不是单臂垃圾，是 **闸门与数据窗口错配**。 |
| **建议改法** | 事件臂改为双轨：(A) **coverage_native**：表实际有 PIT 的最早日 → 今，作机制检验；(B) **book_window**：与密封一致的 2018+（或 Mandate 明示窗）。禁止用「X1=0」单独杀死 2018+ 有密度的机制；缺 X1 时标 `coverage_shifted` 观察，不伪造、也不空转提案。 |

### S3. Mandate / AGENTS / 草案三套资本规则并存（含「名义 L≤1.5」实际不可融资执行）

| 项 | 内容 |
|---|---|
| **现象** | `AGENTS.md`：60万、扣费后年化 15%、最多 50 只、**无杠杆**。`QuantLab-MANDATE_V2.json`：`leverage_allowed=false`，持股 30–60，研究 CAGR 门禁 12–18%、回撤门 −28%。草案 `MANDATE_DRAFT_*`：个股+ETF、**L≤1.5**、AUM 60∧100万。多袖套代码允许 `--leverage`≤1.5，但注释写明 **无 MarginConfig 借款，买入受现金约束，现货总仓≈截在 1.0**。 |
| **证据** | `AGENTS.md`；`docs/v2/QuantLab-MANDATE_V2.json`（capital.leverage_allowed、gates_research_targets）；`docs/v2/MANDATE_DRAFT_STOCK_ETF_MAINLINE_ZH.md`；`quantlab/portfolio/v2_multisleeve_book.py` L18–19、L534–540 |
| **为何不合理** | 同一仓同时存在「无杠杆 / L≤1.5 / 引擎实际做不到现货杠杆」；报告若写 L=1.5 净值，读者会以为加了买力，实为权重缩放或期货名义。目标数字（12–15% vs 15% vs 12–18%）也不一致 → **任何「过线」叙事都可被挑口径**。 |
| **建议改法** | Leo 当面拍一版正式 Mandate：杠杆是否允许、现货是否允许融资、主书袖套表、持股上下限、CAGR/MDD 唯一数字；未接线 `MarginConfig` 前 **禁止** 在主报把 L>1 写成可执行应力，最多标「权重名义缩放（无借款）」。同步改 AGENTS.md 接续句，避免新 agent 读到旧「50 只无杠杆」。 |

### S4. 数据集 `promotion_approved` 与策略 `promotion_approved` 同名易混（总闸语义漂移）

| 项 | 内容 |
|---|---|
| **现象** | `ENG_PING_PATHS.json` / `V2DataRoots.promotion_approved=True`（数据层 Leo 批准）；策略侧 Mandate / 所有臂文档仍 `promotion_approved=false`。`PROMOTION_ACCEPTANCE.md` 写 overall true。代码读者或新 bot 极易把「数据可晋级」读成「策略可晋级」。 |
| **证据** | `output/d1/ENG_PING_PATHS.json`（`promotion_approved_overall: true` + note）；`quantlab/data/v2_readers.py` `default_v2_roots().promotion_approved=True`；`docs/v2/QuantLab-MANDATE_V2.json` 顶层 `promotion_approved: false` |
| **为何不合理** | 总闸语义漂移会在某一天让人把 research_observe NAV 当密封候选；这是流程级事故温床。 |
| **建议改法** | 全局改名：`dataset_promotion_approved` vs `strategy_promotion_approved`；所有策略输出 JSON 强制带后者且默认 false；Eng ping 文档标题禁止单独写「promotion_approved=true」不带「dataset」前缀。 |

### S5.（历史已修、仍须当作严重教训）涨跌停/停牌「持仓收益记 0」曾系统性扭曲年化；文档与小盘模块仍残留旧口径

| 项 | 内容 |
|---|---|
| **现象** | 旧逻辑把涨跌停/停牌日持仓收益记 0 → 研究卡指出可造成每年约数十个百分点量级偏误；2026-10-10 起 `close_to_close_returns` / `held_book_return` / `block_mark_to_zero→永远 False` 已改为 **只挡成交、估值照常**。但 `STRATEGY_RESCUE_PLAN_V1.md` 仍写「收益记 0」；`beta/smallcap_sleeve.py` 模块注仍写「engine currently books limit/halt days as 0 return」。 |
| **证据** | `quantlab/platform/strategy_feed.py` L419–426；`quantlab/portfolio/v2_execution_costs.py` `block_mark_to_zero`；`quantlab/portfolio/v2_strategy_paper_costs.py` L86–88；`docs/v2/STRATEGY_RESCUE_PLAN_V1.md` L28；`quantlab/beta/smallcap_sleeve.py` L17–18；`output/research_survey/cards/C01_*LimitHiddenExcess.md` |
| **为何不合理** | 代码修了、权威文档与卫星模块说明没修 → 后续「急救」或小盘对照可能按错口径重实现；且 fallback `asof_extend_202610` 的 limit 列曾 100% 空（现默认已切 tushare extend，limit 非空），若有人显式走 fallback，`enforce_limits` 会静默不触发。 |
| **建议改法** | 删除/更正 RESCUE 与 smallcap 模块中的「记 0」句；加回归测试：持仓涨停日 NAV 变动 = 收盘价变动；CI 断言 `load_merged_panel` 默认根 limit_up 非空率阈值；禁止业务路径读 `asof_extend_202610` fallback 除非显式 research flag。 |

---

## 2. 中等（架构/流程浪费或系统性偏差）

### M1. AI 因子工厂空转：账本近 6800 次尝试，大量包 `GATE_OK=0`，仍持续堆 vN 脚本与叶

| 项 | 内容 |
|---|---|
| **现象** | `output/ai_factor/ledger.jsonl` ≈6795 行；近窗大量 `fitness=-1e9`；handback 包抽样约半数 `n_gate_ok=0`；`research/ai_factor_gp_reopen_hardgate_v*.py` 从 v2 堆到 v26+。 |
| **证据** | `output/ai_factor/ledger.jsonl`；`output/ai_factor/gp_reopen_hardgate_v17*/` 等；`docs/v2/SYSTEM_ARCH_V3_ZH.md` §3.5（工厂 KPI 本是管线通+ledger，却被当成主 Alpha 产能） |
| **为何不合理** | 在硬闸（新颖性/残差降级/禁教科书）下重复搜索同一叶空间，产出的是目录噪声而非可接线权重；挤占 Data/Beta 注意力。 |
| **建议改法** | 设工厂停机条件：连续 K 个包 GATE_OK=0 或「去叶后无增量」→ 冻结 GP，只允许 **人工指定新信息维 + 覆盖审计** 后再开；把 KPI 从「尝试次数」改为「可被 Strategy 消费的权重长表条数」。 |

### M2. 硬禁同构清单膨胀 → 搜索空间自我塌缩（V29–V34 模式）

| 项 | 内容 |
|---|---|
| **现象** | 每拒一臂就加入硬禁（seat / unlock / tercile / 价叶 / 份额流 / LIMITUP / ocf / DY / 早披露 / V31 同构…）。到 V35 时优先探坑全 blocked。 |
| **证据** | 各 `AI_STOCK_ARM_PROPOSAL_V3*.md` 硬禁表；`AI_NEXT_ARM_COVERAGE_BLOCKED_MEMO_V35_ZH.md` §0–2 |
| **为何不合理** | 正交纪律本身合理，但与 S2 的 X1 闸叠加后，只剩「有 X1 且未禁」的极窄缝 → 必然产出 Leo 所说的「垃圾策略」短窗事件。 |
| **建议改法** | 硬禁改为 **族内 ρ/消融门槛**（实证触发）而非提案标题永久黑名单；允许「同族对照臂」但禁止当 primary；先解 S2 窗口错配再谈禁表。 |

### M3. 冒烟口径（单臂 Sharpe≤0 / avg_names=0）与密封目标（组合净成本 CAGR 12–15%、MDD≤25%）不衔接

| 项 | 内容 |
|---|---|
| **现象** | 事件臂 pretest 以单臂 X1 Sharpe、持仓数为主；即使微正（如 V31 coverage_shifted Sharpe≈+0.28）也明确不晋级、不开 X2、不交 Strategy。没有任何路径把「过预检的叶子」合成 **60/100万 · Full D1 · 成本** 的个股+ETF 主书再对照密封门。 |
| **证据** | `docs/v2/AI_V31_*_BETA_REVIEW_ZH.md`；各 pretest `output/v3/pretest_batch_20261012_*.json`；Mandate 门禁 vs Beta fail_precheck 规则 |
| **为何不合理** | 工厂/冒烟优化的目标函数 ≠ 密封目标函数 → 过线定义永远对不齐。 |
| **建议改法** | 固定一条 **Book-Smoke**：默认袖套（个股篮预算 + ETF 预算）@60万∧100万 · 成本开 · 与 510300 对照；单臂只作为叶子诊断，不能单独宣称「主线进展」。 |

### M4. U30 在 amount 缺口上默认 waive；后期 float_mktcap 稀疏靠 stale carry

| 项 | 内容 |
|---|---|
| **现象** | `d1_masks.waive_u30_on_amount_gap=True`：amount 全 NaN 时不因 U30 剔除。float 日表在 2026-06-30 后曾极稀疏，研究用 stale asof carry。 |
| **证据** | `quantlab/universe/d1_masks.py`；`docs/v2/ASOF_EXTEND_PANEL_MERGE.md`；`docs/v2/PROMOTION_ACCEPTANCE.md` float 段 caveats |
| **为何不合理** | 流动性硬闸被数据缺口软化 → 容量/冲击被低估；市值排序在尾段失真。研究可用，但不能支撑密封叙事。 |
| **建议改法** | 密封/主报强制 `waive_u30_on_amount_gap=False` 或改用有 amount 的 tushare 段；float 尾段缺数则截断样本末日，禁止 silent carry 进主报。 |

### M5. 多执行路径并存，并非所有臂都走 E1 双引擎对账

| 项 | 内容 |
|---|---|
| **现象** | 平台 `run_weight_schedule`、ledger、fastsim、以及若干 Strategy paper（S2 costs、turn_compare）并行；E1 reconcile 存在，但大量 Beta pretest / AI 叶评估用自建轻量路径。 |
| **证据** | `docs/v2/SYSTEM_ARCH_V3_ZH.md` §3.8；`quantlab/platform/e1_reconcile.py`；`output/v3/pretest_batch_*.json` 与 `output/strategy_recon/*` 分流 |
| **为何不合理** | 同一「Sharpe」可能来自不同成本/涨跌停/复权假设；跨臂不可比。 |
| **建议改法** | 凡声称主线相关的数字，必须附 `engine_id ∈ {platform_strategy_v1, ledger, …}`；缺 E1 对账的只能标 diagnostic。 |

### M6. 公司行为 / 总回报因子在部分 paper 路径仍是 opt-in，默认原始收盘 pct_change

| 项 | 内容 |
|---|---|
| **现象** | `execution.strategy_v1` 默认 `corporate_actions=True`；但 `strategy_feed.close_to_close_returns` 的 `total_return_factor` 默认 None；turn_compare 注释承认 paper NAV 有时未传 factor。 |
| **证据** | `quantlab/platform/execution.py` ExecConfig；`quantlab/platform/strategy_feed.py` L419–435；`v2_strategy_paper_turn_compare.py` mark_rule 注释 |
| **为何不合理** | 除权日会把现金分红/送转表现为价格「亏损」，低估长期净值；与平台引擎主路径不一致。 |
| **建议改法** | 所有主报 paper 强制 total-return close（或统一只报 platform 引擎 NAV）；原始价收益仅作诊断。 |

### M7. 角色边界清晰，但「草案未写入正式 Mandate」导致专责各写各的主书

| 项 | 内容 |
|---|---|
| **现象** | SYSTEM_ARCH 角色表清楚；但 MAINBOOK 文档、NOIC 骨架、WATCH 值班条在「切换草案」后仍保留大段 CB/金主表试配。 |
| **证据** | `docs/v2/SYSTEM_ARCH_DIAGRAM_ZH.md`；`STRATEGY_NOIC_AUM_SKELETON_ZH.md`；`WATCH_ZH.md` |
| **为何不合理** | New Bot / Strategy / Beta 可能同时推进两套「当前主线」。 |
| **建议改法** | 未 Leo 确认前：所有「主表试配」标题加前缀 `HISTORICAL_ONLY`；确认后删默认 CB 权重并改 WATCH 唯一主线段。 |

---

## 3. 轻微

### L1. 仓库根大量 `._*` AppleDouble 与根目录 `scripts_*.py` 散落  
污染检索与误跑；应收进 `scripts/` 或删。

### L2. `docs/v2/` 提案/回执爆炸（V20–V35 + 大量 PREREG）  
缺少「现行有效一行索引」；新人只见噪声。建议一页 `ACTIVE_CONTRACTS_ZH.md` 只链现行 Mandate/账本/数据契约。

### L3. 巡检「AI 零活动」误报  
与真实连交提案矛盾；巡检应读 `docs/v2/AI_*` mtime / handback，而非进程名。

### L4. 北交所涨跌停/停牌历史覆盖缺口  
已文档化；主线禁小盘/北交所则影响有限，但宇宙若扩大需补。

### L5. 期货保证金历史档未建模（常数表）  
FUT-RP 仅对照时可接受；若再当压力主臂会偏乐观。

---

## 4. 「其实合理」的设计（避免一味否定）

1. **涨跌停只挡成交、持仓照常 mark-to-close**（修完后）——正确；与实盘一致。  
2. **PIT `available_at` 不可为填 X1 而前移**——正确；V31/V35 诚实标 coverage_blocked 优于造假。  
3. **`promotion_approved=false` 直到密封** + 数据集验收与策略晋级分离（若命名理清）——正确闸门哲学。  
4. **E1 零成本三引擎对账脚手架**——正确工程卫生。  
5. **自拒规则**（无相对粗信号增量 / 空仓靠压舱主导）——正确，避免把黄金 β 当 Alpha。  
6. **禁小盘主仓 + 禁把 MATPREM/金当主书的方向**（Leo 已定）——与容量/目标匹配。  
7. **成本默认：佣金 2.5bp+最低 5 元、滑点 5bp、印花税历史卖出、next_open、参与率帽**——研究级合理起点。  
8. **硬刷新换手 / β 袖套冲突被识别为问题并单独修**（RESCUE P2）——问题意识正确。

---

## 5. 若只改 3 件事（优先级）

| # | 改什么 | 为何最先 |
|---|---|---|
| **1** | **统一正式 Mandate + 默认真书袖套**：写入个股+ETF；默认权重去掉 CB/金/期货主仓；`alpha_event`（或 stock sleeve）必须能吃权重长表；AGENTS.md 与 JSON 对齐；未接融资前禁止叙事 L>1。 | 没有载体，一切 Alpha 冒烟都是空转。 |
| **2** | **重写事件臂窗口闸**：用「表原生覆盖窗」做机制检验 + 「密封窗 2018+」做书级评估；废除「完整 X1=0 ⇒ 提案死亡」单闸。 | 解开 V35 堵死与 V30–V34 空耗的根因。 |
| **3** | **一条 Book-Smoke 对准密封目标**：60万∧100万 · Full D1 · 成本开 · 个股篮+ETF 预算 · 相对 510300；工厂/单臂数字降级为叶子诊断；连续 GATE_OK=0 停 GP。 | 让日常优化函数 = Leo 真正要的函数。 |

（并行卫生）更正「收益记 0」残留文档；数据集/策略 promotion 改名；主报强制 total-return。

---

## 6. 与已知历史的对照（本复盘结论）

| 已知 | 本复盘判定 |
|---|---|
| 涨跌停记 0 曾每年漏损约 25pp | **代码路径已修**；文档/smallcap 注释未清；属严重教训 + 中等残留 |
| MATPREM+金已降级 | 文档声明降级，**默认代码袖套与 handoff 叙事未完全跟上** → S1 |
| V30–V34 多 fail/自拒 | 不全是臂差；**S2+M2 系统性**；Leo 叫停合理 |
| V31 仅 coverage_shifted 微正 | 诚实观察 OK；**不能当过线**；也说明「移位窗」可能是唯一有信号的区间 → 支持改闸 |

---

## 7. 路径索引（便于父代理抽查）

- 架构：`docs/v2/SYSTEM_ARCH_V3_ZH.md`、`SYSTEM_ARCH_DIAGRAM_ZH.md`、`SYSTEM_ARCH_V3_AI_NATIVE_ZH.md`  
- Mandate：`docs/v2/QuantLab-MANDATE_V2.json`、`MANDATE_DRAFT_STOCK_ETF_MAINLINE_ZH.md`、`AGENTS.md`  
- 执行：`quantlab/platform/execution.py`、`strategy_feed.py`、`portfolio/v2_execution_costs.py`  
- 主书：`quantlab/portfolio/v2_multisleeve_book.py`、`docs/v2/STRATEGY_MULTISLEEVE_BOOK.md`、`output/v3/handoff_strategy/WATCH_ZH.md`  
- 覆盖堵死：`docs/v2/AI_NEXT_ARM_COVERAGE_BLOCKED_MEMO_V35_ZH.md`  
- 本报告：`docs/v2/FULL_STACK_REVIEW_UNREASONABLE_20261012_ZH.md`

---

*完。promotion_approved=false；未改业务代码；未开冒烟。*
