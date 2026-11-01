# 叶27 X2 selfcheck_v2 · HILIQ×x2 CMD 草案（**未申 `.ok`** · 独立票）

- **角色**：QuantLab AI（执行器）
- **时刻**：2026-10-26T00:35:00-04:00（America/New_York；墙钟 2026-10-26 00:35 ET）
- **状态**：**DRAFT ONLY · HOLD_UNTIL_MAIN_SUBMIT** · **ok_requested=false** · **不是 `.ok`** · **不替代 Arch 签发** · **禁自开跑**
- **对照**：alpha `652b8a68` / meta `85c2dc78` / summary `80596bff`；脚本（新）`a40d7069`；构建脚本 UNCHANGED `585ba746`；Arch CONSUMED `78557480`；AI `1671eec4`；forbid **八**票含 `0f50daf7`
- **PRIMARY ONLY**：钉既有 alpha → 评价权重 → selfcheck_v2；**无** fallback；**无** Book-Smoke；**无** 复跑 baseline_evac

## 明确声明

> **本文件未申请、未获得、不构成任何 run/probe `.ok`。**  
> 在 Arch 另审 PASS、主排**新窗**并签发**新** `.ok` 之前，**禁止**执行下方 CLI。  
> **禁止** RESTORED 任何 VOID/CONSUMED `.ok`（含 **`0f50daf7`** 与七旧票）。  
> **禁止**把 baseline_evac CONSUMED_PASS 当作 X2 ACCEPT。  
> 失败 → **停 + 上报**；下一跳须主/Arch 另令。

## PRIMARY CLI（待新 `.ok` 钉入；现不可跑 · 唯一阶）

```bash
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf27_x2_selfcheck_v2.py --universe HILIQ --window x2 --alpha-path output/ai_factory/leaf27_on_minus_id_idio_ivol/alpha_HILIQ_x2_20261025_224033.parquet --execute
```

## 无 FALLBACK（本票硬钉）

- **无**同票第二阶 CLI。
- 失败/异常 → **停 + 写回执上报**；**禁静默 fallback**；**禁抬帽**；下一策略须主/Arch 另票另签。

## 硬钉（未来 `.ok` 必须逐字对齐）

| 项 | 值 |
|---|---|
| script | `research/leaf27_x2_selfcheck_v2.py` |
| script sha256 | `a40d7069374bb940863b8af6e3e103a07aa6c82f10c9cf389f53c76c57edddc0`（sha8 **`a40d7069`**） |
| alpha | `…/alpha_HILIQ_x2_20261025_224033.parquet` sha `652b8a68b28871ddc1cbf623834650c23c79c8a81235fabc578ede71f17cf1b1` |
| meta | `…/run_meta_HILIQ_x2_20261025_224033.json` sha `85c2dc7897c2796e36357042d8521e8b4b91beec8f2cd43bf18c31bdf48d4068` |
| summary | `…/build_summary_20261025_224333.json` sha `80596bffb7de1296f6859f3e7bf1afa5c73ef2ec79a579bb365061cba8579cd6` |
| universe / window | `HILIQ` / `x2` |
| 权重落盘 | `output/ai_factory/leaf27_on_minus_id_idio_ivol/_selfcheck/eval_weights_HILIQ_x2_<stamp>.parquet` |
| 报告 | `output/ai_factory/leaf_reports/leaf27_on_minus_id_idio_ivol/selfcheck_v2.json` |
| rss 软帽 | **1500** MB（禁抬；软披露） |
| sampler（若需要） | 仅 `/tmp/quantlab_leaf27_x2_selfcheck_*` |
| 禁复用 `.ok` | **八票**：`e107383f` · `2be59acd` · `a7d98ac9` · `8e51de63` · `3a6caa4f` · `8bcd79dc` · `725be3e0` · **`0f50daf7`** |
| 构建脚本 | `585ba746` **UNCHANGED**（禁改） |
| live / promotion / Book-Smoke / X2 ACCEPT | 全 false |

## Prelaunch 清单（未来主令开跑时；**现不做**）

1. 新 `.ok` 盘证 MATCH（≠ 八票任一）；CLI 逐字 = PRIMARY
2. script sha256 MATCH `a40d7069374bb940863b8af6e3e103a07aa6c82f10c9cf389f53c76c57edddc0`；`--dry-compile-only` → `live:false` `ok_requested:false` `selfcheck_executed:false` `rss_soft_mb:1500`；pin 三件 MATCH；forbid 含 `0f50daf7`
3. healthz：按既定 SOP `ok=true`；若挂 QUIET 听 Arch 规则，AI 勿擅 lift
4. wait≥15s；`pgrep -f 'kline.py|export_static.py|snapshot.py|gen.py'` **必须空**；无本脚本重影
5. MemAvailable 听主软地板；rss 软帽=1500 禁抬
6. sampler 仅 `/tmp/quantlab_leaf27_x2_selfcheck_*`（若启用）；禁 RESTORED；禁 Book-Smoke
7. 单次；交回执（权重 sha + selfcheck_v2.json sha + peak rss）
8. 失败 → **停 + 上报**；禁静默切参数

## 静态自检（本回合已做；非授权）

```bash
sha256sum research/leaf27_x2_selfcheck_v2.py
# → a40d7069374bb940863b8af6e3e103a07aa6c82f10c9cf389f53c76c57edddc0
python3 -c "import py_compile;py_compile.compile('research/leaf27_x2_selfcheck_v2.py',cfile='/tmp/leaf27_x2_selfcheck_v2.pyc',doraise=True)"
# → OK
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf27_x2_selfcheck_v2.py --dry-compile-only
# → live:false ok_requested:false selfcheck_executed:false rss_soft_mb:1500 pin_sha_match:true；forbid 八票；无实数 evaluate
/tmp/ql_pyflakes_venv/bin/pyflakes research/leaf27_x2_selfcheck_v2.py
# → exit 0
```

live=false · ok_requested=false · ≠X2 · SELFCHECK_EXECUTED=false
