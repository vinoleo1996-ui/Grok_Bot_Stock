# Arch 叶27 分块装载 month · 独立 `.ok` 开窗预检证据（2026-10-25）

- 角色：QuantLab Arch
- 时刻（America/New_York）：`2026-10-25T15:45:21-04:00`
- 主令：`MAIN_LEAF27_CHUNKED_MONTH_OK_WINDOW` sha `64c7da1e…`（窗 15:40–16:25；expires 16:27）
- 审阅：`85c6fb82…` PASS_WITH_CONDITIONS
- live=false；promotion_approved=false；≠X2

## 结论

**PRE_OK_PASS=yes** → 已签 **HILIQ × x2 × chunk-mode month** 独立分块 `.ok`（**不含** sealed / FULLA / both / ndays；**禁** RESTORED `3a6caa4f`/`8bcd79dc`/`725be3e0`；禁 silently ndays）。

## 预检链

| 步 | 结果 |
|---|---|
| 1 设 `output/loop/RESEARCH_QUIET.lock` | `2026-10-25T15:43:45-04:00` quiet=true reason=leaf27_month_ok_window |
| 2 healthz quiet=true（≤90s） | `2026-10-25T15:43:52-04:00` quiet=true（lock:…/RESEARCH_QUIET.lock）；snapshot 已停 |
| 3 再等 ≥15s | 至 `2026-10-25T15:44:41-04:00` |
| 4 healthz 复检 | quiet=true；gen/snapshot/kline_running=false；child_pids={} |
| 5 pgrep 括号逃逸 | `[k]line.py|[e]xport_static.py|[s]napshot.py|[g]en.py` **空**；无 leaf27/mem_probe 研究 python |
| MemAvailable@签 | 3344328 kB（≥2.5GiB） |
| live `.ok` | **0**（签前） |
| 叶25 r3b | CONSUMED_PASS `6054b3bf`→`74b5f209`；不冲突 |

## 钉表重哈希（签前）

| 项 | sha8 / 全长 | 判定 |
|---|---|---|
| 脚本 chunked r1 | `262f9bf6` / `262f9bf6878d5c64956529a680abbf36e45adfe72fc7dedc4c68dc1c40291a10` | **MATCH · UNCHANGED** |
| lowmem_v1 | `05bd81ea` / `05bd81ea9da97cd53785b374c36273b327ff0302098c5b1cef1368c051d400f8` | **MATCH · UNCHANGED** |
| Arch 审阅 month | `85c6fb82` / `85c6fb82f8fcc841c63bab77c237f9b1e29f16bb718f43f55a04734ac0cb1119` | **MATCH** |
| 主令窗 | `64c7da1e` / `64c7da1e651ea2c08ac6d624e20262da4720673651d8120597ff1c02b5e07982` | **MATCH** |
| COVER | `c8b33519` / `c8b3351931a593d7e7d5f747e318db29278407d19d07949b1f866f25bae8819b` | **MATCH** |
| CMD 草案 | `5323d614` / `5323d6140b3a0fa4659febbf694561fc9bd048cda9c668cdc914429f9ca11077` | **MATCH** |
| DIFF | `5fa2a29e` / `5fa2a29e2bb6b8b49a38ec7350e4ada33f61b49906fbd5e4e31f9dbb12988ac1` | **MATCH** |
| HAND / HAND_TO_ARCH / VERIFY | `cf258620` / `eb3fb164` / `f649ba15` | **MATCH** |

## 签发

| 项 | 值 |
|---|---|
| 路径 | `output/ai_factory/ARCH_RUN_AUTH_LEAF27_CHUNKED_MEMBERS_MKTCAP_HILIQ_X2_MONTH.ok` |
| sha256 | `8e51de63d661ae67711bbc169300cf5b3f009806ef71ce4c76a6f2e46c29d9c4` |
| sha8 | `8e51de63` |
| 窗 | 2026-10-25T15:40:00-04:00 → 2026-10-25T16:25:00-04:00（expires 2026-10-25T16:27:00-04:00） |
| CLI PRIMARY | `--universe HILIQ --window x2 --chunk-mode month` |
| FALLBACK | ndays=40 **仅另签**；禁 silently |
| rss_limit | 1500MB（禁抬帽） |
| 采样 | 仅 `/tmp/quantlab_leaf27_chunked_month_*` |
| 禁复用 | VOID `3a6caa4f` / `8bcd79dc` / `725be3e0`；禁同 cmd lowmem_v1 |
| 禁 CLI | `--window both` / sealed（本 ok）；FULLA |
| peak_proof | **REQUIRED** |
| QUIET | **保留不 lift**（供 AI prelaunch） |

## 非动作

- **未**代跑；**未** lift QUIET
- sealed / ndays40 须另签
- FULLA 仍 GAP
- ≠X2；live=false
