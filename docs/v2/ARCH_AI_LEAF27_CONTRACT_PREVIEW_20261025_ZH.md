# Arch：叶27 契约预告（预注册 r1 FROZEN；**不签 .ok**）

- 角色：QuantLab Arch
- 时刻（America/New_York）：2026-10-25T06:24:38-04:00
- **修订**（America/New_York）：2026-10-25T06:40:07-04:00
  - 原因：并入 Data 叶27 契约缺口对齐（研究级推荐路径写死；签 .ok 前仍须重钉 sha）
  - Data 回执：`docs/v2/audit/DATA_LEAF27_CONTRACT_GAP_ALIGN_20261025_ZH.md` sha256 `cc85cb34dbaf7dba196e39ec17ce4dfb518302a48ea80769646230305257a745`
  - 前内容 sha256 `9c5d46eb818f0921462b1533764629413a623a08af80a2106b8890e674958b0f` → **SUPERSEDED**（内容级；本文件路径不变；该版已含 Alpha capacity_adv CLOSED）
- **修订**（America/New_York）：2026-10-25T06:36:34-04:00
  - 原因：并入 Alpha §1.5 闭合（capacity_adv 暴露钉）
  - 钉：`docs/v2/ALPHA_LEAF27_CAPACITY_ADV_EXPOSURE_PIN_20261025_ZH.md` sha256 `5e720335400255fffd1ddff10fc24b6ae1766188c2a3d3a5047aad48149e07b7`
  - 前版预告 sha256 `ac853d7f321aca19dc7260c2ad5c26880b74950cad35df59008fdfbad1297641` → **SUPERSEDED**（内容级；本文件路径不变）
- 预注册：**FROZEN** `docs/v2/AI_LEAF27_OVERNIGHT_IDIO_IVOL_PREREG_r1.md` sha256 `f12965dadde8a9563aee31065698a73b72339bf61d7572ed1afe1be083dafdcf` **MATCH**
- who_pays DRAFT（仅交叉引用，**不冻结**）：`docs/v2/AI_LEAF27_OVERNIGHT_IDIO_IVOL_WHO_PAYS_DRAFT_ZH.md` sha256 `4a0eec1a4d1694be7a91b8cd291b8d1547e68ff41f8b9121e90dd7f44967282b`
- **本轮不签任何 .ok**（叶27 / 叶25 / 补跑 / moneyflow 新签一律不签）
- **不挡叶25**：窗 10:00–10:45 ET；现盘 `.ok` sha8 `7b279d47`（全长 `7b279d4731760de3c6b194b1d5d93e47acfc5607fa5d05f1defbd5dce07e31a7`）
- 闸审 / X2 仍 **另签**；live=false；promotion_approved=false

## 0. 冻结要点（摘预注册；Arch **不改**）

| 项 | 冻结值（摘录） |
|---|---|
| mechanism_tag | `g1g5_ashare_on_minus_id_idio_ivol_v1` |
| 主规格方向 | **`α_raw = −ivol`**（禁冻结后翻号；`+ivol` 仅敏感性） |
| β | **510300** · 滚动 **60** 会话 · 最少有效 **40** |
| W（ivol） | **20** 会话 · 最少有效残差 **15** |
| 主拆分量 | `on_minus_id = r_on − r_id`；`r_on=open/pre_close−1`；`r_id=close/open−1` |
| 残差顺序 | SW L1 demean → log 流通市值（T−1）→ 滚动β(510300) → capacity_adv 暴露/活跃指示 → `ivol=std(ε,W)` → `α_raw=−ivol` |
| 宇宙 | HI_LIQ_V1.1 主 / FULLA_V1 对照（不新开宇宙） |
| 叶25 | 窗冲突让路；**禁复用**叶25 `.ok` |

## 1. 契约对齐表（只读检索；未知标 UNKNOWN / 待 Data）

依据：预注册 §2–§7；Data 缺口对齐回执（上表 full sha）；盘上 `docs/v2`、`data/v2` manifest / parquet schema（`pyarrow.parquet.read_schema`，不读收益页）。**不臆造列名**。

### 1.1 OHLC 与拆分（价量、复权/拆分字段）

| 需要（预注册） | 盘上已有 / 研究级推荐 | 缺口 / assertof |
|---|---|---|
| `open` / `close` / **`pre_close`**（算 `r_on`/`r_id`） | **研究级推荐写死**：`data/v2/tushare_raw/daily/{YYYYMMDD}.parquet`（列 `open,high,low,close,pre_close,vol,amount`；覆盖见 Data 回执） | panel（1c85 / asof_extend*）**仍缺**列名 `pre_close`——不得静默用 `reference_price`。缺 `open`/`pre_close` 或 `pre_close≤0` → 该票当日 **无效**。**签 `.ok` 前重钉路径 sha** |
| 复权 / 拆分 | 旁路：`data/v2/adj/adj_factor_2023h2plus.parquet`；AI 复权回执钉「评价层」；拆分主轴按预注册 **未复权** OHLC/`pre_close` | **GAP（实现 sha）**：叶27 **实现 sha 未钉**；若坚持走 panel 须另钉前日收来源+复权 sha |
| 可选结构字段 `overnight_ret`,`intraday_ret`,`on_minus_id` | 预注册 §7：可选，**须重钉实现 sha** | **不得假设**与公式字节级一致；默认按公式现算 |

### 1.2 申万一级 SW L1

| 需要 | 盘上已有 | 缺口 / assertof |
|---|---|---|
| SW L1 PIT 成员（行业 demean） | **有（默认可晋升）**：`data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet` 列 `instrument_id,sw_code,sw_name,in_date,out_date,available_at,source,revision,quality_status,schema,is_new`；manifest `promotion_approved=true`；入口 `load_sw_l1_members` / `docs/v2/SW_XLS_PREFIX_AND_EITIME.md` | 回退路径 prefix/vote **强制不可晋升**；实现须钉 **tushare 默认路径 + sha**；名过少行业仅 demean 并披露 |

### 1.3 市值 T−1（log 流通市值）

| 需要 | 盘上已有 / 研究级推荐 | 缺口 / assertof |
|---|---|---|
| log 流通市值 PIT，**T−1** | **表有**；研究级推荐表：`data/v2/float_mktcap/float_mktcap_daily_from2015_tushare.parquet`；会话 **T 用上一交易日** 行；旁路 asof / daily_tushare 见 Data 回执 | **GAP / 断言仍待钉**：预注册硬规则「缺则不得静默用 T」。须在叶27 脚本 `.ok` 前钉：**T−1 取法 + `available_at` 断言**（reader 合成 EOD≈会话 18:00 Asia/Shanghai；**不自动做 T−1**）。**签 `.ok` 前重钉表 sha** |

### 1.4 510300 β

| 需要 | 盘上已有 / 研究级推荐 | 缺口 / assertof |
|---|---|---|
| 510300 **日收益**（主规格唯一基准） | **研究级推荐写死**：`data/v2/etf/etf_daily_adj.parquet` 滤 `ts_code=="510300.SH"`；**hfq close-to-close**：`r_m = close_hfq_t / close_hfq_{t-1} − 1`（对齐 AI 复权回执） | 另两路径（`etf_510300/panels`、`data/bench/510300_daily`）`promotion_approved=false`，仅交叉核对、禁混用。**签 `.ok` 前重钉路径+定义+sha** |
| β 窗 | 预注册：60 / 最少 40 | 实现断言：不足 → 该票当日无效 |

### 1.5 capacity_adv 暴露 / 活跃指示 — **CLOSED（Alpha 钉）**

| 项 | 写死值（Alpha 钉） |
|---|---|
| 状态 | **CLOSED**（原 UNKNOWN 已闭合；Data **不重复挖**） |
| 暴露 | **`target_weight`**（连续组合权重；≠ ADV 分位；≠ 活跃 0-1） |
| 路径 | `output/strategy_hiliq/legs/g1g5_capacity_adv_hiliq_v1_1_daily_weights_20261014_195620.parquet` |
| 权重文件 sha256 | `3b288c832b956820af9802f02861af459e215e7d4097a6420724b26cf2d31c4d`（sha8 `3b288c83`） |
| 活跃指示 | `active_capadv := 1{target_weight > 0}` — **仅 Jaccard** / 活跃集硬闸披露；**不得**作残差主轴 |
| **禁止** | ADV 分位 / `adv20_yuan`/`adv_fail` 作第 5 步回归量；用活跃 0-1 代替 `target_weight`；混 moneyflow / 叶26 权重进本步 |
| 钉文 | `docs/v2/ALPHA_LEAF27_CAPACITY_ADV_EXPOSURE_PIN_20261025_ZH.md` sha256 `5e720335400255fffd1ddff10fc24b6ae1766188c2a3d3a5047aad48149e07b7` |
| Arch 审签 | 签叶27 脚本 DIFF 前 **必须按本钉核对**路径字节 + sha MATCH；本轮 **仍不签 .ok** |

### 1.6 停牌 / 涨跌停旗

| 需要 | 盘上已有 / 对齐 | 缺口 / assertof |
|---|---|---|
| 当日停牌 → 无效 | **优先**：宇宙掩码列 `suspended`（HI_LIQ/FULLA；例 `output/strategy_hiliq/universe_mask_hiliq_v1.parquet`）；**辅助**：`data/v2/suspend_flags/suspend_flags_v2.parquet` 列 `halted_fullday,intraday_halt,is_resume_day,resume_announced,tradestatus_v2…`（cutoff 20261014） | 回执须披露实际列名+sha；`suspend_d` 为 Tushare raw 目录语义，非掩码列名；cutoff 后增量待 Data |
| 当日涨跌停 → 不参与截面回归与 ivol 更新；持仓 gate=0 | **列名对齐写死**：`limit_up` / `limit_down`（**非** `limit_up_flag`/`limit_down_flag`）；路径：1c85 panels（≤2026-06-30）∪ `asof_extend_tushare_202610/panels`（2026-07+） | **BJ 值空须披露**（1c85 北交所有列名但值全空 / LIMIT_COVERAGE 0%）。HI_LIQ 主宇宙通常沪深；触 BJ 不得静默当未触板。**签 `.ok` 前钉触板定义+路径 sha** |
| 复牌首日 | `is_resume_day` / `resume_announced` 在 suspend_flags_v2 **有** | 预注册：可算则计入残差；`is_resume_day` 仅披露/入场闸参考，**不改主公式** |

## 2. 缺口清单（签叶27 `.ok` 前须闭合或明示研究级豁免）

### 2.1 研究级推荐已写死（仍须签 `.ok` 前重钉路径 sha）

1. **OHLC/`pre_close`**：推荐 `data/v2/tushare_raw/daily/{YYYYMMDD}.parquet`（Data `cc85cb34…`）；panel 仍无 `pre_close` 列名。  
2. **510300 日收益**：推荐 `data/v2/etf/etf_daily_adj.parquet` · `510300.SH` · **hfq close-to-close**（同上 Data 回执）。  
3. **涨跌停列名**：对齐 **`limit_up`/`limit_down`**（非 `limit_up_flag`）；沪深路径见 §1.6。  
4. **停牌优先序**：掩码 `suspended` 优先；`suspend_flags_v2` 辅助（细节/复牌披露）。  
5. **capacity_adv 暴露/活跃指示**：**CLOSED** — Alpha 钉 sha256 `5e720335400255fffd1ddff10fc24b6ae1766188c2a3d3a5047aad48149e07b7`；暴露=`target_weight`；权重 sha `3b288c832b956820af9802f02861af459e215e7d4097a6420724b26cf2d31c4d`；活跃仅 Jaccard；禁 ADV 分位；Data 不重复挖。  

### 2.2 仍 GAP（签 `.ok` 前必须闭合）

1. **float T−1 断言**：推荐表 `float_mktcap_daily_from2015_tushare.parquet` 已写；**T−1 / `available_at` 脚本断言未钉**（禁静默用 T）。  
2. **路径/实现 sha 重钉**：OHLC raw、510300 `etf_daily_adj`、limit panels、suspend 掩码——研究推荐已给，**独立 `.ok` 窗须重钉 full sha**。  
3. **BJ limit 覆盖**：北交所 `limit_up`/`limit_down` 值空须在回执披露；缺有效旗不得静默当未触板。  
4. **panel 无 `pre_close`**：若实现改走 panel，须另钉前日收来源（不得静默 `reference_price`）。  

## 3. 非动作（本预告）

- **不签**叶27 任何 `.ok`；不签自检 / X2 / Book-Smoke  
- **不挡**叶25（`7b279d47` @ 10:00–10:45 ET）  
- 不改 `research/`；不改预注册正文；不 git commit  
- moneyflow deeper P0 已 CONSUMED（研究闭合）；与本叶正交无关  
- live=false

## 4. 下一步（供主裁，非本轮执行）

1. AI：按预注册 + **本预告研究推荐**交脚本 DIFF（残差五步 + 旗名披露 + T−1 断言）；第 5 步严格按 Alpha 钉；DIFF 首页引用 Data 回执 full sha + Alpha 钉 full sha。  
2. Data：float T−1 断言若需额外表/日历旁证可补；BJ limit / suspend cutoff 后增量按需。  
3. Arch：静态审 DIFF 时按 **Alpha 钉 + 本预告** 核对（暴露=`target_weight`；权重路径+sha MATCH；活跃仅 Jaccard；禁 ADV 分位；OHLC/510300/limit 对齐推荐路径）→ **另窗**签叶27 `.ok`（不复用叶25 钉）。**本轮仍不签 .ok**。  
