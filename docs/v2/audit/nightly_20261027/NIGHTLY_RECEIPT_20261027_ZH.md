# QuantLab Data 例程回执：A股日线收盘后更新 D=20261027 — **BLOCKER 停跑**

- 角色：QuantLab Data 执行器
- 时区：America/New_York（ET）
- 回执生成时刻（ET）：2026-10-27T06:06:22-04:00
- live=false；promotion_approved=false；未启动 8787；未碰 moneyflow；未跑 trade_cal/sw
- **outcome=BLOCKER**：跑前快照 vs 基线出现 **MUST_NOT_CHANGE sha 漂移** → 按规程 **未启动** daily_pull / 第二次调用

## 1. 启动前核验

| 项 | 结果 |
|---|---|
| /proc/94322 | 不存在 → 跳过 SIGCONT |
| MemAvailable 起步 | ≈12.24 GiB ≥2GB，继续 |
| 冻结日历 trade_cal_sse_pit.parquet | sha=fa4260b808755b9a1c91e3ade210edec84bbdb91e0dfff4c6a955c4d35fd8a41 **MATCH** |
| SSE 20261027 / 20261028 is_open | 均为 **1**（20261029=1；20261030=1；20261031=0） |
| calendar/manifest.json | sha=7ccc911e8a3ed2e408f30db1f95f12eb71a6fea18003ba88a31246f941cc89a4 **MATCH** |
| Eng 日历 trade_cal.parquet | sha=141078fa6da0ef94bc3cc8829aa031789490b7ff3e051b4baa4e38c496d06086 **MATCH** |
| 快照脚本 nightly_sha_scope_snapshot_20261018.py | sha=0aa6c6505a90aa7b09cb1c56b079695499a44515758a0da849aebfab29328e37 **MATCH** |
| 基线 nightly_sha_baseline_20261018_1022.txt | sha=dfdc25552918c7de24af240138fbc298d1ef2cb532723e18a6a4b7d892fb674c **MATCH** |
| 跑前快照路径 | docs/v2/audit/nightly_20261027/sha_pre_20261027.txt sha=6785bcd237a370c05f87c2c8e90cf22cb2d209cbbf396391d943452316068d14 |
| 跑前快照 vs 基线 | **RESULT MUST_NOT_CHANGE_DIFF_STOP** → **BLOCKER** |
| 上日状态 daily_update_status.json | target_trade_date=2026-10-26（未改，因未跑日更） |

## 2. BLOCKER 明细（MUST_NOT_CHANGE sha 漂移）

相对基线 `nightly_sha_baseline_20261018_1022.txt`（亦相对 10-26 跑前快照，六文件在 10-26 日更时仍与基线一致）：

| 路径 | 基线/10-26 sha8 | 当前 sha8 | mtime（盒本地 +0800 → ET） |
|---|---|---|---|
| quantlab/agents/trading_loop/settle.py | 808f77d6 | a92b7ccf | 2026-10-26 14:12:36 ET |
| quantlab/data/sources.py | 5ee62db0 | c8102489 | 2026-10-26 14:12:36 ET |
| quantlab/portfolio/research_loop.py | d3ded87e | 5fe238f2 | 2026-10-26 14:12:36 ET |
| quantlab/portfolio/trade_calendar.py | ef44e7cd | d2b6046c | 2026-10-26 14:12:36 ET |
| research/b4_paper_extend.py | 6c927ae6 | da62b28a | 2026-10-26 19:28:52 ET |
| research/s6_paper_extend.py | 3b258bbe | 93b00354 | 2026-10-26 19:22:22 ET |

- 证据：`docs/v2/audit/nightly_20261027/sha_pre_vs_baseline.txt`；精简：`MUST_NOT_CHANGE_DRIFT.txt`
- 冻结日历 / Eng 日历 / calendar manifest：**未漂移**（仅 META_ONLY_CHANGE）
- EXPECTED_CHANGE：daily_update_status.json、data_freshness_status.json（相对 10-18 基线，预期）

## 3. 已做 / 未做

### 已做
- mkdir docs/v2/audit/nightly_20261027、_recovery/data/nightly_20261027
- 跑前快照 + vs 基线比对
- Eng 日历备份：`_recovery/data/nightly_20261027/trade_cal.parquet.bak` sha=**141078fa…**（chmod a-w）
- 准备 cal_compare：`/tmp/cal_compare_20261027.py` 与 docs 副本（MUST_OPEN=[20261027,20261028]）sha=b5835b253ae4cc0ee6ad35d2993bea21f0877b4f7bcf40ce6805534a4d47c774

### 未做（因 BLOCKER 停跑）
- **未调用** `python3 scripts/nightly_update.py --date 20261027 --steps daily_pull`
- **未做** 日历比对/恢复（无改写发生；备份保留）
- **未调用** 第二次 14 步
- **未拍** sha_post；无新交易日数据落盘
- 无 DONE marker

## 4. 关键 sha 钉点（停跑时）

| 钉 | 全长 sha | 状态 |
|---|---|---|
| 冻结日历 fa4260b8 | fa4260b808755b9a1c91e3ade210edec84bbdb91e0dfff4c6a955c4d35fd8a41 | 不变 |
| calendar manifest 7ccc911e | 7ccc911e8a3ed2e408f30db1f95f12eb71a6fea18003ba88a31246f941cc89a4 | 不变 |
| Eng 日历 141078fa | 141078fa6da0ef94bc3cc8829aa031789490b7ff3e051b4baa4e38c496d06086 | 不变（备份同） |

## 5. 处置建议（priority → Arch + 主 Agent）

1. Arch 审阅上述 6 个 MUST_NOT_CHANGE 漂移是否为授权变更；若是，**重签/刷新** `nightly_sha_baseline_20261018_1022.txt`（或签发豁免票）后再令 Data 重跑 D=20261027。
2. 若未授权：查明 2026-10-26 14:12 ET / 19:22–19:28 ET 谁改了这些文件，回滚或补签后再跑。
3. Data 侧待命；**不**自行改基线、不绕过 MUST_NOT_CHANGE 门禁。
4. Eng 日历 PIN 与冻结日历完好；交易日 20261027 is_open=1，具备重跑条件（仅卡在代码侧 MUST_NOT_CHANGE）。

## 6. rcs

| 调用 | rc |
|---|---|
| daily_pull | **未执行** |
| 14-step | **未执行** |
| sha pre vs baseline | exit=1（MUST_NOT_CHANGE_DIFF_STOP） |

live=false；promotion=false。
