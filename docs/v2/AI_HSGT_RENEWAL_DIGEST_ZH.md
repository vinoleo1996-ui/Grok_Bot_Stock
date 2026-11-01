# hsgt 续期消化短报（研究级）

| 项 | 值 |
|---|---|
| 日期 | 2026-10-12 ET |
| 作者 | QuantLab AI |
| promotion_approved | **false** |
| 不交 | Strategy |
| 用途 | 核实北向相关落盘相对旧 BLOCKED 状态；**勿空跑依赖未续期叶** |

探针：本机 `python` 读 parquet（2026-10-12 ET）；下列数字为当面观测，非编造。

---

## 1. `hsgt_top10_daily_2018plus.parquet`

| 项 | 观测 |
|---|---|
| path | `data/v2/northbound/hsgt_top10_daily_2018plus.parquet` |
| nrows | **18,729** |
| date_min / date_max | **2018-01-02 → 2022-02-10** |
| nunique(trade_date) | **943** |
| 相对旧 BLOCKED（约至 **2021-12-08**） | 仅微延：2021-12-08 之后约 **38** 个交易日、至 **2022-02-10**；2022-06 及以后 **0** 行 |

结论：仍无 **2022 年中后全日频**。续期进行中/不足。

**工厂 SEARCH：`hsgt_top10_*` 仍标 BLOCKED**（不可作破墙主依赖；无 2022 中后全日频源前勿开 GP 依赖）。

---

## 2. `hk_hold_ashare_daily_2018plus.parquet`

| 项 | 观测 |
|---|---|
| path | `data/v2/northbound/hk_hold_ashare_daily_2018plus.parquet` |
| nrows | **3,708,580** |
| date_min / date_max | **2018-01-02 → 2024-12-31** |
| nunique(trade_date) | **1,567** |
| 日频稠密度 | 约至 **2024-08-16** 仍近似日频；其后仅见 **2024-09-30**、**2024-12-31**（季末稀疏点） |

官方约束（与 `docs/v2/HK_HOLD_COVERAGE_GAP.md` 一致）：**2024-08 后 A 股日频披露停更/不可假设连续**；季末仍可有完整 A 股持股。

**条件接线口径**：接受「日频至 ~2024-08 + 季末点」或样本截断；**不可假装全日频到 2026**。`available_at` = trade_date 18:00 Asia/Shanghai。

---

## 3. `moneyflow_hsgt`（市场层）

| 项 | 观测 |
|---|---|
| path | `data/v2/northbound/moneyflow_hsgt_daily_2018plus.parquet`（与 `*_2014plus` 同窗） |
| nrows | **2,800** |
| date_min / date_max | **2014-11-17 → 2026-10-09** |

已齐至 **2026-10-09**。性质：**市场层**北向/南向资金汇总，**非**个股截面破墙主叶；再交叉易成体制近亲（参见 NB-MARGIN-DIV）。

---

## 4. 对 TrackA 的含义

1. **`hsgt_top10` 仍不可作破墙主依赖**（BLOCKED / 续期不足）。  
2. **席位叶已接线优先**（`dt_inst_net_*` / `dt_nb_channel_net_*` / `dt_retail_hot_net_*` / `dt_inst_breadth*`）；进 SEARCH 须 New Bot 放行且 Leo 明示后再开 v27A。  
3. **`hk_hold` 仅条件接线**（日频截断 + 季末）；勿当全日频。  
4. **`moneyflow_hsgt` 已齐**，但只作市场层背景，不作破墙主叶。  
5. **v27A SEARCH 仍等 Leo 明示「启动 v27A」**；本稿不开跑、不启 GP、不交 Strategy。

---

## 5. 结尾约束

- `promotion_approved=false`；**不交 Strategy**。  
- TrackB 份额流 / 价叶同叶族继续停；ETF-DT-SEAT 已停。  
- 等 Data 续满 `hsgt_top10` 至可用全日频后再复议解禁；当前保持 **BLOCKED**。
