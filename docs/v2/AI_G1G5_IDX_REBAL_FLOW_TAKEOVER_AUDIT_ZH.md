# idx_rebal_flow 接管审计（第七包 Book-Smoke 灭）

| 项 | 值 |
|---|---|
| 日期 | 2026-10-12 ~22:45 ET |
| 作者 | QuantLab AI（search-loop 43 · 接管审计） |
| promotion_approved | **false** |
| 本单动作 | **只审计、不产权重、不开 GP、不交 Strategy** |
| 代跑声明 | 权重 `…215737` 与 Book-Smoke 均为 New Bot 侧代跑；**≠** 本侧已开工 |

---

## 1. 核验数字（本机读 `book_smoke_summary.json`）

| 资本 | X2/BOOK CAGR | MDD | vs C0（≈11.27%） | cost/AUM |
|---:|---:|---:|---:|---:|
| 60万 | **9.97%** | **−18.43%** | ≈−1.29pp | ≈0.79% |
| 100万 | **10.04%** | **−19.07%** | ≈−1.23pp | ≈0.87% |

- `any_pass=false`（门锁 CAGR∈[12%,18%] · MDD≥−28% 未过）
- 权重：`output/ai_factory/g1g5_idx_rebal_flow_daily_weights_20261012_215737.parquet`（3243/668/121；mechanism=`g1g5_ashare_idx_rebal_flow_v1`）
- 回执：`docs/v2/BOOK_SMOKE_G1G5_IDX_REBAL_FLOW_X2_RECEIPT_ZH.md`
- WATCH 已记七包（`output/v3/handoff_strategy/WATCH_ZH.md` @22:42）

## 2. 七败 WATCH（勿再同构）

expand / lowturn / nontextbook / resid_etf / etf_core_sleeve / friction_cost_redesign / **idx_rebal_flow**

## 3. 交接指纹

`AI_FACTORY_HANDOFF_TO_QUANTLAB_AI_ZH.md` 仍停 **02:03 ET**（attachments 零活动）。GP **不开**。

## 4. 下一步（须 Leo 点卡）

下一叶先 who_pays 预注册 → 完整 X2（个股+ETF，禁 CB/金主）→ Book-Smoke；须正交七败；peak≤1.0–1.5GB；产物 `output/ai_factory/`。暴露短报建议：行业硬顶 + 动量暴露中性。
