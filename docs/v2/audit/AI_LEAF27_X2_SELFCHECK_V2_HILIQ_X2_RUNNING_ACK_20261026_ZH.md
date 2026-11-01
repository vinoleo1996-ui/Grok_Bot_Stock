# AI 叶27 X2 selfcheck_v2 · RUNNING 回执

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI |
| 时刻 | 2026-10-26T01:05:04-04:00（America/New_York；墙钟 2026-10-26 01:05 ET） |
| 状态 | **RUNNING**（单次 PRIMARY；禁双开） |
| live / ≠X2 ACCEPT / ≠Book-Smoke | **false** / **true** / **true** |

## 盘证 MATCH

| 项 | 值 |
|---|---|
| `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF27_X2_SELFCHECK_V2_HILIQ_X2.ok` sha8 **`3c19dd7d`**（∉ forbid 八票） |
| QUIET | `output/loop/RESEARCH_QUIET.lock` sha8 **`69cd9d8e`**（**未擅 lift**；8795 quiet=true） |
| 主 GO | `0e5a37e2` |
| 主窗 | `f268d120` **00:55–01:40** expires **01:42** |
| Arch 审 / SIGNED | `46526394` / `b5484e5a` |
| 脚本 | `research/leaf27_x2_selfcheck_v2.py` **`a40d7069`** |
| 构建脚本 | `research/leaf27_chunked_members_mktcap_r1.py` **`585ba746` UNCHANGED**（禁改） |
| 钉 alpha / meta / summary | **`652b8a68`** / **`85c2dc78`** / **`80596bff`** |
| HAND / H2A / COVER / CMD / DIFF / VERIFY / PIN | `3dd71dc3` / `48aa5db7` / `1e28d0e5` / `61c3ef3b` / `1c4fb74a` / `c47be63a` / `4e0473bd` |
| pgrep 读者 | 开跑前空；wait≥15s + healthz quiet=true 再核 |
| MemAvailable@launch | ≈6.4Gi（主称≈6.6Gi） |
| 预检 | pins/脚本/.ok/QUIET/forbid 八票 MATCH；healthz gen/snapshot/kline=false child_pids={} |

## 执行

| 项 | 值 |
|---|---|
| ET_TS | `20261026_010504` |
| run_pid | `2008153` |
| sampler_pid | `2008152` |
| CLI | `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf27_x2_selfcheck_v2.py --universe HILIQ --window x2 --alpha-path output/ai_factory/leaf27_on_minus_id_idio_ivol/alpha_HILIQ_x2_20261025_224033.parquet --execute` |
| rss_limit | **1500** MB（禁抬；峰＞1500→停+上报） |
| sampdir | `/tmp/quantlab_leaf27_x2_selfcheck_20261026_010504` |
| log | `output/ai_factory/leaf27_on_minus_id_idio_ivol/_selfcheck/_logs/run_20261026_010504.log` |
| weights out | `output/ai_factory/leaf27_on_minus_id_idio_ivol/_selfcheck/eval_weights_HILIQ_x2_<stamp>.parquet` |
| report | `output/ai_factory/leaf_reports/leaf27_on_minus_id_idio_ivol/selfcheck_v2.json` |
| begin rss≈ | ~682MB（launch+2s） |

## 硬钉（仍遵守）

- **无 FALLBACK**；ABORT→停 + RUN_RECEIPT 上报（禁抬帽；禁改构建；禁覆写钉盘 alpha·meta·summary）
- forbid RESTORED 八票：`e107383f` / `2be59acd` / `a7d98ac9` / `8e51de63` / `3a6caa4f` / `8bcd79dc` / `725be3e0` / **`0f50daf7`**
- peak_proof REQUIRED（`rss_mb_peak_self` / `evaluate.peak_rss_mb` / sampler_peak）
- 禁擅 lift QUIET；≠X2 ACCEPT；≠Book-Smoke；Arch 不代跑
- SELFCHECK_EXECUTED 本拍将由实跑置 true（仅本票 evaluate）

完后另交 **RUN_RECEIPT**（权重 sha + selfcheck_v2.json sha + peak）。live=false。
