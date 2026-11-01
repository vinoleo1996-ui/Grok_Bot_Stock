# Arch 审：D=20261027 日更跑前 MUST_NOT_CHANGE 6 漂移授权（只审建议；不刷新基线）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器：**只审建议**；**不刷新基线 / 不签发豁免票 / 不令 Data 重跑 / 不改 6 文件**） |
| 时刻 | `2026-10-27T06:13:15-04:00`（America/New_York；墙钟 `2026-10-27 06:13 ET`） |
| **总建议** | **A 刷新基线**（六文件全 **AUTHORIZED**；不宜 B/C） |
| Data 回执 | `docs/v2/audit/nightly_20261027/NIGHTLY_RECEIPT_20261027_ZH.md` sha8 **`6c576eb4`** MATCH |
| 基线（未改） | `docs/v2/audit/nightly_sha_baseline_20261018_1022.txt` sha8 **`dfdc2555`** MATCH |
| 漂移表 | `docs/v2/audit/nightly_20261027/MUST_NOT_CHANGE_DRIFT.txt` sha8 **`622182f4`** |
| 本回合动作 | 写本审回执；prepend TEAM_STATE；**未**改 baseline；**未**豁免；**未**令 Data 跑；**未**改 6 文件；**未签**研究 `.ok`；**未挂** QUIET；live=false；**leo_notify=false**；**不报 Leo** |
| 决策路由 | **主 Agent 拍板**后再动；本拍 ≠ 刷新授权 |

## 0. 一句话

Data D=20261027 跑前 MUST_NOT_CHANGE **6 漂移**相对基线 `dfdc2555`：**现盘六钉全 MATCH**；四件（settle/sources/research_loop/trade_calendar）为 **2026-10-26 14:12 ET 候选3 SSE 日历箱上 port APPLY**（合入核 **`48334fbb` PASS**；Eng APPLY **`5e28aff1`**）；两件（b4/s6_paper_extend）为 **B4/S6 rhythm Option A + B4 热修追认**（DIFF 审 **`e506dc63`**；热修追认 **`e90687aa`**；裁决 **`559e3057`**）。六文件均 **AUTHORIZED**。冻结日历/manifest/Eng PIN **完好未漂**。**总建议 A：主令后由 Arch 刷新/重签基线，再令 Data 重跑**。本拍 **未**改基线、**未**豁免、**未**令跑。

## 1. 钉表再核（本机 sha256）

| 件 | 路径 | 期望 sha8 | 实测全长 | 结果 |
|---|---|---|---|---|
| Data 回执 | `nightly_20261027/NIGHTLY_RECEIPT_20261027_ZH.md` | `6c576eb4` | `6c576eb451dcc1965f80794d330c5573b61fb2a93036dcbd6821f7f39b513c3b` | **MATCH** |
| 基线（未改） | `nightly_sha_baseline_20261018_1022.txt` | `dfdc2555` | `dfdc25552918c7de24af240138fbc298d1ef2cb532723e18a6a4b7d892fb674c` | **MATCH** |
| 漂移表 | `MUST_NOT_CHANGE_DRIFT.txt` | — | `622182f404d1c1e0f346ccbd535bce95c94f511921e06cc049189629cd978e02` | **记录** |
| settle.py 现盘 | `quantlab/agents/trading_loop/settle.py` | `a92b7ccf` | `a92b7ccf12962820a114781b7b52dea7195d401d48aaea11cfec4fdaf305547b` | **MATCH** |
| sources.py 现盘 | `quantlab/data/sources.py` | `c8102489` | `c8102489d662c63dcb67ef39c8ad7eba1ad661f34df6d2c8832624764bd0760c` | **MATCH** |
| research_loop.py 现盘 | `quantlab/portfolio/research_loop.py` | `5fe238f2` | `5fe238f2372b95e809ef58382746d5984169315672edc67edc163654d2c7d4fd` | **MATCH** |
| trade_calendar.py 现盘 | `quantlab/portfolio/trade_calendar.py` | `d2b6046c` | `d2b6046cf27c27d81ca33d4c6a9d212efada5f08ec3803ad41c589d20f981e65` | **MATCH** |
| b4_paper_extend.py 现盘 | `research/b4_paper_extend.py` | `da62b28a` | `da62b28a43a88bb9e28d725eba84040be7c99ae5b08e93e9960e4a0057aad1c6` | **MATCH** |
| s6_paper_extend.py 现盘 | `research/s6_paper_extend.py` | `93b00354` | `93b0035431929ea6fddd955a30673e588606ab8aa97c94c0637dbc0d5a05bd45` | **MATCH** |
| 冻结日历 | `data/v2/calendar/trade_cal_sse_pit.parquet` | `fa4260b8` | `fa4260b808755b9a1c91e3ade210edec84bbdb91e0dfff4c6a955c4d35fd8a41` | **MATCH** |
| calendar manifest | `data/v2/calendar/manifest.json` | `7ccc911e` | `7ccc911e8a3ed2e408f30db1f95f12eb71a6fea18003ba88a31246f941cc89a4` | **MATCH** |
| Eng PIN trade_cal | `data/v2/tushare_raw/trade_cal.parquet` | `141078fa` | `141078fa6da0ef94bc3cc8829aa031789490b7ff3e051b4baa4e38c496d06086` | **MATCH** |
| cand3 合入核 | `ARCH_CAND3_BOX_PORT_APPLY_VERIFY_20261026_ZH.md` | `48334fbb` | `48334fbbb4c4f889366e9029e7b90b433d3008b9d00f12c58242f816484aa677` | **MATCH** |
| Eng APPLY 回执 | `ENG_CAND3_BOX_PORT_APPLY_RECEIPT_20261026_ZH.md` | `5e28aff1` | `5e28aff1fc84031f71ba56aa2a503427e9e49010bd9e0b321914fe1dd9583dce` | **MATCH** |
| cand3 port 复审 | `ARCH_CAND3_BOX_PORT_REVIEW_20261026_ZH.md` | `7276ed4d` | `7276ed4d76227c700da324c5748126fc508baccc3518fa5eb94a60bf82560c1b` | **MATCH** |
| cand3 DIFF | `DIFF_cand3_box_port_20261026.diff` | `24e055fa` | `24e055fa8d1f9ec7be8981740a631903fba8cc5e68905c520b1d8fce6132a4fc` | **MATCH** |
| B4 热修追认 | `ARCH_B4_RHYTHM_OPTION_A_HOTFIX_UPDATE_REVIEW_20261026_ZH.md` | `e90687aa` | `e90687aad848cae6a22bb670b7729d1dcfc77ee56e64627f8c249a1144c6bd62` | **MATCH** |
| B4/S6 DIFF 审 | `ARCH_B4_S6_RHYTHM_OPTION_A_DIFF_REVIEW_20261026_ZH.md` | `e506dc63` | `e506dc63f1789cf8a966ee014624916595e8929286b08c5b661be44d436f40f7` | **MATCH** |
| APPROVE_A 裁决 | `ARCH_B4_RHYTHM_ABORT_ADJUDICATION_A_20261026_ZH.md` | `559e3057` | `559e30571b9459552dfc62b2d5f15aa5d8fe0f6eccc59ecf9405dcded5e86b44` | **MATCH** |
| 增量审计 1418 | `AUDIT_20261026_1418_ET_ZH.md` | — | `0b51c98ab80f62756f290c7d1cd6c98f42da7e7e35683134ad08f3b27fdd635f` | **对照**（钉四生产源码 + parquet PIN 区分） |

## 2. 逐文件裁定

| # | 路径 | 旧→新 sha8 | mtime ET | 改了什么（摘要） | 授权链 | 裁定 |
|---|---|---|---|---|---|---|
| 1 | `quantlab/agents/trading_loop/settle.py` | `808f77d6`→**`a92b7ccf`** | 10-26 14:12 | mock 分支 `pd.bdate_range`→`open_day_range`（SSE 开市日；禁 BDay）；schemas 相对 import 保留 | Eng APPLY `5e28aff1` → Arch 合入核 `48334fbb` PASS；port 复审 `7276ed4d`；DIFF `24e055fa`；AUDIT_1418 钉 | **AUTHORIZED** |
| 2 | `quantlab/data/sources.py` | `5ee62db0`→**`c8102489`** | 10-26 14:12 | `_a_daily` 优先 `trade_calendar.expected_session`；失败标 `calendar_required`；去掉默默 BDay/weekday fallback | 同上 cand3 链 | **AUTHORIZED** |
| 3 | `quantlab/portfolio/research_loop.py` | `d3ded87e`→**`5fe238f2`** | 10-26 14:12 | `_legacy_freshness` 加 DeprecationWarning + DEPRECATED docstring；**主路径 `data_freshness` 未改** | 同上 cand3 链 | **AUTHORIZED** |
| 4 | `quantlab/portfolio/trade_calendar.py` | `ef44e7cd`→**`d2b6046c`** | 10-26 14:12 | 增 `open_day_range` / `advance_open_days` / 测钩 `_OPEN_DAYS_OVERRIDE`；**未改** SRC/CUTOFF_ET/`expected_session`/`open_days` 读盘意图 | 同上 cand3 链 | **AUTHORIZED** |
| 5 | `research/b4_paper_extend.py` | `6c927ae6`→**`da62b28a`** | 10-26 19:28 | Option A：`LEG_CHG` 并入 booked change_days；热修 `\|=`→`.update`（消 UnboundLocalError）；旧 `6c927ae6`/`625ddcd6` **forbid** | APPROVE_A `559e3057` → DIFF 审 `e506dc63` → 热修追认 `e90687aa`（目标钉 **`da62b28a`**） | **AUTHORIZED** |
| 6 | `research/s6_paper_extend.py` | `3b258bbe`→**`93b00354`** | 10-26 19:22 | Option A：`leg_chg \|= set(change_days(...))` 同语义；热修未改 S6（local 合法） | APPROVE_A `559e3057` → DIFF 审 `e506dc63`；热修追认 `e90687aa` 确认现盘仍 **`93b00354`**；旧 `3b258bbe` **forbid** | **AUTHORIZED** |

### 2.1 与 parquet PIN 区分（勿混）

增量审计 `AUDIT_20261026_1418_ET_ZH.md` 钉 **UNCHANGED**：execution `373fed30` / sw_l1 `89d4afa3` / Eng `trade_cal.parquet` **`141078fa`**——后者为 **parquet PIN**，≠ `trade_calendar.py` 源码。源码四钉（tc/settle/rl/sources）在合入核已更新为现盘值；本审再核 **仍 MATCH**。

## 3. 总建议（三选一）

| 选项 | 适用 | 本拍判定 |
|---|---|---|
| **A 刷新基线** | 六文件全授权 → 写新基线（或更新同路径）+ 回执 → 再令 Data 重跑 D=20261027 | **推荐** |
| **B 豁免票** | 临时豁免当日 MUST_NOT_CHANGE 检（不宜改基线时） | **不推荐**——变更均为已合入/已追认的持久授权态；豁免会留下基线与盘不一致 |
| **C 回滚** | 未授权文件回滚到旧 sha 后再跑 | **不推荐**——六文件均授权；回滚会撤销 cand3 port 与 B4/S6 Option A（旧 sha 已 forbid） |

**结论建议 = A**（非混合）。

### 3.1 A 落地条件（主拍板后；本拍不做）

1. 主 MATCH 本审 → **令 Arch** 刷新 `nightly_sha_baseline_20261018_1022.txt`（或另写带日期新基线并改 scope/指针——以主令为准），使上述六路径钉为现盘全长 sha；其它 MUST_NOT_CHANGE 路径保持。
2. Arch 写刷新回执（新旧对照表 + 新基线 sha8）并 prepend TEAM_STATE。
3. 主再令 **Data** 重跑 D=20261027（daily_pull → 14 步）；Data **不得**自改基线/绕门。
4. 日历三钉 `fa4260b8` / `7ccc911e` / `141078fa` 刷新前后须仍 MATCH。

## 4. 禁项（本回合已守）

- **未**改 `nightly_sha_baseline_20261018_1022.txt` 或任何基线指针
- **未**签发豁免票；**未**令 Data 重跑；**未**启动 daily_pull
- **未**改 6 文件内容；**未**回滚
- **未签**研究 `.ok`；**未挂/抬** QUIET；**未**代跑重活
- **未** SendToUser / SendToAgent（父代理任务禁）；**leo_notify=false**；不报 Leo
- live=false；promotion=false；≠X2 ACCEPT

## 5. 下一跳

| 谁 | 动作 |
|---|---|
| **主 Agent** | MATCH 本审 → 拍板 **A** → 令 Arch 刷新基线（写回执）→ 再令 Data 重跑 D=20261027 |
| **Arch（听令后）** | 刷新基线 + 回执；**本拍不预写** |
| **Data** | 继续待命；**不绕门**；基线刷新回执齐后再跑 |
| **Eng / AI / Strategy** | 本 blocker 不派；勿混叶33 / A18 |

## 6. 本文件钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/audit/ARCH_NIGHTLY_20261027_MUST_NOT_CHANGE_DRIFT_REVIEW_20261027_ZH.md` |
| VERDICT / 建议 | **A 刷新基线**（6/6 AUTHORIZED） |
| Data 回执 | **`6c576eb4`** |
| 基线（未改） | **`dfdc2555`** |
| cand3 合入核 | **`48334fbb`** |
| B4 热修追认 | **`e90687aa`** |
| B4/S6 DIFF 审 | **`e506dc63`** |
| APPROVE_A | **`559e3057`** |

live=false.
