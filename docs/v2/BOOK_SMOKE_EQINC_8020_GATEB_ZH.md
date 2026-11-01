# capacity_adv/equity_incentive 80/20 Book-Smoke 与门B 判定（2026-10-14 ET，研究级，live=false）

## 是否同一构造 → 是（复用现有结果，未重跑）
- 主干：Alpha 用 capacity_adv paper r2（≤10-09 与冻结文件 111219 逐行相同，已过 weight gate）；Eng 用 111219。X2 段相同。
- 卫星：两边都是 g1g5_equity_incentive_daily_weights_20261014_023222.parquet（预注册未写别的文件；135031 扩展的历史与之逐行一致）。
- 混合：Alpha 为 80/20 目标权重、每日再平衡；Eng（scripts_eng/blend_equity_incentive.py）为 0.8×主干 + 0.2×卫星，在 session×instrument 上按日归一化。权重层面等价。单名上限：Eng 混合不另加封顶（两条腿各自已封顶），Alpha 也没有。
- 现有运行：output/v3/book_smoke_g1g5_combo_capadv_eqincent_80_20_x2（X2，整手，strategy_v1，BOOK/C0）。内存：无其它大任务（最大进程是 node 1.0GB），不需要重跑。

## 并列（X2，Book-Smoke）
| 轨道 | AUM | CAGR | MDD | Calmar | 月胜率 |
|---|---|---|---|---|---|
| capacity_adv | 60万 | 13.82% | −10.07% | 1.37 | 52% |
| capacity_adv | 100万 | 12.23% | −11.62% | 1.05 | 59% |
| B4 | 60万 | 15.11% | −13.85% | 1.09 | 62% |
| B4 | 100万 | 14.24% | −13.17% | 1.08 | 55% |
| S6（影子，样本内） | 60万 | 17.15% | −11.95% | 1.43 | 62% |
| S6（影子，样本内） | 100万 | 16.37% | −12.66% | 1.29 | 59% |
| capadv+eqincent 80/20 | 60万 | 11.40% | −9.94% | 1.15 | 55% |
| capadv+eqincent 80/20 | 100万 | 12.67% | −11.41% | 1.11 | 55% |

## 门B（字面：两档 Calmar 都胜 capacity_adv，且 MDD 不深于 −15%）→ **不过**
- 60万：1.15 < 1.37 ✗；100万：1.11 > 1.05 ✓；MDD −9.94% / −11.41% 都在 15% 以内 ✓。两档要求只满足一档 → FAIL。

## 为什么 Alpha 本地 1.232/1.208 与 Book-Smoke 不同
1. 窗口：Alpha 2024-01-03→10-09（667 日），包含 2024 年 1-2 月的大跌；Book-Smoke X2 从 2024-06-03 开始。主干本身就不同：Alpha 16.37%/−13.55%，Book-Smoke 13.82%/−10.07%（60万）。
2. 执行：Alpha 用收盘价对收盘价、无整手、无涨跌停/成交量上限、不分档（60万=100万）；Book-Smoke 是 T+1 开盘成交、整手、10% 参与率上限、涨跌停、分档。小资金下卫星 20%（12万/20万）的名字按整手后被买少、被跳过，收益被稀释（60万尤其明显）。
3. 成本：Alpha 固定单边 15bp + 卖出印花 5bp；Book-Smoke 用 strategy_v1（最低佣金 5 元、sqrt 冲击、按 tick 取整），小单受最低佣金影响更大。
4. 价格口径：本次 Alpha 预注册写明用 hfq 复权（research/adj_price.py），**不是**之前审计发现的未复权 close 问题。Book-Smoke 用原始 OHLC + 显式公司行动（总收益口径），两者都是总收益，口径差异很小，不是主因。
5. 门B 余量本来就很薄（1.232 vs 1.208，差 0.024），上面任何一项都足以翻转结论。

## 记分卡
output/loop/scorecard_latest.md 中该行已标注 "[Alpha gateB cand: FAIL]"。
