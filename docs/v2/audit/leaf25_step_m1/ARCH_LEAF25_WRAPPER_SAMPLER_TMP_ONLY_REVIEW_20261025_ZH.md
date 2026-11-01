# Arch 审阅：叶25 P2 wrapper 采样改尽 `/tmp` DIFF

- written_et: 2026-10-25T11:31:03-04:00
- by: QuantLab Arch（执行器）
- live: false
- promotion_approved: false
- **结论: PASS**
- 范围: 静态审；**不签 `.ok`**；**不实跑**；不放宽 C5；不改 TEAM_STATE
- 输入 DIFF: `docs/v2/audit/leaf25_step_m1/AI_LEAF25_WRAPPER_SAMPLER_TMP_ONLY_DIFF_20261025_ZH.md`
- 前置: 叶25 R5_v4 CONSUMED_PASS（Arch `9c96bf35…`；`.ok` `1c32ab1e` 已消费）；本 P2 为开放项

## 1. 现盘 sha 钉

| 项 | 路径 | sha256 全长 | sha8 | 核对 |
|---|---|---|---|---|
| DIFF文 | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_WRAPPER_SAMPLER_TMP_ONLY_DIFF_20261025_ZH.md` | `9584723f8dcce3907c797fd3b50d15576491a1f3898690b75c97fd707337fa38` | `9584723f` | **MATCH** |
| wrapper_v5 | `docs/v2/audit/cmc_v1_1_leaf24/cmc_wrapper_v5_4240ce82.sh` | `4240ce82f0929085ab4bcb37e2400a3414e70e162c9e697cf02d97103342f882` | `4240ce82` | **MATCH** |
| unified_diff | `docs/v2/audit/leaf25_step_m1/DIFF_cmc_wrapper_v4_to_v5.diff` | `c903234b5afcadec73f911e7c05f27b06a7e3d431801183bc85dfc9a21cca903` | `c903234b` | **MATCH** |
| R5c_v5_cmd | `docs/v2/audit/leaf25_step_m1/LEAF25_STEP_M1_R5c_v5.cmd` | `0b43d5bd59d4e6c6be2917410ebd87f7801474d70f2be8a1b3b68437e7743a49` | `0b43d5bd` | **MATCH** |
| cmd_diff | `docs/v2/audit/leaf25_step_m1/DIFF_cmd_R5c_v4_to_R5c_v5.diff` | `07c2d3a4024c23353c1ff000eafa82b7b557ab26c78e3a1af3e7bf2d023f8b4c` | `07c2d3a4` | **MATCH** |
| static_py | `docs/v2/audit/leaf25_step_m1/check_wrapper_v5_sampler_tmp_only.py` | `78dbea51959dedcf60003819bc4622f3e81a5e0237db9621b62bd2156fa4dd1c` | `78dbea51` | **MATCH** |
| wrapper_v4 | `docs/v2/audit/cmc_v1_1_leaf24/cmc_wrapper_v4_6174eacb.sh` | `6174eacb4ff2d0905634477430b96bf155d3606794cd66f23a5a38a4f85e4169` | `6174eacb` | **MATCH** |
| R5c_v4_cmd | `docs/v2/audit/leaf25_step_m1/LEAF25_STEP_M1_R5c_v4.cmd` | `8231cf2df598716cce30343bc335c8bf645614058eeab9d691a6ef768c011052` | `8231cf2d` | **MATCH** |

文中声称 unified DIFF `c903234b…`、草案 cmd R5c_v5 `0b43d5bd…`：**均现盘 MATCH**（无 GAP）。

## 2. 关键条款核对表

| # | 条款 | 结果 | 证据 |
|---|---|---|---|
| A | 默认采样路径在 `/tmp/...` | **MATCH** | v5 L26：`S="/tmp/quantlab_wrapper_sampler/${TAG}_sampler.txt"`；`mkdir -p /tmp/quantlab_wrapper_sampler` |
| B | `--sampler-dir` / `--sampler-file` 强制 `/tmp` 前缀 | **MATCH** | L27 `case "$S" in /tmp/*)`；L32 `_SABS` 亦须 `/tmp/*`；否则 usage rc=2 |
| C | 硬禁 `output*` / `data*`（含 log_dir 默认 sampler） | **MATCH** | L28/L31 字面+绝对路径拒写；默认不再落 `$L`；`log()` 仅 `>> "$S"` |
| D | 旧根因 v4 `S="$L/${TAG}_sampler.txt"` 已消除 | **MATCH** | v5 全文无该赋值；隔离重建后 `old_default_present=False` |
| E | 不放宽 C5；`allow_c5_ignore` 仍须 `.ok=true` 才放行 | **MATCH** | L44–47 与 v4 同文：实跑给 `--arch-ok` 时无 `allow_c5_ignore=true` → refuse 91；草案 cmd 明示 `allow_c5_ignore=false` 且**未**传 `--c5-ignore` |
| F | C4/STOP/guard/assert 语义相对 v4 不变 | **MATCH** | unified DIFF 仅改 sampler 路径/CLI；STOPKB/C4KB/HARDKB/c5watch 未动 |
| G | `bash -n` wrapper v5 | **PASS** | 现盘与 `/tmp` 隔离副本均 OK |
| H | 静态 py → `/tmp` py_compile + 自检 | **PASS** | `check_wrapper_v5_sampler_tmp_only.py` → `/tmp/check_wrapper_v5_sampler_tmp_only.pyc`；自检 PASS |
| I | unified DIFF 可重建 v5（/tmp 隔离；禁 live `git apply`） | **MATCH** | `/tmp` 内自 patch：rebuilt sha=`4240ce82…` 全长一致；v4 现盘未改 |
| J | 草案 R5c_v5.cmd 钉 v5、禁复用消费 `.ok` | **MATCH（草案）** | wrapper→`cmc_wrapper_v5_4240ce82.sh`；`--arch-ok` 占位 `…_R5_v5.ok`；注明禁复用 `1c32ab1e`；`window_pin=TBD_BY_MAIN` |

### 2.1 非挡备注（P3）

`--sampler-dir` 分支在 `/tmp` 校验**之前**执行 `mkdir -p "$SAMPLER_DIR"`：若误传 `output*`/`data*` 路径，可能先建空目录再 rc=2 拒绝。**不构成采样写入旁路**（随后 case 拒绝，且不会 `log()` 写入该处）。建议后续小 DIFF 把 `mkdir` 挪到校验之后；**不挡本轮 PASS / 不挡采纳 v5**。

## 3. 是否可挂下一叶 cmd（仍不签 `.ok`）

| 问 | 答 |
|---|---|
| 可否采纳 wrapper v5 为后续 cmc 窗钉？ | **可以**（本审 PASS） |
| 可否把草案 `LEAF25_STEP_M1_R5c_v5.cmd`（`0b43d5bd…`）挂为下一窗 cmd 候选？ | **可以挂草案**；须主填 `window_pin` + Arch **新签** `.ok`（占位 `…_R5_v5.ok`） |
| 本执行器是否签 `.ok` / 实跑？ | **否** |
| 已消费 R5_v4 / `1c32ab1e`？ | **禁复用**；不必为已 CONSUMED 窗重开 |

## 4. 开放条件

1. **非挡 P3**：`--sampler-dir` 的 `mkdir` 宜移到路径校验后（见 §2.1）。
2. **排窗/签票**：R5c_v5 仍草案；`window_pin=TBD_BY_MAIN`；新 `.ok` 须钉 wrapper sha `4240ce82…` + cmd sha `0b43d5bd…`，且 `allow_c5_ignore` **不得**为 true。
3. **叶27 降内存**：不在本 DIFF / 本审范围。

## 5. 建议 AI 下一步

1. **无需**为 P2 核心再改 wrapper（除非顺手修 §2.1 mkdir 顺序）。
2. 等主给 `window_pin` 后，用已交 R5c_v5.cmd 申**新** `.ok`（由 Arch/主签；AI 禁自签/自跑）。
3. 叶27 降内存包另交（与本 P2 解耦）。

## 6. 主裁附注（2026-10-25≈11:29 ET）

主裁：P2 挡住全叶 `.ok`；密封/X2 分两张 `.ok`；禁复用 `1c32ab1e`；禁抬帽。

（本审结论 **PASS** → 可供主/Arch 解阻「全叶 `.ok`」之 P2 门；**本文件本身不签任何 `.ok`**。）

live=false。
