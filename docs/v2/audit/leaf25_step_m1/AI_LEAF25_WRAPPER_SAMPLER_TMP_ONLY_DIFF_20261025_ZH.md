# 叶25 P2：wrapper 默认采样改尽 `/tmp` DIFF（供 Arch 审）

- written_et: 2026-10-25T11:26:09-04:00
- by: QuantLab AI
- live: false
- promotion_approved: false
- scope: **P2 开放项**（Arch 叶25 R5_v4 CONSUMED_PASS 不挡消费；本 DIFF **不**重开叶25窗、**不**申 `.ok`）
- 前置已消费: Arch 回执 `docs/v2/audit/leaf25_step_m1/ARCH_LEAF25_STEP_M1_R5_V4_CONSUMED_20261025_ZH.md` sha `9c96bf35…`；`.ok` `1c32ab1e` → `_consumed`

## 1. 背景 / 缺口

### 1.1 已闭合（例程侧）

| 项 | 值 |
|---|---|
| 例程并行 30s 采样→`/tmp` DIFF | `AI_LEAF25_SAMPLER_TO_TMP_DIFF_20261025_ZH.md` sha `bcdf617e…` |
| Arch 审 | PASS `91fd02f9…` |
| R5_v4 实跑 | ET_TS `20261025_111646`；并行采样 `/tmp/leaf25_step_m1_r5_20261025_111646_sampler_30s.txt`；**未 C5**；CONSUMED_PASS |

### 1.2 仍开放（wrapper 默认）

R5_v4 回执核：`output/ai_factory/_leaf25_ttm_recon/20261025_111646_logs/leaf25_step_m1_r5_sampler.txt` **3672 B** 仍在（wrapper 内建 RSS/`log()` 默认写 `log_dir`）。

根因（钉核 v4）：

```
# cmc_wrapper_v4_6174eacb.sh L20
mkdir -p "$L"; S="$L/${TAG}_sampler.txt"; ...
```

- 树内 mytree 排除 → **本轮未 C5**（与晨间例程侧 `sampler_30s.txt` 误杀不同）
- 但与 R5c_v4 / Arch「采样改尽 `/tmp`」钉不一致；P2 要求 **默认**也离开 `output*`

Arch 原话（CONSUMED 回执）：「后续须 DIFF 把默认采样改尽 `/tmp`（与 v4 钉一致），再送 Arch 审。」

## 2. 变更（脚本草案）

### 2.1 新 wrapper（v4 继任；v4 文件不动）

| 项 | 值 |
|---|---|
| 新文件 | `docs/v2/audit/cmc_v1_1_leaf24/cmc_wrapper_v5_4240ce82.sh` |
| sha256 全长 | `4240ce82f0929085ab4bcb37e2400a3414e70e162c9e697cf02d97103342f882` |
| sha8 | `4240ce82` |
| 前驱（不变） | `cmc_wrapper_v4_6174eacb.sh` sha `6174eacb4ff2d0905634477430b96bf155d3606794cd66f23a5a38a4f85e4169` |
| unified diff | `docs/v2/audit/leaf25_step_m1/DIFF_cmc_wrapper_v4_to_v5.diff` sha `c903234b5afcadec73f911e7c05f27b06a7e3d431801183bc85dfc9a21cca903` |
| `bash -n` | **OK** |
| 实跑 / 自测 sleep | **未做**（本轮无实跑） |

### 2.2 行为差（相对 v4）

1. **默认** `S=/tmp/quantlab_wrapper_sampler/${TAG}_sampler.txt`（`mkdir -p` 该目录）
2. 可选覆盖：`--sampler-dir DIR` 或 `--sampler-file PATH`（**必须**字面与绝对路径均落在 `/tmp/*`）
3. **硬拒**（usage rc=2，启动前）：
   - 路径不以 `/tmp/` 开头
   - 或字面/绝对路径落在 `/workspace/QuantLab/output*` 或 `.../data*`
4. 启动后立刻 `log "SAMPLER_PATH $S"`，便于回执核对
5. **不变**：`--logdir` 下仍写 `*_exit.txt` / `*_c5.txt` / `*.log` / `*_start.marker` / `*_ps_{before,after}.txt`；C5/C4/STOP/guard/`--c5-ignore` 策略同 v4；**不**放宽 C5、**不** ignore `output*`

### 2.3 静态验收（无盘读业务）

| 检查 | 结果 |
|---|---|
| `bash -n` wrapper v5 | OK |
| 静态脚本 | `docs/v2/audit/leaf25_step_m1/check_wrapper_v5_sampler_tmp_only.py` sha `78dbea51959dedcf60003819bc4622f3e81a5e0237db9621b62bd2156fa4dd1c` |
| `py_compile` → `/tmp/check_wrapper_v5_sampler_tmp_only.pyc` | OK |
| `/tmp/ql_pyflakes_venv` pyflakes | OK（无告警） |
| 静态 PASS（禁旧默认 `S="$L/${TAG}_sampler.txt"`；必含 `/tmp/quantlab_wrapper_sampler` 等） | PASS |

## 3. 叶25 cmd 草案（**非**排窗、**不**申 `.ok`）

供 Arch 若要将后续叶25/同类窗钉到 v5 时选用；**本 P2 成功标准 = wrapper DIFF 可审**，不强制新开叶25。

| 项 | 值 |
|---|---|
| 草案 cmd | `docs/v2/audit/leaf25_step_m1/LEAF25_STEP_M1_R5c_v5.cmd` |
| sha256 全长 | `0b43d5bd59d4e6c6be2917410ebd87f7801474d70f2be8a1b3b68437e7743a49` |
| cmd diff | `docs/v2/audit/leaf25_step_m1/DIFF_cmd_R5c_v4_to_R5c_v5.diff` sha `07c2d3a4024c23353c1ff000eafa82b7b557ab26c78e3a1af3e7bf2d023f8b4c` |
| 相对 v4 唯一运行行变 | wrapper → `cmc_wrapper_v5_4240ce82.sh`；`--arch-ok` 占位 `..._R5_v5.ok`（**须新签**；禁复用 `1c32ab1e`） |
| window_pin | `TBD_BY_MAIN` |
| research 脚本 | **未改**（仍 `f43b9016…`） |

## 4. 硬规则（采纳后）

1. 凡钉 `cmc_wrapper_v5_*` 的窗：内建 RSS/`log()` 采样 **只**在 `/tmp/...`；回执须抄 `SAMPLER_PATH` 行。
2. 并行例程监控继续遵守已 PASS 的 `bcdf617e…`（`/tmp` only）。
3. **禁止**放宽 C5 / `--c5-ignore` 整棵 `output*` 代替路径改写。
4. **禁止** AI 自重跑已消费叶25、自申 `.ok`、git commit。
5. v4 wrapper 保留不动，供历史钉溯源。

## 5. 明确不做

| 项 | 状态 |
|---|---|
| 实数据 / 生产 / 叶25 重跑 | **不做** |
| 申 / 签 `.ok` | **不做** |
| 放宽 C5 / ignore `output*` | **不做** |
| 改 `research/leaf25_ttm_recon_step_m1_r5.py` | **不做** |
| git commit | **不做** |
| 改已消费窗产物 | **不做** |

## 6. 请 Arch

1. 审本 DIFF + wrapper v5 sha `4240ce82…`（全长见上）+ `DIFF_cmc_wrapper_v4_to_v5.diff`。
2. 通过后：后续新窗（叶25 若再排 / 其他 cmc 窗）钉 v5；**不必**为已 CONSUMED 的 R5_v4 重开。
3. R5c_v5.cmd 仅为草案；是否签 `.ok` / 排窗由主+Arch 另决。

live=false。
