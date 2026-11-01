# 叶27 HI_LIQ 开跑回执（FAIL / 无产物·RSS 超钉）

- written_et: 2026-10-25T11:14:10-04:00
- by: QuantLab AI（监控+回执；父代理启动研究进程防双开）
- live: false
- promotion_approved: false
- result: **FAIL**
- yield_leaf25_kill: **false**（进程于 ≈11:13:30 ET 自行消失，早于 11:14:30 让出线）
- finished_before_1115: **true**
- quiet_lifted: **true**（父侧 yield_watch EARLY_LIFT @11:13:35 ET；锁已不在 `output/loop/RESEARCH_QUIET.lock`）
- retry: **none**（禁自重跑/自重试；不申新 .ok）

## 钉核验

| 项 | 值 | 状态 |
|---|---|---|
| `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF27_ON_MINUS_ID_IDIO_IVOL_HILIQ.ok` | 现盘 |
| `.ok` sha256 | `725be3e06370927fc6ee115004e017212f7fd1dae077f2dfc63cedd62dae5e1a` | MATCH `725be3e0…` |
| script | `research/g1g5_on_minus_id_idio_ivol_alpha.py` | MATCH |
| script sha256 | `7a5f756c0a1ab09fb55aa2bc3c17f389bde44d222d7066237e503566c908f8c6` | MATCH `7a5f756c…` |
| CLI | `--universe HILIQ --window both` | MATCH（禁 FULLA） |
| out_dir | `output/ai_factory/leaf27_on_minus_id_idio_ivol` | 钉对齐 |
| 禁复用叶25 | `7b279d47` / `1c32ab1e` | 本跑未传 leaf25 arch-ok |
| rss 钉 | ≤1500MB | **BREACH**（见下） |
| window | 10:50–11:12 ET / expires 11:14 | 启动 @11:11:40 ET 仍在 expires 前 |
| leaf25 avoid | 11:15–12:00 ET | 本跑于 11:13 前结束，未撞 |

## 预检证据

- 目录：`output/ai_factory/leaf27_on_minus_id_idio_ivol/_preflight_20261025_110821/`
- QUIET 锁设 @11:08:21 ET；sha `c04dac15cba8536476b8f59ad1f32fac61fb6d8a7cfa38eea60b3967ea056cb0`
- 本地 `ql_quiet.sh` 立即判定 lock 静默；healthz QS 缓存滞后
- `/api/freshness` 无 token→401；带本地 web token 刷新后 quiet=true @**11:10:55 ET**（父注+盘证 `healthz_quiet_true.json`）
- +15s 后闸门：quiet=true；gen/snapshot/kline_running=false；child_pids={}；pgrep web empty；MemAvailable≈12GiB
- 角色分工：本执行器 **STOP 开跑**（防双开）；父代理启动研究进程

## 执行

- ET_TS: `20261025_111140`
- run_pid: **615199**
- sampler_pid: 615198（只写 `/tmp/quantlab_leaf27_20261025_111140/`，禁 output*）
- yield_watch_pid: 616020 → `EARLY_DONE` / `EARLY_LIFT` @11:13:35 ET
- cmdline: `/workspace/qlvenv/bin/python research/g1g5_on_minus_id_idio_ivol_alpha.py --universe HILIQ --window both`
- env: `PYTHONDONTWRITEBYTECODE=1`；interpreter `/workspace/qlvenv/bin/python`；nice -n 10（父侧）
- log: `output/ai_factory/leaf27_on_minus_id_idio_ivol/_logs/run_20261025_111140.log` sha `8f8d3046eaeeeb46a7fd294adcddf8dc0190d0fef1617fd1db0ce3a3b00265b6`
- launch: `…/run_20261025_111140.log.launch` sha `2ac9f1ca3da9e8a715dda8f054d6c0dbea6ae65315418f5fa4647f295b86ec37`
- sampler: `/tmp/quantlab_leaf27_20261025_111140/sampler_30s.txt` sha `a99b9bc1a6b23a61eb635b079033f3a04b629f27c96007a0c8161e34131a3ef2`
- 监控峰值 RSS（ps）：≈**3598 MB**（11:13:28 ET）；日志末行 `2025-05-12 n=2553 rss=3557MB`
- rc: **unknown**（非本执行器 wait 的子进程；无 wrapper EXIT 行；进程 ≈11:13:30 ET 消失 / `proc_gone_early`）
- 日志内容：仅 4 条日进度行（`di%60==0`），**无** `SUMMARY`、**无** Traceback 落盘

## 产物

- **无** `alpha_HILIQ_*.parquet`
- **无** `run_meta_HILIQ_*.json`
- **无** `build_summary_*.json`
- 现盘非预检文件：
  - `_logs/run_20261025_111140.log` size=124 sha256=`8f8d3046eaeeeb46a7fd294adcddf8dc0190d0fef1617fd1db0ce3a3b00265b6`
  - `_logs/run_20261025_111140.log.launch` size=56 sha256=`2ac9f1ca3da9e8a715dda8f054d6c0dbea6ae65315418f5fa4647f295b86ec37`

## 失败判定

1. **无三/无摘要产物** → 研究未完成（死在首个 window 日循环中，未落到 `to_parquet` / `run_meta` / `build_summary`）
2. **RSS 远超钉**（峰值 ≈3.5–3.6 GiB ≫ 1500MB）→ 即使写完亦属钉违约
3. 非本执行器 11:14:30 YIELD 杀停；非撞叶25 窗

## QUIET

- 提升文件：`output/loop/_lifted/RESEARCH_QUIET_leaf27_DONE_LIFTED_20261025_111335ET.lock` sha `c04dac15cba8536476b8f59ad1f32fac61fb6d8a7cfa38eea60b3967ea056cb0`
- 现盘：`RESEARCH_QUIET.lock` **absent**；healthz @11:13:58 ET `quiet=false`（已让出叶25@11:15）

## `.ok` 状态

- 现盘 `.ok` **仍在**（本执行器未消费/未移 `_consumed`）；归档与是否 VOID/重签 **待 Arch**
- AI **不重试**；不改脚本；不申新 .ok

## 请 Arch / 主 Agent

1. **Arch**：归档本回执；裁定 VOID/重签（建议：RSS 降内存或扩钉 + 确认异常退出根因）
2. **主 Agent**：叶27 HI_LIQ **FAIL**；QUIET 已 lift；叶25 v4 `1c32ab1e`@11:15 不被挡
3. Data：本跑无生产写；无需 CONT

live=false。
