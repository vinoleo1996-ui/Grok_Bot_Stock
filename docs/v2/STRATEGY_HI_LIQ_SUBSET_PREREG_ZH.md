# 高流动性子集预注册 v1（HI_LIQ_V1，Strategy）— FROZEN

- 冻结时间：2026-10-14 07:44 ET（在看到任何 HI_LIQ 回测 / book-smoke 结果之前冻结）
- 依据：Leo 07:42 ET 双轨（经主 Agent）——**FULLA_V1 = 研究轨**（可报密封窗+X2，不进纸面）；**纸面轨 = 高流动性子集**（仍从全 A 可选，但 ADV / 参与率 / 名称数更严）。
- **披露（动机 ≠ 调参）**：FULLA capacity_adv 引擎 X2 两档 MDD 破 25%（见 `docs/v2/STRATEGY_FULLA_X2_ZH.md`）是开通双轨的动机；本子集阈值按容量公式**预先承诺**，不依据 FULLA 回撤数字做网格或事后改阈值。
- 冻结脚本：`research/strategy_hiliq_universe_v1.py`，sha256 `ed9c9aecf277fec7865d74c7f8209375ab53cfde1adce6102aa7bc6eead0dc96`。
- 掩码：`output/strategy_hiliq/universe_mask_hiliq_v1.parquet`（列与 FULLA_V1 相同：date, instrument, in_universe, st, suspended, young, adv_fail, adv20_yuan）。
- live=false；strategy_promotion=false。**不改**既有纸面轨 FROZEN_CONFIG（仍 top300），直至 Leo 明确晋级 HI_LIQ。裸 FULLA 腿不进纸面。

## 定义（PIT，对交易日 S，available_at = S 09:00 +08）— 唯一参数组

1. **基础池** = FULLA_V1 可交易过滤后的全 A：沪深 A（不含北交所）；S 前 20 个开市日至少 1 根 K；剔 ST/*ST；剔停牌（suspend_d 当日 S 或 S-1 无成交）；剔上市不满 60 个开市日。不设市值下限（Leo 07:24：小盘可买，贡献仅披露）。
2. **ADV 下限（纸面）**：ADV20 = S-20…S-1 成交额均值（缺失/停牌按 0，单位元）。
   - 填单可行下界：`6% × 100万 / 0.6% = 1,000 万`（相对 FULLA 的 `6%×100万/2%=300万` 更严参与率）。
   - **本预注册取 ADV20 ≥ 1.0 亿** = 填单下界 × **10 倍冲击缓冲**，使满仓单票对 ADV 的占用 ≤ 0.06%，贴近机构纸面冲击预算。一句理由：10M 仅保证「下得去」，纸面还要「冲击可控」；×10 来自参与率从 0.6% 再收一档到 0.06%，**不是**按 FULLA 失败 MDD 反推。
3. **名称数 / 权重（下游冻结，非宇宙列）**：
   - capacity_adv：股票袖最多 **25** 只 + 510300 固定 **20%**；单票 ≤ **4%**；袖内 `ADV_PARTICIPATION_K = 0.006`（与宇宙公式一致，替换研究轨 0.02）。
   - B4：合成方式不变（50/25/25）；60万 N=6、100万 N=10；组合单票 ≤ **6%**。
4. 只用 S 之前的数据；盘前停牌公告是唯一例外。

## 下游（冻结口径）

- 腿输出目录：`output/strategy_hiliq/legs/`（与 `output/strategy_fulla/` 隔离）。
- 重生成：capacity_adv（Alpha）、earnings_event / insider_increase / equity_incentive 及可交易叶（AI）；逻辑不变，只换 HI_LIQ 掩码 + 上述参与率。
- 引擎：Eng book-smoke，strategy_v1 成本，按手取整，sleeves core=0/stock=1，244 日年化。
- **窗口（均须标注，不宣称晋级）**：
  - 密封窗：2018-01-02→2024-05-31（Mandate 开发/验证段；**样本内/密封，非晋级**）。
  - X2：2024-06-03→2026-10-09（**样本内**）。
- 报告：60万/100万 CAGR、MDD、Calmar、日胜率；与 top300 纸面基线并列；小盘（市值后 30%）贡献与申万一级分布仅披露。

## 试验计数

- 此前累计 **33**（含 FULLA 宇宙变更 +4）。
- 本次 HI_LIQ 预注册重跑：**capacity_adv、B4** 两臂（密封窗与 X2 为同一臂的两段报告，不另计试验）→ 新增 **+2**，累计 **35**。
- 宇宙 + 袖内参与率只有这一组，不做网格。

## 明确不做

- 不把 FULLA 裸腿挂进纸面。
- 不改现有 capacity_adv / B4 / S6 的 FROZEN_CONFIG，直至 Leo 晋级 HI_LIQ。
- 不翻转 live / strategy_promotion。

## 掩码落盘（建设完成；非策略回测结果）

- 路径：`output/strategy_hiliq/universe_mask_hiliq_v1.parquet`
- 掩码 sha256：`c5433e80a74ac3acc0cd5a52d57fdd0bda5ed578fb86fb98cbd652ccb9f1b9af`
- 覆盖：2017-12-01→2026-10-14（2149 日）；密封窗与 X2 均覆盖。
- 在池：全日均值 1996；X2（2024-06-03→2026-10-09）均值约 3007（min 1343 / max 3982）；密封窗均值约 1651。
- 2018-01-02/03 ADV 热身导致在池极薄（0/22）——密封窗报告标注首周数据质量或自有效日起计。
- 抽检 2025-06-03：HI_LIQ 2845 ⊂ FULLA 4916，无越界。
- meta：`output/strategy_hiliq/universe_mask_hiliq_v1.parquet.meta.json`

## 修订 v1.1（2026-10-14 07:48 ET，仍在任何 HI_LIQ 回测结果之前）

依据 Leo 07:48 ET 关切（经主 Agent）。本修订**不改**掩码 ADV 阈值与脚本 sha（掩码本就不含市值筛）；新增组合层约束与报告口径。

1. **筛选维度**：只按 ADV、参与率、可交易性（ST/停牌/上市日）筛。**禁止任何市值筛**（含 topN 市值、mid_large、后 30% 剔除）。小盘可买；小盘贡献仅披露。
2. **申万一级行业上限（组合层，冻结）**：股票袖内任一申万一级行业权重 **≤ 25%**。超配按比例压缩，权重顺延给其他行业排名靠前且未触顶的名字；现金/510300 不计入行业分母。capadv 与 B4 均适用。
3. **报告必报**：申万一级完整分布；**单列** 电子、计算机、通信、医药生物 权重；60万与 100万、密封窗与 X2 四格全报。
4. **ADV 门槛裁定（全队统一）**：
   - 研究轨 FULLA 正式下限 = **ADV20 ≥ 300 万**（`6%×100万/2%`，与 B4 单名≤6% 一致）。
   - `all_a ≥ 200 万`（4% 单名口径）**废弃为非正式**，不作对照主报。
   - 纸面 HI_LIQ = **ADV20 ≥ 1.0 亿**（本预注册，不变）。

累计试验数仍为 **35**（本修订未增臂）。


> **v1.1 修订（开腿前）**：见 [`STRATEGY_HI_LIQ_SUBSET_PREREG_V1_1_ZH.md`](STRATEGY_HI_LIQ_SUBSET_PREREG_V1_1_ZH.md)。冲突条款以 v1.1 为准。
