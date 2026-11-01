# g1g5_ashare_insider_increase_v1 — X2 日权重回执（2026-10-13 ~13:35 ET；文件戳 20261014_011841 为机时）

预注册：docs/v2/AI_G1G5_INSIDER_INCREASE_WHO_PAYS_PREREG_ZH.md（含选题理由；跑前写定，跑后未调参）
脚本：research/g1g5_insider_increase_weights.py（叶3 模板，事件过滤/HOLD=60/后续公告重置窗口）
权重：output/ai_factory/g1g5_insider_increase_daily_weights_20261014_011841.parquet（+ .meta.json）
meta：output/ai_factory/g1g5_insider_increase_run_meta_20261014_011841.json；日志 g1g5_insider_increase_run.log

## 计数/合规
74816 行 / 668 日 / 112 标的；Σw≡1；无负权；无stub；单名 max 4%；行业 max 24%；
510300 均值 21.0%（20%–44%）；日均 19.75 名（max 20，0 名日=0）——持仓密度达标（压舱≤60%）。
事件：过滤后 526 条，入册 523（2023:74/2024:157/2025:191/2026:101）。换手：日均单边 1.97%，累计 13.12（≈年化 5.0 倍）。

## 自检
- 逐日 Jaccard vs 14 包：max 0.154（accrual_quality）；vs capacity_adv max 0.098/均 0.035；vs 叶1 0.12；≥0.7 占比全 0 → 无同构硬拒。
- G6 pass；peak 722MB（time 739MB）。
- 去β：β=0.856，残差α=+3.84%/年；ρ_excess vs capacity_adv=0.250（原始 0.379）→ 路线②机械门通过。
- 毛 CAGR 12.13%（510300 9.45%，capacity_adv 12.07%）；毛 MDD −18.03%（510300 −16.25%）；超额 +2.28%/年。
- 分年 α：2024 −2.07%，2025 +2.91%，2026 +9.52%（集中在 2026 下跌段的防守，β 降至 0.70）。

## 风险
α 来源偏 2026；持仓偏央国企与周期/能源（高频持有：000301 东方盛虹、600905 三峡能源、002493 荣盛石化、601117 中国化学、601668 中国建筑、601898 中煤能源等；2024-10 后“提质增效”增持潮政策驱动），政策性拥挤可能不可持续；
未复权收盘价（高股息持仓除息日被记为亏损，方向上低估）；2024H1 池前视；无增持金额强度；单叶毛 CAGR 刚到 KPI 下沿、MDD 合格，扣费后可能跌出 12%。
promotion=false；live=false；禁 GP；未跑 Book-Smoke。
