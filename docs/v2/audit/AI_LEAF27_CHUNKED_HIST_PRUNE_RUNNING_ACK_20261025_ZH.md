# AI 叶27 hist-prune · RUNNING 回执

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI |
| 时刻 | 2026-10-25T16:57:11-04:00（America/New_York；墙钟 2026-10-25 16:57 ET） |
| 状态 | **RUNNING**（单次 PRIMARY；禁双开） |
| live / ≠X2 | **false** / **true** |

## 盘证 MATCH

| 项 | 值 |
|---|---|
| `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF27_CHUNKED_MEMBERS_MKTCAP_HILIQ_X2_HISTPRUNE.ok` sha8 **`2be59acd`** |
| 主窗 | `3a7adb0f` **16:45–17:30** expires **17:32** |
| Arch 审 | `6543726a` PASS_WITH_CONDITIONS |
| 脚本 | `research/leaf27_chunked_members_mktcap_r1.py` **`8cb3e86f`**（禁 `262f9bf6`） |
| hist_prune_tag | `hist_prune_r1` |
| QUIET | 已挂不擅 lift；8795 quiet=true |
| pgrep 读者 | 开跑前空（再核空） |
| MemAvailable@launch | ≈7.1Gi（>2.5Gi） |

## 执行

| 项 | 值 |
|---|---|
| ET_TS | `20261025_165654` |
| run_pid | `1615483` |
| sampler_pid | `1615481` |
| CLI | `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf27_chunked_members_mktcap_r1.py --universe HILIQ --window x2 --chunk-mode ndays --chunk-ndays 40` |
| rss_limit | **1500** MB（禁抬） |
| sampdir | `/tmp/quantlab_leaf27_chunked_histprune_20261025_165654` |
| log | `output/ai_factory/leaf27_chunked_members_mktcap_hiliq_x2_histprune/_logs/run_20261025_165654.log` |
| launch_status sha | `e887dde4` |
| begin | `chunk_mode=ndays` n_chunks=17；chunk[0] members_loaded ≈447MB |

## 硬钉（仍遵守）

- **无同票 FALLBACK**；ABORT→停 + 回执主（另票，禁抬帽；禁 silently 换 mode）
- forbid RESTORED：`a7d98ac9` / `8e51de63` / `3a6caa4f` / `8bcd79dc` / `725be3e0`
- 峰证明 REQUIRED；禁擅 lift QUIET；禁申 X2；Arch 不代跑

完后另交 **RUN_RECEIPT**。live=false。
