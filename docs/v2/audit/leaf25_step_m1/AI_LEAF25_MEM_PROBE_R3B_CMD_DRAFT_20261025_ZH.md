# 叶25 mem_probe r3b · 实峰 cmd 草案（未授权 · 未申 `.ok`）

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI |
| 起草/刷新 | `2026-10-25T13:11:30-0400`（America/New_York） |
| 状态 | **DRAFT**（**不是 `.ok`** · **未授权实跑** · **不替代 Arch 签发**） |
| live | **false** · promotion_approved **false** |
| 基线 r3 CMD | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_MEM_PROBE_R3_CMD_DRAFT_20261025_ZH.md` sha **`440930e8ac2cc3ef61e2891cad1683271c8b6ceab10ebd92d4c0035b197b84f7`** |
| Arch VOID 裁定 | `docs/v2/audit/ARCH_LEAF25_MEM_PROBE_R3_FAIL_C5_VOID_RULE_20261025_ZH.md` sha **`43fe482e462bb6e3f3c64c687f8dcda9693cbb7849d67593f23f9653f780b0ce`** |
| r3 FAIL 回执 | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_MEM_PROBE_R3_RUN_RECEIPT_20261025_ZH.md` sha **`04552c3c83e3f2084ddeab35b6075f665536fdf4dc22b8952f6de01790e3e5f2`** |
| Arch C5 审阅 | `docs/v2/audit/ARCH_CMC_WRAPPER_V6_C5TIGHTEN_REVIEW_20261025_ZH.md` sha **`74149e2995fde6ee04b9ce812b0a938a6749f006294eac76feb0356469b4812a`**（PASS_WITH_CONDITIONS · sha8 `74149e29`） |
| Arch PIN 文 | `docs/v2/audit/ARCH_CMC_WRAPPER_V6_C5TIGHTEN_PIN_20261025_ZH.md` sha **`340ab36c357c2335fde4c9446038daec19fcc83bd96b800906367be2bb1f3617`**（sha8 `340ab36c`） |
| **Arch wrapper PIN** | `docs/v2/audit/cmc_wrapper_c5_tighten_20261025/cmc_wrapper_v6_C5TIGHTEN_b1208d3c.sh` sha **`b1208d3c075b0ea06ba9a484d8a42833f3efb223defbada02d135dfe624f88d5`** |
| 本回合 | **未申 `.ok`** · **未** `--allow-real-data` · **未** 实峰 · 仅 DRAFT |

---

## 1. 钉表（全长）

| 件 | 路径 / 值 | sha256 |
|---|---|---|
| Arch VOID r3 C5 | `docs/v2/audit/ARCH_LEAF25_MEM_PROBE_R3_FAIL_C5_VOID_RULE_20261025_ZH.md` | `43fe482e462bb6e3f3c64c687f8dcda9693cbb7849d67593f23f9653f780b0ce` |
| r3 FAIL 回执 | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_MEM_PROBE_R3_RUN_RECEIPT_20261025_ZH.md` | `04552c3c83e3f2084ddeab35b6075f665536fdf4dc22b8952f6de01790e3e5f2` |
| r3 CMD 基线 | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_MEM_PROBE_R3_CMD_DRAFT_20261025_ZH.md` | `440930e8ac2cc3ef61e2891cad1683271c8b6ceab10ebd92d4c0035b197b84f7` |
| Arch C5 审阅 | `docs/v2/audit/ARCH_CMC_WRAPPER_V6_C5TIGHTEN_REVIEW_20261025_ZH.md` | `74149e2995fde6ee04b9ce812b0a938a6749f006294eac76feb0356469b4812a` |
| Arch PIN 文 | `docs/v2/audit/ARCH_CMC_WRAPPER_V6_C5TIGHTEN_PIN_20261025_ZH.md` | `340ab36c357c2335fde4c9446038daec19fcc83bd96b800906367be2bb1f3617` |
| **Arch wrapper PIN（启动必须）** | `docs/v2/audit/cmc_wrapper_c5_tighten_20261025/cmc_wrapper_v6_C5TIGHTEN_b1208d3c.sh` | **`b1208d3c075b0ea06ba9a484d8a42833f3efb223defbada02d135dfe624f88d5`** |
| Eng draft（同字节旁证；**非**启动路径） | `docs/v2/audit/cmc_wrapper_c5_tighten_20261025/cmc_wrapper_v6_C5TIGHTEN.draft.sh` | `b1208d3c075b0ea06ba9a484d8a42833f3efb223defbada02d135dfe624f88d5` |
| Eng DIFF | `docs/v2/audit/cmc_wrapper_c5_tighten_20261025/DIFF_cmc_wrapper_v5_to_v6_C5TIGHTEN.diff` | `a3a228a95bc76d2372f928c23da73e15dcaa25f0b7de58d421f3b2235c9aefac` |
| Eng COVER | `docs/v2/audit/cmc_wrapper_c5_tighten_20261025/COVER_cmc_wrapper_v6_C5TIGHTEN_ZH.md` | `6339f298e249b1aee97983f3859d22831a025bf34638ef9e73ff6167d5d7bd34` |
| Eng 回执 | `docs/v2/audit/cmc_wrapper_c5_tighten_20261025/ENG_C5_TIGHTEN_DIFF_RECEIPT_20261025_ZH.md` | `dabe75ec6c289bf12895b810c45bd897c916dbcd6161e77c21bb9137c9e72da9` |
| 基线 wrapper v5（**未覆盖**） | `docs/v2/audit/cmc_v1_1_leaf24/cmc_wrapper_v5_4240ce82.sh` | `4240ce82f0929085ab4bcb37e2400a3414e70e162c9e697cf02d97103342f882` |
| chunk_plan | `research/leaf25_full_factor_chunk_plan_r1.py` | `e858b32d314b9161a366ffef6661605943061162d707f7b86d01439d35dcdb12` (**UNCHANGED**) |
| **mem_probe r3 脚本** | `research/leaf25_full_factor_mem_probe_r3.py` | **`8da4f2e663d83956b4b9910fc958f9decba68f40327f2089610ffa1a069600ea`** (**UNCHANGED**) |
| build stub | `research/leaf25_cfacc_desens_build_r1.py` | `45537fb9294202f10293b8c0c7b57d9ebf95b835f8af23e3ef63a6dc25c47ee3` (**UNCHANGED**) |
| 禁复用 VOID r3 `.ok` | `_consumed/…VOID.FAIL_C5…` | **`c5e540855bc836b97b7395a53dd63a6d3c295860fdd11e72e77abd6cf3152011`** |
| 禁复用 r2 VOID `.ok` | `_consumed/…VOID.FAIL_TYPE…` | **`cd230f9c2aa9fc8de7fc538fb1f04ded8d9c20463f24b88b6c0f76950ec34279`** |
| 禁复用 step_m1 `.ok` | CONSUMED | **`1c32ab1e5ffb9eb3ddf466f15b0cd778a1579eaca678f2f5fbe1dd1ae00e66f0`** |
| 禁混 AI 并行草案 | `docs/v2/audit/leaf25_step_m1/cmc_wrapper_v6_c5_tighten_DRAFT.sh` | **`e03a61b6…` 禁作权威/启动** |
| 宇宙 | **HI_LIQ**（单块） | FULLA **非本轮** |
| 块粒度 | `--mode month` **或** `--mode rebal_days --max-rebaldays ≤20` | **禁** `--window both` |

---

## 2. 帽与采样（禁抬帽；同 r3）

| 项 | 值 |
|---|---|
| C4 | **1331200** kB |
| wrapper STOPKB | **1484800** kB |
| hard | **1536000** kB |
| 拆块阈值 | **1131520** kB（0.85×C4）；破则 exit 94，再拆，**不**抬帽 |
| 采样 | **仅** `/tmp/quantlab_*` |
| `allow_c5_ignore` | **false** |
| 破帽 | **ABORT**；`ai_no_retry` |

`.ok` / `.cmd` 若写成更高帽 → **Arch 应拒签**。  
**禁**实峰带 `--c5-ignore`（refuse-91；Arch/主令同禁）。

---

## 3. 拟 cmd（单块 HI_LIQ · **Arch PIN wrapper** · **未申 `.ok`**）

**相对 r3 唯一实质变更**：wrapper 路径从 v5 → **Arch PIN** `cmc_wrapper_v6_C5TIGHTEN_b1208d3c.sh`（钉 sha `b1208d3c…`；**路径名必须 PIN**，禁启动 `.draft.sh`，禁 `e03a61b6`）。探针脚本仍 `research/leaf25_full_factor_mem_probe_r3.py` `8da4f2e6…`（UNCHANGED）。

占位：
- `<ET_TS>=$(date +%Y%m%d_%H%M%S)`（开跑瞬间）
- `<ARCH_PROBE_OK>` = Arch **新**签发的 **独立实峰 probe** `.ok`（拟名 `output/ai_factory/ARCH_RUN_AUTH_LEAF25_MEM_PROBE_R3B.ok`）——**不得**填 `c5e54085…` / `cd230f9c…` / `1c32ab1e…` / 任何 CONSUMED/VOID / X2 `.ok`
- 拟短窗：主+Arch 另排；**错开叶27 14:00–14:45 ET**（建议 ≥15:00 ET 或叶27 后）

```bash
# DRAFT — 未授权；须新实峰 probe .ok 且主排短窗内才可执行
# 本文件不是 .ok；禁复用 c5e54085 / cd230f9c / 1c32ab1e；禁抬帽；采样仅 /tmp；禁本回合申签
# 禁 --c5-ignore 实峰；禁 --window both；FULLA 非本轮；禁自开跑；≠X2
# wrapper 必须 Arch PIN 路径（禁 .draft.sh 启动；禁 e03a61b6）
cd /workspace/QuantLab && \
ET_TS=$(date +%Y%m%d_%H%M%S) && \
OUT=output/ai_factory/_leaf25_mem_probe_r3b/${ET_TS} && \
LOGDIR=${OUT}_logs && \
SAMPDIR=/tmp/quantlab_leaf25_mem_probe_r3b_${ET_TS} && \
mkdir -p "$OUT" "$LOGDIR" "$SAMPDIR" && \
# 预检：pgrep 空 + 新实峰 probe .ok 钉 Arch PIN wrapper/C4/HI_LIQ/单块 + 时刻∈主排短窗（错开叶27 14:00–14:45）后，再：
bash docs/v2/audit/cmc_wrapper_c5_tighten_20261025/cmc_wrapper_v6_C5TIGHTEN_b1208d3c.sh \
  --arch-ok <ARCH_PROBE_OK> \
  --assert leaf25_full_factor_mem_probe_r3 \
  --tag leaf25_mem_probe_r3b \
  --logdir "$LOGDIR" \
  --outdir "$OUT" \
  --sampler-dir "$SAMPDIR" \
  --meta "$OUT/run_meta.json" \
  --cwd /workspace/QuantLab -- \
  timeout 900 env PYTHONDONTWRITEBYTECODE=1 \
  /workspace/qlvenv/bin/python research/leaf25_full_factor_mem_probe_r3.py \
    --allow-real-data \
    --arch-ok-path <ARCH_PROBE_OK> \
    --universe HI_LIQ \
    --mode month \
    --start 2024-06-03 \
    --end 2024-06-28 \
    --chunk-id 0 \
    --sample-dir "$SAMPDIR" \
    --c4-kb 1331200 --stop-kb 1484800 --hard-kb 1536000 \
    --out "$OUT/"
```

**一行摘要（开跑核；待 `.ok`）**：

```text
bash docs/v2/audit/cmc_wrapper_c5_tighten_20261025/cmc_wrapper_v6_C5TIGHTEN_b1208d3c.sh … -- /workspace/qlvenv/bin/python research/leaf25_full_factor_mem_probe_r3.py --allow-real-data --universe HI_LIQ --mode month
```

| 路径类 | 约定 |
|---|---|
| out_dir | `output/ai_factory/_leaf25_mem_probe_r3b/<ET_TS>/` |
| log | `…/<ET_TS>_logs/` |
| **sampler** | `/tmp/quantlab_leaf25_mem_probe_r3b_<ET_TS>/`（禁 `output*`/`data*`） |
| **wrapper** | **Arch PIN** `cmc_wrapper_v6_C5TIGHTEN_b1208d3c.sh` sha `b1208d3c…`（live v5 `4240ce82` **未替换**） |
| part | `alpha_parts/chunk_XXXX.parquet`（float32；densify=false） |
| 单块窗（example） | 2024-06-03→2024-06-28 · chunk0 |

**明确禁止**：
- 启动路径用 `.draft.sh` 或 AI 并行 `e03a61b6…`
- 复用 `c5e54085…` / `cd230f9c…` / `1c32ab1e…` / X2 `.ok`
- 抬 C4/stop/hard；`allow_c5_ignore=true`；实峰 `--c5-ignore`
- `--window both`；本轮 FULLA；无 `.ok` 盲跑
- 自开跑 / 申 X2.ok / 覆盖生产 v5 / 抢叶27 **14:00–14:45 ET**

## 4. 回执须披露（开跑后）

- `dry_run=false` / `float32=true` / `densify=false` / `claims_full_cfacc=false`
- `peak_kb`、块边界、`n_days`/`n_names`、HI_LIQ mask sha
- RSS 各 stage；若 ≥0.85×C4 → exit 94 拆块（禁抬帽重试）
- C5：期望无 false-positive rc=96；sampler 可含 `C5_SKIP`；**禁**靠 `--c5-ignore` 过关
- wrapper **PIN 路径**与 sha（`b1208d3c…`）

## 5. 下一跳

Arch 审 r3b 包（COVER+本 CMD+DIFF；依赖 Eng C5 + Arch PIN `340ab36c` / 审阅 `74149e29`）→ **另签**实峰 probe `.ok`（拟名 `ARCH_RUN_AUTH_LEAF25_MEM_PROBE_R3B.ok`）→ 主排窗（错开叶27）→ AI 入窗开跑。  
**本文件不是 `.ok`。** live=false。
