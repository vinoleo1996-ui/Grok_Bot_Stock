# DATA 叶25 全叶 X2 字面结束日现盘 PIN（PIT 安全 · 研究级）

- **角色**：QuantLab Data 执行器
- **ET 时刻**：2026-10-25 11:30–11:35 America/New_York（箱内 `date` 同时区）
- **主令**：主→Data 叶25 全叶 X2 需**字面结束日**（不得写「发 .ok 时最新」）；密封已拟 2018-01-02→2024-05-31；X2 起 2024-06-03
- **禁令**：禁签 `.ok`；禁消费补跑 `.ok` `9e4359f9`；禁写生产数据；禁跑策略/因子代码；`live=false`
- **本文件性质**：研究级只读核验回执；**Data 未签** `.ok`；供主/Arch 冻结 X2 字面结束日

---

## 0. 结论行

```
X2_END_TRADE_DATE = 20261009
```

- **字面交易日**：`2026-10-09`（SSE `is_open=1`）
- **X2 拟窗**：2024-06-03 → **2026-10-09**
- **瓶颈板**：**`float_mktcap_daily_from2015_tushare`**（`trade_date` max = **20261009**）
- **对齐旁证**：leaf19 α / capacity_adv HILIQ 权重尾日同为 **20261009**（缺→0 / Gate B 对照亦在此截断）
- **非瓶颈**：OHLC / adj / etf / daily_basic raw 已到 **20261016**；财务 PIT（r5 口径）在 T=20261009 **无前视**且 dump 覆盖充足
- **live=false**；**Data 未签 .ok**；见回执文件 sha（写盘后自算，见文末或父回报）

---

## 1. PIT 口径（本回执采用）

对齐 `docs/v2/AI_LEAF25_ACCRUALS_PREREG_DRAFT_r5.md` §2 + `financials_pit_tushare_manifest.json`：

1. **财务行可用**：`available_at = coalesce(f_ann_date, ann_date) @ 18:00 Asia/Shanghai`；会话日 `d` 上可用 **iff** `date(available_at, Asia/Shanghai) < d`（严格早于 `d`；null `available_at` 永不使用）。
2. **日历会话**：`data/v2/calendar/trade_cal_sse_pit.parquet`，`is_open=1` 为交易日；现盘 sha256 `fa4260b808755b9a1c91e3ade210edec84bbdb91e0dfff4c6a955c4d35fd8a41`（与 r5 钉前缀 `fa4260b8` **MATCH**）。
3. **日频面板安全尾日**：该表 `trade_date`（或等价）**最大且为开市日**的日期；不得外推「发 .ok 时最新」。
4. **X2_end**：各硬输入映射交易日取 **min**，且 ≥ 2024-06-03、且 `is_open=1`。

> 财务 dump「新鲜完整」旁注（非本窗绑死项）：income/CF `max(available_at)=2026-10-10 18:00+08` → 按 r5 首个可用会话为 **20261012**；BS max aa **20261013** → 首完整可用会话旁注 **20261014**。取 X2_end=**20261009** 时，财务 **不是**最短板（见 §3）。

---

## 2. 输入核验表（现盘只读）

| # | 输入 | 路径 | max_date / max_available_at | 映射可安全交易日 | 是否瓶颈 | 备注 |
|---|------|------|-----------------------------|------------------|----------|------|
| 1 | 交易日历 | `data/v2/calendar/trade_cal_sse_pit.parquet` | open 覆盖至 **20261231**；行 `available_at` 近端多为 `2025-12-31 09:00` | 不限（投影历） | 否 | sha `fa4260b8…35fd8a41`；20261009/14/15/16 均为 `is_open=1`；1010/11/17/18 休市 |
| 2 | OHLC 日线 | `data/v2/tushare_raw/daily/` | 文件尾 **20261016.parquet**（n_files=**2130**；首 20180102） | **20261016** | 否 | 行内 `trade_date`=文件名；1014/1015/1016 均存在；1016 sha `d25ca1c7…a65212`（与叶27 PIN 旁证 MATCH） |
| 3 | 利润表 PIT | `data/v2/financials_pit/financials_pit_tushare.parquet` | `available_at` max **2026-10-10 18:00+08** | 无前视可达 OHLC 尾；**新鲜完整旁注 ≤20261012** | 否（本窗） | sha `bc0f4c3d…e7fab3`；T=20261009 时 dump 内 aa≥T 仅 2 行（不会在 T 使用） |
| 4 | 现金流 PIT | `data/v2/financials_pit/cashflow_pit_tushare.parquet` | `available_at` max **2026-10-10 18:00+08** | 同 #3 | 否 | sha `71d5c3d3…b95d79` |
| 5 | 资产负债 PIT | `data/v2/financials_pit/balancesheet_pit_tushare.parquet` | `available_at` max **2026-10-13 18:00+08** | 新鲜完整旁注 ≤**20261014** | 否 | sha `9ca05496…e8dbb5`；供 `total_assets` |
| 6 | **float_mktcap D1** | `data/v2/float_mktcap/float_mktcap_daily_from2015_tushare.parquet` | `trade_date` max **20261009**（n_dates=2857；manifest `date_max=2026-10-09`） | **20261009** | **是（最短板）** | sha `346d0dda…72a1ef`；**无** `available_at`（研究豁免，同叶27）；草案 §2.2 辅输入 / r5 logmv·ADV 代理 |
| 7 | SW L1 PIT | `data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet` | `available_at` max **2026-09-24 18:00**；`in_date` max 2026-09-24 | asof+gap_carry，不按日频截断 X2 | 否* | sha `89d4afa3…87f66c`；*慢表；未当硬日频最短板 |
| 8 | suspend_flags | `data/v2/suspend_flags/suspend_flags_v2.parquet` | `trade_date` max **20261014** | 20261014 | 否 | sha `ac5c10fd…447377`；无 1015/1016 行 |
| 9 | adj_factor | `data/v2/adj/adj_factor_2023h2plus.parquet` | `trade_date` max **20261016** | 20261016 | 否 | sha `4642ca8e…c2ffc3` |
| 10 | etf_daily_adj | `data/v2/etf/etf_daily_adj.parquet` | `trade_date` max **20261016** | 20261016 | 否 | sha `48b21e84…0ffd74c`（β 基准 510300） |
| 11 | HI_LIQ 掩码 | `output/strategy_hiliq/universe_mask_hiliq_v1.parquet` | `date` max **20261014** | 20261014 | 否 | 含 `adv20_yuan` 至 1014；**不**替代 #6 作为 logmv 主表 |
| 12 | FULLA 掩码 | `output/strategy_fulla/universe_mask_fulla_v1.parquet` | `date` max **20261014** | 20261014 | 否 | |
| 13 | leaf19 α（辅） | `output/ai_factory/leaf19_cfacc_rnoa/alpha_*_20261014_213132.parquet` | `date` max **20261009** | 20261009（缺→0） | 软对齐 | HILIQ sha `16202b2e…` / FULLA `c761dc36…` |
| 14 | capadv 权重（Gate B） | `output/strategy_hiliq/legs/g1g5_capacity_adv_hiliq_v1_1_daily_weights_20261014_195620.parquet` | `date` max **20261009** | 20261009 | 软对齐 | sha `3b288c83…2d31c4d` |
| 15 | daily_basic raw（旁证） | `data/v2/tushare_raw/daily_basic/` | 文件尾 **20261016**（含 circ_mv） | （未钉入草案主路径） | 否† | †若未来重建 float_mktcap 可延至 1016；**本回执不把 raw 当已落地 D1** |

**取最短板**：

```
X2_END = min(20261016 OHLC, 20261009 mktcap, 20261014 mask/suspend, 财务无前视可达 …)
       = 20261009
```

---

## 3. 财务 PIT 在候选 T 上的抽检（report_type=="1"）

口径：`aa_ymd < T` 且 `report_type=="1"` 计可用行；`aa_ymd >= T` 为 dump 内相对 T 的「未到点」行（不会在 T 使用 → **无前视**）。

| T | usable income/cf/bs (rt1) | dump 内 aa≥T (inc/cf/bs) | 解读 |
|---|--------------------------|--------------------------|------|
| 20261009 | 422127 / 315717 / 431101 | 2 / 1 / 5 | **推荐 end**：财务安全；瓶颈在 mktcap |
| 20261012 | 422129 / 315718 / 431102 | 0 / 0 / 4 | income/CF dump 新鲜完整旁注日；仍缺 mktcap |
| 20261014 | 422129 / 315718 / 431106 | 0 / 0 / 0 | BS dump 用尽；仍缺 mktcap；mask/suspend 齐 |
| 20261016 | 同上 | 0 / 0 / 0 | OHLC/adj/etf/daily_basic 齐；**mktcap 仍停 1009** |

---

## 4. 10-14 → 10-16 重跑影响

| 表 | 20261014 | 20261015 | 20261016 | 对 X2 字面结束日 |
|----|----------|----------|----------|------------------|
| OHLC `tushare_raw/daily` | 有 | 有 | 有 | 可支撑到 1016，但被 mktcap 卡住 |
| `daily_basic` raw | 有 | 有 | 有 | 原料在；**from2015 mktcap 未重建吸收** |
| `float_mktcap_daily_from2015` | **无** | **无** | **无** | 尾日仍 **20261009** → **建议不变** |
| suspend_flags | 有 | 无 | 无 | 若仅因此最多到 1014，仍 > 瓶颈 |
| HI_LIQ/FULLA mask | 有（尾） | 无 | 无 | 同上 |
| adj / etf | 有 | 有 | 有 | 非瓶颈 |
| 财务 PIT | 无新 aa 日于 1014–1016（income/CF max aa=1010；BS=1013） | — | — | 不因 1014→1016 延长财务板 |

**一句**：10-14→10-16 重跑把行情/复权/ETF/daily_basic 推到 **20261016**，但 **未**把 D1 `float_mktcap_from2015`（及 leaf19/capadv 对照尾）推过 **20261009**；故 X2 字面结束日建议 **维持 20261009**，不延长到 1014/1016。

---

## 5. UNCERTAIN / 非猜项

1. **UNCERTAIN**：若主/Arch 改钉 ADV/logmv **直接**读 `tushare_raw/daily_basic`（至 1016）或 HI_LIQ `adv20_yuan`（至 1014）而不经 `float_mktcap_from2015`，则最短板可能上移——**须改契约后另出 PIN**；本回执按草案 §2.2 现名路径。
2. **UNCERTAIN**：Gate B 是否硬要求 capacity_adv 全日覆盖 X2；现盘 capadv 尾=1009，与本建议一致，但未跑对照脚本。
3. **未做**：TTM/应计全市场覆盖率时序、因子脚本试跑、任何 `.ok` 申请、TEAM_STATE 改写、补跑 `9e4359f9` 消费。
4. SW L1 `in_date` 最大 20260924：依赖 `sw_l1_asof_with_gap_carry`；不将 SW 表 aa 当 X2 日频最短板（与 r5 asof 规则一致）。

---

## 6. 汇总（交主 / Arch）

| 项 | 值 |
|----|-----|
| **X2_END_TRADE_DATE** | **20261009** |
| 瓶颈板 | `data/v2/float_mktcap/float_mktcap_daily_from2015_tushare.parquet` |
| 日历 | 投影至 20261231；钉 sha `fa4260b8…`；1016 前开市日齐 |
| OHLC | 尾文件 **20261016**；n=2130 |
| 财务 | income/CF max aa **20261010**；BS **20261013**；于 T=20261009 PIT 安全 |
| 10-14→10-16 | 行情延长≠mktcap 延长 → **结束日建议不变** |
| Data 签 .ok | **否** |
| live | **false** |

---

*原子写：tmp→rename；本文件新建。全长 sha256 见写盘后校验（父回报携带）。*
