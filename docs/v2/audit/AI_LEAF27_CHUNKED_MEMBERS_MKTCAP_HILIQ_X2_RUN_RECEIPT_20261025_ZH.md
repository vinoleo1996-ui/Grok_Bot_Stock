# 叶27 分块装载 HILIQ×x2×quarter 实峰回执（ABORT_RSS_OVER_LIMIT）

- **角色**：QuantLab AI（执行器）
- **written_et**：2026-10-25T14:16:05-04:00（America/New_York）
- **live**：false · **promotion_approved**：false · **promotion**：false
- **result**：**ABORT_RSS_OVER_LIMIT**
- **retry**：**none**（`ai_no_self_rerun=true`；禁抬帽；禁同 cmd 复跑；禁 RESTORED/`lowmem_v1`；VOID/归档听 Arch）

## 钉与窗

| 项 | 值 |
|---|---|
| `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF27_CHUNKED_MEMBERS_MKTCAP_HILIQ_X2.ok` |
| `.ok` sha256 | `3a6caa4f20a3881d72e493661592550c982698db80c9a190d7cf919c8fedb758` |
| `.ok` sha8 | `3a6caa4f` — **MATCH** |
| script | `research/leaf27_chunked_members_mktcap_r1.py` |
| script sha256 | `262f9bf6878d5c64956529a680abbf36e45adfe72fc7dedc4c68dc1c40291a10` |
| script sha8 | `262f9bf6` — **MATCH** |
| approved_cmd | `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf27_chunked_members_mktcap_r1.py --universe HILIQ --window x2 --chunk-mode quarter` |
| rss_limit | **1500** MB / 1536000 KB（**未抬帽**） |
| 窗 / expires | 14:00–14:45 ET / expires 14:47 ET |
| QUIET | `output/loop/RESEARCH_QUIET.lock` **全程未 lift** |
| 禁 RESTORED | `8bcd79dc` / `725be3e0` — **未复用** |
| 禁 lowmem_v1 同 cmd | **未执行** `g1g5_*_lowmem_v1.py` |

## 执行（主钉 ET_TS=20261025_141322）

| 项 | 实填 |
|---|---|
| ET_TS | `20261025_141322` |
| started_et | 2026-10-25T14:13:22-04:00 |
| ended_et | ≈2026-10-25T14:15:08-04:00（日志末行；sampler EXIT@14:15:22） |
| run_pid | `1091418`（**/proc gone**；`pgrep` 空） |
| sampler_pid | `1091416`（gone） |
| rc | **ABORT**（脚本 soft gate `SystemExit("ABORT_RSS_OVER_LIMIT…")`；典型退出码 1；本 shell 无 waitable rc） |
| result | **ABORT_RSS_OVER_LIMIT** stage=`chunk4_mktcap` |
| interpreter | `/workspace/qlvenv/bin/python` + `nice -n 10` |
| log | `output/ai_factory/leaf27_chunked_members_mktcap_hiliq_x2/_logs/run_20261025_141322.log` sha `669c2cf76fe6582a8a1d50dab44e3c4158761a74821ed0fd57cb1b4f57e18a54` |
| sampler | `/tmp/quantlab_leaf27_chunked_20261025_141322/sampler_30s.txt` sha `e7d0ece154777702c0e7605e584f5c0ef8f0086d142e202a145fa771bc169cb3` |
| AI_LAUNCH_STATUS | `output/ai_factory/leaf27_chunked_members_mktcap_hiliq_x2/AI_LAUNCH_STATUS_20261025_141322.txt`（`ALREADY_LAUNCHED`；**未二次启动**） |

## 实峰（peak_proof）

| 源 | 峰 |
|---|---|
| **日志 rss= 行（准）** | **1572 MB** @ `ABORT_RSS_OVER_LIMIT stage=chunk4_mktcap`（此前 chunk3=1439 / chunk4 capadv=1475） |
| sampler peak_kb | 938540 KB ≈ **917 MB**（30s 采样偏低；进程在采样间隔内冲破 1500） |
| run_meta.peak_rss_mb | **无**（未写出） |
| 破帽 | **YES** 1572 ≫ 1500 → ABORT；**禁抬帽 / 禁自重跑** |

### 日志关键路径（摘要）

```
begin rss=102MB chunk_mode=quarter rss_limit=1500
calendar_days=644 n_chunks=12 …
chunk[0]…mktcap rss=897MB
chunk[1]…mktcap rss=1288MB
chunk[2]…mktcap rss=1397MB
chunk[3]…mktcap rss=1439MB
chunk[4] capadv_days=57 rss=1475MB
ABORT_RSS_OVER_LIMIT stage=chunk4_mktcap rss=1572MB limit=1500
```

## 路径披露（双 out）

| 角色 | 路径 |
|---|---|
| `.ok` out_dir / log_dir | `output/ai_factory/leaf27_chunked_members_mktcap_hiliq_x2/` · `_logs/` |
| 脚本继承 OUT_DIR（lowmem 同源） | `output/ai_factory/leaf27_on_minus_id_idio_ivol/`（本跑无 alpha/run_meta 写出） |
| sampler（仅 /tmp） | `/tmp/quantlab_leaf27_chunked_20261025_141322/`（**未**落 output*/data*） |

## 产物

| 产物 | 状态 |
|---|---|
| alpha parquet | **无** |
| run_meta / build_summary | **无** |
| chunk 完成 | 仅至 chunk[4] mktcap 前破帽；12 块未完 |

## QUIET / Web

| 项 | 实填 |
|---|---|
| RESEARCH_QUIET.lock | **仍在**；AI **未 lift** |
| 8795/healthz 门 | 开跑前 ok=true quiet=true；gen/snapshot/kline=false |
| 8787 | 不通；**未重启 Web**（QUIET 中） |

## 结论

- **PASS**：否  
- **ABORT_RSS**：是（chunk4_mktcap / 1572MB）  
- **live=false** · **ai_no_self_rerun=true** · 本 `.ok` 单次已消费意图；下一跳（month/ndays 或 VOID）**听 Arch/主**，AI 不自申 X2、不抬帽、不复跑。
