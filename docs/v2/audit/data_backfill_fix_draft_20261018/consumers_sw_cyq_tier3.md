# sw_pit / cyq / tier3_daily 的消费方清单（2026-10-18 ET，QuantLab Data，只读 grep）
- 搜索范围：scripts、scripts_eng、quantlab、research（不含 _runner_archive）、output/loop、docs/v2 中的叶子/规格文档。仓库里没有 configs 目录。
- 负责人按路径约定推断：research/intel 属 Intel；research/strategy_* 属 Strategy；quantlab/beta 属 Beta；research/ai_* 属 AI；alpha_labels 属 Alpha。

## A. data/v2/sw_pit（候选表：industry_members_sw_l1/l2_pit、sw2021_classify；实际最新 in_date 为 2026-09-24，manifest built 2026-10-14 04:00）
| 消费方 | 读的表 | 负责人 | 是否检查过期 |
|---|---|---|---|
| research/strategy_fulla_b4_x2.py:253 | sw_pit/industry_members_sw_l1_pit.parquet（in_date/out_date as-of，近似取最后一次名称） | Strategy | 否 |
| research/strategy_hiliq_capadv_b4_x2.py:73, 312 | 同上（load_industry_map 取最后一次名称） | Strategy | 否 |
| research/intel/intel_common.py:172 | 同上 | Intel | 否。只对 mid_large 取最大 session（第 177 行），不检查 sw |
| research/intel/intel_event_study.py:39 | 同上 | Intel | 否 |
| research/intel/intel_c1_gap_split.py:25 | 同上 | Intel | 否 |
| output/loop/alpha_labels.json:1047 | leaf sw_pit_l1l2，ACCEPT_PARTIAL（2026-10-13） | Alpha | 不适用（标签记录，不是读表） |
| scripts/acquire/queue_chain_20261014.py:130 | 读 sw_pit manifest（链式任务汇总） | Data | 否 |
| scripts/nightly_update.py BUNDLE_MAP | 复制 sw_pit 各表进 bundle | Data | 否 |
| docs/v2/WEB_RESEARCH_ROUND3_LEAF8_ZH.md:10 | 判定 sw_pit "不可"作叶子 | Web | 不适用 |
- 说明：行业成员变动本身就稀疏，in_date 最大值为 09-24 不等于数据过期。真正的风险是 10-14 到 10-16 没有成功刷新，期间如有成员变更会被漏掉。以上消费方都不检查 manifest 的 built 时间或 in_date 范围。

## B. cyq（data/v2/tushare_raw/cyq_perf 按日、data/v2/cyq 按月；raw 最新 20261013）
| 消费方 | 读的表 | 负责人 | 是否检查过期 |
|---|---|---|---|
| scripts/acquire/cyq_perf_monthly.py | 生产方 | Data | 写 manifest 的 range |
| scripts/nightly_update.py BUNDLE_MAP | data/v2/cyq/cyq_perf_*.parquet 复制进 bundle | Data | 否 |
| scripts/acquire/queue_chain_20261014.py | 链式任务调用 | Data | 否 |
| docs/v2/WEB_RESEARCH_ROUND3_LEAF8_ZH.md:7、docs/v2/AI_LEAF_CANDIDATES_EXHAUSTED_ZH.md:17 | 判定 cyq "不可"作叶子 | Web / AI | 不适用 |
- 没有发现任何研究或生产代码读取 cyq。

## C. tier3_daily（concept_dc_index/member、concept_ths_index、anns、news、research_report；最新 20261015，concept_ths_index 一个文件都没有）
| 消费方 | 读的表 | 负责人 | 是否检查过期 |
|---|---|---|---|
| scripts/acquire/tier3_daily_snapshot.py | 生产方 | Data | 写入 meta |
| scripts/nightly_update.py bundle() | 当日 tier3 各表复制进 bundle | Data | 文件不存在就跳过，不报警 |
| scripts/fix_sd1/sd1_common.py、test_sd1_common.py | 只出现在门禁的 FORBID 进程名模式里（tier3_daily_snapshot.py），不读数据 | Data | 不适用 |
| docs/v2/WEB_RESEARCH_ROUND3_LEAF8_ZH.md:11 | 判定"不可"（快照只有单日，非满窗） | Web | 不适用 |
| docs/v2/ARCH_LEAF23_24_FIXDIFF_REVIEW_ZH.md:111 | 只记录了进程 142545 | Arch | 不适用 |
- 没有发现任何研究或生产代码读取 tier3_daily。

## D. 另列：data/v2/sw_l1_pit（钉住的 industry_members_sw_l1_tushare，sha 89d4afa3…；与 sw_pit 是不同的表）
- 共 63 个代码文件引用（不含 _runner_archive）。主要使用方：
  - Eng/Strategy：quantlab/portfolio/research_loop.py、v2_s2_book.py、quantlab/universe/mask.py、d1_masks.py
  - Beta：quantlab/beta/sleeve.py 和 configs/smallcap_standalone_v1.json
  - AI：research/ai_factor_* 系列约 30 个文件，以及 ai_cs_panel_build.py
  - Alpha：research/g1g5_*、capital_flow_*、mainbook_v2_a2_sealed、p8_events_sealed、tradable_ic_v1、netret_midlarge_p7、optimizer_core_x2_run_v1_4
  - Data：scripts/acquire/promotion_*、tushare_relay_pull、sw_pit_refresh（只读注释）、data_progress_dashboard、sd1_common（pin）
- research/strategy_* 和 research/intel 两类文件同时引用了两张表。
- 这张表是冻结、钉住的，sw 补数不会写它（sw_pit_refresh.py 第 51 行明确写着不覆盖），所以这些消费方不受 10-14 到 10-16 sw 缺口影响。

完整文件列表：
```
quantlab/beta/configs/smallcap_standalone_v1.json
quantlab/beta/sleeve.py
quantlab/portfolio/research_loop.py
quantlab/portfolio/v2_s2_book.py
quantlab/universe/d1_masks.py
quantlab/universe/mask.py
quantlab/v2_schemas.py
quantlab/v2_smoke.py
research/ai_cs_panel_build.py
research/ai_factor_gp_reopen_hardgate_v10_away.py
research/ai_factor_gp_reopen_hardgate_v10b_resume.py
research/ai_factor_gp_reopen_hardgate_v11_struct.py
research/ai_factor_gp_reopen_hardgate_v12_struct.py
research/ai_factor_gp_reopen_hardgate_v13_event.py
research/ai_factor_gp_reopen_hardgate_v14_event_deep.py
research/ai_factor_gp_reopen_hardgate_v15_event_deep.py
research/ai_factor_gp_reopen_hardgate_v16_struct_event.py
research/ai_factor_gp_reopen_hardgate_v17_struct_event.py
research/ai_factor_gp_reopen_hardgate_v17b_struct_event.py
research/ai_factor_gp_reopen_hardgate_v18_etf_resid.py
research/ai_factor_gp_reopen_hardgate_v19_etf_newleaf.py
research/ai_factor_gp_reopen_hardgate_v20_dual_track.py
research/ai_factor_gp_reopen_hardgate_v23_dual_price.py
research/ai_factor_gp_reopen_hardgate_v24_track_a_stock.py
research/ai_factor_gp_reopen_hardgate_v25_track_a_stock.py
research/ai_factor_gp_reopen_hardgate_v26_track_a_stock.py
research/ai_factor_gp_reopen_hardgate_v28_newleaf_friction.py
research/ai_factor_gp_reopen_hardgate_v6b_resid.py
research/ai_factor_gp_reopen_hardgate_v6c_resid_fix.py
research/ai_factor_gp_reopen_hardgate_v7_diversify.py
research/ai_factor_gp_reopen_hardgate_v8_cov.py
research/ai_factor_gp_reopen_hardgate_v9_dense_micro.py
research/ai_factor_l1c_ann_insider_wf.py
research/ai_factor_l1d_shortlist_coverage_impact.py
research/ai_factor_l1f_wf_stability.py
research/ai_factor_v2e_plus_wf_cov.py
research/attrib_v2/common.py
research/capital_flow_cs3_confirm.py
research/capital_flow_cs3_rerun.py
research/capital_flow_sealed_v1.py
research/g1g5_major_contract_growth_events.py
research/g1g5_nontextbook_weights.py
research/g1g5_overnight_idio_ivol_alpha.py
research/g1g5_overnight_idio_ivol_lowto_alpha.py
research/g1g5_tech_qual_cert_events.py
research/intel/intel_c1_gap_split.py
research/intel/intel_common.py
research/intel/intel_event_study.py
research/intel/weekly/paper_exposure.py
research/mainbook_v2_a2_sealed.py
research/netret_midlarge_p7.py
research/optimizer_core_x2_run_v1_4.py
research/p8_events_sealed.py
research/strategy_fulla_b4_x2.py
research/strategy_hiliq_capadv_b4_x2.py
research/tradable_ic_v1.py
scripts/acquire/promotion_acceptance.py
scripts/acquire/promotion_watch.py
scripts/acquire/sw_pit_refresh.py
scripts/acquire/tushare_relay_pull.py
scripts/data_progress_dashboard.py
scripts/fix_sd1/sd1_common.py
scripts/nightly_update.py
```
