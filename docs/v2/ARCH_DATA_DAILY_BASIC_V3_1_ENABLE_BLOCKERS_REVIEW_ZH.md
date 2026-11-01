# daily_basic 增量 v3.1 — Arch 启用前 P1 阻塞项闭合审查

live=false；promotion=false；**未签 enable/run .ok**；**未改生产**。
- 审查对象：Eng 声称的启用前 P1 阻塞项闭合（incr 新 sha + enable_blockers 回执/DIFF/自测）
- 先验实现审阅：docs/v2/ARCH_DATA_DAILY_BASIC_V3_1_IMPL_REVIEW_ZH.md sha256 **9f6c67542f5c6a43ffcbc6cdec61bd59c1236ece9ff90838582f9afe155c72f9**
- 已签实现审阅 .ok：output/data/ARCH_RUN_AUTH_DAILY_BASIC_INCR_V3_1_IMPL_REVIEW.ok sha256 **2637d277470c3fd3149074b75f0f2fa7c62b50f83edc0048d6550146bb3364a9**（allow_enable=false；钉旧 incr a60490956b4ffd26…）
- 设计钉：**5c6a3a1dcc0fdcba279cafbbacf64c829fc50ee9ed3faf0d8095b6dc4b8c17fc**；设计确认：**23886baac3edbbf0975d257a3126ba05396365c275ba85c684e98b9ecc1c6fa2**
- 审查时刻（America/New_York）：2026-10-25 00:56 ET
- 方式：只读静态 + 自测产物/生产 valuation 元数据 sha；**不重跑自测**；**不写生产**

## 结论

**P1_CLOSED**

- 声称 sha 全核一致；enable_blockers 自测 **27 PASS / 0 FAIL**；A7 生产 `data/v2/valuation/` 6 文件现盘 sha = 库存（equal）。
- 先验实现审阅列出的启用挡板（§2.8/§2.9 stub、C7/A15、C9/A13 满配、C8/A18）均已有代码级替换 + 自测绿。
- **仍 `allow_enable=false` / `allow_run=false`**：启用包（`run_nightly_v1.py` f99dd11a 驱动重钉 + nightly CLI 增量接线 + 全量路径 `QL_DB_ALLOW_FULL` 原子 manifest）**未动**；今晚不签 enable/run。
- 建议父会话 **SUPERSEDE** 旧实现审阅 .ok 并签 **r2**（钉新 incr sha；`enable_blockers=` 清空或改记「启用包未齐」；仍 allow_enable=false）。

## 材料核验（sha256 全长）

| 件 | 声称 | 现盘 | 结果 |
|---|---|---|---|
| daily_basic_incremental.py（新） | a7ac54b3… | `a7ac54b3ecdf33d338710df5c96f447fbec51affdcfbf167fb3e00648f678dd8` | OK |
| （旧基线，作废） | a6049095… | `a60490956b4ffd268dd0cf9c98b204f7cd8fd459bc79d8e762c49ed8c4fe1159` | 记录；已不在现盘路径 |
| tier1_materialize.py | 2af28a69… | `2af28a69ddfbe914df634e113960c44f3ee9eb62f9998521d34abf366cd60204` | OK（未再改） |
| fund_portfolio_stream_merge.py | 374489d0… | `374489d0907d10b8464f9344f79ea127fb960494de0ac5ff7f44905cb5115cec` | OK（未动） |
| transform_sha | 308b5054… | `308b5054c39801116fd0eb19b4e4bd10bdccd4b4d40bfb67dd06a58fa67ab974` | OK（仍钉；tier1 未变） |
| ENABLE_BLOCKERS_RECEIPT_ZH.md | 35aa6b71… | `35aa6b71e667eecb596502f5ba0cfd2860ff36de67bfd26b14dfefb9900b0ba0` | OK |
| DIFF_ENABLE_BLOCKERS_ZH.md | f93599e6… | `f93599e655d368d56d1a22e7798660fd23f657a2469eaee547f9565769e94b0c` | OK |
| selftest_enable_blockers.py | fb7917ed… | `fb7917ed669aadae166e9e04d2e85a7cb9b1732033dcd90ee58b114fb8371eba` | OK |
| SELFTEST_RESULTS.json | （未钉） | `9f3126ba1826a689f9ce5f7f7b9640ac9b513f6024987941e8aa9bfcd0307ccf` | 记录；n_pass=27 n_fail=0 |
| nightly_update.py live | ec079d56… | `ec079d56912aea8a4358a7ae97a73a3ad6ee3df34e83845ad4d655d31d838636` | OK（未改） |
| run_nightly_v1.py（docs audit 钉） | f99dd11a… | `f99dd11aa26f611a…`（docs/v2/audit/nightly_20261019/） | OK（启用接线未动） |
| 设计 / 设计确认 / 旧实现审阅 | 5c6a3a1d / 23886baa / 9f6c6754 | 全长一致 | OK |

## 静态：§2.8 / §2.9 stub 已替换

| 检查 | 结果 |
|---|---|
| `_row_group_physical_col_hashes` + `_verify_readback` 逐 RG 比物理列 hash；不一致→23 | **有**（L282–320 / L727–764） |
| `QL_DB_INCR_LOOSE_READBACK` 旁路 | **删除**（仅出现在 `BANNED_ENVS_INCR` + `_refuse_banned_envs`→20） |
| `_iter_monthly_frames` + `_history_diff_scan` 顺序扫描/按月分桶；调 `tier1._compare_daily_basic_history`；DupKey→24 | **有**（L767–868）；主路径 L1110 调 `_history_diff_scan` |
| 整表 pandas stub / 仅行数回读 | **无功能残留** |
| 命名残留 | L872 `_history_diff_stub = _history_diff_scan`（兼容别名，**非**实现）；`ref_build_year` 诊断键名 `year_sorted_content_col_hashes_stub`（P3 清洁，不挡 P1） |

## 自测门槛数字

| 项 | 门槛 | 回执/RESULTS | 结果 |
|---|---|---|---|
| §2.8 S28 篡改 | → exit 23 | S28_readback_hash_mismatch_23 rc=23 tmp_gone | PASS |
| §2.9 S29 | history_diff_rows>0 | history_diff_rows=20 | PASS |
| C7/A15 五阶段 TERM | ≤5s；回滚完整 | copy/build/readback/diff/commit 均 rc=-15；elapsed≈0.007–0.008s；tmp_gone/dest_same/man_same/pending_gone | PASS |
| C9/A13 满配 | rows=1,313,182；peak_vmhwm_kb≤1e6 | rows=1313182；peak_vmhwm_kb=**253972**（隔离子进程；A13_ISOLATED 另记 254640，同阈） | PASS |
| C8/A18 | 缺/错 new_sha256→20 | 两案均 rc=20 | PASS |
| 三禁用 env | 任一设置→20 | STALE_SHA / LOOSE_READBACK / ALLOW_FULL 均 rc=20 | PASS |
| 合计 | — | **27 PASS / 0 FAIL**（RESULTS 逐条 ok=True） | PASS |
| A7 | 生产 valuation 6 文件不变 | 现盘复核 equal=True（相对 PROD_VALUATION_SHA_INVENTORY_BEFORE.json） | PASS |

## 相对先验实现审阅 enable_blockers 逐项

先验 .ok：`enable_blockers=P1_2.8_2.9_stub|C7_A15_TERM5s|C9_A13_full_1.3M|P2_C8_A18_fixture`

| 键 | 状态 |
|---|---|
| P1_2.8_2.9_stub | **CLOSED** |
| C7_A15_TERM5s | **CLOSED** |
| C9_A13_full_1.3M | **CLOSED** |
| P2_C8_A18_fixture | **CLOSED** |

## 残留（非本晚 P1；挡 enable 包 / 清洁）

1. **启用包未做**（挡 `allow_enable=true`）：`run_nightly_v1.py`（f99dd11a）重钉新 incr/tier1/transform；`nightly_update.py` CLI 改增量路径；全量 `QL_DB_ALLOW_FULL` + 原子 manifest（须另签 full 路径 .ok）。
2. **P3 命名**：`_history_diff_stub` 别名；`year_sorted_content_col_hashes_stub` 键名。
3. **P3**：先验 `_recover_pending` 死代码等清洁项仍在（未复查是否随本 diff 消失；不挡 P1）。
4. S1–S13 全集仍可在启用前/后补齐（本回执未声称全集；不挡本 P1 结论）。

**P0 残留：无。P1 残留：无（启用包另册，不记作本审查 P1 未闭）。**

## 实现审阅 .ok r2 建议键（父会话签发；本文不创建 .ok）

- `kind` / `auth_type`: `impl_review`
- `ok_path`: `output/data/ARCH_RUN_AUTH_DAILY_BASIC_INCR_V3_1_IMPL_REVIEW_r2.ok`（或 SUPERSEDE 同路径并归档旧 2637d277…）
- `supersedes`: `2637d277470c3fd3149074b75f0f2fa7c62b50f83edc0048d6550146bb3364a9`
- `verdict`: `PASS_WITH_CONDITIONS`（条件=启用包未齐）或 `P1_CLOSED_IMPL_OK`
- `path_incr`: `scripts/acquire/daily_basic_incremental.py`
- `incr_sha256`: `a7ac54b3ecdf33d338710df5c96f447fbec51affdcfbf167fb3e00648f678dd8`
- `path_tier1`: `scripts/acquire/tier1_materialize.py`
- `tier1_sha256`: `2af28a69ddfbe914df634e113960c44f3ee9eb62f9998521d34abf366cd60204`
- `transform_sha`: `308b5054c39801116fd0eb19b4e4bd10bdccd4b4d40bfb67dd06a58fa67ab974`
- `enable_blockers_receipt_sha256`: `35aa6b71e667eecb596502f5ba0cfd2860ff36de67bfd26b14dfefb9900b0ba0`
- `enable_blockers_diff_sha256`: `f93599e655d368d56d1a22e7798660fd23f657a2469eaee547f9565769e94b0c`
- `enable_blockers_review_sha256`: （签发时填本审查文 sha256）
- `design_sha256`: `5c6a3a1dcc0fdcba279cafbbacf64c829fc50ee9ed3faf0d8095b6dc4b8c17fc`
- `design_review_sha256`: `23886baac3edbbf0975d257a3126ba05396365c275ba85c684e98b9ecc1c6fa2`
- `prior_impl_review_sha256`: `9f6c67542f5c6a43ffcbc6cdec61bd59c1236ece9ff90838582f9afe155c72f9`
- `enable_blockers`: ``（空）或 `ENABLE_PACK_DRIVER_CLI`
- `allow_enable`: **false**
- `allow_run`: **false**
- `allow_write_production`: **false**
- `forbid_env`: `QL_DB_INCR_ALLOW_STALE_SHA|QL_DB_INCR_LOOSE_READBACK|QL_DB_ALLOW_FULL`
- `live`: false；`promotion`: false
- `note`: P1 enable-blockers closed; enable pack (driver re-pin + CLI) still required; no enable tonight

## 启用包下一步（给 Eng；仍不授权今晚 enable）

1. 新建/改驱动文件（勿原地改 f99dd11a 生产名除非设计允许）：重钉 `incr_sha=a7ac54b3ecdf33d338710df5c96f447fbec51affdcfbf167fb3e00648f678dd8`、`tier1_sha=2af28a69ddfbe914df634e113960c44f3ee9eb62f9998521d34abf366cd60204`、`transform_sha=308b5054c39801116fd0eb19b4e4bd10bdccd4b4d40bfb67dd06a58fa67ab974`；旧 e9c89a6c/a6049095 键作废。
2. `nightly_update` / CLI：增量路径接线到 `materialize_daily_basic_incremental`；全量仍须 `QL_DB_ALLOW_FULL=1` + 原子 manifest，且生产禁设三禁用 env。
3. 交启用包 DIFF + /tmp 接线自测回执后，再申请 **单独** enable .ok（窗与 Data 空档另裁）；**今晚不申请**。

## 给 Eng 的原文草案

> Arch：daily_basic v3.1 启用前 P1 **CLOSED**（审查 docs/v2/ARCH_DATA_DAILY_BASIC_V3_1_ENABLE_BLOCKERS_REVIEW_ZH.md）。incr 钉 **a7ac54b3…**；transform 仍 **308b5054…**；tier1/fundport/nightly 未动核过。27/27 与 A13 peak=253972、A15≈0.008s、A7 equal 已核。建议父会话 SUPERSEDE 旧实现审阅 .ok→r2（仍 allow_enable=false）。**启用包下一步**：①驱动重钉新 incr/tier1/transform；②nightly CLI 增量接线（全量仍 QL_DB_ALLOW_FULL+原子 manifest）；③交 DIFF+/tmp 后再申请单独 enable .ok。**今晚不签 enable/run。** live=false。
