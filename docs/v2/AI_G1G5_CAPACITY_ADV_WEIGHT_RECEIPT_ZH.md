# AI G1G5 容量/ADV 可成交约束权重回执（X2）

- **时间：** 2026-10-13 ~11:12 ET（America/New_York；箱内戳 `20261013_111219`）
- **Leo 指令：** 「A、B同时展开调研」→ 本线叶 A · 容量敏感
- **promotion_approved：** false；不下单；不交 Strategy；禁 stub 前推；不开 GP
- **who_pays 预注册：** `docs/v2/AI_G1G5_CAPACITY_ADV_WHO_PAYS_PREREG_ZH.md`

## 1) 权重产物

| 项 | 值 |
|---|---|
| **路径** | `output/ai_factory/g1g5_capacity_adv_daily_weights_20261013_111219.parquet` |
| 行数 / sessions / 标的 | **32732 / 668 / 49** |
| 日期跨度 | 2024-01-02 → **2026-10-09** |
| reaches_x2_end | **true** |
| stub_window / stub_forward_fill | false / false |
| 名义结构 | 个股预算均值 **≈0.789** / 510300 压舱均值 **≈0.211** |
| 日均活跃（含压舱） | **≈23.6**；个股侧日均 **≈22.6** |
| 单名硬顶观测 | **max=0.04**（= NAME_CAP） |
| 硬排除 | `600519.SH` / `002371.SZ` 正权重行数 **0** |
| mechanism_tag | `g1g5_ashare_capacity_adv_v1` |
| 选股规则 | `adv_ind_demean_capacity_cap4_ind28_exclude_mega_fillgap` |
| 列契约 | `weight_long_v1_20261012` + 别名 |
| meta sidecar | `output/ai_factory/g1g5_capacity_adv_daily_weights_20261013_111219.parquet.meta.json` |
| run meta | `output/ai_factory/g1g5_capacity_adv_run_meta_20261013_111219.json` |
| ledger / G6 proof | `debate_ledger_g1g5_capacity_adv_20261013_111219.jsonl` (+`_g6_proof`) |
| G6 | **pass** |
| peak_rss | **1994.3 MB**（目标尽量 ≤1.5GB；**未达**。D1/打分阶段 ≈477–478MB；尖峰来自日权展开+九败 Jaccard 对照；未预载收盘价矩阵；未叠 uvicorn） |
| 日均单向换手 | **≈0.0125**（月频；34 个非零再平衡日） |
| 行业硬顶 | 申万一级 ≤**28%** |
| 单名硬顶 | ≤**4%**；ADV 参与率 ≤**2%** @ AUM=100万 |

脚本：`research/g1g5_capacity_adv_weights.py`

## 2) 机制（相对九败正交）

| 约束 / 臂 | 定义 |
|---|---|
| **主信号** | D1 asof `ADV≈float_mktcap×turnover_rate/100`；`log(ADV)` 申万一级行业 demean 后流动性分位（高可成交优先） |
| **容量硬约束** | 单名 `w≤4%`；`w×1e6 ≤ 2%×ADV`；行业 ≤28%；容量∝√ADV 加权 |
| **硬排除** | `600519.SH`、`002371.SZ`（d1_val_resid Book-Smoke 记 target∉actual） |
| **压舱** | 510300；**禁** etf_core 0.70 overlay |
| **再平衡** | 月末 + 首末日 |
| **明确非** | 估值残差 / OCF / 动量主轴 / 四臂 / 解禁份额流 / 调仓事件 |

### who_pays（一句）

可成交容量约束下的流动性溢价/冲击成本错误定价对手盘：以 D1 asof ADV 代理经申万一级行业中性后的流动性分位选股；单名权重与 ADV 参与率双硬顶，压百万元端巨头成交/冲击缺口；明确非估值残差、非 OCF、非截面相对强弱；明确非四臂摩擦/解禁/份额流/调仓/ETF-core。

## 3) 相对已败九包 Jaccard（样例月活跃个股集）

| 对照包 | Jaccard 均值 | Jaccard 最大 |
|---|---:|---:|
| expand | 0.268 | 0.364 |
| nontextbook / friction_monthly | 0.265 | 0.406 |
| lowturn | 0.207 | 0.290 |
| resid_etf | 0.301 | 0.406 |
| etf_core | 0.140 | 0.194 |
| friction_cost_redesign | 0.249 | 0.324 |
| idx_rebal_flow | **0.000** | 0.000 |
| indcap_momneut_ocf | 0.217 | 0.364 |
| d1_val_resid | 0.403 | 0.556 |

全部 **≪0.7** → 非换皮。相对 d1_val_resid 略高（同 mid_large 池），但主轴/约束/排除集不同，叙事正交成立。

## 4) 明确不做 / 边界

- 不开 GP；不交 Strategy；不下单；不密封
- 不自跑 Book-Smoke；由 New Bot / Beta 派 @60万∧100万 vs 510300
- `promotion_approved=false`；若 any_pass=false → 入 WATCH，不交 Strategy
- peak 未压到 ≤1.5GB：已诚实记入；下叶继续压对照读入/展开尖峰

## 5) 请 New Bot / Beta

主测本包：

`output/ai_factory/g1g5_capacity_adv_daily_weights_20261013_111219.parquet`
