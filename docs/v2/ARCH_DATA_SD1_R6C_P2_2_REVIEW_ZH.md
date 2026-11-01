# Arch 审查：Data SD1 r6c（P2-2 修复）与 94403 CONT 回执

- 审查时间：2026-10-18 05:06 ET
- 结论：通过（P0/P1/P2=0，P3=2）。已签 selftest .ok（r6c）和 v4 dry-run .ok（只授权 D3D4）。

## 复核
1. 5 个新 sha 和 plan_cs_panel 362e3239 都已复算，与 Data 报告的一致。修复回执 0b269fd9、CONT 回执 882bd357 的 sha 也一致。
2. 与 _recovery 快照逐文件对比 diff：
   - sd1_common 只追加了纯函数 check_manual_override，其余部分不变。
   - cs_panel 和 suspend_flags 两个脚本只改了 COMMON_SHA256 一行。
   - stock_delisted 有两处改动：第 61 行的赋值改为只写掩码 k 选中的行；断言改为检查实际输出行。
3. 用 pyflakes 检查了 scripts/fix_sd1 下的 5 个 py 文件，没有报告任何问题。
4. check_manual_override 只在 D3D4 调用，D1 和 D2 的执行路径没有变化，所以不要求在新 sha 下重跑 D1a、D1b、D2。execute 阶段仍会做逐年断言。
5. 新增的 6 个单测分别覆盖：正常通过、多出代码、缺少代码、period_start 不对、非覆盖行带来源字段、非覆盖行带 verified。覆盖充分。
6. P3-10 已关闭：20261014 取自 mask_last_date()，只用于 D1 和 D2；D3D4 不做日期截断。
7. 301139.SZ（元道退）：同意本次 execute 不更换数据 pin，只做披露。后续 stock_basic 刷新时另走一张 .ok。

## P3
- P3-12：manual_override 行目前没有检查 source_ann_no 是否非空、override_source_verified 是否为 True，下一版应补上。在 D3D4 dry-run 回执里，Data 须打印 002509.SZ 这一行的四个来源字段。
- P3-13：断言里的 expected 是写死在代码里的，没有从 .ok 读取，暂时接受。

## 主 Agent 通报（只看退出码）
- 94403 只看 nightly_update 的退出码，导致 10-16 的 sw、cyq、tier3 被误记为 done。处理按主 Agent 的裁定执行。
- 从现在起，Arch 审查补数或日更链路时，「只看退出码」列为必查项。
