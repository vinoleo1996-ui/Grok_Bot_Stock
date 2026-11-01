# 叶32 净融资流入强度残差慢 α · CMD DRAFT（现不可跑）

- **时刻**：2026-10-27 04:08 ET（America/New_York；ISO 2026-10-27T04:08:34-0400）
- **状态**：DRAFT · EXECUTED=false · 待 Arch 审脚本 → 新 `.ok` + 主签窗
- **脚本**：`research/leaf32_margin_net_flow_resid_alpha_build.py` sha8 **`4e0f3c00`**
- **对齐**：Arch FROZEN **`7c0d864f` PASS_WITH_CONDITIONS**；FROZEN **`6b8de5e9`**；流程门 = 外挂新 `.ok` + 主窗
- **CLI 说明**：脚本**已实现** `--arch-ok-path`（对齐叶31 **build**；真跑须现存文件且 sha8∉forbid）。拟 approved_cmd **含**该 flag（指向**未来新** `.ok`，禁 RESTORED 六票）。**禁**用未签发路径自开。

## approved_cmd_dry（本回合可静校；非实跑）

```
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf32_margin_net_flow_resid_alpha_build.py --dry-compile-only
```

## 拟 approved_cmd（**现不可跑**；须新 `.ok` + 主签窗）

```
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf32_margin_net_flow_resid_alpha_build.py --universe HILIQ --window x2 --x2-end 20261009 --allow-real-data --arch-ok-path output/ai_factory/ARCH_RUN_AUTH_LEAF32_MARGIN_NET_FLOW_RESID_X2_HILIQ.ok --out output/ai_factory/_leaf32_margin_flow/<STAMP>
```

### 可选

- `--also-fulla-research`：额外写 FULLA 研究 α（**不得**作 PRIMARY 判决）
- 显式 `--leaf19-alpha` / `--leaf25-alpha` / `--leaf27-alpha` / `--leaf30-alpha` / `--leaf31-alpha` / `--margin-delta` 钉重叠对照盘
- `--sample-dir /tmp/quantlab_leaf32_margin_flow_<tag>`（须此前缀）

## 硬声明

- 流程门 = Arch **新** `.ok` + 主窗外挂；`--arch-ok-path` 仅校验现存授权文件（sha8 not in forbid），**不**自造 `.ok`
- **禁实跑** / **禁申 `.ok`** / **禁挂 QUIET** / ≠X2 ACCEPT / live=false
- forbid∋`4bb141c9`+`fdbaa512`+`aa25e989`+`7e239487`+`5af20222`+`5ae077fa`
- rss=1500 禁抬；peak_proof REQUIRED（`after_mask` / `after_margin_rebal_*` / `after_float_rebal_*` / `after_bars_rebal_*` / `after_logmv_rebal_*` / `after_daily_concat`）
- Jaccard≥0.7 vs 叶19/25/27/30/31/margin_delta → 硬拒（exit≠0）；ρ>0.5 强度过滤披露；margin_delta 缺文件→PIN_GAP
- `0087c928` 另队不并入；≠Book-Smoke；≠重跑叶30/31

## 钉

| 项 | 值 |
|---|---|
| script | `4e0f3c00` |
| FROZEN / ArchFROZEN | `6b8de5e9` / `7c0d864f` |
| mechanism | `g1g5_ashare_margin_net_flow_resid_v1` |
| W / rebal / α | 20 / 20 / −rank(flow_resid) |
| sampler | `/tmp/quantlab_leaf32_margin_flow_*` |
| out | `output/ai_factory/_leaf32_margin_flow/` |
| overlap | `overlap_vs_leaf19_25_27_30_31_margin_delta.json` |

## 预启动门（签窗后）

QUIET by Arch（若要求）；healthz；wait≥15s；`pgrep` data readers empty；MemAvailable soft-floor；script_sha MATCH `4e0f3c00`；dry-compile PASS；禁 RESTORED 六票；禁抬 rss。

live=false · EXECUTED=false · ok_requested=false · leo_notify=false
