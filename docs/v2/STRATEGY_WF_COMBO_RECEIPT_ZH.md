# 回执：组合层 walk-forward 优化（纸面，未盖章）
- 时间：2026-10-14 01:33 ET；预注册 docs/v2/STRATEGY_WF_COMBO_PREREG_ZH.md（01:25 ET 冻结）。
- 结果：预注册正式路径 0/15 过（筛选无候选）；引擎全量诊断（预注册外）16 组中 S6（cap/ee/eq 50/25/25 集中化）帕累托优于 B4：60万 17.15%/−11.95%，100万 16.37%/−12.66%（B4 15.11%/−13.85%，14.24%/−13.17%）。S6 为事后挑选，WF 规则 D5 未过。
- 引擎：Eng book-smoke，core=0/stock=1/alpha_event=0，strategy_v1 成本开，X2，60万/100万，单进程串行；S0 复现 B4 一致（权重逐行差 0，引擎数字一致）。
- 产物：output/strategy_wf_combo/{SHORT_ZH.md, STATUS.json, compare_table.json, table_ZH.md, screen.json, wf_combo_nav_yearly.png, wf_screen.py, analyze.py, engine_all.sh, weights_*.parquet, engine/*}
- 未动：live、promotion、STATUS/FROZEN_CONFIG（capacity_adv、B4 两轨）、密封窗、任何冻结文件。禁 GP/小盘，L≤1.0。
- 待决：S6 是否作为新纸面候选（需新预注册 + 前向检验，由 Leo 定）。
