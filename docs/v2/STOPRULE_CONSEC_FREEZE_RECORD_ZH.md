# 停跑规则（连续失败）冻结记录
- 冻结人：主 Agent；时间：2026-10-18 00:39 ET
- 文件：docs/v2/STRATEGY_OPTIMIZER_STOPRULE_CONSEC_DRAFT_ZH.md
- sha256：41f29825c85a66c889474460605b45a19f5fa475ae46570f299416535cb3559b（主 Agent 已复算一致）
- 会签：Arch PASS（r3 d52c3510…）；Beta PASS_WITH_AMENDMENTS（M1–M6 已写入 §7）
- 规则：连续 ≥3 个调仓日失败即停跑，与单月 ≥2 INFEASIBLE 规则取并集；滚动 6 期失败 ≥3 只披露。
- 已披露：k=3 是看过 v1.3 失败序列后选定，冻结后不得再改。
- 生效：v1.4/Stage2 起前瞻生效，不追溯 v1.3。
- live=false；promotion=false。
