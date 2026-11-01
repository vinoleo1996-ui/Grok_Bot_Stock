# AI 叶27 Gate A mktcap_cache · HILIQ×x2×ndays40 RUN_RECEIPT

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI |
| 时刻 | 2026-10-25T20:42:29-04:00（America/New_York；墙钟 2026-10-25 20:42 ET） |
| 状态 | **ABORT_RSS**（单次 PRIMARY 已停；**禁复跑**） |
| live / ≠X2 | **false** / **true** |

## 盘证钉

| 项 | 值 |
|---|---|
| ET_TS | `20261025_204028` |
| run_pid / sampler_pid | `1783498` / `1783497`（**均 gone**） |
| `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF27_CHUNKED_MEMBERS_MKTCAP_HILIQ_X2_MKTCAP_CACHE.ok` sha8 **`e107383f`**（**仍在盘**；听 Arch VOID/CONSUME） |
| 脚本 | `research/leaf27_chunked_members_mktcap_r1.py` sha8 **`27aae6db`** |
| 主窗 | `c33c6382` **20:30–21:15** expires **21:17** |
| Arch 审 / SIGNED | `64057bfe` / `abe0e71b` |
| HAND / H2A / COVER / CMD | `a2abe662` / `4cac1bae` / `bf83073a` / `30c58132` |
| CLI | `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf27_chunked_members_mktcap_r1.py --universe HILIQ --window x2 --chunk-mode ndays --chunk-ndays 40` |
| tags | `hist_prune_r1` + `mktcap_cache_r1` |
| rss_limit | **1500** MB（**未抬**） |
| sampdir | `/tmp/quantlab_leaf27_chunked_mktcap_cache_20261025_204028` |
| log | `output/ai_factory/leaf27_chunked_members_mktcap_hiliq_x2_mktcap_cache/_logs/run_20261025_204028.log` |
| RUNNING_ACK | `3f0a5d8c` |
| launch_status | `2d0d21c7` |

## 峰证明（REQUIRED）

| 源 | 值 |
|---|---|
| 日志峰 | **1507MB** @ stage=`chunk6_mktcap`（`ABORT_RSS_OVER_LIMIT … limit=1500`） |
| sampler_30s peak | **898968** KB（≈878MB；EXIT；未触发 sampler kill） |
| 对照 | hist-prune 1518@chunk6；ndays40 1514@chunk6 — Gate A 仍同阶尖峰 |

## chunk ladder（日志 rss）

| chunk | members | capadv | mktcap_cache (hit/miss/load_n / days / rss) | hist_pruned rss |
|---|---|---|---|---|
| 0 | 459 | 851 | hit=0 miss=40 load_n=40 / days=40 / **883** | 883（cache_days=2） |
| 1 | 883 | 1233 | hit=1 miss=40 load_n=40 / days=42 / **1286** | 1286 |
| 2 | 1286 | 1286 | hit=1 miss=40 load_n=40 / days=42 / **1333** | 1333 |
| 3 | 1333 | 1333 | hit=1 miss=40 load_n=40 / days=42 / **1381** | 1381 |
| 4 | 1381 | 1381 | hit=1 miss=40 load_n=40 / days=42 / **1425** | 1425 |
| 5 | 1425 | 1437 | hit=1 miss=40 load_n=40 / days=42 / **1497** | 1497 |
| 6 | 1497 | 1497 | **ABORT @ mktcap 1507** | — |

## mktcap_cache 摘要

- 每块均见 `mktcap_cache hit/miss/load_n` 行；chunk0 冷启动 miss=40；此后 hit≈1、miss=40、load_n=40（跨块仅补日，**未**回到 12-RG 全表语义）。
- hist_prune 后 `mktcap_cache_days=2`（保留日窗生效）；**HWM 未回落**（chunk0→5 单调升至 1497，chunk6 触 1507）。
- Gate A 缓存路径已生效，但 **rss 帽内仍不够**；**禁抬帽**；下一票听主/Arch。

## 硬钉（本票后）

- **已停**；**禁复跑**；**禁抬帽**；**禁静默换 mode/ndays**；**禁 RESTORED** 六票 + 本票 `.ok` 一经 VOID。
- QUIET **未擅 lift**（仍挂；听 Arch）。
- **禁自拟下一票**；等 Arch VOID `e107383f` + 主令。
- ≠X2；live=false。
