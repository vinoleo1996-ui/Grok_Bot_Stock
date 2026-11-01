# 主确认：叶27 Gate A mktcap_cache · 签窗

| 项 | 值 |
|---|---|
| 角色 | 主 Agent |
| 时刻 | `2026-10-25T20:17:42.074655-04:00`（America/New_York） |
| Arch 审阅 | `docs/v2/audit/ARCH_LEAF27_CHUNKED_MKTCAP_CACHE_REVIEW_20261025_ZH.md` sha8 **`64057bfe`**（PASS_WITH_CONDITIONS） |
| 盘证包 | COVER `bf83073a` / CMD `30c58132` / DIFF `779197d8` / HAND 盘上 **`a2abe662`**（口头 `70701c1d` 作废） / VERIFY `f01afc74` / H2A **`4cac1bae`** |
| 脚本 | `research/leaf27_chunked_members_mktcap_r1.py` sha8 **`27aae6db`** CHANGED（prev `8cb3e86f`；禁 `8cb3e86f`/`262f9bf6`） |
| 主交审 | `f574b8e1`（MAIN_LEAF27_MKTCAP_CACHE_SUBMIT_ARCH） |
| Leo | 开 A（widget t1129s4890） |
| live / promotion | **false** / **false** |
| 对照 | hist-prune VOID `fd159322` / 回执 `d8be85cb` / 草案 `a2307c8b` / 笔记 `dd193511` |

## 签窗（主确认）

| 项 | 值 |
|---|---|
| 签窗 | **2026-10-25 20:30–21:15 ET** |
| expires | **21:17 ET**（+2min） |
| QUIET | **签时再挂**；现不挂 |
| 错开 | QUIET 无；live `.ok`=0；无 leaf27 进程；Mem≈11Gi |
| 拟 `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF27_CHUNKED_MEMBERS_MKTCAP_HILIQ_X2_MKTCAP_CACHE.ok`（**新签**；禁 RESTORED 六票） |

## `.ok` 硬钉（抄自审 §4–§7）

- CLI PRIMARY（唯一）：`--universe HILIQ --window x2 --chunk-mode ndays --chunk-ndays 40` + 脚本 **`27aae6db`**（全长 `27aae6dbec0c80d96799c3cf6a7baba1bf8eaea866f0dae5feb2876e201175f5`）
- tags：`mktcap_cache_r1` + 保留 `hist_prune_r1`；**无**同票 FALLBACK；ABORT → 停 + 另票（禁 silently 换 mode；禁抬帽）
- `rss_limit_mb=1500` · `forbid_raise_rss_limit=true`
- `forbid_restored_ok_sha8`：**明文六票** `2be59acd`, `a7d98ac9`, `8e51de63`, `3a6caa4f`, `8bcd79dc`, `725be3e0`
- sampler：`/tmp/quantlab_leaf27_chunked_mktcap_cache_*` only
- out_dir **签文钉死**：`output/ai_factory/leaf27_chunked_members_mktcap_hiliq_x2_mktcap_cache`（脚本 OUT_DIR 若仍继承 lowmem → 签文披露双 out + 日志/采样走本 out_dir）
- HAND：钉盘上全长 **`a2abe662f741da7494c341fb70f86b18d639081ae9abf0fb0b5d8b81bcf7aef4`**（禁口头 `70701c1d`）
- H2A `4cac1bae`；COVER/CMD/DIFF/VERIFY 上列 sha8；审 `64057bfe`
- 峰证明 REQUIRED（日志须含 `mktcap_cache hit/miss/load_n` + rss 阶梯 + sampler_30s）；≠X2
- 条件披露：估峰 1400–1490 须实峰；贴帽/再 ABORT → 停另票禁抬帽

## 下一跳

1. **Arch**：入窗（≥20:30 ET）签发上列 `.ok` 并挂短窗 QUIET；窗前不签；HARD 钉 HAND 盘上全长 + out_dir + forbid 六票。
2. **主**：签后盘证 MATCH → 令 AI prelaunch 单次 PRIMARY mktcap_cache。
3. **AI**：停等签窗+主 GO；禁自开跑/禁申.ok/禁抬帽；ABORT → 停等主令；≠X2。

本文件不是 `.ok`。live=false。
