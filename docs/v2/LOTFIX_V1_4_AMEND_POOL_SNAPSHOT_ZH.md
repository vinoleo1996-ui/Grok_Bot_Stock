# LOTFIX v1.4 落盘附录 AMEND-1：候选池快照（只落盘，不改算法）

- 批准：主 Agent 2026-10-18 01:09 ET
- 母本：v1.4 FROZEN 正文 d921dd3f0f698deb822a59e40aa643f1efc7f43f6c36eaed30c7a672dbdf9425（冻结记录 0d47c52f），正文不改
- 起草：Arch；会签：Beta（必需）；实现：runner 负责方，须在 v1.4 运行前合入

## 1. 新增产出
`core_v1_4_pool_snapshot.parquet`（写入 v1.4 固定输出目录）。
每个调仓日 × 档位（60万/100万）× 袖（两袖都记），**完整候选池每只票一行**，字段：
date, tier, sleeve, code, in_candidate(bool), price, lot_size, lots, u_i(上限), beta, size_z, midcap_m, sw_l1, wb_i, q_cont(连续解权重), q_final(整手后权重), selected(bool), stage(求解阶段标记), K_sel

## 2. 约束
- selected 必须覆盖所有 q_final>0 的票，包括修复阶段新加入、不在支撑集里的票。
- 所有值都取 v1.4 当天实际使用的输入，不重新计算，不读未来数据。
- 只写盘，不改变 v1.4 的任何决策路径。
- 校验：开启和关闭快照写入，v1.4 其余全部产出都要逐位一致（sha 比对）。这一条是 Arch 出 .ok 的前提。
- 内存：快照分日追加写，单进程 RSS ≤1.5GB。

## 3. 核对
Arch 审 v1.4 runner .ok 时一并核对：本附录 sha、快照 schema、覆盖性检查（q_final>0 ⊆ selected）、逐位一致证明。

## r2（2026-10-18 01:17 ET；A3 于 01:18 按 Beta 意见修订为 r2.1）：采纳 Beta 会签 A1–A4（纯文字补充，不改算法）
- A1 池范围：完整 HI_LIQ 池，包括被 S5 剔除的票和 cap_lot=0 的票（in_candidate=false 照样写一行）。每天每档要校验 Σwb_i=1、Σwb_i·beta_i=bb，不通过就 raise。
- A2 基准和标准化参数：bb、zb、mb 以及标准化参数一律取 §7.6 daily_bench，按 (date, tier) 关联。size_z、midcap_m、β 的计算窗口必须和 v1.4 求解用的完全一致。
- A3 现金和 510300：每天每档每种口径各加一行 CASH、一行 510300，code 分别记为 CASH 和 sh.510300，记 q_final 和 beta：CASH 的 beta=0；sh.510300 的 beta 取当天求解和复核实际使用的值，口径②若按基准 β 计就写该值。q_cont 有就写，没有写 NaN。另加一条校验：每天、每档、每种口径，Σq_final（含 CASH 和 510300）=1，且 Σq_final·beta 等于 disclosure 里记录的组合 β（容差 1e-6），不通过就 raise。
- A4 缺失值：β 等暴露缺失时写 NaN，不得写 0。
