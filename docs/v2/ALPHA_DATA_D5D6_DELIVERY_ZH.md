# Alpha D5/D6 交付短文（2026-10-13）

promotion_approved=false，仅研究级。

## D5 · 指数调样公告日
- 路径：`data/v2/index_members/csi_review_calendar.parquet`（18 行，2018-06 ~ 2026-12）；`data/v2/index_members/index_member_events.parquet`（5,840 行，已并入 ann_date / effective_date / available_at / quality_status）；manifest `manifest_d5.json`；脚本 `scripts/acquire/build_d5_index_ann.py`；旧版备份 `index_member_events.bak_pre_d5_20261013.parquet`。
- 覆盖：沪深300 / 中证500 / 中证1000 的 6/12 月定期调样。17 个历史批次中 12 个有公开公告日（中证/上交所公告或财经媒体转载，URL 在 source_url），5 个按规则推断（2018-12、2019-06、2019-12、2020-06、2022-06：上月最后一个周五）；2026-12 为未来批次，标 `scheduled_future_rule`。
- 本次新增公开核实的批次：2021-06（5/28）、2021-12（11/26）、2023-12（11/24）、2024-06（5/31）、2025-12（11/28）、2026-06（5/29）。
- available_at 规则：ann_date 当天 20:00（上海时间），因为公告多在盘后发。effective_date 记为新成分的首个交易日。
- 事件质量：public_report 4,018 / rule_inferred 1,716 / non_periodic_no_ann 106（临时调整，没有统一公告日，ann_date 留空）。
- 已知缺口：2019-12 的媒体报道日期是 12/02–12/03，与规则推断的 11/29 不一致，可信度低；中证500/1000 成分仍来自月末快照夹逼。

## D6 · 配股事件表
- 路径：`data/v2/corporate_actions/rights_issue_em.parquet`（984 行，除权日 1991-06-01 ~ 2026-08-21）；manifest `manifest_d6_rights_issue.json`；脚本 `scripts/acquire/build_d6_rights_issue.py`。
- 来源：东财 RPT_IPO_ALLOTMENT（Tushare 没有配股接口）。字段包括配股比例（每 10 股）、配股价、股权登记日、除权日、缴款起止日、上市日和募资额。
- available_at 规则：first_notice_date 当天 20:00；没有该日期时用股权登记日前 2 天 20:00。
- 与 `exrights_unexplained_recheck_tushare`（3,853 条）交叉：在 "no_tushare_dividend_on_date" 942 条中命中配股 97 条（10.3%）；另外两类的命中数为 0，符合预期。剩下约 845 条要用送转、增发、并购等去解释，这部分不在本次范围内。
