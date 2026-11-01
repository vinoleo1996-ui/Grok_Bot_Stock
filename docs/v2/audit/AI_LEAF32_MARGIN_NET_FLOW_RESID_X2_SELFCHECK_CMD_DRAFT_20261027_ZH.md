# 叶32 Margin Net Flow Resid X2 selfcheck_v1 · CMD DRAFT（现不可跑）· P0 对齐叶31/30/25

- **时刻**：2026-10-27 05:02 ET（America/New_York；墙钟 2026-10-27 05:02 ET）
- **状态**：DRAFT · SELFCHECK_EXECUTED=false · 待新 `.ok` + 主签窗
- **脚本**：`research/leaf32_margin_net_flow_resid_x2_selfcheck_v1.py` sha8 **`dcf6b559`**
- **模板**：派生自叶31 `e1fe578c`（只读；勿改）；叶30 `797724d4` 只读
- **对齐**：叶31/30 P0 CMD → **去掉未实现 `--arch-ok-path`**（流程门由外挂 `.ok`+主窗，不进 CLI）

## approved_cmd_dry（本回合可静校；非实跑）

```
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf32_margin_net_flow_resid_x2_selfcheck_v1.py --universe HILIQ --window x2 --dry-compile-only
```

## 拟 approved_cmd（**现不可跑**；须新 `.ok` + 主签窗）

```
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf32_margin_net_flow_resid_x2_selfcheck_v1.py --universe HILIQ --window x2 --execute
```

### 可选显式钉盘（默认同 PIN；脚本已硬默认）

```
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf32_margin_net_flow_resid_x2_selfcheck_v1.py --universe HILIQ --window x2 --alpha-path output/ai_factory/_leaf32_margin_flow/20261027_042805/alpha_HILIQ_x2_20261027_044214.parquet --meta-path output/ai_factory/_leaf32_margin_flow/20261027_042805/run_meta.json --execute
```

## 硬声明

- **禁** `--arch-ok-path`（脚本未实现；流程门 = Arch 新 `.ok` + 主窗外挂，对齐叶25/30/31 P0）
- **禁实跑** / **禁申 `.ok`** / ≠X2 ACCEPT / live=false / EXECUTED=false
- `0087c928` 另队不夹带；≠Book-Smoke
- 盯 **decay KEEP**（三闸关键路径；叶30/31 均 DECAY_DOWNGRADE HOLD）

## 钉

- alpha `13eee6fd` / meta `e510f346` / overlap `a643d71a`
- 构建 `4e0f3c00` UNCHANGED；模板 `e1fe578c` UNCHANGED；叶30 `797724d4` UNCHANGED
- Arch CONSUME `a1a5e35a`；Alpha 闸 `1aa432a5`；AI RUN `f3e8f991`；RUNNING_ACK `3c4d0124`
- FROZEN `6b8de5e9`；mechanism=`g1g5_ashare_margin_net_flow_resid_v1`
- rss=1500 禁抬；peak_proof REQUIRED；nice=10（签文定）
- sampler `/tmp/quantlab_leaf32_x2_selfcheck_*`
- out weights：`output/ai_factory/_leaf32_margin_flow/20261027_042805/_selfcheck/`
- report：`output/ai_factory/leaf_reports/leaf32_margin_flow/selfcheck_v1.json`
- forbid∋`02426b73`+`4bb141c9`+`fdbaa512`+`aa25e989`+`7e239487`+`5af20222`+`5ae077fa`
- 拟 `.ok`：`output/ai_factory/ARCH_RUN_AUTH_LEAF32_MARGIN_NET_FLOW_RESID_X2_SELFCHECK_V1_HILIQ_X2.ok`（未创建）
- ≠重跑 alpha / ≠Book-Smoke / ≠X2 ACCEPT / live=false

## 预启动门（签窗后）

QUIET by Arch；healthz quiet；wait≥15s；pgrep data readers empty；MemAvailable soft-floor；script_sha MATCH；dry-compile PASS；禁无 `.ok` 自跑。
