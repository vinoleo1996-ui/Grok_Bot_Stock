# 叶25 mem_probe r2 · 实峰 cmd 草案（未授权 · 未申 `.ok`）

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI（执行器） |
| 起草 | `2026-10-25T12:11:55-0400`（America/New_York；墙钟 `2026-10-25 12:11:55 ET`） |
| 状态 | **DRAFT**（**不是 `.ok`** · **未授权实跑** · **不替代 Arch 签发**） |
| live | **false** · promotion_approved **false** |
| 对齐 | Arch 采纳 (A) **`14e9b6ba161057fe73015decf789041eef2a1e910e0ef656c16dcb85d78bce4e`**（拒签 r1 实峰/dry）；NEED_MEM_PROBE `f389c394041cf517b8b8449507bfc157a354e51d2a3f41484adc57d021596d49` |
| 本回合 | **未申 `.ok`** · **未** `--allow-real-data` 读大表 · 仅静态/dry 结构 |

---

## 1. 钉表（全长）

| 件 | 路径 / 值 | sha256 |
|---|---|---|
| Arch 采纳 (A) | `docs/v2/audit/ARCH_LEAF25_MEM_PROBE_ADOPT_A_REJECT_REAL_PEAK_20261025_ZH.md` | `14e9b6ba161057fe73015decf789041eef2a1e910e0ef656c16dcb85d78bce4e` |
| Arch NEED_MEM_PROBE | `docs/v2/audit/ARCH_LEAF25_MEM_CHUNK_REVIEW_20261025_ZH.md` | `f389c394041cf517b8b8449507bfc157a354e51d2a3f41484adc57d021596d49` |
| MEM 分块 | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_FULL_FACTOR_MEM_ESTIMATE_CHUNK_20261025_ZH.md` | `103717df1f9e5d63f8c681f16da091f44801e1b69b219ae1a18b2159446145d1` |
| r6 FROZEN 戳 | `docs/v2/AI_LEAF25_FULL_FACTOR_PREREG_r6_FROZEN_20261025_ZH.md` | `4bb1ff2b805f441499607ada5f871044e72e6176a66052c73b64816130d199e2` |
| **wrapper v5** | `docs/v2/audit/cmc_v1_1_leaf24/cmc_wrapper_v5_4240ce82.sh` | **`4240ce82f0929085ab4bcb37e2400a3414e70e162c9e697cf02d97103342f882`** |
| chunk_plan | `research/leaf25_full_factor_chunk_plan_r1.py` | `e858b32d314b9161a366ffef6661605943061162d707f7b86d01439d35dcdb12` (**UNCHANGED**) |
| **mem_probe r2** | `research/leaf25_full_factor_mem_probe_r2.py` | **`9dfe173a9104330287f6ebfe2f758c63891f3c92b5f9d112118b697898d50e0f`** |
| build stub | `research/leaf25_cfacc_desens_build_r1.py` | `45537fb9294202f10293b8c0c7b57d9ebf95b835f8af23e3ef63a6dc25c47ee3` (**UNCHANGED**) |
| 禁复用 step_m1 `.ok` | CONSUMED | **`1c32ab1e5ffb9eb3ddf466f15b0cd778a1579eaca678f2f5fbe1dd1ae00e66f0`** |
| 宇宙 | **HI_LIQ**（单块） | FULLA **非本轮**（实路径 STOP） |
| 块粒度 | `--mode month` **或** `--mode rebal_days --max-rebaldays ≤20` | **禁** `--window both` |

---

## 2. 帽与采样（禁抬帽）

| 项 | 值 |
|---|---|
| C4 | **1331200** kB |
| wrapper STOPKB | **1484800** kB |
| hard | **1536000** kB |
| 拆块阈值 | **1131520** kB（0.85×C4）；破则 exit 94，再拆，**不**抬帽 |
| 采样 | **仅** `/tmp/quantlab_*`（wrapper 默认 `/tmp/quantlab_wrapper_sampler/`） |
| `allow_c5_ignore` | **false** |
| 破帽 | **ABORT**；`ai_no_retry` |

`.ok` / `.cmd` 若写成更高帽 → **Arch 应拒签**。

---

## 3. 拟 cmd（单块 HI_LIQ · wrapper v5 · **未申 `.ok`**）

占位：
- `<ET_TS>=$(date +%Y%m%d_%H%M%S)`（开跑瞬间）
- `<ARCH_PROBE_OK>` = Arch **新**签发的 **独立实峰 probe** `.ok`（拟名 `output/ai_factory/ARCH_RUN_AUTH_LEAF25_MEM_PROBE_R2.ok`）——**不得**填 `1c32ab1e5ffb9eb3ddf466f15b0cd778a1579eaca678f2f5fbe1dd1ae00e66f0` / 任何 CONSUMED/VOID / X2 `.ok` / r1 dry `.ok`
- 拟短窗：主+Arch 另排（**勿**默认抢占拟 X2 14:30–16:00 全段）

```bash
# DRAFT — 未授权；须新实峰 probe .ok 且主排短窗内才可执行
# 本文件不是 .ok；禁复用 1c32ab1e；禁抬帽；采样仅 /tmp；禁本回合申签
# 禁 --window both；FULLA 非本轮
cd /workspace/QuantLab && \
ET_TS=$(date +%Y%m%d_%H%M%S) && \
OUT=output/ai_factory/_leaf25_mem_probe_r2/${ET_TS} && \
LOGDIR=${OUT}_logs && \
SAMPDIR=/tmp/quantlab_leaf25_mem_probe_r2_${ET_TS} && \
mkdir -p "$OUT" "$LOGDIR" "$SAMPDIR" && \
# 预检：pgrep 空 + 新实峰 probe .ok 钉 wrapper v5/C4/HI_LIQ/单块 + 时刻∈主排短窗 后，再：
bash docs/v2/audit/cmc_v1_1_leaf24/cmc_wrapper_v5_4240ce82.sh \
  --arch-ok <ARCH_PROBE_OK> \
  --assert leaf25_full_factor_mem_probe_r2 \
  --tag leaf25_mem_probe_r2 \
  --logdir "$LOGDIR" \
  --outdir "$OUT" \
  --sampler-dir "$SAMPDIR" \
  --meta "$OUT/run_meta.json" \
  --cwd /workspace/QuantLab -- \
  timeout 900 env PYTHONDONTWRITEBYTECODE=1 \
  /workspace/qlvenv/bin/python research/leaf25_full_factor_mem_probe_r2.py \
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

**等价块粒度（二选一，禁 both）**：

```bash
# 备选：rebal_days ≤ 20
  ... --mode rebal_days --max-rebaldays 20 --start 2024-06-03 --end 2026-10-09 --chunk-id 0 ...
```

**一行摘要（开跑核；待 `.ok`）**：

```text
bash docs/v2/audit/cmc_v1_1_leaf24/cmc_wrapper_v5_4240ce82.sh … -- /workspace/qlvenv/bin/python research/leaf25_full_factor_mem_probe_r2.py --allow-real-data --universe HI_LIQ --mode month
```

| 路径类 | 约定 |
|---|---|
| out_dir | `output/ai_factory/_leaf25_mem_probe_r2/<ET_TS>/` |
| log | `…/<ET_TS>_logs/` |
| **sampler** | `/tmp/quantlab_leaf25_mem_probe_r2_<ET_TS>/`（禁 `output*`/`data*`） |
| part | `alpha_parts/chunk_XXXX.parquet`（float32；densify=false） |
| 单块窗（example） | 2024-06 自然月；或以 chunk_plan 首块为准 |

**明确禁止**：
- 复用 `1c32ab1e5ffb9eb3ddf466f15b0cd778a1579eaca678f2f5fbe1dd1ae00e66f0` / r1 dry `.ok` / X2 `.ok`
- 抬 C4/stop/hard；`allow_c5_ignore=true`
- `--window both`；本轮 FULLA
- 整窗 densify；采样落 `output*`/`data*`
- 无 `.ok` 盲跑 `--allow-real-data`
- 本草案本身当授权

## 4. 回执须披露（开跑后）

- `dry_run=false` / `float32=true` / `densify=false` / `claims_full_cfacc=false`
- `peak_kb`、块边界、`n_days`/`n_names`、HI_LIQ mask sha
- RSS 各 stage；若 ≥0.85×C4 → exit 94 拆块（禁抬帽重试）

## 5. 下一跳

Arch 审 r2 包 → 另签**实峰** probe `.ok`（短窗）→ 主排窗 → AI 入窗开跑 → 回执交 Arch 钉 X2 内存键。  
**本文件不是 `.ok`。** live=false。
