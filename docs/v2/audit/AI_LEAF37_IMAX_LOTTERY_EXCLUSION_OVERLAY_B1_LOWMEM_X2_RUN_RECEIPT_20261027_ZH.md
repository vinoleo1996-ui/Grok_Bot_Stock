# AI · 叶37 B1_LOWMEM X2 RUN_RECEIPT · 2026-10-27

- status: **PASS**
- rc: **0**
- ET_TS: `20261027_183719`
- OUT: `output/ai_factory/_leaf37_imax_lottery/20261027_183719/`
- pid: `795437`
- wall_et: 2026-10-27 18:39:27 EDT
- leo_notify: **false**；live: **false**；≠X2 ACCEPT；book_smoke: false
- QUIET: **未 lift**（仍在位）

## MATCH pins（跑后复核）

| pin | sha8 | 全长 | 状态 |
|---|---|---|---|
| `.ok` | `b5be1164` | `b5be11642107551e241578c41907105763a4a92009fa3a91a0bc810dad453ff0` | 仍在位 MATCH |
| QUIET | `a616211d` | `a616211dd0cdfc06a60f8b40c095c2f543b4f53f886fef6761a8034d6b2d054e` | **未 lift** MATCH |
| 脚本 B1 | `32605aca` | `32605acac230b777cc02e72f8385f31aa64bafd5fdf2784f9f05c8b567090d0c` | MATCH only |
| 基盘 | `108aba8f` | `108aba8f5c3f58f2792d31b36a793ff5251fa732174667e037ffae113eb91f2b` | **UNCHANGED 禁跑** |
| RUNNING_ACK | `08652c66` | `08652c663911a508da9f9b6dcad76495c25901ae650cfbd80aec62c2ec343fd9` | MATCH |
| SIGNED / 审 | `7b3bd298` / `b403a7e5` | — | 未改 |
| COVER / CMD / DIFF / RECEIPT(脚本) | `a4bfa39d` / `286e2104` / `6d61fd79` / `46f4192d` | — | **COVER 未改**（仍为签前草稿） |
| VOID / FROZEN / PIN | `998171e1` / `c5927f1b` / `e01be34c` | — | 未改 |
| 叶33 / 叶35 / 叶34 | `afbbe7e7` / `434ff42c` / `482009dc` | — | UNCHANGED |
| 叶36 | HOLD | — | 不复开 |

## 跑果摘要

- universe=**HILIQ**；window=**x2**；x2-end=**20261009**
- PRIMARY=mask-only；top_q=**0.20**；C3=**B**；full_residual_e_id=**false**
- b1_lowmem=**true**；rss_limit_mb=**1500**（未抬）
- peak_kb=**1107536**（≈1081.6 MiB）＜ soft/hard=**1536000**；split=**1131520**；c4=**1331200**
- overlap_any_jaccard_hard_reject=**false**；overlap_any_required_pin_gap=**false**（leaf36 disclose=HOLD_CLOSED 记 pin_gaps 但非 hard PIN_GAP）
- OK 行：`OK leaf37_imax_lottery_exclusion_overlay universe=HILIQ window=x2 final=output/ai_factory/_leaf37_imax_lottery/20261027_183719/exclusion_mask_HILIQ_x2_20261027_183755.parquet peak_kb=1107536 overlap_hard_reject=False pin_gap=False`
- 禁项遵守：未跑基盘；未 `--no-overlap-report`；未 FULLA；未抬 rss；未 RESTORED；未擅 lift QUIET；未自签；未 git commit

## 产物 sha

| 产物 | sha8 | sha256 | bytes |
|---|---|---|---|
| mask `exclusion_mask_HILIQ_x2_20261027_183755.parquet` | `2503a41e` | `2503a41e297442da43cca4db2598acec314c8647af954231e7c49456c0862f62` | 5129093 |
| overlap `overlap_vs_leaf18_18v_27_hard_24_34_35_36_disclose.json` | `8177578f` | `8177578f72f327fe2d20cd05760459f1a934a3dd903a6cde28651b953e368af8` | 12152 |
| run_meta `run_meta.json` | `e9e9aa1d` | `e9e9aa1df45b95cf0e44d995a9151068bd739b5aae4592bc13b6184accfacd2f` | 7623 |
| run.log `run.log` | `9773df94` | `9773df94e75b5b99c29ff9fd6adfbe7ec274c4911b65801f144239d8c83e86d2` | 11257 |
| alpha | — | — | 无独立 alpha parquet（PRIMARY=mask-only；mask 含 mask/alpha/imax_proxy 列） |

run_meta 钉：arch_ok_sha8=`b5be1164`；script_sha8=`32605aca`；exclusion_mask_sha256=`2503a41e297442da43cca4db2598acec314c8647af954231e7c49456c0862f62`；live=false；x2_accept=false。

## peak_proof 全序列（REQUIRED）

soft=1536000 / split=1131520 / c4=1331200 / hard=1536000；final peak_kb=**1107536**。

含 `after_panel_year_*` / `after_r_id_year_*` / `after_imax_instr_chunk_*` / `after_panel_imax` / `after_mask*`（含 cs_rebal） / `after_daily_concat` / month_chunk_*（日志阶段名 `after_panel_imax` 对应 IMAX_proxy 构建后；无独立字面 `after_imax_proxy` 标签）。

```
STAGE build_start ru_maxrss=107236
RSS_CHECK build_start peak_kb=107440 vmrss_kb=107440 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_mask peak_kb=608612 vmrss_kb=608612 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_panel_year_2023 peak_kb=717176 vmrss_kb=604880 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_r_id_year_2023 peak_kb=717176 vmrss_kb=609104 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_panel_year_2024 peak_kb=721584 vmrss_kb=583044 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_r_id_year_2024 peak_kb=759136 vmrss_kb=674220 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_panel_year_2025 peak_kb=780088 vmrss_kb=708440 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_r_id_year_2025 peak_kb=843304 vmrss_kb=648220 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_panel_year_2026 peak_kb=843304 vmrss_kb=704056 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_r_id_year_2026 peak_kb=843304 vmrss_kb=734996 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_r_id peak_kb=843304 vmrss_kb=734996 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_imax_instr_chunk_000 peak_kb=843304 vmrss_kb=814840 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_imax_instr_chunk_001 peak_kb=843304 vmrss_kb=814840 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_imax_instr_chunk_002 peak_kb=843304 vmrss_kb=814840 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_imax_instr_chunk_003 peak_kb=843304 vmrss_kb=814840 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_imax_instr_chunk_004 peak_kb=843304 vmrss_kb=634872 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_imax_instr_chunk_005 peak_kb=843304 vmrss_kb=636280 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_imax_instr_chunk_006 peak_kb=843304 vmrss_kb=636308 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_imax_instr_chunk_007 peak_kb=843304 vmrss_kb=636364 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_imax_instr_chunk_008 peak_kb=843304 vmrss_kb=636388 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_imax_instr_chunk_009 peak_kb=843304 vmrss_kb=636436 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_imax_instr_chunk_010 peak_kb=843304 vmrss_kb=636436 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_imax_instr_chunk_011 peak_kb=843304 vmrss_kb=636436 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_imax_instr_chunk_012 peak_kb=843304 vmrss_kb=627740 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_imax_instr_chunk_013 peak_kb=843304 vmrss_kb=627740 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_imax_instr_chunk_014 peak_kb=843304 vmrss_kb=627740 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_imax_instr_chunk_015 peak_kb=843304 vmrss_kb=627740 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_imax_instr_chunk_016 peak_kb=843304 vmrss_kb=627688 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_imax_instr_chunk_017 peak_kb=843304 vmrss_kb=627692 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_imax_instr_chunk_018 peak_kb=843304 vmrss_kb=627700 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_imax_instr_chunk_019 peak_kb=843304 vmrss_kb=627704 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_imax_instr_chunk_020 peak_kb=843304 vmrss_kb=470948 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_panel_imax peak_kb=843304 vmrss_kb=500280 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_mask_cs_rebal_20240603 peak_kb=1107536 vmrss_kb=875188 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_mask_cs_rebal_20240702 peak_kb=1107536 vmrss_kb=875240 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_mask_cs_rebal_20240730 peak_kb=1107536 vmrss_kb=878788 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_mask_cs_rebal_20240827 peak_kb=1107536 vmrss_kb=878804 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_mask_cs_rebal_20240926 peak_kb=1107536 vmrss_kb=744336 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_mask_cs_rebal_20241031 peak_kb=1107536 vmrss_kb=748724 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_mask_cs_rebal_20241128 peak_kb=1107536 vmrss_kb=748760 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_mask_cs_rebal_20241226 peak_kb=1107536 vmrss_kb=749788 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_mask_cs_rebal_20250124 peak_kb=1107536 vmrss_kb=750832 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_mask_cs_rebal_20250303 peak_kb=1107536 vmrss_kb=751484 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_mask_cs_rebal_20250331 peak_kb=1107536 vmrss_kb=752344 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_mask_cs_rebal_20250429 peak_kb=1107536 vmrss_kb=753324 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_mask_cs_rebal_20250530 peak_kb=1107536 vmrss_kb=754236 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_mask_cs_rebal_20250630 peak_kb=1107536 vmrss_kb=755148 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_mask_cs_rebal_20250728 peak_kb=1107536 vmrss_kb=756016 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_mask_cs_rebal_20250825 peak_kb=1107536 vmrss_kb=757120 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_mask_cs_rebal_20250922 peak_kb=1107536 vmrss_kb=758300 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_mask_cs_rebal_20251028 peak_kb=1107536 vmrss_kb=759524 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_mask_cs_rebal_20251125 peak_kb=1107536 vmrss_kb=760628 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_mask_cs_rebal_20251223 peak_kb=1107536 vmrss_kb=761668 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_mask_cs_rebal_20260122 peak_kb=1107536 vmrss_kb=762740 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_mask_cs_rebal_20260227 peak_kb=1107536 vmrss_kb=763792 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_mask_cs_rebal_20260327 peak_kb=1107536 vmrss_kb=764992 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_mask_cs_rebal_20260427 peak_kb=1107536 vmrss_kb=766104 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_mask_cs_rebal_20260528 peak_kb=1107536 vmrss_kb=767092 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_mask_cs_rebal_20260626 peak_kb=1107536 vmrss_kb=768124 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_mask_cs_rebal_20260724 peak_kb=1107536 vmrss_kb=769200 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_mask_cs_rebal_20260821 peak_kb=1107536 vmrss_kb=770248 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_mask_cs_rebal_20260918 peak_kb=1107536 vmrss_kb=771196 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_mask_cs_rebal_20261009 peak_kb=1107536 vmrss_kb=772112 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK month_chunk_000_2024-06 peak_kb=1107536 vmrss_kb=571388 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK month_chunk_001_2024-07 peak_kb=1107536 vmrss_kb=572048 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK month_chunk_002_2024-08 peak_kb=1107536 vmrss_kb=572384 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK month_chunk_003_2024-09 peak_kb=1107536 vmrss_kb=500512 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK month_chunk_004_2024-10 peak_kb=1107536 vmrss_kb=500924 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK month_chunk_005_2024-11 peak_kb=1107536 vmrss_kb=502104 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK month_chunk_006_2024-12 peak_kb=1107536 vmrss_kb=502920 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK month_chunk_007_2025-01 peak_kb=1107536 vmrss_kb=503248 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK month_chunk_008_2025-02 peak_kb=1107536 vmrss_kb=503536 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK month_chunk_009_2025-03 peak_kb=1107536 vmrss_kb=503724 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK month_chunk_010_2025-04 peak_kb=1107536 vmrss_kb=503176 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK month_chunk_011_2025-05 peak_kb=1107536 vmrss_kb=503384 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK month_chunk_012_2025-06 peak_kb=1107536 vmrss_kb=503556 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK month_chunk_013_2025-07 peak_kb=1107536 vmrss_kb=503248 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK month_chunk_014_2025-08 peak_kb=1107536 vmrss_kb=503840 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK month_chunk_015_2025-09 peak_kb=1107536 vmrss_kb=505016 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK month_chunk_016_2025-10 peak_kb=1107536 vmrss_kb=503180 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK month_chunk_017_2025-11 peak_kb=1107536 vmrss_kb=504412 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK month_chunk_018_2025-12 peak_kb=1107536 vmrss_kb=504736 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK month_chunk_019_2026-01 peak_kb=1107536 vmrss_kb=503204 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK month_chunk_020_2026-02 peak_kb=1107536 vmrss_kb=503756 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK month_chunk_021_2026-03 peak_kb=1107536 vmrss_kb=504532 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK month_chunk_022_2026-04 peak_kb=1107536 vmrss_kb=503424 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK month_chunk_023_2026-05 peak_kb=1107536 vmrss_kb=504056 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK month_chunk_024_2026-06 peak_kb=1107536 vmrss_kb=504428 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK month_chunk_025_2026-07 peak_kb=1107536 vmrss_kb=503144 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK month_chunk_026_2026-08 peak_kb=1107536 vmrss_kb=503712 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK month_chunk_027_2026-09 peak_kb=1107536 vmrss_kb=503796 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK month_chunk_028_2026-10 peak_kb=1107536 vmrss_kb=503944 soft=1536000 split=1131520 c4=1331200 hard=1536000
RSS_CHECK after_daily_concat peak_kb=1107536 vmrss_kb=631332 soft=1536000 split=1131520 c4=1331200 hard=1536000
OK leaf37_imax_lottery_exclusion_overlay universe=HILIQ window=x2 final=output/ai_factory/_leaf37_imax_lottery/20261027_183719/exclusion_mask_HILIQ_x2_20261027_183755.parquet peak_kb=1107536 overlap_hard_reject=False pin_gap=False
```

## COVER

未更新。COVER 草稿仍为签前 **`a4bfa39d`**（本拍仅真跑回执，不改 COVER/CMD/DIFF）。

## 硬禁重申

禁跑基盘 `108aba8f`；禁 RESTORED `4096d401`+`eb70eef4`+`00eec671`+`10927bd9`+`25ae4572`+旧票；禁抬 rss；禁 `--no-overlap-report`；禁 FULLA；禁 Book-Smoke；禁自签 `.ok`；禁擅 lift QUIET；禁 git commit；**≠X2 ACCEPT**；leo_notify=false；live=false。待 Arch CONSUME/VOID。
