# Arch 审阅：叶33 A1 只读 `n_unlock_pool` 诊断探针票（只审不签不挂不代跑）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审 A1 诊断探针票） |
| 时刻 | `2026-10-27T08:11:44-04:00`（America/New_York；墙钟 `2026-10-27 08:11 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 对照 | 复议审 **`29166bf7`** · 复议 DRAFT **`b84496fe`** · VOID **`6826c01d`** · RUN **`a1b426f5`** · alpha **`ea17e173`** · overlap **`473b339e`** · meta **`f4702783`** · 正式脚本 **`afbbe7e7` UNCHANGED** · 诊断脚本 **`083d09fe`** · FROZEN **`8ed43721`** · PIN **`4e17ccfc`** · FROZEN审 **`bf5234a9`** |
| 本回合动作 | **只审**；**不签**任何 `.ok`；**不挂** QUIET；**不代跑**真数据；**不降** gate=`COVERAGE_MEDIAN_HILIQ=300`；**不钉** θ；**不改**正式脚本 `afbbe7e7`；禁 RESTORED `245df63f`+`c5ed13df`+`5774bb6e`+二十票；`0087c928`/叶28/29 另队；禁触 A18；**≠X2 ACCEPT**；live=false；**不报 Leo** |
| 触发 | 主 · Arch复议审 `29166bf7` → 路径 A1；AI 诊断票 DRAFT `6a22123d` / COVER `92262b70` / RECEIPT `0fb1942d` / 诊断脚本 `083d09fe` |
| Arch 推荐（讨论向） | **建议为探针另排新 `.ok` 签窗跑诊断**（钉 `083d09fe`；禁 RESTORED；rss=1500；peak_proof；禁改正式 `afbbe7e7`）；本拍**不**签、**不**钉 θ、**不**降 gate；**≠X2 ACCEPT** |

## 0. 一句话

A1 只读 `n_unlock_pool` 诊断探针票 **PASS_WITH_CONDITIONS**：DRAFT/COVER/RECEIPT/诊断脚本/正式脚本/上游复议钉 **MATCH**；dry-compile / dry-run **PASS**；无 ok 真跑门 **exit2**；EXECUTED=false；live `.ok`=0；QUIET ABSENT；`n_alpha` 旁证 median=**30.0**；`n_unlock_pool`/`ratio` **待另窗签后跑**；θ **未自决**；gate=300 **未改**；正式脚本 **`afbbe7e7` UNCHANGED**。**建议：是——另排新探针 `.ok` 签窗跑诊断**，得分布后再由主钉 θ / 是否另窗 FROZEN。本拍不签/不挂/不代跑/不降门/不钉 θ。

## 1. 钉表再核（本机 sha256）

| 件 | 路径 / 值 | 期望 sha8 | 实测全长 | 结果 |
|---|---|---|---|---|
| DRAFT | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_N_UNLOCK_POOL_DIAG_DRAFT_20261027_ZH.md` | `6a22123d` | `6a22123dae4a36b5bc21e25a9f92091ccc0d297c50842b46dc6cbcabc3a557be` | **MATCH** |
| COVER | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_N_UNLOCK_POOL_DIAG_COVER_20261027_ZH.md` | `92262b70` | `92262b709f5a9244618b8d0c5f73ec242432bdf94871db568ca2cf6e08d79607` | **MATCH** |
| RECEIPT（AI） | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_N_UNLOCK_POOL_DIAG_RECEIPT_20261027_ZH.md` | `0fb1942d` | `0fb1942d657f49df5d055952d8d86251a0a65b14232a42b33197fc12e5208dde` | **MATCH** · EXECUTED=false |
| 诊断脚本 | `research/leaf33_n_unlock_pool_diag_probe_v1.py` | `083d09fe` | `083d09feaf5cca609b8d18657685c8d42c0e75295af18532807ea7fb4ab6a746` | **MATCH** |
| 正式脚本 | `research/leaf33_share_unlock_pressure_resid_alpha_build.py` | `afbbe7e7` | `afbbe7e7292c17399bbf4733d9f34a922e6d81f1a914a60d24dc61fcba86cbc9` | **UNCHANGED** |
| Arch 复议审 | `docs/v2/audit/ARCH_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_COVERAGE_SPARSE_RECON_REVIEW_20261027_ZH.md` | `29166bf7` | `29166bf7ab27431b9240b0af5f1d182e52bffce21b65cc33bbf4ad2d8a89d4dc` | **MATCH** |
| 复议 DRAFT | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_COVERAGE_SPARSE_RECON_DRAFT_20261027_ZH.md` | `b84496fe` | （盘证前8=`b84496fe`） | **MATCH** |
| Arch VOID | `docs/v2/audit/ARCH_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_X2_VOID_ABORT_COVERAGE_GATE_20261027_ZH.md` | `6826c01d` | （盘证前8=`6826c01d`） | **MATCH** |
| RUN ABORT | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_X2_TZ_ALIGN_RUN_RECEIPT_20261027_ZH.md` | `a1b426f5` | （盘证前8=`a1b426f5`） | **MATCH** |
| alpha | `output/ai_factory/_leaf33_share_unlock/20261027_072135/alpha_HILIQ_x2_20261027_072552.parquet` | `ea17e173` | （盘证前8=`ea17e173`） | **MATCH** · 无新 alpha |
| overlap | `…/overlap_vs_leaf19_25_27_30_31_32_margin_delta_hk_hold_moneyflow.json` | `473b339e` | `473b339ec0c79d9c52400b2cbbf57059097cf288a6496ec733e2c0649765c76d` | **MATCH** |
| run_meta | `…/run_meta.json` | `f4702783` | （盘证前8=`f4702783`） | **MATCH** · coverage_median=**30.0** / gate=**300** / pass=false |
| live leaf33 `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF33*` / `*.ok` | 0 | 0 | **ABSENT** |
| live QUIET | `output/loop/RESEARCH_QUIET*leaf33*` | ABSENT | ABSENT | **ABSENT** |
| 诊断实跑 out | `output/ai_factory/_leaf33_share_unlock/diag_n_unlock_pool_v1/` | ABSENT | ABSENT | **ABSENT**（未真跑） |

交叉引用：DRAFT↔COVER↔RECEIPT 均钉诊断脚本 `083d09fe`、正式 `afbbe7e7`、复议审 `29166bf7`、VOID/`6826c01d`、RUN/`a1b426f5`、alpha/`ea17e173`；禁 RESTORED 三钉齐全；`n_unlock_pool`/`ratio` 均写明 **待签窗后跑**。

## 2. 必审清单（架构裁决）

| # | 审点 | 结果 | 证据 |
|---|---|---|---|
| 1 | DRAFT/COVER/RECEIPT 三件套一致、sha8 MATCH、交叉引用正确 | **PASS** | 三件全长 MATCH；互相钉齐脚本/上游/禁项；COVER 盘证路径指向 DRAFT/RECEIPT/diag |
| 2 | 诊断脚本 sha8=`083d09fe`；正式脚本仍 `afbbe7e7`（UNCHANGED） | **PASS** | 诊断全长 MATCH；正式全长=`afbbe7e7…`；dry 末行 `formal_script_sha8=afbbe7e7`；脚本内 `verify_formal_script_unchanged` + 禁 import 正式模块（静态无 `import/from leaf33_share_unlock…`） |
| 3 | 探针性质：只读 `n_unlock_pool`/ratio；不改正式 α；不降 gate；θ 未自决 | **PASS** | 度量钉 W=20 / rebal=20 / `naive_calendar_day` / 分母0→NaN；`COVERAGE_MEDIAN_HILIQ_READONLY=300`；`theta_undecided=true`；`gate_change_forbidden=true`；kind=`DIAGNOSTIC_PROBE_NOT_FORMAL_ALPHA` |
| 4 | dry-compile / dry-run PASS；无 ok 真跑门 exit2 | **PASS** | 本机 `py_compile` **PASS**；默认 `--dry-run` exit **0**（pins 齐）；`--allow-real-data` 无 `--arch-ok-path` → STOP exit **2**；`--no-dry-run` 无 allow → STOP exit **2**。**未**真跑数据加载重算 |
| 5 | EXECUTED=false；无新 alpha/overlap/run_meta；live `.ok`=0；QUIET ABSENT | **PASS** | AI RECEIPT 钉 + 本机盘证；`_leaf33_share_unlock/` 无新 diag out；live ok/quiet 计数 0 |
| 6 | `n_alpha` 旁证 median=30；`n_unlock_pool`/ratio 待另窗签后跑 | **PASS** | run_meta `f4702783`：n_rebal=30；median=**30.0**；min=15；max=72；gate=300；pass=false。票面明示 `n_unlock_pool`/`ratio` **待签窗后跑**（本拍未实测） |
| 7 | 与复议审 `29166bf7` CONDITIONS 对齐（A1 先诊断、不降门、θ∈0.5–0.8 须主钉、另窗 FROZEN/新脚本+新.ok） | **PASS** | 票面引用 Arch C3/C4；主路径 A1；本拍不落地副闸/不改 FROZEN；下一跳写明签窗→分布→主钉 θ→另窗 FROZEN |
| 8 | 禁 RESTORED 列表完整；无越权签挂跑 | **PASS** | 脚本 `FORBID_OK_SHA8` n=**23** 含 `245df63f`/`c5ed13df`/`5774bb6e`+二十；三件套禁止清单齐；本拍未签/未挂/未代跑；未触 A18；未夹带 `0087c928`/叶28/29 |

## 3. CONDITIONS（采纳后 / 探针签窗前）

1. **C1 本拍不落地**：不签 `.ok`；不挂 QUIET；不代跑；不降 gate=**300**；不钉 θ；正式脚本保持 **`afbbe7e7`**。PASS ≠ 可签 / 可真跑。
2. **C2 建议另排新探针 `.ok` 签窗（YES）**：若主要跑诊断，须发**新**诊断 `.ok`（建议名由主定，如 `ARCH_RUN_AUTH_LEAF33_N_UNLOCK_POOL_DIAG_v1.ok`）；钉诊断脚本 sha8 **`083d09fe`**（全长 `083d09feaf5cca609b8d18657685c8d42c0e75295af18532807ea7fb4ab6a746`）；CLI 须 `--allow-real-data` + `--arch-ok-path <NEW_DIAG_OK>`；**禁** RESTORED `245df63f`/`c5ed13df`/`5774bb6e`+二十票；**禁**改/覆盖正式脚本 `afbbe7e7`；rss=1500 禁抬；peak_proof REQUIRED（探针读 HI_LIQ+share_float 时须报峰）。
3. **C3 真跑范围仅诊断**：输出拟目录 `output/ai_factory/_leaf33_share_unlock/diag_n_unlock_pool_v1/`（或主钉 `/tmp/quantlab_*`）；算 `n_unlock_pool`/`n_alpha`/`ratio` 分布；**禁止**写「建议 θ=…通过」；**≠**正式 α 构建 / **≠**X2。
4. **C4 分布齐后再钉 θ**：θ∈0.5–0.8 **须主钉**（AI/Arch 不自决）；再决定是否另窗修订 FROZEN（稀疏副闸）→ 新正式脚本 + 新 X2 `.ok`（与本探针签窗**分离**）。
5. **C5 禁 RESTORED / 禁夹带**：禁复用 `245df63f`/`c5ed13df`/`5774bb6e`+票；`0087c928`/叶28/29 另队；禁触 A18；禁 `--force`。
6. **C6 本拍口径**：≠X2 ACCEPT；leo_notify=false；live=false；ok_requested=false（本审不代申）。

## 4. 禁项 / 本回合非动作

- **未签**任何 `.ok`（含探针新签 / RESTORED `245df63f`/`c5ed13df`/`5774bb6e`+票）
- **未挂** QUIET；live QUIET **ABSENT**
- **未** `--allow-real-data` 真跑诊断；**未**读 share_float/行情重算 `n_unlock_pool`
- **未改**正式脚本（仍 **`afbbe7e7`**）；**未改**诊断脚本字节（审后仍 **`083d09fe`**）
- **未改** `COVERAGE_MEDIAN_*` / `PRESSURE_MIN_VALID`；**未钉** θ
- **未改** FROZEN `8ed43721` / PIN `4e17ccfc` / AI DRAFT·COVER·RECEIPT
- **未**抬 rss；**未**触 A18；**未审/未夹带** `0087c928`/叶28/29
- **≠X2 ACCEPT** / ≠selfcheck / ≠Book-Smoke
- **未** SendToUser / **未**报 Leo（leo_notify=false）

## 5. 硬钉下一跳

```
A1 诊断票只审 PASS_WITH_CONDITIONS（本回执）
  → 请主：是否另排【新探针 .ok】签窗跑诊断（钉 083d09fe；禁 RESTORED；rss=1500；peak_proof；禁改 afbbe7e7）
      → Arch 建议 = YES
          → AI 持新 .ok 真跑探针 → 得 n_unlock_pool / ratio 分布
              → 主钉 θ（∈0.5–0.8）/ 是否另窗修订 FROZEN
                  → 若采纳稀疏副闸：新正式脚本 + 新 X2 .ok（≠本探针窗；≠X2 ACCEPT 本拍）
```

**本拍不签 / 不挂 / 不代跑 / 不降门 / 不钉 θ**。

## 6. 结论

| 项 | 值 |
|---|---|
| VERDICT | **PASS_WITH_CONDITIONS** |
| DRAFT / COVER / RECEIPT | **`6a22123d`** / **`92262b70`** / **`0fb1942d`** MATCH |
| 诊断脚本 / 正式脚本 | **`083d09fe`** / **`afbbe7e7` UNCHANGED** |
| 复议审 / 复议 DRAFT / VOID / RUN | **`29166bf7`** / **`b84496fe`** / **`6826c01d`** / **`a1b426f5`** MATCH |
| alpha / overlap / meta | **`ea17e173`** / **`473b339e`** / **`f4702783`** MATCH |
| dry-compile / dry-run / 无 ok 门 | **PASS** / **PASS** / **exit2** |
| n_alpha 旁证 | median **30.0**（15–72；n_rebal=30）；gate 300 pass=false |
| n_unlock_pool / ratio | **待另窗签后跑**（未实测） |
| θ / gate | **未钉** / **300 未改** |
| 是否建议新探针 `.ok` 签窗 | **YES** — 票面/脚本齐且只读；须新签后才能得分布再钉 θ |
| EXECUTED | **false** |
| live `.ok` / QUIET | **0** / **ABSENT** |
| live | **false** |
| ≠X2 ACCEPT | **true** |
| leo_notify | **false** |

## 7. 本回执钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/audit/ARCH_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_N_UNLOCK_POOL_DIAG_REVIEW_20261027_ZH.md` |
| VERDICT | **PASS_WITH_CONDITIONS** |
| 上游钉 | DRAFT/`6a22123d` · COVER/`92262b70` · RECEIPT/`0fb1942d` · diag/`083d09fe` · formal/`afbbe7e7` · 复议审/`29166bf7` · VOID/`6826c01d` · RUN/`a1b426f5` |

**EXECUTED=false** · **leo_notify=false** · **live=false** · **ok_requested=false** · **≠X2 ACCEPT**
