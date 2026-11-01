# 叶19 cfacc_rnoa（现金流应计 + RNOA 改善）回执 —— WATCH
- 时间：2026-10-17 23:58 ET（恢复跑；10-15 停摆中断的是下游，α/闸/评价权重 10-14 21:31 ET 已按冻结预注册建好，本次**复用不重建**、不改参数）
- 预注册：docs/v2/AI_G1G5_CFACC_RNOA_WHO_PAYS_PREREG_ZH.md（FROZEN 2026-10-14 09:13:03 ET，sha256 0528549e…，与 output/ai_factory/prereg_sha_leaf19_20_18v.txt 一致，未改）
- 产物：output/ai_factory/leaf19_cfacc_rnoa/（alpha_{HILIQ,FULLA}_20261014_213132.parquet = 日度 base-α 向量主交付；gate_*；eval_weights_*；eval_resume_20261017_235604.json；poolew_excess.json）
- 脚本：research/g1g5_fund_resid_alpha.py（建 α，10-14）；research/g1g5_leaf19_20_18v_eval.py（下游，新）；research/g1g5_poolew_excess.py（披露，新）
- live=false；promotion_approved=false；未自封 research_candidate；未跑 Book-Smoke；未起 8787；禁 GP

## 结论：WATCH（主宇宙 HI_LIQ 不过；不交 Alpha 验收，FULLA 诊断抄送 Alpha 参考）
HI_LIQ（纸面路径，主判）：衰减门 v1.1 DECAY_DOWNGRADE（最新滚动残差 α −14.6%，净 CAGR ≤510300）；成本拖累>毛超额一半 → 不可交易；GATE_V3 FAIL（100万 未赢 capacity_adv）；预注册 Gate B FAIL。残差 α ≈0。

## 数字（复权、T+1 开盘、17.5bp/单位换手；年化 244 主 / 252 对照）
| 宇宙·窗 | 档 | CAGR244 / 252 | MDD | 残差α(对510300) | 单边换手/日 |
|---|---|---|---|---|---|
| HI_LIQ 密封 | 60万 | −1.41% / −1.46% | −62.6% | +1.0% | 2.7% |
| HI_LIQ 密封 | 100万 | 4.55% / 4.70% | −44.8% | +6.7% | 2.5% |
| HI_LIQ X2 | 60万 | 14.96% / 15.49% | −30.4% | +4.5% | 2.4% |
| HI_LIQ X2 | 100万 | 7.75% / 8.01% | −33.3% | −2.4% | 2.3% |
| FULLA 密封 | 60万 | 8.41% / 8.70% | −37.2% | +11.0% | 2.3% |
| FULLA 密封 | 100万 | 8.86% / 9.17% | −37.1% | +10.9% | 2.1% |
| FULLA X2 | 60万 | 32.63% / 33.86% | −30.2% | +20.3% | 1.9% |
| FULLA X2 | 100万 | 34.80% / 36.13% | −25.8% | +21.5% | 1.7% |
（评价权重 Top20 等权 4%，60万=前6、100万=前10，α 序；年度残差 α 见 eval_resume json）

自检（LC 引擎，X2 20 名书）：HI_LIQ 净 10.89%/MDD −29.1%/残差α +0.1%（2024 +15.1/2025 +0.5/2026 −12.2）；FULLA 净 29.49%/MDD −29.5%/残差α +16.6%（2024 +26.6/2025 +24.4/2026 −1.5）。
- ρ(去β) vs capacity_adv(旧) −0.35 / vs capacity_adv_hiliq +0.44（<0.5）；vs insurer_surv_hiliq 0.68、equity_incentive_hiliq 0.58、insider_increase_hiliq 0.54（>0.5，按规则若与这些腿同用只能作过滤）；Jaccard max 0.08（无硬拒）。
- 衰减门：v1 与 v1.1 同为 HI_LIQ DOWNGRADE / FULLA KEEP。
- 组合（cap80+叶20，旧 capacity_adv 书）：HI_LIQ 60万 12.60%→13.90%，100万 13.79%→13.68%（输）；FULLA 60万 12.60%→16.96%、100万 13.79%→18.52%，MDD 均变浅。LC Gate A/B：HI_LIQ current✓ A✗ B✓；FULLA 三项✓。
- HI_LIQ capacity_adv 腿作基（披露）：该腿 X2 自身仅 1.26%/MDD −36.6%，cap80+叶20 两档均"赢"，但基太弱不作依据。
- IC（新池 leaf_selfcheck_v3，HAC t 仅披露）：HI_LIQ 20d IC 0.0001（t 0.02 / HAC 0.03），60d 0.0058（0.82/1.72）；FULLA 20d 0.0079（1.89/2.42），60d 0.0126（1.87/2.75）。

## 关键诚实披露（给 Alpha）
1. **FULLA X2 强主要是小微盘 β**：对 FULLA 池内等权基准，X2 超额仅 +5.3%/年（t 0.89，2026 −8.5%）；密封窗 +9.3%（t 2.43）。HI_LIQ 对池内等权：密封 +12.0%（t 2.99，七年六正），X2 −0.5%（t −0.08）。→ 机制在密封窗有效、X2 明显衰减。FULLA 的 GATE_V3/衰减门 PASS 是以 510300 为基准，不能当作通过。裸 FULLA 本来也不进纸面。
2. 预注册第 5 条「库内 BS 应计」未接入（缺），中性化实际 = SW L1 + log 流通市值 + mom20/60 + vol20 + logADV20（capacity_adv 代理）；分域 P70/P90 标定后再做行业+市值残差。
3. 10-14 建 α 时峰值 RSS 2.79GB，**超 1.5GB 红线**（已发生，本次未重跑；下游评估峰值 1.09GB）。
4. 建 α 脚本 summary 里的「cap/cap80_leaf20」列有误（capacity_adv_hiliq 腿按字母序取前 N 名），作废；以本回执 LC 引擎数为准。
5. HAC t 与原 t 并列，仅披露，阈值未动。
