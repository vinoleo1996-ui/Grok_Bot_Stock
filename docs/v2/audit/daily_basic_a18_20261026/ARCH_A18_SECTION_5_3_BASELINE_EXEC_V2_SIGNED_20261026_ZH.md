# Arch SIGNED：A18 §5.3 引导基线 **EXEC_V2** `.ok`

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻（America/New_York） | `2026-10-26T18:24:45-04:00`（墙钟 2026-10-26 18:24–18:25 ET） |
| **状态** | **SIGNED**（执行授权 EXEC_V2；not_before=18:25） |
| `.ok` | `output/data/ARCH_RUN_AUTH_DAILY_BASIC_A18_SECTION_5_3_BASELINE_EXEC_V2.ok` |
| `.ok` sha8 / 全长 | **`a62881b9`** / `a62881b9f9078cf3df8b3fc992be999701ff562cfacc29a76e98fdb789c06ec6` |
| 主审（dest 同构复审） | `ARCH_A18_SECTION_5_3_DEST_ISOMORPH_REVIEW_20261026_ZH.md` sha8 **`0815e13f`** / 全长 `0815e13f4559db9bc99112dad91017692e76319e07d214529c76089d34f1fb53` |
| 继承原审 | sha8 **`232a2295`** / 全长 `232a229583ae602520861e2bcad72c3a08aca3d8ce4f103a8636f561cb486dbb` |
| 口径判 | **`6466c490`** HASH_CALIBER_BUG（已由 v2 dest 月累加同构修） |
| A9 归档旧 EXEC | **`f28183e0`**（旧票 `6de02e74` live ABSENT） |
| driver_v2 | `a18_s53_driver_v2_dest_monthly.py` **`af15b52d`** / `af15b52dbd54ed52216b41891f29a833cd13084f9c21512ca1fe01389e622deb` |
| helper | `a18_s53_year_sorted_content_col_hashes_helper.py` **`3094f0b6`** / `3094f0b60fa721922489b5ea21b1e7c4ca29b1b7d2bb8b65288b80b22fa9ab02` |
| Eng DIFF / 回执 / 2014 proof | **`dbff641d`** / **`8bbcf874`** / **`2cc3e356`** |
| 废止旧票 | sha8 **`6de02e74`**（A9_RECONCILE_FAIL；`_consumed/…EXEC.6de02e74…`；**禁复用**） |
| 签窗 | **2026-10-26 18:25–23:00 ET**（not_before=18:25；expires=**23:02**） |
| QUIET | **已挂** `output/loop/RESEARCH_QUIET.lock` holder=`a18_s53_v2` sha8 **`bf4548d4`** / `bf4548d48a8eb16c1cfc45d6f7d5245b45ed4cd60808faf0d8f8bcd8f34a57dd`；do_not_lift_until_arch_or_consumed=true |
| live / promotion | false / false |
| ≠ | seed / allow_run / 物化 / enable `4377eb59` / 旧 EXEC `6de02e74` / `a158f17a` / 叶30 `5ae077fa` RESTORED / X2 / 盲 seed / 代码 bootstrap / 代跑 |

## 签前门禁（本签）

| 项 | 结果 |
|---|---|
| dest 复审 sha 仍 `0815e13f` PASS_WITH_CONDITIONS | **PASS** |
| driver_v2 `af15b52d` / helper `3094f0b6` | **PASS**（复算 MATCH） |
| dest pin `f6bbf9e5` / manifest `8c2c978b` | **PASS**（本签复算 MATCH；未改生产） |
| incr `a7ac54b3` UNTOUCHED | **PASS** |
| baseline ABSENT | **PASS** |
| 叶30 VOID `ff30406f`；`.ok` `5ae077fa` live ABSENT；QUIET lift `821fd5b3` live ABSENT | **PASS** |
| 无 a18/ref_build/leaf30/daily_basic 重进程 | **PASS**（pgrep 空） |
| MemAvailable 充足（≈9.1 Gi） | **PASS** |
| 签前 QUIET ABSENT → 本签新建 holder=a18_s53_v2 | **PASS** |
| 禁复用 `6de02e74`/`4377eb59`/`a158f17a`/`5ae077fa` 及 RESTORED/VOID 习惯集 | **钉入** |
| 未触叶30 `_consumed` | **未触碰** |

## 授权边界（复述）

- allow_ref_build=**true**（驱动钉 v2 dest 月累加同构；YEARS=2014..2026；END=`20261016`；OUT_TMP=`/tmp/a18_s53_v2_<ts>_<pid>`；单进程逐年）
- dest_monthly_isomorph=**true**；forbid_year_once_dig_dest=**true**
- allow_write_baseline=**true**（**仅**对账一致时原子写 `build_baseline.json`）
- allow_write_baseline_on_mismatch=**false**（A9）
- allow_read_dest_for_reconcile=**true**
- allow_write_production_parquet / allow_write_manifest / allow_seed / allow_materialize / allow_run / allow_backfill / allow_enable = **false**
- A13 VmHWM ≤ 1,000,000 kB
- single_use=true；archive_by=Arch only
- **Arch 不代跑**；≠X2 ACCEPT；≠Book-Smoke

## 请主

1. MATCH 本 EXEC_V2 `.ok` sha8 **`a62881b9`** + QUIET **`bf4548d4`** + 本回执
2. 令 Eng ≥**18:25 ET** 用 driver_v2 **`af15b52d`** + helper **`3094f0b6`** 开跑（窗至 23:00；expires 23:02）
3. Eng 仍 HOLD 至 MATCH；消费后由 Arch 归档/lift QUIET

≠X2；不报 Leo；live=false。

---
文档结束（Arch A18 §5.3 EXEC_V2 SIGNED）
