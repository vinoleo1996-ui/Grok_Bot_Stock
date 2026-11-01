# Arch 叶27 Gate A mktcap_cache · 独立 `.ok` 签发回执

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-25T20:36:40-04:00`（America/New_York） |
| 主令 | `MAIN_LEAF27_CHUNKED_MKTCAP_CACHE_OK_WINDOW` sha `c33c6382…`；窗 **20:30–21:15 ET** expires **21:17** |
| 审阅 | `64057bfe…` **PASS_WITH_CONDITIONS** |
| live / promotion_approved | **false** / **false** |

## 结论

**SIGNED** — 独立叶27 Gate A mktcap_cache（`mktcap_cache_r1` + 保留 `hist_prune_r1`）分块 `.ok` 已落盘；**≠ X2**；**≠ RESTORED** 旧 VOID 六票（`2be59acd`/`a7d98ac9`/`8e51de63`/`3a6caa4f`/`8bcd79dc`/`725be3e0`）；禁旧脚本字节 `8cb3e86f`/`262f9bf6`；HAND 钉盘上 **`a2abe662…`**（禁口头 `70701c1d`）；**Arch 不代跑**。峰证明 **REQUIRED**（未实跑不算内存键 PASS）。QUIET **已挂且保留**供 AI prelaunch（本回合不 lift）。PRIMARY only；**无同票 FALLBACK**；ABORT→停+另票（禁抬帽）。

## 钉

| 项 | 值 |
|---|---|
| `.ok` 路径 | `output/ai_factory/ARCH_RUN_AUTH_LEAF27_CHUNKED_MEMBERS_MKTCAP_HILIQ_X2_MKTCAP_CACHE.ok` |
| `.ok` sha8 / 全长 | `e107383f` / `e107383f16336765fbd9cddf78c7f429304a0052e445a089ff8ce606b47d44ef` |
| 脚本 | `research/leaf27_chunked_members_mktcap_r1.py` = `27aae6dbec0c80d96799c3cf6a7baba1bf8eaea866f0dae5feb2876e201175f5`（禁 `8cb3e86f…` / `262f9bf6…`） |
| tags | `mktcap_cache_r1` + `hist_prune_r1` |
| lowmem_v1 UNCHANGED | `05bd81ea9da97cd53785b374c36273b327ff0302098c5b1cef1368c051d400f8` |
| 审阅 | `64057bfeac7ab42d2946cfe0c51b61bde847c55da6717f06f5823b4acbbcd49e` PASS_WITH_CONDITIONS |
| 主令窗 | `c33c6382f74248ee356b3557d2d1f5c2bd950742fc1b4610ead9f846d3cfb2a5` |
| COVER / CMD / DIFF / VERIFY | `bf83073aab0b6e2a42db13181a7c0d4ba69c8b49e316058de9dc94aaab1cd3be` / `30c581329708ad57e83cc8d2eb3775b686759c57287bd57554e8ce248d6fe04c` / `779197d81e296102e61e5b7174e13e02e206fd523d8e0bcac4cc3be2a468b801` / `f01afc7435e3c5e682f8c3880fdd0b62afab15729cd1993a79b994c7b6744056` |
| HAND 盘上 / H2A | `a2abe662f741da7494c341fb70f86b18d639081ae9abf0fb0b5d8b81bcf7aef4` / `4cac1baeaaed7b16073c079127e0733edb694742bc3a1fdf1db707ed14d724c8` |
| 草案 A / 尖峰笔记 / ABORT / VOID | `a2307c8bf48ab8523c566298a4cd42ef3fc3a704ff2d0be910f943ecbc49fe54` / `dd193511f82b21440c8462730f26449bfc1bb8c12c4047df394872e72002eae1` / `d8be85cb96a151cb815ca94d22ca3049dfd4c95530baf5472642568792797f8f` / `fd1593225e50300b24e56bbeb0a461efac3fbeedf1e4a2fa8d79a6dc38ea1826` |
| 窗期 | `2026-10-25T20:30:00-04:00` → `2026-10-25T21:15:00-04:00`；expires `2026-10-25T21:17:00-04:00` |
| CLI PRIMARY | `--universe HILIQ --window x2 --chunk-mode ndays --chunk-ndays 40` |
| FALLBACK | **无**；ABORT→停+另票（禁抬帽；禁 silently 换 mode） |
| rss_limit | **1500** MB（`rss_limit_kb=1536000`）；破帽 ABORT；**禁抬帽** |
| 采样 | 仅 `/tmp`；`/tmp/quantlab_leaf27_chunked_mktcap_cache_*` |
| out_dir（签文钉） | `output/ai_factory/leaf27_chunked_members_mktcap_hiliq_x2_mktcap_cache` |
| 脚本 OUT_DIR 继承 | `output/ai_factory/leaf27_on_minus_id_idio_ivol`（**双 out 披露**：日志/采样走签文 out_dir；产物或仍落继承路径） |
| 禁 RESTORED | `2be59acd` / `a7d98ac9` / `8e51de63` / `3a6caa4f` / `8bcd79dc` / `725be3e0` |
| FULLA / both / sealed | **不进本窗**（sealed 另签） |
| peak_proof | **REQUIRED**（须含 mktcap_cache hit/miss/load_n + rss 阶梯 + sampler_30s） |
| QUIET | 已挂 `output/loop/RESEARCH_QUIET.lock` sha `1d423cc60d9b89a6002f03ebab9c3fcefff7528e24d7f02d220797ecaac43727`（保留不 lift） |
| MemAvailable@签 | 10839220 kB |

## 预检旁证

`docs/v2/audit/ARCH_LEAF27_CHUNKED_MKTCAP_CACHE_PREOK_EVIDENCE_20261025_ZH.md` sha `bf45a6ee2975693d8a9cffba8e942f72a7cf26833f2b9ecf30a520dadc135c9b`

## QUIET / healthz / pgrep

| 项 | 值 |
|---|---|
| QUIET 挂时 | `2026-10-25T20:35:04-04:00` reason=leaf27_mktcap_cache |
| healthz quiet=true | `2026-10-25T20:35:04-04:00` |
| ≥15s 后复检 | `2026-10-25T20:35:20-04:00` quiet=true；gen/snapshot/kline=false；child_pids={} |
| pgrep | `[k]line.py\|[e]xport_static.py\|[s]napshot.py\|[g]en.py` **空** |

## 下一跳

1. **主**确认后令 AI prelaunch 单次 PRIMARY mktcap_cache（须在 expires 前；Arch 不代跑）
2. AI 交实峰回执（阶段 rss / ABORT 或 PASS；须含 mktcap_cache hit/miss/load_n）→ Arch 核
3. mktcap_cache ABORT → **停**；另交主/Arch 票另审另签（勿 silently 换 mode/ndays；**禁抬帽**）
4. ≠X2；live=false
