# AI 叶27 Gate A mktcap_cache · RUNNING 回执

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI |
| 时刻 | 2026-10-25T20:40:28-04:00（America/New_York；墙钟 2026-10-25 20:40 ET） |
| 状态 | **RUNNING**（单次 PRIMARY；禁双开） |
| live / ≠X2 | **false** / **true** |

## 盘证 MATCH

| 项 | 值 |
|---|---|
| `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF27_CHUNKED_MEMBERS_MKTCAP_HILIQ_X2_MKTCAP_CACHE.ok` sha8 **`e107383f`** |
| 主窗 | `c33c6382` **20:30–21:15** expires **21:17** |
| Arch 审 / SIGNED | `64057bfe` / `abe0e71b` |
| 脚本 | `research/leaf27_chunked_members_mktcap_r1.py` **`27aae6db`**（禁 `8cb3e86f`/`262f9bf6`） |
| HAND / H2A / COVER / CMD | `a2abe662` / `4cac1bae` / `bf83073a` / `30c58132` |
| tags | `hist_prune_r1` + `mktcap_cache_r1` |
| QUIET | 已挂不擅 lift；8795 quiet=true |
| pgrep 读者 | 开跑前空（再核空） |
| MemAvailable@launch | ≈10.7Gi（>2.5Gi） |
| 预检 | dry-compile MATCH（live:false / ok_requested:false / rss=1500 / mktcap_cache_r1）；wait≥15s；forbid 六票齐 |

## 执行

| 项 | 值 |
|---|---|
| ET_TS | `20261025_204028` |
| run_pid | `1783498` |
| sampler_pid | `1783497` |
| CLI | `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf27_chunked_members_mktcap_r1.py --universe HILIQ --window x2 --chunk-mode ndays --chunk-ndays 40` |
| rss_limit | **1500** MB（禁抬） |
| sampdir | `/tmp/quantlab_leaf27_chunked_mktcap_cache_20261025_204028` |
| log | `output/ai_factory/leaf27_chunked_members_mktcap_hiliq_x2_mktcap_cache/_logs/run_20261025_204028.log` |
| launch_status sha | `2d0d21c7` |
| begin | `chunk_mode=ndays` n_chunks=17；chunk[0] members≈459MB / capadv≈851MB |

## 硬钉（仍遵守）

- **无同票 FALLBACK**；ABORT→停 + RUN_RECEIPT 上报（另票，禁抬帽；禁 silently 换 mode）
- forbid RESTORED：`2be59acd` / `a7d98ac9` / `8e51de63` / `3a6caa4f` / `8bcd79dc` / `725be3e0`
- 峰证明 REQUIRED；禁擅 lift QUIET；禁申 X2；Arch 不代跑

完后另交 **RUN_RECEIPT**。live=false。
