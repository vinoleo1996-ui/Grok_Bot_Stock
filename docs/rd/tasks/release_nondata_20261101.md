# Release 里的非行情文件

压缩包里的脚本、笔记和配置没有并进 `quantlab/`。副本在 git 忽略的 `data/_quarantine_nondata/`。清单里没有密钥文件名。

来自 `v2.tar.gz`：

- `data/v2/universe/MID_LARGE_RULE.md`
- `data/v2/financials_pit/AVAILABLE_AT_RESTATEMENT_POLICY.md`
- `data/v2/sw_l1_pit/NOT_PROMOTION_GRADE.md`
- `data/v2/text/em_heat/PILOT.md`
- `data/v2/text/xueqiu/BLOCKED.md`
- `data/v2/text/xueqiu/csi300_symbols.txt`
- `data/v2/_quarantine/sw_pit_INCOMPLETE_20261018/INCOMPLETE.md`
- `data/v2/announcements/cninfo/priority_post202406.txt`
- `data/v2/announcements/cninfo/priority_csi300_500.txt`
- `data/v2/announcements/cninfo/priority_post202406_ts.txt`

来自 `data_small.tar.gz`：

- `data/baostock/ql_codes.txt`
- `data/baostock/have_profit.txt`
- `data/baostock/have_growth.txt`
- `data/baostock/have_cash_flow.txt`

`NOT_PROMOTION_GRADE.md` 写的是免费重建的申万表不能当晋升级。它没有把 `strategy_promotion_approved` 设成 true。财务笔记写明 D0 财务的 `available_at` 曾经整列为空；这次抽出的 tushare 财务宽表 `available_at` 不是整列为空。这两份笔记只作隔离记录，不改读取器。

part349–469 里新增、同样只隔离的笔记：

- `data/v2/corporate_actions/EXRIGHTS_RECONCILE_LIMITS.md`
- `data/v2/corporate_actions/GAP_CLOSURE_PLAN.md`
- `data/v2/free_hunt/github/SKILL.md`
