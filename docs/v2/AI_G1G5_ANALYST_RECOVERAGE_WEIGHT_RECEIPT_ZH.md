# G1G5 叶12 权重回执：g1g5_ashare_analyst_recoverage_v1（研究级，promotion=false，live=false，未跑 Book-Smoke，禁 GP）
- 预注册：DRAFT 2026-10-14 00:27:56 ET（先于计数和收益）；**FROZEN 00:28:09 ET**：docs/v2/AI_G1G5_ANALYST_RECOVERAGE_WHO_PAYS_PREREG_ZH.md。约 00:28 ET 开跑，00:29 ET 出结果。
- 脚本：research/g1g5_analyst_recoverage_events.py、research/g1g5_analyst_recoverage_weights.py；日志 output/ai_factory/g1g5_analyst_recoverage_run.log
- 权重：output/ai_factory/g1g5_analyst_recoverage_daily_weights_20261014_122813.parquet，sha256 bd43e0ec0e8501213bca1031eaeafb034017685a5d92f41f28b47b7cbed27b53（198,396 行/668 日/297 名）；meta run_meta_20261014_122813.json
## 计数（只看计数）
池 mid_large PIT top300（锚 2024-06-28，流通市值口径），排除后 298 只。全窗 19,041 条/298 只；X2 相关 8,716 条/297 只 → 计数闸通过，但事件极密。
## 合规
Σw≡1、无负权、单名 4%、行业 max 28%、600519/002371 恒 0。每日满 20 名，压舱恒 20%；单边日均换手 31.6%（极高）。
## 自检（复权，毛、无成本，非 Book-Smoke）
- 毛 CAGR 13.80% / MDD −15.17%（510300 12.34%/−16.25%；capacity_adv 17.66%/−13.18%）；β 1.00
- 残差 α +1.64%/年；分年 2024 +14.05%｜2025 **−5.79%**｜2026 **−5.70%**
- 去 β ρ：report_rc_allup 0.095｜earnings_event 0.268｜capacity_adv 0.043｜insider 0.330｜equity_incentive 0.466｜unlock 0.214｜interim_div 0.174｜block_trade 0.209
- 逐日 Jaccard max 0.216（vs capacity_adv）；vs report_rc_allup 0.130、earnings_event 0.136 → 无硬拒
- 入场落在 report_rc_allup 持仓窗内 2.6%（222/8,694），earnings_event 3.1%（270/8,694）（以 T2 当日是否被该包持有为代理）
- G6 pass；peak RSS 1,241 MB
## 组合层闸（预注册写死：cap80+叶20，两档 CAGR 与 MDD 均优）
| 档 | cap 单独 | cap80+叶20 | cap70+叶30 |
|---|---|---|---|
| 60万 | 14.96%/−13.63% | 12.74%/−15.63% | 11.61%/−16.85% |
| 100万 | 18.85%/−12.25% | 19.62%/−12.70% | 19.47%/−13.29% |
→ **不过**（60万 收益和回撤都差；100万 回撤差）。
## 判定
失败条件 4（组合层）与 5（2025、2026 两年残差 α 为负）触发 → **WATCH，不送 ACCEPT**。α 集中在 2024 且衰减；事件过密使持仓近似池内高换手轮动。
