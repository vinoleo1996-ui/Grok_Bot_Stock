# Arch 叶27 分块装载 ndays=40 · 独立 `.ok` 签发回执

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-25T16:16:59-04:00`（America/New_York） |
| 主令 | `MAIN_LEAF27_CHUNKED_NDAYS40_OK_WINDOW` sha `c6fb3c2e…`；窗 **16:15–17:00 ET** expires **17:02** |
| 审阅 | `18ea1567…` **PASS_WITH_CONDITIONS** |
| live / promotion_approved | **false** / **false** |

## 结论

**SIGNED** — 独立叶27 ndays=40 分块 `.ok` 已落盘；**≠ X2**；**≠ RESTORED** 旧 VOID（含 month `8e51de63` / quarter `3a6caa4f` / lowmem `8bcd79dc` / `725be3e0`）；**Arch 不代跑**。峰证明 **REQUIRED**（未实跑不算内存键 PASS）。QUIET **已挂且保留**供 AI prelaunch（本回合不 lift）。PRIMARY only；**无同票 FALLBACK**；ABORT→另交 hist-prune。

## 钉

| 项 | 值 |
|---|---|
| `.ok` 路径 | `output/ai_factory/ARCH_RUN_AUTH_LEAF27_CHUNKED_MEMBERS_MKTCAP_HILIQ_X2_NDAYS40.ok` |
| `.ok` sha8 / 全长 | `a7d98ac9` / `a7d98ac97a34c3e966577c22168e4d782a247ff0930afc0dea912afa331bac90` |
| 脚本 | `research/leaf27_chunked_members_mktcap_r1.py` = `262f9bf6878d5c64956529a680abbf36e45adfe72fc7dedc4c68dc1c40291a10` |
| lowmem_v1 UNCHANGED | `05bd81ea9da97cd53785b374c36273b327ff0302098c5b1cef1368c051d400f8` |
| 审阅 | `18ea156743f320beb31aa8eba02f21a7df04f4ad79f4734039993b3ffb1e5d04` PASS_WITH_CONDITIONS |
| 主令窗 | `c6fb3c2ea8bd2d7dcf81335031cd8ce0c0367394ebe0466e20fea64cf375f935` |
| COVER / CMD / DIFF | `ec5f67e9ba402449421339bd6b8fc47639aa5b19a818732862e2b6a47bb6f23d` / `af6f0d49dc89ae963e0e218b620184ecbf069d9e693b4aeeced62a33e82d8c2b` / `5449dde5fed4fe73d6669572cdb8381c1764b27381c61a07ca5755d6794a6c66` |
| HAND / HAND_TO_ARCH / VERIFY | `5547940bec333aa5515af5defccdde241c8812a9fb87f5bcc495427586424a81` / `2986bd01bfe23bfcbbf169ea93e07647c64472b3cdaaddd25048275042ed7ddb`（≠口头 `b7c33ca8`） / `305f7a93177d8d7a67204d4e58499374d5155cf79dc262f1515333a1545b4d5e` |
| 主交审 | `b1cbafa15d6a5e78c346b62d81d95384a3536e4a71bc25e73f9e5ed1d96d1e77` |
| month ABORT / VOID 回执 | `03c58db58e7f3e0e2ff1aa22e8e519a11bf3506d1526bec361f0b5c832039177` / `30f7289db17cf8fc4a878066162e79a92efb9344cc2773ed6935189c1988b394` |
| 窗期 | `2026-10-25T16:15:00-04:00` → `2026-10-25T17:00:00-04:00`；expires `2026-10-25T17:02:00-04:00` |
| CLI PRIMARY | `--universe HILIQ --window x2 --chunk-mode ndays --chunk-ndays 40` |
| FALLBACK | **无**；ABORT→另交 hist-prune（禁 silently 换 mode） |
| rss_limit | **1500** MB（`rss_limit_kb=1536000`）；破帽 ABORT；**禁抬帽** |
| 采样 | 仅 `/tmp`；`/tmp/quantlab_leaf27_chunked_ndays40_*` |
| 禁 RESTORED | `8e51de63` / `3a6caa4f` / `8bcd79dc` / `725be3e0`（已 VOID；禁同 cmd lowmem_v1） |
| FULLA / both / sealed | **不进本窗**（sealed 另签） |
| peak_proof | **REQUIRED** |
| QUIET | 已挂 `output/loop/RESEARCH_QUIET.lock`（保留不 lift） |
| MemAvailable@签 | 7288964 kB |

## 预检旁证

`docs/v2/audit/ARCH_LEAF27_CHUNKED_NDAYS40_PREOK_EVIDENCE_20261025_ZH.md` sha `9eedb34e7d14b521bc89be9b77bb7dd44677153800526c29608281d0efa2deda`

## QUIET / healthz / pgrep

| 项 | 值 |
|---|---|
| QUIET 挂时 | `2026-10-25T16:15:55-04:00` reason=leaf27_ndays40_arch_quiet |
| healthz quiet=true | `2026-10-25T16:15:55-04:00` |
| ≥15s 后复检 | `2026-10-25T16:16:21-04:00` quiet=true；gen/snapshot/kline=false；child_pids={} |
| pgrep | `[k]line.py|[e]xport_static.py|[s]napshot.py|[g]en.py` **空** |

## 下一跳

1. **主**确认后令 AI prelaunch 单次 PRIMARY ndays40（须在 expires 前；Arch 不代跑）
2. AI 交实峰回执（阶段 rss / ABORT 或 PASS）→ Arch 核
3. ndays40 ABORT → **停**；另交 **hist-prune** 票另审另签（勿 silently 换 mode/ndays；禁抬帽）
4. ≠X2；live=false
