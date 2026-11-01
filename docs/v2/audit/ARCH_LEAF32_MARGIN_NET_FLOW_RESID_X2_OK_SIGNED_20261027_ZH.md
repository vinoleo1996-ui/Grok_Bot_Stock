# Arch 叶32 净融资流入强度残差慢 α · 独立 X2 `.ok` 签发回执

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-27T04:21:23-04:00`（America/New_York） |
| 主令 | 主 04:19 ET priority · 叶32 独立 X2 签窗 OPEN→SIGN（脚本审 `814939b8` PASS_WITH_CONDITIONS；钉脚本 `4e0f3c00`） |
| 脚本审 | `814939b8…` **PASS_WITH_CONDITIONS** |
| FROZEN / FROZEN审 | `6b8de5e9…` / `7c0d864f…` |
| live / promotion_approved | **false** / **false** |

## 结论

**SIGNED** — 独立叶32 净融资流入强度残差慢 α（mechanism=`g1g5_ashare_margin_net_flow_resid_v1`；PRIMARY=HILIQ×x2→20261009；W=20 / 再平衡=20；α=`−rank(flow_resid)`；残差 SW L1 demean→OLS logmv T−1 + mom20/vol20/logADV20；`primary_load=rebal_day_lazy_margin_float_bars` → `_leaf32_margin_flow/<ET_TS>/`）`.ok` 已落盘；**≠ X2 ACCEPT**；**≠ selfcheck**；**≠ Book-Smoke**；**≠ RESTORED** 六票（`4bb141c9`/`fdbaa512`/`aa25e989`/`7e239487`/`5af20222`/`5ae077fa`）；脚本全长 **`4e0f3c00…`**；脚本审 **`814939b8` PASS_WITH_CONDITIONS**；COVER `b269aec5` / CMD `53002ae3` / DIFF `264d0159` / RECEIPT `0937a882`；FROZEN `6b8de5e9` / FROZEN审 `7c0d864f` / FROZEN RECEIPT `7623ce8c`；who_pays 审 `84df02b5` / WHO `fad5911e` / who COVER `ebda2603`；**禁** `--no-overlap-report`；真跑须写并消费 `overlap_vs_leaf19_25_27_30_31_margin_delta.json`（Jaccard≥0.7 硬拒；ρ>0.5 强度；计数抽样≠正式；margin_delta 缺→PIN_GAP）；rss 软/硬帽 **1500** 禁抬（硬 Exit **94/95**）；peak_proof **REQUIRED**（含 `after_mask` / `after_sw` / `after_margin_rebal_*` / `after_float_rebal_*` / `after_bars_rebal_*` / `after_logmv_rebal_*` / `after_daily_concat`；ru_maxrss/VmHWM/RSS_CHECK）；**Arch 不代跑**；叶30 KEEP/衰减修复 `0087c928` **另队不夹带**；**禁触 A18**。QUIET **已挂且保留**供 AI prelaunch（本回合不 lift；holder=`leaf32_MARGIN_NET_FLOW_RESID_X2`）。PRIMARY only；FULLA 仅 `--also-fulla-research` 研究旁路；**无同票 FALLBACK**；峰＞1500→Exit 94/95 停+上报（禁抬帽）。ALPHA_BUILD_EXECUTED@签=**false**。**≠A18**。

## 钉点 MATCH 表

| 项 | 期望 | 实测 | 结果 |
|---|---|---|---|
| 脚本审 | `814939b8` PASS_WITH_CONDITIONS | `814939b8bb1c911e48e3425953ee3e92826a0d0f0c00d7a0801503e8560b372a` | **MATCH** |
| 脚本 | `4e0f3c00…` | `4e0f3c002057393c031598e0379c6622afe8ca4a18579c9ab3b9f3d7ba4ae187` | **MATCH** |
| COVER | `b269aec5` | `b269aec512b826f74384106d3313f85c4e2f69b18f1fac370171b2244201818a` | **MATCH** |
| CMD | `53002ae3` | `53002ae3860b64e79f52455f13fc046ae5baa5302ec079d46ef0410e78e7067f` | **MATCH** |
| DIFF | `264d0159` | `264d01596154c71923f17fa4b0106db661daf29f95f19e9ccddbf1e91256b294` | **MATCH** |
| SCRIPT_RECEIPT | `0937a882` | `0937a8823a01cf025ba07aaaa3c4546bc2863ca72964676971d2faedd449b438` | **MATCH** |
| FROZEN | `6b8de5e9` | `6b8de5e9d4a4cc6caecbe344bfc4b6ce4da0f9e983f87c7c7b73759e0f893f42` | **MATCH** |
| FROZEN审 | `7c0d864f` | `7c0d864f7d544e8bd16817c74fa4dd7e35c9609c5066eedc4ee15f71765b5d84` | **MATCH** |
| FROZEN RECEIPT | `7623ce8c` | `7623ce8c351ce7c1927b17dd095953f8c968753fbfe5f9d5eb29042bf814bb37` | **MATCH** |
| who_pays 审 | `84df02b5` | `84df02b5ddfd10314bf8bc95acdf931d12ba9e53e43dd318e61fdc85b7b6fb01` | **MATCH** |
| who_pays draft | `fad5911e` | `fad5911eec855a3b77d77971f8d44241798bfa4355adebd3f14aa67910fc6c44` | **MATCH** |
| who COVER | `ebda2603` | `ebda2603283198382c7225924f4105d9ec9891acad3ba83a022a2172a1dac9fc` | **MATCH** |
| 拟 .ok 签前 | 不存在 | 不存在 | **MATCH** |
| QUIET 签前 | ABSENT | ABSENT | **MATCH** |
| ai_factory live leaf32 `.ok` | 0→1（本签） | 签前 0 / 签后 1 | **MATCH** |
| forbid 六票碰撞 | 新 `.ok` sha8 ∉ forbid | `02426b73` ∉ `4bb141c9/fdbaa512/aa25e989/7e239487/5af20222/5ae077fa` | **MATCH** |
| pgrep leaf32 | 空 | 空 | **MATCH** |
| 窗期 | ≥90min prelaunch → expires | `2026-10-27T04:21:00-04:00` → `2026-10-27T05:51:00-04:00` / expires `2026-10-27T05:53:00-04:00`；签时 `2026-10-27T04:21:23-04:00` | **IN_WINDOW** |

## 钉

| 项 | 值 |
|---|---|
| `.ok` 路径 | `output/ai_factory/ARCH_RUN_AUTH_LEAF32_MARGIN_NET_FLOW_RESID_X2_HILIQ.ok` |
| `.ok` sha8 / 全长 | `02426b73` / `02426b73d253237127772bd0023c52938ad58bdb76204feeddac87ceb385d736` |
| QUIET 路径 | `output/loop/RESEARCH_QUIET.lock` |
| QUIET sha8 / 全长 | `6d62911f` / `6d62911f53c0ab7820be756dbbbddae3fa7c78f623d58cdf377ec64edd3505a5` |
| 脚本 | `research/leaf32_margin_net_flow_resid_alpha_build.py` = `4e0f3c002057393c031598e0379c6622afe8ca4a18579c9ab3b9f3d7ba4ae187` |
| 脚本审 | `814939b8bb1c911e48e3425953ee3e92826a0d0f0c00d7a0801503e8560b372a` PASS_WITH_CONDITIONS |
| COVER / CMD / DIFF / RECEIPT | `b269aec5…` / `53002ae3…` / `264d0159…` / `0937a882…` |
| FROZEN / FROZEN审 / FROZEN RECEIPT | `6b8de5e9…` / `7c0d864f…` / `7623ce8c…` |
| who_pays 审 / WHO / who COVER | `84df02b5…` / `fad5911e…` / `ebda2603…` |
| 窗期 | `2026-10-27T04:21:00-04:00` → `2026-10-27T05:51:00-04:00`；expires `2026-10-27T05:53:00-04:00` |
| CLI PRIMARY | `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf32_margin_net_flow_resid_alpha_build.py --universe HILIQ --window x2 --x2-end 20261009 --allow-real-data --arch-ok-path output/ai_factory/ARCH_RUN_AUTH_LEAF32_MARGIN_NET_FLOW_RESID_X2_HILIQ.ok --out output/ai_factory/_leaf32_margin_flow/<ET_TS>/`；**无** `--no-overlap-report` |
| FALLBACK | **无**；峰＞1500 / 失败 / ABORT → Exit 94/95 停+上报（禁抬帽） |
| rss 软/硬帽 | **1500** MB；禁抬帽；硬 Exit **94/95** |
| overlap | 强制 `overlap_vs_leaf19_25_27_30_31_margin_delta.json`；Jaccard≥0.7 硬拒；ρ>0.5 强度；count≠formal |
| PRIMARY load | **rebal_day_lazy_margin_float_bars**；禁整窗 `logmv_rebal=` 预载 |
| mechanism / W / 再平衡 / α | `g1g5_ashare_margin_net_flow_resid_v1`；20 / 20；`−rank(flow_resid)` |
| style_cols | mom20,vol20,logADV20 |
| 产物 | `_leaf32_margin_flow/<ET_TS>/` + alpha parquet + `run_meta.json` + `overlap_vs_leaf19_25_27_30_31_margin_delta.json` |
| 采样 | 仅 `/tmp/quantlab_leaf32_margin_flow_*` |
| 禁 RESTORED | 六票：`4bb141c9,fdbaa512,aa25e989,7e239487,5af20222,5ae077fa`（全长已写入 `.ok`） |
| Book-Smoke / X2 ACCEPT / selfcheck | **false** / **false** / **false** |
| peak_proof | **REQUIRED**（after_mask / after_sw / after_margin_rebal_* / after_float_rebal_* / after_bars_rebal_* / after_logmv_rebal_* / after_daily_concat） |
| `0087c928` | 另队；**不在**本 `.ok` |
| MemAvailable@签 | 13283276 kB |

## QUIET / pgrep

| 项 | 值 |
|---|---|
| QUIET 挂时 | `2026-10-27T04:21:23-04:00` reason=`leaf32_margin_net_flow_resid_x2` holder=`leaf32_MARGIN_NET_FLOW_RESID_X2` |
| do_not_lift_until_arch_or_consumed | **true**（本拍不 lift） |
| neq_a18 | **true** |
| pgrep leaf32 margin build | 空 |
| 签时 web | empty（prelaunch 仍须 healthz quiet） |

## 下一跳

1. **主** MATCH `.ok`+`QUIET` 后令 AI prelaunch 单次 PRIMARY（须在 expires 前；Arch **不代跑**）
2. AI 交实峰回执（alpha sha + run_meta sha + overlap JSON + peak rss 含 after_mask / after_sw / after_margin_rebal_* / after_float_rebal_* / after_bars_rebal_* / after_logmv_rebal_* / after_daily_concat；峰＞1500→Exit 94/95 停；Jaccard≥0.7→硬拒票）→ Arch 核 CONSUME
3. ≠X2 ACCEPT；≠selfcheck；≠Book-Smoke；不解阻 `0087c928` 另队；**≠A18**；不 RESTORED 六票；live=false

live=false。
