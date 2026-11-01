# Data：叶27 契约缺口对齐回执（研究级；**不签 .ok**）

- 角色：QuantLab Data
- 时刻（America/New_York）：**2026-10-25T06:32:15-04:00**
- 主令：Arch 叶27 契约预告对齐（P1）；**不挡叶25**；**不申请**叶27 `.ok`；不写生产；**live=false**；`promotion_approved=false`
- 补钉：主 Agent FYI — capacity_adv 暴露已钉（`target_weight`；主称 `5e720335…` / 表 `3b288c83…`）；本文件仅改该项状态，四项实证不变
- 方法：只读检索；`pyarrow.parquet.read_schema` / metadata / 抽样列；未读收益页；未跑策略；未改 `research/`

## 输入核验（sha MATCH）

| 文件 | 期望前缀 | 全长 sha256 | 结果 |
|---|---|---|---|
| `docs/v2/ARCH_AI_LEAF27_CONTRACT_PREVIEW_20261025_ZH.md` | `ac853d7f` | `ac853d7f321aca19dc7260c2ad5c26880b74950cad35df59008fdfbad1297641` | **MATCH** |
| `docs/v2/AI_LEAF27_OVERNIGHT_IDIO_IVOL_PREREG_r1.md` | `f12965da` | `f12965dadde8a9563aee31065698a73b72339bf61d7572ed1afe1be083dafdcf` | **MATCH** |

旁证文档（交叉，非本回执输入闸）：

| 文件 | sha256 |
|---|---|
| `docs/v2/LIMIT_COVERAGE_2018.md` | `c240cb49c381056ba8ff7d5c76120f3b025014375a73583186b9672bba97c330` |
| `docs/v2/AI_ADJ_PRICE_RECEIPT_ZH.md` | `0c5f5af55866f178083349a0c5f14687b379666d7e86e3df12e2b333ad242bf9` |

## 结论表（OK / GAP / UNKNOWN）

| # | 项 | 状态 | 一句话 |
|---|---|---|---|
| 1 | OHLC / `pre_close` 统一路径 | **GAP**（路径有、panel 缺列） | `tushare_raw/daily` **有** `pre_close`；1c85 / asof_extend* panel **无** `pre_close` 列名 |
| 2 | float_mktcap T−1 + `available_at` 断言 | **GAP**（表有、脚本断言未钉） | 两表列齐全；reader 合成 EOD `available_at≈session 18:00 Asia/Shanghai`；**T−1 取法须脚本钉死**，缺则无效 |
| 3 | 510300 单一路径 + 收益定义 | **GAP**（多路径；须钉一条） | 研究级推荐：`etf_daily_adj` · `510300.SH` · **hfq close-to-close**；另两路径 `promotion_approved=false` |
| 4 | 涨跌停列名 | **OK**（名对齐）+ BJ **GAP** | 盘上为 `limit_up`/`limit_down`（**非** `limit_up_flag`）；北交所 1c85 列在但值全空 |
| — | 停牌优先序 | **OK**（披露） | 宇宙掩码 `suspended` 优先；细节用 `suspend_flags_v2.halted_fullday` / `is_resume_day` |
| — | capacity_adv 暴露 | **主已钉**（Data 不重复挖） | 主编排 FYI：权重表 `target_weight`；主称 sha 前缀 `5e720335` / 表 `3b288c83`；本回执不另挖 |

### 研究级推荐路径（签 `.ok` 前实现须重钉 sha）

| 用途 | 推荐路径 | 备注 |
|---|---|---|
| `r_on`/`r_id`（未复权公式） | `data/v2/tushare_raw/daily/{YYYYMMDD}.parquet` | 列含 `open,close,pre_close`；缺/`pre_close≤0` → 无效 |
| log 流通市值 T−1 | `data/v2/float_mktcap/float_mktcap_daily_from2015_tushare.parquet` | 会话 T 用 **上一交易日** 行；禁静默用 T |
| 510300 日收益 | `data/v2/etf/etf_daily_adj.parquet` 滤 `ts_code=="510300.SH"` | `r_m = close_hfq_t / close_hfq_{t-1} − 1` |
| 涨跌停 gate | 1c85 panels（至 2026-06-30）∪ `asof_extend_tushare_202610/panels`（2026-07+） | 列名 `limit_up`/`limit_down`；BJ 无效或缺则剔除/披露 |
| 停牌无效 | `output/strategy_hiliq/universe_mask_hiliq_v1.parquet` 列 `suspended` | 复牌披露辅以 `suspend_flags_v2` |

---

## 1) OHLC / `pre_close` 统一路径

### 1.1 `data/v2/tushare_raw/daily` — **有 `pre_close`**

- 样本：`data/v2/tushare_raw/daily/20180102.parquet`
- 覆盖（文件名）：`20180102.parquet` → `20261016.parquet`（n=2130）
- 样本 sha256：`22720a21387636fdc92f9946da7db5298e94e4f4f8e49b67e9e9083d9ba60631`
- **pyarrow schema（列名:类型）**：

```
ts_code:large_string
trade_date:large_string
open:double
high:double
low:double
close:double
pre_close:double
change:double
pct_chg:double
vol:double
amount:double
```

### 1.2 1c85 / extend panels — **无列名 `pre_close`**

| Panel | 路径样本 | sha256（样本文件） | `pre_close` | 相关价列 |
|---|---|---|---|---|
| 1c85 D0 | `data/local_market/1c85fd9aceaa03c3c4863bec/panels/sh.600000.parquet` | `029750da9f2edf01b6495558d1af0b8e13c0cf8e9ab183504697bf548d628641` | **ABSENT** | `open,high,low,close,reference_price,factor,…` |
| asof_extend | `data/v2/asof_extend_202610/panels/sh.600000.parquet` | `6bdd9191e8c8a5d72d8d5a2e868df1510ec682b925fa6ccbe854586c090cb3df` | **ABSENT** | `open,high,low,close,factor,limit_up,limit_down,…` |
| asof_extend_tushare | `data/v2/asof_extend_tushare_202610/panels/sh.600000.parquet` | `b7fd818335b8dd12458ca9f72b1c9fab9b31c0cf3377cc240217bcefc2c8742a` | **ABSENT** | `open,high,low,close,adj_factor_tushare,limit_up,limit_down,…` |

1c85 样本关键价相关列（节选）：`open,high,low,close,volume,amount,factor,feature_close,reference_price,upper_limit,lower_limit,limit_up,limit_down,available_at,…` — **无 `pre_close`**。

### 1.3 研究级推荐（算 `r_on` / `r_id`）

- **主推荐（对齐预注册公式字节）**：按交易日读 `data/v2/tushare_raw/daily/{trade_date}.parquet`，用未复权  
  - `r_on = open / pre_close − 1`  
  - `r_id = close / open − 1`  
  - 缺 `open`/`pre_close` 或 `pre_close≤0` → 该票当日 **无效**（预注册已写死）。
- **若坚持走 panel**：须另钉「前日收 / `pre_close`」来源（例如同日 join raw `pre_close`，或用 PIT 合法的前收推导）+ 复权实现 sha；**不得**把 `reference_price` 静默当 `pre_close`（本回执未验证其语义≡`pre_close`）。
- 复权旁路（评价层，非本拆分主公式）：个股见 `docs/v2/AI_ADJ_PRICE_RECEIPT_ZH.md`（`adj_factor`）；基准见 §3。叶27 拆分残差主轴以预注册未复权 OHLC/`pre_close` 为准，除非独立 `.ok` 另钉。

**本项状态：GAP**（raw OK；统一 panel 路径缺 `pre_close`）。

---

## 2) float_mktcap T−1 + `available_at` 断言

### 2.1 两表列名（实证）

**A. `data/v2/float_mktcap/float_mktcap_asof.parquet`**  
sha256：`51d96f20096f739ff8452357584a3d53d36d50b7e906b505b8b4d4c291c532f0`（987 行；单日快照，样本 session=`2026-10-09`）

```
instrument_id:large_string
session:date32[day]
float_mktcap:double
available_at:timestamp[us, tz=Asia/Shanghai]
source:large_string
revision:large_string
quality_status:large_string
```

`available_at` 样本值：`2026-10-09T18:00:00+08:00`（与 session 同日 18:00 Asia/Shanghai）。

**B. `data/v2/float_mktcap/float_mktcap_daily_tushare.parquet`**  
sha256：`4e397c2c5022a31f16bfb9e4d2f0a68430f81387f5e95635d86ba21bb46c9aa3`（9,756,821 行）

```
instrument_id:large_string
trade_date:timestamp[us]
float_mktcap:double
total_mv:double
turnover_rate:double
source:large_string
schema:large_string
quality_status:large_string
promotion_approved:bool   # 盘上 unique = [false]
```

**无列 `available_at`**（由 reader 合成，见下）。

**历史长表（研究密封窗推荐）**：`float_mktcap_daily_from2015_tushare.parquet`  
sha256：`346d0dda8a95e8d209fd388cfb1aad5425745fc0b5eb0a16dd4de3ab3d72a1ef`  
manifest：`date_min=2015-01-05` … `date_max=2026-10-09`；`promotion_approved=false`；列同 daily_tushare（含 `promotion_approved`）。

短窗 manifest（`data/v2/float_mktcap/manifest.json`）：`promotion_approved=false`；指向短 daily + asof（研究不可晋升）。

### 2.2 Reader 语义（`quantlab/data/v2_readers.py`）

- `load_float_mktcap_asof` / `load_float_mktcap_daily` / `FloatMktcapSessionLookup`：入口存在。
- `_read_float_daily` 注释原文要点：**「tushare daily_basic is EOD; available_at = session 18:00 CST proxy (documented)」** — 对 `trade_date` 表合成  
  `available_at = session + 18 hours`（naive→按 session 日），`revision="tushare_daily_basic"`。
- `FloatMktcapSessionLookup`：**Priority: v2_daily (exact session) > v2_parquet (asof exact) > stale_carry**；**Never invents values**；`promotion_approved` 恒 False。
- Reader **不自动做 T−1 偏移**——「用哪一会话的市值」由调用方决定。

### 2.3 研究级断言建议（签脚本前须钉）

对交易日 **T**（截面日）：

1. 取流通市值行：`trade_date = prev_trading_session(T)`（**T−1**，按交易日历，非自然日−1）。  
2. PIT：合成/表内 `available_at ≤ decision_cutoff(T)`（建议决策钟点与既有 18:00 Asia/Shanghai EOD 代理一致；若 cutoff 在 T 开盘前，则 T 日 EOD 市值不可用——故必须用 T−1）。  
3. `float_mktcap` 缺失 / ≤0 / 无行 → 该票当日 **无效**（不进残差、不进 α）；**禁止静默改用 T 日市值**。  
4. 表选择：密封/X2 长窗用 **`float_mktcap_daily_from2015_tushare.parquet`**（sha 上表）；`float_mktcap_asof.parquet` **仅**单日快照，**不得**当历史序列。  
5. 实现 sha 在叶27 独立 `.ok` 窗重钉（本回执不签）。

**本项状态：GAP**（路径与列 OK；T−1/`available_at` 脚本断言未钉）。

---

## 3) 510300 单一路径 + 收益定义

### 3.1 三路径对照

| 路径 | promotion_approved | 关键列 | 文件 sha256 | 备注 |
|---|---|---|---|---|
| `data/v2/etf/etf_daily_adj.parquet` | **文件无该列**；研究消费已钉（AI 复权回执）；coverage `510300.SH` 20150105→20261016（本机切片 2862 行，`close_hfq` nulls=0） | `ts_code,trade_date,pre_close,open,high,low,close,…,adj_factor,open_hfq,…,close_hfq,pre_close_hfq,available_at,…` | `48b21e84695b120b8621eff11f31f3e47879bfc05c93d3d979ddab9220ffd74c` | **研究级主推** |
| `data/v2/etf_510300/panels/sh.510300.parquet` | **false**（manifest） | `open,high,low,close,volume,factor,…`（**无** `close_hfq` / `pre_close`） | `cd90a4fa083cc4c57d710b8450c63d16858a393d42bc14a6a2a9379967d6bd87` | manifest gaps：limit 仍 null；跨源 |
| `data/bench/510300_daily.parquet` | **false**（manifest） | `date,open_raw,close_raw,…,open_hfq,close_hfq,…` | `cb0653afc7018f1800728c38bc31f659a46366531311ab7fb3058d14381ed776` | 截止 as_of 2026-10-09 |

### 3.2 研究级单一路径推荐（叶27 β）

- **路径**：`data/v2/etf/etf_daily_adj.parquet`，过滤 `ts_code == "510300.SH"`。  
- **收益定义（hfq close-to-close）**：  
  `r_510300(t) = close_hfq(t) / close_hfq(t−1) − 1`  
  （与 `docs/v2/AI_ADJ_PRICE_RECEIPT_ZH.md`「基准 510300 `close_hfq`」一致；**非** raw close-to-close 作主规格）。  
- **文件 sha256**：`48b21e84695b120b8621eff11f31f3e47879bfc05c93d3d979ddab9220ffd74c`。  
- β 窗断言沿预注册：60 会话 / 最少 40；不足 → 该票当日无效。  
- 另两路径可作交叉核对，**不得**与主路径混用而不披露。

**本项状态：GAP**（推荐已给出；叶27 `.ok` 仍须写死路径+定义+sha）。

---

## 4) 涨跌停列名：`limit_up` / `limit_down`

### 4.1 列名确认

- 预注册优先名 `limit_up_flag` / `limit_down_flag`：在 1c85 / asof_extend / asof_extend_tushare 各抽 20 个 panel（共 60）中 **0 命中**。  
- 盘上实际列名：**`limit_up` / `limit_down`**（boolean/double 旗或价，类型为 `double`；沪深样本非空率高）。  
- 覆盖文档：`docs/v2/LIMIT_COVERAGE_2018.md`（sha 见文首）；`docs/v2/ALPHA_DATA_REQUESTS_STATUS.md` 亦指向该文。

### 4.2 Panel 路径

| 段 | 路径 | 说明 |
|---|---|---|
| ≤2026-06-30 | `data/local_market/1c85fd9aceaa03c3c4863bec/panels/{ex}.{code}.parquet` | 沪深 `limit_up`/`limit_down` 覆盖见 LIMIT_COVERAGE |
| ≥2026-07-01 | `data/v2/asof_extend_tushare_202610/panels/`（ACCEPT 默认） | schema 含 `limit_up`,`limit_down`,`tradestatus`；**无** `pre_close` |
| 回退 | `data/v2/asof_extend_202610/panels/` | 同有 `limit_up`/`limit_down` |

沪深样本（sh.600000 1c85）：`limit_up`/`limit_down` nulls≈5/3002；`tradestatus` nulls=0。

### 4.3 北交所缺口（披露）

- 1c85 **有列名** `limit_up`/`limit_down`/`tradestatus`，但 **值全空**：抽样 bj.920000 全 175 行 null；前 30 个 `bj.*` panel 均为双列全 null；`LIMIT_COVERAGE_2018.md`：2021+ 北交所 limit/tradestatus **0.0%**（约 23.3 万行级缺口）。  
- HI_LIQ 主宇宙通常沪深，叶27 若触 BJ：**缺有效涨跌停旗 → 不得静默当未触板**；建议无效或显式豁免并披露。

**本项状态：列名 OK；北交所覆盖 GAP（披露）**。

---

## 5) 附：停牌优先序 / capacity_adv

### 5.1 停牌

| 源 | sha256 | 关键列 | 建议优先序 |
|---|---|---|---|
| `output/strategy_hiliq/universe_mask_hiliq_v1.parquet` | `c5433e80a74ac3acc0cd5a52d57fdd0bda5ed578fb86fb98cbd652ccb9f1b9af` | `date,instrument,in_universe,st,**suspended**,young,adv_fail,adv20_yuan` | **① 宇宙无效**：`suspended==True` → 不进 α/活跃集 |
| `data/v2/suspend_flags/suspend_flags_v2.parquet` | `ac5c10fde28a5dfbea10b755a2b79df1fc876690c1c7d7aebf5134f53a447377` | `halted_fullday,intraday_halt,is_resume_day,resume_announced,tradestatus_v2,…` | **② 细节/复牌披露**；manifest `cutoff_date=20261014`（其后增量待 Data） |

`suspend_d` 为 Tushare raw 目录语义，**不是**掩码列名。

### 5.2 capacity_adv 暴露

- 预注册残差第 5 步需要 vs capacity_adv 暴露/活跃指示。  
- **主编排 FYI（2026-10-25 ≈06:34 ET）已钉**：暴露取 capacity_adv **权重表 `target_weight`**；主称 sha 前缀 `5e720335` / 表 sha 前缀 `3b288c83`。  
- **Data 本回执不重复挖**路径/全长 sha（以主钉为准）；旁证掩码列 `adv_fail`/`adv20_yuan` 仍可用作宇宙侧，不替代已钉暴露定义。  
- **状态：主已钉**（非 Data UNKNOWN；签叶27 `.ok` 时实现对齐主钉即可）。

---

## 6) 非动作

- **不签**叶27 / 叶25 / 补跑 / moneyflow 任何新 `.ok`
- **不挡**叶25（窗 10:00–10:45 ET；现盘钉由主编排）
- 不改 `research/`；不 git commit；不写生产权重  
- **live=false**

## 7) 回执元数据

- 产出路径：`docs/v2/audit/DATA_LEAF27_CONTRACT_GAP_ALIGN_20261025_ZH.md`（新建，禁覆盖）
- 本文件 sha256：见落盘后 `sha256sum`（由执行器回报全长）
