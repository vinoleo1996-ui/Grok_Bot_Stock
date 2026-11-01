# 叶27 Gate A mktcap_cache · HILIQ×x2×ndays40 CMD 草案（**未申 `.ok`** · 独立票）

- **角色**：QuantLab AI（执行器）
- **时刻**：2026-10-25T20:08:10-04:00（America/New_York；墙钟 2026-10-25 20:08 ET）
- **状态**：**DRAFT ONLY · HOLD_UNTIL_MAIN_SUBMIT** · **ok_requested=false** · **不是 `.ok`** · **不替代 Arch 签发** · **禁自开跑**
- **对照**：Arch 草案 **`a2307c8b`**；尖峰笔记 **`dd193511`**；ABORT 回执 **`d8be85cb`**；VOID **`fd159322`**；prev 脚本 **`8cb3e86f`** → 新脚本 **`27aae6db`**（mktcap_cache_r1）；forbid 六票明文
- **PRIMARY ONLY**：本票 **仅** 同 CLI ndays=40 + **代码** Gate A mktcap 缓存；**无** silent fallback / 无同票二阶 CLI

## 明确声明

> **本文件未申请、未获得、不构成任何 run/probe `.ok`。**  
> 在 Arch 另审 PASS、主排**新窗**并签发**新** `.ok` 之前，**禁止**执行下方 CLI。  
> **禁止**复跑 hist-prune/ndays40/month/quarter 票 / RESTORED 任何 VOID/CONSUMED `.ok`。  
> **禁止**在本票内静默切其它 chunk-mode 或其它 ndays。  
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
| script sha256 | `27aae6dbec0c80d96799c3cf6a7baba1bf8eaea866f0dae5feb2876e201175f5`（sha8 **`27aae6db`**；**CHANGED** vs `8cb3e86f`；mktcap_cache_r1） |
| prev script | `8cb3e86f0d5b199c474b38eba1950a44b18e4c0a1ded67d0f371429a55810012`（hist_prune_r1 基线；禁再签旧字节） |
| universe / window | `HILIQ` / `x2`（**禁** `both`；sealed 另签） |
| chunk_mode PRIMARY | `ndays` + `--chunk-ndays 40`（**唯一**；与 hist-prune/ABORT 票同 CLI） |
| hist_prune_tag | `hist_prune_r1`（**保留**） |
| mktcap_cache_tag | `mktcap_cache_r1`（Gate A：跨块缓存 + miss-only filters） |
| rss_limit | **1500** MB（**禁抬帽**） |
| 采样 | `/tmp/quantlab_leaf27_chunked_mktcap_cache_*` only |
| out_dir 建议 | `output/ai_factory/leaf27_chunked_members_mktcap_hiliq_x2_mktcap_cache` |
| 禁复用 `.ok` | **`2be59acd`** · **`a7d98ac9`** · **`8e51de63`** · **`3a6caa4f`** · **`8bcd79dc`** · **`725be3e0`** 及一切 VOID/CONSUMED |
| 禁同 cmd | 旧 `…_lowmem_v1.py` / 旧脚本字节 `8cb3e86f` **不可**再签；hist-prune/ndays40/month/quarter 票 **不可**复跑 |
| 对照 | Arch `a2307c8b` · 笔记 `dd193511` · 回执 `d8be85cb` · VOID `fd159322` |

## 与 hist-prune ABORT 票差异（防误复用）

| | hist-prune 票（ABORT） | 本草案（独立·Gate A） |
|---|---|---|
| chunk_mode | `ndays` + 40 | **同**（非 mode 变更） |
| 脚本字节 | `8cb3e86f…` | **`27aae6db…`** mktcap_cache_r1 |
| mktcap 装载 | 每块 `load_mktcap_by_session` 全表 12 RG | 跨块 cache；miss-only + pyarrow filters |
| 块末 mktcap | `clear()+del` | **保留** store（members/capadv 仍清） |
| hist_prune | `hist_prune_r1` | **保留** |
| `.ok` | VOID/`fd159322` 链路；禁 RESTORED | **无**（未申；须新签） |
| 峰证据 | 1518MB @chunk6_mktcap | **未实跑** |
| sampler 前缀 | `/tmp/quantlab_leaf27_chunked_histprune_*` | `/tmp/quantlab_leaf27_chunked_mktcap_cache_*` |
| 同票 fallback | 无 | **无**（PRIMARY only；ABORT→停+上报） |

## Prelaunch 清单（未来主令开跑时；**现不做**）

1. 新 `.ok` 盘证 MATCH（≠ 六票任一）；CLI 逐字 = PRIMARY ndays40
2. script sha256 MATCH `27aae6dbec0c80d96799c3cf6a7baba1bf8eaea866f0dae5feb2876e201175f5`；`--dry-compile-only` → `live:false` `ok_requested:false` `rss_limit_mb:1500` `hist_prune_tag:hist_prune_r1` `mktcap_cache_tag:mktcap_cache_r1`
3. healthz：`8795`（或既定 SOP）`ok=true` 且 `quiet=true`；若 8787 不通按 SOP，**勿**因短暂宕自改 CLI/抬帽
4. wait≥15s；`pgrep` 无 gen/snapshot/kline/本脚本重影
5. MemAvailable≥2.5GiB；rss 帽=1500 禁抬
6. sampler 仅 `/tmp/quantlab_leaf27_chunked_mktcap_cache_*`；禁 RESTORED/`lowmem_v1` 同 cmd；禁 `--window both`/FULLA
7. 单次；峰证明 REQUIRED（日志 `mktcap_cache hit/miss/load_n` + rss 阶梯 + sampler_30s）；交回执；QUIET 听 Arch 规则，AI 勿擅 lift
8. ABORT → **停 + 上报**；**禁静默切其它 mode**；下一跳听主/Arch

## 静态自检（本回合已做；非授权）

```bash
sha256sum research/leaf27_chunked_members_mktcap_r1.py
# → 27aae6dbec0c80d96799c3cf6a7baba1bf8eaea866f0dae5feb2876e201175f5
python3 -c "import py_compile;py_compile.compile('research/leaf27_chunked_members_mktcap_r1.py',cfile='/tmp/leaf27_mc.pyc',doraise=True)"
# → OK
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf27_chunked_members_mktcap_r1.py --dry-compile-only
# → live:false ok_requested:false rss_limit_mb:1500 hist_prune_tag:hist_prune_r1 mktcap_cache_tag:mktcap_cache_r1（无实数加载）
/tmp/ql_pyflakes_venv/bin/pyflakes research/leaf27_chunked_members_mktcap_r1.py
# → exit 0
```

schema-only 探类型（非实跑）：`trade_date=timestamp[us]`；`pq.read_table(..., filters=[("trade_date","in", [datetime,...])])` 对 2 日烟测行数合理。

live=false。
