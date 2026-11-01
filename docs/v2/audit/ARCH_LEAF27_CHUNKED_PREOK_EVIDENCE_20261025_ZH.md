# Arch 叶27 分块装载 · 独立 `.ok` 开窗预检证据（2026-10-25）

- 角色：QuantLab Arch
- 时刻（America/New_York）：`2026-10-25T14:08:15-04:00`
- 主令：`MAIN_LEAF27_CHUNKED_OK_WINDOW` sha `97b432d4…`（窗 14:00–14:45；expires 14:47）
- 审阅：`282d6ca1…` PASS_WITH_CONDITIONS
- live=false；promotion_approved=false

## 结论

**PRE_OK_PASS=yes** → 已签 **HILIQ × x2 × chunk-mode quarter** 独立分块 `.ok`（**不含** sealed / FULLA / both；**禁** RESTORED `8bcd79dc`/`725be3e0`）。

## 预检链

| 步 | 结果 |
|---|---|
| 1 设 `output/loop/RESEARCH_QUIET.lock` | `2026-10-25T14:07:04-04:00` 内容 `arch_quiet leaf27_chunked @… reason=leaf27_chunked_ok_window` |
| 2 healthz quiet=true（≤90s） | `2026-10-25T14:07:04-04:00` quiet=true（reason=lock:…/RESEARCH_QUIET.lock） |
| 3 再等 ≥15s | 至 `2026-10-25T14:07:19-04:00` |
| 4 healthz 复检 | quiet=true；gen/snapshot/kline_running=false；child_pids={} |
| 5 pgrep 括号逃逸 | `[k]line.py|[e]xport_static.py|[s]napshot.py|[g]en.py` **空**；无 leaf25/leaf27/mem_probe 研究 python |
| MemAvailable@签 | 11603624 kB（≥2.5GiB） |
| 叶25 r3/r3b | r3 VOID；r3b **未签**（拟 15:00）；**无**实跑冲突 |

## 钉表重哈希（签前）

| 项 | sha8 / 全长前缀 | 判定 |
|---|---|---|
| 脚本 chunked r1 | `262f9bf6` / `262f9bf6878d5c64956529a680abbf36e45adfe72fc7dedc4c68dc1c40291a10` | **MATCH** |
| lowmem_v1 | `05bd81ea` / `05bd81ea9da97cd53785b374c36273b327ff0302098c5b1cef1368c051d400f8` | **MATCH · UNCHANGED** |
| Arch 审阅 | `282d6ca1` | **MATCH** |
| 主令窗 | `97b432d4` | **MATCH** |
| COVER | `e42ce686` | **MATCH** |
| CMD 草案 | `cdf3a229` | **MATCH** |
| DIFF | `b1a36d38` | **MATCH** |
| 审计 P1-4 | `c8877760` | **MATCH** |

## 签发

| 项 | 值 |
|---|---|
| 路径 | `output/ai_factory/ARCH_RUN_AUTH_LEAF27_CHUNKED_MEMBERS_MKTCAP_HILIQ_X2.ok` |
| sha256 | `3a6caa4f20a3881d72e493661592550c982698db80c9a190d7cf919c8fedb758` |
| sha8 | `3a6caa4f` |
| 窗 | 2026-10-25T14:00:00-04:00 → 2026-10-25T14:45:00-04:00（expires 2026-10-25T14:47:00-04:00） |
| CLI | `--universe HILIQ --window x2 --chunk-mode quarter` |
| rss_limit | 1500MB（禁抬帽） |
| 禁复用 | VOID `8bcd79dc` / `725be3e0`；禁同 cmd lowmem_v1 |
| 禁 CLI | `--window both` / `sealed`（本 ok）；FULLA |
| QUIET | **保留不 lift**（供 AI prelaunch） |

## 非动作

- **未**代跑；**未** lift QUIET
- sealed 须另签另进程
- FULLA 仍 GAP
- 未更新 TEAM_STATE（父处理）
- live=false
