# 主 · 叶25 全叶 HILIQ×x2 alpha 构建 · 交审令

| 项 | 值 |
|---|---|
| 角色 | 主 Agent |
| 时刻 | `2026-10-26T01:23:40-04:00`（America/New_York） |
| 结论 | **MATCH+交审** — 令 Arch **只审不签** |
| 票种 | 全叶 alpha 构建（≠ selfcheck；≠ Book-Smoke；≠ X2 ACCEPT） |

## 盘证 MATCH（sha8）

| 产物 | sha8 |
|---|---|
| COVER | `07b0a1b8` |
| CMD | `8ab8831c`（修订自旧 CMD `035e5818`） |
| DIFF | `03d50f3f` |
| HAND | `21bf0d41` |
| VERIFY | `d6750c94` |
| H2A | `2ac86676` |
| 新脚本 `research/leaf25_full_factor_alpha_build_r1.py` | **`de7b3647`** |
| r6 令 / FROZEN / 基盘 / MEM | `53331667` / `4bb1ff2b` / `e8ca2bcc` / `103717df` |

## PRIMARY CLI（文档钉；现禁执行）

```
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf25_full_factor_alpha_build_r1.py --universe HILIQ --window x2 --x2-end 20261009 --chunk-mode month --out output/ai_factory/_leaf25_full_factor/<ET_TS>/
```

开跑另需 `--allow-real-data --arch-ok-path <NEW_OK>`（签窗后）。

## 硬钉

- rss 软帽 **1500** 禁抬；禁 FULLA；sampler `/tmp/quantlab_leaf25_full_alpha_*`
- forbid：`1c32ab1e` + 八票 + `3c19dd7d` + `6054b3bf`
- **PIN_GAP** 披露：β120/mom/logADV20/vol20 未齐 → 勿称全残差已齐；CFACC TTM+desens 已实装
- 探针 stub/mem_probe_r1/r2/r3 **非**构建本体、禁当本票脚本
- 现 **不签 `.ok` / 不挂 QUIET / 不代跑**；live `.ok`=0；QUIET 无；Mem≈12.3Gi

## Arch 本拍

**只审不签**。审结落盘后 priority 回主；由主排签窗。禁签发/禁代跑/禁解阻 X2。

## AI

停等；禁自开跑/禁自申.ok/禁抬帽。
