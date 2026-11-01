# Arch 合入核：候选3 箱上 port APPLY（只核不 enable）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器 APPLY 合入核） |
| 时刻 | `2026-10-26T14:18:30-04:00`（America/New_York；墙钟 `2026-10-26 14:18 ET`） |
| **结论** | **PASS** |
| 本回合动作 | **只核**：不 enable；不签 enable `.ok`；不挂 QUIET；不 merge Origin #6；不代跑纸面；不改生产源码；≠X2；live=false；promotion=false；**不报 Leo**；**不混** A18 §5.2（已 SIGNED 另线）与叶25 X2 selfcheck（16:15）；勿动叶25 CONSUMED；禁消费 `9e4359f9` |
| 触发 | 主 ~14:15 ET priority 令（TEAM_STATE；Eng APPLY 回执已落盘） |
| 对照前轮 | port 复审 `ARCH_CAND3_BOX_PORT_REVIEW_20261026_ZH.md` sha8 **`7276ed4d`**；意图审 `c5b0ce67` |

## 0. 一句话

箱上 port **已 APPLY 且合入核 PASS**：Eng 回执 `5e28aff1` 与生产四钉（tc`d2b6046c`/settle`a92b7ccf`/rl`5fe238f2`/sources`c8102489`）+ HEAD `da9fde6` **全 MATCH**；行为闸落实（settle **无代码态** `pd.bdate_range`；SSE/`CUTOFF_ET`/`data_freshness` 保留；legacy **DeprecationWarning**；sources `calendar_required`）；国庆对生产本核复跑 **9 passed**。**合入核可关闭**。**enable 仍禁**（本核不签 enable `.ok` / 不挂 QUIET / 不授权纸面）。本核**不构成** enable / merge / 纸面 `.ok` 授权。

## 1. 钉表（合入核再核）

| 件 | 路径 | 期望 sha8 | 实测 sha8 | 结果 |
|---|---|---|---|---|
| Eng APPLY 回执 | `ENG_CAND3_BOX_PORT_APPLY_RECEIPT_20261026_ZH.md` | `5e28aff1` | `5e28aff1…` | **MATCH** |
| 前轮 port 复审 | `ARCH_CAND3_BOX_PORT_REVIEW_20261026_ZH.md` | `7276ed4d` | `7276ed4d…` | **MATCH** |
| DIFF（侧稿包） | `DIFF_cand3_box_port_20261026.diff` | `24e055fa` | `24e055fa…` | **MATCH** |
| 生产 trade_calendar | `quantlab/portfolio/trade_calendar.py` | `d2b6046c` | `d2b6046c…` | **MATCH** |
| 生产 settle | `quantlab/agents/trading_loop/settle.py` | `a92b7ccf` | `a92b7ccf…` | **MATCH**（相对 `.schemas`；异于侧稿 `c423e96e` 仅 import，预期） |
| 生产 research_loop | `quantlab/portfolio/research_loop.py` | `5fe238f2` | `5fe238f2…` | **MATCH** |
| 生产 sources | `quantlab/data/sources.py` | `c8102489` | `c8102489…` | **MATCH** |
| HEAD | `/workspace/QuantLab` | `da9fde6` | `da9fde6a…` | **MATCH**（未 commit） |
| Eng apply 国庆日志 | `port/pytest_cand3_box_port_apply_20261026.log` | `4326a614` | `4326a614…` | **MATCH** |
| 本核复跑国庆日志 | `/tmp/cand3_apply_verify_pytest.log` | （复跑） | `4326a614…`（文案同 9 passed） | **OK** |

## 2. 检查清单

| # | 检查项 | 结果 | 证据 |
|---|---|---|---|
| 1 | Eng APPLY 回执 sha MATCH | **PASS** | `5e28aff1fc84…` |
| 2 | 生产四文件 sha MATCH 主核盘表 | **PASS** | 全长见上表；与 Eng 回执 Apply 后生产钉一致 |
| 3 | settle **无代码态** `pd.bdate_range`（注释可提） | **PASS** | AST walk 代码命中 **NONE**；仅 L79 注释提及 |
| 4 | settle import 相对 `.schemas`；可 import | **PASS** | `from .schemas import force_research_flags`；`compute_horizon_returns` import OK |
| 5 | 保留 SSE `trade_cal.parquet` + `CUTOFF_ET=(6,30)` + 纸面 `data_freshness` | **PASS** | tc `SRC`/`CUTOFF_ET`；rl `data_freshness()` 仍在；import smoke `CUTOFF_ET=(6,30)` |
| 6 | legacy `_legacy_freshness` → DeprecationWarning | **PASS** | 烟测 `DeprecationWarning_count=1`；文案指向 `data_freshness()` |
| 7 | sources 可选 `calendar_required`；无静默 BDay | **PASS** | `_a_daily` 标 `calendar_required`；注释禁 BDay/weekday fallback |
| 8 | 国庆测对生产可 9 passed | **PASS** | `pytest -q port/test_trade_calendar_settle_port.py` → **9 passed**（0.36s）；复跑后四钉仍 MATCH |
| 9 | py_compile 四文件 OK | **PASS** | qlvenv py_compile OK |
| 10 | **未 enable**；无新 enable `.ok` | **PASS** | `docs/v2/audit/cand3_sse_calendar_20261026/*.ok` 无；无 `*CAND3*ENABLE*`；本核未签任何 `.ok` |
| 11 | 禁整文件合 Origin #6；HEAD 未 commit | **PASS** | 箱上为 port 增量合入；HEAD 仍 `da9fde6` |
| 12 | 错开 A18 / 叶25 | **PASS** | 本核未改 A18 `.ok`（另线已 SIGNED `dc51a0b3`）；叶25 selfcheck `.ok` 仍 ABSENT；未挂 QUIET |

## 3. 站立约束（不挡合入核关闭）

1. **enable 仍禁**：合入核 PASS ≠ enable；纸面 enable / 签 enable `.ok` / 晋级须 **另轮 Arch + 主令**；本核不授权。
2. **HEAD 未 commit**：预期；是否 commit 由主/Eng 另令；不挡合入核关闭。
3. **隔离**：勿混 A18 §5.2（窗内另线）与叶25 X2 selfcheck（16:15–17:45）；勿动叶25 CONSUMED（禁 RESTORED 十二票含 `3c297052`）；禁消费 `9e4359f9`；≠X2；live=false。

## 4. 本回合未做（硬约束复核）

- 未 enable；未签任何 enable / 纸面 / 候选3 `.ok`；未挂 QUIET；未 merge Origin #6；未改 `quantlab/**`（只读核验）；未代跑纸面；未 SendToUser / SendToAgent；不报 Leo；live=false；promotion=false；≠X2；未混 A18/叶25 签窗动作。

## 5. 给主的收口

| 项 | 值 |
|---|---|
| 结论 | **PASS** |
| 审回执 | `docs/v2/audit/cand3_sse_calendar_20261026/ARCH_CAND3_BOX_PORT_APPLY_VERIFY_20261026_ZH.md`（落盘后 sha8 见 SHA256SUMS） |
| 合入核 | **可关闭** |
| enable | **仍禁**（确认） |
| 生产钉 | tc`d2b6046c` / settle`a92b7ccf` / rl`5fe238f2` / sources`c8102489` / HEAD `da9fde6` |
| 建议下一手 | 主标合入核关闭即可；**勿**令 enable；叶25 仍等 16:15 SIGN；A18 另线 MATCH→Data/Eng |
