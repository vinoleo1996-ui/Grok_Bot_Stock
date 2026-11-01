# 叶27 分块装载 HILIQ×x2×ndays40 + hist_prune_r1 实峰回执（ABORT_RSS_OVER_LIMIT）

- **角色**：QuantLab AI（执行器）
- **written_et**：2026-10-25T16:59:20-04:00（America/New_York）
- **live**：false · **promotion_approved**：false · **promotion**：false
- **result**：**ABORT_RSS_OVER_LIMIT**
- **retry**：**none**（`ai_no_retry=true` / `ai_no_self_rerun=true`；`forbid_silent_fallback=true`；禁抬帽；禁同 cmd 复跑；禁 RESTORED；VOID/归档听 Arch；**ABORT→停+回执主（另票）**，本回合未静默换 mode）

## 钉与窗

| 项 | 值 |
|---|---|
| `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF27_CHUNKED_MEMBERS_MKTCAP_HILIQ_X2_HISTPRUNE.ok` |
| `.ok` sha256 | `2be59acd5d201b06eea78ff99354c0acaf21f990e87f02a43e57f247617f6e77` |
| `.ok` sha8 | `2be59acd` — **MATCH**（仍在盘；**未** VOID/CONSUME；听 Arch） |
| script | `research/leaf27_chunked_members_mktcap_r1.py` |
| script sha256 | `8cb3e86f0d5b199c474b38eba1950a44b18e4c0a1ded67d0f371429a55810012` |
| script sha8 | `8cb3e86f` — **MATCH** / hist_prune_r1（禁 `262f9bf6`） |
| approved_cmd | `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf27_chunked_members_mktcap_r1.py --universe HILIQ --window x2 --chunk-mode ndays --chunk-ndays 40` |
| rss_limit | **1500** MB / 1536000 KB（**未抬帽**） |
| 主窗令 | `3a7adb0f`（`MAIN_LEAF27_CHUNKED_HIST_PRUNE_OK_WINDOW_20261025_ZH.md`） |
| 窗 / expires | **16:45–17:30 ET** / expires **17:32 ET**（本跑全程在窗内） |
| Arch 审 | `6543726a` PASS_WITH_CONDITIONS |
| RUNNING_ACK | `17a02110`（`AI_LEAF27_CHUNKED_HIST_PRUNE_RUNNING_ACK_20261025_ZH.md` 全长 `17a02110abdafe177592970f26be9f0157c9a1c40b6da55b53632ae40d609e23`） |
| QUIET | `output/loop/RESEARCH_QUIET.lock` **全程未 lift**（仍在） |
| 禁 RESTORED | `a7d98ac9` / `8e51de63` / `3a6caa4f` / `8bcd79dc` / `725be3e0` — **未复用** |
| 禁 silent fallback | **未**静默换 mode / 未另开 FALLBACK；ABORT 后停，另票听主/Arch |
| ≠X2 | **true**（禁申 X2） |

## 执行（主钉 ET_TS=20261025_165654）

| 项 | 实填 |
|---|---|
| ET_TS | `20261025_165654` |
| started_et | 2026-10-25T16:56:54-04:00 |
| ended_et | ≈2026-10-25T16:58:55-04:00（日志末行 mtime）；sampler EXIT@16:58:56 ET |
| run_pid | `1615483`（**/proc gone**；`pgrep` 空） |
| sampler_pid | `1615481`（gone；EXIT） |
| rc | **ABORT**（脚本 soft gate `ABORT_RSS_OVER_LIMIT…`；典型退出码 1；本监控无 waitable shell rc） |
| result | **ABORT_RSS_OVER_LIMIT** stage=`chunk6_mktcap` |
| interpreter | `/workspace/qlvenv/bin/python`（`PYTHONDONTWRITEBYTECODE=1`） |
| log | `output/ai_factory/leaf27_chunked_members_mktcap_hiliq_x2_histprune/_logs/run_20261025_165654.log` sha `b781497be209a87e5416fbeec9c743c3219c601abce056cf9338b5d1769e107a` |
| sampler | `/tmp/quantlab_leaf27_chunked_histprune_20261025_165654/sampler_30s.txt` sha `458a73c439db83ec2c88d3d5c6455dcf4f5b7e4e4107895b56cf1edd987850f6` |
| AI_LAUNCH_STATUS | `output/ai_factory/leaf27_chunked_members_mktcap_hiliq_x2_histprune/AI_LAUNCH_STATUS_20261025_165654.txt`（`LAUNCHED`；**未二次启动**） |
| sampdir | `/tmp/quantlab_leaf27_chunked_histprune_20261025_165654` |
| ABORT.txt | **无**（soft gate 写日志行；sampler 未触发 TERM） |
| hist_prune_tag | `hist_prune_r1`（块边界 prune+freed 已见日志） |

## 实峰（peak_proof）

| 源 | 峰 |
|---|---|
| **日志 rss= 行（准）** | **1518 MB** @ `ABORT_RSS_OVER_LIMIT stage=chunk6_mktcap`（此前 chunk5 hist_pruned+freed=1485 / chunk6 capadv=1485） |
| sampler peak_kb | **1392852** KB ≈ **1360 MB**（30s 采样偏低；进程在采样间隔内冲破 1500） |
| run_meta.peak_rss_mb | **无**（`leaf27_on_minus_id_idio_ivol/` 本跑未写出 run_meta_*.json） |
| 破帽 | **YES** 1518 ≫ 1500 → ABORT；**禁抬帽 / 禁自重跑 / 禁静默换 mode** |
| vs 前跳 ndays40 | 前跳无 hist_prune 峰 1514@chunk6；本跳 hist_prune 仍破帽 1518@chunk6（略高/同阶段） |

### 日志关键路径（摘要）

```
begin rss=103MB chunk_mode=ndays rss_limit=1500
calendar_days=644 n_chunks=17 chunk_lens=[40×16, 4] rss=328MB
chunk[0]…mktcap rss=894MB → hist_pruned+freed rss=894MB
chunk[1]…mktcap rss=1260MB → hist_pruned+freed rss=1260MB
chunk[2]…mktcap rss=1331MB → hist_pruned+freed rss=1331MB
chunk[3]…mktcap rss=1359MB → hist_pruned+freed rss=1359MB
chunk[4]…mktcap rss=1394MB → hist_pruned+freed rss=1394MB
chunk[5]…mktcap rss=1485MB → hist_pruned+freed rss=1485MB
chunk[6] members_loaded rss=1485MB / capadv rss=1485MB
ABORT_RSS_OVER_LIMIT stage=chunk6_mktcap rss=1518MB limit=1500
```

### 日志末 ~40 行（核）

```
  chunk[3] mktcap_days=41 rss=1359MB
  2024-08-07 n=1223 rss=1359MB chunk=3
  chunk[3] hist_pruned+freed rss=1359MB ret_hist_n=2566 eps_hist_n=1395
  chunk[4] days=40 span=2024-10-11..2024-12-05 members_loaded rss=1359MB
  chunk[4] capadv_days=40 rss=1359MB
  chunk[4] mktcap_days=41 rss=1394MB
  2024-11-08 n=1381 rss=1394MB chunk=4
  chunk[4] hist_pruned+freed rss=1394MB ret_hist_n=3935 eps_hist_n=2353
  chunk[5] days=40 span=2024-12-06..2025-02-10 members_loaded rss=1394MB
  chunk[5] capadv_days=40 rss=1431MB
  chunk[5] mktcap_days=41 rss=1485MB
  chunk[5] hist_pruned+freed rss=1485MB ret_hist_n=3875 eps_hist_n=3124
  chunk[6] days=40 span=2025-02-11..2025-04-08 members_loaded rss=1485MB
  chunk[6] capadv_days=40 rss=1485MB
ABORT_RSS_OVER_LIMIT stage=chunk6_mktcap rss=1518MB limit=1500 (forbid raise; chunked r1 soft gate)
```

### sampler_30s.txt（全）

```
ts_et rss_kb peak_kb status
2026-10-25T16:56:56-0400 780068 780068 OK
2026-10-25T16:57:26-0400 1134344 1134344 OK
2026-10-25T16:57:56-0400 1392852 1392852 OK
2026-10-25T16:58:26-0400 865384 1392852 OK
2026-10-25T16:58:56-0400 0 1392852 EXIT
```

## 路径披露（双 out）

| 角色 | 路径 |
|---|---|
| `.ok` out_dir / log_dir | `output/ai_factory/leaf27_chunked_members_mktcap_hiliq_x2_histprune/` · `_logs/` |
| 脚本继承 OUT_DIR（lowmem 同源） | `output/ai_factory/leaf27_on_minus_id_idio_ivol/`（本跑无 alpha/run_meta 写出） |
| sampler（仅 /tmp） | `/tmp/quantlab_leaf27_chunked_histprune_20261025_165654/`（**未**落 output*/data*） |

## 产物

| 产物 | 状态 |
|---|---|
| alpha parquet | **无** |
| run_meta / build_summary | **无** |
| chunk 完成 | 仅至 chunk[6] mktcap 前破帽；17 块未完（0–5 完成 hist_pruned+freed） |

## QUIET / Web

| 项 | 实填 |
|---|---|
| RESEARCH_QUIET.lock | **仍在**；AI **未 lift** |
| 8795/healthz 门 | 本回执未改 Web；QUIET 全程持 |
| 8787 | 本回执未触；**未重启 Web**（QUIET 中） |

## ABORT 后硬钉（执行器遵守）

- **停**：未抬帽、未复跑、未静默换 mode、未申 X2、未 lift QUIET、未 VOID `.ok`
- **下一跳**：听主/Arch 另票（禁抬帽）；本 `.ok` `2be59acd` 单次已消费意图 → **听 Arch VOID/CONSUME**
- **forbid**：RESTORED `a7d98ac9`/`8e51de63`/`3a6caa4f`/`8bcd79dc`/`725be3e0`；silent fallback；raise rss；X2.ok；自重跑同 cmd

## 结论

- **PASS**：否  
- **ABORT_RSS**：是（chunk6_mktcap / **1518MB**；sampler peak_kb=**1392852**）  
- **live=false** · **ai_no_retry=true** · **forbid_silent_fallback=true** · **≠X2** · 本 `.ok` 单次已消费意图；下一跳（另票或 VOID）**听 Arch/主**，AI 不自申 X2、不抬帽、不复跑、不静默 fallback、不擅 lift QUIET。
