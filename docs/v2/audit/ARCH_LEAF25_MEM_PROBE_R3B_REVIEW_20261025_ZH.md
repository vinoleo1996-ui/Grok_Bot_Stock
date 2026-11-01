# Arch 审阅：叶25 mem_probe **r3b**（PIN wrapper 启动侧 · 探针 UNCHANGED）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审） |
| 时刻 | `2026-10-25T13:19:08-04:00`（America/New_York） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 本回合动作 | **只审不签** `.ok`；**不挂 QUIET**；**不代跑**真实行情/财务大表；≠解阻 X2 |
| live / promotion_approved | **false** / **false** |
| 对照 VOID 裁定 | `docs/v2/audit/ARCH_LEAF25_MEM_PROBE_R3_FAIL_C5_VOID_RULE_20261025_ZH.md` sha **`43fe482e462bb6e3f3c64c687f8dcda9693cbb7849d67593f23f9653f780b0ce`**（sha8 **`43fe482e`**） |
| 对照 r3 滤子修审 | `docs/v2/audit/ARCH_LEAF25_MEM_PROBE_R3_FILTER_FIX_REVIEW_20261025_ZH.md` sha **`63500a9f34015264eff43eec41e1f9af5ed8b2a86d7a1a1a74e2bc2d8c47018d`**（sha8 **`63500a9f`**） |
| 对照 C5 审阅 | `docs/v2/audit/ARCH_CMC_WRAPPER_V6_C5TIGHTEN_REVIEW_20261025_ZH.md` sha **`74149e2995fde6ee04b9ce812b0a938a6749f006294eac76feb0356469b4812a`**（sha8 **`74149e29`**） |
| 对照 Arch PIN 文 | `docs/v2/audit/ARCH_CMC_WRAPPER_V6_C5TIGHTEN_PIN_20261025_ZH.md` sha **`340ab36c357c2335fde4c9446038daec19fcc83bd96b800906367be2bb1f3617`**（sha8 **`340ab36c`**） |
| Arch wrapper PIN | `docs/v2/audit/cmc_wrapper_c5_tighten_20261025/cmc_wrapper_v6_C5TIGHTEN_b1208d3c.sh` sha **`b1208d3c075b0ea06ba9a484d8a42833f3efb223defbada02d135dfe624f88d5`** |
| 拟 `.ok` 名 | `output/ai_factory/ARCH_RUN_AUTH_LEAF25_MEM_PROBE_R3B.ok`（**另回合**签发；本回合不写） |

## 0. 一句话

r3b 包相对 r3 **唯一实质变更**为启动 wrapper：v5 `4240ce82` → Arch **已 PIN** 的 v6 C5TIGHTEN **`b1208d3c…`**（路径必须 `…_b1208d3c.sh`）。探针 `research/leaf25_full_factor_mem_probe_r3.py` **UNCHANGED** `8da4f2e6…`（滤子修后真实峰路径 PIT→α→落盘→gc 仍在）。帽未抬；`allow_c5_ignore=false`；实跑 cmd 块无 `--c5-ignore`；禁复用 VOID 旧票；≠X2；live=false。**静态足以供另回合另签**独立实峰 probe `.ok`；签窗建议 **≥15:00 ET**（错开叶27 **14:00–14:45**），expires+2min；**签时再挂 QUIET，现不挂**。

## 1. 结论枚举

| 字段 | 值 |
|---|---|
| **裁定** | **PASS_WITH_CONDITIONS** |
| 包完整性（四件 sha） | **MATCH** 宣称 |
| 启动钉 PIN wrapper | **PASS**（路径+sha；禁 `.draft.sh` / `e03a61b6`） |
| 探针 UNCHANGED | **PASS** `8da4f2e6…` |
| 帽 / `/tmp` / HI_LIQ 单块 | **PASS**（同 r3；禁抬） |
| `--c5-ignore` / `allow_c5_ignore` | **PASS**（实跑块无忽略旗；表钉 false） |
| VOID 旧票 / RESTORED | **PASS**（`c5e54085`/`cd230f9c`/`1c32ab1e` 仍在 `_consumed`；包内无 RESTORED） |
| ≠X2 / live=false | **PASS** |
| DIFF 性质 | **仅 CMD 文档**（r3 CMD→r3b CMD）；**无**探针 `.py` 变更 |
| `py_compile` 探针 | **PASS**（产物 `/tmp/leaf25_mem_probe_r3_py_compile_check.pyc`） |
| 本回合是否可签 `.ok` | **否**（任务禁签；且宜等 ≥15:00 ET 短窗） |
| 另回合是否可签 | **可**——满足 §6 条件后另签 |

## 2. 包指纹（盘核 · 全长）

| 件 | 路径 | 宣称 sha256 | 实测 | 结果 |
|---|---|---|---|---|
| COVER | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_MEM_PROBE_R3B_COVER_20261025_ZH.md` | `c5d0c4f0af18b3e23a9242717f3f68e9e31b2023c6940dcc98ed3eeda6cf5e8d` | 同左 | **MATCH** |
| CMD | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_MEM_PROBE_R3B_CMD_DRAFT_20261025_ZH.md` | `689dc55cee93b4cc767b5fe19ecd0e89cbb2182350ac5da7a2d5bf2ee6919770` | 同左 | **MATCH** |
| DIFF | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_MEM_PROBE_R3B_20261025.diff` | `e92796fe1b502f661eea5c9ac470005aaa184699d394b1f6ba375b35c3711fe7` | 同左 | **MATCH** |
| 交手回执 | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_MEM_PROBE_R3B_HAND_TO_ARCH_RECEIPT_20261025_ZH.md` | `9fab0ef416867abb80129a650bc136bb768cfab0153df511ac497488769d58bf`（AI 交审/盘） | 同左 | **MATCH** |
| Arch wrapper PIN | `…/cmc_wrapper_v6_C5TIGHTEN_b1208d3c.sh` | `b1208d3c075b0ea06ba9a484d8a42833f3efb223defbada02d135dfe624f88d5` | 同左 | **MATCH** |
| 探针 | `research/leaf25_full_factor_mem_probe_r3.py` | `8da4f2e663d83956b4b9910fc958f9decba68f40327f2089610ffa1a069600ea` | 同左 | **MATCH · UNCHANGED** |
| chunk_plan | `research/leaf25_full_factor_chunk_plan_r1.py` | `e858b32d314b9161a366ffef6661605943061162d707f7b86d01439d35dcdb12` | 同左 | **MATCH · UNCHANGED** |
| build stub | `research/leaf25_cfacc_desens_build_r1.py` | `45537fb9294202f10293b8c0c7b57d9ebf95b835f8af23e3ef63a6dc25c47ee3` | 同左 | **MATCH · UNCHANGED** |
| Eng DIFF / COVER / 回执 | `a3a228a9…` / `6339f298…` / `dabe75ec…` | 全长见 CMD §1 | 盘核同 | **MATCH** |
| 基线 v5（未覆盖） | `cmc_wrapper_v5_4240ce82.sh` | `4240ce82f0929085ab4bcb37e2400a3414e70e162c9e697cf02d97103342f882` | 同左 | **MATCH · 未改** |
| PIN 文 / C5 审阅 | `340ab36c…` / `74149e29…` | 全长见上表头 | 盘核同 | **MATCH** |
| VOID 裁定 / r3 FAIL 回执 | `43fe482e…` / `04552c3c…` | 全长见 CMD §1 | 盘核同 | **MATCH** |
| 滤子修审 | `63500a9f…` | 全长见上表头 | 盘核同 | **MATCH** |
| r3 CMD 基线 | `AI_LEAF25_MEM_PROBE_R3_CMD_DRAFT_…` | `440930e8ac2cc3ef61e2891cad1683271c8b6ceab10ebd92d4c0035b197b84f7` | 同左 | **MATCH** |

### 2.1 交手回执自指 sha（COND）

回执正文「本回执」栏写 `110f484f32a84e9ab6d3bf49a6b94623a5028ce199f6b7e88e64f05a02b31ce1`，与盘文件实测 **`9fab0ef4…` 不一致**（自指陈旧）。COVER 已写「交手回执以盘为准」。**不构成拒签**；另回合签发时以盘 `9fab0ef4…` 钉回执，勿信正文自指。

## 3. CMD 启动侧核（可执行块 · 去注释）

| 检查项 | 结果 | 证据 |
|---|---|---|
| wrapper 路径 | **PASS** | `bash docs/v2/audit/cmc_wrapper_c5_tighten_20261025/cmc_wrapper_v6_C5TIGHTEN_b1208d3c.sh` |
| wrapper sha 钉 | **PASS** | 全文钉 `b1208d3c075b0ea06ba9a484d8a42833f3efb223defbada02d135dfe624f88d5`；`bash -n` PIN → PASS |
| 禁 `.draft.sh` 启动 | **PASS** | 可执行 `bash` 行无 `.draft.sh`；draft 仅旁证（与 PIN **字节相同** `cmp` YES，仍禁作启动路径） |
| 禁 `e03a61b6` | **PASS** | 可执行块无；禁项明文；并行草案盘 sha `e03a61b6e706c0b4…` ≠ PIN |
| 探针路径/sha | **PASS** | `research/leaf25_full_factor_mem_probe_r3.py` + UNCHANGED `8da4f2e6…` |
| `--assert` | **PASS**（注） | `leaf25_full_factor_mem_probe_r3`（脚本未改名；tag=`leaf25_mem_probe_r3b`） |
| C4/STOP/HARD | **PASS** | `1331200` / `1484800` / `1536000`（可执行块与表一致；禁抬） |
| `allow_c5_ignore` | **PASS** | 表钉 **false**；可执行块未开 |
| `--c5-ignore` | **PASS** | **仅**禁项注释；可执行块 **无**该旗 |
| universe / mode | **PASS** | `--universe HI_LIQ` · `--mode month` · 例窗 2024-06-03→2024-06-28 · chunk0 |
| `--window both` | **PASS** | 可执行块无；禁项注释有 |
| logdir / outdir | **PASS** | `output/ai_factory/_leaf25_mem_probe_r3b/${ET_TS}` + `_logs` |
| sampler | **PASS** | `/tmp/quantlab_leaf25_mem_probe_r3b_${ET_TS}`（禁 output*/data*） |
| 禁 VOID 旧票 | **PASS** | 明文禁 `c5e54085`/`cd230f9c`/`1c32ab1e`；盘仍 `_consumed` VOID/CONSUMED |
| ≠X2 / live=false | **PASS** | 封面/CMD/回执一致 |
| 排窗 | **PASS** | 错开叶27 14:00–14:45；拟 ≥15:00 ET |

## 4. DIFF 扫阅

- 头：`--- a/…/AI_LEAF25_MEM_PROBE_R3_CMD_DRAFT_…` → `+++ b/…/AI_LEAF25_MEM_PROBE_R3B_CMD_DRAFT_…`
- **无** `research/*.py` 文件级变更；文内提及探针路径仅为 CMD 叙述。
- 相对 r3 CMD 的实质 diff：wrapper v5→PIN v6；out/log/sampler 目录名 r3→r3b；禁项补 `c5e54085`/`--c5-ignore`/`e03a61b6`/叶27 错开；拟 `.ok` 名 → `…_R3B.ok`。
- **无需**对探针做隔离 `patch` 重建（宣称 UNCHANGED 且盘 sha 已 MATCH `8da4f2e6…`）。

## 5. 探针真实峰路径（对照 `63500a9f`）

静态扫 `research/leaf25_full_factor_mem_probe_r3.py`（未改字节）：

| 环节 | 结果 |
|---|---|
| `real_peak_path` | **在** |
| PIT 加载 | `_read_pit_projected` / `stage("pit_*_loaded")` **在** |
| 滤子修 | `_end_date_filter_value` / `_norm_pit` **在**（r3 滤子修保留） |
| 截面 α | `stage("cs_alpha_done")` 等 **在** |
| 落盘 | parquet 写出路径 **在** |
| gc | `gc.collect` ×3 **在** |
| 帽检查 | `c4_kb`/`stop_kb`/`hard_kb`/`check_rss` **在** |
| `py_compile` | **PASS** → `/tmp/leaf25_mem_probe_r3_py_compile_check.pyc` |

未读真实行情、未实峰、未 `--allow-real-data` 执行。

## 6. 条件（另回合签发前必须满足）

1. **新票**：另签 `output/ai_factory/ARCH_RUN_AUTH_LEAF25_MEM_PROBE_R3B.ok`；**禁**复用/RESTORED `c5e54085`/`cd230f9c`/`1c32ab1e` 及任何 CONSUMED/VOID/X2 票。
2. **钉启动**：`.ok`/`.cmd` 必须钉 PIN 路径 `cmc_wrapper_v6_C5TIGHTEN_b1208d3c.sh` + sha `b1208d3c075b0ea06ba9a484d8a42833f3efb223defbada02d135dfe624f88d5`；**禁**启动 `.draft.sh`；**禁** `e03a61b6…`。
3. **钉载荷**：探针 `8da4f2e6…`；C4/STOP/HARD=`1331200/1484800/1536000`；`allow_c5_ignore=false`；实跑**禁** `--c5-ignore`；sampler **仅** `/tmp/quantlab_*`；HI_LIQ 单块；禁 `--window both`；禁本轮 FULLA。
4. **签窗**：建议 **≥15:00 ET**（America/New_York），短窗 **expires=+2min**；**错开叶27 14:00–14:45 ET**；**签时再挂 QUIET**（本审阅回合不挂）。
5. **回执钉盘**：交手回执以盘 sha `9fab0ef4…` 为准（忽略正文自指 `110f484f…`）。
6. **范围**：≠解阻 X2；live v5 `4240ce82` **不**替换为生产默认；本审阅 **不**授权开跑。

## 7. 禁项（重申）

- 禁自开跑 / 盲跑 `--allow-real-data`
- 禁抬帽；禁 `allow_c5_ignore=true`；禁实峰 `--c5-ignore`
- 禁复用 VOID/CONSUMED 旧票；禁 RESTORED
- 禁申 X2；禁抢叶27 14:00–14:45
- 禁混 AI 并行 wrapper `e03a61b6`；禁以 `.draft.sh` 作启动权威
- 禁 git commit / 覆盖生产 v5

## 8. 下一跳

1. **Arch 父/另回合**：≥15:00 ET（或叶27 窗后）按 §6 **另签** `ARCH_RUN_AUTH_LEAF25_MEM_PROBE_R3B.ok` + 短窗 QUIET。
2. **主**：排窗错开叶27。
3. **AI**：入窗持新 `.ok` 开跑；回执须披露 PIN wrapper sha、`peak_kb`、C5 无 false-positive rc=96（或 sampler `C5_SKIP`）；破 0.85×C4 → exit 94 拆块（禁抬帽）。

**本文件不是 `.ok`。** live=false。
