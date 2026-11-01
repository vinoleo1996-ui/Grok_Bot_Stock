# Eng A3：AlphaLens paper.py ↔ capacity_adv / B4 纸面轨对照（append-only · T+1 · 满 N 日 · 基准）

- **计划行**：`docs/v2/audit/MAIN_ALPHALENS_ABSORB_PLAN_20261025_ZH.md` · **A3**（Eng）
- **授权**：Leo 批准吸收（主裁 2026-10-25）；**live=false** · **promotion_approved=false**
- **本交付**：只文档对照表 + 缺口 DIFF 草案；**不擅改 live/paper 生产**（不改 runners / ledgers / 权重 parquet / NAV / `.ok` / FROZEN_CONFIG）
- **ET**：2026-10-25（America/New_York）
- **引擎共用声明（只说一次）**：`capacity_adv` 与 `B4` **共用** `book-smoke` → `v2_multisleeve_book.run_book` → `run_weight_schedule` + `ExecConfig.strategy_v1`（`fill=next_open`）；差异仅在**权重袖套文件**（capacity_adv 单叶长表 vs B4 50/25/25 集中化三腿）及 B4 的 `FROZEN_CONFIG` / rehash / booked-day 闸门。下文分列是为回答五问，不是两套独立结算引擎。

---

## 0. 关键文件 sha256（本回合核验）

| 文件 | sha256 |
|---|---|
| `docs/v2/refs/alphalens_workbuddy/paper.py` | `ddbe48d1c5d9f2b4135ffbf3824b3859666e52de3c424145c1ff01f14f241557` |
| `docs/v2/audit/MAIN_ALPHALENS_ABSORB_PLAN_20261025_ZH.md` | `578a19f1de9ebf97f506d839c7ca5585c136ca64862f5a9b1979b93dcd28098e` |
| `quantlab/portfolio/b4_paper.py` | `ffe195e68db279ca3fe41b7aa521e0fdd282b685c02243e21696571db08b03a3` |
| `quantlab/portfolio/book_smoke.py` | `1a5fa1aa6ab847bd1ecda4d01bd4bda88b23535edceb91021520261be3e8251b` |
| `research/capacity_adv_paper_extend.py` | `bfb056305ea624c96ca6d6f7e9f5d39ecf932d2881c5b0c4b41bb6a292958a18` |
| `research/b4_paper_extend.py` | `6c927ae692685e4b87054ecccd1a1342be735d8242cbfe82f0b1f84b9a82653c` |
| `docs/v2/CAPACITY_ADV_PAPER_ENG_ZH.md` | `1b112a3e5655f205cf5878d4affafefabd243868e523d3ef1b62787635632c5e` |
| `docs/v2/B4_PAPER_ENG_ZH.md` | `50a3ec46358fbee53a355afc805a76ce08a93677fbadf79389328b31820f3390` |
| `output/strategy_paper_b4/FROZEN_CONFIG.json` | `f0783861798138da7b4f3bab5595533a04fb4489e49564339c280239bc1e3e5c` |

---

## 1. 五问直答（摘要）

| # | 问题 | (A) AlphaLens `paper.py` | (B) capacity_adv paper | (C) B4 paper | Gap? |
|---|---|---|---|---|---|
| 1 | **append-only?** | **是**：`_append` 写 jsonl；同 `trade_date` 已存在则 `record` 直接跳过（L44–47, L61–63） | **权重侧近似是**（`<=FROZEN_END` 逐行钉死，exists+different→abort）；**NAV 侧否**（book-smoke 复跑可覆写目录；纸面包多为 symlink） | **权重侧强是**：rehash `history_match` + `splice_booked`「booked days never rewritten」；**NAV 侧同 B**：backfill 复跑可覆写 `backfill_x2/` | **部分 Gap**：QL 无 AlphaLens 式「信号日 jsonl 只追加」；权重冻结已有，日级信号账本形态缺 |
| 2 | **可否改日?** | **不可改已记账信号日**（同日 skip）；`settle` 只重算盯市，不改写 ledger 行 | **历史权重不可改**（`|dw|≤1e-8`）；前向月频重算日**不得**回写昨日（日历设计刻意避免）；NAV 可整窗重算覆写 | **已 booked session 不可改**（`|Δw|≤1e-8`）；分歧延至**恰下一 SSE 交易日**；rehash 失败则 FROZEN 不变 | **弱 Gap**：B4/capacity_adv 权重改日门已严；缺的是「信号批 jsonl + revisions 审计」形态（另见 `forward_paper_book` 有 revisions.jsonl，**非**本二轨主路径） |
| 3 | **是否次日开盘结算?** | **是**：`entry_date = bench_dates[idx0+1]`，`entry = open`（L105–114） | **是**：`ExecConfig.strategy_v1` → `fill=next_open`（T+1 open）；盯市 close | **是**（同引擎）；monitor 注「target=T vs actual=T+1 fill」 | **无 Gap**（语义对齐） |
| 4 | **满 N 日才计?** | **是**：`holding_days >= 5` 才进 `stats`（L162–179） | **否**：连续 NAV 自窗起点计 CAGR/MDD/Sharpe；无 batch 成熟度过滤 | **否**：同连续 NAV；另有 H1/H2/forward **分段**展示，仍非「满 N 日信号批」 | **有 Gap**（口径不同：批次回放成熟度 vs 连续组合全窗） |
| 5 | **基准对照?** | **是**：沪深300 `1.000300`；`excess_pct` / `portfolio_excess_pct`（L148–158, L168–176） | **是**：同引擎臂 **C0=纯 510300**；headline vs C0 ΔCAGR（60万 +2.56pp / 100万 +0.97pp） | **是**：vs C0 + vs **capacity_adv 主干**（TRUNK_RUN）；分段超额分列 | **弱 Gap**：AlphaLens 指数点位；QL 为**可成交 ETF 510300 同成本臂**——更严，宜保留；勿退回裸指数 |

---

## 2. 对照表（扩展行）

| 维度 | AlphaLens `paper.py` | capacity_adv | B4 | Gap? |
|---|---|---|---|---|
| **账本形态** | `paper-v{VERSION}.jsonl` 逐日信号批（TOP10 建仓/左侧试仓） | 权重长表 parquet + book-smoke `nav.csv` / `summary.json`；纸面包 `output/strategy_paper_capacity_adv/`（symlink→`book_smoke_g1g5_capacity_adv_x2`） | `FROZEN_CONFIG.json` 钉权重 path/sha；`backfill_x2/.../nav.csv` + `forward/...` + `monitor.json` | Gap：形态不同（信号批 jsonl vs 连续组合 NAV） |
| **改写策略** | 同日不写；无 rehash API | extend：历史 verbatim；新文件 exists+diff→exit 3；不覆写 frozen 源包 | rehash 双检 (a)历史 (b)新行；content_gate + deferral；booked splice | 权重侧 QL≥AlphaLens；NAV 覆写策略需文档钉死「复跑=新 run_id」 |
| **结算价** | 建仓=次日 open；标记=最新 close；另跑 Account 止损/目标 | 信号日 close 锁目标；成交 next_open；盯市 close；公司行动开盘前 | 同左 | 对齐 |
| **最小持有/成熟** | ≥5 交易日批次才进汇总统计 | 无 | 无（有分段，非满 N 日） | Gap：是否为「纸面信号批」另开成熟度规则（见 DIFF） |
| **基准** | CSI300 指数同步涨跌超额 | C0 510300 BOOK（含成本/分红） | C0 + capacity_adv trunk | 保留 QL C0；可选附加裸指数附录 |
| **连续 vs 批次** | **独立信号批次回放**；注明确认「非连续组合」；连续见模拟账户 | **连续组合 NAV**（X2 探索窗） | **连续** backfill + 独立 forward 窗（2026-11-02 起，WAITING） | **架构差**：勿把 AlphaLens 批次收益与 QL NAV 直接比数字 |
| **成本/滑点** | Account 费用+止损；doc 称不含冲击以外成本 | strategy_v1：佣金/印花/sqrt impact k=1 / 10% 参与率 / lots / limits | 同引擎 | QL 更全；吸收时勿降级 |
| **Universe / 池** | 当日 quant TOP10（CN）；计划禁「当日池回测」 | 中大盘 ADV 容量叶 + 表内 510300 压舱；sleeves `core=0,stock=1` | 三腿 topN 集中（60万 N=6 / 100万 N=10）；单名帽 6% | 禁吸收：8 维技打分主 alpha / LLM 多空辩论下单 / 当日池回测（计划原文） |
| **AUM** | suggested_equity 字段 | 主敏感度 60万∧100万 | 同，分文件 | — |
| **入口** | WorkBuddy 刷新钩子 | `python -m quantlab.cli capacity-adv-paper` | `python -m quantlab.cli b4-paper --mode …` | — |

### 关键代码锚点

- AlphaLens append / 同日 skip：`paper.py` L44–47, L50–63, L87  
- AlphaLens T+1 open + 满 5 日 + 基准超额：L105–114, L148–158, L162–176, L187（连续 vs 批次 note）  
- QL `strategy_v1` = next_open：`quantlab/platform/execution.py` L343–349；文档 `docs/v2/EXECUTION_COSTS_PLATFORM.md` L49–51, L108  
- capacity_adv 历史不可改 / 不覆写 frozen：`research/capacity_adv_paper_extend.py` L1–24  
- B4 booked-day：`research/b4_paper_extend.py` L134–150；rehash/content_gate：`b4_paper.py` L351–402, L405+  
- 共用引擎声明：`b4_paper.py` L3–5；`docs/v2/B4_PAPER_ENG_ZH.md` L7  

---

## 3. 缺口 DIFF 草案（只文档级提案 · **不擅改 live/paper 生产**）

> 下列为 Eng **建议** Arch/主裁签 `code_change` 前的文档草案。本回合 **零生产改动**。

### P0（对齐诚实边界 / 防口径混用）

| ID | 提案 | 保留 | 明确不吸收 |
|---|---|---|---|
| P0-1 | 在 `CAPACITY_ADV_PAPER_ENG_ZH.md` / `B4_PAPER_ENG_ZH.md` 各加一节「与 AlphaLens paper 对照」：**连续 NAV ≠ 信号批次回放**；禁止用 AlphaLens `avg_ret_pct` 对比 QL CAGR | 现有 C0/trunk 超额与成本臂 | 把 AlphaLens 批次统计替换 QL headline |
| P0-2 | 文档钉死：**权重历史 append-forward + 冻结**已满足 A3「不可改日」精神；**NAV 产物**若复跑须新 `run_id`/目录，禁止静默覆写已引用 symlink 源（capacity_adv 现状：纸面包 symlink 到固定 book_smoke 目录——复跑风险写进 HARDEN/STATUS 警告） | B4 rehash + booked-day | 移植 AlphaLens 8 维分 / LLM 辩论单 / 当日池 |
| P0-3 | 结算语义写清一行金句：「信号日 close 锁目标 → **次日 open 成交** → close 盯市」（两端已一致，只需交叉引用 `ENG_PRICE_BASIS_AUDIT_RECEIPT_ZH.md`） | `ExecConfig.strategy_v1` | `fill=close` 当纸面主口径 |

### P1（可选增强 · 另签 code_change）

| ID | 提案 | 说明 |
|---|---|---|
| P1-1 | **信号批账本（可选并行轨）**：若 Strategy 要「每日 TOP 意图」可审计，新增 **研究级** jsonl（append-only、同日 skip），**不**替代 book-smoke NAV；mature_days 默认 5 可配置 | 对标 AlphaLens `record`/`settle`；live=false |
| P1-2 | **满 N 日过滤**：仅作用于 P1-1 批次统计；**不得**裁剪连续 NAV 窗起点（避免选样） | |
| P1-3 | **基准双挂**：主对比保持 C0 510300；附录可加裸 CSI300 点位超额（AlphaLens 同款），标注「无冲击/不可成交」 | |
| P1-4 | capacity_adv 权重 extend 已有 abort-on-diff；建议监控回执显式打出 `history_ok` / `last_booked`（B4 monitor 已较完整） | 文档/监控字段，非改引擎 |
| P1-5 | `forward_paper_book.py` 的 per-date rewrite + `revisions.jsonl` **勿**默认为 capacity_adv/B4 主路径；若复用须 LOCK 密封 + 改日审计升到与 B4 booked 同级 | 防「可改日」回潮 |

### 明确不做（计划「禁抄」+ 本 DIFF）

- 不移植 AlphaLens 全站 / NeoData  
- 不以 8 维技术打分做主 alpha  
- 不以 LLM 多空辩论结果直接下单  
- 不引入「当日股票池回测」幸存者路径  
- **不**在本吸收回合改 live、翻 promotion、消费无关 `.ok`、实跑补跑包  

---

## 4. 结论（给主裁一句）

A3 对照完成：**T+1 开盘结算两端已对齐**；**基准两端都有超额（QL 用可成交 510300 C0，更严）**；**改日禁令在 QL 权重侧（尤其 B4 booked/rehash）已不低于 AlphaLens**；主要缺口是 **(i) 连续 NAV vs 信号批次回放 的形态差**、**(ii) 无「满 5 日才进汇总」的批次成熟度规则**、**(iii) NAV 产物覆写策略需文档钉死**。DIFF 仅文档级 P0/P1；**等待 Arch `code_change` 前不改生产**。

---

## 5. 元数据

- 专责：QuantLab Eng  
- live=false · 无纸面实跑 · 无 `.ok` 消费 · 未改 TEAM_STATE  
- 关联计划：`MAIN_ALPHALENS_ABSORB_PLAN_20261025_ZH.md` A3  
- 产出路径：`docs/v2/audit/alphalens_absorb_a3_20261025/ENG_A3_PAPER_APPENDONLY_COMPARE_20261025_ZH.md`
