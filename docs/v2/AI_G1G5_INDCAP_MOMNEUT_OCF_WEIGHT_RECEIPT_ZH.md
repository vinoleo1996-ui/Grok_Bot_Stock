# AI G1G5 行业硬顶+动量暴露中性·OCF兑现 权重回执（X2）

- **时间：** 2026-10-13 ~10:57 ET（America/New_York；箱内 CST 同拍）
- **Leo 指令：** 「并行展开」→ 叶 A
- **promotion_approved：** false；不下单；不交 Strategy；禁 stub 前推；不开 GP
- **who_pays 预注册：** `docs/v2/AI_G1G5_INDCAP_MOMNEUT_OCF_WHO_PAYS_PREREG_ZH.md`

## 1) 权重产物

| 项 | 值 |
|---|---|
| **路径** | `output/ai_factory/g1g5_indcap_momneut_ocf_daily_weights_20261013_105739.parquet` |
| 行数 / sessions / 标的 | **34068 / 668 / 51**（50 个股宇宙 + 510300 压舱名位；多数日压舱权重=0） |
| 日期跨度 | 2024-01-02 → **2026-10-09** |
| reaches_x2_end | **true**（50/50 panel 达 X2 末日） |
| stub_window / stub_forward_fill | false / false |
| 日权重合计 | min=mean=max=**1.0**；再平衡日活跃个股≈**17–20** |
| mechanism_tag | `g1g5_ashare_indcap_momneut_ocf_v1` |
| universe_id | `g1g5_mid_large_liquid_top50` |
| 列契约 | `weight_long_v1_20261012` + 别名 `session,instrument_id,weight` |
| meta sidecar | `output/ai_factory/g1g5_indcap_momneut_ocf_daily_weights_20261013_105739.parquet.meta.json` |
| run meta | `output/ai_factory/g1g5_indcap_momneut_ocf_run_meta_20261013_105739.json` |
| ledger / G6 proof | `debate_ledger_g1g5_indcap_momneut_ocf_20261013_105739.jsonl` (+`_g6_proof`) |
| G6 | **pass** |
| peak_rss | **1967.5 MB**（目标 ≤1.0–1.5GB；本机当时 available≈2.4–6GB 且已有 uvicorn 占用；低于 2GB 硬线、略超研究目标带，已记） |
| 日均单向换手 | **0.00903**（月频；33 个非零再平衡日） |

脚本：`research/g1g5_indcap_momneut_ocf_weights.py`

## 2) 机制（相对七败正交）

| 约束 / 臂 | 定义 |
|---|---|
| **主信号 OCF** | `ocf_to_profit` PIT；排除 `np_negative`/`denom_small`；截面 winsor；**非** EP/BM、**非**截面动量排序 |
| **行业硬顶** | 申万一级单行业 ≤**28%**（贪婪选股；max≈5/20 名） |
| **动量暴露中性** | 篮内倾斜使 20d 超额 vs 510300 落入 **±1.5pp**；超阈才倾斜，**不**改选股主轴 |
| **市值带** | 包内 float_mktcap 分位 **∈[0.35, 0.75]** |
| **再平衡** | 月末 + 首日（35 次）→ top20（顶约束后可 17–20） |

### 暴露实测（再平衡日）

| 指标 | 值 |
|---|---|
| HHI 均值 / 最大 | **0.114 / 0.148**（告警阈 0.18；告警率 **0%**） |
| mom 暴露 after 均值 | **+0.02pp** |
| mom 暴露 after \|·\| 均值 | **≈1.59pp**（走廊 1.5pp；部分再平衡日倾斜后仍略超，已如实记） |

### who_pays（一句）

经营现金流相对净利润的兑现落差（OCF/利润 PIT）在中大盘液态宇宙内被错误定价的对手盘，支付本叶相对 510300 的持有窗；另受申万一级单行业硬顶与相对 510300 的 20 日超额强度暴露走廊中性化约束。

## 3) 相对七败 Jaccard（样例月活跃个股集）

| 对照包 | Jaccard 均值 | Jaccard 最大 |
|---|---:|---:|
| expand | 0.233 | 0.333 |
| nontextbook | 0.251 | 0.310 |
| lowturn | 0.209 | 0.250 |
| resid_etf | 0.241 | 0.357 |
| etf_core | 0.106 | 0.185 |
| friction_cost | 0.223 | 0.250 |
| idx_rebal | **0.000** | 0.000 |

全部 **≪0.7** → 非换皮；相对调仓流活跃集正交。

## 4) 明确不做 / 边界

- 不开 GP；不交 Strategy；不下单；不密封
- 不自跑 Book-Smoke（交 New Bot / Beta 派 60万∧100万 vs 510300）
- `promotion_approved=false`；Alpha D1 ACCEPT ≠ 晋级授权
- 首跑曾因行业顶「渐进权重」误拒全员→全压舱；已修贪婪逻辑后重跑本回执包

## 5) 请 New Bot / Beta（可选下一拍）

主测本包：

`output/ai_factory/g1g5_indcap_momneut_ocf_daily_weights_20261013_105739.parquet`

若 Book-Smoke any_pass=false → 入 WATCH，不交 Strategy。
