# 叶34 高应计剔除 overlay · CMD DRAFT（现不可跑）

- **时刻**：2026-10-27 10:29 ET（America/New_York；ISO 2026-10-27T10:29:55-04:00）
- **状态**：DRAFT · EXECUTED=false · 待 Arch 审脚本 → 新 `.ok` + 主签窗
- **脚本**：`research/leaf34_high_accrual_exclusion_overlay_alpha_build.py` sha8 **`482009dc`**
- **对齐**：Arch FROZEN **`027efa26` PASS_WITH_CONDITIONS**；FROZEN **`8be1099e`**；PIN **`bb418e6a`**；流程门 = 外挂新 `.ok` + 主窗
- **CLI 说明**：脚本**已实现** `--arch-ok-path`（对齐叶32/33 build；真跑须现存文件且 sha8∉forbid）。拟 approved_cmd **含**该 flag（指向**未来新** `.ok`，禁 RESTORED）。**禁**用未签发路径自开。

## approved_cmd_dry（本回合可静校；非实跑）

```
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf34_high_accrual_exclusion_overlay_alpha_build.py --dry-compile-only
```

## 拟 approved_cmd（**现不可跑**；须新 `.ok` + 主签窗）

```
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf34_high_accrual_exclusion_overlay_alpha_build.py --universe HILIQ --window x2 --x2-end 20261009 --allow-real-data --arch-ok-path output/ai_factory/ARCH_RUN_AUTH_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_X2_HILIQ.ok --out output/ai_factory/_leaf34_high_accrual/<STAMP>
```

### 可选

- `--also-fulla-research`：额外写 FULLA 研究 mask（**不得**作 PRIMARY 判决）
- `--enable-soft-penalty`：连续 soft-penalty（**非 PRIMARY**；须 SW+style；缺列 PIN_GAP）
- 显式 `--leaf19-alpha` … `--leaf33-alpha` 钉重叠对照盘
- `--sample-dir /tmp/quantlab_leaf34_high_accrual_<tag>`（须此前缀）
- **禁**真跑路径用 `--no-overlap-report` 绕过 C7（脚本硬 STOP）
- **禁** `--universe FULLA` 作 PRIMARY（dry/真跑均 STOP）

## 硬声明

- 流程门 = Arch **新** `.ok` + 主窗外挂；`--arch-ok-path` 仅校验现存授权文件（sha8 not in forbid），**不**自造 `.ok`
- **禁实跑** / **禁申 `.ok`** / **禁挂 QUIET** / ≠X2 ACCEPT / live=false
- forbid∋`245df63f+c5ed13df+5774bb6e+02426b73+4bb141c9+fdbaa512+aa25e989+7e239487+5af20222+5ae077fa+3c297052+e107383f+2be59acd+a7d98ac9+8e51de63+3a6caa4f+8bcd79dc+725be3e0+0f50daf7+3c19dd7d+1c32ab1e+6054b3bf+6de02e74+81521fb5`
- rss=1500 禁抬；peak_proof REQUIRED（`after_mask` / `after_ocf_rebal_*` / `after_mask_cs_rebal_*` / `after_daily_concat`）
- Jaccard≥0.7 vs 叶19/25/27/30/31/32/33 → 硬拒（exit≠0）；ρ>0.5 强度过滤披露；缺文件→PIN_GAP；须披露叶25 尾窗 n_common + ρ_max
- PRIMARY=mask-only top_q=0.20；C3 PIN `bb418e6a`；禁 BS WC PRIMARY；禁 CFACC TopN 主 α
- KEEP 三闸仅钉；**KEEP 不解阻** X2 ACCEPT（叶32 `45dd87dc`）；COUNT APPROX ≠ ACCEPT
- `0087c928`/叶28/29 另队不并入；叶33 `afbbe7e7` UNCHANGED；≠Book-Smoke

## 钉

| 项 | 值 |
|---|---|
| script | `482009dc` |
| FROZEN / PIN / ArchFROZEN | `8be1099e` / `bb418e6a` / `027efa26` |
| mechanism | `g1g5_ashare_high_accrual_exclusion_overlay_v1` |
| top_q / delivery / rebal | 0.20 / mask-only / 20 |
| sampler | `/tmp/quantlab_leaf34_high_accrual_*` |
| out | `output/ai_factory/_leaf34_high_accrual/` |
| overlap | `overlap_vs_leaf19_25_27_30_31_32_33.json` |

## 预启动门（签窗后）

QUIET by Arch（若要求）；healthz；wait≥15s；`pgrep` data readers empty；MemAvailable soft-floor；script_sha MATCH `482009dc`；dry-compile PASS；禁 RESTORED；禁抬 rss。

live=false · EXECUTED=false · ok_requested=false · leo_notify=false
