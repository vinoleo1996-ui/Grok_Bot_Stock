# Arch 审阅：叶25 mem_probe 实现包（r1）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器） |
| 时刻 | `2026-10-25T12:03:34-0400`（America/New_York；墙钟 `2026-10-25 12:03:34 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 动作本回合 | **不签 `.ok`** · **不实跑**真实行情/财务大表 · live=false · promotion_approved=false |
| 对齐 | Arch MEM 审 **NEED_MEM_PROBE** `f389c394041cf517b8b8449507bfc157a354e51d2a3f41484adc57d021596d49` |
| 禁复用 | step_m1 `.ok` `1c32ab1e5ffb9eb3ddf466f15b0cd778a1579eaca678f2f5fbe1dd1ae00e66f0`（CONSUMED） |
| rss | C4/stop/hard **1331200 / 1484800 / 1536000** kB；拆块阈 **1131520**（0.85×C4）；**禁抬帽** |
| 拟短窗（主令，供父签） | **2026-10-25 12:10–12:40 ET**（本执行器**不签**） |

## 0. 一句话结论

静态实现包**合格可签独立 probe `.ok`（短窗 / dry 轨）**：门闩、三帽、`/tmp`、禁复用、wrapper v5 齐。**条件**：本 r1 真实 PIT 峰路径仍为 **NotImplemented**——父签的 probe `.ok` **必须钉 dry-run（禁授权 `--allow-real-data` 实读大表）**；CMD 草案里带 `--allow-real-data` 的形参**不得**原样写入本窗 `.ok` 授权命令。dry 峰**不能**单独解锁 X2 内存键；校准峰须等 AI 填 `real_peak_path`（r2）后再另签实数据 probe。

## 1. 输入 sha256 核对（全长）

| 件 | 路径 | 期望 | 盘证 | 结果 |
|---|---|---|---|---|
| COVER | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_MEM_PROBE_IMPL_COVER_20261025_ZH.md` | `24901024ded0a0d2c077e7d766ed63df9848e2dfe7318e7d7da68d2f1529a19d` | 同左 | **MATCH** |
| CMD | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_MEM_PROBE_CMD_DRAFT_20261025_ZH.md` | `c8a853c5e3d76227e0fb34ead0ba99c956c0d9938b620fcea6738f425590ca03` | 同左 | **MATCH** |
| DIFF | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_MEM_PROBE_R1_20261025.diff` | `25bc47bd5ae2040642e5a50ad1ca7715387cdd2a7ad4cf54dcf456856df51f1a` | 同左 | **MATCH** |
| probe | `research/leaf25_full_factor_mem_probe_r1.py` | `a0071e627d37f7e2498ea73984abb5b7ee4b1d2d0d27afdb85f8fc30986aed23` | 同左 | **MATCH** |
| chunk_plan | `research/leaf25_full_factor_chunk_plan_r1.py` | `e858b32d314b9161a366ffef6661605943061162d707f7b86d01439d35dcdb12` | 同左 | **MATCH** |
| build stub | `research/leaf25_cfacc_desens_build_r1.py` | `45537fb9294202f10293b8c0c7b57d9ebf95b835f8af23e3ef63a6dc25c47ee3` | 同左 | **MATCH** |
| Arch MEM 审 | `docs/v2/audit/ARCH_LEAF25_MEM_CHUNK_REVIEW_20261025_ZH.md` | `f389c394041cf517b8b8449507bfc157a354e51d2a3f41484adc57d021596d49` | 同左 | **MATCH** |
| wrapper v5 | `docs/v2/audit/cmc_v1_1_leaf24/cmc_wrapper_v5_4240ce82.sh` | `4240ce82…` | `4240ce82f0929085ab4bcb37e2400a3414e70e162c9e697cf02d97103342f882` | **MATCH** |
| MEM 分块（交叉） | `…/AI_LEAF25_FULL_FACTOR_MEM_ESTIMATE_CHUNK_20261025_ZH.md` | `103717df…` | `103717df1f9e5d63f8c681f16da091f44801e1b69b219ae1a18b2159446145d1` | **MATCH** |

## 2. 静态 / 重建 / 门闩烟测（无真大表）

| 检查 | 结果 |
|---|---|
| `py_compile` → `/tmp/leaf25_{chunk_plan,mem_probe,cfacc_build}_r1.pyc` | **PASS**（`PYTHONPYCACHEPREFIX=/tmp/...`；research **无** leaf25 `__pycache__`） |
| pyflakes 三脚本 | **PASS**（rc=0） |
| `/tmp` 隔离 `patch -p0` 重建 DIFF | 三脚本 + CMD **sha MATCH**；COVER 仅 §2 自钉 sha 行在 DIFF 后补全（文案差，**非**脚本漂移）→ 脚本侧 **PASS**；COVER 以盘 `24901024…` 为准 |
| dry-run 烟测（synthetic cal，`/tmp/quantlab_*`，HI_LIQ month 2024-06） | **PASS** rc=0；peak≈113812 kB ≪ 1131520（**仅结构**，非全叶校准峰） |
| `--allow-real-data` + 假 `.ok` | **STOP**「real peak path not enabled…」（NotImplemented 门闩）rc≠0 |
| `--allow-real-data` 无 `--arch-ok-path` | **STOP** rc=2 |
| `--c4-kb` 上调 | **STOP** ban raise rc=2 |
| `--sample-dir` 落 `output/` | **STOP** `/tmp/quantlab_*` 强制 rc≠0 |

## 3. 审阅要点裁定

| # | 要点 | 裁定 | 说明 |
|---|---|---|---|
| 1 | 对齐 NEED_MEM_PROBE（C4 三帽 / 0.85×C4 / `/tmp` / wrapper v5 / 禁 `1c32ab1e` / 禁与密封·X2 同张） | **PASS** | 脚本常量 `1331200/1484800/1536000`、`SPLIT=1131520`、exit 94/95；COVER/CMD 同钉；`BANNED_OK_SHA` 硬比对；轨文案 mem_probe only |
| 2 | dry vs real-data 门闩 | **PASS_WITH_CONDITIONS** | 默认 dry；真读须 `--allow-real-data` + 现存 `--arch-ok-path` + 禁复用 sha。**另**：即便双闸打开，`real_peak_path_gated` 仍硬退出——**防 densify 合格**，但 CMD 草案示例带 `--allow-real-data` **不能**作为本窗授权命令（会秒退）。签 probe 时须 **dry-only** 或等 r2 实路径 |
| 3 | py_compile/`__pycache__`/DIFF 重建 | **PASS**（COVER 脚注见上） | 见 §2 |
| 4 | 是否足以签**短窗 probe `.ok`**（非 X2） | **YES（带条件）** | 可签 **dry 轨** 短窗 12:10–12:40 ET；**不可**凭本包授权真读大表；dry 峰**不**替代 X2 内存键校准 |
| 5 | 本回合签？ | **否** | 本执行器**不签**；由父按本审条件签发 |

## 4. 是否可签 probe `.ok` / 签前条件

**可以签独立 probe `.ok`（dry / 短窗）——须全部满足：**

1. **轨**：`mem_probe` only；**禁**与密封 / X2 实跑同张；**禁**复用 `1c32ab1e5ffb9eb3ddf466f15b0cd778a1579eaca678f2f5fbe1dd1ae00e66f0`
2. **命令轨**：**dry-run**（默认；可显式 `--synthetic-calendar`）；**禁止**在本窗 `.ok` 授权行写入 `--allow-real-data`（r1 真路径未实现）
3. **wrapper** v5 sha `4240ce82f0929085ab4bcb37e2400a3414e70e162c9e697cf02d97103342f882`；assert/tag 钉 `leaf25_full_factor_mem_probe_r1` / `leaf25_mem_probe_r1`
4. **帽**：c4/stop/hard = **1331200 / 1484800 / 1536000**；`peak_split_threshold_kb=1131520`；`ban_raise_rss_cap=true`；破帽/`≥0.85×C4` → ABORT / exit 94·95，`ai_no_retry=true`
5. **脚本钉**：probe `a0071e627d37f7e2498ea73984abb5b7ee4b1d2d0d27afdb85f8fc30986aed23`；chunk_plan `e858b32d314b9161a366ffef6661605943061162d707f7b86d01439d35dcdb12`
6. **宇宙/块**：`HI_LIQ`；单块 `--mode month`（例 2024-06-03…2024-06-28）或 `rebal_days≤20`；禁 `--window both`；FULLA 非本窗优先
7. **采样**：仅 `/tmp/quantlab_*`（wrapper 默认 `/tmp/quantlab_wrapper_sampler/`）；`allow_c5_ignore=false`
8. **溯源**：`arch_mem_review_sha256=f389c394…`；`mem_estimate_sha256=103717df…`；本审阅文全长（落盘后）；COVER `24901024…`；CMD `c8a853c5…`；DIFF `25bc47bd…`
9. **窗**：主排 **12:10–12:40 ET**；not_before/expires 由父填；live=false
10. **披露预期**：回执须标 `dry_run=true`、`not_real_data`、peak_kb、块边界；并明示 **不足以钉 X2 expected_peak**

## 5. probe `.ok` 应硬钉键（供父签；本回合不落盘）

| 键意图 | 值 / 约束 |
|---|---|
| `track` | `leaf25_mem_probe_r1`（非 X2 / 非密封） |
| `dry_run_only` | **true**（本 r1；禁 `--allow-real-data`） |
| `wrapper_sha256` | `4240ce82f0929085ab4bcb37e2400a3414e70e162c9e697cf02d97103342f882` |
| `c4_limit_kb` / `stopkb` / `rss_limit_kb` | **1331200 / 1484800 / 1536000** |
| `peak_split_threshold_kb` | **1131520** |
| `ban_raise_rss_cap` | true |
| `script_sha256` | probe `a0071e627d37f7e2498ea73984abb5b7ee4b1d2d0d27afdb85f8fc30986aed23` |
| `chunk_plan_sha256` | `e858b32d314b9161a366ffef6661605943061162d707f7b86d01439d35dcdb12` |
| `universe` | `HI_LIQ`；单块 month 或 ≤20 rebal |
| `sampler_root` | `/tmp/quantlab_*` only |
| `ban_reuse_ok` | `1c32ab1e5ffb9eb3ddf466f15b0cd778a1579eaca678f2f5fbe1dd1ae00e66f0` |
| `arch_mem_review_sha256` | `f389c394041cf517b8b8449507bfc157a354e51d2a3f41484adc57d021596d49` |
| `mem_estimate_sha256` | `103717df1f9e5d63f8c681f16da091f44801e1b69b219ae1a18b2159446145d1` |
| `arch_probe_impl_review_sha256` | （本文件落盘全长） |
| `cover_sha256` / `cmd_draft_sha256` / `diff_sha256` | `24901024…` / `c8a853c5…` / `25bc47bd…` |
| `ai_no_retry` | true |
| `live` | false |
| `window` | 12:10–12:40 ET（父填 not_before/expires） |

## 6. 给主 / AI / 父的下一跳

| 角色 | 动作 |
|---|---|
| **父（签）** | 按 §4–§5 **立即**签独立 probe `.ok`（dry-only；窗 12:10–12:40 ET）；**勿**抄 CMD 里的 `--allow-real-data` 行；本执行器**不代签** |
| **AI** | 入窗后仅 dry 命令开跑；回执披露 dry/peak/块；**并行**实现 `real_peak_path`（列投影 PIT→HI_LIQ CS→float32 part→gc）交 r2 包再审；**勿**申 X2 `.ok` |
| **主** | 采纳本审；短窗让 AI 跑 dry probe；X2 14:30 段仍等实数据探针校准 + §8 重验 |
| **Arch** | 本文件即审结；**本回合不签**；消费 dry 回执后不据此签 X2；待 r2 实路径再审另签实数据 probe |

## 7. 总裁定

**PASS_WITH_CONDITIONS** — 八件输入全长 MATCH；三帽/0.85×C4/`/tmp`/禁 `1c32ab1e`/wrapper v5 对齐 NEED_MEM_PROBE；dry 默认与真读双闸 + NotImplemented 防 densify **安全**；`py_compile`/pyflakes/DIFF 脚本重建 PASS。**可签短窗 probe `.ok`（dry-only）**；**不可**本包授权真读大表，也**不可**凭 dry 峰签 X2。本回合 Arch **不签** `.ok`。

live=false。
