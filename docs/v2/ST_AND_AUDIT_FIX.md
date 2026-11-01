# ST 标记修复 + 审计意见入库（研究级，2026-10-10 ET）

不改动 `promotion_approved_overall`。新表 quality_status=research。

## 1. ST 标记
**问题**：`asof_extend_202610/panels`（5201 只）与 `asof_extend_tushare_202610/panels`（5578 只）2026-07-01 起 `is_st_at_open` 全为 0/False，部分面板缺此列，ST 股混入篮子。
**来源**：`tushare_raw/namechange`（322 个按公告月文件，非空）∪ `st_events/namechange_all.parquet`，去重 12823 行 / 5903 只。
**规则**：名称含 ST（含 *ST、S*ST）；区间 start_date→end_date；end_date 为空时截到同代码下一个名称前一天，再截到退市日；`is_st_at_open(d)=区间覆盖 d 且 ann_date < d`。
**产出**
- `data/v2/st_flags/st_intervals_tushare.parquet`：2716 个 ST 区间 / 1087 只，201 个当前未结束
- `data/v2/st_flags/is_st_daily_2018_2026.parquet`（instrument_id, trade_date, is_st_at_open）：320,476 行（只列 ST=True 的日子）
- 面板已就地修补：extend 面板 12,446 行由 0→1（ST 行共 13,512）；Tushare 面板 13,713 行
- `limit_ratio_at_open` 按 `quantlab/data/exchange_rules.limit_ratio` 重算：主板 ST 5% 仅到 2026-07-03，**2026-07-06 起主板 ST 为 10%**（上证发〔2026〕41号，仓库现行规则）；科创/创业 20%；北交所 30%。Tushare 面板无此列，未新增。
**校验**
- stock_basic 当前名称含 ST 的 201 只：2026-10-09 全部标记，无缺无多
- 与 D0（1c85）2018 起重叠 914 万行对比：一致率 99.98%；11 只有分歧（600721、002490、600321、000806、600375、601399、600816 各 80–260 天，其余 1 天），多为摘帽/戴帽日期口径差，未逐条核
- 0630 后每日 ST 数：201–214（7-01 214 → 10-09 201，均值 207）

## 2. 审计意见
- 原始：`data/v2/tushare_raw/fina_audit/<ts_code>.parquet`，按代码拉全 5912 只（relay+datahub 分摊），零失败，无单代码触及 100 行上限
- `data/v2/audit/audit_opinion_pit_tushare.parquet`：52,774 行 / 5592 只；字段 instrument_id, ts_code, end_date, ann_date, available_at（公告日 18:00 Asia/Shanghai）, audit_result, is_non_standard, audit_fees, audit_agency, audit_sign, quality_status
- 分布：标准无保留 50,310；带强调事项段 1,035；保留 871；无法表示 547；否定 7；无保留带持续经营重大不确定性 1
- 年报覆盖（当年末已上市、次年 4/30 前未退市）：FY2017 96.0%、2018 96.0%、2019 96.0%、2020 95.2%、2021 94.3%、2022 93.1%、2023 96.3%、2024 96.2%、2025 96.2%；每年非标 143–301 家
- 缺口：约 4–7% 上市公司无年报审计行（FY2025 缺 204 只，分布在主板 123/创业 46/科创 27/北交 8），属上游缺失；有 320 只从未有记录；end_date 也含少量半年/季度审计行，使用时按 month==12 过滤
