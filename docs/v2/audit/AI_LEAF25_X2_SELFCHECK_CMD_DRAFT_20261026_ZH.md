# 叶25 X2 selfcheck_v2 · HILIQ×x2 CMD 草案（**未申 `.ok`** · 独立票）

- **角色**：QuantLab AI（执行器）
- **时刻**：2026-10-26T13:35:00-04:00（America/New_York；墙钟 2026-10-26 13:35 ET）
- **状态**：**DRAFT ONLY · HOLD_UNTIL_MAIN_SUBMIT** · **ok_requested=false** · **不是 `.ok`** · **不替代 Arch 签发** · **禁自开跑**
- **对照**：alpha `8be12024` / meta `44c27f54`；脚本（新）`b1db0886`；构建脚本 UNCHANGED `de7b3647`；Arch CONSUMED `fb19ac28`；AI `b8c0b050`；forbid **十二**票含 `3c297052`
- **PRIMARY ONLY**：钉既有 alpha → 评价权重 → selfcheck_v2；**无** fallback；**无** Book-Smoke；**无** 复跑 alpha 构建
- **PIN_GAP PARTIAL**：β120/mom/logADV20/vol20；CFACC TTM+desens 已实装；**勿称全残差齐**

## 明确声明

> **本文件未申请、未获得、不构成任何 run/probe `.ok`。**  
> 在 Arch 另审 PASS、主排**新窗**并签发**新** `.ok` 之前，**禁止**执行下方 CLI。  
> **禁止** RESTORED 任何 VOID/CONSUMED `.ok`（含 **`3c297052`** 与十一旧票）。  
> **禁止**把全叶 alpha CONSUMED_PASS 当作 X2 ACCEPT。  
> 失败 → **停 + 上报**；下一跳须主/Arch 另令。

## PRIMARY CLI（待新 `.ok` 钉入；现不可跑 · 唯一阶）

```bash
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf25_x2_selfcheck_v2.py --universe HILIQ --window x2 --alpha-path output/ai_factory/_leaf25_full_factor/20261026_015610/alpha_HILIQ_x2_20261026_125138.parquet --execute
```

## 无 FALLBACK（本票硬钉）

- **无**同票第二阶 CLI。
- 失败/异常 → **停 + 写回执上报**；**禁静默 fallback**；**禁抬帽**；下一策略须主/Arch 另票另签。

## 硬钉（未来 `.ok` 必须逐字对齐）

| 项 | 值 |
|---|---|
| script | `research/leaf25_x2_selfcheck_v2.py` |
| script sha256 | `b1db0886ddcc7e6e9686bbfc0cf0f7d061001eaea157b8ce27152bcc6314b0c3`（sha8 **`b1db0886`**） |
| alpha | `output/ai_factory/_leaf25_full_factor/20261026_015610/alpha_HILIQ_x2_20261026_125138.parquet` sha `8be12024f57fc85833d99e44f94f5c2916b1aaab64f037eed223f0fc61792393` |
| meta | `output/ai_factory/_leaf25_full_factor/20261026_015610/run_meta.json` sha `44c27f5467420861b2c28a6b0311674c06b69fe8d051fbc256ce31cd7bc7d7e9` |
| universe / window | `HILIQ` / `x2` |
| 权重落盘 | `output/ai_factory/_leaf25_full_factor/20261026_015610/_selfcheck/eval_weights_HILIQ_x2_<stamp>.parquet` |
| 报告 | `output/ai_factory/leaf_reports/leaf25_full_factor/selfcheck_v2.json` |
| rss 软/硬帽 | **1500** MB（禁抬；硬 ABORT）+ peak_proof REQUIRED |
| sampler | 仅 `/tmp/quantlab_leaf25_x2_selfcheck_*` |
| 拟 `.ok`（未创建） | `output/ai_factory/ARCH_RUN_AUTH_LEAF25_X2_SELFCHECK_V2_HILIQ_X2.ok` |
| 禁复用 `.ok` | **十二票**：`e107383f` / `2be59acd` / `a7d98ac9` / `8e51de63` / `3a6caa4f` / `8bcd79dc` / `725be3e0` / `0f50daf7` / `3c19dd7d` / `1c32ab1e` / `6054b3bf` / **`3c297052`** |
| 构建脚本 | `de7b3647` **UNCHANGED**（禁改） |
| PIN_GAP | PARTIAL · β120/mom/logADV20/vol20；CFACC 已实装；勿称全残差齐 |
| Gate | decay + portfolio A/B/current（`leaf_selfcheck_common.evaluate`） |
| live / promotion / Book-Smoke / X2 ACCEPT | 全 false |

## Prelaunch 清单（未来主令开跑时；**现不做**）

1. 新 `.ok` 盘证 MATCH（≠ 十二票任一；拟名 `output/ai_factory/ARCH_RUN_AUTH_LEAF25_X2_SELFCHECK_V2_HILIQ_X2.ok`）；CLI 逐字 = PRIMARY
2. script sha256 MATCH `b1db0886ddcc7e6e9686bbfc0cf0f7d061001eaea157b8ce27152bcc6314b0c3`；`--dry-compile-only` → `live:false` `ok_requested:false` `selfcheck_executed:false` `rss_soft_mb:1500` `rss_hard_mb:1500`；pin 两件 MATCH；forbid 含 `3c297052`；`pin_gap.overall=PARTIAL`
3. healthz：按既定 SOP `ok=true`；若挂 QUIET 听 Arch 规则，AI 勿擅 lift
4. wait≥15s；`pgrep -f 'kline.py|export_static.py|snapshot.py|gen.py'` **必须空**；无本脚本重影
5. MemAvailable 听主软地板；rss 软/硬帽=1500 禁抬；peak_proof REQUIRED
6. sampler 仅 `/tmp/quantlab_leaf25_x2_selfcheck_*`（若启用）；禁 RESTORED；禁 Book-Smoke
7. 单次；交回执（权重 sha + selfcheck_v2.json sha + peak rss + **PIN_GAP PARTIAL 复述**）
8. 失败 → **停 + 上报**；禁静默切参数

## 静态自检（本回合已做；非授权）

```bash
sha256sum research/leaf25_x2_selfcheck_v2.py
# → b1db0886ddcc7e6e9686bbfc0cf0f7d061001eaea157b8ce27152bcc6314b0c3
python3 -c "import py_compile;py_compile.compile('research/leaf25_x2_selfcheck_v2.py',cfile='/tmp/leaf25_x2_selfcheck_v2.pyc',doraise=True)"
# → OK
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf25_x2_selfcheck_v2.py --dry-compile-only
# → live:false ok_requested:false selfcheck_executed:false rss_soft_mb:1500 rss_hard_mb:1500 pin_sha_match:true；forbid 十二票含 3c297052；pin_gap PARTIAL；无实数 evaluate
/tmp/pyflakes_venv/bin/pyflakes research/leaf25_x2_selfcheck_v2.py
# → exit 0
```

live=false · ok_requested=false · ≠X2 · SELFCHECK_EXECUTED=false · PIN_GAP=PARTIAL
