# daily_basic 增量 v3.1 — Arch 实现审阅

live=false；promotion=false。
- 审查对象：Eng 实现 + /tmp 自测 + transform_sha 提案（非启用/运行授权）
- 设计钉：docs/v2/DATA_DAILY_BASIC_INCREMENTAL_DESIGN_v3_1_ZH.md sha256 **5c6a3a1dcc0fdcba279cafbbacf64c829fc50ee9ed3faf0d8095b6dc4b8c17fc**（FROZEN 逐字节一致）
- Arch 设计确认：docs/v2/ARCH_DATA_DAILY_BASIC_V3_1_REVIEW_ZH.md sha256 **23886baac3edbbf0975d257a3126ba05396365c275ba85c684e98b9ecc1c6fa2**
- 归档：`_recovery/data/daily_basic_incr_20261025T003519ET/`（tier1 **e9c89a6c…**；nightly_update **ec079d56…**，与 live `scripts/nightly_update.py` 一致）
- 审查时刻（America/New_York）：2026-10-25 00:44 ET
- 方式：只读静态 + 自测产物/生产 valuation 元数据 sha 核对；**未改生产代码/parquet**；**未签 enable/run .ok**

## 结论

**PASS_WITH_CONDITIONS**

- 声称 sha 全核一致；/tmp 自测 **13 PASS / 0 FAIL**；A7 生产 `data/v2/valuation/` 6 文件 sha 与开跑前库存一致（现盘复核 equal）。
- C1–C6、C10–C12 主体已落地；C7/C8 夹具/C9 满配按 Eng 披露延期，**挡启用 .ok，不挡本实现审阅**（见下表）。
- **条件（挡启用，不挡带条件签发实现审阅 .ok）：**
  1. **P1 §2.8/§2.9**：`_verify_readback` 仅比行数；`_history_diff_stub` 整表读入 pandas，非设计顺序扫描/按月分桶。启用前须换成设计级实现并补测，禁止依赖 stub 上生产。
  2. **P1 C7/A15**：五阶段 TERM≤5s 未测（SIGHUP→32 已绿）。启用前须绿。
  3. **P1 C9/A13**：满配 1,313,182 行 VmHWM≤1e6 kB 未测（scaled 18k peak≈156MB）。启用前须绿。
  4. **P2 C8/A18**：专用「新表+过时 manifest」夹具未跑；precheck 在 `build.new_sha256` 缺失时不触发 A18。启用前补夹具，并收紧「无合格基线→20」。
- **今晚不签 enable / 补跑 / 运行 .ok**。实现审阅 .ok（若签）必须 `allow_enable=false`、`allow_run=false`。
- `run_nightly_v1.py`（f99dd11a）L66 仍钉旧 tier1 **e9c89a6c**——符合设计 §6.1「新驱动文件名后重钉」；**未改 f99dd11a / nightly_update**。启用包另办。

## 材料核验（sha256 全长）

| 件 | 声称 | 现盘 | 结果 |
|---|---|---|---|
| 设计 v3.1 | 5c6a3a1d… | `5c6a3a1dcc0fdcba279cafbbacf64c829fc50ee9ed3faf0d8095b6dc4b8c17fc` | OK（=FROZEN） |
| Arch 设计确认 | 23886baa… | `23886baac3edbbf0975d257a3126ba05396365c275ba85c684e98b9ecc1c6fa2` | OK |
| tier1_materialize.py | 2af28a69… | `2af28a69ddfbe914df634e113960c44f3ee9eb62f9998521d34abf366cd60204` | OK |
| daily_basic_incremental.py | a6049095… | `a60490956b4ffd268dd0cf9c98b204f7cd8fd459bc79d8e762c49ed8c4fe1159` | OK |
| fund_portfolio_stream_merge.py | 374489d0… | `374489d0907d10b8464f9344f79ea127fb960494de0ac5ff7f44905cb5115cec` | OK（未动） |
| nightly_update.py live | ec079d56… | `ec079d56912aea8a4358a7ae97a73a3ad6ee3df34e83845ad4d655d31d838636` | OK（=归档，未改） |
| 归档 tier1 | e9c89a6c… | `e9c89a6c3a0719d9b78064404f2b7d66a7076430f5676e65335db06efae1c3bb` | OK |
| DIFF_C1_C12_ZH.md | e7154df7… | `e7154df73aad4ca5771c3e0ddc9a929c12091374d6870ed93f30dbf2205f2714` | OK |
| SELFTEST_RECEIPT_ZH.md | 862e62d4… | `862e62d4cc69ea6fbdbc84d0b07259136e98bb5e40c69c3aaebbbc3da4ac6de9` | OK |
| ENG_TRANSFORM_SHA_PROPOSAL_ZH.md | eef349f9… | `eef349f9b22243d29eacec602d8687d0625406e45f4062c06f197d0bdc240724` | OK |
| transform_sha（本环境复算） | 308b5054… | `308b5054c39801116fd0eb19b4e4bd10bdccd4b4d40bfb67dd06a58fa67ab974` | OK |
| SELFTEST_RESULTS.json | （未钉） | `2f2e52d6f5d0cf0f5eedb3571cd74bc58a8fb5fd72e3ca12be2851152e6800ab` | 记录；n_pass=13 |

## C1–C12 实现核对

| ID | 状态 | 挡谁 | 证据要点 |
|---|---|---|---|
| C1 | **CLOSED** | — | `RAW_NAME_RE=^\d{8}\.parquet$` L35；`_select_raw_files`；`_year_has_tmp`→27；自测 C1 rc=27 |
| C2 | **CLOSED** | — | `DbIncrSignal`；SIGHUP→32 不重发；SIGTERM 清理后重杀→−15；自测 A16 rc=32 |
| C3 | **CLOSED** | — | `compute_transform_sha` AST dump+常量表；runtime_versions 独立；错钉→28；自测 rc=28 |
| C4 | **CLOSED** | — | 模块级 `transform_daily_basic_one` L169；`materialize_daily_basic` 改调；A14 三文件 22 列 hash ok |
| C5 | **CLOSED** | — | except 入口 SIGTERM/SIGHUP→SIG_IGN L805–806，再回滚 |
| C6 | **CLOSED** | — | O_CREAT\|O_EXCL + 立刻 fstat inode；再 path 开 ParquetWriter（披露：fd 直交 Writer 在 pyarrow26 留 0 字节）；自测 O_EXCL+inode PASS |
| C7 | **DEFERRED** | **enable** | handler/回滚路径有；五阶段 TERM≤5s（A15）未测 |
| C8 | **DEFERRED** | **enable** | `dest_sha!=build.new_sha256`→20（A18 路径）；缺 `new_sha256` 时不触发；专用夹具未跑；基线仍须 ref_build |
| C9 | **DEFERRED** | **enable** | `ref_build_year`+VmHWM guard 有；scaled 18k PASS；满配 1.3M 未测 |
| C10 | **CLOSED** | — | 快筛含 st_ctime_ns；raw_touched / `QL_DB_RAW_FULL_SHA_REQUIRED`→content；A17 PASS（.ok 键 raw_full_sha_required 待启用包接线） |
| C11 | **CLOSED** | — | pending→STALE_TMP→precheck；自测 stale_tmp rc=21 |
| C12 | **CLOSED** | — | 秒级 bak 名；os.link 失败撤回；成品仅 os.replace；自测 hardlink PASS（DIFF 行号 L554 笔误，实锚 L593） |

**汇总：CLOSED 9 / DEFERRED 3 / OPEN 0**（相对 C1–C12）。另有非 C 编号残留见 P1。

## 自测与生产隔离

- 工作目录：`/tmp/ql_db_incr_test_*`（RESULTS.work 已核）
- 13/13 ok=True；进程末 VmHWM 回执 177296 kB
- A7：生产 valuation 6 文件现盘 sha = 库存；自测未写生产
- runtime_versions：python 3.13.5 / pandas 3.0.6 / pyarrow 26.0.0 / numpy 2.5.4

## transform_sha 裁示（Arch）

**接受** Eng 提案（`ENG_TRANSFORM_SHA_PROPOSAL_ZH.md`）：

1. `ast.dump(..., include_attributes=False, indent=None)` — **Yes**（抗 lineno/格式化）。
2. 函数集仅 `transform_daily_basic_one` + `to_iid` + `_daily_basic_val_cols` + `TRANSFORM_CONSTANTS`（json sort_keys compact）— **Yes**；**不含** `_compare_daily_basic_history` / history_diff。
3. 去 docstring + `fix_missing_locations` — **Yes**。
4. 废止「inspect.getsource 去行尾空白再 sha」— **Yes**（与设计 C3 一致）。
5. `runtime_versions` 独立字段，与 transform_sha **同退码 28** 但不同键 — **Yes**。

**钉值（本仓库当前 tier1 字节）：**  
`transform_sha = 308b5054c39801116fd0eb19b4e4bd10bdccd4b4d40bfb67dd06a58fa67ab974`  
（Arch 本机复算与 Eng 一致；随上述三函数或常量表变更而失效，须重算重钉。）

建议写入设计 §2.7 补丁段或 v3.2 时照抄本裁示；**不在今晚改冻结设计字节**。

### 启用 .ok 应如何钉该键

启用 .ok（另签，非今晚）至少钉：

- `transform_sha`: `308b5054c39801116fd0eb19b4e4bd10bdccd4b4d40bfb67dd06a58fa67ab974`
- `path_incr` / `incr_sha256`: `scripts/acquire/daily_basic_incremental.py` / `a60490956b4ffd268dd0cf9c98b204f7cd8fd459bc79d8e762c49ed8c4fe1159`
- `path_tier1` / `tier1_sha256`: `scripts/acquire/tier1_materialize.py` / `2af28a69ddfbe914df634e113960c44f3ee9eb62f9998521d34abf366cd60204`
- `design_sha256` / `design_review_sha256` / `impl_review_sha256`
- `allow_enable`: true（仅当启用包门禁齐：A13/A15/A18、§2.8/§2.9 非 stub、驱动重钉）
- 生产环境**禁止**设置：`QL_DB_INCR_ALLOW_STALE_SHA`、`QL_DB_INCR_LOOSE_READBACK`、`QL_DB_ALLOW_FULL`（除非另签 full 路径）

## 残留（进启用核对清单）

1. §2.8 物理序列 hash 回读未实现（仅行数）。
2. §2.9 history_diff 为 stub（整表加载）——生产规模有 RSS 风险。
3. C7/A15、C9/A13 满配、C8/A18 专用夹具、S1–S13 全集。
4. nightly_update CLI 改增量、全量路径 `QL_DB_ALLOW_FULL`+原子 manifest、驱动 f99dd11a 重钉 — 属启用包。
5. `_recover_pending` L345 `os.replace(...) if False` 死代码（P3 清洁项）。
6. DIFF C12 声称行号 L554 实为 hist 报告戳；bak 在 L593（P3）。

## 实现审阅 .ok 建议键（父会话签发；本文不创建 .ok）

- `kind` / `auth_type`: `impl_review`
- `path_incr`: `scripts/acquire/daily_basic_incremental.py`
- `incr_sha256`: `a60490956b4ffd268dd0cf9c98b204f7cd8fd459bc79d8e762c49ed8c4fe1159`
- `path_tier1`: `scripts/acquire/tier1_materialize.py`
- `tier1_sha256`: `2af28a69ddfbe914df634e113960c44f3ee9eb62f9998521d34abf366cd60204`
- `transform_sha`: `308b5054c39801116fd0eb19b4e4bd10bdccd4b4d40bfb67dd06a58fa67ab974`
- `receipt_sha256`: `862e62d4cc69ea6fbdbc84d0b07259136e98bb5e40c69c3aaebbbc3da4ac6de9`
- `diff_sha256`: `e7154df73aad4ca5771c3e0ddc9a929c12091374d6870ed93f30dbf2205f2714`
- `proposal_sha256`: `eef349f9b22243d29eacec602d8687d0625406e45f4062c06f197d0bdc240724`
- `design_sha256`: `5c6a3a1dcc0fdcba279cafbbacf64c829fc50ee9ed3faf0d8095b6dc4b8c17fc`
- `design_review_sha256`: `23886baac3edbbf0975d257a3126ba05396365c275ba85c684e98b9ecc1c6fa2`
- `impl_review_sha256`: （签发时填本审查文 sha256）
- `allow_enable`: **false**
- `allow_run`: **false**
- `live`: false
- `promotion_approved`: false
- `single_use`: true（若团队惯用）
- `note`: 启用另签；须先闭合 P1（§2.8/§2.9 非 stub、A13、A15、A18）并重钉驱动

## P0 / P1 / P2

- **P0：** 无
- **P1：** §2.8/§2.9 stub；C7/A15；C9/A13 满配 —— 均**挡启用**
- **P2：** C8/A18 夹具与缺 `new_sha256` 时门闩；raw_full_sha_required 仅 env 未接 .ok

## 下一步

1. **父会话**：可选签实现审阅 .ok（上表键；allow_enable=false）。**今晚不签 enable/run。**
2. **Eng**：启用前替换 history_diff/readback stub；补 A13/A15/A18；交启用包 diff。
3. **Data**：叶25 窗与补跑纪律不变；增量启用仍走完整门禁。

（完）
