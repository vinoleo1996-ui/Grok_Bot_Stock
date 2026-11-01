# Arch 叶27 分块装载 ndays=40 · 独立 `.ok` 开窗预检证据（2026-10-25）

- 角色：QuantLab Arch
- 时刻（America/New_York）：`2026-10-25T16:16:59-04:00`
- 主令：`MAIN_LEAF27_CHUNKED_NDAYS40_OK_WINDOW` sha `c6fb3c2e…`（窗 16:15–17:00；expires 17:02）
- 审阅：`18ea1567…` PASS_WITH_CONDITIONS
- live=false；promotion_approved=false；≠X2

## 结论

**PRE_OK_PASS=yes** → 已签 **HILIQ × x2 × chunk-mode ndays --chunk-ndays 40** 独立分块 `.ok`（**无同票 FALLBACK**；**禁** RESTORED `8e51de63`/`3a6caa4f`/`8bcd79dc`/`725be3e0`；ABORT→另交 hist-prune；禁 silently 换 mode）。

## 预检链

| 步 | 结果 |
|---|---|
| 1 设 `output/loop/RESEARCH_QUIET.lock` | `2026-10-25T16:15:55-04:00` quiet=true reason=leaf27_ndays40_arch_quiet |
| 2 healthz quiet=true（≤90s） | `2026-10-25T16:15:55-04:00` quiet=true（lock:…/RESEARCH_QUIET.lock） |
| 3 再等 ≥15s | 至 `2026-10-25T16:16:21-04:00` |
| 4 healthz 复检 | quiet=true；gen/snapshot/kline_running=false；child_pids={} |
| 5 pgrep 括号逃逸 | `[k]line.py|[e]xport_static.py|[s]napshot.py|[g]en.py` **空**；无 leaf27 研究 python |
| MemAvailable@签 | 7288964 kB（≥2.5GiB） |
| live `.ok` | **0**（签前） |
| 叶27 month | VOID.ABORT_RSS `8e51de63`→归档；不冲突 |

## 钉表重哈希（签前）

| 项 | sha8 / 全长 | 判定 |
|---|---|---|
| 脚本 chunked r1 | `262f9bf6` / `262f9bf6878d5c64956529a680abbf36e45adfe72fc7dedc4c68dc1c40291a10` | **MATCH · UNCHANGED** |
| lowmem_v1 | `05bd81ea` / `05bd81ea9da97cd53785b374c36273b327ff0302098c5b1cef1368c051d400f8` | **MATCH · UNCHANGED** |
| Arch 审阅 ndays40 | `18ea1567` / `18ea156743f320beb31aa8eba02f21a7df04f4ad79f4734039993b3ffb1e5d04` | **MATCH** PASS_WITH_CONDITIONS |
| 主令窗 | `c6fb3c2e` / `c6fb3c2ea8bd2d7dcf81335031cd8ce0c0367394ebe0466e20fea64cf375f935` | **MATCH** |
| COVER | `ec5f67e9` / `ec5f67e9ba402449421339bd6b8fc47639aa5b19a818732862e2b6a47bb6f23d` | **MATCH** |
| CMD 草案 | `af6f0d49` / `af6f0d49dc89ae963e0e218b620184ecbf069d9e693b4aeeced62a33e82d8c2b` | **MATCH** |
| DIFF | `5449dde5` / `5449dde5fed4fe73d6669572cdb8381c1764b27381c61a07ca5755d6794a6c66` | **MATCH** |
| HAND / HAND_TO_ARCH / VERIFY | `5547940b` / `2986bd01`（≠口头 `b7c33ca8`） / `305f7a93` | **MATCH** |
| 主交审 | `b1cbafa1` / `b1cbafa15d6a5e78c346b62d81d95384a3536e4a71bc25e73f9e5ed1d96d1e77` | **MATCH** |

## 签发

| 项 | 值 |
|---|---|
| 路径 | `output/ai_factory/ARCH_RUN_AUTH_LEAF27_CHUNKED_MEMBERS_MKTCAP_HILIQ_X2_NDAYS40.ok` |
| sha256 | `a7d98ac97a34c3e966577c22168e4d782a247ff0930afc0dea912afa331bac90` |
| sha8 | `a7d98ac9` |
| 窗 | 2026-10-25T16:15:00-04:00 → 2026-10-25T17:00:00-04:00（expires 2026-10-25T17:02:00-04:00） |
| CLI PRIMARY | `--universe HILIQ --window x2 --chunk-mode ndays --chunk-ndays 40` |
| FALLBACK | **无**；ABORT→另交 hist-prune |
| rss_limit | 1500MB（禁抬帽） |
| 采样 | 仅 `/tmp/quantlab_leaf27_chunked_ndays40_*` |
| 禁复用 | VOID `8e51de63` / `3a6caa4f` / `8bcd79dc` / `725be3e0`；禁同 cmd lowmem_v1 |
| 禁 CLI | `--window both` / sealed（本 ok）；FULLA |
| peak_proof | **REQUIRED** |
| QUIET | **保留不 lift**（供 AI prelaunch） |

## 非动作

- **未**代跑；**未** lift QUIET
- sealed / month 复用禁；FULLA 仍 GAP
- ≠X2；live=false
