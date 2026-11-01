# 叶25 步骤−1 R5 开跑回执（FAIL / rc=96 C5）

- written_et: 2026-10-25T10:04:00-04:00
- by: QuantLab AI（例程 `25-1-10-00`）
- live: false
- promotion_approved: false
- result: **FAIL**
- retry: **none**（例程钉：no retry；rc=124=fail；本轮 rc=96 亦不重试）

## 钉核验（开跑前）

| 项 | 值 | 状态 |
|---|---|---|
| `.ok` 路径 | `output/ai_factory/ARCH_RUN_AUTH_LEAF25_TTM_RECON_STEP_M1_R5_v3.ok` | 现盘 |
| `.ok` sha256 | `7b279d4731760de3c6b194b1d5d93e47acfc5607fa5d05f1defbd5dce07e31a7` | MATCH 现盘钉 `7b279d47…`（旧 `8c77420a` SUPERSEDED_CMDPIN） |
| `cmd_path` | `docs/v2/audit/leaf25_step_m1/LEAF25_STEP_M1_R5c_v3.cmd` | MATCH `.ok` |
| `cmd_sha256` | `be7f5e5a48af13f0dfe30e1363709a697331521c5fae3abd6b28e31a8819b268` | MATCH `be7f5e5a…` |
| window | 10:00–10:45 ET / expires 11:00 | 开跑 @10:02:50 ET 窗内 |
| 94322 | EXITED（形态证 `8eeb0866…`） | PASS |
| MemAvailable | ≈9.0 GiB（≥2.5） | PASS |
| pgrep web readers | empty | PASS |
| Data 窗确认 | `.ok` `data_window_confirm=data_20261025_0025ET_no_prod_write_in_window` + 窗前自采 ps/mem | PASS（旁证） |

## 静默门禁

1. 设 `output/loop/RESEARCH_QUIET.lock` @10:01:08 ET（sha `4a65f3926217974c42ba0eb848e861ca2a2213ee8bc2f386ad5e3e4ed4a2bf1c`）
2. healthz 轮询至 quiet=true @10:02:17 ET（≈61s≤90；经 `/api/freshness` 刷新 QS 缓存后可见）
3. 再等 ≥15s → 10:02:32 ET 复核 quiet=true；gen/snapshot/kline_running=false；child_pids={}
4. 证据目录：`output/ai_factory/_leaf25_ttm_recon/preflight_20261025_100108/`

## 执行

- ET_TS: `20261025_100250`
- out_dir: `output/ai_factory/_leaf25_ttm_recon/20261025_100250/`（**空**，无三输出）
- log_dir: `output/ai_factory/_leaf25_ttm_recon/20261025_100250_logs/`
- void: `output/ai_factory/_void/leaf25_step_m1_r5_rc96_20261025_100256/`
- wrapper: `WRAPPER_DONE tag=leaf25_step_m1_r5 rc=96 stopped=0 peak_kb=379092 C4=PASS`
- exit 摘要 sha: `583ba19ee142438bfdd0650787d1e9c9d8e09398c60390d38a47e03f7591a929`
- sampler sha: `3452d7c8f5aaaf3c4130cf0048586b1329982be18c4337659066d0e5f43e0294`
- c5 sha: `1cc01a013518b291467a22954bf56ac1d378eaac10947e6eb8f2d9ea2b958ce5`

## 失败根因（C5）

- C5_HIT pid=**530984** fd:`…/20261025_100250_logs/sampler_30s.txt`
- 该 PID 是 AI 例程**并行 30s pgrep/Mem 采样器**（写在 log_dir 下），被 wrapper C5 判为「他进程持有 `/workspace/QuantLab/output*` fd」→ kill 研究组 → **rc=96**
- **非** kline/export_static/snapshot/gen 读盘冲突；非 94322；非真实第二研究进程
- 脚本仅到 `STAGE sha_ok`（ru_maxrss≈105468 kB）；**未**写出 raw_rows.csv / ttm_script.csv / run_meta.json；**无** rule_exercised

## `.ok` 状态

- 现盘 `.ok` **仍在**（未消费/未移 `_consumed`）；single_use 消费与归档 **待 Arch**
- AI **不重试**；不擅自改 cmd / 不重签

## 请 Arch / Data / 主 Agent

1. **Arch**：归档本回执；裁定是否 VOID/重签新窗 `.ok`（建议：C5 误伤=操作采样写 output，可重签同钉或新窗；须显式允许/忽略采样路径，或要求采样写 `/tmp`）
2. **Data**：本次 **无需 CONT**（94322 已 EXITED；无生产写）
3. **主 Agent**：转达 Leo——叶25 步骤−1 **未完成**（rc=96）；窗内一次机会已用尽；等 Arch 重签/新窗

## 待 Arch 归档

- 本回执 + log_dir + void 目录 + 现盘 `.ok`（`7b279d47…`）处置

live=false。
