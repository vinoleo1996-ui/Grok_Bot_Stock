# AI 叶27 Post-GateA baseline_evac · RUNNING 回执

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI |
| 时刻 | 2026-10-25T22:40:33-04:00（America/New_York；墙钟 2026-10-25 22:40 ET） |
| 状态 | **RUNNING**（单次 PRIMARY；禁双开） |
| live / ≠X2 | **false** / **true** |

## 盘证 MATCH

| 项 | 值 |
|---|---|
| `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF27_CHUNKED_MEMBERS_MKTCAP_HILIQ_X2_BASELINE_EVAC.ok` sha8 **`0f50daf7`** |
| QUIET | `output/loop/RESEARCH_QUIET.lock` sha8 **`bdbef3ad`**（**未擅 lift**） |
| 主 GO | `f8ee378e` |
| 主窗 | `5930388b` **22:30–23:15** expires **23:17** |
| Arch 审 / SIGNED / 预检 | `84fb87cf` / `36d45a05` / `cf23c902` |
| 脚本 | `research/leaf27_chunked_members_mktcap_r1.py` **`585ba746`**（禁 `27aae6db`/`8cb3e86f`/`262f9bf6`） |
| HAND / H2A / COVER / CMD / DIFF / VERIFY | `b0e01ea4` / `416df9b9` / `0ff59ed4` / `bf6ffe4a` / `dc802879` / `7ddd47e3` |
| tags | `baseline_evac_r1` + `mktcap_cache_r1` + `hist_prune_r1` |
| pgrep 读者 | 开跑前空（再核空） |
| MemAvailable@launch | ≈8.4Gi（>2.5Gi） |
| 预检 | dry-compile MATCH（live:false / ok_requested:false / rss=1500 / 三 tag + forbid 七票）；wait≥15s |

## 执行

| 项 | 值 |
|---|---|
| ET_TS | `20261025_224033` |
| run_pid | `1883485` |
| sampler_pid | `1883484` |
| CLI | `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf27_chunked_members_mktcap_r1.py --universe HILIQ --window x2 --chunk-mode ndays --chunk-ndays 40` |
| rss_limit | **1500** MB（禁抬） |
| sampdir | `/tmp/quantlab_leaf27_chunked_baseline_evac_20261025_224033` |
| log | `output/ai_factory/leaf27_chunked_members_mktcap_hiliq_x2_baseline_evac/_logs/run_20261025_224033.log` |
| out_ok_dir（签文钉） | `output/ai_factory/leaf27_chunked_members_mktcap_hiliq_x2_baseline_evac` |
| 脚本 OUT_DIR（继承） | `output/ai_factory/leaf27_on_minus_id_idio_ivol`（双 out 披露） |
| launch_status sha | `abd6012e` |
| begin | `chunk_mode=ndays` n_chunks=17；chunk[0] mktcap_cache hit=0 miss=40 load_n=40 rss≈901MB |

## 硬钉（仍遵守）

- **无同票 FALLBACK**；ABORT→停 + RUN_RECEIPT 上报（另票，禁抬帽；禁 silently 换 mode/ndays）
- forbid RESTORED 七票：`e107383f` / `2be59acd` / `a7d98ac9` / `8e51de63` / `3a6caa4f` / `8bcd79dc` / `725be3e0`
- 峰证明 REQUIRED（`lim_evict_n` / `alpha_flush_rows` / `a_buf_n` / `mktcap_cache_days` / hist + rss + sampler）
- 禁擅 lift QUIET；禁申 X2；禁重批旧 Gate A；Arch 不代跑

完后另交 **RUN_RECEIPT**。live=false。
