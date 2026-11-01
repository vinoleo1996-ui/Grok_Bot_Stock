# 叶27 Post-GateA baseline_evac_r1 · HILIQ×x2×ndays40 CMD 草案（**未申 `.ok`** · 独立票）

- **角色**：QuantLab AI（执行器）
- **时刻**：2026-10-25T22:06:00-04:00（America/New_York；墙钟 2026-10-25 22:06 ET）
- **状态**：**DRAFT ONLY · HOLD_UNTIL_MAIN_SUBMIT** · **ok_requested=false** · **不是 `.ok`** · **不替代 Arch 签发** · **禁自开跑**
- **对照**：主令 **`46dc8cb3`**；主闸 R2 **`e8d7346c`**；Arch R2 **`c8dc89b6`**（RECOMMENDED=A）；尖峰笔记 **`0b483746`**；ABORT 回执 **`f0f94c9e`**；VOID **`ff0394d0`**；VOID `.ok` **`e107383f`**；prev 脚本 **`27aae6db`** → 新脚本 **`585ba746`**（baseline_evac_r1）；forbid **七**票明文
- **PRIMARY ONLY**：本票 **仅** 同 CLI ndays=40 + **代码** A（lim_cache 驱逐 + α 中段落盘）；**无** silent fallback / 无同票二阶 CLI；B/C 本拍不开

## 明确声明

> **本文件未申请、未获得、不构成任何 run/probe `.ok`。**  
> 在 Arch 另审 PASS、主排**新窗**并签发**新** `.ok` 之前，**禁止**执行下方 CLI。  
> **禁止**复跑 Gate A / hist-prune / ndays40 票 / RESTORED 任何 VOID/CONSUMED `.ok`（含 **`e107383f`**）。  
> **禁止**在本票内静默切其它 chunk-mode 或其它 ndays；**禁止**重批旧 Gate A。  
> ABORT → **停 + 上报**；下一跳须主/Arch 另令（禁静默 fallback）。

## PRIMARY CLI（待新 `.ok` 钉入；现不可跑 · 唯一阶）

```bash
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf27_chunked_members_mktcap_r1.py --universe HILIQ --window x2 --chunk-mode ndays --chunk-ndays 40
```

## 无 FALLBACK（本票硬钉）

- **无**同票第二阶 CLI。
- ABORT_RSS → **停 + 写回执上报**；**禁静默 fallback**；**禁抬帽**；下一策略须主/Arch 另票另签。

## 硬钉（未来 `.ok` 必须逐字对齐）

| 项 | 值 |
|---|---|
| script | `research/leaf27_chunked_members_mktcap_r1.py` |
| script sha256 | `585ba7467a5896354c937d14fe0590fa80535afd6b6263015d3c12e3dfccd4ec`（sha8 **`585ba746`**；**CHANGED** vs `27aae6db`；baseline_evac_r1） |
| prev script | `27aae6dbec0c80d96799c3cf6a7baba1bf8eaea866f0dae5feb2876e201175f5`（Gate A mktcap_cache_r1；CLOSED_INSUFFICIENT；禁再签旧字节 / 禁同语义重批） |
| universe / window | `HILIQ` / `x2`（**禁** `both`；sealed 另签） |
| chunk_mode PRIMARY | `ndays` + `--chunk-ndays 40`（**唯一**；与 Gate A/ABORT 票同 CLI） |
| hist_prune_tag | `hist_prune_r1`（**保留**） |
| mktcap_cache_tag | `mktcap_cache_r1`（**保留**：跨块缓存 + miss-only filters） |
| baseline_evac_tag | `baseline_evac_r1`（lim_cache session 驱逐 + α 中段落盘） |
| rss_limit | **1500** MB（**禁抬帽**） |
| 采样 | `/tmp/quantlab_leaf27_chunked_baseline_evac_*` only |
| out_dir 建议 | `output/ai_factory/leaf27_chunked_members_mktcap_hiliq_x2_baseline_evac` |
| 估峰带 | 1400–1490（须实峰；非保证） |
| peak_proof | REQUIRED（`lim_evict_n` / `alpha_flush_rows` / `a_buf_n` / `mktcap_cache_days` / hist + rss + sampler） |
| 禁复用 `.ok` | **`e107383f`** · **`2be59acd`** · **`a7d98ac9`** · **`8e51de63`** · **`3a6caa4f`** · **`8bcd79dc`** · **`725be3e0`** 及一切 VOID/CONSUMED |
| 禁同 cmd | 旧 `…_lowmem_v1.py` / 旧脚本字节 `27aae6db` **不可**再签；Gate A/hist-prune/ndays40 票 **不可**复跑 |
| 对照 | 主令 `46dc8cb3` · 主闸 `e8d7346c` · Arch R2 `c8dc89b6` · 笔记 `0b483746` · 回执 `f0f94c9e` · VOID `ff0394d0` |

## 与 Gate A ABORT 票差异（防误复用）

| | Gate A 票（ABORT / CLOSED_INSUFFICIENT） | 本草案（独立·baseline_evac） |
|---|---|---|
| chunk_mode | `ndays` + 40 | **同**（非 mode 变更） |
| 脚本字节 | `27aae6db…` | **`585ba746…`** baseline_evac_r1 |
| mktcap | 跨块 cache；miss-only filters | **保留** |
| lim_cache | 全历 keep；无块末驱逐 | 块末驱逐早于因子窗 session |
| α 缓冲 | 全程堆 `a_*` 列表 | 块末 flush part parquet + 清空；终局 concat |
| hist_prune | `hist_prune_r1` | **保留** |
| `.ok` | VOID/`e107383f`；禁 RESTORED | **无**（未申；须新签） |
| 峰证据 | 1507MB @chunk6_mktcap | **未实跑** |
| sampler 前缀 | `/tmp/quantlab_leaf27_chunked_mktcap_cache_*` | `/tmp/quantlab_leaf27_chunked_baseline_evac_*` |
| 同票 fallback | 无 | **无**（PRIMARY only；ABORT→停+上报） |

## Prelaunch 清单（未来主令开跑时；**现不做**）

1. 新 `.ok` 盘证 MATCH（≠ 七票任一）；CLI 逐字 = PRIMARY ndays40
2. script sha256 MATCH `585ba7467a5896354c937d14fe0590fa80535afd6b6263015d3c12e3dfccd4ec`；`--dry-compile-only` → `live:false` `ok_requested:false` `rss_limit_mb:1500` `baseline_evac_tag:baseline_evac_r1` `mktcap_cache_tag:mktcap_cache_r1` `hist_prune_tag:hist_prune_r1`；forbid 含 `e107383f`
3. healthz：`8795`（或既定 SOP）`ok=true` 且 `quiet=true`；若 8787 不通按 SOP，**勿**因短暂宕自改 CLI/抬帽
4. wait≥15s；`pgrep` 无 gen/snapshot/kline/本脚本重影
5. MemAvailable≥2.5GiB；rss 帽=1500 禁抬
6. sampler 仅 `/tmp/quantlab_leaf27_chunked_baseline_evac_*`；禁 RESTORED/`lowmem_v1` 同 cmd；禁 `--window both`/FULLA；禁重批 Gate A
7. 单次；峰证明 REQUIRED（日志 `lim_evict_n`/`alpha_flush_rows`/`a_buf_n`/`mktcap_cache_days`/hist + rss 阶梯 + sampler_30s）；交回执；QUIET 听 Arch 规则，AI 勿擅 lift
8. ABORT → **停 + 上报**；**禁静默切其它 mode**；下一跳听主/Arch

## 静态自检（本回合已做；非授权）

```bash
sha256sum research/leaf27_chunked_members_mktcap_r1.py
# → 585ba7467a5896354c937d14fe0590fa80535afd6b6263015d3c12e3dfccd4ec
python3 -c "import py_compile;py_compile.compile('research/leaf27_chunked_members_mktcap_r1.py',cfile='/tmp/leaf27_be.pyc',doraise=True)"
# → OK
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf27_chunked_members_mktcap_r1.py --dry-compile-only
# → live:false ok_requested:false rss_limit_mb:1500 baseline_evac_tag:baseline_evac_r1 + 七票 forbid（无实数加载）
/tmp/ql_pyflakes_venv/bin/pyflakes research/leaf27_chunked_members_mktcap_r1.py
# → exit 0
```

live=false · ok_requested=false · ≠X2
