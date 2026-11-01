# 叶25 步骤−1：采样改写 /tmp DIFF（供 Arch 审）

- written_et: 2026-10-25T10:09:00-04:00
- by: QuantLab AI
- live: false
- promotion_approved: false
- scope: **下一窗**例程/操作说明补丁（面向新签窗）；**不**为本已消耗窗重 enable
- 本窗处置: VOID `.ok` `7b279d47…`（Arch 裁定；AI 不重跑、不申 .ok、不改 cmd）

## 1. 背景 / 根因 / Arch 裁定

### 1.1 本窗失败（已证实）

| 项 | 值 |
|---|---|
| 回执 | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_STEP_M1_R5_RUN_RECEIPT_20261025_ZH.md` |
| 回执 sha256 | `af961f32d75c33e42f798aea9f3215326cb341feafb28498fb9fc2a701bdaf2b` |
| wrapper | `docs/v2/audit/cmc_v1_1_leaf24/cmc_wrapper_v4_6174eacb.sh` sha `6174eacb…` |
| cmd（未改） | `LEAF25_STEP_M1_R5c_v3.cmd` sha `be7f5e5a…` |
| ET_TS | `20261025_100250` |
| rc | **96**（C5） |
| C5 日志 sha | `1cc01a013518b291467a22954bf56ac1d378eaac10947e6eb8f2d9ea2b958ce5` |
| exit 摘要 sha | `583ba19ee142438bfdd0650787d1e9c9d8e09398c60390d38a47e03f7591a929` |
| wrapper 内建 sampler sha | `3452d7c8f5aaaf3c4130cf0048586b1329982be18c4337659066d0e5f43e0294` |
| 并行 30s 采样文件 | `output/ai_factory/_leaf25_ttm_recon/20261025_100250_logs/sampler_30s.txt` |

C5_HIT（摘自 `leaf25_step_m1_r5_c5.txt`）：

- pid=**530984** pgid=530888（他进程，非 wrapper mytree）
- `fd:/workspace/QuantLab/output/ai_factory/_leaf25_ttm_recon/20261025_100250_logs/sampler_30s.txt`
- 该 PID = AI 例程 `25-1-10-00` **并行 30s pgrep/Mem 采样器**（写在 `log_dir` 下）
- **非** kline / export_static / snapshot / gen；非 94322；非第二研究进程
- 研究组被 killgrp → rc=96；无三输出、无 `rule_exercised`

### 1.2 Arch 裁定（必须遵守）

- 本窗 **不重签、不重试**；VOID `7b279d47…`
- 新窗前置 = **采样改写 `/tmp`**
- **不接受**放宽 C5 ignore `output*`（不改 wrapper C5 白名单、不借 `--c5-ignore` 规避）
- 修妥本 DIFF 后由**主排窗**再签 `.ok`
- 叶27 例程 10:50 仍执行；**禁复用**叶25钉

## 2. C5 规则位置（只读核）与「写 /tmp 可避开」证明

Wrapper：`cmc_wrapper_v4_6174eacb.sh`（钉 sha `6174eacb4ff2d0905634477430b96bf155d3606794cd66f23a5a38a4f85e4169`）

关键片段（`c5watch`，约 L48–L57）：

1. **排除** mytree（wrapper `$$` 及其子孙）→ wrapper **自带** `$L/${TAG}_sampler.txt`（写在 `log_dir`）安全，因其在树内。
2. **排除** guard pid（默认 94322）与（仅自测且 `.ok` 显式允许时的）`--c5-ignore` pid。
3. **命中条件**（他进程）：
   - cwd ∈ `/workspace/QuantLab/data*` 或 `/workspace/QuantLab/output*`
   - **或** 任一 fd → `/workspace/QuantLab/data/*` **或** `/workspace/QuantLab/output/*`  ← **本窗命中点**
   - **或** maps / cmdline 命中 research|scripts|scripts_eng|`python -m quantlab` 等

结论：

- 并行监控只要持有 **`/workspace/QuantLab/output/...` 打开 fd**，即被 C5 判为外来冲突 → rc=96。
- 将采样文件写到 **`/tmp/...`**（路径不以 `/workspace/QuantLab/output` 或 `.../data` 为前缀）时，**fd/cwd 两条均不命中**；bash 循环 `pgrep`/`/proc/*/status` 的 cmdline 也不触 research/scripts 模式。
- 因此 **无需**改 C5 规则、**无需** `--c5-ignore`、**无需**放宽 ignore `output*`。
- Wrapper 内建 RSS sampler 仍写 `log_dir`（树内排除）——**本 DIFF 不改 wrapper、不改 R5c_v3.cmd**。

## 3. 硬规则（下一窗强制）

1. AI 例程/操作侧启动的**一切并行监控**（含 30s pgrep、Mem/RSS 抽样、额外 tee、旁路日志）输出路径 **必须**落在：
   - `/tmp/quantlab_leaf25_<ET_TS>/`（推荐），或
   - 等价的 **`/tmp` 下专用前缀**（如 `/tmp/quantlab_leaf25_mon/`），且全路径可预知、可回执引用。
2. **禁止**写 `output/**`（含 `output/ai_factory/_leaf25_ttm_recon/<ET_TS>_logs/`、任何 `_logs`、outdir）。
3. **禁止**以「放宽 C5 / ignore output* / `--c5-ignore`」代替路径改写。
4. **禁止**改 `LEAF25_STEP_M1_R5c_v3.cmd` / wrapper；`.ok` **仅**由 Arch 新签。
5. 已消耗窗（`20261025_100250` / VOID `7b279d47`）**不**重 enable；本补丁只服务**新窗**。

## 4. 建议下一窗例程 prompt 补丁（可直接粘贴意图句）

> 并行 30s 监控（pgrep / MemAvailable / 研究 PID RSS 抽样）的输出文件必须写在 `/tmp/quantlab_leaf25_<ET_TS>/`（例如 `sampler_30s.txt`、`pgrep_snap.txt`）；开跑前 `mkdir -p` 该目录。严禁把任何并行监控文件写到 `output/**`（含本次 `log_dir` / `_logs`）。开跑后抽样确认监控 PID 的 `/proc/<pid>/fd/*` 与 `lsof -p <pid>` 均无指向 `/workspace/QuantLab/output` 的打开文件；若发现 output fd，先停监控再开跑。本规则不改变 R5c_v3.cmd、不放宽 C5、不使用 c5-ignore。一次窗、no retry。live=false。

（父代理在 Arch 审过本 DIFF 后再 UpdateRoutine；AI 本轮 **不** UpdateRoutine。）

## 5. 仓库代码变更

**NO_REPO_CODE_CHANGE**

- 误杀源是例程侧并行 shell 采样写 `log_dir`，**不是**仓库内 helper/script。
- 检索：`sampler_30s` 仅见于本窗回执 / log / TEAM_STATE；无独立 `scripts*`/`research*` 采样器脚本需改。
- 不改：`cmc_wrapper_v4_6174eacb.sh`、`LEAF25_STEP_M1_R5c_v3.cmd`、`research/leaf25_ttm_recon_step_m1_r5.py`。
- 无 unified diff 可贴。

## 6. 验收（新窗开跑前 / 中）

开跑前：

1. `mkdir -p /tmp/quantlab_leaf25_<ET_TS>`；监控重定向仅指向该前缀下文件。
2. 启动监控后、wrapper 启动前：对监控 PID 执行 `ls -l /proc/<pid>/fd` 或 `lsof -p <pid>`，确认 **无** `/workspace/QuantLab/output` 前缀打开文件。
3. 钉核照旧：新 `.ok`（Arch 签发）+ `R5c_v3.cmd` `be7f5e5a…` MATCH；静默门禁；Mem；94322 EXITED/T。

开跑中 / 后：

4. C5 文件应为空或不含「sampler / 并行监控」类 fd 命中；若仍 C5，须是真实外来 research/data/output 冲突，而非自采。
5. 回执写明：`mon_dir=/tmp/quantlab_leaf25_<ET_TS>` + 关键监控文件 sha；并附开跑前 fd 抽样摘录。

## 7. 明确不做

| 项 | 状态 |
|---|---|
| 改 R5c_v3.cmd | **不做** |
| 放宽 C5 / ignore `output*` / `--c5-ignore` | **不做**（Arch 明确不接受） |
| 本窗重跑 / 重 enable `25-1-10-00` | **不做** |
| AI 自行申 / 签 `.ok` | **不做**（待 Arch 新签） |
| git commit | **不做** |
| UpdateRoutine | **不做**（父代理于 DIFF 审过后改） |
| 实数据 / 生产跑 | **不做**；live=false |

## 8. 请 Arch / 主

1. **Arch**：审本 DIFF；通过后归档并按主排窗重签新 `.ok`（钉可仍指 R5c_v3，但须新窗/新 `.ok`；VOID 旧 `7b279d47`）。
2. **主**：排新窗（TEAM_STATE 主节已拟 11:15–12:00 ET 避叶27@10:50）；审过后再改例程 prompt。
3. **AI**：等 Arch 审 + 新 `.ok`；叶27@10:50 照例程、禁复用叶25钉。

live=false。
