# Arch 审查：SD1 execute D3D4（SD1 收官）
- 时间：2026-10-18T05:34:17-04:00
- 结论：通过。SD1 四步 execute 全部审结，可对 94322 发 SIGCONT。

## 核对项
- 回执 5 件与 Data 报告一致：receipt df68653a、stdout 34a3a861、ps 48f4f8cf、rawdiff 165d5586、normdiff e3b0c442（空）。
- 产物 sha 已重算：stock_delisted_v2.parquet 9d757b96，manifest 156bcf3a，receipt 417d918d。receipt 状态 PASS，ok 为 f03357f1，prev 为 06d06a79（即 D2 回执）。
- 期望键已强制校验：stdout 中 FACE_CHECK 的 expect_from_ok 已填值，四只代码为 000861/002505/002509/600297，unknown 为 56/56，diff 为 0。归一化时屏蔽 expect_from_ok，是因为 dry-run 下该字段为 null，属设计如此，接受。
- P3-12 只读复核：002509.SZ 的 source 为 manual_override，start 为 20200604，verified 为 True。非 override 行共 338 行。
- 行数 339，与 v1 一致。退市整理期从 89 增到 151，lost 为 0。
- 94322 状态为 T。

## 之后
- EXECUTE_v1.ok（f03357f1）已用完，归档到 _consumed。
- 下游接入这三份产物：cs_panel_v2_resumefix、suspend_flags_v2、stock_delisted_v2。每个下游各自的 run 都需要单独的 .ok，并钉住上述 sha。
