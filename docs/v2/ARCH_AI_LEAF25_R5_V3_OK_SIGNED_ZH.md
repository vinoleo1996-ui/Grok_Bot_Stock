# 叶25 step_m1 R5 — 新窗 .ok 签发回执（v3）

- 时刻（America/New_York）：2026-10-25T04:38:07-04:00
- 依据：Leo 04:30 ET 解冻；主分签令；旧 R5_v2 恢复后禁直接消费
- live=false；promotion=false

## .ok

| 项 | 值 |
|---|---|
| 新路径 | `output/ai_factory/ARCH_RUN_AUTH_LEAF25_TTM_RECON_STEP_M1_R5_v3.ok` |
| sha256 | `8c77420ab965cdceb95e563863fb23baa946cbbe5db342e2a9b2f4b4f4318b05` |
| sha8 | `8c77420a` |
| 窗 | 2026-10-25 10:00–10:45 ET（expires 11:00 ET） |
| 旧 R5_v2 | 已 SUPERSEDED → `output/ai_factory/_consumed/ARCH_RUN_AUTH_LEAF25_TTM_RECON_STEP_M1_R5_v2.b052fc9b.SUPERSEDED.20261025T043807ET.ok`（旧 sha `b052fc9bd1ac334dfbb1340c032836827b19e7edd0fcc032b9ec52828d0d2b77`） |

## 钉复核

script/cmd/pin_list/wrapper 现盘 MATCH；输入财务/日历钉沿用 R5_v2。
MemAvailable@sign = 6749128 kB；pgrep web = empty。

## 给 AI

可在窗内按本 v3 .ok 开跑 step_m1/accruals r5；**勿消费**已 SUPERSEDED 的 R5_v2。
prelaunch：RESEARCH_QUIET + healthz quiet + ≥15s + 括号 pgrep 空 + MemAvailable≥2.5GiB。
