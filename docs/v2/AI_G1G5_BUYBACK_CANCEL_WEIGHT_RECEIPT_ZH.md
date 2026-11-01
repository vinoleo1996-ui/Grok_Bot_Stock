# g1g5_ashare_buyback_cancel_v1 — X2 日权重回执（2026-10-13 ~13:05 ET 运行；文件戳 20261014_010405 为机时）

预注册：docs/v2/AI_G1G5_BUYBACK_CANCEL_WHO_PAYS_PREREG_ZH.md（跑前写定，无收益探针调参）
脚本：research/g1g5_buyback_cancel_weights.py（叶1 earnings_event 模板：去跳空确认、HOLD=60、120日首次去重、新近度排序、增逐日Jaccard全先验）
权重：output/ai_factory/g1g5_buyback_cancel_daily_weights_20261014_010405.parquet（+ .meta.json）
meta：output/ai_factory/g1g5_buyback_cancel_run_meta_20261014_010405.json；日志 g1g5_buyback_cancel_run.log

## 计数/合规
28724 行 / 668 日（2024-01-02~2026-10-09）/ 43 标的；Σw≡1；min w=0；无stub；单名 max 4%；行业 max 8%（≤28%）；
池 mid_large PIT 298（锚定 2024-06-28）；510300 压舱 均值 82.1%（min 60%）；日均 4.49 名（max 10，0 名日=0）。
事件：池内注销型回购 76 条（去重后入册 53；2023:1/2024:21/2025:17/2026:14）。

## 自检
- 逐日 Jaccard vs 14 个先验包（accrual_quality、capacity_adv、capacity_adv_negevent、d1_val_resid、earnings_event、etf_core_sleeve、friction_cost_redesign、idx_rebal_flow、indcap_momneut_ocf、margin_delta、moneyflow_resid、northbound_flow、resid_etf 等）：max 0.20（vs earnings_event），vs capacity_adv max 0.08；≥0.7 日占比全 0 → 无同构硬拒。
- G6 pass；peak RSS 730.5MB（/usr/bin/time 748MB）≤1.5GB。
- 去β（vs 510300，无成本 close-to-close）：β=0.956，残差α=+0.58%/年；ρ_excess(去β) vs capacity_adv=0.213（原始超额ρ 0.317）→ 路线②机械门 ρ<0.5∧α>0 通过。
- 毛 CAGR 9.67%（510300 9.45%，capacity_adv 12.07%）；毛 MDD −15.18%（510300 −16.25%）；超额 +0.10%/年。
- 分年残差α：2024 +3.16%，2025 −0.68%，2026 −2.70%（衰减）。

## 判读
机械门过，但经济上近似 510300 克隆：α 仅 +0.58% 且 2025/2026 为负，82% 压舱，事件稀疏。单叶 KPI 门（CAGR 12–18%）毛值即不达。
作为卫星：α 太薄，难以让组合在 60万/100万扣费后跑赢主干。

## 缺口
无回购金额/占市值字段；未写用途的回购方案漏检；2024H1 池前视；未复权收盘价；仅做过全市场事件计数（非收益探针）。
promotion=false；live=false；禁 GP；未跑 Book-Smoke。
