# 叶验收 v2 预注册：组合边际贡献 + 假设批判（ALPHA_LEAF_ACCEPT_V2）

- 来源：ARCH_GITHUB_LANDSCAPE_20261014_ZH.md 第2项（alphagen 组合 IC 思路）+ 第7项（RD-Agent hypo_critic 思路）
- 归属：QuantLab Alpha 定义口径与阈值；QuantLab AI 产出数据并接入自检 v2
- 约束：promotion_approved=false，live=false，handoff=NO；禁 GP，禁 LLM 搜索循环；只做中大盘（mid_large_members_pit）
- 本文不改 GATE_V3、Gate B 或衰减闸门 v1，只在叶 ACCEPT 前加两步。要改闸门本身，必须有 Leo 在 Alpha 聊天里的原话。

## 1. 组合边际贡献（Combo Marginal Contribution, CMC）
### 1.1 定义
- 基准书 B0：capacity_adv + B4（capacity_adv/earnings_event/insider_increase 50/25/25），按当前纸面权重配置。
- 候选书 B1：B0 + 候选叶。配置沿用 GATE_V3：B0 占 80，叶占 20；top-N 6/10，单票 ≤6%。
- 信号：每个叶先对 B0 各叶信号和行业/市值/β 做截面残差化，再进入组合。组合信号是残差信号按上述权重的等权 z 合成。
- 用到的价格和成本：research/adj_price.py 复权价；成本按 17.5bp/单位换手计。窗口和成交口径与 Eng Book-Smoke X2 一致。

### 1.2 指标（报 B1−B0）
1. ΔIC：组合 RankIC 的差，用日频 20 日前瞻收益计算。
2. ΔICIR：双读（全样本 + 滚动 252 日中位数），沿用 QuantMind P0 的口径。
3. ΔCAGR 和 ΔMDD：60万和100万两档都要算，扣成本后的净值。
4. 叶残差信号与 B0 组合信号的相关 ρ，作为参考。

### 1.3 冻结阈值（两档 AUM 必须同时满足，即 60万∧100万）
| 项 | 阈值 |
|---|---|
| ΔIC | ≥ +0.003 |
| ΔICIR（两种读法都要满足） | ≥ +0.05 |
| ΔCAGR（净） | ≥ +0.50pp，两档都要 |
| ΔMDD | ≤ +1.0pp（回撤恶化不超过 1pp），且 B1 的 MDD ≤25% |
| ρ(叶残差, B0) | ≤ 0.5；超过的直接记为重叠 |
| 年度稳定性 | 按年计算的 ΔCAGR 为负的年份不超过 1 个 |

判定：
- CMC_PASS：全部满足。
- CMC_MARGINAL：IC 类两项满足，但 ΔCAGR 落在 [0, 0.5pp) 区间。结果记为 WATCH，不派烟测。
- CMC_FAIL：其余情况。
- 本地 CMC 只是前置筛选。最终仍以 GATE_V3 和 Eng Book-Smoke X2 为准。
- 参照：叶11 本地复核的 ΔCAGR 在 60万档约 +0.4pp（基准只有 capacity_adv）。按本文口径，它会落在 CMC_MARGINAL。这一条只作说明，不追溯改叶11 的现有状态。

## 2. 假设批判（Hypothesis Critic, HC）
这是结构化清单，由人工或 agent 填写后 Alpha 裁定。只做一轮批判和一次改写，不迭代搜索，不用 GP，不用 LLM 生成或搜索因子。

| # | 检查项 | 要求 | 一票否决 |
|---|---|---|---|
| H1 | 经济机制 | 一句话写清楚因果链，以及收益来自什么风险或行为 | 写不出就否决 |
| H2 | who_pays | 说明谁在付钱（对手方）、能持续的原因、容量来源 | 写不出就否决 |
| H3 | 前视/PIT | 每个字段都给出 available_at 和延迟，复权价、成员表都用 PIT 版本 | 有任何违规就否决 |
| H4 | 与现有叶重叠 | 写出与 capacity_adv、B4 三叶的相关和持仓重合度；ρ>0.5 必须说明 | ρ>0.7 否决 |
| H5 | 事后挑选风险 | 记录尝试次数、参数自由度、是否看过 X2 窗口；尝试多于 3 次时，阈值上浮 50% | 未披露就否决 |
| H6 | 宇宙/交易性 | 只用中大盘；双边换手 ≤20%/日 | 不满足就否决 |
| H7 | 反方论证 | 至少写 2 条“它为什么会失败”，并给出可证伪的预期 | — |

判定：
- HC_PASS：H1–H6 无否决。
- HC_REWRITE：允许改写一次，然后重审。
- HC_REJECT：否决，记档，同一个叶不重开。

## 3. 接入自检 v2（与 QuantLab AI 分工）
- 顺序：HC（预注册阶段，在跑数之前）→ 单叶研究级验收 → CMC → 衰减闸门 v1 → GATE_V3 本地 → Eng Book-Smoke X2。
- Alpha 负责：本文的定义、阈值、判定和最终裁定。
- AI 负责：在叶的权重包里附上 `cmc` 块（ΔIC、ΔICIR 双读、60万/100万两档的 ΔCAGR/ΔMDD、ρ、按年 ΔCAGR）和 `hc` 块（H1–H7 原文），写进 selfcheck_v2 的 JSON。AI 不做判定。
- 缺 `cmc` 或 `hc` 块的包一律记为 INCOMPLETE，不进入裁定。
- 判定结果写入 output/loop/alpha_labels.json，新增字段 cmc_verdict 和 hc_verdict。
- 参考脚本 research/alpha_combo_marginal.py 暂未实现（见 §5）。

## 4. 不做
不改 GATE_V3、Gate B 的阈值；不晋级；不纸面化；不实盘；不跑 GP 或任何符号回归、RL 搜索；不碰小盘。

## 5. 干跑
本次跳过。现有 leaf11 产物只有汇总 JSON，没有叶的残差信号面板，要重建成本较高。实现交给 AI 在自检 v2 里接入，Alpha 按本文口径核验。

## 6. 冻结
- 冻结时间：2026-10-14 18:06:32 ET
- sha256（计算时把本节两行替换为占位符 FREEZE_TS/SHA_PLACEHOLDER 后对全文求哈希）：dffd8eef34aba24fd036e002025c919c86ca53861d77228cc56d583b058a3381
