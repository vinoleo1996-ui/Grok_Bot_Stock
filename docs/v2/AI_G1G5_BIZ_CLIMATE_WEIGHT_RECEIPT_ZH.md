# 叶21 biz_climate（经营景气：合同负债变化 + 存货周转变化）回执 —— WATCH
- 时间：2026-10-18 00:40 ET
- 预注册：docs/v2/AI_G1G5_BIZ_CLIMATE_WHO_PAYS_PREREG_ZH.md。FROZEN 于 2026-10-18 00:18:58 ET，在建任何 α、读任何收益之前；sha256 df982a39…（见 output/ai_factory/prereg_sha_leaf21.txt）。
- 脚本：research/g1g5_biz_climate_alpha.py（按年分块构建 α/gate 并落盘；评价阶段只读再平衡日）；下游脚本 research/g1g5_leaf19_20_18v_eval.py（CFG 21）和 research/g1g5_poolew_excess.py。
- 产物：output/ai_factory/leaf21_biz_climate/。其中 alpha_{HILIQ,FULLA}_{2018..2026}.parquet 是日度 base-α 向量（主交付）；另有 eval_weights_*_20261018_003628、eval_resume_20261018_003650.json、poolew_excess.json。
- RSS（守护 1.5GB）：
  - 构建峰值 HI_LIQ 0.93GB、FULLA 1.03GB；下游 1.25GB；池等权 1.30GB。
  - 第一版评价阶段在 FULLA 密封窗短暂冲到 1.74GB（进程内 ru_maxrss），第二版在 1.74GB 时被守护杀掉。改为只读再平衡日后峰值 0.46GB，结果与原 FE.weights 逐行一致（HI_LIQ 两窗差异 0）。这两版的产物已作废，未使用。
- 运行时有别的 agent 在跑 book-smoke（约 0.3–0.4GB）；我开跑前查 ps 时它还不存在。
- live=false；promotion=false；未自封；未跑 Book-Smoke；未起 8787；禁 GP；研发资本化和日内反转未启动。

## 覆盖（硬闸，过）
再平衡日可算 α 的名数中位数：HI_LIQ 密封 1545、X2 2881（门槛 ≥300）；FULLA 密封 3319、X2 4586（门槛 ≥800）。

## 结论：WATCH（不交 Alpha 验收）
HI_LIQ（主判）未过：
- 衰减门 v1.1 为 DECAY_DOWNGRADE（最新滚动残差 α −7.5%，H2 净 CAGR ≤510300）。
- GATE_V3 FAIL：叠加后两档都没跑赢 capacity_adv。
- 预注册 Gate B FAIL。
- 新池 IC≈0。
- 对池等权基准：X2 +3.1%（t 0.51），密封 +7.3%（t 1.73）。

## 数字（复权、T+1 开盘、17.5bp；244 主 / 252 对照）
| 宇宙·窗 | 档 | CAGR244 / 252 | MDD | 残差α(对510300) |
|---|---|---|---|---|
| HI_LIQ 密封 | 60万 | −2.25% / −2.32% | −51.9% | −0.1% |
| HI_LIQ 密封 | 100万 | 0.24% / 0.25% | −42.4% | +2.2% |
| HI_LIQ X2 | 60万 | 7.35% / 7.60% | −26.3% | −0.5% |
| HI_LIQ X2 | 100万 | 6.48% / 6.70% | −21.8% | −2.3% |
| FULLA 密封 | 60万 | 1.67% / 1.73% | −39.9% | +3.7% |
| FULLA 密封 | 100万 | 6.91% / 7.15% | −34.9% | +8.3% |
| FULLA X2 | 60万 | 16.61% / 17.20% | −28.0% | +7.7% |
| FULLA X2 | 100万 | 20.48% / 21.22% | −19.2% | +10.3% |

- 自检（LC 引擎，X2 20 名）：
  - HI_LIQ 净 14.80%，MDD −18.1%，残差α +4.6%（2024 +8.7 / 2025 +6.1 / 2026 −0.5），双边换手 4.1%/日，可交易。
  - FULLA 净 28.48%，MDD −17.5%，残差α +16.3%，衰减门 KEEP，GATE_V3 形式上通过。但对 FULLA 池等权的超额只有 X2 +5.2%（t 0.89）、密封 +5.1%（t 1.41），收益主要是小微盘 β，与叶19 FULLA 同一现象。裸 FULLA 本来也不进纸面。
- ρ(去β)：
  - vs capacity_adv −0.21、vs cap_hiliq 0.34（Gate A 过）。
  - vs 叶19 0.75、叶20 0.51、insurer_surv_hiliq 0.62 → 与这些同用时只能作过滤。
  - Jaccard max 0.11，无硬拒。
- 组合（cap80 + 叶20，旧 capacity_adv 书）：
  - HI_LIQ：60万 12.60%→12.37%（−0.23pp），100万 13.79%→13.46%（−0.33pp），MDD 变浅；对 B4 分别 −1.00pp / −1.18pp。
  - LC Gate：HI_LIQ current/A/B 全过，FULLA A/B 过、current 不过。
- IC（新池，HAC 仅披露）：HI_LIQ 20d 0.0002（t 0.05 / HAC 0.07）；FULLA 20d 0.0027（0.88 / 1.24）。

## 披露
- 存货周转用 revenue × (1 − 毛利率) 推出的 COGS 代理（PIT 表里没有 oper_cost）。
- 合同负债与预收合并，口径跨 2020 年准则切换保持连续。
- 金融（银行、非银）已剔除。
- 评价权重为等权 4%，top-N 按 α 序取。
