# QuantLab 正式 Mandate 草案（个股 + ETF 主线）

**日期**：2026-10-12 · America/New_York  
**状态**：架构统一草案 · **`strategy_promotion_approved=false`** · 密封未过 · **不写实盘权重**  
**来源**：Leo 批准按 `FULL_STACK_REVIEW_UNREASONABLE_20261012_ZH.md` 三条开工（S1–S3 /「若只改 3 件事」）  
**门锁拍板**：**Leo 2026-10-12** 沿用旧 JSON——净成本 CAGR **12%–18%** · MDD **−28%**（否决草案 12–15% / ≤25%）  
**Supersede**：
- `docs/v2/MANDATE_DRAFT_STOCK_ETF_MAINLINE_ZH.md`（本页更完整；旧草案保留历史）
- `AGENTS.md` 旧接续句「60万 / 15% / 最多50只 / 无杠杆」→ **以本页为准**（AGENTS 已加指针）
- `docs/v2/QuantLab-MANDATE_V2.json` 仍为 defaults_locked；**CAGR/MDD 门锁已与本页一致（Leo 2026-10-12 拍板）**；资本/杠杆/主书袖套以本页为准

---

## 0. 一句话

主书 = **中大盘个股篮（事件/资金结构 Alpha）+ 宽基/行业/主题 ETF 压舱与 Beta**；  
可转债 / 黄金 / 期货名义 **仅显式对照臂**；现货 **无融资**（名义 L≤1.0）；  
晋级总闸 **`strategy_promotion_approved=false`** 直至密封通过。

---

## 1. 资本与杠杆（唯一口径）

| 项 | 正式口径 | 禁止叙事 |
|---|---|---|
| AUM 主结论 | **60 万 ∧ 100 万 CNY**（须同时过；大资金仅附录） | 用 5M 当主报 |
| 净成本 CAGR 门 | **12%–18%**（研究门禁，非承诺） | 与 15% / 12–15% 混用而不声明 |
| 最大回撤门 | **MDD 不差于 −28%**（研究观察；可恢复缩放，非永久死亡） | 与 ≤25% 门混用不声明 |
| 现货杠杆 | **名义 L ≤ 1.0**；**无融资 / 无融券**；引擎无 `MarginConfig` 借款 | 把 L>1 写成「可执行加仓」 |
| 期货名义 | 仅对照臂；若出现在账本须标 `futures_overlay_contrast`；**不得**撑主书密封叙事 | 用 IC 名义制造假 L>1 |
| 现金 | 合法；闲置目标 ≈2%，硬上限 ≈5% | — |
| 只做多 | 是 | 裸空主仓 |

> **未接线融资前**：`--leverage>1` / `--max-gross>1` 最多标「权重名义缩放（无借款）」，主报禁止写成可执行应力。

---

## 2. 主书袖套（默认）

| 袖套 key | 默认预算 | 角色 |
|---|---|---|
| **core** | **1.0**（无个股权重时长表时） | 宽基压舱 **510300** 买入持有 |
| **stock** | 0.0（有权重长表后上调） | 中大盘个股篮 |
| **alpha_event** | 0.0 | 事件/资金结构 Alpha（与 stock 同契约） |
| marp / cb / xd / gold / e2 / ind_mom | **默认 0** | **仅** `--sleeves` / `--arms` 显式对照 |

代码默认：`quantlab/portfolio/v2_multisleeve_book.py` → `DEFAULT_SLEEVES`。  
合成：最终权重 = Σ（袖套预算 × 袖套内权重）；空袖套预算停 **511880**。

### 权重长表契约（stock / alpha_event）

路径由 `--stock-path` / `--alpha-event-path` 传入（parquet/csv）。列名别名：

| 逻辑列 | 接受别名 |
|---|---|
| session | `session` \| `date` \| `trade_date` |
| instrument_id | `instrument_id` \| `instrument` \| `ts_code` \| `code` |
| weight | `weight` \| `target_weight` |

缺路径、不可读、或行数为 0 → 运行时标 **`not_book_consumable`**，日志清晰；**禁止**把该臂当主线进度。

---

## 3. 风险与宇宙

- 基准：沪深300 / **510300**
- 禁小盘主仓；微盘不得作宇宙
- 个股侧持股约 **30–60**；单股 ≤5%；申万一级 ≤25%
- 流动性 U30；上市 ≥120 日；剔 ST / 退市整理 / 默认北交所
- 成本：佣金 2.5bp+最低 5 元；滑点 5bp；印花税历史卖出；`ExecConfig.strategy_v1`

---

## 4. 窗口

| 窗 | 用途 |
|---|---|
| **coverage_native** | 表实际 PIT 最早日→今（机制检验）；见 `EVENT_ARM_WINDOW_GATES_ZH.md` |
| **book_window / 密封相关** | 开发验证 **2018-01→2024-05**（未授权不重跑密封）；探索 **2024-06→今** |
| 旧「完整 X1 2015-06→2017-12」 | **可选对照**，不得单独因 X1=0 杀死 2018+ 有密度机制 |

---

## 5. 晋级命名（强制区分）

| 字段 | 含义 | 默认 |
|---|---|---|
| **`dataset_promotion_approved`** | 数据层可被研究管线消费（Eng ping / V2 roots） | 可 true（数据验收） |
| **`strategy_promotion_approved`** | 策略/主书可晋级密封或实盘 | **false** 直至 Leo 密封 |

所有策略输出 JSON 必须带 **`strategy_promotion_approved=false`**（本草案期间）。  
禁止单独写 `promotion_approved=true` 而不带 `dataset_` / `strategy_` 前缀。

---

## 6. Book-Smoke KPI（对准密封，非 GP 次数）

固定入口：`python3 -m quantlab.portfolio.book_smoke`（或等价脚本）。

- AUM **60万 ∧ 100万** · 成本开 · 默认袖套
- 无个股权重 → 诚实跑 **纯 510300 book baseline**，写明缺口
- KPI：**可被 Strategy 消费的权重长表条数** / Book-Smoke 净值路径  
- 连续工厂 GATE_OK=0 → **停 GP**，勿空转

---

## 7. Leo 已拍板 / 仍待决

1. ~~CAGR~~ → **已拍板（Leo 2026-10-12）**：沿用旧 JSON **12%–18%**（净成本；非承诺）  
2. ~~MDD~~ → **已拍板（Leo 2026-10-12）**：沿用旧 JSON **不差于 −28%**（不是 ≤25%）  
3. 个股篮默认预算何时从 0 上调（需首条可消费权重长表）——仍待  
4. 密封窗是否允许「coverage_shifted 2018+」作为机制过闸证据（本页：**允许标观察，不自动晋级**）——仍待  

---

路径：`docs/v2/MANDATE_UNIFIED_STOCK_ETF_20261012_ZH.md`  
关联：`EVENT_ARM_WINDOW_GATES_ZH.md` · `FULL_STACK_REVIEW_UNREASONABLE_20261012_ZH.md`
