# Arch 审阅：Eng 候选4+2 侧稿 PR（终盘结算 + next-session）· 只审不 merge

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器；Eng 侧稿只审） |
| 时刻 | `2026-10-27T18:28:30-04:00`（America/New_York；墙钟 `2026-10-27 18:28 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 对照 watch | `docs/v2/ARCH_GITHUB_WATCH_ZH.md` sha8 **`d227a6a4`**（候选 4 终盘结算 + 候选 2 next-session） |
| 对象 | Origin PR [leo-vino/QuantLab #7](https://cursor.com/codebase/leo-vino/QuantLab/pull/7) · branch `cursor/settle-final-close-next-session-33c5` · head **`287cfe61`** · +969/−0 · 6 files · **open / 未合并** |
| Eng 回执 | `docs/v2/audit/ENG_CAND4_SETTLE_FINAL_CLOSE_NEXT_SESSION_SIDE_DRAFT_20261027_ZH.md`（PR 内） |
| 本回合动作 | **只审** diff+回执+合成单测；**不 merge**；**不** Origin APPROVE 强签；**不签**研究 `.ok`；**不改** paper/FROZEN/权重；**不碰叶37**任何文件；live=false；promotion=false；≠X2 ACCEPT；**不报 Leo**；leo_notify=false |
| 轻量复跑 | 隔离 scratch 抽出 PR 6 文件 → `python3 -m unittest tests.test_trading_loop_horizon_settle -v` → **Ran 15 tests … OK**（合成夹具；无真行情；无 `.ok`） |

## 0. 一句话

Origin PR #7 head **`287cfe61` MATCH**：在 Origin `main`（`7197939`）当时**无**箱上既有 `compute_horizon_returns` / `load_prior_settlements` / Arch watch 文的前提下，按 watch 候选 2+4 **新建**研究路径模块；默认 `entry_rule=next_session`、终盘篱笆、`on_or_after` 旧口径保留、记忆按决策日序、15 合成单测 OK、未并候选 3、未混叶37、LIVE/PROMOTION/X2_ACCEPT=false。回执诚实。**PASS_WITH_CONDITIONS**（见 §3）：(A) bench 未走终盘篱笆；(B) Origin 绿野新建 ≠ 箱上既有模块可直接覆盖；(C) 候选 3 日历仍外置。**本拍不 merge / 不签 `.ok`。**

## 1. 钉表再核

| 件 | 期望 | 实测 | 结果 |
|---|---|---|---|
| PR head SHA | `287cfe61` | `287cfe61de8cc893e96828d44c7939de4212de18` | **MATCH** |
| base | `main` @ `7197939` | `7197939d7949778cd7223158bf8d7190d0d86dbb` | **MATCH** |
| state | open / 未合并 | `state=open` `merged=false` `changedFiles=6` `+969/−0` | **MATCH** |
| `settle.py` blob sha8 | `f0648fe0` | Origin `get_file_contents` → `f0648fe0c8b25e90…` | **MATCH** |
| `ai_debate_memory_runner.py` blob sha8 | `8cdf9b61` | Origin → `8cdf9b613b4604f3…` | **MATCH** |
| `tests/test_trading_loop_horizon_settle.py` blob sha8 | `8d710643` | Origin → `8d7106431b748088…` | **MATCH** |
| Arch watch（箱上只读） | `d227a6a4` | `sha256sum` 前8 = `d227a6a4` | **MATCH** |
| 文件集 | 6 added | settle / `__init__` / memory_runner / research `__init__` / tests / Eng 回执 | **MATCH** · 无 paper/FROZEN/叶37 路径 |
| 单测宣称 | 15 OK | 隔离复跑 **15 OK**（0.054s） | **MATCH** |

PR 文件清单（全部 `added`，无删改主干既有路径）：

1. `docs/v2/audit/ENG_CAND4_SETTLE_FINAL_CLOSE_NEXT_SESSION_SIDE_DRAFT_20261027_ZH.md`
2. `quantlab/agents/trading_loop/__init__.py`
3. `quantlab/agents/trading_loop/settle.py`
4. `research/__init__.py`
5. `research/ai_debate_memory_runner.py`
6. `tests/test_trading_loop_horizon_settle.py`

## 2. 必审清单（对照 watch 候选 2 + 候选 4）

| # | 审点 | 结果 | 证据 |
|---|---|---|---|
| 1 | **候选 2 next-session**：默认入场 = 决策日**严格之后**第一根 bar；`on_or_after` 仅复现旧口径；bench 同 `entry_dt` | **PASS** | `DEFAULT_ENTRY_RULE="next_session"`；`_select_entry` / `_calendar_entry` 用 `>` vs `>=`；单测 `SameDayUpMove`：决策日 +50% 不进 next_session 收益；`on_or_after` 可入场决策日；bench 测锁定同 entry |
| 2 | **候选 4 终盘篱笆**：`available_at > now` 丢弃；缺列则「今日且未到常规收盘」丢弃；未来日非终盘 | **PASS_WITH_CONDITIONS** | `_is_final_close` + `_load_closes` 对 **instrument** 路径落实；A 股默认 15:00 Asia/Shanghai。**CONDITION A**：`benchmark_closes` 进 `_score_window` 仅 `_normalize_closes`，**未**经 `_load_closes` / `_is_final_close`——watch「inst/**bench**」双篱笆未满；合成测未覆盖「今日盘中 bench bar 渗入」 |
| 3 | **exit / pending**：entry 后第 H 个**已终盘**交易日；不足 pending 且不写 settled；日历显示窗未完 → 不取价 | **PASS** | `_score_window` / calendar 前置 `_pending("calendar_window_unfinished")` 且 loader 0 调用（单测锁）；`write_settlement` pending 不写 settled；已 settled 行保旧值 + 新行打 `settle_rule` |
| 4 | **取数扩窗**：上界仍短且 `end < today` → 仅扩 fetch 到 today，**不改 H** | **PASS** | `expanded_to_today`；国庆缺口单测：扩窗后 settled / 仍不足则 pending |
| 5 | **记忆排序（caf6792 族）**：`load_prior_settlements` 按 `(session\|resolution_date, 行序)` 降序，非写入序 | **PASS** | 先写 6 月再回填 1 月 → `limit=1` 仍取 6 月；pending 过滤；无 session 时用 resolution_date |
| 6 | **范围仍为研究侧稿**：不碰 paper/FROZEN/权重/live；未并候选 3；未混叶37 | **PASS** | PR 6 文件全为新建研究/测试/回执；常量 `LIVE=False` `PROMOTION_APPROVED=False` `X2_ACCEPT=False`；回执与 PR body 明示未并 PR #6；文件名/路径无 leaf37 |
| 7 | **回执诚实**：Origin main 无既有模块 → **新建**（非伪称「改箱上既有」） | **PASS** | Eng 回执 + PR body 均写明 Origin `main`（`7197939`）当时无 `compute_horizon_returns` / `load_prior_settlements` / watch 文；与 Origin 盘证一致 |
| 8 | **默认安全 / 旧口径复现** | **PASS** | 默认 next_session；`on_or_after` API 保留；已 settled decision_log 不覆写 |
| 9 | **禁项核（本拍）** | **PASS** | 未 merge；未点 APPROVE；未签研究 `.ok`；未改 paper/FROZEN/权重；叶37 B1 `.ok`/脚本本拍**未写**（并行签窗独立）；无 SendToUser |

## 3. CONDITIONS（须后续消化；不阻塞「侧稿可审过」）

| ID | CONDITION | 等级 | 建议 Owner |
|---|---|---|---|
| **A** | **bench 终盘篱笆缺口**：`benchmark_closes` 未走 `_is_final_close` / `available_at`；盘中假今日 bench 理论上可渗入 alpha | 中 | Eng 补丁：对 bench 复用 `_load_closes`（同 now/tz/regular_close）；补合成测 |
| **B** | **Origin 绿野 ≠ 箱上可覆盖**：箱上已有 `quantlab/agents/trading_loop/settle.py`（仍 `ON OR AFTER`、未落地 cand2）与体积更大的 `research/ai_debate_memory_runner.py`（`load_prior_settlements` 签名含 `instrument=` / `non_null_only=` 等）。**禁止**把本 PR 文件整棵覆盖进箱上主干；并入箱须**行为移植**+适配既有 API，另开 Arch 窗 | 高（落地时） | Eng 出箱上 port 计划；Arch 另审；本 Origin PR 可先合 Origin（主裁）但≠箱上 ACCEPT |
| **C** | **候选 3 仍外置**：本 PR 故意不并 SSE 日历 PR #6；无 calendar 时「窗未完不取价」依赖调用方传入；国庆单测用内联合成日历——可接受侧稿，全链路仍待 cand3 | 低 | 候选 3 合并后接线；非本 PR 阻断 |

## 4. 残留风险（知情）

- 真行情 / decision_log 重算仍须另签 Arch `.ok`（本侧稿与单测明确不读 parquet）。
- 箱上既有 settle 头注释仍留「wait:」草稿 + `>=` 入场——**本 PR 不自动修复箱上**（见 CONDITION B）。
- `as_of` 记忆篱笆用 decision stamp（session 优先）；与 G6「resolution_date≤as_of」细义若需严格对齐，后续可加参，不构成本次 FAIL。

## 5. 硬禁确认

| 项 | 状态 |
|---|---|
| merge PR #7 | **未做**（仍 open） |
| Origin APPROVE / REQUEST_CHANGES | **未做**（审票仅落箱 audit） |
| 改 paper / FROZEN / 权重 | **未做** |
| 签研究 `.ok` | **未做** |
| 碰叶37（脚本 / B1 `.ok` / QUIET / VOID） | **未做** |
| 真行情 / `--allow-real-data` | **未做** |
| SendToUser / 报 Leo | **未做** · leo_notify=false · live=false |

## 6. 交付摘要（回主 / Eng）

- **verdict**：**PASS_WITH_CONDITIONS**
- **审票路径**：`docs/v2/audit/ARCH_ENG_CAND4_SETTLE_FINAL_CLOSE_NEXT_SESSION_SIDE_DRAFT_REVIEW_20261027_ZH.md`
- **head/关键 MATCH**：head `287cfe61`；settle `f0648fe0`；memory_runner `8cdf9b61`；tests `8d710643`；watch `d227a6a4`
- **CONDITIONS**：A bench 篱笆；B 箱上 port 禁覆盖；C cand3 外置
- **确认**：未 merge；未碰叶37；15 合成单测 OK；≠X2 ACCEPT；live=false
