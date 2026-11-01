# 叶23 r2.10 X2 方案A 运行回执 — **STOP @ A02 (eval FULLA)**
- 执行者：AI（executor）。脚本 research/g1g5_sue_desens_cs_alpha.py sha f13443240e204a54611e9c9123d9367f1365d99b07c09534fceebfbfe50fda10（commit 821a910）。
- .ok output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_10_X2.ok sha 97964bb1…fbe100（核对一致）；.cmd output/ai_factory/ARCH_TOOL_CMDS_LEAF23_X2.cmd sha 6c65f6c3…bdcfb（核对一致；正文仅 CMC 行，未执行）。
- 步骤命令逐字取自 Arch 审过的步骤表 docs/v2/AI_LEAF23_R2_10_PROPOSED_CMD.txt（sha 644ce1f6…，A01–A27），由 /tmp/l23run.py 逐步串行执行，无 || true，PYTHONDONTWRITEBYTECODE=1 保留。
- 94322 STOP 证据：stop_94322_20261018_r2_10.md（32872897）。

## 每步前置检查（A01、A02 均 OK）
pgrep forecast_history_pull 空；94322 状态 T；forecast f1e59284 / manifest 0bdabc47；sw_l1_pit(industry_members_sw_l1_tushare.parquet) 89d4afa3；/proc fdinfo 无进程以写方式打开 data/v2/events（lsof 未安装，用 /proc 替代）；MemAvailable 10.9GB/10.87GB；无其他 qlvenv/research/uvicorn 进程；早于 10-19 04:30 ET。

## 步骤结果
| 步 | 阶段 | 开始–结束 (ET) | 退出码 | VmHWM kB | peak_check | STAMP | RSS_GUARD_KILL | meta |
|---|---|---|---|---|---|---|---|---|
| A01 | primary eval_HILIQ | 06:30:57–06:31:46 | 0 | 1109996 | 有 | 20261018_063101 | 无 | eval_HILIQ_meta.json 7c382b89771118746f82da8ac195a961a5874c3b297fd328b4c020e052cd9be5 |
| A02 | primary eval_FULLA | 06:31:46–06:32:24 | **1** | 1161840 | 有 | **无** | 无 | **eval_FULLA_meta.json 未写出** |
A03–A27 未执行。

## STOP 原因（A02）
日志末行：`STOP (B3): Mp != fulla_carry on 2 restored resume rows / 0 carried non-suspended name-days / 0 .BJ member rows (P3-D) — report to Arch`
B3_carry_mismatch_FULLA.json（sha f82f5ee02969d98482cae468c7b239bea4947219cf0de122d1fc2b3177d9ee8e）：resume_rows_checked=805，carry_mismatch=2，carry_unindexed=0：
- 2025-04-30 002868.SZ fulla_carry=True row_origin=restored restore_reason=resume
- 2026-01-14 603056.SH fulla_carry=True row_origin=restored restore_reason=resume
（非内存问题；HILIQ 侧同一检查通过。）
日志：logs/A01.log sha e28dc421640059f7a6363e21640bc9c1c74d631b9290f04190cc0d59989151b7；logs/A02.log sha 9f438278b0956f8080b4723cab67e42eede477586132a42ad2cc0d93bd79f868；logs/steps.jsonl。

## A01 产物 sha
- summary_HILIQ_20261018_063101.json af3f29abdc491f67c54e1588baa29cd0c31f0285acf65d2c703b6940b960756d
- eval_weights_HILIQ_top10_100w_x2 0679107… / top6_60w_x2 d4fb418f… / top10_100w_cap20_disclosure 7fa8ee88… / top6_60w_cap20_disclosure 63d64393… / top20_disclosure 5445cfe1…（均 _20261018_063101）
- 外部：g1g5_sue_desens_cs_top10_100w_daily_weights_20261018_063101.parquet 067910784ea7ec3a7286b14b848764957f020767bd0edbf968c7ad5a55f4fa29；top6_60w_daily_weights d4fb418f5ec4cc74b0bb26d7024e140a8ff087e3bb7d95fec165da9f92056010；run_meta top10 749fb2d3… / top6 2598045f…

## HILIQ 半边结果（仅供参考；merge 未完成，不构成正式判定）
| 档 | CAGR244 | CAGR252 | MDD | Calmar(244) | vs wb HAC t | resid HAC t |
|---|---|---|---|---|---|---|
| 60万 top6 | 3.18% | 3.28% | −21.96% | 0.145 | −1.41 | −1.59 |
| 100万 top10 | 4.39% | 4.54% | −22.72% | 0.193 | −0.83 | −1.30 |
decisive（HILIQ）：t_hac_ge_2_50=False，wb_floor_pass=False，beats_poolEW=False，verdict_cap=FAIL。两档 |t| 都 <2.50，即便 FULLA 跑通也不可能过决定性检验。胜率 summary 未直接给出，未补算。
基准：poolEW 12.68%，wb 11.60%（244）。

## 检查
- delisted_master max delist_date = 2026-07-30 ✔（sha 63590f23）。
- N4（HILIQ）：排除名日中位数 117，wb 权重占比中位数 22.8%。
- 7 只名 S=True 名·日、r0.index==rr.index、FULLA N4：因停在 A02 未得到，未核。
- 敏感性：未跑。

## 披露 / 环境 / resume
- 数据截止 20261014；301139.SZ 有缺口。
- qlvenv 3.12.14 / pandas 3.0.6 / pyarrow 25.0.1（叶19/20 用 system python3 3.13）。
- resume 接受的 r2.9 meta：fund f393b3e9…、build_HILIQ fb4b2ad4…、build_FULLA 07391924…（运行后重测仍一致）。
- research/__pycache__/…cpython-313.pyc：叶23 未完成，按指示**未删除**。
- 未改任何代码/.ok/.cmd，未碰 _void，未提交。
