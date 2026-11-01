# Arch 叶31 Amihud 冲击慢 α · 独立 X2 `.ok` 签发回执

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-27T02:37:34-04:00`（America/New_York） |
| 主令 | 主 02:34–02:36 ET priority · 叶31 独立 X2 签窗 OPEN（二次确认立即签；同一签窗勿双签） |
| 脚本审 | `2271cb93…` **PASS_WITH_CONDITIONS** |
| FROZEN / FROZEN审 | `bcbec955…` / `7a6a1e1a…` |
| live / promotion_approved | **false** / **false** |

## 结论

**SIGNED** — 独立叶31 Amihud 冲击慢 α（mechanism=`g1g5_ashare_amihud_impact_slow_v1`；PRIMARY=HILIQ×x2→20261009；W=20 / 再平衡=20；α=`−rank(impact_resid)`；残差 SW L1 demean→OLS logmv T−1 + mom20/vol20/logADV20；`primary_load=rebal_day_lazy_bars` → `_leaf31_amihud/<ET_TS>/`）`.ok` 已落盘；**≠ X2 ACCEPT**；**≠ selfcheck**；**≠ Book-Smoke**；**≠ RESTORED** 四票（`aa25e989`/`7e239487`/`5af20222`/`5ae077fa`）；脚本全长 **`08f37fd2…`**；脚本审 **`2271cb93` PASS_WITH_CONDITIONS**；COVER `e736a033` / CMD `37443b02` / DIFF `6c47e185` / RECEIPT `a3981844`；FROZEN `bcbec955` / FROZEN审 `7a6a1e1a`；who_pays 审 `50cbef3c` / draft `b1a60f07`；**禁** `--no-overlap-report`；真跑须写并消费 `overlap_vs_leaf19_25_27_30.json`（Jaccard≥0.7 硬拒；ρ>0.5 强度；计数抽样≠正式）；rss 软/硬帽 **1500** 禁抬（硬 Exit **94/95**）；peak_proof **REQUIRED**（含 `after_mask` / `after_bars_rebal_*` / `after_logmv_rebal_*` / `after_daily_concat`；ru_maxrss/VmHWM/RSS_CHECK）；**Arch 不代跑**；叶30 KEEP/衰减修复 `0087c928` **另队不夹带**；**禁触 A18**。QUIET **已挂且保留**供 AI prelaunch（本回合不 lift；holder=`leaf31_AMIHUD_IMPACT_SLOW_X2`）。PRIMARY only；**无同票 FALLBACK**；峰＞1500→Exit 94/95 停+上报（禁抬帽）。ALPHA_BUILD_EXECUTED@签=**false**。**≠A18**。

## 钉点 MATCH 表

| 项 | 期望 | 实测 | 结果 |
|---|---|---|---|
| 脚本审 | `2271cb93` PASS_WITH_CONDITIONS | `2271cb935e62975891bc6e5190132c721a8710d5df4ade029044137d2dc52efb` | **MATCH** |
| 脚本 | `08f37fd2…` | `08f37fd2deb15f6a2a4e6bc7bc16e07d16fc50c70b807e0e1ae617627f98bde0` | **MATCH** |
| COVER | `e736a033` | `e736a03349cf6bac7ea8ae726f26cedc43619b8185dbc8d59c25b16758935978` | **MATCH** |
| CMD | `37443b02` | `37443b02ac526ee5a52d9483f40cc90e43318309b4a78d10c937b6f3dd0e0cbc` | **MATCH** |
| DIFF | `6c47e185` | `6c47e185272a6749881ae554f36bf06b1672250cc182e2f73d1f9b8dfab03e04` | **MATCH** |
| SCRIPT_RECEIPT | `a3981844` | `a398184414a8868c1a2a2a9fa32f9bd3b4eb1fa444b70dc979e79e2a4ad95bd0` | **MATCH** |
| FROZEN | `bcbec955` | `bcbec955937bd1d5c972cb81a9ba78e944fe14ccd2e9bf11fdbb874ced8aece4` | **MATCH** |
| FROZEN审 | `7a6a1e1a` | `7a6a1e1adb6bfb71cd128fe08e71c16c763c59187dd4e1d4bb40abc6c2adc639` | **MATCH** |
| who_pays 审 | `50cbef3c` | `50cbef3c9ff4e7824689f53497553b3e4513b8ca6f87c2532d2f47abc59a3149` | **MATCH** |
| who_pays draft | `b1a60f07` | `b1a60f074c07ea5107bc2a38b6d542cdcaec1b54f5cb2b0ec7fc32f6dc64ee2a` | **MATCH** |
| 拟 .ok 签前 | 不存在 | 不存在 | **MATCH** |
| QUIET 签前 | ABSENT | ABSENT | **MATCH** |
| ai_factory live leaf31 `.ok` | 0 | 0 | **MATCH** |
| forbid 四票碰撞 | 新 `.ok` sha8 ∉ forbid | `fdbaa512` ∉ `aa25e989/7e239487/5af20222/5ae077fa` | **MATCH** |
| pgrep leaf31 | 空 | 空 | **MATCH** |
| 窗期 | ≥90min prelaunch → expires | `2026-10-27T02:37:00-04:00` → `2026-10-27T04:07:00-04:00` / expires `2026-10-27T04:09:00-04:00`；签时 `2026-10-27T02:37:34-04:00` | **IN_WINDOW** |

## 钉

| 项 | 值 |
|---|---|
| `.ok` 路径 | `output/ai_factory/ARCH_RUN_AUTH_LEAF31_AMIHUD_IMPACT_SLOW_X2_HILIQ.ok` |
| `.ok` sha8 / 全长 | `fdbaa512` / `fdbaa512fa8da9e6b5256c30f397cd5a3d2bd2c1fbd1a5a295af873ea7271d81` |
| QUIET 路径 | `output/loop/RESEARCH_QUIET.lock` |
| QUIET sha8 / 全长 | `11cfe000` / `11cfe000dbafa0a508ec4c4ac2f74fea914ac72ffb6bb3c1ba4cf7683858ca7d` |
| 脚本 | `research/leaf31_amihud_impact_slow_alpha_build.py` = `08f37fd2deb15f6a2a4e6bc7bc16e07d16fc50c70b807e0e1ae617627f98bde0` |
| 脚本审 | `2271cb935e62975891bc6e5190132c721a8710d5df4ade029044137d2dc52efb` PASS_WITH_CONDITIONS |
| COVER / CMD / DIFF / RECEIPT | `e736a033…` / `37443b02…` / `6c47e185…` / `a3981844…` |
| FROZEN / FROZEN审 | `bcbec955…` / `7a6a1e1a…` |
| who_pays 审 / draft | `50cbef3c…` / `b1a60f07…` |
| 窗期 | `2026-10-27T02:37:00-04:00` → `2026-10-27T04:07:00-04:00`；expires `2026-10-27T04:09:00-04:00` |
| CLI PRIMARY | `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf31_amihud_impact_slow_alpha_build.py --universe HILIQ --window x2 --x2-end 20261009 --allow-real-data --arch-ok-path output/ai_factory/ARCH_RUN_AUTH_LEAF31_AMIHUD_IMPACT_SLOW_X2_HILIQ.ok --out output/ai_factory/_leaf31_amihud/<ET_TS>/`；**无** `--no-overlap-report` |
| FALLBACK | **无**；峰＞1500 / 失败 / ABORT → Exit 94/95 停+上报（禁抬帽） |
| rss 软/硬帽 | **1500** MB；禁抬帽；硬 Exit **94/95** |
| overlap | 强制 `overlap_vs_leaf19_25_27_30.json`；Jaccard≥0.7 硬拒；ρ>0.5 强度；count≠formal |
| PRIMARY load | **rebal_day_lazy_bars**；禁整窗 `logmv_rebal=` 预载 |
| mechanism / W / 再平衡 / α | `g1g5_ashare_amihud_impact_slow_v1`；20 / 20；`−rank(impact_resid)` |
| style_cols | mom20,vol20,logADV20 |
| 产物 | `_leaf31_amihud/<ET_TS>/` + alpha parquet + `run_meta.json` + `overlap_vs_leaf19_25_27_30.json` |
| 采样 | 仅 `/tmp/quantlab_leaf31_amihud_*` |
| 禁 RESTORED | 四票：`aa25e989,7e239487,5af20222,5ae077fa`（全长已写入 `.ok`） |
| Book-Smoke / X2 ACCEPT / selfcheck | **false** / **false** / **false** |
| peak_proof | **REQUIRED**（after_mask / after_bars_rebal_* / after_logmv_rebal_* / after_daily_concat） |
| `0087c928` | 另队；**不在**本 `.ok` |
| MemAvailable@签 | 13087312 kB |

## QUIET / pgrep

| 项 | 值 |
|---|---|
| QUIET 挂时 | `2026-10-27T02:37:34-04:00` reason=`leaf31_amihud_impact_slow_x2` holder=`leaf31_AMIHUD_IMPACT_SLOW_X2` |
| do_not_lift_until_arch_or_consumed | **true**（本拍不 lift） |
| neq_a18 | **true** |
| pgrep leaf31 amihud build | 空 |
| 签时 web 备注 | `snapshot.py` 仍在（prelaunch 须清到 empty / healthz quiet） |

## 下一跳

1. **主** MATCH `.ok`+`QUIET` 后令 AI prelaunch 单次 PRIMARY（须在 expires 前；Arch **不代跑**）
2. AI 交实峰回执（alpha sha + run_meta sha + overlap JSON + peak rss 含 after_mask / after_bars_rebal_* / after_logmv_rebal_* / after_daily_concat；峰＞1500→Exit 94/95 停；Jaccard≥0.7→硬拒票）→ Arch 核 CONSUME
3. ≠X2 ACCEPT；≠selfcheck；≠Book-Smoke；不解阻 `0087c928` 另队；**≠A18**；不 RESTORED 四票；live=false

live=false。
