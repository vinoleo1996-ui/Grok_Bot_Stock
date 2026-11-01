# 叶27 更深分块 · HILIQ×x2×ndays40 CMD 草案（**未申 `.ok`** · 独立票）

- **角色**：QuantLab AI（执行器）
- **时刻**：2026-10-25T15:56:48-04:00（America/New_York；墙钟 2026-10-25 15:56 ET）
- **状态**：**DRAFT ONLY · HOLD_UNTIL_MAIN_SUBMIT** · **ok_requested=false** · **不是 `.ok`** · **不替代 Arch 签发** · **禁自开跑**
- **对照**：month ABORT 回执 sha8 **`03c58db5`**；脚本 UNCHANGED **`262f9bf6`**；已消费 month `.ok` **`8e51de63`**（禁 RESTORED）；先验 VOID `3a6caa4f`/`8bcd79dc`/`725be3e0`；month 审 `85c6fb82`（另交 ndays40）
- **PRIMARY ONLY**：本票 **仅** ndays=40；**无** silent fallback / 无同票二阶 CLI

## 明确声明

> **本文件未申请、未获得、不构成任何 run/probe `.ok`。**  
> 在 Arch **VOID/CONSUME** 已消费 month `.ok` `8e51de63` 且另审 PASS、主排**新窗**并签发**新** `.ok` 之前，**禁止**执行下方 CLI。  
> **禁止**复跑 month/quarter 票 / RESTORED 任何 VOID/CONSUMED `.ok`。  
> **禁止**在本票内静默切其它 chunk-mode 或其它 ndays。

## PRIMARY CLI（待新 `.ok` 钉入；现不可跑 · 唯一阶）

```bash
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf27_chunked_members_mktcap_r1.py --universe HILIQ --window x2 --chunk-mode ndays --chunk-ndays 40
```

## 无 FALLBACK（本票硬钉）

- **无**同票第二阶 CLI。
- ABORT_RSS → **停**；另交 **hist-prune** 独立票（听主/Arch）；**禁静默 fallback**；**禁抬帽**。

## 硬钉（未来 `.ok` 必须逐字对齐）

| 项 | 值 |
|---|---|
| script | `research/leaf27_chunked_members_mktcap_r1.py` |
| script sha256 | `262f9bf6878d5c64956529a680abbf36e45adfe72fc7dedc4c68dc1c40291a10`（**UNCHANGED**；CLI-only 侧稿） |
| universe / window | `HILIQ` / `x2`（**禁** `both`；sealed 另签） |
| chunk_mode PRIMARY | `ndays` + `--chunk-ndays 40`（**唯一**） |
| rss_limit | **1500** MB（**禁抬帽**） |
| 采样 | `/tmp/quantlab_leaf27_chunked_ndays40_*` only |
| out_dir 建议 | `output/ai_factory/leaf27_chunked_members_mktcap_hiliq_x2_ndays40` |
| 禁复用 `.ok` | `8bcd79dc…` · `725be3e0…` · `3a6caa4f…` · **`8e51de63…`（month 已消费）** 及一切 VOID/CONSUMED |
| 禁同 cmd | 旧 `…_lowmem_v1.py --universe HILIQ --window x2` **不可**再签；month/quarter 票 **不可**复跑 |

## 与 month 已消费票差异（防误复用）

| | month 票（ABORT） | 本草案（独立） |
|---|---|---|
| chunk_mode | `month` | **`ndays` + `--chunk-ndays 40`** |
| 脚本字节 | `262f9bf6…` | **同** UNCHANGED |
| `.ok` | `8e51de63` 已消费 | **无**（未申；须新签） |
| 峰证据 | 1502MB @chunk12_mktcap | **未实跑** |
| sampler 前缀 | `/tmp/quantlab_leaf27_chunked_month_*` | `/tmp/quantlab_leaf27_chunked_ndays40_*` |
| 同票 fallback | month 包曾列 ndays40 为 FALLBACK | **本票无 FALLBACK**（PRIMARY only） |

## Prelaunch 清单（未来主令开跑时；**现不做**）

1. 新 `.ok` 盘证 MATCH（≠ `8e51de63` / ≠ `3a6caa4f` / ≠ `8bcd79dc` / ≠ `725be3e0`）；CLI 逐字 = PRIMARY ndays40
2. script sha256 MATCH `262f9bf6…`；`--dry-compile-only` → `live:false` `ok_requested:false` `rss_limit_mb:1500`
3. healthz：`8795`（或既定 SOP）`ok=true` 且 `quiet=true`；若 8787 不通按 SOP，**勿**因短暂宕自改 CLI/抬帽
4. wait≥15s；`pgrep` 无 gen/snapshot/kline/本脚本重影
5. MemAvailable≥2.5GiB；rss 帽=1500 禁抬
6. sampler 仅 `/tmp/quantlab_leaf27_chunked_ndays40_*`；禁 RESTORED/`lowmem_v1` 同 cmd；禁 `--window both`/FULLA
7. 单次；峰证明 REQUIRED；交回执；QUIET 听 Arch 规则，AI 勿擅 lift
8. ABORT → 停 + 另交 hist-prune 票；**禁静默切其它 mode**

## 静态自检（本回合已做；非授权）

```bash
sha256sum research/leaf27_chunked_members_mktcap_r1.py
# → 262f9bf6878d5c64956529a680abbf36e45adfe72fc7dedc4c68dc1c40291a10
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf27_chunked_members_mktcap_r1.py --dry-compile-only
# → live:false ok_requested:false rss_limit_mb:1500（本回合已跑；无实数加载）
```

live=false。
