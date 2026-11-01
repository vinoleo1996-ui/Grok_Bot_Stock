# Data 10-18 新文件勘误（新文件，不改被勘误的文件）

- 作者：QuantLab Data；2026-10-18 10:40 ET。被勘误文件在安装后按规则不再修改，以本文为准。

## 1. 起草时间写错（写成了尚未到来的时间）
| 文件 | sha256 | 文中写的 | 实际（安装时刻，ET） |
|---|---|---|---|
| docs/v2/audit/BACKFILL_1014_1016_OK_REQUEST_ZH.md | 122277e2f0c58a423e34ce23676bf8263a38660bbeefb1cf176708194bc252b7 | 起草 10:20–10:50 ET | 10:20–10:31:41 |
| docs/v2/plans/DATA_SW_L1_PIT_V2_FIX_PLAN_ZH_r3_1.md | daa19d2695f2e42591712204a6e622dcd16801434d3dd4480c15d56d9490ddab | 起草 10:30–11:00 ET | 10:31–10:34:23 |
| docs/v2/plans/DATA_CALENDAR_2027_PACKAGE_PLAN_ZH_r2.md | c1b51e13aa923d35b294eb98b8563ae5781257d1120873885c55cf8ca9f804d7 | 起草 11:00–11:20 ET；§5「11:10 ET 重新计数」 | 起草 10:34–10:36:20；§5 默认忽略规则四组计数在 10:27:43，-uu 两组在 10:34:57 |
| docs/v2/plans/DATA_DAILY_FALLBACK_PUBLIC_SOURCE_PLAN_ZH_r3_1.md | 5071d1aefd74890034b2bf9bd12e025e2c08a21f455179855ed6c4c6d4065673 | 起草 11:20–11:40 ET | 10:36–10:38:16 |
- 内容、命令、行号与 sha 不受影响；只是时间标注错误，记 Data 的错误。

## 2. 日历 r2 §3 的一处说明
- available_at_for_year() 拒绝「公告发布时间晚于拉取完成时间」，所以通过检查时恒有 notice_at ≤ pulled_sh，max(rule_floor, notice_at, pulled_sh) 实际等于 max(rule_floor, pulled_sh)；notice_at 在公式里不会成为最大值，它的作用是顺序检查与 manifest 记录。这与 Arch P2-2 的公式结果一致。§3 selftest 用例 11 里「公告晚发」那一条的期望值因此是 pulled_sh。

## 3. SW r3.1 §8 自报的补充
- 写完 SW r3.1 之后，10:35 ET 前后又有一次把 cut 接在 rg 后面的管道（把 trade_cal_pit.py 与 trade_cal 引用整理到 /tmp/arch1018 下的文件），同属「可能读 stdin 的命令接在管道后」，只处理 rg 的输出，没有写 repo 或 data。之后的命令都改为输出到文件再读。
