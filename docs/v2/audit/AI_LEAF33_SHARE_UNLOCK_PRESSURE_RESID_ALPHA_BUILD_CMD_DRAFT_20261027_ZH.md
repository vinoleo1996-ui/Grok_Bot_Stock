# 叶33 限售解禁压力残差慢 α · CMD DRAFT（现不可跑）

- **时刻**：2026-10-27 06:13 ET（America/New_York；ISO 2026-10-27T06:13:30-04:00）
- **状态**：DRAFT · EXECUTED=false · 待 Arch 审脚本 → 新 `.ok` + 主签窗
- **脚本**：`research/leaf33_share_unlock_pressure_resid_alpha_build.py` sha8 **`05c45917`**
- **对齐**：Arch FROZEN **`bf5234a9` PASS_WITH_CONDITIONS**；FROZEN **`8ed43721`**；PIN **`4e17ccfc`**；流程门 = 外挂新 `.ok` + 主窗
- **CLI 说明**：脚本**已实现** `--arch-ok-path`（对齐叶32 build；真跑须现存文件且 sha8∉forbid）。拟 approved_cmd **含**该 flag（指向**未来新** `.ok`，禁 RESTORED `5774bb6e`+二十票）。**禁**用未签发路径自开。

## approved_cmd_dry（本回合可静校；非实跑）

```
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf33_share_unlock_pressure_resid_alpha_build.py --dry-compile-only
```

## 拟 approved_cmd（**现不可跑**；须新 `.ok` + 主签窗）

```
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf33_share_unlock_pressure_resid_alpha_build.py --universe HILIQ --window x2 --x2-end 20261009 --allow-real-data --arch-ok-path output/ai_factory/ARCH_RUN_AUTH_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_X2_HILIQ.ok --out output/ai_factory/_leaf33_share_unlock/<STAMP>
```

### 可选

- `--also-fulla-research`：额外写 FULLA 研究 α（**不得**作 PRIMARY 判决）
- 显式 `--leaf19-alpha` / `--leaf25-alpha` / `--leaf27-alpha` / `--leaf30-alpha` / `--leaf31-alpha` / `--leaf32-alpha` / `--margin-delta` / `--hk-hold-weights` / `--moneyflow-weights` 钉重叠对照盘
- `--sample-dir /tmp/quantlab_leaf33_share_unlock_<tag>`（须此前缀）
- **禁**真跑路径用 `--no-overlap-report` 绕过 C4（脚本硬 STOP）

## 硬声明

- 流程门 = Arch **新** `.ok` + 主窗外挂；`--arch-ok-path` 仅校验现存授权文件（sha8 not in forbid），**不**自造 `.ok`
- **禁实跑** / **禁申 `.ok`** / **禁挂 QUIET** / ≠X2 ACCEPT / live=false
- forbid∋`5774bb6e+02426b73+4bb141c9+fdbaa512+aa25e989+7e239487+5af20222+5ae077fa+3c297052+e107383f+2be59acd+a7d98ac9+8e51de63+3a6caa4f+8bcd79dc+725be3e0+0f50daf7+3c19dd7d+1c32ab1e+6054b3bf+6de02e74`
- rss=1500 禁抬；peak_proof REQUIRED（`after_mask` / `after_share_float_rebal_*` / `after_close_rebal_*` / `after_float_mktcap_rebal_*` / `after_bars_rebal_*` / `after_logmv_rebal_*` / `after_daily_concat`）
- Jaccard≥0.7 vs 叶19/25/27/30/31/32/margin_delta/hk_hold/moneyflow → 硬拒（exit≠0）；ρ>0.5 强度过滤披露；缺文件→PIN_GAP
- C3：(a)+加价；close 钉不复权 `close`；表内 float_ratio PRIMARY 禁用
- KEEP 三闸仅钉；**KEEP 不解阻** X2 ACCEPT（叶32 `45dd87dc`）
- `0087c928`/叶28/29 另队不并入；≠Book-Smoke；≠重跑叶30/31/32

## 钉

| 项 | 值 |
|---|---|
| script | `05c45917` |
| FROZEN / PIN / ArchFROZEN | `8ed43721` / `4e17ccfc` / `bf5234a9` |
| mechanism | `g1g5_ashare_share_unlock_pressure_resid_v1` |
| H / H_back / W / rebal / α | 20 / 5 / 20 / 20 / −rank(pressure_resid) |
| sampler | `/tmp/quantlab_leaf33_share_unlock_*` |
| out | `output/ai_factory/_leaf33_share_unlock/` |
| overlap | `overlap_vs_leaf19_25_27_30_31_32_margin_delta_hk_hold_moneyflow.json` |

## 预启动门（签窗后）

QUIET by Arch（若要求）；healthz；wait≥15s；`pgrep` data readers empty；MemAvailable soft-floor；script_sha MATCH `05c45917`；dry-compile PASS；禁 RESTORED `5774bb6e`+二十票；禁抬 rss。

live=false · EXECUTED=false · ok_requested=false · leo_notify=false
