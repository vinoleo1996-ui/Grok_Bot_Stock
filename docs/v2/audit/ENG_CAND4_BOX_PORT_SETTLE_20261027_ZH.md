# Eng 回执：cand4 CONDITION B 箱上 port（终盘篱笆 / FIX_A）· 只移植不 merge

| 项 | 值 |
|---|---|
| 角色 | QuantLab Eng（执行器；箱上行为移植） |
| 时刻 | `2026-10-27T18:57-04:00`（America/New_York；墙钟 `2026-10-27 18:57 ET`） |
| 主裁窗口 | TEAM_STATE 开 CONDITION B；主收窄：**只移植终盘篱笆 / FIX_A**；保留箱上调用面与 ON OR AFTER 默认 |
| Arch 对照 | FIX_A 复审 `docs/v2/audit/ARCH_ENG_CAND4_FIX_A_REREVIEW_20261027_ZH.md` sha8 **`76a050ef`**；首审 CONDITION B `a2051e37` §3 |
| Origin 参考（禁覆盖） | PR #7 head `e04227a1` settle git-sha8 `9d98ad4f`（`/tmp/cand4_fix_a_settle.py`）；**未**整棵写入箱上 |
| live | **false** · `PROMOTION_APPROVED=False` · ≠X2 ACCEPT · leo_notify=false · **未报 Leo** |

## 0. 一句话

箱上 `quantlab/agents/trading_loop/settle.py` 已做 **FIX_A 终盘篱笆行为移植**（instrument **与** benchmark 同走 `available_at` / 今日未收盘丢弃）；**保留**既有契约 `compute_horizon_returns(instrument, session, horizon_trading_days, *, benchmark=..., etf_path=..., allow_mock=...)` 与 **ON OR AFTER** 入场默认。合成单测 **7 OK**。**未**整棵覆盖 Origin 绿野文件；**未**改 `memory_runner`；**未 merge** PR #7；**未碰叶37**；cand3/PR#6 **仍禁**。交 Arch **只审 port**。

## 1. 钉表（pre → post）

| 件 | sha8 / 值 | 说明 |
|---|---|---|
| settle **pre** content sha256 | **`a92b7ccf`**…`f305547b` | 开窗前箱上（Arch 复审钉） |
| settle **post** content sha256 | **`862a2c29`**`826b3dda2911bb60c280ff17100eb194a555ebbf133326eee1f348a4` | 本拍 port 后 |
| settle **post** git hash-object | **`88f3c97e`**`2bc1a58b5d9e9dc1efd1a3b8f3a9aadb` | 箱上工作树；**非** Origin blob |
| tests content sha256 | **`772547f5`**`a76ea7ce85625f4a6f17fadfe22f80e921e32c871d1cdfcecce5158f` | `tests/test_cand4_box_port_settle_fence.py` |
| tests git hash-object | **`5edfcd36`**`e4004e4242a377c7aed0d04f5e07f36d` | |
| unittest 日志 sha256 | **`8132e0c7`**…（`/tmp/cand4_box_port_settle_fence_unittest.log`） | `Ran 7 tests … OK` |
| vs Origin FIX_A settle | byte_identical=**False**（箱 13010 B ≠ Origin 17132 B） | CONDITION B 禁覆盖成立 |
| `research/ai_debate_memory_runner.py` | content sha8 **`e1736d80`**（本拍**未改**） | 勿换 Origin 版 |
| Data pgrep（`kline\|export_static\|snapshot\|gen`） | 空 | 跑测前 bracket 复核 |

## 2. 本窗落地行为（最小集 · 主收窄后）

| # | 行为 | 状态 |
|---|---|---|
| 1 | instrument 走终盘篱笆：`available_at>now` 丢；否则「今日且未到 15:00 Asia/Shanghai」丢；未来日非终盘 | **已落地** `_is_final_close` + `_load_closes(..., now=)` |
| 2 | **benchmark 同篱笆**（FIX_A）：同一 `_load_closes` / 同 `now`/`tz`/`regular_close` | **已落地** |
| 3 | 缺定价出场所需 bench 终盘 → `pending` + `reason=insufficient_benchmark_final_closes`；不写 alpha | **已落地** |
| 4 | 入/出场日锁标的 `entry_dt`/`exit_dt`；bench 须在篱笆后具备同日终盘点 | **已落地** |
| 5 | 调用面兼容：`instrument, session, horizon_trading_days` + `benchmark`/`etf_path`/`allow_mock`；可选 `now`/`tz`/`regular_close`（缺省不破坏旧调用） | **已落地** |
| 6 | 入场默认仍 **ON OR AFTER**（`>= session`）；**未**改默认 `next_session`（cand3 mock 契约 / 既有调用面） | **刻意保留** |
| 7 | 不替换 `memory_runner`；决策日排序等记忆增强 **本窗推迟** | **推迟**（见 §5） |

## 3. 合成单测

命令：

```bash
cd /workspace/QuantLab
PYTHONPATH=/workspace/QuantLab python3 -m unittest tests.test_cand4_box_port_settle_fence -v
```

结果：**Ran 7 tests in ~0.09s → OK**（仅 TemporaryDirectory 合成 parquet；无真行情读作门禁；无 `.ok`）。

覆盖要点：

1. ON OR AFTER 契约：决策日可为 entry  
2. 盘中假今日 bench（999）不渗入 alpha  
3. exit 日 bench `available_at>now` → pending；稍后 settled  
4. 无 `available_at` 时今日未收盘 → pending `insufficient_final_closes`  
5. 旧 kwargs 表面兼容  
6. 模块非 Origin 绿野整棵覆盖  
7. `LIVE` / `PROMOTION_APPROVED` 仍 false  

附：cand3 mock 契约手核（注入合成日历）`entry_date=2025-09-30` / `exit_date=2025-10-08` **OK**；非本 unittest 文件内。

## 4. 硬禁确认

| 项 | 状态 |
|---|---|
| merge Origin PR #7 | **未做**（仍应交听主） |
| Origin APPROVE | **未做** |
| 整棵覆盖箱上 settle ← Origin 文件 | **未做**（行为移植） |
| 改 / 覆盖 `ai_debate_memory_runner.py` | **未做** |
| 启用 cand3 / merge PR #6 | **仍禁** |
| 改 paper / FROZEN / 权重 | **未做** |
| 碰叶37 | **未做** |
| 签研究 `.ok` / 真行情门禁跑批 | **未做** |
| 写 TEAM_STATE Eng 段 | **未做**（交父代理） |
| SendToUser / 报 Leo | **未做** · live=false |

## 5. 推迟 / 设计选择

| 项 | 决定 | 理由 |
|---|---|---|
| 默认 `entry_rule=next_session` | **本窗不做** | 主收窄：以终盘篱笆为准；箱上 cand3 mock 与既有调用依赖 ON OR AFTER；擅自改默认会破契约 |
| `write_settlement` / Origin 绿野 API | **不引入** | 箱上已有 `settle_log` + debate ledger 路径 |
| `load_prior_settlements` 决策日序 | **推迟** | 箱上签名已含 `instrument=` / `non_null_only=` / `as_of=`；改排序属 memory_runner 窗，非本 settle.py port |
| 取数扩窗 `expanded_to_today` | **推迟** | 非 FIX_A 最小集；箱上仍按已加载终盘序列判窗长 |

## 6. 请 Arch

- **只审**本箱上 port（settle DIFF + 合成测 + 本回执）  
- **不** merge PR #7；**不**开 Origin APPROVE  
- 验收建议钉：pre `a92b7ccf` → post `862a2c29` / git `88f3c97e`；测 `772547f5`；7 OK；bench 篱笆两条合成测；调用面 ON OR AFTER 仍成立  

## 7. 路径清单

1. `quantlab/agents/trading_loop/settle.py`（修改）  
2. `tests/test_cand4_box_port_settle_fence.py`（新增）  
3. `/tmp/cand4_box_port_settle_fence_unittest.log`（7 OK）  
4. `docs/v2/audit/ENG_CAND4_BOX_PORT_SETTLE_20261027_ZH.md`（本回执）  
