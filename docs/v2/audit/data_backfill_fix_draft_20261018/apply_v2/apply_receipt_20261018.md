# 补数误记 done 修复 v2：替换回执（2026-10-18 ET，QuantLab Data）
- 依据：output/data/ARCH_CODE_CHANGE_BACKFILL_FALSEDONE_FIX_V2.ok，sha 803413cd23ef6c439b75110a7b0f8d3bde2f303adb3479ef50783336d6c38047。
  - signed_et 05:09:39-04:00，不晚于当前时间（date 为 05:10:27 EDT）；expires_et 2026-10-19T05:09:39-04:00，未过期。
- 前置条件（05:10:29.92 EDT，逐个扫描 /proc/*/cmdline 和 stat，没有用 kill -0）：
  - 没有 relay_outage_backfill 进程，也没有 nightly_update 进程（扫描结果为空）；
  - output/relay_outage_backfill.pid 不存在；
  - 队列 sha 为 c22322a3…，与 .ok 的 queue_sha256_at_sign 相同；
  - nightly_update.py 的 sha 为 ec079d56912aea8a4358a7ae97a73a3ad6ee3df34e83845ad4d655d31d838636，未改动；
  - 草案目录 SHA256SUMS 的 sha 为 eef2d3eb…，与 .ok 相同；三个草案文件与 /tmp 草案逐字节相同（cmp）。
- 归档：_recovery/data/backfill_fix_pre_20261018/
  - relay_outage_backfill.py 4db3d9b197ce8c7bb063d0b3d571f59819491f7e3444efbdc3753876ffd4155c（= .ok current_backfill）
  - data_freshness_status.py 38e2911c489adcffd4dccdfe655a7fb75a3a1fbd5af39b1de77871e2daa569c3（= .ok current_freshness）
  - SHA256SUMS 的 sha 为 83e3dbe66a0c17725df29616b244aa32d4e0249baed66ae5ab34099d08f30d21
- 三处 sha 核对（草案 / 目标 / .ok pin）：

| 目标 | 草案 | 目标 | .ok pin | 结果 |
|---|---|---|---|---|
| scripts/acquire/relay_outage_backfill.py | 8d8364121b45dfadf03087698e10f6dfce6c630dc346dcedfc9885d6b0ec3a69 | 8d8364121b45dfadf03087698e10f6dfce6c630dc346dcedfc9885d6b0ec3a69 | 8d8364121b45dfadf03087698e10f6dfce6c630dc346dcedfc9885d6b0ec3a69 | MATCH |
| scripts/acquire/data_freshness_status.py | a759d29788859b43783bac6360014347b2df0e4dce5949302a0908db511f1d50 | a759d29788859b43783bac6360014347b2df0e4dce5949302a0908db511f1d50 | a759d29788859b43783bac6360014347b2df0e4dce5949302a0908db511f1d50 | MATCH |
| scripts/acquire/test_relay_outage_backfill_step_status.py | 7916a7ff14fc9410d77b8f5b314368b749b3d48ce83d28e2025675f4826243a8 | 7916a7ff14fc9410d77b8f5b314368b749b3d48ce83d28e2025675f4826243a8 | 7916a7ff14fc9410d77b8f5b314368b749b3d48ce83d28e2025675f4826243a8 | MATCH |

- py_compile 三个文件全部 ok，输出写到 /tmp/pyc_apply，设了 PYTHONDONTWRITEBYTECODE=1。
- scripts/acquire/__pycache__ 是原先就有的目录，里面最新的文件是 02:28:07 写的 event_flow_build。本次没有新增任何 pyc（find -newermt 05:10 结果为空）。
- 没有改 nightly_update.py 和队列，没有运行 freshness，没有重启补数。
