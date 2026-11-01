# AI 叶27 ndays40 · RUNNING 回执

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI |
| 时刻 | 2026-10-25T16:22:14-04:00（America/New_York） |
| 状态 | **RUNNING**（单次 PRIMARY；禁双开） |
| live / ≠X2 | **false** / **true** |

## 盘证 MATCH

| 项 | 值 |
|---|---|
| `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF27_CHUNKED_MEMBERS_MKTCAP_HILIQ_X2_NDAYS40.ok` sha **`a7d98ac9`** |
| 主令 GO | `MAIN_LEAF27_CHUNKED_NDAYS40_PRELAUNCH_GO_20261025_ZH.md` sha **`005db5df`** |
| Arch 签发回执 | `bc86ca19`（签收文 `ARCH_LEAF27_CHUNKED_NDAYS40_OK_SIGN_RECEIPT`） |
| 审 / 窗 | `18ea1567` / `c6fb3c2e` **16:15–17:00** expires **17:02** |
| 脚本 | `research/leaf27_chunked_members_mktcap_r1.py` **`262f9bf6`** UNCHANGED |
| QUIET | 已挂不擅 lift；8795 quiet=true |
| pgrep 读者 | 开跑前空 |
| MemAvailable@launch | ≈7.0Gi |

## 执行

| 项 | 值 |
|---|---|
| ET_TS | `20261025_162212` |
| run_pid | `1576337` |
| sampler_pid | `1576336` |
| CLI | `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf27_chunked_members_mktcap_r1.py --universe HILIQ --window x2 --chunk-mode ndays --chunk-ndays 40` |
| rss_limit | **1500** MB（禁抬） |
| sampdir | `/tmp/quantlab_leaf27_chunked_ndays40_20261025_162212` |
| log | `output/ai_factory/leaf27_chunked_members_mktcap_hiliq_x2_ndays40/_logs/run_20261025_162212.log` |
| launch_status sha | `8993df15` |
| begin | `chunk_mode=ndays` n_chunks=17；chunk[0] members_loaded ≈437MB |

## 硬钉（仍遵守）

- **无同票 FALLBACK**；ABORT→停并另交 hist-prune（禁 silently 换 mode）
- forbid RESTORED：`8e51de63` / `3a6caa4f` / `8bcd79dc` / `725be3e0`
- 峰证明 REQUIRED；禁擅 lift QUIET；禁申 X2；Arch 不代跑

完后另交 **RUN_RECEIPT**。live=false。
