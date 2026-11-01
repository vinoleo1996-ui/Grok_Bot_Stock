# 叶27 分块装载 HILIQ×x2×month 实峰回执（ABORT_RSS_OVER_LIMIT）

- **角色**：QuantLab AI（执行器）
- **written_et**：2026-10-25T15:54:45-04:00（America/New_York）
- **live**：false · **promotion_approved**：false · **promotion**：false
- **result**：**ABORT_RSS_OVER_LIMIT**
- **retry**：**none**（`ai_no_retry=true` / `ai_no_self_rerun=true`；`forbid_silent_ndays=true`；禁抬帽；禁同 cmd 复跑；禁 RESTORED/`lowmem_v1`；VOID/归档听 Arch；**另交 ndays=40 票，本回合未开 ndays**）

## 钉与窗

| 项 | 值 |
|---|---|
| `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF27_CHUNKED_MEMBERS_MKTCAP_HILIQ_X2_MONTH.ok` |
| `.ok` sha256 | `8e51de63d661ae67711bbc169300cf5b3f009806ef71ce4c76a6f2e46c29d9c4` |
| `.ok` sha8 | `8e51de63` — **MATCH**（仍在盘；**未** VOID/CONSUME；听 Arch） |
| script | `research/leaf27_chunked_members_mktcap_r1.py` |
| script sha256 | `262f9bf6878d5c64956529a680abbf36e45adfe72fc7dedc4c68dc1c40291a10` |
| script sha8 | `262f9bf6` — **MATCH** |
| approved_cmd | `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf27_chunked_members_mktcap_r1.py --universe HILIQ --window x2 --chunk-mode month` |
| rss_limit | **1500** MB / 1536000 KB（**未抬帽**） |
| 主令 GO | `4ac3ded4`（`MAIN_LEAF27_CHUNKED_MONTH_PRELAUNCH_GO_20261025_ZH.md`） |
| 窗 / expires | 15:40–16:25 ET / expires 16:27 ET（窗令 `64c7da1e`；审 `85c6fb82`） |
| QUIET | `output/loop/RESEARCH_QUIET.lock` **全程未 lift**（仍在） |
| 禁 RESTORED | `3a6caa4f` / `8bcd79dc` / `725be3e0` — **未复用** |
| 禁 silent ndays | **未**启动 `--chunk-mode ndays` / ndays=40；ABORT 后停，另票听主/Arch |

## 执行（主钉 ET_TS=20261025_154958）

| 项 | 实填 |
|---|---|
| ET_TS | `20261025_154958` |
| started_et | 2026-10-25T15:49:58-04:00 |
| ended_et | ≈2026-10-25T15:53:12-04:00（日志末行 mtime）；sampler EXIT@15:53:28 ET |
| run_pid | `1511644`（**/proc gone**；`pgrep` 空） |
| sampler_pid | `1511643`（gone） |
| rc | **ABORT**（脚本 soft gate `ABORT_RSS_OVER_LIMIT…`；典型退出码 1；本监控无 waitable shell rc） |
| result | **ABORT_RSS_OVER_LIMIT** stage=`chunk12_mktcap` |
| interpreter | `/workspace/qlvenv/bin/python`（`PYTHONDONTWRITEBYTECODE=1`） |
| log | `output/ai_factory/leaf27_chunked_members_mktcap_hiliq_x2_month/_logs/run_20261025_154958.log` sha `c84c66b8a3b1e52e7f966c64575ee4044557b63650eccd7354bd5c71669d7d61` |
| sampler | `/tmp/quantlab_leaf27_chunked_month_20261025_154958/sampler_30s.txt` sha `8b37fab291871526785670470319d336c8e6f65e71ae389bc6dbd5ebad589c67` |
| AI_LAUNCH_STATUS | `output/ai_factory/leaf27_chunked_members_mktcap_hiliq_x2_month/AI_LAUNCH_STATUS_20261025_154958.txt`（`LAUNCHED`；**未二次启动**） |

## 实峰（peak_proof）

| 源 | 峰 |
|---|---|
| **日志 rss= 行（准）** | **1502 MB** @ `ABORT_RSS_OVER_LIMIT stage=chunk12_mktcap`（此前 chunk11=1467 / chunk12 capadv=1467） |
| sampler peak_kb | **1264396** KB ≈ **1235 MB**（30s 采样偏低；进程在采样间隔内冲破 1500） |
| run_meta.peak_rss_mb | **无**（`leaf27_on_minus_id_idio_ivol/` 本跑未写出 run_meta_*.json） |
| 破帽 | **YES** 1502 ≫ 1500 → ABORT；**禁抬帽 / 禁自重跑 / 禁静默 ndays** |

### 日志关键路径（摘要）

```
begin rss=102MB chunk_mode=month rss_limit=1500
calendar_days=644 n_chunks=33 …
chunk[0]…mktcap rss=849MB
chunk[1]…mktcap rss=1174MB
…
chunk[9]…mktcap rss=1419MB
chunk[10]…mktcap rss=1460MB
chunk[11]…mktcap rss=1467MB
chunk[12] capadv_days=18 rss=1467MB
ABORT_RSS_OVER_LIMIT stage=chunk12_mktcap rss=1502MB limit=1500
```

### 日志末 ~40 行（核）

```
  chunk[6] freed rss=1346MB
  chunk[7] days=19 span=2024-09-02..2024-09-30 members_loaded rss=1346MB
  chunk[7] capadv_days=19 rss=1346MB
  chunk[7] mktcap_days=20 rss=1357MB
  chunk[7] freed rss=1357MB
  chunk[8] days=18 span=2024-10-08..2024-10-31 members_loaded rss=1357MB
  chunk[8] capadv_days=18 rss=1357MB
  chunk[8] mktcap_days=19 rss=1357MB
  chunk[8] freed rss=1357MB
  chunk[9] days=21 span=2024-11-01..2024-11-29 members_loaded rss=1357MB
  chunk[9] capadv_days=21 rss=1363MB
  chunk[9] mktcap_days=22 rss=1419MB
  2024-11-08 n=1916 rss=1419MB chunk=9
  chunk[9] freed rss=1419MB
  chunk[10] days=22 span=2024-12-02..2024-12-31 members_loaded rss=1419MB
  chunk[10] capadv_days=22 rss=1419MB
  chunk[10] mktcap_days=23 rss=1460MB
  chunk[10] freed rss=1460MB
  chunk[11] days=18 span=2025-01-02..2025-01-27 members_loaded rss=1460MB
  chunk[11] capadv_days=18 rss=1460MB
  chunk[11] mktcap_days=19 rss=1467MB
  chunk[11] freed rss=1467MB
  chunk[12] days=18 span=2025-02-05..2025-02-28 members_loaded rss=1467MB
  chunk[12] capadv_days=18 rss=1467MB
ABORT_RSS_OVER_LIMIT stage=chunk12_mktcap rss=1502MB limit=1500 (forbid raise; chunked r1 soft gate)
```

## 路径披露（双 out）

| 角色 | 路径 |
|---|---|
| `.ok` out_dir / log_dir | `output/ai_factory/leaf27_chunked_members_mktcap_hiliq_x2_month/` · `_logs/` |
| 脚本继承 OUT_DIR（lowmem 同源） | `output/ai_factory/leaf27_on_minus_id_idio_ivol/`（本跑无 alpha/run_meta 写出） |
| sampler（仅 /tmp） | `/tmp/quantlab_leaf27_chunked_month_20261025_154958/`（**未**落 output*/data*） |

## 产物

| 产物 | 状态 |
|---|---|
| alpha parquet | **无** |
| run_meta / build_summary | **无** |
| chunk 完成 | 仅至 chunk[12] mktcap 前破帽；33 块未完（0–11 完成 freed） |

## QUIET / Web

| 项 | 实填 |
|---|---|
| RESEARCH_QUIET.lock | **仍在**；AI **未 lift** |
| 8795/healthz 门 | 开跑前盘证 quiet=true；本回执未改 Web |
| 8787 | 本回执未触；**未重启 Web**（QUIET 中） |

## ABORT 后硬钉（执行器遵守）

- **停**：未抬帽、未复跑、未启动 ndays=40、未申 X2、未 lift QUIET、未 VOID `.ok`
- **下一跳**：另交 **ndays=40** 票（听主/Arch 另审另签）；本 `.ok` `8e51de63` 单次已消费意图 → **听 Arch VOID/CONSUME**
- **forbid**：RESTORED `3a6caa4f`/`8bcd79dc`/`725be3e0`；silent ndays；raise rss；X2.ok

## 结论

- **PASS**：否  
- **ABORT_RSS**：是（chunk12_mktcap / **1502MB**）  
- **live=false** · **ai_no_retry=true** · **forbid_silent_ndays=true** · 本 `.ok` 单次已消费意图；下一跳（ndays=40 另票或 VOID）**听 Arch/主**，AI 不自申 X2、不抬帽、不复跑、不静默 fallback。
