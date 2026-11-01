# ALPHA_DATA_REQUESTS_STATUS · QuantMind 深读单（2026-10-12）

更新：2026-10-12 12:13 EDT · `promotion_approved=false` · 未改 overall 晋级门

依据：`docs/v2/ALPHA_DATA_REQUESTS_QUANTMIND_20261012_ZH.md`；Alpha `ACCEPT_STAGE` D1 残差回执。

| ID | 状态 | 路径 | 日期范围 | available_at | 已知缺口 |
|---|---|---|---|---|---|
| **D1** | **有（残差部分修复）** | `data/v2/valuation/daily_basic_full_tushare.parquet` + manifest；窄表 `daily_basic_valuation_tushare.parquet` + `..._ext_20261012.parquet` | full：2014-01-02→2026-10-12（**2014-04-08→12-31 空窗回填中**）；估值主表 2018-01-02→2026-10-09 + ext **2026-10-12** | `trade_date` 18:00 Asia/Shanghai；**禁止裸 trade_date 开盘信号** | ① full 2014-04→12 SSE≈183 日：`tier1_pull.py db2014` 续拉中（raw 已过 20140411）；② full manifest 已补 `trade_date_semantics`；③ 估值 date_max 经 extension 对齐到 2026-10-12（周末 10–11 休市） |
| **D2** | **做** | 目标 `data/v2/moneyflow/moneyflow_stock_daily_pit.parquet`；raw `data/v2/tushare_raw/moneyflow/{YYYYMMDD}.parquet` | 目标 2018-01-02→最新（沪深）；当前 raw 自 20180102 起逐日推进 | 下一开市日 09:00 Asia/Shanghai（open 决策） | PCD relay 曾 Tl/Read-timeout；**已单 loop 改 MF_BACKEND=datahub**（promax relay 后备，timeout 180s）；进度见 `output/d1/moneyflow_pull_progress.json` |
| **D3** | **有** | `data/v2/universe/mid_large_members_pit.parquet`（+ `MID_LARGE_RULE.md` / manifest） | session 2015-01-06→2026-10-09；≈5,552,904 行 | session 09:00 Asia/Shanghai；成员用**前一交易日** float_mktcap | **显式 ≠ CSI300**；SSE+SZSE、剔 ST、流通市值 top 50%；研究级 |
| **D4** | **拒** | — | — | — | Tushare/datahub **无历史 IOPV**：`etf_iopv`/`fund_iopv`/`rt_fund_daily` → unknown_api；仓内 `fund_daily` 无 iopv 列；仅有实时 `rt_etf_sz_iopv`（深市、无 start/end 史）。份额/NAV PIT 已有，不能伪造 IOPV |
| D5 | 排队 | 指数调样公告日 | — | — | Tushare 无 ann_date；未抓中证官网 |
| D6 | 排队 | 配股 PIT | — | — | 解释 exrights_unexplained 用 |

## 运维备注（本拍）
- Mac 打包 / BS 续拉：**未杀**；moneyflow 与 db2014 错峰限速。
- moneyflow：杀掉 Tl 卡死的 3062103/3062110 后，**只保留一条** datahub loop；日志含 `backend=datahub`。
- 估值窄表未整表重写（RAM/IO）；用 `extension_paths` 对齐 date_max。合并读：`union_read` 见估值 manifest。
