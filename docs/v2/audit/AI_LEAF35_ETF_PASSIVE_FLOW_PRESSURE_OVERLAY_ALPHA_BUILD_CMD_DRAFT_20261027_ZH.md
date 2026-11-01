# 叶35 ETF 被动压力 overlay · CMD DRAFT（现不可跑）

- **时刻**：2026-10-27 13:25 ET（America/New_York；ISO 2026-10-27T13:25:29-04:00）
- **状态**：DRAFT · EXECUTED=false · 待 Arch 审脚本 → 新 `.ok` + 主签窗
- **脚本**：`research/leaf35_etf_passive_flow_pressure_overlay_alpha_build.py` sha8 **`25ae4572`**
- **对齐**：Arch FROZEN **`5a082d18` PASS_WITH_CONDITIONS**；FROZEN **`be9fc459`**；PIN **`dd17044a`**；流程门 = 外挂新 `.ok` + 主窗
- **CLI 说明**：脚本**已实现** `--arch-ok-path`（对齐叶34 build；真跑须现存文件且 sha8∉forbid）。拟 approved_cmd **含**该 flag（指向**未来新** `.ok`，禁 RESTORED）。**禁**用未签发路径自开。
- **本拍未执行真跑**（无 `--allow-real-data` 实跑）。

## approved_cmd_dry（本回合可静校；非实跑）

```
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf35_etf_passive_flow_pressure_overlay_alpha_build.py --dry-compile-only
```

## 拟 approved_cmd（**现不可跑**；须新 `.ok` + 主签窗）

```
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf35_etf_passive_flow_pressure_overlay_alpha_build.py --universe HILIQ --window x2 --x2-end 20261009 --allow-real-data --arch-ok-path output/ai_factory/ARCH_RUN_AUTH_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_X2_HILIQ.ok --out output/ai_factory/_leaf35_etf_passive_flow_pressure/<STAMP>
```

### 可选

- `--also-fulla-research`：额外写 FULLA 研究 mask（**不得**作 PRIMARY 判决）
- `--enable-soft-penalty`：连续 soft-penalty（**非 PRIMARY**；须 SW+style；缺列 PIN_GAP）
- 显式 `--moneyflow-resid` / `--leaf26-resid-alpha` / `--leaf8a-alpha` / `--leaf25-alpha` … `--leaf34-alpha` 钉重叠对照盘
- `--sample-dir /tmp/quantlab_leaf35_etf_passive_<tag>`（须此前缀）
- **禁**真跑路径用 `--no-overlap-report` 绕过 C7（脚本硬 STOP）
- **禁** `--universe FULLA` 作 PRIMARY（dry/真跑均 STOP）

## 硬声明

- 流程门 = Arch **新** `.ok` + 主窗外挂；`--arch-ok-path` 仅校验现存授权文件（sha8 not in forbid），**不**自造 `.ok`
- **禁实跑** / **禁申 `.ok`** / **禁挂 QUIET** / ≠X2 ACCEPT / live=false
- forbid∋`178e90e9+c1b71e64+245df63f+c5ed13df+5774bb6e+81521fb5+02426b73+4bb141c9+fdbaa512+aa25e989+7e239487+5af20222+5ae077fa+3c297052+e107383f+2be59acd+a7d98ac9+8e51de63+3a6caa4f+8bcd79dc+725be3e0+0f50daf7+3c19dd7d+1c32ab1e+6054b3bf+6de02e74`
- rss=1500 禁抬；peak_proof REQUIRED（`after_mask` / `after_weight_pin` / `after_pressure_rebal_*` / `after_mask_cs_rebal_*` / `after_daily_concat`）
- Jaccard≥0.7 vs moneyflow/叶26残差(若有)/8a(若有)/25/27/30–34 → 硬拒（exit≠0）；ρ>0.5 强度过滤披露；leaf26-like raw J=1.0 **不得**硬拒；缺 required 文件→PIN_GAP
- PRIMARY=mask-only top_q=0.20；C3 PIN `dd17044a` 方案 A；禁叶26 完整残差 α 主交付
- KEEP 三闸仅钉；**KEEP 不解阻** X2 ACCEPT（叶32 `45dd87dc` / 叶34 `178e90e9`）；COUNT APPROX ≠ ACCEPT
- `0087c928`/叶28/29 另队不并入；叶33 `afbbe7e7` UNCHANGED；≠Book-Smoke

## 钉

| 项 | 值 |
|---|---|
| script | `25ae4572` |
| FROZEN / PIN / ArchFROZEN | `be9fc459` / `dd17044a` / `5a082d18` |
| mechanism | `g1g5_ashare_etf_passive_flow_pressure_overlay_v1` |
| top_q / delivery / rebal | 0.20 / mask-only / 20 |
| C3 | 方案 A 次月首个交易日 09:00 Asia/Shanghai |
| sampler | `/tmp/quantlab_leaf35_etf_passive_*` |
| out | `output/ai_factory/_leaf35_etf_passive_flow_pressure/` |
| overlap | `overlap_vs_moneyflow_leaf26resid_8a_25_27_30_31_32_33_34.json` |

## 预启动门（签窗后）

QUIET by Arch（若要求）；healthz；wait≥15s；`pgrep` data readers empty；MemAvailable soft-floor；script_sha MATCH `25ae4572`；dry-compile PASS；禁 RESTORED；禁抬 rss。

live=false · EXECUTED=false · ok_requested=false · leo_notify=false
