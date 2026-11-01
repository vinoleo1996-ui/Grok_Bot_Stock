# 叶37 IMAX/隔夜彩票剔除 Overlay X2 selfcheck_v1 · CMD DRAFT（现不可跑）· P0 对齐叶34/32/25

- **时刻**：2026-10-27 18:58 ET（America/New_York；墙钟 2026-10-27 18:58 ET）
- **状态**：DRAFT · SELFCHECK_EXECUTED=false · 待新 `.ok` + 主签窗
- **脚本**：`research/leaf37_imax_lottery_exclusion_overlay_x2_selfcheck_v1.py` sha8 **`015e6f06`**
- **模板**：派生自叶34 `d210efba`（只读；勿改）；叶32 `dcf6b559` 只读；`leaf_selfcheck_common.py` `218b61cf` 只读
- **对齐**：叶34/32 P0 CMD → **去掉未实现 `--arch-ok-path`**（流程门由外挂 `.ok`+主窗，不进 CLI）

## approved_cmd_dry（本回合可静校；非实跑）

```
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf37_imax_lottery_exclusion_overlay_x2_selfcheck_v1.py --dry-compile-only
```

（等价显式：`--universe HILIQ --window x2 --dry-compile-only`）

## 拟 approved_cmd（**现不可跑**；须新 `.ok` + 主签窗）

```
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf37_imax_lottery_exclusion_overlay_x2_selfcheck_v1.py --universe HILIQ --window x2 --execute
```

### 可选显式钉盘（默认同 PIN；脚本已硬默认）

```
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf37_imax_lottery_exclusion_overlay_x2_selfcheck_v1.py --universe HILIQ --window x2 --mask-path output/ai_factory/_leaf37_imax_lottery/20261027_183719/exclusion_mask_HILIQ_x2_20261027_183755.parquet --meta-path output/ai_factory/_leaf37_imax_lottery/20261027_183719/run_meta.json --execute
```

## 硬声明

- **禁** `--arch-ok-path`（脚本未实现；流程门 = Arch 新 `.ok` + 主窗外挂，对齐叶34/32/25 P0）
- **禁实跑** / **禁申 `.ok`** / ≠X2 ACCEPT / live=false / EXECUTED=false
- `0087c928`/叶28/29 另队不夹带；≠Book-Smoke
- **KEEP 不解阻 X2 ACCEPT**（叶32 HOLD `45dd87dc`；叶36 HOLD 不复开）
- PRIMARY=**mask-only** top_q=**0.20**；C3=**B** IMAX_proxy；b1_lowmem=**true**；soft-penalty **非 PRIMARY**；禁静默 FULLA
- B1 `32605aca` UNCHANGED；基盘 `108aba8f` ban_as_live（禁跑）

## 钉

- mask `2503a41e` / meta `e9e9aa1d` / overlap `8177578f`
- B1 `32605aca` UNCHANGED；基盘 `108aba8f` UNCHANGED ban_as_live；模板 `d210efba`/`dcf6b559`/`218b61cf` UNCHANGED
- Arch CONSUME `c0a6b5ae`；consumed `.ok` `b5be1164`（ABSENT；禁 RESTORED）；VOID `4096d401`
- AI RUN `c6d8b1ce`；RUNNING_ACK `08652c66`；SIGNED `7b3bd298`；审 `b403a7e5`；VOID回执 `998171e1`
- FROZEN `c5927f1b`；PIN `e01be34c`；mechanism=`g1g5_ashare_imax_lottery_exclusion_overlay_v1`
- CAP_ADV=`output/ai_factory/g1g5_capacity_adv_daily_weights_20261013_111219.parquet`
- rss=1500 禁抬；peak_proof REQUIRED；sampler `/tmp/quantlab_leaf37_x2_selfcheck_*`
- coverage_gate≥300（meta coverage_median=2816.5）；peak_kb=1107536
- out weights：`output/ai_factory/_leaf37_imax_lottery/20261027_183719/_selfcheck/`
- report：`output/ai_factory/leaf_reports/leaf37_imax_lottery/selfcheck_v1.json`
- forbid∋`b5be1164`+`4096d401`+`eb70eef4`+`00eec671`+`10927bd9`+`25ae4572`+`178e90e9`+`c1b71e64`+…（n=32）
- 拟 `.ok`：`output/ai_factory/ARCH_RUN_AUTH_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_X2_SELFCHECK_V1_HILIQ_X2.ok`（未创建）
- ≠重跑 B1/基盘 / ≠Book-Smoke / ≠X2 ACCEPT / live=false
- 叶33 `afbbe7e7` / 叶35 `434ff42c` / 叶34 `482009dc` UNCHANGED；叶36 HOLD 不复开；C11≠叶24

## 预启动门（签窗后）

QUIET by Arch；healthz quiet；wait≥15s；pgrep data readers empty；MemAvailable soft-floor；script_sha MATCH；dry-compile PASS；禁用 `.ok` 自跑。
