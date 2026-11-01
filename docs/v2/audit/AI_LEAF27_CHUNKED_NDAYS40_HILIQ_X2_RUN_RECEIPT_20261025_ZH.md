# 叶27 分块装载 HILIQ×x2×ndays40 实峰回执（ABORT_RSS_OVER_LIMIT）

- **角色**：QuantLab AI（执行器）
- **written_et**：2026-10-25T16:24:35-04:00（America/New_York）
- **live**：false · **promotion_approved**：false · **promotion**：false
- **result**：**ABORT_RSS_OVER_LIMIT**
- **retry**：**none**（`ai_no_retry=true` / `ai_no_self_rerun=true`；`forbid_silent_fallback=true`；禁抬帽；禁同 cmd 复跑；禁 RESTORED/`lowmem_v1`；VOID/归档听 Arch；**ABORT→另交 hist-prune**，本回合未静默换 mode）

## 钉与窗

| 项 | 值 |
|---|---|
| `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF27_CHUNKED_MEMBERS_MKTCAP_HILIQ_X2_NDAYS40.ok` |
| `.ok` sha256 | `a7d98ac97a34c3e966577c22168e4d782a247ff0930afc0dea912afa331bac90` |
| `.ok` sha8 | `a7d98ac9` — **MATCH**（仍在盘；**未** VOID/CONSUME；听 Arch） |
| script | `research/leaf27_chunked_members_mktcap_r1.py` |
| script sha256 | `262f9bf6878d5c64956529a680abbf36e45adfe72fc7dedc4c68dc1c40291a10` |
| script sha8 | `262f9bf6` — **MATCH** / UNCHANGED |
| approved_cmd | `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf27_chunked_members_mktcap_r1.py --universe HILIQ --window x2 --chunk-mode ndays --chunk-ndays 40` |
| rss_limit | **1500** MB / 1536000 KB（**未抬帽**） |
| 主令 GO | `005db5df`（`MAIN_LEAF27_CHUNKED_NDAYS40_PRELAUNCH_GO_20261025_ZH.md` 全长 `005db5df5aa768593de254a140fb26bde3709ea02dc8387c3a799652b68ca237`） |
| 窗 / expires | 16:15–17:00 ET / expires 17:02 ET（窗令 `c6fb3c2e`；审 `18ea1567`） |
| QUIET | `output/loop/RESEARCH_QUIET.lock` **全程未 lift**（仍在） |
| 禁 RESTORED | `8e51de63` / `3a6caa4f` / `8bcd79dc` / `725be3e0` — **未复用** |
| 禁 silent fallback | **未**静默换 mode / 未另开 FALLBACK；ABORT 后停，另交 hist-prune 听主/Arch |

## 执行（主钉 ET_TS=20261025_162212）

| 项 | 实填 |
|---|---|
| ET_TS | `20261025_162212` |
| started_et | 2026-10-25T16:22:12-04:00 |
| ended_et | ≈2026-10-25T16:24:04-04:00（日志末行 mtime）；sampler EXIT@16:24:12 ET |
| run_pid | `1576337`（**/proc gone**；`pgrep` 空） |
| sampler_pid | `1576336`（gone；EXIT） |
| rc | **ABORT**（脚本 soft gate `ABORT_RSS_OVER_LIMIT…`；典型退出码 1；本监控无 waitable shell rc） |
| result | **ABORT_RSS_OVER_LIMIT** stage=`chunk6_mktcap` |
| interpreter | `/workspace/qlvenv/bin/python`（`PYTHONDONTWRITEBYTECODE=1`） |
| log | `output/ai_factory/leaf27_chunked_members_mktcap_hiliq_x2_ndays40/_logs/run_20261025_162212.log` sha `ee1b0f417f53f46727ed54f3d7528a13c8e3cd25f1bc8985764b070329b95540` |
| sampler | `/tmp/quantlab_leaf27_chunked_ndays40_20261025_162212/sampler_30s.txt` sha `59ed56ff1a913ebc0417c226e589a88fc07be3c04a568890b607a9f102d29ca9` |
| AI_LAUNCH_STATUS | `output/ai_factory/leaf27_chunked_members_mktcap_hiliq_x2_ndays40/AI_LAUNCH_STATUS_20261025_162212.txt`（`LAUNCHED`；**未二次启动**） |
| sampdir | `/tmp/quantlab_leaf27_chunked_ndays40_20261025_162212` |
| ABORT.txt | **无**（soft gate 写日志行；sampler 未触发 TERM） |

## 实峰（peak_proof）

| 源 | 峰 |
|---|---|
| **日志 rss= 行（准）** | **1514 MB** @ `ABORT_RSS_OVER_LIMIT stage=chunk6_mktcap`（此前 chunk5 freed=1479 / chunk6 capadv=1479） |
| sampler peak_kb | **1147568** KB ≈ **1121 MB**（30s 采样偏低；进程在采样间隔内冲破 1500） |
| run_meta.peak_rss_mb | **无**（`leaf27_on_minus_id_idio_ivol/` 本跑未写出 run_meta_*.json） |
| 破帽 | **YES** 1514 ≫ 1500 → ABORT；**禁抬帽 / 禁自重跑 / 禁静默换 mode** |

### 日志关键路径（摘要）

```
begin rss=103MB chunk_mode=ndays rss_limit=1500
calendar_days=644 n_chunks=17 chunk_lens=[40×16, 4] rss=330MB
chunk[0]…mktcap rss=913MB
chunk[1]…mktcap rss=1290MB
chunk[2]…mktcap rss=1332MB
chunk[3]…mktcap rss=1381MB
chunk[4]…mktcap rss=1410MB
chunk[5]…mktcap rss=1479MB
chunk[6] capadv_days=40 rss=1479MB
ABORT_RSS_OVER_LIMIT stage=chunk6_mktcap rss=1514MB limit=1500
```

### 日志末 ~40 行（核）

```
  chunk[3] mktcap_days=41 rss=1381MB
  2024-08-07 n=1337 rss=1381MB chunk=3
  chunk[3] freed rss=1381MB
  chunk[4] days=40 span=2024-10-11..2024-12-05 members_loaded rss=1381MB
  chunk[4] capadv_days=40 rss=1381MB
  chunk[4] mktcap_days=41 rss=1410MB
  2024-11-08 n=1916 rss=1410MB chunk=4
  chunk[4] freed rss=1410MB
  chunk[5] days=40 span=2024-12-06..2025-02-10 members_loaded rss=1410MB
  chunk[5] capadv_days=40 rss=1430MB
  chunk[5] mktcap_days=41 rss=1479MB
  chunk[5] freed rss=1479MB
  chunk[6] days=40 span=2025-02-11..2025-04-08 members_loaded rss=1479MB
  chunk[6] capadv_days=40 rss=1479MB
ABORT_RSS_OVER_LIMIT stage=chunk6_mktcap rss=1514MB limit=1500 (forbid raise; chunked r1 soft gate)
```

### sampler_30s.txt（全）

```
ts_et rss_kb peak_kb status
2026-10-25T16:22:12-0400 4112 4112 OK
2026-10-25T16:22:42-0400 900888 900888 OK
2026-10-25T16:23:12-0400 991860 991860 OK
2026-10-25T16:23:42-0400 1147568 1147568 OK
2026-10-25T16:24:12-0400 0 1147568 EXIT
```

## 路径披露（双 out）

| 角色 | 路径 |
|---|---|
| `.ok` out_dir / log_dir | `output/ai_factory/leaf27_chunked_members_mktcap_hiliq_x2_ndays40/` · `_logs/` |
| 脚本继承 OUT_DIR（lowmem 同源） | `output/ai_factory/leaf27_on_minus_id_idio_ivol/`（本跑无 alpha/run_meta 写出） |
| sampler（仅 /tmp） | `/tmp/quantlab_leaf27_chunked_ndays40_20261025_162212/`（**未**落 output*/data*） |

## 产物

| 产物 | 状态 |
|---|---|
| alpha parquet | **无** |
| run_meta / build_summary | **无** |
| chunk 完成 | 仅至 chunk[6] mktcap 前破帽；17 块未完（0–5 完成 freed） |

## QUIET / Web

| 项 | 实填 |
|---|---|
| RESEARCH_QUIET.lock | **仍在**；AI **未 lift** |
| 8795/healthz 门 | 开跑前盘证 quiet=true；本回执未改 Web |
| 8787 | 本回执未触；**未重启 Web**（QUIET 中） |

## ABORT 后硬钉（执行器遵守）

- **停**：未抬帽、未复跑、未静默换 mode、未申 X2、未 lift QUIET、未 VOID `.ok`
- **下一跳**：另交 **hist-prune**（听主/Arch 另审另签）；本 `.ok` `a7d98ac9` 单次已消费意图 → **听 Arch VOID/CONSUME**
- **forbid**：RESTORED `8e51de63`/`3a6caa4f`/`8bcd79dc`/`725be3e0`；silent fallback；raise rss；X2.ok；自重跑同 cmd

## 结论

- **PASS**：否  
- **ABORT_RSS**：是（chunk6_mktcap / **1514MB**；sampler peak_kb=**1147568**）  
- **live=false** · **ai_no_retry=true** · **forbid_silent_fallback=true** · 本 `.ok` 单次已消费意图；下一跳（hist-prune 另票或 VOID）**听 Arch/主**，AI 不自申 X2、不抬帽、不复跑、不静默 fallback。
