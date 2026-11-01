# Arch 叶33 限售解禁压力残差慢 α · tz 对齐独立 X2 `.ok` 签发回执

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-27T07:15:32-04:00`（America/New_York） |
| 主令 | 主 07:11 ET priority · 叶33 独立 X2 签窗 OPEN→SIGN（落地脚本审 `069ba364` PASS_WITH_CONDITIONS；钉脚本 `afbbe7e7`；tz_align_mode=`naive_calendar_day`） |
| 脚本审 | `069ba364…` **PASS_WITH_CONDITIONS**（LANDED） |
| 补丁审 | `19cc790f…` PASS_WITH_CONDITIONS |
| FROZEN / FROZEN审 / PIN | `8ed43721…` / `bf5234a9…` / `4e17ccfc…` |
| VOID / RUN | `8a3b25ba…` / `481bacda…` |
| live / promotion_approved / leo_notify | **false** / **false** / **false** |

## 结论

**SIGNED** — 叶33 限售解禁压力残差慢 α **tz 对齐重签**（mechanism=`g1g5_ashare_share_unlock_pressure_resid_v1`；PRIMARY=HILIQ×x2→20261009；H=20 / H_back=5 / W=20 / 再平衡=20；α=`−rank(pressure_resid)`；残差 SW L1 demean→OLS logmv T−1 + mom20/vol20/logADV20；C3=(a)+加价；tz_align_mode=`naive_calendar_day`；基线对照脚本 `05c45917`；落地脚本 **`afbbe7e7`**；primary_load=`rebal_day_lazy_share_float_close_mktcap_bars` → `_leaf33_share_unlock/<ET_TS>/`）**新** `.ok` 已落盘；**≠ RESTORED** 旧 VOID `c5ed13df`；**≠ X2 ACCEPT**；**≠ selfcheck**；**≠ Book-Smoke**；**≠ RESTORED** `c5ed13df`+`5774bb6e`+二十票（**22**）；脚本全长 **`afbbe7e7…`**；落地脚本审 **`069ba364` PASS_WITH_CONDITIONS**；补丁审 **`19cc790f`**；COVER `9fd7af74` / CMD `7b0756db` / DIFF `99d40f9a` / RECEIPT `617f0481`；VOID `8a3b25ba` / RUN `481bacda`；FROZEN `8ed43721` / FROZEN审 `bf5234a9` / FROZEN RECEIPT `8f43e2f8`；PIN `4e17ccfc`；who_pays 审 `55531e12` / WHO `1032477d` / who COVER `61d9f656`；叶32 模板 **`4e0f3c00` UNCHANGED**；**禁** `--no-overlap-report`；真跑须 `--allow-real-data` + `--arch-ok-path <NEW_OK>` 并写/消费 `overlap_vs_leaf19_25_27_30_31_32_margin_delta_hk_hold_moneyflow.json`（Jaccard≥0.7 硬拒；ρ>0.5 强度；计数抽样≠正式；缺→PIN_GAP）；rss 软/硬帽 **1500** 禁抬（硬 Exit **94/95**）；peak_proof **REQUIRED**；**Arch 不代跑**；叶30 KEEP/衰减修复 `0087c928` / 叶28/29 **另队不夹带**；**禁触 A18**。QUIET **已挂且保留**供 AI prelaunch（本回合不 lift；holder=`leaf33_SHARE_UNLOCK_PRESSURE_RESID_X2`；reason=`leaf33_share_unlock_pressure_resid_x2_tz_align`）。PRIMARY only；FULLA 仅 `--also-fulla-research` 研究旁路；**无同票 FALLBACK**；峰＞1500→Exit 94/95 停+上报（禁抬帽）。ALPHA_BUILD_EXECUTED@签=**false**。**≠A18**。leo_notify=**false**。

## 钉点 MATCH 表

| 项 | 期望 | 实测 | 结果 |
|---|---|---|---|
| 落地脚本审 | `069ba364` PASS_WITH_CONDITIONS | `069ba36417d138402d07fb0bd2649d55579d38f09b91558c417bec18a0c7f29b` | **MATCH** |
| 脚本 | `afbbe7e7…` only | `afbbe7e7292c17399bbf4733d9f34a922e6d81f1a914a60d24dc61fcba86cbc9` | **MATCH** |
| 基线对照脚本 | `05c45917…` | `05c4591788b8bf244c03b63fd918f154ae87e15b5f08cb8930f5ff78c8fb01e2` | **MATCH**（对照钉） |
| tz_align_mode | `naive_calendar_day` | `naive_calendar_day` | **MATCH** |
| 补丁审 | `19cc790f` | `19cc790f83b529e238e7e36b7e5142c6aa7f2d7e375098d35b7f035f408641c7` | **MATCH** |
| COVER | `9fd7af74` | `9fd7af747293645700a021e75461c5fd1a6df4132b1c3f2c7492473582465045` | **MATCH** |
| CMD | `7b0756db` | `7b0756dbc46d2da87f95e4890ca32bca5a4afcade46dcfec4d3650c1a3b2cd7f` | **MATCH** |
| DIFF | `99d40f9a` | `99d40f9a9ab1aecc3e696d9a3b98f562eee0b0271b4c1f7a10f9a0e99b14b43b` | **MATCH** |
| RECEIPT | `617f0481` | `617f0481bf86d720af89c75da4894d8bbfb273da25cba6bb5705ecd31865139f` | **MATCH** |
| VOID | `8a3b25ba` | `8a3b25bae0c80377f1087e7d0d5287b61b7db62f96ebfa3106b95e219c5c5cd5` | **MATCH** |
| RUN | `481bacda…` | `481bacda12b3f820134adc0acf7dbb574c52c6f49a3a21303df4f85f1a70e6c1` | **MATCH** |
| FROZEN | `8ed43721` | `8ed437210214015bfd6b3ee17104b4bae3c38baf62583f2e529433f550983189` | **MATCH** |
| FROZEN审 | `bf5234a9` | `bf5234a9fb732a7e71a0bc1ca5b7e6097e50d4e1d023778e534f2bf58e9c19d3` | **MATCH** |
| FROZEN RECEIPT | `8f43e2f8` | `8f43e2f8f1f62ad9dddfb9a9be71c32c574b9c3037c61a256e971ef2385085ff` | **MATCH** |
| PIN | `4e17ccfc` | `4e17ccfc16cb3c2ed388941514dc65e0dbfce1242bb15b3923cc2f89da6cfb75` | **MATCH** |
| who_pays 审 | `55531e12` | `55531e129e89077e9390a45c2f1310d5e2a80421ff6d16927b46bbaf1a7ee3c5` | **MATCH** |
| who_pays draft | `1032477d` | `1032477d54c9c2c4b0bc4398066d76d852369d9187f3ff3e7c7610953c086075` | **MATCH** |
| who COVER | `61d9f656` | `61d9f656b8dcfa686f512f92637c884ab3029dfd523956bda4d2bfbbf70c5f70` | **MATCH** |
| 叶32 模板 | `4e0f3c00` UNCHANGED | `4e0f3c002057393c031598e0379c6622afe8ca4a18579c9ab3b9f3d7ba4ae187` | **MATCH** |
| 拟 .ok 签前 | ABSENT（禁 RESTORED c5ed13df） | ABSENT | **MATCH** |
| QUIET 签前 | ABSENT | ABSENT | **MATCH** |
| ai_factory live leaf33 `.ok` | 0→1（本签） | 签前 0 / 签后 1 | **MATCH** |
| 新 `.ok` sha8 ∉ forbid22 | ≠`c5ed13df` 且 ∉ 21+1 | `245df63f` ∉ forbid22（含 `c5ed13df`） | **MATCH** |
| pgrep leaf33 | 空 | 空 | **MATCH** |
| 窗期 | ≥90min prelaunch → expires | `2026-10-27T07:11:00-04:00` → `2026-10-27T08:41:00-04:00` / expires `2026-10-27T08:45:00-04:00`；签时 `2026-10-27T07:15:32-04:00` | **IN_WINDOW** |

## 钉

| 项 | 值 |
|---|---|
| `.ok` 路径 | `output/ai_factory/ARCH_RUN_AUTH_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_X2_HILIQ.ok` |
| `.ok` sha8 / 全长 | `245df63f` / `245df63f5c8e39052da15a4f2338132382d6e60751c2f22df316a7d71575e4cc` |
| QUIET 路径 | `output/loop/RESEARCH_QUIET.lock` |
| QUIET sha8 / 全长 | `ca492c09` / `ca492c09202addb0af5ab13ad078a99eeefb53f34305d41476068788183cdf72` |
| 脚本 | `research/leaf33_share_unlock_pressure_resid_alpha_build.py` = `afbbe7e7292c17399bbf4733d9f34a922e6d81f1a914a60d24dc61fcba86cbc9` |
| 落地脚本审 | `069ba36417d138402d07fb0bd2649d55579d38f09b91558c417bec18a0c7f29b` PASS_WITH_CONDITIONS |
| COVER / CMD / DIFF / RECEIPT | `9fd7af74…` / `7b0756db…` / `99d40f9a…` / `617f0481…` |
| VOID / RUN | `8a3b25ba…` / `481bacda…` |
| FROZEN / FROZEN审 / FROZEN RECEIPT / PIN | `8ed43721…` / `bf5234a9…` / `8f43e2f8…` / `4e17ccfc…` |
| who_pays 审 / WHO / who COVER | `55531e12…` / `1032477d…` / `61d9f656…` |
| tz | tz_align_mode=`naive_calendar_day`；base=`05c45917`；patch审=`19cc790f` |
| 叶32 模板 | `4e0f3c00` UNCHANGED |
| 窗期 | `2026-10-27T07:11:00-04:00` → `2026-10-27T08:41:00-04:00`；expires `2026-10-27T08:45:00-04:00` |
| CLI PRIMARY | `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf33_share_unlock_pressure_resid_alpha_build.py --universe HILIQ --window x2 --x2-end 20261009 --allow-real-data --arch-ok-path output/ai_factory/ARCH_RUN_AUTH_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_X2_HILIQ.ok --out output/ai_factory/_leaf33_share_unlock/<ET_TS>/ --sample-dir /tmp/quantlab_leaf33_share_unlock_<ET_TS>`；**无** `--no-overlap-report` |
| FALLBACK | **无**；峰＞1500 / 失败 / ABORT → Exit 94/95 停+上报（禁抬帽） |
| rss 软/硬帽 | **1500** MB；禁抬帽；硬 Exit **94/95** |
| overlap | 强制 `overlap_vs_leaf19_25_27_30_31_32_margin_delta_hk_hold_moneyflow.json`；Jaccard≥0.7 硬拒；ρ>0.5 强度；count≠formal |
| PRIMARY load | **rebal_day_lazy_share_float_close_mktcap_bars**；禁整窗 `logmv_rebal=` 预载 |
| C3 | (a)+加价；close_unadjusted=true；float_ratio_primary_disabled=true；c3_mode=a_plus_pricing |
| mechanism / H / H_back / W / 再平衡 / α | `g1g5_ashare_share_unlock_pressure_resid_v1`；20 / 5 / 20 / 20；`−rank(pressure_resid)` |
| style_cols | mom20,vol20,logADV20 |
| 产物 | `_leaf33_share_unlock/<ET_TS>/` + alpha parquet + `run_meta.json` + overlap JSON |
| 采样 | 仅 `/tmp/quantlab_leaf33_share_unlock_*` |
| 禁 RESTORED | **22** 票：`5774bb6e,02426b73,4bb141c9,fdbaa512,aa25e989,7e239487,5af20222,5ae077fa,3c297052,e107383f,2be59acd,a7d98ac9,8e51de63,3a6caa4f,8bcd79dc,725be3e0,0f50daf7,3c19dd7d,1c32ab1e,6054b3bf,6de02e74,c5ed13df`（含旧 VOID tz；ban_restored_ok_c5ed13df=true） |
| Book-Smoke / X2 ACCEPT / selfcheck | **false** / **false** / **false** |
| peak_proof | **REQUIRED**（after_mask / after_sw / after_share_float_rebal_* / after_close_rebal_* / after_float_mktcap_rebal_* / after_bars_rebal_* / after_logmv_rebal_* / after_daily_concat） |
| `0087c928` / 叶28/29 | 另队；**不在**本 `.ok` |
| MemAvailable@签 | 12498052 kB |

## QUIET / pgrep

| 项 | 值 |
|---|---|
| QUIET 挂时 | `2026-10-27T07:15:32-04:00` reason=`leaf33_share_unlock_pressure_resid_x2_tz_align` holder=`leaf33_SHARE_UNLOCK_PRESSURE_RESID_X2` |
| do_not_lift_until_arch_or_consumed | **true**（本拍不 lift） |
| neq_a18 | **true** |
| pgrep leaf33 share unlock build | 空 |
| 签时 web | empty（prelaunch 仍须 healthz quiet） |
| Arch 代跑 `--allow-real-data` | **未执行** |

## 下一跳

1. **主** MATCH `.ok`+`QUIET` 后令 AI prelaunch 单次 PRIMARY（须在 expires 前；Arch **不代跑**）
2. AI 交实峰回执（alpha sha + run_meta sha + overlap JSON + peak rss 含 after_mask / after_sw / after_share_float_rebal_* / after_close_rebal_* / after_float_mktcap_rebal_* / after_bars_rebal_* / after_logmv_rebal_* / after_daily_concat；峰＞1500→Exit 94/95 停；Jaccard≥0.7→硬拒票）→ Arch 核 CONSUME
3. ≠X2 ACCEPT；≠selfcheck；≠Book-Smoke；不解阻 `0087c928`/叶28/29 另队；**≠A18**；不 RESTORED 22 票（含 `c5ed13df`）；live=false；leo_notify=false

live=false.
