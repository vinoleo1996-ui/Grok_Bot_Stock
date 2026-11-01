# 补跑授权 .ok 签发回执（1019–1023）

- 时刻（America/New_York）：2026-10-25T04:45:52-04:00
- 依据：主 04:41 补跑令；enable 已消费（4377eb59…）；Leo 解冻续接
- live=false；promotion=false

## .ok

| 项 | 值 |
|---|---|
| 路径 | `output/data/ARCH_RUN_AUTH_DATA_BACKFILL_1019_1023.ok` |
| sha256 | `9e4359f9b6521e9d8d2b9578c7031ac6e79d42bd7dc4e3003e34a7c0c3e32714` |
| sha8 | `9e4359f9` |
| date_list | `20261019,20261020,20261021,20261022,20261023` |
| allow_backfill | true |
| allow_run | true（**仅** date_list；须专用补跑执行器） |
| allow_paper / stream | false |

## 重要边界

- **不是** `ok_type=run` 的 nightly 单日 .ok；`run_nightly_v1_dbincr_v3_1.py` 仍强制 ET 日==D，**禁止**用它硬跑历史日。
- Eng 须交 **1019–23 专用补跑执行器包**（仿 plan R），Arch 审 runner 后再实跑；本 .ok 授权补跑窗口与钉。
- 钉：driver f1910e8a / nightly 2b4704e8 / incr a7ac54b3 / transform 308b5054 / tier1 7205ba43 / trade_cal 141078fa；enable 4377eb59。
- trade_cal 只读：1019–23 均为 is_open=1。

## 分发

主 / Eng / Data。勿与叶25/纸面/stream 混用。
