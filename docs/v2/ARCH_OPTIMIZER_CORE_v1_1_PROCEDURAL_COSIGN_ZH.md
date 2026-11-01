# OPTIMIZER Core FROZEN_v1.1 程序性复签（Arch，2026-10-14 08:45 ET）
结论：PROCEDURAL_COSIGN_PASS（有条件）。策略/λ/池/基准/窗口均未改动，只修实现缺陷；v0 已归档，未评分（_archive_v0/NOTE.md）。
已核：条款①Σw=1、整手后现金≤2%、LOT_CASH_GT2 披露；②INFEASIBLE 沿用上期、禁回退 step1；③确定性 top-k 重解（|w0| 降序、代码兜底），下限 2% 沿用 §3.5(b)。smoke：3 日×2 档全部 OK，K=21–24，现金 1.49–2.00%。
条件（重跑必须做到，否则 A 列不得出业绩）：
C1 整手补手后逐日复核 Size/MidCap/β/行业，超出 ±0.35σ+已用 slack、β±0.10 的标 LOT_STYLE_DRIFT 并逐日披露；超限天数占比与 INFEASIBLE 一起写进文档。
C2 slack 逐日披露：smoke 中 5/6 次贴着上限用 slack（0.05σ/1pp），说明 Size 约束在 K≥20 时经常绑定。如果全量中贴上限的天数超过 50%，要单列说明，不得据此放宽。
C3 K 与 tries 逐日落盘；K0 在 smoke 中恒为 20（初解里≥2% 的名字少于 20），属预期，但要统计分布。
C4 INFEASIBLE 逐日清单与现金分布在算业绩前补进文档（Strategy 已承诺）。

## 附注（08:43 ET，主 Agent 裁定 P1-T2 选 a）
- Core Stage1：X2 三列并排披露只作入场门槛；2026-11-02 起的前向窗是唯一晋级判定窗。C 列不补跑密封窗。
- 新增条件 C5：Eng 用 v1.1 逻辑重报 INFEASIBLE 可行率，须在 A 列出业绩前完成。
- 新增条件 C6：P1-T1 路径统一（smoke_* 对 book_smoke_*）须先修好。
