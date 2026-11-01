# Arch 复审：Eng cand4 CONDITION B 箱上 port（终盘篱笆 / FIX_A）· 只审不 merge

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器；对照首审 `a2051e37` §3 CONDITION B + FIX_A 复审 `76a050ef`） |
| 时刻 | `2026-10-27T19:01:59-04:00`（America/New_York；墙钟 `2026-10-27 19:01 ET`） |
| **结论** | **PASS**（CONDITION B **关闭**；C 仍开放；不挡本拍） |
| 对照首审 | `docs/v2/audit/ARCH_ENG_CAND4_SETTLE_FINAL_CLOSE_NEXT_SESSION_SIDE_DRAFT_REVIEW_20261027_ZH.md` sha8 **`a2051e37`** |
| 对照 FIX_A 复审 | `docs/v2/audit/ARCH_ENG_CAND4_FIX_A_REREVIEW_20261027_ZH.md` sha8 **`76a050ef`** |
| Eng 回执 | `docs/v2/audit/ENG_CAND4_BOX_PORT_SETTLE_20261027_ZH.md` content sha8 **`f3f876e7`** / git hash-object **`b0a620df`** |
| Origin 参考（禁覆盖） | PR [leo-vino/QuantLab #7](https://cursor.com/codebase/leo-vino/QuantLab/pull/7) head **`e04227a1`** · settle git-sha8 **`9d98ad4f`**（`/tmp/cand4_fix_a_settle.py` 17132 B） |
| 本回合动作 | **只审**箱上 port；**不 merge**；**不** Origin APPROVE；**不改** settle/tests；**不签**研究 `.ok`；**不碰叶37**；live=false；≠X2 ACCEPT；**不报 Leo**；leo_notify=false |
| 轻量复跑 | `PYTHONPATH=/workspace/QuantLab python3 -m unittest tests.test_cand4_box_port_settle_fence -v` → **Ran 7 tests … OK**（0.096s；TemporaryDirectory 合成 parquet；无真行情；无 `.ok`） |

## 0. 一句话

箱上 `settle.py` 已做 **FIX_A 终盘篱笆行为移植**（instrument **与** benchmark 同走 `_load_closes` / `_is_final_close`）；post content **`862a2c29` ≠** Origin FIX_A blob **`9d98ad4f`**（13010 B ≠ 17132 B；禁整棵覆盖成立）；调用面与 **ON OR AFTER** 入场默认保留；缺 bench 终盘 → `pending`/`insufficient_benchmark_final_closes`。合成测 **7 OK**（含篱笆 + 非字节等同）。**CONDITION B 关闭。** C（cand3）仍外置。**未 merge / 未 APPROVE / 未碰叶37。**

## 1. MATCH 表

| 件 | 期望 | 实测 | 结果 |
|---|---|---|---|
| Eng 回执 content sha256 | `f3f876e7…` | `f3f876e7c1c4a5872d5edd8e44785992010090cc9159925f4c626b573d41275d` | **MATCH** |
| Eng 回执 git hash-object | `b0a620df` | `b0a620df65676a53076aead4a0416e0e79b4319b` | **MATCH** |
| settle **post** content sha256 | `862a2c29…` | `862a2c29826b3dda2911bb60c280ff17100eb194a555ebbf133326eee1f348a4`（13010 B） | **MATCH** |
| settle **post** git hash-object | `88f3c97e` | `88f3c97e2bc1a58b5d9e9dc1efd1a3b8f3a9aadb` | **MATCH** |
| settle vs Origin FIX_A | ≠ `9d98ad4f` / 非整盖 | Origin blob `9d98ad4f…` 17132 B；`cmp` exit 1；box 无 `DEFAULT_ENTRY_RULE` | **MATCH（禁覆盖成立）** |
| settle **pre** 钉（开窗前） | `a92b7ccf`（FIX_A 复审 / Eng） | 本拍未再物化 pre 文件；以 FIX_A 复审 `76a050ef` §1 与 Eng 回执钉为准；post 已变且 ≠ Origin | **认钉（pre 文件未重现）** |
| tests content sha256 | `772547f5…` | `772547f5a76ea7ce85625f4a6f17fadfe22f80e921e32c871d1cdfcecce5158f` | **MATCH** |
| tests git hash-object | `5edfcd36` | `5edfcd36e4004e4242a377c7aed0d04f5e07f36d` | **MATCH** |
| FIX_A 复审票 | `76a050ef` | `76a050ef0bc6eaaf0951cb5250d78d7df14ddc5cbd9937fa05986e171c8f2f95` | **MATCH** |
| 首审票 | `a2051e37` | `a2051e37140e4e12871f31410fbbadcd39e37cf2b2b1a223c9fff1ef3448a6a5` | **MATCH** |
| `research/ai_debate_memory_runner.py` | Eng：`e1736d80` 本拍未改 | content sha256 前8 **`e1736d80`**；mtime 仍 `2026-10-25` 基盘；**本拍未写** | **MATCH（UNCHANGED）** |
| `quantlab/agents/trading_loop/memory_runner.py` | 箱上 ABSENT | **ABSENT**（目录仅 settle/state_machine/…；勿伪造） | **MATCH** |
| Origin PR #7 | open / 未合并 | `state=open` `merged=false` head `e04227a1` | **MATCH** |
| 单测宣称 | 7 OK | Arch 复跑 **Ran 7 tests … OK**（0.096s） | **MATCH** |
| 叶37 live `.ok` / QUIET | ABSENT（勿碰） | 无 live `.ok`；QUIET 仅 `_lifted/` 历史；本拍**未写**叶37 | **MATCH** |

## 2. CONDITION B 复审（首审原文对照）

首审 `a2051e37` §3 B：

> **Origin 绿野 ≠ 箱上可覆盖**：箱上已有 `settle.py`（仍 ON OR AFTER）与体积更大的 `research/ai_debate_memory_runner.py`。**禁止**把本 PR 文件整棵覆盖进箱上主干；并入箱须**行为移植**+适配既有 API，另开 Arch 窗。

主收窄后本窗验收：只移植终盘篱笆 / FIX_A；保留调用面与 ON OR AFTER；不 merge；cand3 仍禁。

| 审点 | 结果 | 证据 |
|---|---|---|
| 行为移植非整盖 | **PASS** | post settle `862a2c29` ≠ Origin `9d98ad4f`；13010≠17132 B；保留 `allow_mock` / `settle_log` / `instrument,session,horizon_trading_days`；无 Origin `DEFAULT_ENTRY_RULE`/`next_session` 默认 |
| 相对 pre 仅篱笆/FIX_A | **PASS**（认钉） | Eng §2 最小集：`_is_final_close` + `_load_closes(..., now=)` 双路径；入场默认仍 `>= session`；next_session/记忆日序刻意推迟 |
| 调用面保留 | **PASS** | `inspect.signature` = `(instrument, session, horizon_trading_days, *, benchmark, etf_path, allow_mock, now, tz, regular_close)`；测 `test_api_kwargs_backward_compatible` OK |
| 入场默认仍 ON OR AFTER | **PASS** | `inst[inst.index >= session_ts]`；测 `test_on_or_after_entry_contract_preserved`（决策日可为 entry）OK；无 `DEFAULT_ENTRY_RULE` |
| instrument+bench 同 `_is_final_close` | **PASS** | `compute_horizon_returns` 对 `inst` 与 `bench` 均调 `_load_closes(..., now=now_m, tz=tz, regular_close=regular_close)` |
| 缺 bench → pending | **PASS** | `bench.empty` / `max < exit_day` / 入出场日缺终盘 / 价格无效 → `reason=insufficient_benchmark_final_closes`，不写 alpha |
| 合成覆盖篱笆 | **PASS** | 盘中假今日 bench 999 不渗入；exit 日 `available_at>now` → pending 稍后 settled；无 available_at 今日未收盘 → `insufficient_final_closes` |
| 非字节等同 Origin | **PASS** | `test_not_byte_identical_to_origin_greenfield` 钉 ON OR AFTER / `_is_final_close` / `insufficient_benchmark_final_closes` / 旧 API 标记 |
| next_session / 记忆日序 | **OPEN（不挡 B）** | Eng §5 本窗推迟；符合主收窄；不构成本拍 FAIL |
| 不 merge / 不 APPROVE | **PASS** | Origin PR #7 仍 `open`/`merged=false`；本拍无 Origin 写评 |
| cand3 仍禁 | **PASS** | 未启用 PR #6；未改默认 entry_rule 为 next_session |

**判定：CONDITION B 关闭。**

## 3. CONDITIONS 状态（本拍后）

| ID | 状态 | 说明 |
|---|---|---|
| **A** | **CLOSED**（先拍） | FIX_A 复审 `76a050ef`：Origin bench 篱笆已闭合 |
| **B** | **CLOSED**（本拍） | 箱上行为移植落地；非整盖；ON OR AFTER 保留；7 OK；见 §2 |
| **C** | **OPEN**（不挡本拍） | 候选 3 / SSE 日历 PR #6 仍外置；全链路待 cand3。**仍禁**启用 / merge cand3 |

## 4. memory_runner 箱上状态

| 路径 | 状态 |
|---|---|
| `quantlab/agents/trading_loop/memory_runner.py` | **ABSENT**（勿伪造；非本窗产物） |
| `research/ai_debate_memory_runner.py` | **在位** · content sha8 **`e1736d80`** · Eng 称本拍未改 · Arch 核 mtime/内容钉一致 · **未替换为 Origin 绿野版** |

记忆日序 / `load_prior_settlements` 排序增强属后续窗，不挡 B 关闭。

## 5. 硬禁确认

| 项 | 状态 |
|---|---|
| merge Origin PR #7 | **未做**（仍 open / `merged=false`） |
| Origin APPROVE / REQUEST_CHANGES | **未做**（复审票仅落箱 audit） |
| 改 settle.py / tests（本拍 Arch） | **未做**（只读复审） |
| 整棵覆盖箱上 settle ← Origin | **未发生**（Eng 行为移植；Arch 核 ≠） |
| 改 / 覆盖 `ai_debate_memory_runner.py` | **未做** |
| 启用 cand3 / merge PR #6 | **仍禁** |
| 改 paper / FROZEN / 权重 | **未做** |
| 签研究 `.ok` | **未做** |
| 碰叶37 | **未做** |
| 真行情 / `--allow-real-data` | **未做** |
| SendToUser / 报 Leo | **未做** · leo_notify=false · live=false |

## 6. 交付摘要（回主 / Eng）

- **verdict**：**PASS**（B **关闭**；C 仍开放但不挡）
- **复审票路径**：`docs/v2/audit/ARCH_ENG_CAND4_BOX_PORT_REVIEW_20261027_ZH.md`
- **MATCH**：Eng 回执 `f3f876e7` / git `b0a620df`；settle post `862a2c29` / git `88f3c97e`（≠ Origin `9d98ad4f`）；tests `772547f5` / git `5edfcd36`；memory_runner research `e1736d80` UNCHANGED；trading_loop `memory_runner.py` ABSENT；FIX_A `76a050ef`；首审 `a2051e37`；PR #7 仍 open @ `e04227a1`
- **unittest**：Arch 复跑 **Ran 7 tests … OK**
- **B 关闭**；**C** cand3 仍外置仍禁
- **确认**：未 merge；未 APPROVE；未改 settle/tests；未碰叶37；≠X2 ACCEPT；live=false；leo_notify=false
