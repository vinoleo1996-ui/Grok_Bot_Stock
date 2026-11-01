# Book-Smoke：叶11 report_rc_allup 按 GATE_V3_MDD25 终判（研究级）2026-10-14

live=false；promotion=false；禁 GP；单进程串行（每次峰值 RSS 约 0.69–0.71GB）；仅跑一次。授权：Alpha 转达 Leo 06:02 ET 确认。
预注册：docs/v2/GATE_V3_MDD25_PREREG_ZH.md（FROZEN 06:01:04 ET，sha256 44093b67…）。单名上限按预注册原文为 **≤6%**（Alpha 写的“06%”是笔误）。

## 构造（严格按预注册：cap80 + 叶20，topN 规则不变）
- 叶：output/ai_factory/g1g5_report_rc_allup_daily_weights_20261014_122118.parquet；主干：g1g5_capacity_adv_daily_weights_20261013_111219.parquet（即 X2 主干冻结文件）。
- topN 规则沿用 conc_v2 的冻结实现（research/b4_paper_extend.py `build()`：各腿股票取 topN 后按腿预算归一，ETF 直通，合并后单名 >6% 的溢出转入 510300）。把 MIX 设为 {capacity_adv:1} 时，产出与 conc_v2 CORE_60w/100w **逐行一致**（max|Δw|=0，668 个交易日），证明规则相同。
- 产出：output/gatev3/gatev3_cap80_rc20_topN_{60w,100w}.parquet。股票最大单名 6.00%，每日权重和为 1；510300 压舱均值 60万 57.9% / 100万 34.6%。
- 运行：quantlab.cli book-smoke --run-nav，X2，core=0/stock=1/alpha_event=0，BOOK,C0，整手，ExecConfig.strategy_v1 成本；60w 文件只跑 60万，100w 文件只跑 100万。
- 对照：预注册把 topN 规则作用于叠加口径，Alpha 自检中的 capacity_adv 也是 topN 版，所以同口径对照为 conc_v2 CORE（已有 X2 运行，规则已证明一致，不重跑）。标准（非集中）主干并列报出。

## 结果（X2 2024-06-03→2026-10-09）
| 档 | 组合 | CAGR | MDD | Calmar | 填单率 | 月胜率 | 成本/初始 |
|---|---|---|---|---|---|---|---|
| 60万 | cap80+叶20 topN | 13.54% | -13.02% | 1.04 | 95.2% | 58.6%（17/29）| 1.67% |
| 60万 | capacity_adv topN（CORE，同口径）| 13.69% | -12.57% | 1.09 | 96.1% | 58.6% | 1.31% |
| 60万 | capacity_adv 标准主干 | 13.82% | -10.07% | 1.37 | 97.0% | 51.7% | 1.72% |
| 100万 | cap80+叶20 topN | 14.73% | -11.90% | 1.24 | 92.1% | 51.7%（15/29）| 1.98% |
| 100万 | capacity_adv topN（CORE，同口径）| 13.83% | -11.66% | 1.19 | 96.4% | 48.3% | 1.67% |
| 100万 | capacity_adv 标准主干 | 12.23% | -11.62% | 1.05 | 96.9% | 58.6% | 1.71% |

## GATE_V3 逐条判定
1. 两档 MDD ≤25%：✓（-13.02% / -11.90%）。≤15% 变体（仅参考）：✓。
2. 两档 CAGR 都高于 capacity_adv 单独：**✗**。60万 13.54% < 同口径 13.69%（-0.15pt），也低于标准主干 13.82%；100万 ✓（+0.90pt 同口径，+2.50pt 对标准主干）。
3. alpha_decay_gate=KEEP：沿用 Alpha 自检结果（本侧未复算）。
4. 可交易：沿用 Alpha 自检结果（双边日换手 2.1%）。Book-Smoke 中 60万成本 1.67% 高于 CORE 的 1.31%。

**终判：GATE_V3 FAIL**（第 2 条在 60万档不过）。和 Alpha 复核里点出的风险一致：60万档余量只有约 +0.4pt，整手和 10% 参与率稀释了 20% 卫星，60万档实测翻转。预注册的事后发现声明仍然适用。

## 自检（14.06%/13.33% 净值）和 Book-Smoke 差在哪
自检用复权 close-to-close、无整手，成本按固定 17.5bp×换手；Book-Smoke 用 T+1 开盘成交、整手、10% 参与率和涨跌停约束，并持有闲置现金（约 5.4%）。60万档组合填单率 95.2%，卫星小单最容易被整手吃掉。
