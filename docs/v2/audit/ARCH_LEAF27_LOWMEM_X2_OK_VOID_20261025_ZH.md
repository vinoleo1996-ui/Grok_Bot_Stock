# Arch 叶27 LOWMEM×x2 `.ok` 正式 VOID（ABORT_RSS）

- 角色：QuantLab Arch
- 时刻：2026-10-25T11:52:36-04:00（America/New_York）
- 依据：主→Arch 正式 VOID；主旁证 `docs/v2/audit/MAIN_LEAF27_LOWMEM_ABORT_RSS_STOP_20261025_ZH.md` sha8=`07e3efef`；AI 报 ET_TS=`20261025_115003` 峰 1877MB
- live=false；promotion_approved=false

## 结论

**VOID** — `.ok` 原内容 sha8=`8bcd79dc` **禁再消费**；**未新签前禁重开**。

## 钉

| 项 | 值 |
|---|---|
| 原 live 路径 | `output/ai_factory/ARCH_RUN_AUTH_LEAF27_ON_MINUS_ID_IDIO_IVOL_HILIQ_LOWMEM_X2.ok`（已不在 live） |
| 原内容 sha256 | `8bcd79dcc7a0e10640f2b7807a7e632ba2a6b7e20e385dfc1d58d07487fc9078` |
| 原内容 sha8 | `8bcd79dc` |
| 主 park 后字节 sha | `1d5e1016d9bdf8c4f529c1116083a02092ce7535b18b16b371580ea565d49f09`（含 `# MAIN_ABORT_PARK` 脚注） |
| Arch VOID 归档 | `output/ai_factory/_consumed/ARCH_RUN_AUTH_LEAF27_ON_MINUS_ID_IDIO_IVOL_HILIQ_LOWMEM_X2.8bcd79dc.VOID.ABORT_RSS.20261025T1152ET.ok` |
| 脚本 | `05bd81ea…`（lowmem_v1） |
| 审阅 | `aefa7faa…` PASS_WITH_CONDITIONS（静态合格≠峰≤1500） |
| 另 VOID | `725be3e0`（11:15 旧 HI_LIQ）仍禁复用 |

## 两跳事实

| 跑 | ET_TS | pid | log 峰 | 结果 |
|---|---|---|---|---|
| 1 | 20261025_114923 | 719646 | **1933MB** | ABORT_RSS @ members_loaded days=644 |
| 2 | 20261025_115003 | 720992 | **1877MB** | 同 `.ok` 第二跑；主 TERM；Arch 确认无存活进程 |

- 装载点：`members_loaded` / `capadv_days` / `mktcap_days` 均报同峰 → **日历 644 日一次性装载**未压到 ≤1500
- 无 alpha 产物
- `STOP_NO_RELAUNCH`：present — '2026-10-25T11:50:30-04:00 MAIN: ABORT_RSS both launches; .ok parked; DO NOT relaunch without new Arch .ok\nrun1=1933MB run2=1877MB members_loaded; rss_limit=1500\nlive=false\n'

## 下一跳（架构）

1. **禁**复用 `8bcd79dc` / `725be3e0`；**禁抬帽** 1500
2. 下一包须 **改装载/分块**（按年或季切 `cal_set`，禁止 644 日一次 `load_*`）；另 DIFF+审阅后再另窗签
3. sealed 仍另签；FULLA 仍 GAP
4. QUIET：现盘无锁（跑已停）；不代挂除非主/下一窗需要

## 非动作

- 本回合**不**新签 `.ok`；**不**代跑；**不**抬 rss
