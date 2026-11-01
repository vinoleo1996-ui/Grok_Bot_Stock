# Arch 叶27 分块装载 hist-prune · 独立 `.ok` 签发回执

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-25T16:52:17-04:00`（America/New_York） |
| 主令 | `MAIN_LEAF27_CHUNKED_HIST_PRUNE_OK_WINDOW` sha `3a7adb0f…`；窗 **16:45–17:30 ET** expires **17:32** |
| 审阅 | `6543726a…` **PASS_WITH_CONDITIONS** |
| live / promotion_approved | **false** / **false** |

## 结论

**SIGNED** — 独立叶27 hist-prune（hist_prune_r1）分块 `.ok` 已落盘；**≠ X2**；**≠ RESTORED** 旧 VOID 五票（`a7d98ac9`/`8e51de63`/`3a6caa4f`/`8bcd79dc`/`725be3e0`）；禁旧脚本字节 `262f9bf6`；**Arch 不代跑**。峰证明 **REQUIRED**（未实跑不算内存键 PASS）。QUIET **已挂且保留**供 AI prelaunch（本回合不 lift）。PRIMARY only；**无同票 FALLBACK**；ABORT→停+另票（禁抬帽）。

## 钉

| 项 | 值 |
|---|---|
| `.ok` 路径 | `output/ai_factory/ARCH_RUN_AUTH_LEAF27_CHUNKED_MEMBERS_MKTCAP_HILIQ_X2_HISTPRUNE.ok` |
| `.ok` sha8 / 全长 | `2be59acd` / `2be59acd5d201b06eea78ff99354c0acaf21f990e87f02a43e57f247617f6e77` |
| 脚本 | `research/leaf27_chunked_members_mktcap_r1.py` = `8cb3e86f0d5b199c474b38eba1950a44b18e4c0a1ded67d0f371429a55810012`（禁 `262f9bf6…`） |
| hist_prune_tag | `hist_prune_r1` |
| lowmem_v1 UNCHANGED | `05bd81ea9da97cd53785b374c36273b327ff0302098c5b1cef1368c051d400f8` |
| 审阅 | `6543726acda009512558612687552083969d61ed3c1a1de79515fe6ba1730a86` PASS_WITH_CONDITIONS |
| 主令窗 | `3a7adb0f32cf2a2fce72be3caba318edb384c83d280b94f97b39a17258ee8211` |
| COVER / CMD / DIFF | `850225060aeb07d4350d38ca569fe241956359605ee492520235105aca6b8019` / `4cc9773a4ebde6548308e717e694df520a4b72877a02a8c40f20df0220f7b3a3` / `0c7af6ed66b9a9152a95ee3a0d008264ee3bb3b6801e496ff4ab587e27686e90` |
| HAND / HAND_TO_ARCH / VERIFY | `cc21f3c762bac4f370b25cac0b6c6b3d788a6cfa3008c195a909598ddb8b6152` / `e8cc6058b0c081b01142de559b42c56bc9f7d8eae2d141ef336af0d3fa84c8f6` / `4714256a107a724cfb85b404be9564ed042772b935062c4f5f6bafa276165931` |
| 主交审 | `3806f92228ea8577530773161dc36090ffbe153ade0db804fe1092384397d6aa` |
| ndays40 ABORT / VOID 回执 | `03064d50bc1997e40cff3a10c55d10e91930473472a183d7ac0c0782b514b099` / `ad2947ef0403ff4b2db1e49d9aa0456589f371555cc484a1a83d583282870640` |
| 窗期 | `2026-10-25T16:45:00-04:00` → `2026-10-25T17:30:00-04:00`；expires `2026-10-25T17:32:00-04:00` |
| CLI PRIMARY | `--universe HILIQ --window x2 --chunk-mode ndays --chunk-ndays 40` + hist_prune_r1 |
| FALLBACK | **无**；ABORT→停+另票（禁抬帽；禁 silently 换 mode） |
| rss_limit | **1500** MB（`rss_limit_kb=1536000`）；破帽 ABORT；**禁抬帽** |
| 采样 | 仅 `/tmp`；`/tmp/quantlab_leaf27_chunked_histprune_*` |
| out_dir | `output/ai_factory/leaf27_chunked_members_mktcap_hiliq_x2_histprune` |
| 禁 RESTORED | `a7d98ac9` / `8e51de63` / `3a6caa4f` / `8bcd79dc` / `725be3e0`（已 VOID；禁同 cmd lowmem_v1） |
| FULLA / both / sealed | **不进本窗**（sealed 另签） |
| peak_proof | **REQUIRED** |
| QUIET | 已挂 `output/loop/RESEARCH_QUIET.lock`（保留不 lift） |
| MemAvailable@签 | 7356760 kB |

## 预检旁证

`docs/v2/audit/ARCH_LEAF27_CHUNKED_HIST_PRUNE_PREOK_EVIDENCE_20261025_ZH.md` sha `c0be53016e9622862a64563f6562fb38a9dcf38a1e86fcdb0b591c54c2e178b5`

## QUIET / healthz / pgrep

| 项 | 值 |
|---|---|
| QUIET 挂时 | `2026-10-25T16:50:08-04:00` reason=leaf27_histprune_arch_quiet |
| healthz quiet=true | `2026-10-25T16:50:08-04:00` |
| ≥15s 后复检 | `2026-10-25T16:50:23-04:00` quiet=true；gen/snapshot/kline=false；child_pids={} |
| pgrep | `[k]line.py|[e]xport_static.py|[s]napshot.py|[g]en.py` **空** |

## 下一跳

1. **主**确认后令 AI prelaunch 单次 PRIMARY histprune（须在 expires 前；Arch 不代跑）
2. AI 交实峰回执（阶段 rss / ABORT 或 PASS）→ Arch 核
3. histprune ABORT → **停**；另交主/Arch 票另审另签（勿 silently 换 mode/ndays；**禁抬帽**）
4. ≠X2；live=false
