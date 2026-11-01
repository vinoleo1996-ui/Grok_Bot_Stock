# Arch 审阅：候选3 Origin PR #6 意图（只审不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态意图审） |
| 时刻 | `2026-10-26T13:52:00-04:00`（America/New_York；墙钟 `2026-10-26 13:52 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 本回合动作 | **不签**任何 `.ok`；**不挂 QUIET**；**不代跑**；**不 merge**；**不改**主干代码；禁整文件合箱；≠X2；live=false；promotion=false；**不报 Leo**；**不混** A18 / 叶25 X2 selfcheck / 叶25 CONSUMED `.ok`（`3c297052`/`d37a157e`） |
| 触发 | 主 13:47 ET priority 令（TEAM_STATE）；Eng 回执已落盘 |
| 对照 | Eng 回执 sha8 **`f7db7c67`** · Origin PR [#6](https://cursor.com/codebase/leo-vino/QuantLab/pull/6) head **`986627db`** · 箱上 HEAD **`da9fde6`** · 日扫采纳 `ARCH_GITHUB_WATCH_ZH.md` sha **`df0c3d81`** |

## 0. 一句话

Origin [#6](@`986627db`) 的**设计意图**对齐 Arch 日扫候选3（alphalens #74 / `60755d1`）：国庆窗合成断言、无日历 → `calendar_required`、legacy 标废弃、禁 `bdate_range` 持仓到期。云端 Eng 报 16 passed。但 PR 相对 Origin `main`（`7197939d`）是「**新增 stub 模块**」树；箱上 `da9fde6` 已有完整纸面 `research_loop` / `trade_calendar`（SSE `trade_cal.parquet` + ET cutoff）且 `settle.py` 仍 `pd.bdate_range`。**同意 Eng 建议2：另开箱上 port DIFF，勿整文件合箱**。合箱前纸面主路径不变；未合入前 **不谈 enable**。本审**不构成** merge / `.ok` / 晋级授权。

## 1. 钉表

| 件 | 路径 / 引用 | 期望 sha8 | 实测 | 结果 |
|---|---|---|---|---|
| Eng 回执 | `docs/v2/audit/cand3_sse_calendar_20261026/ENG_CAND3_SSE_CALENDAR_RECEIPT_20261026_ZH.md` | `f7db7c67` | `f7db7c67ea81cffaa86837b42b7b2063c7f7ca6a50cfd8331fcc8eb0a4c2344a` | **MATCH** |
| Arch 日扫采纳 | `docs/v2/ARCH_GITHUB_WATCH_ZH.md`（候选3 节） | `df0c3d81` | `df0c3d81208846c18bc18e38d0f093647bc9744ce454eef865b66a6821a273a4` | **MATCH** |
| Origin PR head | PR #6 `cursor/sse-calendar-freshness-settle-1269` | `986627db` | `986627dbfb5b4c518c6abc5a36d1f11c438b240a` | **MATCH** |
| Origin base | `main` | （Eng 钉） | `7197939d7949778cd7223158bf8d7190d0d86dbb` | 记录 |
| 箱上 HEAD | `/workspace/QuantLab` | `da9fde6` | `da9fde6a0037da6e2d10f09f65b14f4f0997f952` | **MATCH** |
| 箱 `trade_calendar.py` | `quantlab/portfolio/trade_calendar.py` | — | sha8 **`ef44e7cd`**（全长 `ef44e7cd04911523dbb94c19500393cc0cf423c6728a35826bf0cbb123925eec`） | 对照 |
| 箱 `research_loop.py` | `quantlab/portfolio/research_loop.py` | — | sha8 **`d3ded87e`**（全长 `d3ded87e111bb6d12c6ab7e1dfba3e8511fe8f02815322b98da438a6c1ea4630`） | 对照 |
| 箱 `settle.py` | `quantlab/agents/trading_loop/settle.py` | — | sha8 **`808f77d6`**（全长 `808f77d6f4ef8e3b4861b91c1ffc6af0c3418df479623a448508609e3326601a`） | 对照 |

云端：`bc-f6cbb47f-6463-5fc7-b05e-d7ce287b1269`；Eng：`pytest tests/test_trade_calendar_settle.py tests/test_data_execution.py` → **16 passed**。本审 `checks_read(PR#6)` rollup=**empty**（无物化 CI 页；采信 Eng 回执云测声明，**不**当作箱上已绿）。

## 2. PR 意图核对（相对日扫候选3）

| # | 意图点 | 结果 | 证据（Origin #6 @`986627db`） |
|---|---|---|---|
| 1 | **国庆断言**（2025-10-01..10-07 到期/期望日不落休市） | **PASS** | `tests/test_trade_calendar_settle.py`：`TradeCalendarNationalDay` / `SettleNationalDay` / fake parquet；`holdings_expiry("2025-09-30",1)`→`2025-10-08`；`expected_session` 假期中停在 `2025-09-30`；对比 weekday/`bdate_range` 会落 `2025-10-01` |
| 2 | **calendar_required**（无日历不静默 weekday） | **PASS** | `data_freshness` 缺日历 → `status=calendar_required`；`DataFeed._a_daily` 无 `expected_session` 时 `attrs["freshness"]="calendar_required"`，不再 `BDay`+`weekday>=5` |
| 3 | **legacy deprecated** | **PASS** | `trade_calendar._legacy_freshness`：`DeprecationWarning` + 注释「weekday / CN holidays not modeled」；单测断言警告且假期 weekday 会落闭市日 |
| 4 | **禁 bdate_range 意图**（持仓到期/交易日切片） | **PASS**（意图） | 新 `agents/trading_loop/settle.py`：`open_day_range` / `holdings_expiry` / `settle_asof` 走 `open_days`/`advance_open_days`；模块 docstring 明文禁 `pd.bdate_range` |
| 5 | 不改纸面权重 / 不物化 / live=false | **PASS** | PR body + `RESEARCH_CONTINUITY.md`：live=false；promotion_approved=false；范围外 wrapper/X2/leaf25/daily_basic/enable |
| 6 | 与箱上分叉风险 | **CONDITIONS** | 见 §3：PR 对 Origin 是 *added* stub；箱上已是完整生产模块 → **禁整文件合箱** |
| 7 | Eng「另开箱上 port DIFF」 | **同意** | 见 §4 CONDITIONS |

变更文件（7）：`trade_calendar.py`(+277 added)、`research_loop.py`(+27 re-export stub)、`settle.py`(+83 added)、`sources.py`(_a_daily 闸)、`tests/test_trade_calendar_settle.py`(+186)、`trading_loop/__init__.py`、`docs/RESEARCH_CONTINUITY.md`。

## 3. 箱上对照（只读；分叉风险）

| 箱上现状 | 与 PR 关系 | 风险 |
|---|---|---|
| `trade_calendar.py`：读 **`data/v2/tushare_raw/trade_cal.parquet`**；`CUTOFF_ET=(6,30)`；`expected_session`/`open_days`/`prev_trading_day`/`cross_check` 已纸面在用 | PR 新增平行 API（多路径探测 `data/trade_cal.parquet` 等；默认 close_hour=18 Asia/Shanghai；**无**箱上 ET cutoff / Data 交叉校验） | 整文件覆盖会丢掉纸面 cutoff 与路径钉 |
| `research_loop.py`：完整纸面环；`data_freshness()` L636+ 已走 SSE + marker/tables；`_legacy_freshness()` L704+ 仍 weekday、**无** DeprecationWarning | PR 的 `research_loop.py` 仅 27 行 re-export stub | 整文件覆盖会**旁路/摧毁**纸面闸 |
| `settle.py`：生产结算路径；mock 分支 **L79 `pd.bdate_range`** | PR 的 settle 是全新 stub（`open_day_range`/`holdings_expiry`），非箱上 settle 补丁 | 整文件覆盖会丢掉现网 settle 逻辑；mock 路径的 bdate **需外科 port** |
| 箱 `quantlab/data/sources.py` `_a_daily` 仍 `BDay`/weekday（约 L179–180） | PR 已改为 `expected_session` / `calendar_required` | 可 port 该闸，但须保留箱上其它 DataFeed 行为 |

**结论**：PR 是 Origin 空树补齐，**不是**箱上生产树的可直接应用补丁。分叉风险 = **P0 合箱禁止**（整文件）。

## 4. CONDITIONS（可执行下一步）

1. **Eng 另开箱上 port 包（侧稿 DIFF）**——**同意 Eng 建议2**。范围建议：
   - **保留**箱上 `trade_calendar` 的 `data/v2/tushare_raw/trade_cal.parquet` 路径、`CUTOFF_ET`、`cross_check`、纸面 `data_freshness` 主路径。
   - **移植意图**：国庆/假期合成单测（可新建 `tests/test_trade_calendar_settle.py` 或扩箱上既有测）；`settle.py` mock（及任何「N 交易日」到期）改走 `open_days`/`first_trading_day_on_or_after`/`advance` 等价物，**删除**该路径 `pd.bdate_range`。
   - **legacy**：箱上 `_legacy_freshness` 加 `DeprecationWarning`（或等价标注废弃），**不得**再作默认新鲜度闸。
   - **可选**：`DataFeed._a_daily` 无日历时标 `calendar_required`（对齐 PR），但不得破坏箱上其它 fetch/cache 契约。
   - **禁**：整文件用 PR stub 覆盖 `research_loop.py` / `trade_calendar.py` / `settle.py`。
2. **合入箱上 port 后**再交 Arch **port DIFF 复审**；通过前 **不 enable**、不签纸面 enable `.ok`、不谈晋级。
3. **未合入前**：纸面主路径行为不变；Origin #6 可保持 open 作意图/云测对照，**本审不 merge**。
4. **隔离**：勿混 A18 §5.2（14:15 SIGN 另线）、叶25 X2 selfcheck（16:15–17:45 另线）、CONSUMED `3c297052`/`d37a157e`。
5. 真实数据 / wrapper / X2 / leaf25 / daily_basic：**仍范围外**。

## 5. 本回合未做（硬约束复核）

- 未签任何 `.ok`；未挂 QUIET；未代跑 pytest/纸面；未 merge PR #6；未改主干/`quantlab/**` 代码；未整文件合箱；未 SendToUser / SendToAgent；不报 Leo；live=false；promotion=false；≠X2。

## 6. 给主的收口

| 项 | 值 |
|---|---|
| 结论 | **PASS_WITH_CONDITIONS** |
| 审回执 | `docs/v2/audit/cand3_sse_calendar_20261026/ARCH_CAND3_ORIGIN_PR6_INTENT_REVIEW_20261026_ZH.md`（落盘后 sha8 见 SHA256SUMS） |
| 同意 Eng 建议2 | **是**（箱上 port DIFF；勿整文件合箱） |
| 下一手 | 主令 Eng 交箱上 port 侧稿 → Arch 复审 port → 再谈 enable |
