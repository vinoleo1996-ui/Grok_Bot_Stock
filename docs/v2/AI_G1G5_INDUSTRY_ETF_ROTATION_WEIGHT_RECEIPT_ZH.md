# g1g5_ashare_industry_etf_rotation_v1 — X2 日权重回执（2026-10-13 ~13:25 ET；文件戳 20261014_011706 为机时）

预注册：docs/v2/AI_G1G5_INDUSTRY_ETF_ROTATION_WHO_PAYS_PREREG_ZH.md（跑前写定，无收益探针；跑后未调参）
脚本：research/g1g5_industry_etf_rotation_weights.py
权重：output/ai_factory/g1g5_industry_etf_rotation_daily_weights_20261014_011706.parquet（+ .meta.json）
meta：output/ai_factory/g1g5_industry_etf_rotation_run_meta_20261014_011706.json；日志 g1g5_industry_etf_rotation_run.log

## 计数/合规
26052 行 / 668 日 / 39 标的（38 只行业/主题 ETF + 510300）；Σw≡1；无负权；无stub；单资产 max 20%；
510300 均值 55.4%（min 40%）；日均 2.23 只 ETF；0 ETF 日 40；调仓 134 次（非零换手 118 次）；
换手：日均单边 5.8%，累计单边 38.8（≈年化 14.6 倍单边）；流动性门 amt20≥2000万元，100万×20% 参与率≤1%。
入选频次最高：801170 交通运输 / 801760 传媒 / 801160 公用事业 / 801780 银行。

## 自检
- 逐日 Jaccard vs 14 包（含叶1/2/3、capacity_adv、etf_core_sleeve、resid_etf）：max 0.143（vs etf_core_sleeve），其余 0 → 无同构硬拒。
- G6 pass；peak 412MB。
- 去β：β=0.999；残差α=−0.64%/年（不过）；ρ_excess vs capacity_adv=−0.145（原始 −0.115）。
- 毛 CAGR 8.25%（510300 9.45%，capacity_adv 12.07%）；毛 MDD −20.62%（510300 −16.25%）。
- 分年 α：2024 −11.68%，2025 +12.16%，2026 −4.42% —— 极不稳定，依赖单年。
- 判读：路线②门（ρ<0.5 ∧ α>0）**未过**；单叶 KPI 门不达；扣费前即跑输 510300。

## 缺口
代表 ETF 为名称关键词映射（主题 ETF 跟踪误差大，PIT 切换）；aum_wan 多缺失，规模自算；份额 T+1；
510300 基准价可能未计分红（ETF 用后复权，略偏向叶）；无 IOPV/折溢价；冲击未建模。
promotion=false；live=false；禁 GP；未跑 Book-Smoke。
