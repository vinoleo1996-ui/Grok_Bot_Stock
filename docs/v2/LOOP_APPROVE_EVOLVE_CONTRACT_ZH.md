# approve→evolve 契约（Eng）——**有限回写已开启（Leo 2026-10-13 批准）；GP 仍禁**

状态：只读索引加有限回写。回写范围**只有**队列优先级、fitness 标签、同构黑名单；**GP 仍禁**，不做自动结构搜索，不自动开新叶，live=false。按 QuantLab AI 的要求，**Eng 不写 AI 目录或代码**：回写只落在 Eng 自有的契约文件，由 AI 拉取读取。

## 入口
`PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.cli loop-sync`（幂等：内容无变化时输出 `unchanged`，不重写文件）

## 输入（只读）
- output/ai_factory/g1g5_<leaf>_daily_weights_<YYYYMMDD_HHMMSS>.parquet：每叶取最新时间戳，排除 combo_/conc4leg。
- output/ai_factory/g1g5_<leaf>_run_meta_<ts>.json：取 mechanism_tag。
- docs/v2/AI_G1G5_<LEAF>_WEIGHT_ACCEPT_ZH.md：Alpha 标签，从文档开头约 400 字匹配（RESEARCH_ACCEPT/ACCEPT/WATCH/PASS/FAIL/REJECT/DONE_FAIL），匹配不到记为 see_doc。属尽力解析，以原文为准。
- docs/v2/AI_LEAF_LEDGER_ZH.md：仅作人读参考，按 mechanism_tag 摘取「结论」和「自检价格口径」两列。
- output/v3/book_smoke_g1g5_<leaf>_x2/book_smoke_summary.json，以及 combo_* / conc4leg_* 的 Book-Smoke 汇总（组合是否胜主干按“CAGR 更高且 MDD 更浅、两档都须满足”判定）。

## 输出 output/loop/leaf_status_index.{json,parquet}
叶字段：leaf, mechanism_tag, weights, weights_ts, run_meta, alpha_accept_doc, alpha_label, ledger_verdict, ledger_price_basis, smoke_run, smoke（JSON：各档 cagr/mdd/sharpe/cost/c0_cagr/gate）, smoke_gate_both。
JSON 另含 combos[]（combo, by_capital, beats_trunk, beats_trunk_both）以及标志：live=false、promotion=false、evolve_writeback=DISABLED_PENDING_GP_UNBAN_BY_LEO。

## 回写（`loop-sync --writeback`）
输出 output/loop/factory_feedback.{json,parquet}，schema 为 `quantlab.loop.factory_feedback.v1`。
- 顶层：version_sha256（行内容哈希）、updated_at（ET）、scope、live=false、promotion_approved=false。
- 行字段：leaf_id、kind（leaf / leaf_ledger_only / combo / combo_paper）、mechanism_tag、queue_priority（0–100）、fitness_label、blacklist（bool）、blacklist_reason、source_doc、smoke_run、updated_at。
- 幂等：version_sha256 不变时不重写，updated_at 也不变。
- 规则（固定，不含任何搜索）：
  - fitness：Alpha 标签或台账含 FAIL/REJECT/同构 → fail；WATCH → watch；ACCEPT 且 Book-Smoke 两档过门 → smoke_pass，否则 accept_smoke_fail；无标签但过门 → smoke_pass_unlabeled；其余 unlabeled。capacity_adv 与 B4 → paper_active。
  - 优先级：paper 100 / smoke_pass 80 / smoke_pass_unlabeled 60 / watch 40 / accept_smoke_fail 35 / unlabeled 20 / fail 0；组合胜主干 60，否则 0。
  - 黑名单：fail；台账中的同构叶或计数闸失败叶；未在两档同时胜主干（CAGR 更高且 MDD 更浅）的组合。
- AI 侧如何使用由 AI 决定；本文件不触发任何运行。
