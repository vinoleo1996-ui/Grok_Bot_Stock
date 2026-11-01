# Arch：moneyflow deeper P0 reuse-blended **CONSUMED**（研究闭合）

- 角色：QuantLab Arch
- 时刻（America/New_York）：2026-10-25T06:24:38-04:00
- live=false；promotion=false；paper 未动；**未改 research/**；**未抬帽**；out_dir **未挪**（成功产物保留）

## 核验（PASS → CONSUMED，非 VOID）

| 项 | 结果 |
|---|---|
| Strategy 回执路径 | `docs/v2/STRATEGY_MONEYFLOW_STACK_DIAG_DEEPER_P0_RECEIPT_20261025_ZH.md` |
| 回执 **实测** sha256 | `46ff920a7e35c1854eed7cfd57e93d47754e5ec743d76859194b25bf6a1de537`（sha8 `46ff920a`） |
| Strategy 口头 sha8 | `d15fb48d` → **与盘上不一致**；回执文末自报 `f9817a3f…` 亦 **不 MATCH** 盘上；Arch **以 `sha256sum` 实测为准** |
| run.ok（归档前） | `output/strategy_hiliq/ARCH_RUN_AUTH_STRATEGY_MONEYFLOW_STACK_DIAG_DEEPER_P0_REUSE_BLENDED_RUN.ok` |
| run.ok sha256 | `b5425d53498ff81bf7e94beda31547619290b5414ec9f8eec1d815fc468d4abf` **MATCH** |
| EXIT | **0**（无 `VOID.json`） |
| peak VmHWM | **753.8 MB** < rss_cap **2048** |
| blended | `3f8a2b33a995f381ee9e7060858a2029c1a8854a31a32b48ab4842281f188103` **MATCH**（hardlink 复用） |
| summary.json | 存在；sha256 `5718de4cea59ff8e76af76eb2733051a0e9c425b48c645f2ad08b0c917cafd5e` |
| 门 B | **FAIL**（两档 calmar>trunk 但 mdd_le_15=false） |
| GATE_V3 | **FAIL**（`decay_outcome=REJECT` 钉死 → decay_keep=false；两档 mdd_le_25=false） |
| 门控解读 | decay=REJECT **预期失败**；研究诊断 **COMPLETE**，**非 VOID**、非晋级 |
| mf 残留进程 | 无 |
| single_use | 已消费 → **CONSUMED** |

## 归档

| 项 | 值 |
|---|---|
| 消费路径 | `output/strategy_hiliq/_consumed/ARCH_RUN_AUTH_STRATEGY_MONEYFLOW_STACK_DIAG_DEEPER_P0_REUSE_BLENDED_RUN.CONSUMED.20261025T0624ET.ok` |
| MARKER | `output/strategy_hiliq/_consumed/ARCH_RUN_AUTH_STRATEGY_MONEYFLOW_STACK_DIAG_DEEPER_P0_REUSE_BLENDED_RUN.CONSUMED_MARKER.txt` |
| MARKER sha256 | （文末） |
| out_dir | `output/strategy_hiliq/moneyflow_stack_8020_reuse_blended_20261025/`（**保留**；含 ARTIFACT_MANIFEST / summary / meta / blended / book_smoke） |

## 指标一行

`EXIT=0 · VmHWM=753.8<2048 · blended MATCH 3f8a2b33… · 门B/GATE_V3 FAIL（decay=REJECT 预期）· 研究闭合非晋级`

## 约束

- 禁复用废签 `42a16384` / `68c04741`；本签 `b5425d53` 已 CONSUMED，不可再跑
- 补跑 SUSPEND / 叶25 窗 **未动**；live=false

## 本回执

- MARKER sha256：`a476387a029597600202c01165a7bd778adf40024e500e8a4519c11713ae5cce`
- 本文件：落盘后以 `sha256sum` 为准
