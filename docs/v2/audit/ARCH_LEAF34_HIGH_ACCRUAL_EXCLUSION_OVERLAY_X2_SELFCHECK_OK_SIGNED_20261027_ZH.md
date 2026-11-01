# Arch 叶34 High Accrual Exclusion Overlay X2 selfcheck_v1 · 独立 `.ok` 签发回执

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-27T11:43:33-04:00`（America/New_York） |
| 主令 | 主 11:35 ET priority · 叶34 X2 selfcheck 独立签窗 OPEN · 立即 SIGN |
| 审阅 | `e2902e64…` **PASS_WITH_CONDITIONS** |
| CMD | `4255ad33…`（禁 `--arch-ok-path`；流程门=新 `.ok`+主窗） |
| live / promotion_approved | **false** / **false** |

## 结论

**SIGNED** — 独立叶34 High Accrual Exclusion Overlay X2 selfcheck_v1（PRIMARY：钉既有 HILIQ×x2 exclusion_mask `8b5d6d24` → mask-only overlay capacity_adv×mask top_q=0.20 → `leaf_selfcheck_common.evaluate` → `selfcheck_v1.json`）`.ok` 已落盘；**≠ X2 ACCEPT**；**≠ Book-Smoke**；**≠ 重跑 alpha/mask 构建**；**≠ RESTORED** 二十五票（首项叶34 X2 构建 CONSUMED `c1b71e64`；次项叶33 VOID coverage `245df63f`；三项叶33 VOID tz `c5ed13df`；四项叶32 selfcheck `5774bb6e`；及 classic20 + 叶33 diag `81521fb5`）；脚本全长 **`d210efba…` MATCH**；构建 **`482009dc` UNCHANGED**；模板叶32 **`dcf6b559` UNCHANGED** / 叶31 **`e1fe578c` UNCHANGED** / common **`218b61cf` UNCHANGED**；叶33 **`afbbe7e7` 只读**；审 **`e2902e64`**；COVER **`0bf02521`**；CMD **`4255ad33`**；DIFF **`a1a6689d`**；SCRIPT_RECEIPT **`a5467d7d`**；Arch CONSUME **`fea9b3ff`**；FROZEN **`8be1099e`**；PIN **`bb418e6a`**；rss 软/硬帽 **1500** 禁抬 + 硬 ABORT + peak_proof **REQUIRED**；流程门=本 `.ok`+主窗（`--execute` alone 不算授权）；**禁** CLI `--arch-ok-path`；sampler 外挂 `/tmp/quantlab_leaf34_x2_selfcheck_*`；盯 decay KEEP 三闸+gates A/B/current；**KEEP 不解阻 X2 ACCEPT**（`45dd87dc`）；**Arch 不代跑**。QUIET **已挂且保留**供 AI prelaunch（本回合不 lift；≠A18）。PRIMARY only；**无同票 FALLBACK**；峰＞1500→硬 ABORT 停+上报（禁抬帽）。SELFCHECK_EXECUTED@签=**false**。PIN_GAP **MASK_ONLY_OVERLAY_NO_FULL_ALPHA**。**≠A18**。`0087c928` **另队不夹带**。**不报 Leo**。

## 钉点 MATCH 表

| 项 | 期望 | 实测 | 结果 |
|---|---|---|---|
| 脚本 | `d210efba…` | `d210efba27ff3b45d3da88faa3f0767adc4d6b5481420f48a31bf6e77e38f7f6` | **MATCH** |
| CMD | `4255ad33` | `4255ad338bec4bf07d5c84b20a2b857a8e477334487065a86d05ab7737768860` | **MATCH** |
| COVER | `0bf02521` | `0bf0252123d09e61a483ac9b9a9dcc8ebd6cb47ce14d6aef1f8fd62046a1bd03` | **MATCH** |
| SCRIPT_RECEIPT | `a5467d7d` | `a5467d7d80237220fea0545db649ef1fa8044656c1aceb5af210d7a37728f1bb` | **MATCH** |
| 审回执 | `e2902e64` PASS_WITH_CONDITIONS | `e2902e649c209fd3ade4b9d2d8adf394ca6df62ab22eb5c4137c307a95a1c90a` | **MATCH** |
| DIFF | `a1a6689d` | `a1a6689dff0ef55de117c7712d7210986fbef3e086947ada5540330f49fd0819` | **MATCH** |
| mask | `8b5d6d24` | `8b5d6d247d8f3968f5fef521aa5d08891f6f6f6c8626dd761c7313bc0d71dabb` | **MATCH** |
| overlap / meta | `77368c8f` / `4fc6108d` | `77368c8fed1f7c167dfa51f4aa2e94e9b405236bf388c8f20f95365613e72fb7` / `4fc6108d64ca5a2e112b04fbb468c9d95e554cf8498ba03fc13828c2ef7ee7ad` | **MATCH** |
| 构建脚本 | `482009dc` UNCHANGED | `482009dc697cbf74b369cbf3fb035f1fc447a4af9339de8abf283f3ed4e971bc` | **MATCH** |
| 模板叶32 selfcheck | `dcf6b559` UNCHANGED | `dcf6b559165e43dcaa56df8adc3cb5d9574b6b55cc5ba20cf39d97b0285cda4f` | **MATCH** |
| 模板叶31 / common | `e1fe578c` / `218b61cf` | `e1fe578ca70bd61f6c98bd849357beecb918f9e88f0732ac6bbc98dcfb0d4b38` / `218b61cfbf2bf0b6bb133ef030aa2d7ff20b3eafda9724aa98c9f3b1fa5cb054` | **MATCH** |
| 叶33 正式只读 | `afbbe7e7` | `afbbe7e7292c17399bbf4733d9f34a922e6d81f1a914a60d24dc61fcba86cbc9` | **MATCH** |
| Arch CONSUME | `fea9b3ff` | `fea9b3ff5ac3824f5cb7e19fe27753372fc75da6ab72f82f42620cef01fd666c` | **MATCH** |
| FROZEN / PIN | `8be1099e` / `bb418e6a` | `8be1099e73c6029ad2ddcbe7a18a28fc5a27cc03acfb91cba048e26b7867f815` / `bb418e6ae8ee7fd2b0cfc6816360bcb7bb197537dc1aac44fcfb05d375224e9b` | **MATCH** |
| 拟 .ok 签前 | ABSENT | ABSENT | **MATCH** |
| QUIET 签前 | ABSENT | ABSENT | **MATCH** |
| live leaf34 selfcheck `.ok` | 0 | 0→1（本签） | **MATCH** |
| `_selfcheck/` / `selfcheck_v1.json` | ABSENT | ABSENT → EXECUTED=false | **MATCH** |
| CMD 拟 CLI | 无 `--arch-ok-path`；`… --universe HILIQ --window x2 --execute` | 同左 | **MATCH** |
| forbid 碰撞 | 新 `.ok` sha8 ∉ 二十五票 | `178e90e9` ∉ forbid | **PASS** |
| pgrep leaf34 selfcheck | 空 | 空 | **MATCH** |
| 窗期 | ≥90min | `2026-10-27T11:43:00-04:00` → `2026-10-27T13:13:00-04:00` / expires `2026-10-27T13:17:00-04:00`；签时 `2026-10-27T11:43:33-04:00` | **IN_WINDOW** |

## 钉

| 项 | 值 |
|---|---|
| `.ok` 路径 | `output/ai_factory/ARCH_RUN_AUTH_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_X2_SELFCHECK_V1_HILIQ_X2.ok` |
| `.ok` sha8 / 全长 | `178e90e9` / `178e90e905466abfea88186967fdcba5dbb4600e67d969452b68f3afd6c3671d` |
| QUIET 路径 | `output/loop/RESEARCH_QUIET.lock` |
| QUIET sha8 / 全长 | `3fce510e` / `3fce510eea7c4594904e85402c0c5f17df5310f0b6ad4d26dd4c3c5c2d52c2de` |
| QUIET holder | `leaf34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_X2_SELFCHECK_V1`（含 leaf34_selfcheck；≠A18） |
| 脚本 | `research/leaf34_high_accrual_exclusion_overlay_x2_selfcheck_v1.py` = `d210efba27ff3b45d3da88faa3f0767adc4d6b5481420f48a31bf6e77e38f7f6` |
| 构建脚本 UNCHANGED | `research/leaf34_high_accrual_exclusion_overlay_alpha_build.py` = `482009dc697cbf74b369cbf3fb035f1fc447a4af9339de8abf283f3ed4e971bc` |
| 模板叶32 / 叶31 / common | `dcf6b559…` / `e1fe578c…` / `218b61cf…` |
| 审阅 | `e2902e649c209fd3ade4b9d2d8adf394ca6df62ab22eb5c4137c307a95a1c90a` PASS_WITH_CONDITIONS |
| CMD / COVER / DIFF / RECEIPT | `4255ad338bec4bf07d5c84b20a2b857a8e477334487065a86d05ab7737768860` / `0bf0252123d09e61a483ac9b9a9dcc8ebd6cb47ce14d6aef1f8fd62046a1bd03` / `a1a6689dff0ef55de117c7712d7210986fbef3e086947ada5540330f49fd0819` / `a5467d7d80237220fea0545db649ef1fa8044656c1aceb5af210d7a37728f1bb` |
| CONSUME / FROZEN / PIN | `fea9b3ff5ac3824f5cb7e19fe27753372fc75da6ab72f82f42620cef01fd666c` / `8be1099e73c6029ad2ddcbe7a18a28fc5a27cc03acfb91cba048e26b7867f815` / `bb418e6ae8ee7fd2b0cfc6816360bcb7bb197537dc1aac44fcfb05d375224e9b` |
| mask / overlap / meta | `8b5d6d247d8f3968f5fef521aa5d08891f6f6f6c8626dd761c7313bc0d71dabb` / `77368c8fed1f7c167dfa51f4aa2e94e9b405236bf388c8f20f95365613e72fb7` / `4fc6108d64ca5a2e112b04fbb468c9d95e554cf8498ba03fc13828c2ef7ee7ad` |
| 窗期 | `2026-10-27T11:43:00-04:00` → `2026-10-27T13:13:00-04:00`；expires `2026-10-27T13:17:00-04:00` |
| CLI PRIMARY | `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf34_high_accrual_exclusion_overlay_x2_selfcheck_v1.py --universe HILIQ --window x2 --execute` |
| CLI 可选显式钉盘 | `… --mask-path …/exclusion_mask_HILIQ_x2_20261027_105958.parquet --meta-path …/run_meta.json --execute` |
| FALLBACK | **无**；峰＞1500 / 失败 → 硬 ABORT 停+上报（禁抬帽） |
| rss 软/硬 | **1500** / **1500** MB；forbid_raise_rss；hard_abort_on_rss=true |
| PIN_GAP | **MASK_ONLY_OVERLAY_NO_FULL_ALPHA**（IC/ICIR/WF 非本票主交付） |
| PRIMARY | mask-only top_q=**0.20** × capacity_adv（≠α TopN） |
| decay KEEP | 盯 KEEP 三闸 + portfolio gates A/B/current；**KEEP 不解阻 X2 ACCEPT**（`45dd87dc`） |
| 采样 | 仅 `/tmp/quantlab_leaf34_x2_selfcheck_*` |
| 产物 | `_selfcheck/` + `leaf_reports/leaf34_high_accrual/selfcheck_v1.json`（禁覆写钉盘 mask/meta/overlap） |
| 禁 RESTORED | 二十五票：`c1b71e64,245df63f,c5ed13df,5774bb6e,02426b73,4bb141c9,fdbaa512,aa25e989,7e239487,5af20222,5ae077fa,3c297052,e107383f,2be59acd,a7d98ac9,8e51de63,3a6caa4f,8bcd79dc,725be3e0,0f50daf7,3c19dd7d,1c32ab1e,6054b3bf,6de02e74,81521fb5` |
| Book-Smoke / X2 ACCEPT / 重跑构建 | **false** / **false** / **false** |
| peak_proof | **REQUIRED** |
| MemAvailable@签 | 12775928 kB |
| ≠A18 | ban_touch_a18_ok_a62881b9=true；未触 |
| `0087c928` | 另队；**不在**本 `.ok` |

## CONDITIONS（签文硬钉）

1. approved_cmd 仅 `… --universe HILIQ --window x2 --execute`（可选显式 mask/meta path）；**禁** `--arch-ok-path`
2. 流程门=本 `.ok`+主窗；`--execute` alone 不算授权
3. forbid∋`c1b71e64`+`245df63f`+`c5ed13df`+`5774bb6e`+二十票(+`81521fb5`)（二十五票齐）
4. rss=1500 禁抬 + 硬 ABORT + peak_proof REQUIRED
5. 钉 mask `8b5d6d24`；PRIMARY=mask-only top_q=0.20×capacity_adv；≠重跑构建；≠Book-Smoke；≠X2 ACCEPT
6. sampler 外挂 `/tmp/quantlab_leaf34_x2_selfcheck_*`；Arch 不代跑
7. 盯 decay KEEP 三闸 + gates A/B/current；**KEEP 不解阻 X2 ACCEPT**（`45dd87dc`）
8. `0087c928` 另队不夹带；≠A18

## QUIET / pgrep

| 项 | 值 |
|---|---|
| QUIET 挂时 | `2026-10-27T11:43:33-04:00` reason=leaf34_high_accrual_exclusion_overlay_x2_selfcheck holder=`leaf34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_X2_SELFCHECK_V1` |
| do_not_lift_until_arch_or_consumed | **true**（本拍不 lift） |
| neq_a18 | **true**（未触 `_lifted` 旧 A18 QUIET） |
| pgrep leaf34 selfcheck / kline/… | 空 |
| SELFCHECK_EXECUTED@签 | **false**（无 `_selfcheck/`、无 `selfcheck_v1.json`） |

## 下一跳

1. **主** MATCH `.ok`+`QUIET`+本回执后令 AI prelaunch→execute（须在 expires 前；Arch **不代跑**）
2. AI 交实峰回执（权重 sha + selfcheck_v1.json sha + peak rss + **PIN_GAP MASK_ONLY_OVERLAY_NO_FULL_ALPHA 复述** + decay KEEP outcome + gates A/B/current + ρ_excess 若可得；峰＞1500→硬 ABORT 停）→ Arch 核 CONSUME
3. ≠X2 ACCEPT；≠Book-Smoke；不解阻全量 X2；KEEP 不解阻 ACCEPT；≠A18；不 RESTORED `c1b71e64`/`245df63f`/`c5ed13df`/`5774bb6e`/`81521fb5`；`0087c928` 另队；live=false；**不报 Leo**

live=false.
