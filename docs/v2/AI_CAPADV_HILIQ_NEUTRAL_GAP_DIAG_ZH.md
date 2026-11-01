# capacity_adv HI_LIQ 25 名全袖：中性化净超额 −48.7% 对 +8.2% 的差距诊断（AI）
- 写于 2026-10-18 01:03 ET。只读，只用 X2（动量/β 预热用到 2023-06 起的过去收益）；live=false。脚本 `research/ai_capadv_neutral_gap_diag.py`，挂 1.5GB 守护，峰值 1.30GB。结果：`output/ai_factory/capadv_neutral_gap_diag.json`；equity_incentive 复核：`neutral_gap_diag_g1g5_equity_incentive_hiliq_v1_A0,A1,B0.json`。
- 统计口径与 Alpha `alpha_s8_errata_fullsleeve_b.nstat` 相同：W.shift(2) × ε，ε 缺失按 0，成本 17.5bp × 换手，从 iloc[3:] 起算，年化 244。

## 根因：AI 风格集里的 logmv 用的是**当日**流通市值
- cs_panel 的 `logmv` 是当日收盘的流通市值（daily_basic，含当日涨跌），AI 的 ε 却拿它去回归**同一天**的 ret（`ai_hiliq_sec8_supplement.neutral_eps` 及其所有复刻）。
- logmv 的日变化与当日收益的截面相关是 **0.93**。于是「市值」回归项把持仓股当天的涨跌机械地吸收掉了。
- capacity_adv 的持仓偏大市值、高流动性：持仓暴露 logmv +2.2σ、logADV +3.2σ。这个回归项因此每天从持仓 ε 里扣掉一块。

| 变体（只改一项，逐步叠加） | 净超额/年 | t | 市值项贡献 |
|---|---|---|---|
| A0：AI 原样（当日 logmv，截尾，当日池） | **−48.67%** | −5.62 | **+44.2%** |
| A1：logmv 改用前一日 | **−1.35%** | −0.16 | −3.1% |
| A2：A1 + 不截尾 | −1.35% | −0.16 | — |
| A3：A2 + 改用前一日的池 | −0.60% | −0.07 | — |
| B0：Alpha 冻结风格，用 cs_panel 重建（前一日 logmv + β120 + mom(120→20) + logADV20） | +9.21% | 1.20 | — |
| B1：B0 + mom20 + vol20 | +8.75% | 1.18 | — |
| B2：B0，但 logmv 改成当日 | −2.91% | −0.38 | 市值项 +960%，与 liq 项严重共线 |
- A0 精确复现了 Alpha 报的 −48.7%。A0 与 B0 的 ε 逐日截面相关为 0.977，与 Alpha 报的 0.976 一致。
- **当日 logmv 一项就解释了 57.9pp 总差距中的 47.3pp。** 剩下约 10pp（A1 的 −1.4% 对 B0 的 +9.2%）是两套风格集真实不同造成的。主要在于 Alpha 的风格集含 logADV20 和 β120，而 capacity_adv 本身就是高 ADV 暴露；mom20/vol20 加进去几乎没有影响（B1 与 B0 只差 0.5pp）。

## 其他嫌疑逐项排除
- **ret 时点**：cs_panel 的 ret 是当日 close/pre_close，与 Alpha 的 C.pct_change 同一天对齐；持仓滞后两边都是 W.shift(2)。A3 把池也换成前一日，结果只变 0.7pp。
- **截尾**：HI_LIQ 池内 X2 没有 |ret|>21% 的观测（涨跌停 ±20%），持仓在截尾日的权重为 0。截尾 [−21%, +31%] 的影响为 0。
- **残差复利**：两边都是 ε 的算术日和 ×244，没有复利。
- **缺失日补 0**：持仓 25 名里每天平均 0.11 名 ε 缺失（停牌），约 0.4% 权重，可以忽略。
- **持仓名缺失**：cap 腿有正权重的代码全部在 cs_panel 里。

## 修正后的数字
- capacity_adv HI_LIQ 全袖，AI 风格集修正后（前一日 logmv）：**−1.35%/年（t −0.16）**；连池也改用前一日：−0.60%。Alpha 冻结风格的重建值 +9.2%，与 Alpha 报的 +8.2% 相差约 1pp，来自市值/ADV 数据源和行业表的细节差异。
- **顺带：equity_incentive 全袖**：AI 风格原样 −8.93%（与 Alpha 报的 −8.9% 一致）→ 修正后 **+8.80%（t 1.56）**；Alpha 风格重建 +9.27%。**两套风格集修正后符号一致，原来的「符号随风格集翻转」是这个 bug 造成的，不是风格集差异。**

## 影响与处理
- 以下数字作废，已在原文档追加勘误，不重写正文：
  - `AI_EQINC_SEC8_RECONCILE_ZH.md` 里「中性化净超额符号纯由风格集决定」及 AI 风格下的负值（−4%~−7%）；
  - `AI_HILIQ_V1_SEC8_SUPPLEMENT_ZH.md` 里 AI 风格的 neutral_net。
  - 建议 Alpha 复核勘误第 3 条（两套风格集符号相反记 PASS*）在 equity_incentive 上的适用性：修正后两套同号。这只是建议，裁定归 Alpha。
- 叶构建里的快门（行业 + 当日 logmv 残差收益的左尾）同样用了当日 logmv。快门在 t 日收盘计算、T+1 才使用，不构成前视；但残差定义不纯，影响限于快门选名。按冻结预注册，已完成的叶不改；新叶如需修正，在预注册里写明。
- 主观判断：这不是数据错误，而是 AI 自己 ε 实现里的口径错误，责任在 AI。
