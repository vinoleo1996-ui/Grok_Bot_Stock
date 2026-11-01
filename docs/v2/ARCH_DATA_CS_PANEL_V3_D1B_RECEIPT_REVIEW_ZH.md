# Arch 审查：Data cs_panel v3 D1b dry-run 回执

- 审查时间：2026-10-18 04:55 ET
- .ok：output/data/ARCH_RUN_AUTH_CS_PANEL_RESUMEFIX_v3.ok（dac5f6dd…）
- 结论：通过（P0/P1/P2=0，P3=2）。放行 D2_suspend_flags dry-run。

## 复核
1. 三个 sha 复算全部一致：stdout 4313dac0、receipt b8de3dbe、ps 快照 9c420478。
2. 去掉 rss_mb、PEAK_RSS_KB、RUN_CONDITION_MATCHES、ok_sha256 后，与 v2 stdout（90a48b35）diff 为 0 行，由 Arch 独立复算。
3. 9 年均为 v1_rows_missing_in_v2=0、v1_value_mismatch=0；GATE_PASS step=D1b_resume_execute mode=dryrun ok=dac5f6dd。
4. 峰值 RSS 约 1336MB，低于 1450MB 的上限，余量约 114MB。
5. data/v2/suspend_flags 不存在。04:49 之后 data/v2 的新文件只有 tushare_raw/fund_portfolio_dh/*，写入者是 94322（remaining_after_stk_surv.py），不是 D1b 的输入，也不在 fix_sd1 的读取范围内。94403=Ts，212762=Z。

## P3
- P3-7：回执的零写入证明只列了 4 个输出路径。D2 回执须附 `find data/v2 -newermt <开始时间> -type f` 的计数，并按目录分组说明写入者。
- P3-8：quantlab-web 的 kline.py 以只读方式读 data/local_market，属于预期内情况。execute 窗口内也要披露它。
