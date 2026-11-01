# Arch 审阅：叶25 mem_probe r2 真实峰路径包

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审） |
| 时刻 | `2026-10-25T12:18:42-04:00`（America/New_York；墙钟 `2026-10-25 12:18 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 本回合动作 | **不签**任何 `.ok`；**不实跑**真实行情/财务大表；不解阻 X2 / NEED_MEM_PROBE |
| live / promotion_approved | **false** / **false** |
| 对齐主裁定 (A) | `docs/v2/audit/ARCH_LEAF25_MEM_PROBE_ADOPT_A_REJECT_REAL_PEAK_20261025_ZH.md` sha `14e9b6ba161057fe73015decf789041eef2a1e910e0ef656c16dcb85d78bce4e` |
| 相对 r1 | 勿复用 r1 执行器审 `0c7709299abae048968b82c06cf4a1ecb26a7a1c1c7228428398caf96dea013a` 的「dry 可签」结论；本审针对 **r2 实峰** |

## 0. 一句话

r2 已**填实** `real_peak_path`（列投影 PIT→HI_LIQ 截面粗应计 zscore→float32 part→gc），门闩/C4 三帽/禁复用 `1c32ab1e…`/无.ok→STOP 静态与烟测均过；**足以供父另签独立实峰 probe `.ok`**（非 X2、非密封同张），但须按下节硬钉。**本回合执行器不签**；实峰 probe 跑 PASS 前 **不解阻 X2**。

## 1. 输入 sha256 再核（全长 · 本机 `sha256sum`）

| 件 | 路径 | 期望 | 实测 | 结果 |
|---|---|---|---|---|
| mem_probe r2 | `research/leaf25_full_factor_mem_probe_r2.py` | `9dfe173a9104330287f6ebfe2f758c63891f3c92b5f9d112118b697898d50e0f` | 同左 | **MATCH** |
| chunk_plan | `research/leaf25_full_factor_chunk_plan_r1.py` | `e858b32d314b9161a366ffef6661605943061162d707f7b86d01439d35dcdb12` | 同左 | **MATCH · UNCHANGED** |
| build stub | `research/leaf25_cfacc_desens_build_r1.py` | `45537fb9294202f10293b8c0c7b57d9ebf95b835f8af23e3ef63a6dc25c47ee3` | 同左 | **MATCH · UNCHANGED** |
| COVER | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_MEM_PROBE_R2_REAL_PATH_COVER_20261025_ZH.md` | `4fa12c5a9876c2541bd062858a4e7464fea6e69650a75d53aade3d7342d5c92b` | 同左 | **MATCH** |
| CMD | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_MEM_PROBE_R2_CMD_DRAFT_20261025_ZH.md` | `837078627aab3b93190607609ca3620c8b1d5decdabc62a866f53371836df74a` | 同左 | **MATCH** |
| DIFF | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_MEM_PROBE_R2_20261025.diff` | `e0d9acdb973d80647fccd89aec8b27e59c2c1fd441a25aa87680a82629e1c6a8` | 同左 | **MATCH** |
| wrapper v5 | `docs/v2/audit/cmc_v1_1_leaf24/cmc_wrapper_v5_4240ce82.sh` | `4240ce82f0929085ab4bcb37e2400a3414e70e162c9e697cf02d97103342f882` | 同左 | **MATCH** |
| 主 (A) 裁定 | `docs/v2/audit/ARCH_LEAF25_MEM_PROBE_ADOPT_A_REJECT_REAL_PEAK_20261025_ZH.md` | `14e9b6ba161057fe73015decf789041eef2a1e910e0ef656c16dcb85d78bce4e` | 同左 | **MATCH** |
| NEED_MEM_PROBE | `docs/v2/audit/ARCH_LEAF25_MEM_CHUNK_REVIEW_20261025_ZH.md` | `f389c394041cf517b8b8449507bfc157a354e51d2a3f41484adc57d021596d49` | 同左 | **MATCH** |

## 2. 必检要点对照

| # | 要点 | 结果 | 证据摘要 |
|---|---|---|---|
| 1 | `real_peak_path` 已填实（无 NotImplemented / 空 stub） | **PASS** | AST 无 `NotImplemented`/`NotImplementedError`；函数可调用，源约 132 行；路径=列投影 PIT（KEY1+VAL）→HI_LIQ 成员→按日 asof 粗应计 `(NI-OCF)/TA` CS zscore→`float32` parquet part→`del`+`gc`；`densify=False`；`claims_full_cfacc=false`；`alpha_kind=crude_accrual_cs_zscore_probe_only` |
| 2 | 门闩：默认 dry；`--allow-real-data`+现存 `--arch-ok-path`；无.ok→STOP；禁 `1c32ab1e…`；C4 三帽；0.85×C4=1131520→94；hard→95；采样 `/tmp/quantlab_*` | **PASS** | 常量 `C4/STOP/HARD=1331200/1484800/1536000`，`SPLIT=1131520`；上调帽 STOP rc=2；无.ok STOP rc=2；`--no-dry-run` 无 allow STOP rc=2；`BANNED_OK_SHA` 比对；`assert_tmp_quantlab`；CLI 非法 sample-dir STOP |
| 3 | 宇宙/块：HI_LIQ；month 或 rebal≤20；禁 both；FULLA 非本窗优先 | **PASS_WITH_CONDITIONS** | 无 `--window` 参数（禁 both 成立）；实路径对 `FULLA` **STOP**；默认 `--universe HI_LIQ`、`--mode month`、`--max-rebaldays 20`。**缺口**：脚本**未**硬钉 `max_rebaldays≤20`（CLI 可传入更大值）；FULLA 仍在 choices（dry 可过）。须在 `.ok`/CMD 硬钉 |
| 4 | `py_compile`/`pyflakes`→`/tmp`；DIFF `patch -p0` 隔离重建 sha MATCH | **PASS**（pyflakes 环境例外见下） | `py_compile`→`/tmp/leaf25_mem_probe_r2.pyc` 等 PASS；DIFF 隔离重建脚本 sha **`9dfe173a…` MATCH**（原始 DIFF 含重复 `+++` 行，GNU patch 仍成功；属文档瑕疵非内容错）。本环境 `qlvenv` **无** `pyflakes` 模块，未能复跑 AI 声称的 pyflakes；以 AST 顶层 unused-import 检查替代 → **空/PASS** |
| 5 | dry 烟测（synthetic，`/tmp`）；禁止无 Arch `.ok` 真读大表 | **PASS** | dry HI_LIQ month 2024-06、`--synthetic-calendar`、`--sample-dir /tmp/quantlab_*` → rc=0，`dry_run=true`，`densify=false`；本审**未**开 `--allow-real-data` 读大表。schema 只读确认 PIT 三表与 HI_LIQ mask 列齐备（非 densify 全窗） |
| 6 | 是否足以让父签**独立实峰 probe `.ok`** | **是（附硬钉）** | 见 §4–§5；**非** X2 / **非**密封同张；签后仍须主排短窗 + AI 入窗实跑 PASS 才解阻内存键 |
| 7 | 本回合不签；不解阻 X2 直至实峰 probe 跑 PASS | **确认** | 执行器本文件**不**签发 `.ok`；NEED_MEM_PROBE 状态不变 |

## 3. 静态/烟测明细

| 检查 | 结果 |
|---|---|
| sha 全件 MATCH | **PASS** |
| AST 无 NotImplemented | **PASS** |
| `real_peak_path` callable + 非空实现 | **PASS** |
| `py_compile` → `/tmp`（r2 / chunk_plan / stub） | **PASS** |
| pyflakes（本机复跑） | **SKIP**（`qlvenv` 无模块）；AST unused-import **PASS** |
| DIFF `patch -p0` 隔离重建 | **PASS** sha `9dfe173a9104330287f6ebfe2f758c63891f3c92b5f9d112118b697898d50e0f` |
| dry 烟测 synthetic HI_LIQ month | **PASS** rc=0 |
| `--allow-real-data` 无 `--arch-ok-path` | **PASS** STOP rc=2 |
| `--c4-kb` 上调 | **PASS** STOP rc=2 |
| `--sample-dir` 非 `/tmp/quantlab_*` | **PASS** STOP |
| `--no-dry-run` 无 `--allow-real-data` | **PASS** STOP rc=2 |
| PIT/mask 列投影 schema 存在 | **PASS**（income/cashflow/balance KEY1+VAL 无缺列；mask 含 `date`/`instrument`/`in_universe`） |
| 本回合真读大表 / densify 全窗 | **未做（禁）** |

## 4. 条件与瑕疵（不阻断另签，但必须钉进 `.ok`/开跑前）

1. **硬钉块粒度**：`.ok`/CMD 明文 `--mode month` **或** `--mode rebal_days --max-rebaldays ≤20`；单 `chunk-id`；**禁**把 `max_rebaldays` 抬过 20（脚本未码级拦截）。
2. **硬钉宇宙**：仅 `--universe HI_LIQ`；本窗 **禁 FULLA**（尽管 CLI choices 仍含 FULLA，实路径会 STOP，仍勿在授权里放开）。
3. **硬钉帽与采样**：C4/stop/hard **1331200/1484800/1536000**；阈 **1131520** exit 94；hard exit 95；**禁抬帽**；采样/sampler **仅** `/tmp/quantlab_*`；`allow_c5_ignore=false`；破帽 **ABORT + ai_no_retry**。
4. **硬钉门闩与禁复用**：须现存独立实峰 probe `.ok` + `--allow-real-data`；**禁**复用 `1c32ab1e5ffb9eb3ddf466f15b0cd778a1579eaca678f2f5fbe1dd1ae00e66f0`；**禁** r1 dry `.ok`；**禁** X2 / 密封同张 `.ok`。
5. **硬钉包装**：wrapper v5 sha `4240ce82f0929085ab4bcb37e2400a3414e70e162c9e697cf02d97103342f882`；脚本 sha `9dfe173a9104330287f6ebfe2f758c63891f3c92b5f9d112118b697898d50e0f`；chunk_plan / stub UNCHANGED 如上。
6. **口径披露**：回执必须带 `dry_run=false` / `float32=true` / `densify=false` / `claims_full_cfacc=false` / `alpha_kind=crude_accrual_cs_zscore_probe_only`；**勿**把本探针当成全叶 CFACC 完成。
7. **卫生**：盘上存在 `research/__pycache__/leaf25_full_factor_mem_probe_r2.cpython-313.pyc`（COVER 称无）——开跑前删除；DIFF 头重复 `+++` 行可后续清洗（不影响重建 MATCH）。
8. **文档漂移**：脚本模块 docstring 仍写「r1 … Arch PASS_WITH_CONDITIONS dry .ok」，与主 (A)/`14e9b6ba…` **拒签 dry** 不一致——不影响运行，签 `.ok` 时勿引用该句。
9. **性能观察（非 FAIL）**：`_asof_value` 按日×码过滤，HI_LIQ 单月可接受；CMD 草案 `timeout 900` 合理。若逼近超时优先缩块，**禁**抬帽。

## 5. 签前硬钉键（供父签发独立实峰 probe `.ok` 时抄入）

```text
assert: leaf25_full_factor_mem_probe_r2
script_sha: 9dfe173a9104330287f6ebfe2f758c63891f3c92b5f9d112118b697898d50e0f
chunk_plan_sha: e858b32d314b9161a366ffef6661605943061162d707f7b86d01439d35dcdb12
stub_sha: 45537fb9294202f10293b8c0c7b57d9ebf95b835f8af23e3ef63a6dc25c47ee3
wrapper_v5_sha: 4240ce82f0929085ab4bcb37e2400a3414e70e162c9e697cf02d97103342f882
universe: HI_LIQ
mode: month | rebal_days&max_rebaldays<=20
chunk: single (explicit --chunk-id)
window_both: FORBIDDEN
FULLA: FORBIDDEN_THIS_WINDOW
c4_kb/stop_kb/hard_kb: 1331200/1484800/1536000
split_thresh_kb: 1131520 (exit 94); hard exit 95
raise_cap: FORBIDDEN
sample_dir: /tmp/quantlab_* only
banned_ok: 1c32ab1e5ffb9eb3ddf466f15b0cd778a1579eaca678f2f5fbe1dd1ae00e66f0
allow_real_data: requires THIS ok path present
not_x2: true
not_seal_same_ticket: true
claims_full_cfacc: false
densify: false
ai_no_retry: true
live: false
promotion_approved: false
unblocks_X2: ONLY_AFTER_real_peak_probe_run_PASS
```

## 6. 结论枚举

| 字段 | 值 |
|---|---|
| **结论** | **PASS_WITH_CONDITIONS** |
| 本回合是否签 `.ok` | **否** |
| 父可否另签独立实峰 probe `.ok` | **可**（须纳入 §5 硬钉；主另排短窗） |
| 是否解阻 X2 / NEED_MEM_PROBE | **否**（直至实峰 probe **入窗实跑 PASS** 并回执过 Arch） |
| 阻断项（挡另签） | **无** |
| 条件项（钉进 `.ok`，不挡结论） | §4.1–§4.8 |

## 7. 明确禁项（再申）

- 本审阅**不是** `.ok`，**不授权** `--allow-real-data` 开跑。
- **禁**把本包当 X2 实跑授权；**禁**密封同张混签。
- **禁**复用 r1 dry 可签叙事；**禁**复用 `1c32ab1e…`。
- **禁**抬 C4/stop/hard；**禁** `--window both`；**禁**本窗 FULLA；**禁**整窗 densify。
- **禁**采样写入 `output*` / `data*`。

live=false；promotion_approved=false。
