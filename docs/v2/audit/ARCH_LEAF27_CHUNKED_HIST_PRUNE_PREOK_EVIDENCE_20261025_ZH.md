# Arch 叶27 分块装载 hist-prune · 独立 `.ok` 开窗预检证据（2026-10-25）

- 角色：QuantLab Arch
- 时刻（America/New_York）：`2026-10-25T16:52:17-04:00`
- 主令：`MAIN_LEAF27_CHUNKED_HIST_PRUNE_OK_WINDOW` sha `3a7adb0f…`（窗 16:45–17:30；expires 17:32）
- 审阅：`6543726a…` PASS_WITH_CONDITIONS
- live=false；promotion_approved=false；≠X2

## 结论

**PRE_OK_PASS=yes** → 已签 **HILIQ × x2 × chunk-mode ndays --chunk-ndays 40 + hist_prune_r1** 独立分块 `.ok`（脚本 **`8cb3e86f`**；禁旧字节 `262f9bf6`；**无同票 FALLBACK**；**禁** RESTORED 五票 `a7d98ac9`/`8e51de63`/`3a6caa4f`/`8bcd79dc`/`725be3e0`；ABORT→停+另票禁抬帽；禁 silently 换 mode）。

## 预检链

| 步 | 结果 |
|---|---|
| 1 设 `output/loop/RESEARCH_QUIET.lock` | `2026-10-25T16:50:08-04:00` quiet=true reason=leaf27_histprune_arch_quiet |
| 2 healthz quiet=true（≤90s） | `2026-10-25T16:50:08-04:00` quiet=true（lock:…/RESEARCH_QUIET.lock） |
| 3 再等 ≥15s | 至 `2026-10-25T16:50:23-04:00` |
| 4 healthz 复检 | quiet=true；gen/snapshot/kline_running=false；child_pids={} |
| 5 pgrep 括号逃逸 | `[k]line.py|[e]xport_static.py|[s]napshot.py|[g]en.py` **空**；无 leaf27 研究 python |
| MemAvailable@签 | 7356760 kB（≥2.5GiB） |
| live `.ok` | **0**（签前） |
| 叶27 ndays40 | VOID.ABORT_RSS `a7d98ac9`→归档；不冲突 |

## 钉表重哈希（签前）

| 项 | sha8 / 全长 | 判定 |
|---|---|---|
| 脚本 chunked r1 hist_prune_r1 | `8cb3e86f` / `8cb3e86f0d5b199c474b38eba1950a44b18e4c0a1ded67d0f371429a55810012` | **MATCH · CHANGED** vs `262f9bf6` |
| lowmem_v1 | `05bd81ea` / `05bd81ea9da97cd53785b374c36273b327ff0302098c5b1cef1368c051d400f8` | **MATCH · UNCHANGED** |
| Arch 审阅 hist-prune | `6543726a` / `6543726acda009512558612687552083969d61ed3c1a1de79515fe6ba1730a86` | **MATCH** PASS_WITH_CONDITIONS |
| 主令窗 | `3a7adb0f` / `3a7adb0f32cf2a2fce72be3caba318edb384c83d280b94f97b39a17258ee8211` | **MATCH** |
| COVER | `85022506` / `850225060aeb07d4350d38ca569fe241956359605ee492520235105aca6b8019` | **MATCH** |
| CMD 草案 | `4cc9773a` / `4cc9773a4ebde6548308e717e694df520a4b72877a02a8c40f20df0220f7b3a3` | **MATCH** |
| DIFF | `0c7af6ed` / `0c7af6ed66b9a9152a95ee3a0d008264ee3bb3b6801e496ff4ab587e27686e90` | **MATCH** |
| HAND / HAND_TO_ARCH / VERIFY | `cc21f3c7` / `e8cc6058` / `4714256a` | **MATCH** |
| 主交审 | `3806f922` / `3806f92228ea8577530773161dc36090ffbe153ade0db804fe1092384397d6aa` | **MATCH** |
| ndays40 ABORT / VOID | `03064d50` / `ad2947ef` | **MATCH** |

## 签发

| 项 | 值 |
|---|---|
| 路径 | `output/ai_factory/ARCH_RUN_AUTH_LEAF27_CHUNKED_MEMBERS_MKTCAP_HILIQ_X2_HISTPRUNE.ok` |
| sha256 | `2be59acd5d201b06eea78ff99354c0acaf21f990e87f02a43e57f247617f6e77` |
| sha8 | `2be59acd` |
| 窗 | 2026-10-25T16:45:00-04:00 → 2026-10-25T17:30:00-04:00（expires 2026-10-25T17:32:00-04:00） |
| CLI PRIMARY | `--universe HILIQ --window x2 --chunk-mode ndays --chunk-ndays 40` + hist_prune_r1 |
| FALLBACK | **无**；ABORT→停+另票（禁抬帽） |
| rss_limit | 1500MB（禁抬帽） |
| 采样 | 仅 `/tmp/quantlab_leaf27_chunked_histprune_*` |
| out_dir | `output/ai_factory/leaf27_chunked_members_mktcap_hiliq_x2_histprune` |
| 禁复用 | VOID 五票 `a7d98ac9`/`8e51de63`/`3a6caa4f`/`8bcd79dc`/`725be3e0`；禁同 cmd lowmem_v1；禁脚本 `262f9bf6` |
| 禁 CLI | `--window both` / sealed（本 ok）；FULLA |
| peak_proof | **REQUIRED** |
| QUIET | **保留不 lift**（供 AI prelaunch） |

## 非动作

- **未**代跑；**未** lift QUIET
- sealed / ndays40 复用禁；FULLA 仍 GAP
- ≠X2；live=false
