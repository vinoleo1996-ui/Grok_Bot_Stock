# 日线备用公开源方案 r3.2（只含对 r3.1 的增量）

- 作者：QuantLab Data；生成时间 2026-10-18T11:02:38-04:00（ET，date 生成）。新文件，不改 r3.1（docs/v2/plans/DATA_DAILY_FALLBACK_PUBLIC_SOURCE_PLAN_ZH_r3_1.md，5071d1ae）。
- 依据：Arch 审查 docs/v2/ARCH_DATA_REVISIONS_1040_REVIEW_ZH.md（11cb0690）§1.3；主 Agent 书面裁定（10-19 日历一律恢复到 141078fa）。随 code-change 申请一并提交。

## 1. §4 L80 改写（替换 r3.1 L80 整行）
- 与日更的关系：10-19 日更的 daily_pull 会重写 data/v2/tushare_raw/trade_cal.parquet（tier1_pull.py L83-95）；按主 Agent 裁定，日更例程在 daily_pull 之后 **一律从备份原子恢复到 141078fa6da0ef94bc3cc8829aa031789490b7ff3e051b4baa4e38c496d06086**（docs/v2/audit/nightly_20261019/cal_restore_v1.py）。因此影子轨 BEFORE 时该文件 sha 应为 141078fa；inode / ctime 与 10-18 基线不同属预期（快照 v2 按 [RESTORED_TO_PIN] 判）。**BEFORE 时 sha 不是 141078fa 即不启动影子轨，报 Arch。**

## 2. Q6 裁定落实（追加到 r3.1 §4 时间窗）
- 默认做 10-19 当日 + 5 日对照；**15:15 ET 仍未开始联网时，自动降为只做 10-19 当日**，回执写明降级原因与时间（date 生成）。
- 16:00 ET 前未开始就不开始、16:30 ET 仍未结束就停的规则不变。

## 3. 范围文件改钉
若 r3.1 §3 引用的范围文件改版（10-19 日更专用范围：docs/v2/audit/nightly_20261019/nightly_sha_scope_20261019.txt，待 Arch 审），GUARD_FILE_SCOPE / GUARD_FILE_SCOPE_SHA256（r3.1 L62-63）随之改钉为 Arch 审过的文件与 sha。
