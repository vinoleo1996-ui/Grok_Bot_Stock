# 叶34 High Accrual Exclusion Overlay X2 selfcheck_v1 · CMD DRAFT（现不可跑）· P0 对齐叶32/31/30/25

- **时刻**：2026-10-27 11:16 ET（America/New_York；墙钟 2026-10-27 11:16 ET）
- **状态**：DRAFT · SELFCHECK_EXECUTED=false · 待新 `.ok` + 主签窗
- **脚本**：`research/leaf34_high_accrual_exclusion_overlay_x2_selfcheck_v1.py` sha8 **`d210efba`**
- **模板**：派生自叶32 `dcf6b559`（只读；勿改）；叶31 `e1fe578c` 只读；`leaf_selfcheck_common.py` `218b61cf` 只读
- **对齐**：叶32/31/30 P0 CMD → **去掉未实现 `--arch-ok-path`**（流程门由外挂 `.ok`+主窗，不进 CLI）

## approved_cmd_dry（本回合可静校；非实跑）

```
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf34_high_accrual_exclusion_overlay_x2_selfcheck_v1.py --dry-compile-only
```

（等价显式：`--universe HILIQ --window x2 --dry-compile-only`）

## 拟 approved_cmd（**现不可跑**；须新 `.ok` + 主签窗）

```
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf34_high_accrual_exclusion_overlay_x2_selfcheck_v1.py --universe HILIQ --window x2 --execute
```

### 可选显式钉盘（默认同 PIN；脚本已硬默认）

```
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf34_high_accrual_exclusion_overlay_x2_selfcheck_v1.py --universe HILIQ --window x2 --mask-path output/ai_factory/_leaf34_high_accrual/20261027_105941/exclusion_mask_HILIQ_x2_20261027_105958.parquet --meta-path output/ai_factory/_leaf34_high_accrual/20261027_105941/run_meta.json --execute
```

## 硬声明

- **禁** `--arch-ok-path`（脚本未实现；流程门 = Arch 新 `.ok` + 主窗外挂，对齐叶25/30/31/32 P0）
- **禁实跑** / **禁申 `.ok`** / ≠X2 ACCEPT / live=false / EXECUTED=false
- `0087c928`/叶28/29 另队不夹带；≠Book-Smoke
- **KEEP 不解阻 X2 ACCEPT**（叶32 HOLD `45dd87dc`）
- PRIMARY=**mask-only** top_q=**0.20**；soft-penalty **非 PRIMARY**；禁静默 FULLA

## 钉

- mask `8b5d6d24` / meta `4fc6108d` / overlap `77368c8f`
- 构建 `482009dc` UNCHANGED；模板 `dcf6b559`/`e1fe578c`/`218b61cf` UNCHANGED
- Arch CONSUME `fea9b3ff`；consumed `.ok` `c1b71e64`（ABSENT；禁 RESTORED）
- AI RUN `1441a7ec`；RUNNING_ACK `c03d2f16`
- FROZEN `8be1099e`；PIN `bb418e6a`；mechanism=`g1g5_ashare_high_accrual_exclusion_overlay_v1`
- CAP_ADV=`output/ai_factory/g1g5_capacity_adv_daily_weights_20261013_111219.parquet`
- rss=1500 禁抬；peak_proof REQUIRED；sampler `/tmp/quantlab_leaf34_x2_selfcheck_*`
- out weights：`output/ai_factory/_leaf34_high_accrual/20261027_105941/_selfcheck/`
- report：`output/ai_factory/leaf_reports/leaf34_high_accrual/selfcheck_v1.json`
- forbid∋`c1b71e64`+`245df63f`+`c5ed13df`+`5774bb6e`+二十票(+`81521fb5`)
- 拟 `.ok`：`output/ai_factory/ARCH_RUN_AUTH_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_X2_SELFCHECK_V1_HILIQ_X2.ok`（未创建）
- ≠重跑构建 / ≠Book-Smoke / ≠X2 ACCEPT / live=false
- 叶33 `afbbe7e7` UNCHANGED；叶32 HOLD `45dd87dc` 不回撤

## 预启动门（签窗后）

QUIET by Arch；healthz quiet；wait≥15s；pgrep data readers empty；MemAvailable soft-floor；script_sha MATCH；dry-compile PASS；禁用 `.ok` 自跑。
