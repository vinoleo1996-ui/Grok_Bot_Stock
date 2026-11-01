# 叶25 mem_probe r3 · 实峰 cmd 草案（未授权 · 未申 `.ok`）

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI（执行器） |
| 起草 | `2026-10-25T12:35:23-0400`（America/New_York；墙钟 `2026-10-25 12:35:23 ET`） |
| 状态 | **DRAFT**（**不是 `.ok`** · **未授权实跑** · **不替代 Arch 签发**） |
| live | **false** · promotion_approved **false** |
| 对齐主令 | `52aa42c239b6b785a4c01345b7773776cb0a705ffa86a5ef6b4c70938456f6d4`（`MAIN_LEAF25_MEM_PROBE_R2_FAIL_R3_ORDER_20261025_ZH.md`） |
| 对齐 Arch VOID+r3 | `6ef34f99c78c341bd1c8308100507856b7b7990ffae462abc859cb47f7ddfe3f`（sha8 `6ef34f99`） |
| r2 FAIL 回执 | `d01f95c0b2f5ffa59c56787bfeb09c30c980de6a0f0ce10f10998c4fe3050454`（sha8 `d01f95c0`） |
| 本回合 | **未申 `.ok`** · **未** `--allow-real-data` · 仅静态/dry 结构 |

---

## 1. 钉表（全长）

| 件 | 路径 / 值 | sha256 |
|---|---|---|
| 主令 | `docs/v2/audit/MAIN_LEAF25_MEM_PROBE_R2_FAIL_R3_ORDER_20261025_ZH.md` | `52aa42c239b6b785a4c01345b7773776cb0a705ffa86a5ef6b4c70938456f6d4` |
| Arch VOID+r3 | `docs/v2/audit/ARCH_LEAF25_MEM_PROBE_R2_FAIL_VOID_R3_RULE_20261025_ZH.md` | `6ef34f99c78c341bd1c8308100507856b7b7990ffae462abc859cb47f7ddfe3f` |
| r2 FAIL 回执 | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_MEM_PROBE_R2_RUN_RECEIPT_20261025_ZH.md` | `d01f95c0b2f5ffa59c56787bfeb09c30c980de6a0f0ce10f10998c4fe3050454` |
| **wrapper v5** | `docs/v2/audit/cmc_v1_1_leaf24/cmc_wrapper_v5_4240ce82.sh` | **`4240ce82f0929085ab4bcb37e2400a3414e70e162c9e697cf02d97103342f882`** |
| chunk_plan | `research/leaf25_full_factor_chunk_plan_r1.py` | `e858b32d314b9161a366ffef6661605943061162d707f7b86d01439d35dcdb12` (**UNCHANGED**) |
| **mem_probe r3** | `research/leaf25_full_factor_mem_probe_r3.py` | **`8da4f2e663d83956b4b9910fc958f9decba68f40327f2089610ffa1a069600ea`** |
| build stub | `research/leaf25_cfacc_desens_build_r1.py` | `45537fb9294202f10293b8c0c7b57d9ebf95b835f8af23e3ef63a6dc25c47ee3` (**UNCHANGED**) |
| 禁复用 step_m1 `.ok` | CONSUMED | **`1c32ab1e5ffb9eb3ddf466f15b0cd778a1579eaca678f2f5fbe1dd1ae00e66f0`** |
| 禁复用 r2 VOID `.ok` | `_consumed/…VOID.FAIL_TYPE.20261025T1232ET.ok` | **`cd230f9c2aa9fc8de7fc538fb1f04ded8d9c20463f24b88b6c0f76950ec34279`** |
| 宇宙 | **HI_LIQ**（单块） | FULLA **非本轮** |
| 块粒度 | `--mode month` **或** `--mode rebal_days --max-rebaldays ≤20` | **禁** `--window both` |

---

## 2. 帽与采样（禁抬帽）

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

---

## 3. 拟 cmd（单块 HI_LIQ · wrapper v5 · **未申 `.ok`**）

占位：
- `<ET_TS>=$(date +%Y%m%d_%H%M%S)`（开跑瞬间）
- `<ARCH_PROBE_OK>` = Arch **新**签发的 **独立实峰 probe** `.ok`（拟名 `output/ai_factory/ARCH_RUN_AUTH_LEAF25_MEM_PROBE_R3.ok`）——**不得**填 `cd230f9c2aa9fc8de7fc538fb1f04ded8d9c20463f24b88b6c0f76950ec34279` / `1c32ab1e5ffb9eb3ddf466f15b0cd778a1579eaca678f2f5fbe1dd1ae00e66f0` / 任何 CONSUMED/VOID / X2 `.ok` / r1 dry `.ok` / r2 票
- 拟短窗：主+Arch 另排（与叶27 互斥 QUIET）

```bash
# DRAFT — 未授权；须新实峰 probe .ok 且主排短窗内才可执行
# 本文件不是 .ok；禁复用 cd230f9c / 1c32ab1e；禁抬帽；采样仅 /tmp；禁本回合申签
# 禁 --window both；FULLA 非本轮；禁自开跑
cd /workspace/QuantLab && \
ET_TS=$(date +%Y%m%d_%H%M%S) && \
OUT=output/ai_factory/_leaf25_mem_probe_r3/${ET_TS} && \
LOGDIR=${OUT}_logs && \
SAMPDIR=/tmp/quantlab_leaf25_mem_probe_r3_${ET_TS} && \
mkdir -p "$OUT" "$LOGDIR" "$SAMPDIR" && \
# 预检：pgrep 空 + 新实峰 probe .ok 钉 wrapper v5/C4/HI_LIQ/单块 + 时刻∈主排短窗 后，再：
bash docs/v2/audit/cmc_v1_1_leaf24/cmc_wrapper_v5_4240ce82.sh \
  --arch-ok <ARCH_PROBE_OK> \
  --assert leaf25_full_factor_mem_probe_r3 \
  --tag leaf25_mem_probe_r3 \
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
bash docs/v2/audit/cmc_v1_1_leaf24/cmc_wrapper_v5_4240ce82.sh … -- /workspace/qlvenv/bin/python research/leaf25_full_factor_mem_probe_r3.py --allow-real-data --universe HI_LIQ --mode month
```

| 路径类 | 约定 |
|---|---|
| out_dir | `output/ai_factory/_leaf25_mem_probe_r3/<ET_TS>/` |
| log | `…/<ET_TS>_logs/` |
| **sampler** | `/tmp/quantlab_leaf25_mem_probe_r3_<ET_TS>/`（禁 `output*`/`data*`） |
| part | `alpha_parts/chunk_XXXX.parquet`（float32；densify=false） |
| 单块窗（example） | 2024-06-03→2024-06-28 · chunk0 |

**明确禁止**：
- 复用 `cd230f9c2aa9fc8de7fc538fb1f04ded8d9c20463f24b88b6c0f76950ec34279`（VOID）/ `1c32ab1e5ffb9eb3ddf466f15b0cd778a1579eaca678f2f5fbe1dd1ae00e66f0` / r1 dry `.ok` / X2 `.ok`
- 抬 C4/stop/hard；`allow_c5_ignore=true`
- `--window both`；本轮 FULLA
- 整窗 densify；采样落 `output*`/`data*`
- 无 `.ok` 盲跑 `--allow-real-data`；本草案本身当授权
- 自开跑 / 申 X2.ok

## 4. 回执须披露（开跑后）

- `dry_run=false` / `float32=true` / `densify=false` / `claims_full_cfacc=false`
- `peak_kb`、块边界、`n_days`/`n_names`、HI_LIQ mask sha
- RSS 各 stage；若 ≥0.85×C4 → exit 94 拆块（禁抬帽重试）
- 滤子类型：`end_date` RHS=`Timestamp`（非 string）

## 5. 下一跳

Arch 审 r3 包 → 另签**实峰** probe `.ok`（短窗）→ 主排窗 → AI 入窗开跑 → 回执交 Arch。  
**本文件不是 `.ok`。** live=false。
