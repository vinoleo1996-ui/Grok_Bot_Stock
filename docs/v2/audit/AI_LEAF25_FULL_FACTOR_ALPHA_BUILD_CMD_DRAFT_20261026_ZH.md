# 叶25 全叶/HILIQ×x2 alpha 构建 · CMD 草案（**未申 `.ok`** · 修订自 `035e5818`）

- **角色**：QuantLab AI（执行器）
- **时刻**：2026-10-26T01:20:00-04:00（America/New_York；墙钟 2026-10-26 01:20 ET）
- **状态**：**DRAFT ONLY · HOLD_UNTIL_MAIN_SUBMIT** · **ok_requested=false** · **不是 `.ok`** · **不替代 Arch 签发** · **禁自开跑** · **禁自签** · Arch **只审不签**
- **对照**：主令本拍「定下一票｜叶25 alpha 构建」；旧 CMD **`035e5818`**；r6 令 **`53331667`**；FROZEN **`4bb1ff2b`**；基盘 **`e8ca2bcc`**；MEM **`103717df`**；新脚本 **`de7b3647`**；wrapper v5 **`4240ce82`**；forbid 明文见下
- **票种**：**alpha 构建**（**≠** selfcheck · **≠** Book-Smoke · **≠** X2 ACCEPT）
- **PRIMARY ONLY**：HILIQ×x2；禁 FULLA；禁 `--window both`；密封另签不含

## 明确声明

> **本文件未申请、未获得、不构成任何 run/probe `.ok`。**  
> 在 Arch 另审 PASS、主排**新窗**并签发**新** `.ok` 之前，**禁止**执行下方 CLI。  
> **禁止**复用 forbid 任一 VOID/CONSUMED `.ok`（含 **`1c32ab1e`** / **`6054b3bf`** 等）。  
> **禁止**把 mem_probe 探针脚本当本票构建入口。  
> ABORT → **停 + 上报**；下一跳须主/Arch 另令（禁静默 fallback / 禁抬帽）。

## PRIMARY CLI（待新 `.ok` 钉入；现不可跑 · 唯一阶）

```bash
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf25_full_factor_alpha_build_r1.py --universe HILIQ --window x2 --x2-end 20261009 --chunk-mode month --out output/ai_factory/_leaf25_full_factor/<ET_TS>/
```

一行摘要：

```text
/workspace/qlvenv/bin/python research/leaf25_full_factor_alpha_build_r1.py --universe HILIQ --window x2 --x2-end 20261009 --chunk-mode month --out <OUT>
```

## 拟 wrapper 形（可选；与直接 python+sampler 二选一）

修订自旧 CMD `035e5818`：仍可钉 wrapper v5 `4240ce82`。开跑瞬间须另加 `--allow-real-data --arch-ok-path <NEW_OK>`（**本草案不填** CONSUMED）。

```bash
# DRAFT — 未授权；须新 X2 .ok + 主排窗后才可执行
cd /workspace/QuantLab && \
ET_TS=$(date +%Y%m%d_%H%M%S) && \
OUT=output/ai_factory/_leaf25_full_factor/${ET_TS} && \
LOGDIR=${OUT}_logs && \
SAMPDIR=/tmp/quantlab_leaf25_full_alpha_${ET_TS} && \
mkdir -p "$OUT" "$LOGDIR" "$SAMPDIR" && \
bash docs/v2/audit/cmc_v1_1_leaf24/cmc_wrapper_v5_4240ce82.sh \
  --arch-ok <ARCH_X2_OK_NEW> \
  --assert leaf25_full_factor_alpha_hiliq_x2 \
  --tag leaf25_full_factor_alpha_hiliq_x2 \
  --logdir "$LOGDIR" \
  --outdir "$OUT" \
  --meta "$OUT/run_meta.json" \
  --cwd /workspace/QuantLab -- \
  timeout 3600 env PYTHONDONTWRITEBYTECODE=1 \
  /workspace/qlvenv/bin/python research/leaf25_full_factor_alpha_build_r1.py \
    --universe HILIQ --window x2 --x2-end 20261009 \
    --chunk-mode month --out "$OUT/" \
    --allow-real-data --arch-ok-path <ARCH_X2_OK_NEW> \
    --sample-dir "$SAMPDIR"
```

**本回合选择**：文档钉 **直接 python PRIMARY CLI** 为开跑核；wrapper v5 为可选外壳（与旧 `035e5818` 对齐）。二者均须新 `.ok`。

## 无 FALLBACK（本票硬钉）

- **无**同票第二阶 CLI（无 FULLA / 无 both / 无抬帽）。
- ABORT_RSS → **停 + 写回执上报**；**禁静默 fallback**；**禁抬帽**。

## 硬钉（未来 `.ok` 必须逐字对齐）

| 项 | 值 |
|---|---|
| script | `research/leaf25_full_factor_alpha_build_r1.py` |
| script sha256 | `de7b36477908ee522c73e71db64ac904356d7a65c420ea897332925c36427856`（sha8 **`de7b3647`**） |
| universe / window | `HILIQ` / `x2`（**禁** `both`；**禁** FULLA；密封另签） |
| x2_end | `20261009`（窗 2024-06-03→2026-10-09） |
| chunk_mode | `month`（PRIMARY；`rebal` 可选同票另钉） |
| mechanism_tag | `g1g5_ashare_cfacc_desens_cs_v1` |
| rss_limit | **1500** MB（**禁抬帽**） |
| C4 / stop / hard | **1331200 / 1484800 / 1536000** kB |
| sampler | `/tmp/quantlab_leaf25_full_alpha_*` only |
| out_dir 建议 | `output/ai_factory/_leaf25_full_factor/<ET_TS>/` |
| wrapper（可选） | v5 `4240ce82f0929085ab4bcb37e2400a3414e70e162c9e697cf02d97103342f882` |
| 禁复用 `.ok` | `1c32ab1e / e107383f / 2be59acd / a7d98ac9 / 8e51de63 / 3a6caa4f / 8bcd79dc / 725be3e0 / 0f50daf7 / 3c19dd7d / 6054b3bf` 及一切 VOID/CONSUMED |
| 对照 | 旧 CMD `035e5818` · r6 令 `53331667` · FROZEN `4bb1ff2b` · 基盘 `e8ca2bcc` · MEM `103717df` |
| 残差 | CFACC 主路径实装；β120/mom/logADV20/vol20 = PIN_GAP（见 meta） |

## 与旧 X2 CMD / 探针差异（防误复用）

| | 旧 X2 CMD `035e5818` / 探针 | 本草案（alpha 构建） |
|---|---|---|
| 脚本 | `<BUILD_SCRIPT>` 占位 / mem_probe_r3 | **`de7b3647`** 新文件 |
| 目的 | cmd 形 / MEM 峰探针 | **全叶 α 构建** |
| α | 未实现 / crude probe | CFACC TTM + desens + 部分残差 |
| FULLA | 未禁死 | **CLI choices 不含；见即 STOP** |
| `.ok` | 未申；禁 1c32ab1e | **未申**；forbid 扩至十一票 |

## Prelaunch 清单（未来主令开跑时；**现不做**）

1. 新 `.ok` 盘证 MATCH（≠ forbid 任一）；CLI 逐字 = PRIMARY
2. script sha256 MATCH `de7b36477908ee522c73e71db64ac904356d7a65c420ea897332925c36427856`；`--dry-compile-only` → `live:false` `ok_requested:false` `rss_limit_mb:1500` `universe:HILIQ` `window:x2` `mechanism_tag:g1g5_ashare_cfacc_desens_cs_v1`；forbid 含 `1c32ab1e`/`6054b3bf`
3. healthz 按 SOP；`pgrep` 无研究重影
4. MemAvailable 充足；rss 帽=1500 禁抬
5. sampler 仅 `/tmp/quantlab_leaf25_full_alpha_*`；禁 `--window both`/FULLA
6. 单次；峰证明 REQUIRED；交回执；QUIET 听 Arch
7. ABORT → **停 + 上报**

## 静态自检（本回合已做；非授权）

```bash
sha256sum research/leaf25_full_factor_alpha_build_r1.py
# → de7b36477908ee522c73e71db64ac904356d7a65c420ea897332925c36427856
python3 -c "import py_compile;py_compile.compile('research/leaf25_full_factor_alpha_build_r1.py',cfile='/tmp/leaf25_full_alpha_build_r1.pyc',doraise=True)"
# → OK
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf25_full_factor_alpha_build_r1.py --dry-compile-only
# → live:false ok_requested:false rss_limit_mb:1500 universe:HILIQ window:x2 + forbid 列表（无实数加载）
/tmp/ql_pyflakes_venv/bin/pyflakes research/leaf25_full_factor_alpha_build_r1.py
# → exit 0
```

live=false · ok_requested=false · ≠X2 ACCEPT · ≠selfcheck · HOLD_UNTIL_MAIN_SUBMIT
