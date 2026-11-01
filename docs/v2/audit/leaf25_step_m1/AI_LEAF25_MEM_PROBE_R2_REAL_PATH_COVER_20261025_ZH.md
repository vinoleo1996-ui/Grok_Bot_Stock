# 叶25 mem_probe r2 · 实峰路径增量封面（交 Arch 审）

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI（执行器） |
| 起草 | `2026-10-25T12:11:55-0400`（America/New_York；墙钟 `2026-10-25 12:11:55 ET`） |
| 状态 | **r2 实峰路径已落地** · **未申 `.ok`** · **本回合未读真实行情/财务大表** |
| live | **false** · promotion_approved **false** |
| 对齐 Arch 裁定 | `docs/v2/audit/ARCH_LEAF25_MEM_PROBE_ADOPT_A_REJECT_REAL_PEAK_20261025_ZH.md` → **FAIL_FOR_REAL_PEAK / (A)** sha **`14e9b6ba161057fe73015decf789041eef2a1e910e0ef656c16dcb85d78bce4e`** |
| 相对 r1 | r1 `real_peak_path_gated`=NotImplemented（sha `a0071e627d37f7e2498ea73984abb5b7ee4b1d2d0d27afdb85f8fc30986aed23`）→ **Arch 拒签任何 probe `.ok`（含 dry）**；本 r2 **填实** `real_peak_path`，另审另签实峰短窗 |
| 动作本回合 | 新脚本 + `py_compile`→`/tmp` + pyflakes + dry 结构烟测 + 本封面/CMD/DIFF；**禁** `--allow-real-data` 实跑 · **禁**申 `.ok` · **禁**抬帽 · **禁** git commit |

## 0. 目的

落实 Arch 采纳 **(A)**：r1 不得签实峰（亦拒签 DRY_STRUCTURAL 入窗）。交付 **r2** 最小真实峰路径实现包（列投影 PIT→HI_LIQ 截面 α→float32 part→gc），交 Arch **另签独立实峰 probe `.ok`**。本包**不等于**授权开跑。

## 1. 输入 sha256 核对（全长）

| 件 | 路径 | sha256 | 结果 |
|---|---|---|---|
| Arch 采纳 (A) 拒签实峰 | `docs/v2/audit/ARCH_LEAF25_MEM_PROBE_ADOPT_A_REJECT_REAL_PEAK_20261025_ZH.md` | `14e9b6ba161057fe73015decf789041eef2a1e910e0ef656c16dcb85d78bce4e` | **MATCH** |
| Arch NEED_MEM_PROBE | `docs/v2/audit/ARCH_LEAF25_MEM_CHUNK_REVIEW_20261025_ZH.md` | `f389c394041cf517b8b8449507bfc157a354e51d2a3f41484adc57d021596d49` | **MATCH** |
| MEM 分块 | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_FULL_FACTOR_MEM_ESTIMATE_CHUNK_20261025_ZH.md` | `103717df1f9e5d63f8c681f16da091f44801e1b69b219ae1a18b2159446145d1` | **MATCH** |
| r6 FROZEN 戳 | `docs/v2/AI_LEAF25_FULL_FACTOR_PREREG_r6_FROZEN_20261025_ZH.md` | `4bb1ff2b805f441499607ada5f871044e72e6176a66052c73b64816130d199e2` | **MATCH** |
| wrapper v5 | `docs/v2/audit/cmc_v1_1_leaf24/cmc_wrapper_v5_4240ce82.sh` | `4240ce82f0929085ab4bcb37e2400a3414e70e162c9e697cf02d97103342f882` | **MATCH** |
| r1 probe（被 SUPERSEDE 实路径） | `research/leaf25_full_factor_mem_probe_r1.py` | `a0071e627d37f7e2498ea73984abb5b7ee4b1d2d0d27afdb85f8fc30986aed23` | 保留 dry 骨架；**不**再申 r1 `.ok` |

## 2. 交付物 sha256（全长）

| 件 | 路径 | sha256 | 注 |
|---|---|---|---|
| **mem_probe r2** | `research/leaf25_full_factor_mem_probe_r2.py` | **`9dfe173a9104330287f6ebfe2f758c63891f3c92b5f9d112118b697898d50e0f`** | **NEW**；`real_peak_path` 已实现 |
| chunk_plan | `research/leaf25_full_factor_chunk_plan_r1.py` | `e858b32d314b9161a366ffef6661605943061162d707f7b86d01439d35dcdb12` | **UNCHANGED** |
| build stub | `research/leaf25_cfacc_desens_build_r1.py` | `45537fb9294202f10293b8c0c7b57d9ebf95b835f8af23e3ef63a6dc25c47ee3` | **UNCHANGED** |
| 本封面 | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_MEM_PROBE_R2_REAL_PATH_COVER_20261025_ZH.md` | 以盘 `sha256sum` 为准（落盘后自钉） |
| probe cmd 草案 | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_MEM_PROBE_R2_CMD_DRAFT_20261025_ZH.md` | `837078627aab3b93190607609ca3620c8b1d5decdabc62a866f53371836df74a` |
| unified DIFF | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_MEM_PROBE_R2_20261025.diff` | `e0d9acdb973d80647fccd89aec8b27e59c2c1fd441a25aa87680a82629e1c6a8` |

## 3. r2 实峰路径要点（相对 Arch 条件）

| 要求 | 本包落实 |
|---|---|
| 去 NotImplemented；PIT→截面α→分区→gc | `real_peak_path()`：列投影 income/cashflow/balance → HI_LIQ CS 粗应计 zscore → `alpha_parts/chunk_XXXX.parquet`（float32）→ del+gc |
| HI_LIQ 单块；禁 both；FULLA 非本轮 | 默认 `--universe HI_LIQ`；实路径对 FULLA **STOP**；无 `--window both` 参数 |
| 列投影；禁整窗 densify | KEY1+VAL 投影 + `end_date` 下界 + codes 过滤；长表按日截面，不宽面板 densify |
| HI_LIQ mask | 默认 `output/strategy_hiliq/universe_mask_hiliq_v1.parquet`；缺文件 / 块空 → **清晰 STOP**（禁 silent FULLA） |
| 门闩 | `--allow-real-data` + 现存 `--arch-ok-path`；硬禁复用 `1c32ab1e5ffb9eb3ddf466f15b0cd778a1579eaca678f2f5fbe1dd1ae00e66f0`；无 `.ok` → STOP rc=2 |
| C4 三帽 / 0.85×C4 / 禁抬 | 1331200/1484800/1536000；split=1131520；上调 → STOP rc=2；≥split exit 94；≥hard exit 95 |
| 采样 | `--sample-dir` 强制 `/tmp/quantlab_*` |
| α 口径披露 | `crude_accrual_cs_zscore_probe_only`；`claims_full_cfacc=false`（**勿**当全叶 CFACC 完成） |
| wrapper v5 | CMD 草案钉 `4240ce82f0929085ab4bcb37e2400a3414e70e162c9e697cf02d97103342f882` |
| 未申 `.ok` | 本回合仅交审；实跑须 Arch 另签实峰 probe `.ok` + 主排短窗 |

## 4. 禁项

- **禁**申 X2 实跑 `.ok`；**禁**本回合申 probe `.ok`
- **禁**复用 step_m1 `.ok` `1c32ab1e5ffb9eb3ddf466f15b0cd778a1579eaca678f2f5fbe1dd1ae00e66f0`
- **禁**抬 C4/stop/hard；破帽/破 0.85×C4 → 拆块，不自抬帽重试
- **禁**整窗 densify；**禁** `--window both`
- **禁**采样写入 `output*` / `data*`
- **禁**本回合 `--allow-real-data` 读真大表（仅 dry 结构烟测）
- **禁** git commit；**禁** research `__pycache__`
- **禁**再为 r1 dry 窗做准备 / 申 r1 `.ok`（Arch `14e9b6ba…` 已拒）

## 5. 静态检查（本回合）

| 检查 | 结果 |
|---|---|
| `py_compile` → `/tmp/leaf25_mem_probe_r2.pyc` | **PASS** |
| `py_compile` chunk_plan / stub → `/tmp` | **PASS**（UNCHANGED） |
| pyflakes `leaf25_full_factor_mem_probe_r2.py` | **PASS**（rc=0） |
| research `__pycache__` 新增 r2 | **无** |
| dry-run 烟测（synthetic cal，HI_LIQ month 2024-06，`/tmp/quantlab_*`） | **PASS** rc=0 |
| `--allow-real-data` 无 `--arch-ok-path` | **STOP** rc=2 |
| `--c4-kb` 上调 | **STOP** rc=2 |
| 静态 import：`real_peak_path` callable 且源无 NotImplemented | **PASS** |

## 6. 给 Arch / 主的下一跳

1. **Arch**：审本 r2 包（脚本 `9dfe173a9104330287f6ebfe2f758c63891f3c92b5f9d112118b697898d50e0f` + 本封面 + CMD + DIFF）；通过后**另签独立实峰 probe `.ok`**（钉 wrapper v5 / C4 三帽 / `/tmp` / HI_LIQ 单块 month|rebal≤20 / 禁 `1c32ab1e` / `ai_no_retry` / **允许** `--allow-real-data`）。**勿**签 r1 dry。
2. **主**：排实峰 mem_probe 短窗；勿占用拟 X2 14:30–16:00 全段除非探针极短。
3. **AI**：等实峰 probe `.ok` + 入窗后再 `--allow-real-data`；回执披露 float32 / densify=false / peak_kb / 块边界 / `claims_full_cfacc=false`；**勿**申 X2 `.ok`。

live=false；promotion_approved=false。
