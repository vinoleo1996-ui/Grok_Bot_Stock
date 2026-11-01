# AI 叶27 Post-GateA baseline_evac · HILIQ×x2×ndays40 RUN_RECEIPT

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI |
| 时刻 | 2026-10-25T22:46:30-04:00（America/New_York；墙钟 2026-10-25 22:46 ET） |
| 状态 | **DONE**（单次 PRIMARY 完结；**非 ABORT**；**禁自复跑**） |
| live / ≠X2 | **false** / **true** |

## 盘证钉

| 项 | 值 |
|---|---|
| ET_TS | `20261025_224033` |
| run_pid / sampler_pid | `1883485` / `1883484`（**均 gone**） |
| `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF27_CHUNKED_MEMBERS_MKTCAP_HILIQ_X2_BASELINE_EVAC.ok` sha8 **`0f50daf7`**（**仍在盘**；听 Arch CONSUME/VOID） |
| QUIET | `output/loop/RESEARCH_QUIET.lock` sha8 **`bdbef3ad`**（**仍挂；未擅 lift**） |
| 脚本 | `research/leaf27_chunked_members_mktcap_r1.py` sha8 **`585ba746`** |
| 主 GO / 窗 | `f8ee378e` / `5930388b` **22:30–23:15** expires **23:17** |
| Arch 审 / SIGNED / 预检 | `84fb87cf` / `36d45a05` / `cf23c902` |
| HAND / H2A / COVER / CMD / DIFF / VERIFY | `b0e01ea4` / `416df9b9` / `0ff59ed4` / `bf6ffe4a` / `dc802879` / `7ddd47e3` |
| CLI | `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf27_chunked_members_mktcap_r1.py --universe HILIQ --window x2 --chunk-mode ndays --chunk-ndays 40` |
| tags | `baseline_evac_r1` + `mktcap_cache_r1` + `hist_prune_r1` |
| rss_limit | **1500** MB（**未抬**） |
| sampdir | `/tmp/quantlab_leaf27_chunked_baseline_evac_20261025_224033` |
| log | `output/ai_factory/leaf27_chunked_members_mktcap_hiliq_x2_baseline_evac/_logs/run_20261025_224033.log` sha8 `d59d0434` |
| out_ok_dir（签文钉 / 日志） | `output/ai_factory/leaf27_chunked_members_mktcap_hiliq_x2_baseline_evac` |
| 脚本 OUT_DIR（继承 / 产物） | `output/ai_factory/leaf27_on_minus_id_idio_ivol`（**双 out 披露**） |
| RUNNING_ACK | `905d2047` |
| launch_status | `abd6012e` |

## 峰证明（REQUIRED）

| 源 | 值 |
|---|---|
| 日志 done | **done rss=1401MB peak=1401MB**（`<1500`；非 ABORT） |
| meta/summary peak_rss_mb | **1401.22265625** |
| sampler_30s peak | **1324124** KB（≈1293.1MB；EXIT；未触发 sampler kill） |
| n_chunks | **17** 全过（chunk_lens 40×16 + 4） |
| lim_evict_n（块末合计） | **2676042**（chunk1+ 非零；chunk0=0） |
| alpha_flush_rows（块末合计） | **1271399**；meta `alpha_flush_total_rows`=**1271399**；`alpha_part_n`=**16** |
| a_buf_n | 各块末均为 **0**（flush 后清空） |
| mktcap_cache_days | 各块 hist 后均为 **2**（drop_before 生效） |
| 对照 | Gate A ABORT 1507@chunk6 / hist-prune 1518 / ndays40 1514 → 本票峰 **1401** 帽内完结 |

## chunk ladder（日志 rss + peak_proof）

| chunk | members | capadv | mktcap_cache (hit/miss/load_n / days / rss) | hist+evac（rss；cache_days；lim_evict；alpha_flush；a_buf） |
|---|---|---|---|---|
| 0 | 418 | 843 | hit=0 miss=40 load_n=40 / days=40 / **901** | 901（cache_days=2；lim_evict_n=0；alpha_flush_rows=0；a_buf_n=0） |
| 1 | 901 | 1222 | hit=1 miss=40 load_n=40 / days=42 / **1294** | 1294（cache_days=2；lim_evict_n=67303；alpha_flush_rows=8561；a_buf_n=0） |
| 2 | 1294 | 1299 | hit=1 miss=40 load_n=40 / days=42 / **1370** | 1370（cache_days=2；lim_evict_n=141222；alpha_flush_rows=51173；a_buf_n=0） |
| 3 | 1370 | 1370 | hit=1 miss=40 load_n=40 / days=42 / **1370** | 1370（cache_days=2；lim_evict_n=147367；alpha_flush_rows=43088；a_buf_n=0） |
| 4 | 1370 | 1370 | hit=1 miss=40 load_n=40 / days=42 / **1372** | 1372（cache_days=2；lim_evict_n=170144；alpha_flush_rows=56777；a_buf_n=0） |
| 5 | 1372 | 1372 | hit=1 miss=40 load_n=40 / days=42 / **1372** | 1372（cache_days=2；lim_evict_n=176211；alpha_flush_rows=83490；a_buf_n=0） |
| 6 | 1372 | 1372 | hit=1 miss=40 load_n=40 / days=42 / **1372** | 1372（cache_days=2；lim_evict_n=182086；alpha_flush_rows=88227；a_buf_n=0） |
| 7 | 1372 | 1372 | hit=1 miss=40 load_n=40 / days=42 / **1372** | 1372（cache_days=2；lim_evict_n=186892；alpha_flush_rows=84295；a_buf_n=0） |
| 8 | 1372 | 1372 | hit=1 miss=40 load_n=40 / days=42 / **1372** | 1372（cache_days=2；lim_evict_n=191257；alpha_flush_rows=89547；a_buf_n=0） |
| 9 | 1372 | 1372 | hit=1 miss=40 load_n=40 / days=42 / **1372** | 1372（cache_days=2；lim_evict_n=195847；alpha_flush_rows=103672；a_buf_n=0） |
| 10 | 1372 | 1372 | hit=1 miss=40 load_n=40 / days=42 / **1372** | 1372（cache_days=2；lim_evict_n=198225；alpha_flush_rows=110879；a_buf_n=0） |
| 11 | 1372 | 1372 | hit=1 miss=40 load_n=40 / days=42 / **1392** | 1392（cache_days=2；lim_evict_n=199497；alpha_flush_rows=106759；a_buf_n=0） |
| 12 | 1392 | 1392 | hit=1 miss=40 load_n=40 / days=42 / **1392** | 1392（cache_days=2；lim_evict_n=200656；alpha_flush_rows=116062；a_buf_n=0） |
| 13 | 1392 | 1392 | hit=1 miss=40 load_n=40 / days=42 / **1400** | 1400（cache_days=2；lim_evict_n=202074；alpha_flush_rows=110769；a_buf_n=0） |
| 14 | 1400 | 1400 | hit=1 miss=40 load_n=40 / days=42 / **1400** | 1400（cache_days=2；lim_evict_n=202574；alpha_flush_rows=106820；a_buf_n=0） |
| 15 | 1400 | 1400 | hit=1 miss=40 load_n=40 / days=42 / **1401** | 1401（cache_days=2；lim_evict_n=198994；alpha_flush_rows=101379；a_buf_n=0） |
| 16 | 1401 | 1401 | hit=1 miss=4 load_n=4 / days=6 / **1401** | 1401（cache_days=2；lim_evict_n=15693；alpha_flush_rows=9901；a_buf_n=0） |

## 产物（OUT_DIR 继承路径）

| 项 | 路径 | sha8 |
|---|---|---|
| alpha | `output/ai_factory/leaf27_on_minus_id_idio_ivol/alpha_HILIQ_x2_20261025_224033.parquet` | `652b8a68` |
| run_meta | `output/ai_factory/leaf27_on_minus_id_idio_ivol/run_meta_HILIQ_x2_20261025_224033.json` | `85c2dc78` |
| build_summary | `output/ai_factory/leaf27_on_minus_id_idio_ivol/build_summary_20261025_224333.json` | `80596bff` |

- n_alpha_rows=**1271399**；span=['2024-06-03', '2026-10-09']；chunk_mode=ndays / ndays=40
- forbid 七票盘证于 meta：`e107383f`/`2be59acd`/`a7d98ac9`/`8e51de63`/`3a6caa4f`/`8bcd79dc`/`725be3e0`
- live=false；promotion_approved=false

## 硬钉（本票后）

- **DONE**；**禁自复跑**；**禁抬帽**；**禁静默换 mode/ndays**；**禁重批旧 Gate A**；**禁 RESTORED** 七票。
- QUIET **未擅 lift**（仍挂；听 Arch CONSUME/lift）。
- `.ok` `0f50daf7` **仍在盘**（听 Arch CONSUME）。
- **禁申 X2**；下一动听主/Arch；≠X2；live=false。
