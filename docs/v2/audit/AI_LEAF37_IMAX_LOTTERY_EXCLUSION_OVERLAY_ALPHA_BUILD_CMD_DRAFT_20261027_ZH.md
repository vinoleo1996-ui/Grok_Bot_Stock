# 叶37 IMAX/隔夜彩票剔除 overlay · CMD DRAFT（现不可跑）

- **时刻**：2026-10-27 17:21 ET（America/New_York；ISO 2026-10-27T17:21:30-04:00）
- **状态**：DRAFT · EXECUTED=false · 待 Arch 审脚本 → 新 `.ok` + 主签窗
- **脚本**：`research/leaf37_imax_lottery_exclusion_overlay_alpha_build.py` sha8 **`108aba8f`**
- **对齐**：Arch FROZEN **`a5a9336d` PASS_WITH_CONDITIONS**；FROZEN **`c5927f1b`**；PIN **`e01be34c`**；流程门 = 外挂新 `.ok` + 主窗
- **CLI 说明**：脚本**已实现** `--arch-ok-path`（对齐叶34 build；真跑须现存文件且 sha8∉forbid）。拟 approved_cmd **含**该 flag（指向**未来新** `.ok`，禁 RESTORED）。**禁**用未签发路径自开。

## approved_cmd_dry（本回合可静校；非实跑）

```
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf37_imax_lottery_exclusion_overlay_alpha_build.py --dry-compile-only
```

## 拟 approved_cmd（**现不可跑**；须新 `.ok` + 主签窗）

```
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf37_imax_lottery_exclusion_overlay_alpha_build.py --universe HILIQ --window x2 --x2-end 20261009 --allow-real-data --arch-ok-path output/ai_factory/ARCH_RUN_AUTH_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_X2_HILIQ.ok --out output/ai_factory/_leaf37_imax_lottery/<STAMP>
```

### 可选

- `--also-fulla-research`：额外写 FULLA 研究 mask（**不得**作 PRIMARY 判决）
- `--enable-soft-penalty`：连续 soft-penalty（**非 PRIMARY**；须 SW+logmv+style；缺列 PIN_GAP）
- 显式 `--leaf18-alpha` / `--leaf18v-alpha` / `--leaf27-alpha` / `--leaf24-dir` / `--leaf34-mask` / `--leaf35-mask` / `--leaf36-count-json`
- `--sample-dir /tmp/quantlab_leaf37_imax_lottery_<tag>`（须此前缀）
- **禁**真跑路径用 `--no-overlap-report` 绕过 C7（脚本硬 STOP）
- **禁** `--universe FULLA` 作 PRIMARY（dry/真跑均 STOP）

## 硬声明

- 流程门 = Arch **新** `.ok` + 主窗外挂；`--arch-ok-path` 仅校验现存授权文件（sha8 not in forbid），**不**自造 `.ok`
- **禁实跑** / **禁申 `.ok`** / **禁挂 QUIET** / ≠X2 ACCEPT / live=false
- forbid∋`eb70eef4+00eec671+10927bd9+25ae4572+178e90e9+c1b71e64+245df63f+c5ed13df+5774bb6e+81521fb5+02426b73+4bb141c9+fdbaa512+aa25e989+7e239487+5af20222+5ae077fa+3c297052+e107383f+2be59acd+a7d98ac9+8e51de63+3a6caa4f+8bcd79dc+725be3e0+0f50daf7+3c19dd7d+1c32ab1e+6054b3bf+6de02e74`
- rss=1500 禁抬；peak_proof REQUIRED（`after_mask` / `after_panel_imax` / `after_mask_cs_rebal_*` / `after_daily_concat`）
- Jaccard≥0.7 vs 叶18/18v/27 → 硬拒（exit≠0）；ρ>0.5 强度过滤披露（COUNT ρ18≈0.505/ρ27≈0.665）；vs 叶24/34/35/36 披露；缺硬文件→PIN_GAP
- PRIMARY=mask-only top_q=0.20；C3=B PIN `e01be34c`；`full_residual_e_id=false`；禁静默升全 e_id；禁叶24 完整主 α
- KEEP 三闸仅钉；**KEEP 不解阻** X2 ACCEPT；COUNT APPROX ≠ ACCEPT
- 叶36 HOLD CLOSED 不复开；叶33 `afbbe7e7` / 叶35 `434ff42c` UNCHANGED；≠Book-Smoke

## 钉

| 项 | 值 |
|---|---|
| script | `108aba8f` |
| FROZEN / PIN / ArchFROZEN | `c5927f1b` / `e01be34c` / `a5a9336d` |
| mechanism | `g1g5_ashare_imax_lottery_exclusion_overlay_v1` |
| top_q / delivery / rebal / C3 | 0.20 / mask-only / 20 / B IMAX_proxy |
| sampler | `/tmp/quantlab_leaf37_imax_lottery_*` |
| out | `output/ai_factory/_leaf37_imax_lottery/` |
| overlap | `overlap_vs_leaf18_18v_27_hard_24_34_35_36_disclose.json` |

## 预启动门（签窗后）

QUIET by Arch（若要求）；healthz；wait≥15s；`pgrep` data readers empty；MemAvailable soft-floor；script_sha MATCH `108aba8f`；dry-compile PASS；禁 RESTORED；禁抬 rss。

live=false · EXECUTED=false · ok_requested=false · leo_notify=false
