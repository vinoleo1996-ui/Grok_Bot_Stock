# Data 对 Alpha D5/D6 验收缺口的修补（2026-10-14 CST）

promotion_approved=false。修补前的备份文件名带 `*.bak_pre_fix_20261014.parquet`。

| 缺口 | 处理 | 结果 |
|---|---|---|
| G0 SHA256 | 队列脚本 `scripts/acquire/queue_chain_20261014.py` 的 g0 步骤给 D5、D6、hsgt、sw_pit、cyq 的 manifest 写入 `sha256` 字段（按文件），在 G3 之后执行，全部新表跑完后再算一次 | 见 output/remaining_queue_status.json 中的 G0 |
| G1 1,716 条规则推断 | 五批改用媒体或交易所页面核实的公告日；available_at 取首个可证实的公开时点（只会往后推，不会提前）。2018-12 定为 12/03 09:00（上证报 12/03 08:28 报道"日前宣布"）；2019-06 定为 06/03 20:00（上交所联合公告落款）；2019-12 定为 12/03 20:00（中证官网 12/03，深交所 12/02，取较晚的一个）；2020-06 定为 06/01 20:00；2022-06 定为 05/27 20:00（中证官网晚间发布）。quality_status 改为 public_report_media。另外 2018-06 批次保守地改到 05-28 09:00（上交所页面落款为 5/28） | rule_inferred 剩 0 条；ann_date 晚于 effective_date 的仍是 0 条 |
| G2 106 条非定期事件 | 没有找到公告。available_at 设为 snapshot_date 20:00，只能作为成分状态使用，不能当事件信号 | 106 条均已标注 |
| G3 hsgt_top10 2022-06 到 2023-12 | 用 fill_hsgt_top10_extend.py（TOP10_START=20220601，TOP10_END=20231231）回补，并对 7 个空日逐日重新请求核对 | 见状态文件中的 G3 |
| G4 SW | L1 从 7,743 行降到 7,735 行，L2 从 7,758 行降到 7,753 行：删掉同一代码、同一 in_date 下已关闭的重复记录。同时挂多个当前行业的股票（L1 有 12 只）新增 `is_primary` 列，优先取 is_new=Y，再取 in_date 最新的一条。197 只没有现行 SW 分类的股票，源头 index_member_all 没有数据，**没有补**，研究时应作为缺失处理，不能填"其他" | 剩下的 (instrument, in_date) 重复都是同一天挂两个不同行业，用 is_primary 区分 |
