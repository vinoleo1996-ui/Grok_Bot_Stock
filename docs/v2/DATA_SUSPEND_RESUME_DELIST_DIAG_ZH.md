# 停复牌与退市诊断（D-1~D-4）——事故后重写版

更正（01:2x ET）：上一版说的"回滚、文件丢失"是误报。当时读到的是 box 重启后还没恢复完的状态，恢复约在 01:14 ET 完成。复核后，所列输入（v1 cs_panel、ai_cs_panel_build.py、掩码脚本、tier1_materialize.py、stock_delisted.parquet、daily 到 20261016）都在，只有 output/diag 的明细是空的。正式方案见 DATA_CS_PANEL_RESUME_REBUILD_PLAN_ZH.md 和 DATA_SUSPEND_DELIST_FIX_PLAN_ZH.md。

## D-1 cs_panel 缺复牌首日
根因：ai_cs_panel_build.py 只保留 HI_LIQ 掩码中 fulla|in_universe 的行；掩码 strategy_hiliq_universe_v1.py:148 定义 suspended = suspend_d当日S | ~bar_prev，复牌首日必然被标成停牌，所以被丢掉。daily 和 asof 层都有这一行（002445.SZ 2026-03-09、002090.SZ 2025-07-23、603007.SH 2026-04-21、300658.SZ 2026-01-19 都核过）。2018–2026 共 4971 次复牌，cs_panel 收录 0 次，应补 2865 次（2024 年以来 734 次）。
方案：掩码不改；新出 cs_panel_v2_resumefix，是 v1 的超集。is_resume_day = 掩码 suspended & 当日 vol>0 & 当日无全天 S；fulla_v2 = fulla_v1 | (is_resume_day & 非ST & 非次新 & adv20≥3e6)；新增 is_resume_day、intraday_halt、hiliq_carry 三列；按年分块，RSS<1.5GB。脚本与方案以 docs/v2/DATA_CS_PANEL_RESUME_REBUILD_PLAN_ZH.md r3（回应 Arch r2）为准；此处计数均为 .ok 前的参考值，作废，以授权后回执为准。

## D-2 002445.SZ 2026-08-24 误标停牌
根因：tier1_materialize.py:62-72 只要 suspend_d 当日有该股任一记录就置 tradestatus=0，不区分 suspend_type 和 timing。08-24 那条是 R（复牌）。2026-07-01 起的 asof_extend_tushare 段共 125 行冲突（R 105、盘中 S 20）。原始层面，有成交且有 suspend_d 记录的共 6022 行（R 4979、盘中 S 1041、全天 S 2）。
方案（侵入最小）：不改面板，另出 data/v2/suspend_flags/suspend_flags_v2.parquet（列：ts_code、trade_date、halted_fullday、intraday_halt、intraday_halt_timing、is_resume_day、vol），由引擎 join；tier1_materialize 改为只在 S 且 timing 为空时置 0。

## D-3/D-4 stock_delisted
D-4：分类认"名称含退"，ref_tables_20261014.py 计算整理期起点时只认以"退"结尾，漏掉"退市XX"写法，61 只天数记 0（改正后 15–30 天，全部有成交）。规则问题，不是数据缺失。
D-3：build_delisted.py 的 reason() 没有面值规则。最后 20 个收盘全部 <1 元的命中 122 只，其中被分为合并/私有化的 4 只应改为面值退市：600297.SH 广汇汽车 0.78、002505.SZ 鹏都农牧 0.36、000861.SZ 海印股份 0.62、002509.SZ 天茂退 0.15。
002509.SZ 人工核对：namechange 里只有天广消防、天广中茂（止于 20200603），缺少"天茂退"一条；delisted_daily 显示 20200604→20200717 持续有成交，收盘 0.27→0.15，06-19 起成交量放大约 100 倍。结论：面值退市，且实际进入过整理期，namechange 缺记录（数据缺失）。应设 face_value_delist_flag=True，delist_period_start 按 20200604 记（须补公告核对）。
方案：出 stock_delisted_v2，新增 delist_period_start/end/days、face_value_delist_flag、needs_manual_source；旧版保留。
