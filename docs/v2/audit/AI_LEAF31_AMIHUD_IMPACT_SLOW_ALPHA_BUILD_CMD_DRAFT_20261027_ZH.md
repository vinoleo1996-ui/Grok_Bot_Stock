# 叶31 Amihud 冲击慢 α · CMD DRAFT（现不可跑）

- **时刻**：2026-10-27 02:26 ET（America/New_York；ISO 2026-10-27T02:26:17-0400）
- **状态**：DRAFT · EXECUTED=false · 待 Arch 审脚本 → 新 `.ok` + 主签窗
- **脚本**：`research/leaf31_amihud_impact_slow_alpha_build.py` sha8 **`08f37fd2`**
- **对齐**：Arch FROZEN **`7a6a1e1a` PASS_WITH_CONDITIONS**；FROZEN **`bcbec955`**；流程门 = 外挂新 `.ok` + 主窗
- **CLI 说明**：脚本**已实现** `--arch-ok-path`（对齐叶30 **build**；真跑须现存文件且 sha8∉forbid）。拟 approved_cmd **含**该 flag（指向**未来新** `.ok`，禁 RESTORED 四票）。**禁**用未签发路径自开。

## approved_cmd_dry（本回合可静校；非实跑）

```
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf31_amihud_impact_slow_alpha_build.py --dry-compile-only
```

## 拟 approved_cmd（**现不可跑**；须新 `.ok` + 主签窗）

```
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf31_amihud_impact_slow_alpha_build.py --universe HILIQ --window x2 --x2-end 20261009 --allow-real-data --arch-ok-path output/ai_factory/ARCH_RUN_AUTH_LEAF31_AMIHUD_IMPACT_SLOW_X2_HILIQ.ok --out output/ai_factory/_leaf31_amihud/<STAMP>
```

### 可选

- `--also-fulla-research`：额外写 FULLA 研究 α（**不得**作 PRIMARY 判决）
- 显式 `--leaf19-alpha` / `--leaf25-alpha` / `--leaf27-alpha` / `--leaf30-alpha` 钉重叠对照盘
- `--sample-dir /tmp/quantlab_leaf31_amihud_<tag>`（须此前缀）

## 硬声明

- 流程门 = Arch **新** `.ok` + 主窗外挂；`--arch-ok-path` 仅校验现存授权文件（sha8 not in forbid），**不**自造 `.ok`
- **禁实跑** / **禁申 `.ok`** / **禁挂 QUIET** / ≠X2 ACCEPT / live=false
- forbid∋`aa25e989`+`7e239487`+`5af20222`+`5ae077fa`
- rss=1500 禁抬；peak_proof REQUIRED（`after_mask` / `after_bars_rebal_*` / `after_logmv_rebal_*` / `after_daily_concat`）
- Jaccard≥0.7 vs 叶19/25/27/30 → 硬拒（exit≠0）；ρ>0.5 强度过滤披露
- `0087c928` 另队不并入；≠Book-Smoke；≠重跑叶30

## 钉

| 项 | 值 |
|---|---|
| script | `08f37fd2` |
| FROZEN / ArchFROZEN | `bcbec955` / `7a6a1e1a` |
| mechanism | `g1g5_ashare_amihud_impact_slow_v1` |
| W / rebal / α | 20 / 20 / −rank |
| sampler | `/tmp/quantlab_leaf31_amihud_*` |
| out | `output/ai_factory/_leaf31_amihud/` |
| overlap | `overlap_vs_leaf19_25_27_30.json` |

## 预启动门（签窗后）

QUIET by Arch（若要求）；healthz；wait≥15s；`pgrep` data readers empty；MemAvailable soft-floor；script_sha MATCH `08f37fd2`；dry-compile PASS；禁 RESTORED 四票；禁抬 rss。

live=false · EXECUTED=false · ok_requested=false · leo_notify=false
