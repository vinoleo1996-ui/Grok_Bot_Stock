# 叶31 Amihud Impact Slow X2 selfcheck_v1 · CMD DRAFT（现不可跑）· P0 对齐叶30/叶25

- **时刻**：2026-10-27 02:59 ET（America/New_York；墙钟 2026-10-27 02:59 ET）
- **状态**：DRAFT · SELFCHECK_EXECUTED=false · 待新 `.ok` + 主签窗
- **脚本**：`research/leaf31_amihud_impact_slow_x2_selfcheck_v1.py` sha8 **`e1fe578c`**
- **模板**：派生自叶30 `797724d4`（只读；勿改）
- **对齐**：叶30 P0 CMD（`c25f1321` 形态）→ **去掉未实现 `--arch-ok-path`**（流程门由外挂 `.ok`+主窗，不进 CLI）

## approved_cmd_dry（本回合可静校；非实跑）

```
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf31_amihud_impact_slow_x2_selfcheck_v1.py --universe HILIQ --window x2 --dry-compile-only
```

## 拟 approved_cmd（**现不可跑**；须新 `.ok` + 主签窗）

```
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf31_amihud_impact_slow_x2_selfcheck_v1.py --universe HILIQ --window x2 --execute
```

### 可选显式钉盘（默认同 PIN；脚本已硬默认）

```
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf31_amihud_impact_slow_x2_selfcheck_v1.py --universe HILIQ --window x2 --alpha-path output/ai_factory/_leaf31_amihud/20261027_024204/alpha_HILIQ_x2_20261027_024422.parquet --meta-path output/ai_factory/_leaf31_amihud/20261027_024204/run_meta.json --execute
```

## 硬声明

- **禁** `--arch-ok-path`（脚本未实现；流程门 = Arch 新 `.ok` + 主窗外挂，对齐叶25/30 P0）
- **禁实跑** / **禁申 `.ok`** / ≠X2 ACCEPT / live=false / EXECUTED=false
- `0087c928` 另队不夹带；≠Book-Smoke

## 钉

- alpha `d4ceb78b` / meta `696ab1cc` / overlap `8396f211`
- 构建 `08f37fd2` UNCHANGED；模板 `797724d4` UNCHANGED
- Arch CONSUME `7bd6f33a`；Alpha 闸 `a476567d`；AI RUN `49d6641c`
- mechanism=`g1g5_ashare_amihud_impact_slow_v1`
- rss=1500 禁抬；peak_proof REQUIRED；nice=10（签文定）
- sampler `/tmp/quantlab_leaf31_x2_selfcheck_*`
- out weights：`output/ai_factory/_leaf31_amihud/20261027_024204/_selfcheck/`
- report：`output/ai_factory/leaf_reports/leaf31_amihud/selfcheck_v1.json`
- forbid∋`fdbaa512`+`aa25e989`+`7e239487`+`5af20222`+`5ae077fa`
- 拟 `.ok`：`output/ai_factory/ARCH_RUN_AUTH_LEAF31_AMIHUD_IMPACT_SLOW_X2_SELFCHECK_V1_HILIQ_X2.ok`（未创建）
- ≠重跑 alpha / ≠Book-Smoke / ≠X2 ACCEPT / live=false

## 预启动门（签窗后）

QUIET by Arch；healthz quiet；wait≥15s；pgrep data readers empty；MemAvailable soft-floor；script_sha MATCH；dry-compile PASS；禁无 `.ok` 自跑。
