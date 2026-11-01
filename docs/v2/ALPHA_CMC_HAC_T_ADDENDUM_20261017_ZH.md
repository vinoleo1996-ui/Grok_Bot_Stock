# 叶验收 v2 / CMC 附录：股票池口径 + IC 显著性并列披露（Alpha）

- 日期：2026-10-17（ET）；依据：Arch P1（docs/v2/ARCH_GITHUB_WATCH_ZH.md，skfolio #409）、Leo 2026-10-14 09:12（经主 Agent）
- 范围：`research/alpha_combo_marginal.py`（Alpha 持有）。`research/leaf_selfcheck_v3.py` 归 QuantLab AI，本附录不改它。
- **阈值不变**：ΔIC ≥ +0.003、ΔICIR ≥ +0.05（双读）、ΔCAGR ≥ +0.5pp、ΔMDD ≤ 1pp、ρ ≤ 0.5。本附录不改任何闸门数值；live=false，promotion_approved=false。

## 1. 股票池
- `--universe hiliq`（**闸门默认**）：`output/strategy_hiliq/universe_mask_hiliq_v1.parquet`；B0 腿换成 HI_LIQ_V1.1 腿（capacity_adv 195620 / earnings_event 202822 / insider_increase 202928）；分档净值用 `output/strategy_hiliq/b4/B4_50_25_25_topN_{60w,100w}.parquet`。
- `--universe fulla`（**仅诊断**）：`output/strategy_fulla/universe_mask_fulla_v1.parquet`；输出带 `universe_role=diagnostic_only`，不进入判定。
- mid_large top300 默认已移除；旧结论按旧池口径保留，不回写。
- 叶参数可直接传 parquet 路径（例如 HI_LIQ 腿）。

## 2. 显著性并列披露（只披露）
对 h 日前瞻收益（h=20）的日频 RankIC 序列 {IC_t}，与 ICIR 并列给出：
- `ic_t_naive` = mean / (sd/√n)。因为窗口重叠，这个值会被高估。
- `ic_t_neff` = mean / (sd/√(n/h))，有效样本 n_eff = n/h。
- `ic_t_hac` = mean / NW_se，Newey-West Bartlett 核，lag = h−1 = 19。
- ΔIC 序列（B1−B0）同样给出这三种 t 值（`d_ic_tstats`）。

## 3. 切换提议（两周后）
- 从 2026-10-17 起并列披露两周（到 2026-10-31 左右）。之后由 Alpha 汇总 naive / neff / HAC 三种读法分歧的叶，并向主 Agent 提议闸门是否加 `ic_t_hac` 读法（例如 |t_hac| ≥ 2 作为附加条件）。
- 闸门级变更须 Leo 原话，主 Agent 转述不算授权；在此之前 HAC t 不作判定键。
