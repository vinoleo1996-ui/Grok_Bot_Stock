# 叶30 CRR X2 selfcheck_v1 · CMD DRAFT（现不可跑）· P0 对齐 Arch `3826aa63`

- **时刻**：2026-10-27 01:38 ET（America/New_York；墙钟 2026-10-27 01:38 ET）
- **状态**：DRAFT · SELFCHECK_EXECUTED=false · 待新 `.ok` + 主签窗
- **脚本**：`research/leaf30_crr_x2_selfcheck_v1.py` sha8 **`797724d4`**（**UNCHANGED**；禁改）
- **对齐**：Arch 只审 **PASS_WITH_CONDITIONS** `3826aa63` → **去掉未实现 `--arch-ok-path`**（对齐叶25：流程门由外挂 `.ok`+主窗，不进 CLI）
- **旧 CMD** `37ea30a5` **作废**（含 `--arch-ok-path`）

## approved_cmd_dry（本回合可静校；非实跑）

```
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf30_crr_x2_selfcheck_v1.py --universe HILIQ --window x2 --dry-compile-only
```

## 拟 approved_cmd（**现不可跑**；须新 `.ok` + 主签窗）

```
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf30_crr_x2_selfcheck_v1.py --universe HILIQ --window x2 --execute
```

### 可选显式钉盘（默认同 PIN；脚本已硬默认）

```
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf30_crr_x2_selfcheck_v1.py --universe HILIQ --window x2 --alpha-path output/ai_factory/_leaf30_crr/20261027_003132/alpha_HILIQ_x2_20261027_010815.parquet --meta-path output/ai_factory/_leaf30_crr/20261027_003132/run_meta.json --execute
```

## 硬声明

- **禁** `--arch-ok-path`（脚本未实现；流程门 = Arch 新 `.ok` + 主窗外挂，对齐叶25）
- 脚本 **`797724d4` 勿改**
- **禁实跑** / **禁申 `.ok`** / ≠X2 ACCEPT / live=false

## 钉

- alpha `c8c7a5a5` / meta `a6acfe27` / overlap `f9991d9d`
- 构建 `3ee9fed2` UNCHANGED
- rss=1500 禁抬；peak_proof REQUIRED；nice=10（签文定）
- sampler `/tmp/quantlab_leaf30_x2_selfcheck_*`
- out weights：`output/ai_factory/_leaf30_crr/20261027_003132/_selfcheck/`
- report：`output/ai_factory/leaf_reports/leaf30_crr/selfcheck_v1.json`
- forbid∋`7e239487`+`5af20222`+`5ae077fa`
- ≠重跑 alpha / ≠Book-Smoke / ≠X2 ACCEPT / live=false

## 预启动门（签窗后）

QUIET by Arch；healthz quiet；wait≥15s；pgrep data readers empty；MemAvailable soft-floor；script_sha MATCH `797724d4`；dry-compile PASS；禁无 `.ok` 自跑。
