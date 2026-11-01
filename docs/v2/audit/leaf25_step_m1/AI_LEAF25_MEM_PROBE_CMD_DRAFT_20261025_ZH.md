# 叶25 mem_probe · cmd 草案（未授权 · 未申 `.ok`）

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI（执行器） |
| 起草 | `2026-10-25T11:57:36-0400`（America/New_York；墙钟 `2026-10-25 11:57:36 ET`） |
| 状态 | **DRAFT**（**不是 `.ok`** · **未授权实跑** · **不替代 Arch 签发**） |
| live | **false** · promotion_approved **false** |
| 对齐 | Arch **NEED_MEM_PROBE** `f389c394041cf517b8b8449507bfc157a354e51d2a3f41484adc57d021596d49`；封面同批 |
| 本回合 | **未申 `.ok`** · **未读真实行情/财务大表** · 仅静态/dry 结构 |

---

## 1. 钉表（全长）

| 件 | 路径 / 值 | sha256 |
|---|---|---|
| Arch 审 | `docs/v2/audit/ARCH_LEAF25_MEM_CHUNK_REVIEW_20261025_ZH.md` | `f389c394041cf517b8b8449507bfc157a354e51d2a3f41484adc57d021596d49` |
| MEM | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_FULL_FACTOR_MEM_ESTIMATE_CHUNK_20261025_ZH.md` | `103717df1f9e5d63f8c681f16da091f44801e1b69b219ae1a18b2159446145d1` |
| r6 FROZEN 戳 | `docs/v2/AI_LEAF25_FULL_FACTOR_PREREG_r6_FROZEN_20261025_ZH.md` | `4bb1ff2b805f441499607ada5f871044e72e6176a66052c73b64816130d199e2` |
| **wrapper v5** | `docs/v2/audit/cmc_v1_1_leaf24/cmc_wrapper_v5_4240ce82.sh` | **`4240ce82f0929085ab4bcb37e2400a3414e70e162c9e697cf02d97103342f882`** |
| chunk_plan | `research/leaf25_full_factor_chunk_plan_r1.py` | `e858b32d314b9161a366ffef6661605943061162d707f7b86d01439d35dcdb12` |
| **mem_probe** | `research/leaf25_full_factor_mem_probe_r1.py` | **`a0071e627d37f7e2498ea73984abb5b7ee4b1d2d0d27afdb85f8fc30986aed23`** |
| 禁复用 step_m1 `.ok` | CONSUMED | **`1c32ab1e5ffb9eb3ddf466f15b0cd778a1579eaca678f2f5fbe1dd1ae00e66f0`** |
| 宇宙 | **HI_LIQ**（单块） | FULLA 后置 |
| 块粒度 | 默认 `--mode month`（≈1 自然月）或 `--mode rebal_days --max-rebaldays 20` | 对齐 Arch §3 / MEM P0 |

---

## 2. 帽与采样（禁抬帽）

| 项 | 值 |
|---|---|
| C4 | **1331200** kB |
| wrapper STOPKB | **1484800** kB |
| hard | **1536000** kB |
| 拆块阈值 | **1131520** kB（0.85×C4）；破则 exit 94，再拆，**不**抬帽 |
| 采样 | **仅** `/tmp/quantlab_*`（wrapper 默认 `/tmp/quantlab_wrapper_sampler/`；并行监控亦须 `/tmp`） |
| 破帽 | **ABORT**；`ai_no_retry` |

`.ok` / `.cmd` 若写成更高帽 → **Arch 应拒签**。

---

## 3. 拟 cmd（单块 HI_LIQ · wrapper v5 · **未申 `.ok`**）

占位：
- `<ET_TS>=$(date +%Y%m%d_%H%M%S)`（开跑瞬间）
- `<ARCH_PROBE_OK>` = Arch **新**签发的 **独立 probe** `.ok`（拟名 `output/ai_factory/ARCH_RUN_AUTH_LEAF25_MEM_PROBE_R1.ok`）——**不得**填 `1c32ab1e5ffb9eb3ddf466f15b0cd778a1579eaca678f2f5fbe1dd1ae00e66f0` / 任何 CONSUMED/VOID / X2 `.ok`
- 拟短窗：**主排**（建议叶27 12:30–13:30 ET 之后的短窗；**勿**默认抢占拟 X2 14:30–16:00 全段）——具体 not_before/expires 以主+Arch 为准；本稿仅占位

```bash
# DRAFT — 未授权；须新 probe .ok 且主排短窗内才可执行
# 本文件不是 .ok；禁复用 1c32ab1e；禁抬帽；采样仅 /tmp；禁本回合申签
cd /workspace/QuantLab && \
ET_TS=$(date +%Y%m%d_%H%M%S) && \
OUT=output/ai_factory/_leaf25_mem_probe/${ET_TS} && \
LOGDIR=${OUT}_logs && \
SAMPDIR=/tmp/quantlab_leaf25_mem_probe_${ET_TS} && \
mkdir -p "$OUT" "$LOGDIR" "$SAMPDIR" && \
# 预检：pgrep 空 + 新 probe .ok 钉 wrapper v5/C4/HI_LIQ/单块 + 时刻∈主排短窗 后，再：
bash docs/v2/audit/cmc_v1_1_leaf24/cmc_wrapper_v5_4240ce82.sh \
  --arch-ok <ARCH_PROBE_OK> \
  --assert leaf25_full_factor_mem_probe_r1 \
  --tag leaf25_mem_probe_r1 \
  --logdir "$LOGDIR" \
  --outdir "$OUT" \
  --sampler-dir "$SAMPDIR" \
  --meta "$OUT/run_meta.json" \
  --cwd /workspace/QuantLab -- \
  timeout 900 env PYTHONDONTWRITEBYTECODE=1 \
  /workspace/qlvenv/bin/python research/leaf25_full_factor_mem_probe_r1.py \
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

> 注：r1 骨架在 `--allow-real-data` 下仍对「真实 PIT 峰路径」保持 **NotImplemented 门闩**（防 densify）；Arch 审过实现包并签 probe `.ok` 后，须另补真实路径实现或 r2 再钉 sha，方可实跑校准峰。本草案展示 **开跑形参与帽/采样约束**，**不是**授权。

**一行摘要（开跑核；待 `.ok`）**：

```text
bash docs/v2/audit/cmc_v1_1_leaf24/cmc_wrapper_v5_4240ce82.sh … -- /workspace/qlvenv/bin/python research/leaf25_full_factor_mem_probe_r1.py --allow-real-data --universe HI_LIQ --mode month
```

| 路径类 | 约定 |
|---|---|
| out_dir | `output/ai_factory/_leaf25_mem_probe/<ET_TS>/` |
| log | `…/<ET_TS>_logs/` |
| **sampler** | `/tmp/quantlab_leaf25_mem_probe_<ET_TS>/`（禁 `output*`/`data*`） |
| 单块窗（example） | 如 2024-06 自然月开市日；以 chunk_plan 首块为准 |

**明确禁止**：
- 复用 step_m1 `.ok` `1c32ab1e5ffb9eb3ddf466f15b0cd778a1579eaca678f2f5fbe1dd1ae00e66f0`
- 抬 C4/stop/hard 超 1331200/1484800/1536000
- 采样写入 `output*` / `data*`
- 将本草案或实现包封面当作 `.ok`
- 本回合申 X2 实跑 `.ok` 或自开跑读大表
- 与密封/X2 实跑同张 `.ok`

---

## 4. probe `.ok` 结构要求（供 Arch；AI **不申**）

| 键意图 | 要求 |
|---|---|
| 轨 | **mem_probe only**（非 X2 / 非密封） |
| wrapper | v5 `4240ce82f0929085ab4bcb37e2400a3414e70e162c9e697cf02d97103342f882` |
| c4 / stop / hard | **1331200 / 1484800 / 1536000** |
| peak_split_threshold_kb | **1131520** |
| script | mem_probe `a0071e627d37f7e2498ea73984abb5b7ee4b1d2d0d27afdb85f8fc30986aed23` + chunk_plan `e858b32d314b9161a366ffef6661605943061162d707f7b86d01439d35dcdb12` |
| universe | HI_LIQ；单块（month 或 ≤20 rebal） |
| sampler | `/tmp` only；`allow_c5_ignore=false` |
| ban_reuse_ok | 显式禁 `1c32ab1e5ffb9eb3ddf466f15b0cd778a1579eaca678f2f5fbe1dd1ae00e66f0` |
| arch_mem_review_sha256 | `f389c394041cf517b8b8449507bfc157a354e51d2a3f41484adc57d021596d49` |
| mem_estimate_sha256 | `103717df1f9e5d63f8c681f16da091f44801e1b69b219ae1a18b2159446145d1` |
| ai_no_retry | true |
| live | false |
| 窗 | 主排短窗占位；not_before/expires 由主+Arch 填 |

---

## 5. 本文件边界

| 本文件是 | 本文件不是 |
|---|---|
| probe cmd **草案** + 帽/采样/禁复用钉表 | **不是** `.ok` / 不是授权 |
| 对齐 Arch NEED_MEM_PROBE §3 | **不**替代 Arch 签发 |
| 拟短窗占位 | **未申 `.ok`**；**不**自开跑 |

live=false.
