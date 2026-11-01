# Arch 叶37 IMAX Lottery Exclusion Overlay X2 selfcheck_v1 · 独立 `.ok` 签发回执

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-27T19:17:08-04:00`（America/New_York） |
| 主令 | 主 ~叶37 X2 selfcheck 独立签窗 OPEN · 认审票 `3d40f713` MATCH · PASS_WITH_CONDITIONS 主裁开窗 · **只签** `.ok`（硬钉脚本 `015e6f06` only；**禁挂 QUIET**；禁代跑；禁改脚本；≠X2 ACCEPT） |
| 审阅 | `3d40f713…` **PASS_WITH_CONDITIONS** |
| CMD | `6f5d48bd…`（禁 `--arch-ok-path`；流程门=新 `.ok`+主窗） |
| COVER / DIFF / RECEIPT | `8c83ba13…` / `2542e7cd…` / `bb616bdb…` |
| mask / meta / overlap / CONSUMED | `2503a41e…` / `e9e9aa1d…` / `8177578f…` / `c0a6b5ae…` |
| live / promotion_approved / leo_notify | **false** / **false** / **false** |

## 结论

**SIGNED** — 独立叶37 IMAX Lottery Exclusion Overlay X2 selfcheck_v1（mechanism=`g1g5_ashare_imax_lottery_exclusion_overlay_v1`；PRIMARY：钉既有 B1_LOWMEM HILIQ×x2 exclusion_mask `2503a41e` → mask-only overlay capacity_adv×mask top_q=0.20 → `leaf_selfcheck_common.evaluate` → `selfcheck_v1.json`；C3=**B** IMAX_proxy；`b1_lowmem=true`；≠叶24 `g1g5_ashare_imax_intraday_v1`）`.ok` 已落盘；**≠ X2 ACCEPT**；**≠ Book-Smoke**；**≠ 复跑 B1 `32605aca` / 基盘 `108aba8f`**；**≠ RESTORED** 三十二票（首项 B1 CONSUMED `b5be1164`；次项 VOID.ABORT_PEAK `4096d401`；+`eb70eef4`+…）；脚本全长 **`015e6f06…` MATCH**；B1 构建 **`32605aca` UNCHANGED / ban_as_live（本窗不跑）**；基盘 **`108aba8f` UNCHANGED / ban_as_live**；模板叶34 **`d210efba` UNCHANGED** / 叶32 **`dcf6b559` UNCHANGED** / common **`218b61cf` UNCHANGED**；叶33 **`afbbe7e7` 只读**；叶35 **`434ff42c` 只读**；叶34 构建 **`482009dc` 只读**；审 **`3d40f713`**；COVER **`8c83ba13`**；CMD **`6f5d48bd`**；DIFF **`2542e7cd`**；SCRIPT_RECEIPT **`bb616bdb`**；Arch CONSUME **`c0a6b5ae`**；FROZEN **`c5927f1b`**；PIN **`e01be34c`**；rss 软/硬帽 **1500** 禁抬 + 硬 ABORT + peak_proof **REQUIRED**；流程门=本 `.ok`+主窗（`--execute` alone 不算授权）；**禁** CLI `--arch-ok-path`（脚本不认该旗；禁复用旧票路径）；sampler 外挂 `/tmp/quantlab_leaf37_x2_selfcheck_*`；盯 decay KEEP 三闸+gates A/B/current；**KEEP 不解阻 X2 ACCEPT**（`45dd87dc`）；**Arch 不代跑**。**QUIET 本拍未挂=ABSENT**（主令明文禁挂；`ban_hang_quiet_this_sign=true`；`quiet_set_at_sign=false`；holder 标识 only=`leaf37_IMAX_LOTTERY_EXCLUSION_OVERLAY_X2_SELFCHECK_V1`）。SELFCHECK_EXECUTED@签=**false**。PIN_GAP **MASK_ONLY_OVERLAY_NO_FULL_ALPHA**。叶36 HOLD 不复开。**≠A18**。`0087c928` **另队不夹带**。leo_notify=**false**。

## 钉点 MATCH 表

| 项 | 期望 | 实测 | 结果 |
|---|---|---|---|
| 脚本 | `015e6f06…` only | `015e6f0666f697d07f33ea33f4572b4e90d099ab6e6bfba74e10c00328e61e61` | **MATCH** |
| 审回执 | `3d40f713` PASS_WITH_CONDITIONS | `3d40f7139c5386c98b9d0a9ce0036087238c008bb9595772c0e780549f22448e` | **MATCH** |
| COVER | `8c83ba13` | `8c83ba135e9e2d675e56b8c47cd82b2ea56aa8189f2ece25477b6cd25769874c` | **MATCH** |
| CMD | `6f5d48bd` | `6f5d48bdc5e3f7f63889e72a140b02d56b937337f92d8ceefd2f630be59632b2` | **MATCH** |
| DIFF | `2542e7cd` | `2542e7cdaa2fe24f18bd78b36284d754197cbe533163056141736c6005ff123c` | **MATCH** |
| SCRIPT_RECEIPT | `bb616bdb` | `bb616bdbb54e2530f24fac8a72f4f8e2e5f7cc6b4f42129a1134de1e1b72cedc` | **MATCH** |
| mask / meta / overlap | `2503a41e` / `e9e9aa1d` / `8177578f` | `2503a41e297442da43cca4db2598acec314c8647af954231e7c49456c0862f62` / `e9e9aa1df45b95cf0e44d995a9151068bd739b5aae4592bc13b6184accfacd2f` / `8177578f72f327fe2d20cd05760459f1a934a3dd903a6cde28651b953e368af8` | **MATCH** |
| Arch CONSUME | `c0a6b5ae` | `c0a6b5ae6a6408a3bae35b84f8daa2c4734a1ce29cdc2a87212d899bd4903c98` | **MATCH** |
| B1 脚本 | `32605aca` UNCHANGED ban_as_live | `32605acac230b777cc02e72f8385f31aa64bafd5fdf2784f9f05c8b567090d0c` | **MATCH** |
| 基盘脚本 | `108aba8f` UNCHANGED ban_as_live | `108aba8f5c3f58f2792d31b36a793ff5251fa732174667e037ffae113eb91f2b` | **MATCH** |
| 模板叶34 / 叶32 / common | `d210efba` / `dcf6b559` / `218b61cf` UNCHANGED | MATCH | **MATCH** |
| 叶33 / 叶35 / 叶34 构建 | `afbbe7e7` / `434ff42c` / `482009dc` 只读 | MATCH | **MATCH** |
| FROZEN / PIN | `c5927f1b` / `e01be34c` | `c5927f1b07a67c4e839c3084202e84f10529a379779a3dfc10ae751487676213` / `e01be34cfedeedffe750e753ace1977071d0b073238ac294fe78d75284ea0c2a` | **MATCH** |
| 拟 .ok 签前 | ABSENT（主令路径无 `_HILIQ_X2` 后缀；≠脚本 PROPOSED 名） | ABSENT | **MATCH** |
| QUIET 签前/签后 | **ABSENT**（本拍禁挂） | ABSENT / ABSENT | **MATCH** |
| ai_factory live `.ok` | 0→1（本签） | 签前 0 / 签后 1 | **MATCH** |
| `_selfcheck/` / `selfcheck_v1.json` | ABSENT | ABSENT → EXECUTED=false | **MATCH** |
| CMD 拟 CLI | 无 `--arch-ok-path`；`… --universe HILIQ --window x2 --execute` | 同左 | **MATCH** |
| forbid 碰撞 | 新 `.ok` sha8 ∉ 三十二票 | `57ab9096` ∉ forbid32（首项 `b5be1164`） | **PASS** |
| pgrep leaf37 selfcheck | 空 | 空 | **MATCH** |
| 窗期 | ≥90min | `2026-10-27T19:17:00-04:00` → `2026-10-27T20:47:00-04:00` / expires `2026-10-27T20:51:00-04:00`；签时 `2026-10-27T19:17:08-04:00` | **IN_WINDOW** |

## 钉

| 项 | 值 |
|---|---|
| `.ok` 路径 | `output/ai_factory/ARCH_RUN_AUTH_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_X2_SELFCHECK_V1.ok` |
| `.ok` sha8 / 全长 | `57ab9096` / `57ab909622f1edaf2c19dd3f40824a20b6ef407b8b3436c9dafe1fabc820fa64` |
| QUIET 路径 | `output/loop/RESEARCH_QUIET.lock` |
| QUIET 状态 | **ABSENT**（本拍**未挂**；`quiet_set_at_sign=false`；`ban_hang_quiet_this_sign=true`） |
| holder（标识 only） | `leaf37_IMAX_LOTTERY_EXCLUSION_OVERLAY_X2_SELFCHECK_V1` |
| 脚本 | `research/leaf37_imax_lottery_exclusion_overlay_x2_selfcheck_v1.py` = `015e6f0666f697d07f33ea33f4572b4e90d099ab6e6bfba74e10c00328e61e61` |
| B1 构建 UNCHANGED ban_as_live | `research/leaf37_imax_lottery_exclusion_overlay_alpha_build_b1_lowmem.py` = `32605acac230b777cc02e72f8385f31aa64bafd5fdf2784f9f05c8b567090d0c` |
| 基盘 UNCHANGED ban_as_live | `research/leaf37_imax_lottery_exclusion_overlay_alpha_build.py` = `108aba8f5c3f58f2792d31b36a793ff5251fa732174667e037ffae113eb91f2b` |
| 模板叶34 / 叶32 / common | `d210efba…` / `dcf6b559…` / `218b61cf…` |
| 审阅 | `3d40f7139c5386c98b9d0a9ce0036087238c008bb9595772c0e780549f22448e` PASS_WITH_CONDITIONS |
| CMD / COVER / DIFF / RECEIPT | `6f5d48bdc5e3f7f63889e72a140b02d56b937337f92d8ceefd2f630be59632b2` / `8c83ba135e9e2d675e56b8c47cd82b2ea56aa8189f2ece25477b6cd25769874c` / `2542e7cdaa2fe24f18bd78b36284d754197cbe533163056141736c6005ff123c` / `bb616bdbb54e2530f24fac8a72f4f8e2e5f7cc6b4f42129a1134de1e1b72cedc` |
| CONSUME / FROZEN / PIN | `c0a6b5ae6a6408a3bae35b84f8daa2c4734a1ce29cdc2a87212d899bd4903c98` / `c5927f1b07a67c4e839c3084202e84f10529a379779a3dfc10ae751487676213` / `e01be34cfedeedffe750e753ace1977071d0b073238ac294fe78d75284ea0c2a` |
| mask / meta / overlap | `2503a41e297442da43cca4db2598acec314c8647af954231e7c49456c0862f62` / `e9e9aa1df45b95cf0e44d995a9151068bd739b5aae4592bc13b6184accfacd2f` / `8177578f72f327fe2d20cd05760459f1a934a3dd903a6cde28651b953e368af8` |
| 窗期 | `2026-10-27T19:17:00-04:00` → `2026-10-27T20:47:00-04:00`；expires `2026-10-27T20:51:00-04:00` |
| CLI PRIMARY | `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf37_imax_lottery_exclusion_overlay_x2_selfcheck_v1.py --universe HILIQ --window x2 --execute` |
| CLI 可选显式钉盘 | `… --mask-path …/exclusion_mask_HILIQ_x2_20261027_183755.parquet --meta-path …/run_meta.json --execute` |
| FALLBACK | **无**；峰＞1500 / 失败 → 硬 ABORT 停+上报（禁抬帽） |
| rss 软/硬 | **1500** / **1500** MB；forbid_raise_rss；hard_abort_on_rss=true |
| PIN_GAP | **MASK_ONLY_OVERLAY_NO_FULL_ALPHA**（IC/ICIR/WF 非本票主交付） |
| PRIMARY | mask-only top_q=**0.20** × capacity_adv（≠α TopN）；C3=B IMAX_proxy；b1_lowmem=true |
| decay KEEP | 盯 KEEP 三闸 + portfolio gates A/B/current；**KEEP 不解阻 X2 ACCEPT**（`45dd87dc`） |
| 采样 | 仅 `/tmp/quantlab_leaf37_x2_selfcheck_*` |
| 产物 | `_selfcheck/` + `leaf_reports/leaf37_imax_lottery/selfcheck_v1.json`（禁覆写钉盘 mask/meta/overlap） |
| 禁 RESTORED | **32** 票：`b5be1164,4096d401,eb70eef4,00eec671,10927bd9,25ae4572,178e90e9,c1b71e64,245df63f,c5ed13df,5774bb6e,81521fb5,02426b73,4bb141c9,fdbaa512,aa25e989,7e239487,5af20222,5ae077fa,3c297052,e107383f,2be59acd,a7d98ac9,8e51de63,3a6caa4f,8bcd79dc,725be3e0,0f50daf7,3c19dd7d,1c32ab1e,6054b3bf,6de02e74` |
| Book-Smoke / X2 ACCEPT / 复跑 B1·基盘 | **false** / **false** / **false** |
| peak_proof | **REQUIRED** |
| MemAvailable@签 | 12536172 kB |
| ≠A18 | ban_touch_a18=true；未触 |
| `0087c928` | 另队；**不在**本 `.ok` |
| leo_notify | **false** |

## CONDITIONS（签文硬钉；主令覆盖审票 §4.3「签时挂 QUIET」→本拍禁挂）

1. approved_cmd 仅 `… --universe HILIQ --window x2 --execute`（可选显式 mask/meta path）；**禁** `--arch-ok-path`
2. 流程门=本 `.ok`+主窗；`--execute` alone 不算授权
3. forbid∋**`b5be1164`**+**`4096d401`**+`eb70eef4`+…（**三十二票**齐；禁 RESTORED/VOID/CONSUMED）
4. rss=1500 禁抬 + 硬 ABORT + peak_proof REQUIRED
5. 钉 mask `2503a41e` / meta `e9e9aa1d` / overlap `8177578f`；PRIMARY=mask-only top_q=0.20×capacity_adv；C3=B IMAX_proxy；b1_lowmem；≠复跑 B1/基盘；≠Book-Smoke；≠X2 ACCEPT；≠叶24
6. sampler 外挂 `/tmp/quantlab_leaf37_x2_selfcheck_*`；**Arch 不代跑**；**本拍禁挂 QUIET**
7. 盯 decay KEEP 三闸 + gates A/B/current；**KEEP 不解阻 X2 ACCEPT**（`45dd87dc`）；叶36 HOLD 不复开
8. `0087c928` 另队不夹带；≠A18；leo_notify=false

## QUIET / pgrep

| 项 | 值 |
|---|---|
| QUIET 本拍 | **未挂 = ABSENT**（主令明文禁挂；覆盖审票 §4.3「签时挂 QUIET」） |
| quiet_set_at_sign | **false** |
| ban_hang_quiet_this_sign | **true** |
| quiet_status_at_sign | **ABSENT** |
| holder（标识 only，未挂 QUIET） | `leaf37_IMAX_LOTTERY_EXCLUSION_OVERLAY_X2_SELFCHECK_V1` |
| neq_a18 | **true** |
| pgrep leaf37 selfcheck / kline/… | 空 |
| SELFCHECK_EXECUTED@签 | **false**（无 `_selfcheck/`、无 `selfcheck_v1.json`） |
| Arch 代跑 `--execute` | **未执行** |

## 下一跳

1. **主** MATCH 本 `.ok`（+ SIGNED 回执；QUIET=ABSENT）后令 AI prelaunch→execute（须在 expires 前；Arch **不代跑**；本签**未挂** QUIET——若主另令挂 QUIET 再挂）
2. AI 交实峰回执（权重 sha + selfcheck_v1.json sha + peak rss + **PIN_GAP MASK_ONLY_OVERLAY_NO_FULL_ALPHA 复述** + decay KEEP outcome + gates A/B/current + ρ_excess 若可得；峰＞1500→硬 ABORT 停）→ Arch 核 CONSUME
3. ≠X2 ACCEPT；≠Book-Smoke；不解阻全量 X2；KEEP 不解阻 ACCEPT；≠复跑 B1 `32605aca`/基盘 `108aba8f`；≠A18；不 RESTORED `b5be1164`/`4096d401`/…（32 票）；`0087c928` 另队；live=false；**leo_notify=false**

live=false.
