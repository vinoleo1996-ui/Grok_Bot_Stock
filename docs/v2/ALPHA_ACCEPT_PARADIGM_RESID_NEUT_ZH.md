# 验收范式预注册：残差 α + 中性化有效性 + 特质α / 快慢因子错配（Alpha）— FROZEN

- **冻结时间**：2026-10-14 07:58:51 ET（America/New_York；在看到任何据此范式重算的新闸门数字之前；含 Leo 07:56–07:58 增补）
- **文件 sha256**：`c134183c4433b2e5e2c5a5b8feda4c7fe212ac6956354ef69c258ed600d08013`
- **依据**：Leo 07:56 ET 范式 + 07:58 ET 增补（经主 Agent）——闸门证据须为域内残差/特质 α 与中性化后有效性；须检查快慢因子错配；**拒绝**仅 Top-N 等权回测作闸门证据。
- 适用范围：HI_LIQ_V1.1 纸面候选轨、FULLA_V1 研究轨、叶验收 v2、GATE_V3 本地估计。不改既有 FROZEN_CONFIG；promotion_approved=false；live=false；handoff=NO；禁 GP。
- 配套清单：`docs/v2/ALPHA_HILIQ_GATEV3_ACCEPT_CHECKLIST_ZH.md` §8。

## 1. 可用作闸门证据（须齐备）

| # | 证据 | 最低读法 |
|---|---|---|
| A | **域内 / 宇宙内残差 α 质量** | 目标宇宙（HI_LIQ 或 FULLA）内，对申万一级 + 风格（至少 log 流通市值、滚动 β）残差化后的 IC、双读 ICIR、衰减门 v1.1 |
| A′ | **特质 α（idiosyncratic α）** | 在 A 的残差正交化之后，残余信号对下一期收益的预测力（残差 IC / 残差多空净）；不得把行业或风格 β 当作 α |
| B | **行业+风格中性化后相对基准的有效性** | 中性化后相对约定基准（默认 510300 或同宇宙 capacity_adv 单跑）的净超额；组合层：净收益、T+1、244 日、60万∧100万 |
| C | **快慢因子错配 / 伪耦合检查** | 叶与主书（或叶与叶）不得仅靠「简单加权求和」过门。须披露：与主书残差相关 ρ、换手半衰期/调仓频率（快 vs 慢）、叠加后相对「各腿独立贡献之和」的增量是否来自同向暴露而非正交增量。若叠加收益 ≈ 加权之和且 ρ 高、频率同档 → 判 **伪耦合 / 未增益**，CMC 不得 PASS |

- 研究级单叶 ACCEPT：至少 A + A′。
- 进 GATE_V3 / 派 Eng / 纸面候选：A + A′ + B + C 全过，且叶验收 v2 与 GATE_V3 四条仍过。

## 2. 明确拒绝作为闸门证据

- **仅 Top-N 等权回测**（按信号排序 Top-N、等权、无残差、无行业/风格中性化、不报对基准超额）。
- **仅叶子简单加权求和**冒充组合边际（无残差正交、无快慢错配检查）。
- 上述可作附录 / `diag_*` 披露；**不得**单独支撑 RESEARCH_ACCEPT、派烟、GATE_V3 通过或纸面晋级提议。
- 历史包若只有等权 Top-N：须补 A/A′/B/C 后重判；未补前维持 WATCH 或不升级。

## 3. 仍强制（不因本范式削弱）

- 密封窗（2018-01-02→2024-05-31，非晋级）+ Eng Book-Smoke X2（2024-06-03→2026-10-09，样本内）。
- 资本框 60万 ∧ 100万。
- GATE_V3 四条：MDD≤25%；净 CAGR 严格高于同口径 capacity_adv 单跑；衰减门 v1.1 KEEP；双边换手≤20%/日。
- HI_LIQ：股票袖申万一级 ≤25%；电子 / 计算机 / 通信 / 医药生物 单列；无市值筛；ADV_PARTICIPATION_K=0.006。
- 叶验收 v2：HC → 单叶 → CMC → 衰减 → GATE_V3 本地 → Eng X2；叶不提升主书 → fail-fast，不派烟。

## 4. 与现有脚本的衔接

- 残差 IC/ICIR / 特质 α：`research/alpha_combo_marginal.py`、`research/leaf_selfcheck_common.py`（SW L1 + log 流通市值 + 滚动 β）。
- 衰减门：`research/alpha_decay_gate_v1_1.py`。
- CMC / 伪耦合：CMC 主报 ΔCAGR 与残差 ρ；附录须含快慢标签（调仓周期）与「叠加 vs 加权和」对比；ρ 高且无正交增量 → CMC_FAIL。
- 组合对照：同宇宙、同引擎 capacity_adv 单跑（HI_LIQ 对 HI_LIQ；勿混 top300 旧基线）。
- Top-N 等权：降级为 `diag_equal_weight_topn`，不进入 `gate_v3` / `cmc_verdict` / `hc_verdict` 判定键。

## 5. 明确不做

- 不改 FROZEN_CONFIG；不翻转 live / promotion。
- 不把等权 Top-N 或叶子简单加权的好看数字回写成 ACCEPT。
- 不做 GP；不网格本范式阈值。

## 6. 修订

变更本文件须重算 sha、更新冻结时间；闸门级变更须 Leo 原话（主 Agent 转述≠授权）。
