# Arch 复审：Eng 候选4 FIX_A（bench 终盘篱笆）· 只审不 merge

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器；对照首审 `a2051e37` §3 CONDITION A） |
| 时刻 | `2026-10-27T18:48:00-04:00`（America/New_York；墙钟 `2026-10-27 18:48 ET`） |
| **结论** | **PASS**（CONDITION A **关闭**；B/C 仍记开放但不挡侧稿复审） |
| 对照首审 | `docs/v2/audit/ARCH_ENG_CAND4_SETTLE_FINAL_CLOSE_NEXT_SESSION_SIDE_DRAFT_REVIEW_20261027_ZH.md` sha8 **`a2051e37`** |
| 对照 watch | `docs/v2/ARCH_GITHUB_WATCH_ZH.md` sha8 **`d227a6a4`**（仍钉） |
| 对象 | Origin PR [leo-vino/QuantLab #7](https://cursor.com/codebase/leo-vino/QuantLab/pull/7) · branch `cursor/settle-final-close-next-session-33c5` · head **`e04227a1`**（全长 `e04227a13be688e3b3a194c3b99c0ee821e3b710`）· 相对旧 head `287cfe61` +1 commit · **open / 未合并** |
| Eng 回执 | `docs/v2/audit/ENG_CAND4_SETTLE_FINAL_CLOSE_NEXT_SESSION_SIDE_DRAFT_20261027_ZH.md` git-sha8 **`e5bba36f`** / 箱上内容 sha256 **`cb7bb16b`**（含 FIX_A 附录） |
| 本回合动作 | **只复审 A**；**不 merge**；**不** Origin APPROVE；**不开**箱上 port；**不签**研究 `.ok`；**不碰叶37**；live=false；≠X2 ACCEPT；**不报 Leo**；leo_notify=false |
| 轻量复跑 | 隔离 scratch 抽出 PR 6 文件 → `PYTHONPATH=… python3 -m unittest tests.test_trading_loop_horizon_settle -v` → **Ran 17 tests … OK**（0.093s；合成夹具；无真行情；无 `.ok`） |

## 0. 一句话

Origin PR #7 FIX_A head **`e04227a1` MATCH**：`_score_window` 对 `benchmark_closes` 已复用 `_load_closes`（同 `now` / `tz` / `regular_close` / 取价上界）；入场/出场仍锁标的 `entry_dt` / `exit_dt`；篱笆去掉定价出场所需 bench 终盘点 → `pending`/`insufficient_benchmark_final_closes`，盘中假今日 bench 不再渗入 alpha。合成测 **+2** 覆盖 A，合计 **17 OK**。**CONDITION A 关闭。** B（箱上 port）与 C（cand3 外置）仍开放但不挡本拍。**不 merge / 不开 port / 不 APPROVE。**

## 1. MATCH 表

| 件 | 期望 | 实测 | 结果 |
|---|---|---|---|
| PR head SHA | `e04227a1` | `e04227a13be688e3b3a194c3b99c0ee821e3b710` | **MATCH** |
| 旧 head（父） | `287cfe61` | FIX_A commit parent = `287cfe61de8cc893…` | **MATCH** |
| base | `main` @ `7197939` | `7197939d7949778cd7223158bf8d7190d0d86dbb` | **MATCH** |
| state | open / 未合并 | `state=open` `merged=false` `changedFiles=6` | **MATCH** |
| `settle.py` git-sha8 | `9d98ad4f` | Origin blob + 隔离 `git hash-object` = `9d98ad4f…` | **MATCH** |
| `tests/…horizon_settle.py` git-sha8 | `56e381fc` | Origin + 隔离 = `56e381fc…` | **MATCH** |
| `ai_debate_memory_runner.py` | `8cdf9b61`（未改） | Origin blob `8cdf9b61…` | **MATCH** |
| Eng 回执 git-sha8 | `e5bba36f` | Origin + 箱上 `git hash-object` = `e5bba36f` | **MATCH** |
| Eng 回执箱上内容 sha256 | `cb7bb16b` | `sha256sum` 前8 = `cb7bb16b` | **MATCH** |
| Arch watch（箱上只读） | `d227a6a4` | `sha256sum` 前8 = `d227a6a4` | **MATCH** |
| 首审票 | `a2051e37` | 箱上仍在位 | **MATCH** |
| 单测宣称 | 17 OK | 隔离复跑 **17 OK**（0.093s） | **MATCH** |
| 箱上既有 `settle.py` | 未覆盖 | 箱上内容 sha256 前8 **`a92b7ccf`**（≠ PR blob；未开 port） | **MATCH（禁覆盖成立）** |

## 2. CONDITION A 复审（首审原文对照）

首审 `a2051e37` §3 A：

> **bench 终盘篱笆缺口**：`benchmark_closes` 未走 `_is_final_close` / `available_at`；盘中假今日 bench 理论上可渗入 alpha。建议：对 bench 复用 `_load_closes`（同 now/tz/regular_close）；补合成测。

| 审点 | 结果 | 证据 |
|---|---|---|
| bench 走 `_load_closes` | **PASS** | `_score_window`：`bench = _load_closes(benchmark, session_ts, fetch_end, now=now, tz=tz, regular_close=regular_close)`；不再仅 `_normalize_closes` |
| 同篱笆参数下发 | **PASS** | `compute_horizon_returns` 两处调用 `_score_window` 均传 `now=now_m`、`regular_close=regular_close`；取价上界仍 `fetch_end`/`today` |
| 入/出场锁标的 | **PASS** | 注释与实现：`entry_dt`/`exit_dt` 来自标的序列；bench 用 `asof(entry_dt)`/`asof(exit_dt)`，不独自选第一根 |
| 缺 bench 终盘 → pending | **PASS** | `bench.empty` 或 `max < exit_dt` 或 asof NaN/≤0 → `_pending("insufficient_benchmark_final_closes")`，不写 alpha |
| 合成覆盖 A | **PASS** | `test_today_still_trading_bench_bar_does_not_change_alpha`（盘中 999 不渗入）；`test_available_at_after_now_on_exit_bench_forces_pending`（`available_at>now` → pending，稍后 settled） |
| 原 15 项仍绿 | **PASS** | 隔离 17 OK = 原 15 + A 的 2 |

**判定：CONDITION A 关闭。**

## 3. CONDITIONS 状态（本拍后）

| ID | 状态 | 说明 |
|---|---|---|
| **A** | **CLOSED** | bench 与 inst 同终盘/`available_at` 篱笆；合成测覆盖；见 §2 |
| **B** | **OPEN**（不挡本拍） | Origin 绿野新建 ≠ 箱上可覆盖；箱上既有 `settle.py`（`a92b7ccf`）仍独立。**禁止**整棵覆盖；并入箱须行为移植+另开 Arch 窗。本拍**未开 port** |
| **C** | **OPEN**（不挡本拍） | 候选 3 / SSE 日历 PR #6 仍外置；本 PR 故意不并。全链路待 cand3 |

## 4. 硬禁确认

| 项 | 状态 |
|---|---|
| merge PR #7 | **未做**（仍 open / `merged=false`） |
| Origin APPROVE / REQUEST_CHANGES | **未做**（复审票仅落箱 audit） |
| 开箱上 port / 覆盖箱上 settle | **未做** |
| 改 paper / FROZEN / 权重 | **未做** |
| 签研究 `.ok` | **未做** |
| 碰叶37 | **未做** |
| 真行情 / `--allow-real-data` | **未做** |
| SendToUser / 报 Leo | **未做** · leo_notify=false · live=false |

## 5. 交付摘要（回主 / Eng）

- **verdict**：**PASS**（A 关闭；B/C 仍开放但不挡）
- **复审票路径**：`docs/v2/audit/ARCH_ENG_CAND4_FIX_A_REREVIEW_20261027_ZH.md`
- **head/settle/tests MATCH**：head `e04227a1`；settle `9d98ad4f`；tests `56e381fc`；memory_runner `8cdf9b61`；Eng 回执 `e5bba36f` / 箱上 sha256 `cb7bb16b`；watch `d227a6a4`；首审 `a2051e37`
- **unittest**：隔离 **Ran 17 tests … OK**
- **A 关闭**；**B** 箱上 port 仍须另窗；**C** cand3 仍外置
- **确认**：未 merge；未 APPROVE；未开 port；未碰叶37；≠X2 ACCEPT；live=false
