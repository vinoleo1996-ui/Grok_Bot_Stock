# Arch 回执：D=20261027 日更基线刷新（主 MATCH 拍板 A）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器：**刷新基线 + 写回执**；**不豁免 / 不回滚六文件 / 不令 Data 跑**） |
| 时刻 | `2026-10-27T06:22:29-04:00`（America/New_York；墙钟 `2026-10-27 06:22 ET`） |
| **VERDICT** | **BASELINE_REFRESHED**（拍板 **A**） |
| 主令 | 06:16/06:18 ET MATCH 拍板 A（审 **`02cacfc3`**；Data **`6c576eb4`**） |
| 旧基线 sha8 | **`dfdc2555`** |
| 新基线 sha8 | **`b7b39c2b`** |
| 工具 | `nightly_sha_scope_snapshot_20261018.py` sha8 **`0aa6c650`**（官方快照；未手改半行） |
| 本回合动作 | 备份旧基线 → 生成新快照 → compare 仅 6 MUST_NOT_CHANGE DIFF → 原子替换 → post-compare RESULT OK → 写本回执 → prepend TEAM_STATE；**未**豁免；**未**回滚；**未**令 Data；**未签**研究 `.ok`；**未挂** QUIET；≠混叶33；live=false；**leo_notify=false** |

## 0. 一句话

主 MATCH 漂移审 **`02cacfc3`** 后拍板 **A**：已用官方快照工具重签 `docs/v2/audit/nightly_sha_baseline_20261018_1022.txt`，旧 **`dfdc2555`** → 新 **`b7b39c2b`**；纳入现盘六钉；日历三钉 **`fa4260b8`/`7ccc911e`/`141078fa` 完好**；pre-compare MUST_NOT_CHANGE DIFF **仅 6**；post-compare vs 现盘 **RESULT OK**。**未令 Data 跑**——请主令 Data 重跑 D=20261027。

## 1. 新旧基线钉

| 项 | 路径 | sha8 | 全长 |
|---|---|---|---|
| 旧基线（刷新前） | `docs/v2/audit/nightly_sha_baseline_20261018_1022.txt` | **`dfdc2555`** | `dfdc25552918c7de24af240138fbc298d1ef2cb532723e18a6a4b7d892fb674c` |
| 旧基线备份 | `docs/v2/audit/nightly_20261027/nightly_sha_baseline_20261018_1022.PRE_REFRESH_dfdc2555.txt` | **`dfdc2555`** | `dfdc25552918c7de24af240138fbc298d1ef2cb532723e18a6a4b7d892fb674c`（`sha256sum` 与旧件一致） |
| **新基线（现盘）** | `docs/v2/audit/nightly_sha_baseline_20261018_1022.txt` | **`b7b39c2b`** | `b7b39c2b3b7342748af1f00dcee594a9fa07653a5e8b3c8b574596d92638717b` |
| scope | `docs/v2/audit/nightly_sha_scope_20261018.txt` | `b24a4a88` | （未改） |
| 快照工具 | `docs/v2/audit/nightly_sha_scope_snapshot_20261018.py` | **`0aa6c650`** | MATCH 钉 |

## 2. 六钉表（旧→新；全长本机 `sha256sum`）

| # | 路径 | 旧 sha8 | 新 sha8 | 全长（新） | 授权 |
|---|---|---|---|---|---|
| 1 | `quantlab/agents/trading_loop/settle.py` | `808f77d6` | **`a92b7ccf`** | `a92b7ccf12962820a114781b7b52dea7195d401d48aaea11cfec4fdaf305547b` | cand3 |
| 2 | `quantlab/data/sources.py` | `5ee62db0` | **`c8102489`** | `c8102489d662c63dcb67ef39c8ad7eba1ad661f34df6d2c8832624764bd0760c` | cand3 |
| 3 | `quantlab/portfolio/research_loop.py` | `d3ded87e` | **`5fe238f2`** | `5fe238f2372b95e809ef58382746d5984169315672edc67edc163654d2c7d4fd` | cand3 |
| 4 | `quantlab/portfolio/trade_calendar.py` | `ef44e7cd` | **`d2b6046c`** | `d2b6046cf27c27d81ca33d4c6a9d212efada5f08ec3803ad41c589d20f981e65` | cand3 |
| 5 | `research/b4_paper_extend.py` | `6c927ae6` | **`da62b28a`** | `da62b28a43a88bb9e28d725eba84040be7c99ae5b08e93e9960e4a0057aad1c6` | B4/S6 |
| 6 | `research/s6_paper_extend.py` | `3b258bbe` | **`93b00354`** | `93b0035431929ea6fddd955a30673e588606ab8aa97c94c0637dbc0d5a05bd45` | B4/S6 |

六路径现盘 sha8 **全部 MATCH** 上表；已写入新基线。

## 3. 日历 PIN（必须保持；本拍完好）

| PIN | 路径 | sha8 | 结果 |
|---|---|---|---|
| 冻结日历 | `data/v2/calendar/trade_cal_sse_pit.parquet` | **`fa4260b8`** | **MATCH**（新旧基线同钉；META_ONLY 可忽略） |
| calendar manifest | `data/v2/calendar/manifest.json` | **`7ccc911e`** | **MATCH** |
| Eng PIN trade_cal | `data/v2/tushare_raw/trade_cal.parquet` | **`141078fa`** | **MATCH** |

## 4. compare 证据

### 4.1 旧备份 vs 新快照（替换前闸）

命令：`python3 docs/v2/audit/nightly_sha_scope_snapshot_20261018.py --compare <scope> <PRE_REFRESH_dfdc2555> </tmp/nightly_sha_baseline_refresh_20261027.txt>`

| 类 | 计数 | 说明 |
|---|---|---|
| **DIFF MUST_NOT_CHANGE** | **6** | **仅**上表六路径；无第 7 个 → **PASS 闸，允许替换** |
| DIFF EXPECTED_CHANGE | 2 | `data_freshness_status.json` / `daily_update_status.json`（允许变） |
| META_ONLY_CHANGE | 多 | sha 同、mtime/ctime/inode 异（含日历三钉；**不挡**） |
| RESULT（工具 exit） | `MUST_NOT_CHANGE_DIFF_STOP` / exit1 | 预期（正是待纳入的 6 钉） |

日志：`docs/v2/audit/nightly_20261027/compare_PRE_dfdc2555_vs_NEW.txt`

六 DIFF 行：
```
DIFF MUST_NOT_CHANGE .../settle.py 808f77d6f4ef -> a92b7ccf1296
DIFF MUST_NOT_CHANGE .../sources.py 5ee62db01e7e -> c8102489d662
DIFF MUST_NOT_CHANGE .../research_loop.py d3ded87e111b -> 5fe238f2372b
DIFF MUST_NOT_CHANGE .../trade_calendar.py ef44e7cd0491 -> d2b6046cf27c
DIFF MUST_NOT_CHANGE .../b4_paper_extend.py 6c927ae69268 -> da62b28a43a8
DIFF MUST_NOT_CHANGE .../s6_paper_extend.py 3b258bbe9bd2 -> 93b003543192
```

### 4.2 新基线 vs 现盘再 snap（替换后）

命令：再 snap → `--compare` 新基线 vs live

| 项 | 值 |
|---|---|
| RESULT | **OK**（exit 0） |
| DIFF MUST_NOT_CHANGE | **0** |
| 日志 | `docs/v2/audit/nightly_20261027/compare_NEW_baseline_vs_live.txt` |

## 5. 授权链引用

| 环 | sha8 | 路径/说明 |
|---|---|---|
| 漂移审（建议 A） | **`02cacfc3`** | `docs/v2/audit/ARCH_NIGHTLY_20261027_MUST_NOT_CHANGE_DRIFT_REVIEW_20261027_ZH.md` |
| Data 跑前 BLOCKER 回执 | **`6c576eb4`** | `docs/v2/audit/nightly_20261027/NIGHTLY_RECEIPT_20261027_ZH.md` |
| cand3 合入核 | **`48334fbb`** | `docs/v2/audit/cand3_sse_calendar_20261026/ARCH_CAND3_BOX_PORT_APPLY_VERIFY_20261026_ZH.md` |
| Eng cand3 APPLY | **`5e28aff1`** | `docs/v2/audit/cand3_sse_calendar_20261026/ENG_CAND3_BOX_PORT_APPLY_RECEIPT_20261026_ZH.md` |
| B4 APPROVE_A 裁决 | **`559e3057`** | `docs/v2/audit/ARCH_B4_RHYTHM_ABORT_ADJUDICATION_A_20261026_ZH.md` |
| B4/S6 DIFF 审 | **`e506dc63`** | `docs/v2/audit/ARCH_B4_S6_RHYTHM_OPTION_A_DIFF_REVIEW_20261026_ZH.md` |
| B4 热修追认 | **`e90687aa`** | `docs/v2/audit/ARCH_B4_RHYTHM_OPTION_A_HOTFIX_UPDATE_REVIEW_20261026_ZH.md` |

## 6. 工序实录

1. 记录旧基线全长=`dfdc25552918c7de24af240138fbc298d1ef2cb532723e18a6a4b7d892fb674c`（sha8 **`dfdc2555`** MATCH 期望）
2. 备份 → `nightly_20261027/nightly_sha_baseline_20261018_1022.PRE_REFRESH_dfdc2555.txt`（复制；旧件保留至替换成功）
3. `python3 docs/v2/audit/nightly_sha_scope_snapshot_20261018.py docs/v2/audit/nightly_sha_scope_20261018.txt /tmp/nightly_sha_baseline_refresh_20261027.txt`（工具 **`0aa6c650`**）
4. 校验：六路径 sha8 MATCH；日历三钉 MATCH；`--compare` 旧备份 vs 新快照 → MUST_NOT_CHANGE DIFF **仅 6**（无第 7 → 未 STOP）
5. 原子写入：`cp` stage → `mv` 覆盖 `nightly_sha_baseline_20261018_1022.txt`；新 sha8=**`b7b39c2b`**
6. 再 snap + compare 新基线 vs 现盘 → **RESULT OK**
7. 写本回执；顶插 TEAM_STATE

## 7. 禁项（本回合已守）

- **未**签发豁免票（非 B）
- **未**回滚六文件（非 C）
- **未**自行令 Data 跑 / 未启动 daily_pull / 未改 `daily_update_status`
- **未签**研究 `.ok`；**未挂/抬** QUIET；**未**代跑研究
- **未**混叶33 / A18；**未** SendToUser / SendToAgent（父任务禁）
- live=false；promotion=false；**leo_notify=false**；不报 Leo

## 8. 下一跳

| 谁 | 动作 |
|---|---|
| **主 Agent** | MATCH 本刷新回执 → **令 Data 重跑 D=20261027**（daily_pull → 14 步；门禁用旧基线 `dfdc2555`） |
| **Data** | 等主令；用新基线 **`b7b39c2b`** 重跑；**不绕门**；不自改基线 |
| **Arch** | 本拍完成；听令；≠混叶33 |
| **Eng / AI / Strategy** | 本 blocker 不派 |

## 9. 本文件钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/audit/ARCH_NIGHTLY_20261027_BASELINE_REFRESH_20261027_ZH.md` |
| VERDICT | **BASELINE_REFRESHED**（A） |
| 旧基线 | **`dfdc2555`** |
| 新基线 | **`b7b39c2b`** |
| Data 回执（上游） | **`6c576eb4`** |
| 漂移审 | **`02cacfc3`** |
| 日历 PIN | **`fa4260b8`/`7ccc911e`/`141078fa` 完好** |
| 未令 Data | **true** |

live=false.
