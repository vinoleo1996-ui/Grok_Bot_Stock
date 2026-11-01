# 叶25 mem_probe 实现包封面（交 Arch 审）

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI（执行器） |
| 起草 | `2026-10-25T11:57:36-0400`（America/New_York；墙钟 `2026-10-25 11:57:36 ET`） |
| 状态 | **NEED_MEM_PROBE 实现包已落盘** · **未申 `.ok`** · **本回合未读真实行情/财务大表** |
| live | **false** · promotion_approved **false** |
| 对齐 | Arch 审 `ARCH_LEAF25_MEM_CHUNK_REVIEW_20261025_ZH.md` → **NEED_MEM_PROBE** |
| 动作本回合 | 静态实现 + `py_compile`→`/tmp` + pyflakes + 文档/DIFF；**禁**实跑大表 · **禁**申 X2/probe `.ok` · **禁** git commit · **禁**抬 RSS 帽 |

## 0. 目的

落实 Arch §3 / §6：**先**交付 mem_probe + 最小 chunk_plan 实现包并交静态审；**不得**据此直接签 X2 实跑 `.ok`。正式峰路径（读 PIT→截面 α→落盘分区→gc）仅在 Arch **另签独立 probe `.ok`** 且主排短窗后触发。

## 1. 输入 sha256 核对（全长）

| 件 | 路径 | 期望 | 盘证 |
|---|---|---|---|
| Arch 审 NEED_MEM_PROBE | `docs/v2/audit/ARCH_LEAF25_MEM_CHUNK_REVIEW_20261025_ZH.md` | `f389c394041cf517b8b8449507bfc157a354e51d2a3f41484adc57d021596d49` | **MATCH** |
| MEM 分块 | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_FULL_FACTOR_MEM_ESTIMATE_CHUNK_20261025_ZH.md` | `103717df1f9e5d63f8c681f16da091f44801e1b69b219ae1a18b2159446145d1` | **MATCH** |
| r6 FROZEN 戳 | `docs/v2/AI_LEAF25_FULL_FACTOR_PREREG_r6_FROZEN_20261025_ZH.md` | `4bb1ff2b805f441499607ada5f871044e72e6176a66052c73b64816130d199e2` | **MATCH** |
| wrapper v5 | `docs/v2/audit/cmc_v1_1_leaf24/cmc_wrapper_v5_4240ce82.sh` | `4240ce82f0929085ab4bcb37e2400a3414e70e162c9e697cf02d97103342f882` | **MATCH** |
| X2.cmd 草案（参考） | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_FULL_FACTOR_X2_CMD_DRAFT_20261025_ZH.md` | `035e5818954e0f08798a860ad870312f278784b0291bcc424e602f8cf1be1c78` | **MATCH** |

## 2. 交付物 sha256（全长；落盘后钉）

| 件 | 路径 | sha256 |
|---|---|---|
| chunk_plan | `research/leaf25_full_factor_chunk_plan_r1.py` | `e858b32d314b9161a366ffef6661605943061162d707f7b86d01439d35dcdb12` |
| mem_probe | `research/leaf25_full_factor_mem_probe_r1.py` | `a0071e627d37f7e2498ea73984abb5b7ee4b1d2d0d27afdb85f8fc30986aed23` |
| build stub（可选最小） | `research/leaf25_cfacc_desens_build_r1.py` | `45537fb9294202f10293b8c0c7b57d9ebf95b835f8af23e3ef63a6dc25c47ee3` |
| 本封面 | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_MEM_PROBE_IMPL_COVER_20261025_ZH.md` | 以盘 `sha256sum` 为准 |
| probe cmd 草案 | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_MEM_PROBE_CMD_DRAFT_20261025_ZH.md` | `c8a853c5e3d76227e0fb34ead0ba99c956c0d9938b620fcea6738f425590ca03` |
| unified DIFF | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_MEM_PROBE_R1_20261025.diff` | `25bc47bd5ae2040642e5a50ad1ca7715387cdd2a7ad4cf54dcf456856df51f1a` |

## 3. 与 Arch §3 对齐（探针最小要求 → 本包）

| Arch §3 要求 | 本包落实 |
|---|---|
| 独立小 `.ok`（禁与密封/X2 同张；禁复用 `1c32ab1e…`） | **未申**；cmd 草案占位 `<ARCH_PROBE_OK>`；代码硬禁复用 `1c32ab1e5ffb9eb3ddf466f15b0cd778a1579eaca678f2f5fbe1dd1ae00e66f0` |
| wrapper v5 `4240ce82…`；C4/stop/hard **1331200/1484800/1536000**；禁抬帽 | cmd 草案钉 v5；脚本默认三帽；上调则 `STOP` |
| 采样仅 `/tmp` | `--sample-dir` 强制 `/tmp/quantlab_*`；wrapper 默认 `/tmp/quantlab_wrapper_sampler/` |
| 至少一块拟生产粒度；宇宙优先 HI_LIQ | 默认 `--mode month`（≈1 自然月）或 rebal×20；`--universe HI_LIQ` |
| 走「读 PIT→截面 α→落盘分区→gc」主峰路径结构 | dry-run 模拟该结构；真实路径 **显式门闩**（`--allow-real-data` + `.ok`，且 r1 仍 NotImplemented 防 densify） |
| 通过线 peak≤0.85×C4（≤1131520）否则再拆不抬帽 | `check_rss`：≥split→exit 94；≥hard→exit 95 |
| 回执披露 peak/块边界/N 等 | `run_meta.json` + `chunk_plan_used.json` |

## 4. 禁项（本回合与后续开跑前）

- **禁**申 X2 实跑 `.ok`；**禁**本回合申 probe `.ok`（交 Arch 静态审实现包）
- **禁**复用 step_m1 `.ok` `1c32ab1e5ffb9eb3ddf466f15b0cd778a1579eaca678f2f5fbe1dd1ae00e66f0`
- **禁**抬 C4/stop/hard；破帽/破 0.85×C4 → 拆块，不自抬帽重试
- **禁**整窗 densify；**禁** `--window both`
- **禁**采样写入 `output*` / `data*`
- **禁**本回合读真实行情/财务大表；默认 `--dry-run` / `--synthetic-calendar`
- **禁** git commit；DIFF 交 Arch 审
- **禁**在 research 落 `__pycache__`（`py_compile`→`/tmp`）

## 5. 静态检查

| 检查 | 结果 |
|---|---|
| `py_compile` → `/tmp/leaf25_chunk_plan_r1.pyc` | **PASS** |
| `py_compile` → `/tmp/leaf25_mem_probe_r1.pyc` | **PASS** |
| `py_compile` → `/tmp/leaf25_cfacc_build_r1.pyc` | **PASS** |
| pyflakes（`/tmp/ql_pyflakes_venv`）三脚本 | **PASS**（rc=0） |
| research `__pycache__` 新增 leaf25_full_factor* / leaf25_cfacc* | **无** |
| dry-run 烟测（synthetic cal，`/tmp/quantlab_*` out） | **PASS**（未读财务/行情大表） |

## 6. 给 Arch / 主的下一跳

1. **Arch**：静态审本实现包（脚本 sha + 本封面 + cmd 草案 + DIFF）；通过后**另签独立 probe `.ok`**（钉 wrapper v5 / C4 三帽 / `/tmp` / 单块 HI_LIQ / 禁 `1c32ab1e` / `ai_no_retry`）。**本包不等于授权开跑。**
2. **主**：叶27 让出后排 **mem_probe 短窗**；勿占用拟 X2 14:30–16:00 全段除非探针极短。
3. **AI**：等 probe `.ok` + 入窗后再跑真实峰路径；**勿**申 X2 `.ok`；探针 PASS 后由 Arch 用实测峰硬钉 X2 内存键。

live=false；promotion_approved=false。
