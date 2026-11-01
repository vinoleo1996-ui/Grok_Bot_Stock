# STRATEGY FULLA B4 X2 回执（研究轨）

**时间**：2026-10-14 ~08:00 ET  
**窗口**：X2 2024-06-03→2026-10-09（**样本内**）  
**引擎**：`quantlab.cli book-smoke --run-nav` / `ExecConfig.strategy_v1` / core=0 stock=1 / 按手取整  
**live / promotion**：false（**未动** FROZEN_CONFIG / 纸面轨 / 密封窗）  
**双轨**：FULLA_V1 = **研究 only**；纸面 = HI_LIQ_V1（并行，本回执不替代）  
**预注册**：`docs/v2/STRATEGY_FULLA_UNIVERSE_PREREG_ZH.md`  
**合成**：B4 = capacity_adv / earnings_event / insider_increase **50/25/25**；per-leg topN（60万 N=6，100万 N=10）；组合单名 ≤6%，超额→510300  

权重目录：`output/strategy_fulla/b4/`  
脚本：`research/strategy_fulla_b4_x2.py`

## 1. 主表：B4 FULLA vs 基线（同引擎）

| 臂 | AUM | CAGR | MDD | Calmar | 日胜率 | 月胜率 | 填单率 | 成本/初资 | vs MDD≤25% |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| **B4 FULLA** | 60万 | **16.80%** | **−19.95%** | 0.84 | 50.3% | 53.6% | 76.0% | 6.92% | 未破 |
| **B4 FULLA** | 100万 | **13.78%** | **−22.21%** | 0.62 | 49.6% | 53.6% | 77.0% | 6.35% | 未破 |
| B4 top300 conc_v2 | 60万 | 15.11% | −13.85% | — | — | — | — | ~2.5% | 未破 |
| B4 top300 conc_v2 | 100万 | 14.24% | −13.17% | — | — | — | — | ~2.2% | 未破 |
| capacity_adv FULLA | 60万 | −2.83% | −27.86% | −0.10 | 48.5% | 46.4% | 62.9% | 2.63% | **破** |
| capacity_adv FULLA | 100万 | −1.41% | −31.16% | −0.05 | 48.3% | 50.0% | 67.5% | 2.83% | **破** |
| capacity_adv top300 | 60万 | 13.82% | −10.07% | 1.37 | — | — | — | — | 未破 |
| capacity_adv top300 | 100万 | 12.23% | −11.62% | 1.05 | — | — | — | — | 未破 |

### 解读（研究，非晋级）

- **B4 FULLA 两档 MDD 均未破 Leo 25%**（−19.95% / −22.21%），相对单腿 capacity_adv FULLA（破门且 CAGR 为负）大幅改善：事件腿 50% 预算显著缓冲了全 A 流动性尾部。
- 相对 **B4 top300**：60万 CAGR 更高（+1.7pp）但 MDD 更深（−6.1pp）；100万 CAGR 略低（−0.5pp）且 MDD 更深（−9.0pp）。**成本显著更高**（~6–7% vs ~2%），填单 ~76–77%（优于单腿 FULLA 的 63–68%，仍低于 top300 集中化）。
- 样本内结果，不作密封/前向声明。

![CAGR/MDD](../../output/strategy_fulla/b4/fulla_b4_cagr_mdd.png)

## 2. 分年 & NAV

| AUM | 2024 | 2025 | 2026（至10-09） |
|---|---:|---:|---:|
| B4 FULLA 60万 | 5.54% | 31.54% | 9.40% |
| B4 FULLA 100万 | 0.09% | 30.60% | 6.74% |

![分年](../../output/strategy_fulla/b4/fulla_b4_yearly.png)

![NAV](../../output/strategy_fulla/b4/fulla_b4_nav.png)

## 3. 可选研究叠加（非主推；不晋级）

| 臂 | 配比 | 60万 CAGR/MDD | 100万 CAGR/MDD | MDD≤25% |
|---|---|---:|---:|---|
| 叶11 satellite | cap 50 / report_rc_allup 50 | 13.04% / −21.01% | 10.33% / −22.48% | 两档未破 |
| 叶14 satellite | cap 50 / insurer_surv 50 | 12.82% / −20.32% | 7.07% / **−26.74%** | **100万破** |
| S6 shadow | cap/ee/eqincent 50/25/25 | 23.35% / −21.33% | 21.21% / −22.34% | 未破（**事后挑选，不晋级**） |

- 叶11/叶14 均未在两档同时稳定优于 B4 FULLA。
- S6 数字更好但属影子/事后挑选族，**禁止 promotion**；仅作对照。

## 4. 密封窗

**N/A**。FULLA 腿权重仅自 **2024-01-02** 起；密封窗 2018-01-02→2024-05-31 **无完整权重**，不发明权重。2024-01-02→2024-05-31 仅为部分重叠，**不作密封声明**。

## 5. 小盘归因（仅披露）

定义：PIT `total_mv` 沪深 A 截面**后 30%**（非剔除条件）。

| 指标 | B4 60万 | B4 100万 |
|---|---:|---:|
| 真小盘权重×时间均值 | **0.27%** | **0.21%** |
| 有小盘持仓的交易日占比 | 7.2% | 9.1% |
| 低于市值中位数权重均值 | 1.41% | 1.41% |

**解读**：B4 FULLA 真小盘贡献极低（≪1%）；收益主要来自中大盘 + 旧 top300 外中盘流动性票，与 capacity_adv ADV 排序一致。小盘可买政策下仍几乎不持有后 30%。

## 6. 申万一级（B4 60万，股票袖，权重×时间）

![行业](../../output/strategy_fulla/b4/fulla_b4_industry_sw_l1.png)

Top：电子 15.5%、通信 12.1%、计算机 7.3%、电力设备 7.0%、汽车 6.4%、基础化工 5.2%、有色 5.1%、医药 4.6%。  
全表：`output/strategy_fulla/b4/b4_60w_industry_share.csv`（100万：`b4_100w_industry_share.csv`）。

## 7. 产物路径

| 类型 | 路径 |
|---|---|
| B4 权重 | `output/strategy_fulla/b4/B4_50_25_25_topN_{60,100}w.parquet` |
| 叶11/叶14/S6 权重 | 同目录 `L11_*` / `L14_*` / `S6_*` |
| book-smoke | `output/strategy_fulla/b4/smoke_*` |
| summary JSON | `output/strategy_fulla/b4/summary.json` |
| 小盘归因 | `output/strategy_fulla/b4/b4_{60,100}w_smallcap_attr.json` |
| 图表 | `output/strategy_fulla/b4/fulla_b4_{cagr_mdd,yearly,nav,industry_sw_l1}.png` |
| 本回执 | `docs/v2/STRATEGY_FULLA_B4_X2_ZH.md` |

## 8. 红线 / 下一步

- live=false；promotion=false；**FULLA 不进纸面**；纸面继续 HI_LIQ 子集（等腿重生）。
- 试验：FULLA B4 + 叶11/叶14/S6 影子对照已落盘；不替换 top300 纸面 B4。
- 阻塞：无（FULLA 研究本项完成）。HI_LIQ 纸面腿重生仍并行，不阻塞本回执。
