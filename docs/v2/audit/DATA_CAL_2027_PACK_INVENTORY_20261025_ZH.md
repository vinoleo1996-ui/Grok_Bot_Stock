# 2027 交易日历包 · 离线盘点与缺口清单（2026-10-25）

- 作者：QuantLab Data；时区 America/New_York（ET）。**文档 only**：本回合未拉网、未调中转、未改生产。
- 依据现盘只读 + 既有方案：`docs/v2/plans/DATA_CALENDAR_2027_PACKAGE_PLAN_ZH_r2.md`（c1b51e13）/`_r3.md`（3772c424）；Arch 审 `ARCH_DATA_CALENDAR_2027_PLAN_REVIEW_ZH.md`（5d35e63c）、`ARCH_DATA_REVISIONS_1040_REVIEW_ZH.md` §1.2。
- 目标：11-30 前交 Arch；切换仍按方案 12-15 前（硬停：上海 2027-01-01 墙钟起读 CLEAN/纸面需 2027 段）。

## 1. 结论

| 项 | 现盘事实 |
|---|---|
| 止日 | PIT / raw 均为 **20261231**；2026 全年 365 自然日、242 开市日，无缺日 |
| 2027 | **全缺**（0 行）；非部分缺 |
| 建议包范围 | 年份 **2027 全年**（自然日 + is_open + pretrade_date）；PIT 另含 `available_at`；字段对齐现盘 schema |
| 随包修复 | **20130424**：`is_open=1` 但 `pretrade_date` 空（应填 **20130423**）；元旦闭市空 pretrade 属常态，不改 |
| 是否等中转 | **是**：正式 pull 须中转 `trade_cal` 通 + 休市公告；离线仅盘点/方案/验收草案 |

## 2. 现盘表（只读核）

| 路径 | sha8（全文 sha256 前缀） | min–max `cal_date` | 行数 | 开市日 | 空 `pretrade_date` |
|---|---|---|---|---|---|
| `data/v2/calendar/trade_cal_sse_pit.parquet` | **fa4260b8**（`fa4260b808755b9a1c91e3ade210edec84bbdb91e0dfff4c6a955c4d35fd8a41`） | 20050101–**20261231** | 8035 | 5343 | 22（21×元旦闭市 + **20130424 开市脏点**） |
| `data/v2/tushare_raw/trade_cal.parquet` | **141078fa**（`141078fa6da0ef94bc3cc8829aa031789490b7ff3e051b4baa4e38c496d06086`） | 20000101–**20261231** | 9862 | 6543 | 27（同上 + 更早元旦闭市） |
| `data/v2/calendar/manifest.json` | **7ccc911e** | start/end 与 PIT 一致；`open_days=5343`；钉 PIT sha=fa4260b8… | — | — | — |

- PIT 列：`cal_date, is_open, pretrade_date, available_at`；raw 列：`exchange, cal_date, is_open, pretrade_date`（exchange=SSE）。
- 2027 年段：两表均为 0 行。**20261231** `is_open=1`（现盘）。
- 脏点明细（PIT 行）：`20130424 | is_open=1 | pretrade_date="" | available_at=2012-12-31 09:00`；前一开市日现盘为 **20130423**。

## 3. 拟交付清单（不写代码；对齐 r2/r3）

**新文件（白名单写，禁覆盖现盘三钉）：**
1. `data/v2/calendar/trade_cal_sse_pit.v2027.parquet` + `trade_cal_sse_pit.v2027.manifest.json`
2. pull 影子：`data/v2/tushare_raw/trade_cal_<YYYYMMDD_HHMMSS>/`（exist_ok=False）
3. 纸面 raw 新版（主令并入）：`tushare_raw` 侧新文件（非原地 `141078fa`）；`tier1_pull` `end_date` 改参数的 code-change 另文
4. 比对产物：`output/data/trade_cal_compare_<stamp>/`
5. 读者侧：`TRADE_CAL_SHA_PIN` → v2027 全长 sha（Strategy code-change）；指针 `trade_cal_APPROVED.json` 仅交叉核

**验收断言草案：**
- A1 现盘三路径 sha 不变：fa4260b8 / 7ccc911e / 141078fa（inode 守卫，r3 用例 12）
- A2 v2027：`cal_date` 覆盖至 **20271231**；2027 自然日连续无缺；开市日数与公告一致
- A3 2026 及以前段字节级等同现盘（除约定修复 **20130424.pretrade_date=20130423**）
- A4 `available_at` = max(rule_floor, notice_at, pulled_sh)（r2 §3 / P2-2）；公告缺失拒写 2027 段
- A5 selftest 用例 1–12 全绿后，才申请 write/switch `.ok`；11-30 前交 Arch 审包

## 4. 依赖

| 可离线 | 须中转恢复后 |
|---|---|
| 本盘点；方案/验收文；selftest 文本与受保护路径守卫设计；20130424 修复规则定稿 | `trade_cal` pull（含 2027 + 公告字段）；生成 v2027 parquet/manifest；纸面 raw 新版；任何写盘 / `.ok` 消费 |

当前：`CONSUME_SUSPEND` / `RELAY_DOWN` 维持 → **本包实施拉取阻塞**；不阻塞文档与验收草案迭代。

## 5. 确认

- 本回合：**未改**任何 parquet / `.ok` / `TEAM_STATE` / 生产日历；**未**调 Tushare/中转；**未** SendToAgent / 报 Leo。
- 整文件 sha256（正文，不含本行）：`fbc76bcae21fbfa9675ab2222386f30c5e10380685ff2f59389c655bdc6d2a43`
