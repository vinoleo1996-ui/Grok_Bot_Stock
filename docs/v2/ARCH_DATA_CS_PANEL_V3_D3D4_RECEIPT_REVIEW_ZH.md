# Arch 审查：Data v3 D3D4_stock_delisted dry-run 回执

- 审查时间：2026-10-18 05:02 ET
- .ok：dac5f6dd
- 结论：通过（P0/P1/P2=0，新增 P3=2）。v3 的四步 dry-run 全部完成。

## 复核
1. 四个 sha 复算一致：stdout c47c674c、receipt 0700bfe1、rawdiff 4b51e0dd、normdiff 5c8e2024。GATE_PASS，没有 VOID。开跑后 data/v2 下除 fund_portfolio_dh 外没有新文件，由 Arch 复算。
2. 两个期望值已记录，execute .ok 原样采用：
   - expected_face_value_recategorised = 000861.SZ,002505.SZ,002509.SZ,600297.SH
   - expected_unknown_needs_source_count = 56
3. FACE_CHECK：与诊断的双向差集为空，4 只股票每只都有 20 个收盘价，最高收盘不超过 0.99。UNKNOWN 为 56，差 0。
4. 进入整理期的从 89 变为 151，差值 +62 = 61 个零天修正 + 1 个 manual_override，没有丢失。
5. 与 v2 归一化对比后剩 5 行不同，都是 r6b 的新增或披露项。其余数字不变：339 行、61→0、89→151、face_value_flag 93。

## 仍未关闭（execute 前必须处理）
- P2-2（R6B）：manual_override 的断言仍是静态常量检查。本次回执的核对是 Data 人工完成的，不能替代代码断言。修复后须重签 dry-run .ok 并重跑 D3D4。
- P3-10：fix_sd1 中找不到 20261014 截断常量。Data 须查清它的来源（mask、v1 还是原始数据范围），写进修复回执，并说明是否影响 2026-07-30 之后的退市覆盖。
- P3-11：MemAvailable 从 10.7GB 降到约 3–4.5GB（Arch 在 05:01 实测为 4569MB）。ps 中最大的进程是 sand-host，约 1.0GB，这部分内存可能属于同机其他 agent。execute 前若低于 2GB，就暂停并报告。
