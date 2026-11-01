# 主 · 叶25 全叶 HILIQ×x2 alpha 构建 MATCH+GO

| 项 | 值 |
|---|---|
| 角色 | 主 Agent |
| 时刻 | `2026-10-26T01:54:13-04:00`（America/New_York） |
| 窗令 | `12dc8e6d` **01:45–02:30 ET** expires **02:32** |
| 审阅 | `dd68765e` PASS_WITH_CONDITIONS |
| Arch SIGNED | `4166d9ef` @ `2026-10-26T01:50:19-04:00` |
| 结论 | **MATCH+GO** — 令 AI prelaunch 单次 PRIMARY（须 `--allow-real-data --arch-ok-path`） |

## 盘证 MATCH

| 项 | sha8 |
|---|---|
| `.ok` | `3c297052`（全长 `3c297052af27c24a…`；∉ forbid 十一票） |
| QUIET | `073fe7a4`（勿 lift；8795 应 quiet=true） |
| 脚本 | `de7b3647`（`research/leaf25_full_factor_alpha_build_r1.py`） |
| COVER / CMD / DIFF | `07b0a1b8` / `8ab8831c` / `03d50f3f` |
| HAND / VERIFY / H2A | `21bf0d41` / `d6750c94` / `2ac86676` |
| 审阅 / 窗令 / 签回执 | `dd68765e` / `12dc8e6d` / `4166d9ef` |
| MemAvailable@GO | ≈6.4Gi（签时≈4.4Gi；软地板已过；prelaunch 可开） |

## PRIMARY CLI（单次）

```
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf25_full_factor_alpha_build_r1.py --universe HILIQ --window x2 --x2-end 20261009 --chunk-mode month --out output/ai_factory/_leaf25_full_factor/<ET_TS>/ --allow-real-data --arch-ok-path output/ai_factory/ARCH_RUN_AUTH_LEAF25_FULL_FACTOR_ALPHA_BUILD_HILIQ_X2.ok
```

## 硬钉

- rss 软/硬帽 **1500** MB 禁抬；峰＞1500→停+上报；peak_proof **REQUIRED**
- sampler 前缀 `/tmp/quantlab_leaf25_full_alpha_*`
- **PIN_GAP** 披露：β120/mom/logADV20/vol20 未齐 → overall=PARTIAL；勿称全残差；CFACC TTM+desens 已实装
- ≠ X2 ACCEPT；≠ selfcheck；禁 Book-Smoke；禁 mem_probe 冒充 build；禁改脚本 `de7b3647`
- forbid 十一票：`1c32ab1e`+八票+`3c19dd7d`+`6054b3bf`（本 `.ok` `3c297052` 新签）
- FALLBACK **无**；完后交 RUN_RECEIPT（alpha/meta/peak + PIN_GAP 重述）
- Arch 不代跑不 lift；live=false

## 下一跳

AI RUNNING→DONE/ABORT → RUN_RECEIPT → Arch CONSUMED+lift → 主收口。**不推 Leo**（等 DONE/ABORT 再报）。
