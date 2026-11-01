# AI G1G5 D1 估值残差 asof 权重回执（X2）

- **时间：** 2026-10-13 ~11:01 ET（America/New_York；箱内 CST 同拍）
- **Leo 指令：** 「并行展开」→ 叶 B
- **promotion_approved：** false；不下单；不交 Strategy；禁 stub 前推；不开 GP
- **who_pays 预注册：** `docs/v2/AI_G1G5_D1_VAL_RESID_WHO_PAYS_PREREG_ZH.md`
- **D1：** ACCEPT_FULL 仅研究 asof；**≠** GP/promotion 授权

## 1) 权重产物

| 项 | 值 |
|---|---|
| **路径** | `output/ai_factory/g1g5_d1_val_resid_daily_weights_20261013_110154.parquet` |
| 行数 / sessions / 标的 | **34068 / 668 / 51**（个股活跃 + 510300 压舱名位） |
| 日期跨度 | 2024-01-02 → **2026-10-09** |
| reaches_x2_end | **true** |
| stub_window / stub_forward_fill | false / false |
| 名义结构 | 个股预算均值 **≈0.80** / 510300 压舱均值 **≈0.20** |
| mechanism_tag | `g1g5_ashare_d1_val_resid_v1` |
| universe_id / 选股规则 | `d1_ep_ind_size_resid_mom_ortho_ew_indcap30` |
| 列契约 | `weight_long_v1_20261012` + 别名 |
| meta sidecar | `output/ai_factory/g1g5_d1_val_resid_daily_weights_20261013_110154.parquet.meta.json` |
| run meta | `output/ai_factory/g1g5_d1_val_resid_run_meta_20261013_110154.json` |
| ledger / G6 proof | `debate_ledger_g1g5_d1_val_resid_20261013_110154.jsonl` (+`_g6_proof`) |
| G6 | **pass**（blocked_future + kept_past） |
| peak_rss | **1940.6 MB**（目标 ≤1.0–1.5GB；略超研究目标带，已记；下叶尽量压） |
| 日均单向换手 | **≈0.00618**（月频；33 个非零再平衡日） |
| 行业硬顶 | 申万一级 ≤**30%** |

脚本：`research/g1g5_d1_val_resid_weights.py`

## 2) 机制（相对八败正交）

| 约束 / 臂 | 定义 |
|---|---|
| **主信号** | D1 `pe_ttm`→EP；SW L1 行业 demean → 流通市值三分位 demean → 对 20d 相对 510300 超额简单正交 |
| **PIT** | `available_at` asof；同日 basic 不作开盘前偷看 |
| **持仓** | 低估侧 top20 等权；行业硬顶 ≤30%；压舱 510300 |
| **再平衡** | 月末 + 首日 |

### who_pays（一句）

错误定价纠偏：D1 asof 估值倍数经申万一级行业与流通市值中性后的残差修正；低估侧收敛由边际资金支付相对 510300 的持有窗；并对相对宽基 20 日超额收益暴露做正交化压低；明确非裸 EP/BM/PE 截面排序；明确非残差收益×份额流同构；明确非四臂摩擦/解禁/调仓流/ETF-core 直接持有。

## 3) 相对已败包 Jaccard（样例月活跃个股集）

| 对照包 | Jaccard 均值 | Jaccard 最大 |
|---|---:|---:|
| expand | 0.296 | 0.481 |
| nontextbook / friction_monthly | 0.234 | 0.333 |
| lowturn | 0.244 | 0.296 |
| resid_etf | 0.303 | 0.379 |
| etf_core | 0.183 | 0.217 |
| friction_cost_redesign | 0.246 | 0.290 |
| idx_rebal_flow | **0.000** | 0.000 |
| indcap_momneut_ocf（叶A·八败） | 0.309 | 0.379 |

全部 **≪0.7** → 非换皮；相对调仓流活跃集正交。

## 4) 明确不做 / 边界

- 不开 GP；不交 Strategy；不下单；不密封
- 不把 D1 ACCEPT_FULL 当晋级/GP 授权
- Book-Smoke 由 New Bot / Beta 派 @60万∧100万 vs 510300
- `promotion_approved=false`；若 any_pass=false → 入 WATCH，不交 Strategy

## 5) 请 New Bot / Beta

主测本包：

`output/ai_factory/g1g5_d1_val_resid_daily_weights_20261013_110154.parquet`
