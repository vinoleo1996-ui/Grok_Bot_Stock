# Arch 复审：A18 §5.3 dest `year_sorted_content_col_hashes` 月累加同构清单（只审不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行手） |
| 时刻（America/New_York） | `2026-10-26T18:17:08-04:00`（墙钟 2026-10-26 18:17 ET） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 本回合动作 | **不签**任何新 `.ok`；**不代跑** §5.3；**不 lift** 叶30 QUIET；**不触** 叶30 `.ok`；不复用 `6de02e74`/`4377eb59`；不 seed / allow_run / 物化 / 写 baseline；不改生产 parquet·manifest·incr；live=false；**不报 Leo** |
| 触发 | 主令 A18 §5.3 复审 Eng dest 同构清单（对照审 `232a2295` §3.1 / 判 `6466c490`） |
| 依据判稿 | **HASH_CALIBER_BUG** sha8 **`6466c490`**；A9 archive **`f28183e0`**（EXEC `6de02e74` live ABSENT） |

## 0. 一句话

Eng 侧草稿 helper + v2 驱动把 dest 侧从「整年一次 dig」改为与 `ref_build_year` **同构的月累加**；本机对照 incr `a7ac54b3` 月循环 **锁步 MATCH**；2014 钉测相对 OUT_TMP `ref_year_2014.json` **22/22 + stub + rows MATCH**（复算确认）。A9 仍钉；生产未动；叶30 QUIET/`.ok` **未触**。结论 **PASS_WITH_CONDITIONS**：**可另签新窗**用 v2 驱动全量重跑，但须等叶30 QUIET 自然 ABSENT、另签新 `.ok`、全窗 2014..2026 对账、A9/A13 仍硬闸。

## 1. 钉表再核（本机 sha256）

| 件 | 路径 | 期望 sha8 | 实测 | 结果 |
|---|---|---|---|---|
| DIFF | `docs/v2/audit/daily_basic_a18_20261026/ENG_A18_SECTION_5_3_DEST_HASH_ISOMORPH_DIFF_20261026_ZH.md` | `dbff641d` | `dbff641dfee72b9f4b7a473fbaf13a3795147d04caf123182b47018c6d884e83` | **MATCH** |
| Eng 回执 | `…/ENG_A18_SECTION_5_3_DEST_HASH_ISOMORPH_RECEIPT_20261026_ZH.md` | `8bbcf874` | `8bbcf87458d9c476ee10ddec8cb34f19445238c3e9882657bf84276fd06571f3` | **MATCH** |
| driver v2 | `…/a18_s53_driver_v2_dest_monthly.py` | `af15b52d` | `af15b52dbd54ed52216b41891f29a833cd13084f9c21512ca1fe01389e622deb` | **MATCH** |
| helper | `…/a18_s53_year_sorted_content_col_hashes_helper.py` | `3094f0b6` | `3094f0b60fa721922489b5ea21b1e7c4ca29b1b7d2bb8b65288b80b22fa9ab02` | **MATCH** |
| 2014 proof | `…/ENG_A18_SECTION_5_3_DEST_HASH_ISOMORPH_PIN_2014_PROOF.json` | `2cc3e356` | `2cc3e3568a33c7e6283561942fef66b96f4e0ae95a237ce43e3c0f05494a4b5f` | **MATCH** |
| 原审 | `…/ARCH_A18_SECTION_5_3_BASELINE_REVIEW_20261026_ZH.md` | `232a2295` | `232a229583ae602520861e2bcad72c3a08aca3d8ce4f103a8636f561cb486dbb` | **MATCH** |
| 口径判 | `…/ARCH_A18_SECTION_5_3_HASH_CALIBER_JUDGE_20261026_ZH.md` | `6466c490` | `6466c4905c74fc8aea6a82d94fc77807e72dae9fc74b7638d9bf87f6c63a8abb` | **MATCH** |
| A9 archive | `…/ARCH_A18_SECTION_5_3_A9_ARCHIVE_20261026_ZH.md` | `f28183e0` | `f28183e0e749f86c116bfee2ef9af72a6b32c87413216f0d906fc86610ed1cd0` | **MATCH** |
| 前序 A9 D1 | `…/ENG_A18_SECTION_5_3_BASELINE_RECEIPT_20261026_ZH.md` | `09c1b2c8` | `09c1b2c8bf6cf7678d727f9a6c39139314806bbd96f21314cc4bed916addc751` | **MATCH** |
| 生产 incr | `scripts/acquire/daily_basic_incremental.py` | `a7ac54b3` | `a7ac54b3ecdf33d338710df5c96f447fbec51affdcfbf167fb3e00648f678dd8`；mtime `2026-10-25 01:17 ET`（早于本 DIFF） | **UNTOUCHED MATCH** |
| dest / man | parquet / manifest | `f6bbf9e5` / `8c2c978b` | 复算 MATCH；mtime 均 `2026-10-25` | **UNTOUCHED MATCH** |
| baseline | `data/v2/valuation/daily_basic_full_tushare_build_baseline.json` | ABSENT | **ABSENT** | **MATCH** |
| live EXEC `.ok` | `output/data/ARCH_RUN_AUTH_DAILY_BASIC_A18_SECTION_5_3_BASELINE_EXEC.ok` | ABSENT | **ABSENT**（`_consumed/…6de02e74…A9_RECONCILE_FAIL…` 仍在；本审未动） | **MATCH** |
| 叶30 QUIET | `output/loop/RESEARCH_QUIET.lock` | `e6180a7a`（禁 lift） | `e6180a7a…`；mtime `18:11:42 ET`；本审前后同钉 | **未触** |
| 叶30 `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF30_CRR_CFOOE_VOLPEN_ALPHA_BUILD_HILIQ_X2.ok` | `5ae077fa`（禁动） | `5ae077fa…`；mtime `18:11:42 ET`；本审前后同钉 | **未触** |

`py_compile` helper+driver：**PASS**（侧草稿；本审未改字节）。

## 2. 审点（对照判稿 §2.3 / 修法要点 + 原审 §3.1）

### 2.1 dest 侧是否与 `ref_build_year` 月累加同构 — **PASS**

| 步骤 | `ref_build_year`（incr `a7ac54b3` L1227–1264） | helper `3094f0b6` + driver v2 dest 路径 | 结果 |
|---|---|---|---|
| 月切 | `for m in sorted(by_m)` | `for m in sorted(months.unique())`（`trade_date.month`） | **同构** |
| 月内去重/排序 | `drop_duplicates(ts_code,trade_date,keep=last)` → `sort_values([trade_date,ts_code])` | 同 | **同构** |
| Arrow | `pa.Table.from_pandas(chunk, preserve_index=False)` | 同 | **同构** |
| 外层 header | 首月 once：`name+\0+arrow_type+\0`（dtype=该月 from_pandas） | 同（消旧 dest「dtype 取 round-trip 前 tbl」瑕疵） | **同构 + 修次要瑕疵** |
| 物理 dig | 每月 `_row_group_physical_col_hashes(tbl)` → `update(bytes.fromhex(dig))` | 同（注入 `dbi._row_group_physical_col_hashes`） | **同构** |
| stub | `ts_code,trade_date\n` + 行流 | 同 | **同构** |
| 内存 | `del` + `release_unused` | 同 | **同构** |
| 旧 bug | — | 旧 `/tmp/a18_s53_driver.py`：整年一次 dig（已弃） | **已替换** |

权威公式现为两侧一致：

`H( header ‖ dig(m1) ‖ … ‖ dig(m12) )`

双重 header（外层 + physical 内嵌）**保持与 ref 同构**（判稿 §4 次要项；本票不单独改 ref）— **接受**。

### 2.2 helper 与 ref/dest 共用序列化/排序/空值口径 — **PASS**

- 排序键 / keep=last / `str(td)[:10]` stub 截断 / `from_pandas(preserve_index=False)` / physical 函数本体（incr 内，未改）均与 ref 同源。
- driver 对账列集合 = `TRANSFORM_CONSTANTS["out_cols"]`；并新增 stub 对账（优于旧 §3.1 驱动未写 dest_stub）。
- 年级预去重再按月切：跨月 `(ts_code,trade_date)` 不可能重复 → 与月内去重等价；2014 内容/stub 已证。

### 2.3 2014 proof 22/22 — **PASS**（支撑口径；**不**替代全窗）

| 检查 | 结果 |
|---|---|
| proof 自证 | `all_match=true`；`mismatched_cols=[]`；`match_count=22`；method=`year_dedupe_sort_then_groupby_month_header_once_monthly_physical` |
| 本机复算 vs OUT_TMP `/tmp/a18_s53_20261026T175303_2902093/ref_year_2014.json` | dest_ysch **22/22 MATCH**；stub **MATCH** `02bb7e21…`；rows **570677=570677** |
| 足以定口径？ | **是**（关闭 HASH_CALIBER_BUG 修法） |
| 足以免全窗重跑？ | **否** → CONDITIONS C3 |

### 2.4 A9 禁区 — **仍有效 PASS**

v2 驱动 L246–253：`reconcile.ok` 为 false → 写 `DIFFS.json`、打印 `baseline_NOT_written A9`、`return 9`；**仅** ok 时 `os.replace` 写 baseline。禁盲 seed / allow_run / 物化 / 带病 baseline：DIFF/回执/驱动注释均复述；本审未违。

### 2.5 禁复用票 / 单进程逐年 / OUT_TMP / rss·a13 — **PASS（签文须再钉）**

- 驱动无引用 `6de02e74`/`4377eb59`；pin 校验 dest/man/incr；transform `308b5054`；END=`20261016`；YEARS=2014..2026。
- `ref_build_year` **逐年单进程**循环；OUT_TMP 默认 `/tmp/a18_s53_v2_<ts>_<pid>`（或环境变量）。
- A13：`A13_LIMIT_KB=1_000_000`；`a13_ok = peak_all <= limit`（记入 reconcile；前次峰 260192）。
- 叶25 窗 16:15–17:45 仍 abort（旁证；叶25 已 CONSUMED，保留无害）。

### 2.6 生产 parquet/manifest/incr 未被本 DIFF 改动 — **PASS**

incr/dest/man mtime 均 `2026-10-25`；DIFF mtime `2026-10-26 18:14`；incr sha 仍 `a7ac54b3`；baseline ABSENT；交付物均在 audit pack。

### 2.7 叶30 线隔离 — **PASS（本拍遵守）**

本审**零字节**改 `RESEARCH_QUIET.lock`（`e6180a7a`）与叶30 `.ok`（`5ae077fa`）；审前/审后 mtime 同 `18:11:42 ET`。现场可见 leaf30 真跑进程（rss_sampler + `leaf30_crr…r1.py`）— **勿抢窗**。

## 3. CONDITIONS（须主签窗时钉入）

| ID | 条件 | 理由 |
|---|---|---|
| **C1** | 新窗 Eng 开跑前：**叶30 QUIET 须已自然 ABSENT**；**禁** Arch/Eng lift `e6180a7a`；**禁**动 `.ok` `5ae077fa` | 叶30 PRIMARY 在跑；原 §3.0 空档门遇 QUIET 应停，不得误当 hung 清掉 |
| **C2** | **另签新** `.ok`（建议名 `ARCH_RUN_AUTH_DAILY_BASIC_A18_SECTION_5_3_BASELINE_EXEC_V2.ok`）；**禁**复用 `6de02e74`（含 `_consumed`）/ enable `4377eb59` / 任何 RESTORED/VOID 旧票 | single_use；A9 已归档 |
| **C3** | 新窗必须 **全量** 2014..2026 ref_build + dest 月同构对账；2014 钉测**只**证明口径，**不**免全窗 | 其余年同图案高概率，但仍须 A9 实跑 |
| **C4** | A9 仍硬闸（不一致不写 baseline）；A13 VmHWM≤1,000,000 kB；单进程逐年；中间只写 OUT_TMP；禁 seed/allow_run/物化/改 parquet·manifest | 设计/原审未变 |
| **C5** | 签文挂空档门：无 a18/ref_build/daily_basic 重进程；baseline ABSENT；**非**叶25 16:15–17:45；QUIET ABSENT（C1）；驱动钉 v2+helper sha | 替代旧 `/tmp/a18_s53_driver.py` |

非阻塞旁证：Eng 回执 §5 纸面 SW 披露覆写 — **本审未核**；≠本票范围。

## 4. 建议新窗 CLI / 驱动钉（PASS 路径；供主另签）

**驱动钉**

| 钉 | 值 |
|---|---|
| driver | `docs/v2/audit/daily_basic_a18_20261026/a18_s53_driver_v2_dest_monthly.py` sha8 **`af15b52d`**（全长 `af15b52d…622deb`） |
| helper | 同目录 `a18_s53_year_sorted_content_col_hashes_helper.py` sha8 **`3094f0b6`** |
| incr / transform | `a7ac54b3` / `308b5054`（驱动内 pin） |
| dest / man | `f6bbf9e5` / `8c2c978b` |
| END | `20261016` |
| YEARS | `2014..2026` |
| OUT_TMP | `/tmp/a18_s53_v2_<YYYYMMDDTHHMMSS>_<pid>`（或 `OUT_TMP=` 注入） |
| dest_hash_caliber | `monthly_accumulate_isomorphic_ref_build_year_v2`（驱动写入 reconcile） |
| 对照审/判/本审 | `232a2295` / `6466c490` / 本回执 sha8（落盘后） |
| A9 / A13 | 不一致不写；peak≤1e6 kB |
| 禁复用 | `6de02e74` / `4377eb59` |

**建议 CLI（签后 Eng；QUIET 已 ABSENT）**

```bash
# === A18 §5.3 GUIDE BASELINE V2 (America/New_York) ===
set -euo pipefail
cd /workspace/QuantLab
HHMM=$(date '+%H%M')
if [ "$HHMM" -ge 1615 ] && [ "$HHMM" -lt 1745 ]; then
  echo "ABORT: leaf25 window"; exit 2
fi
test ! -e output/loop/RESEARCH_QUIET.lock || { echo "ABORT: QUIET present (wait leaf30; do NOT lift)"; exit 2; }
test ! -e data/v2/valuation/daily_basic_full_tushare_build_baseline.json \
  || { echo "ABORT: baseline exists"; exit 2; }
if pgrep -af 'a18_s53|ref_build_year|daily_basic_incremental|materialize|run_nightly' \
  | grep -vE 'pgrep|rg |grep |leaf30'; then
  echo "ABORT: data/ref process present"; exit 2
fi
test "$(sha256sum docs/v2/audit/daily_basic_a18_20261026/a18_s53_driver_v2_dest_monthly.py | cut -c1-8)" = "af15b52d"
test "$(sha256sum docs/v2/audit/daily_basic_a18_20261026/a18_s53_year_sorted_content_col_hashes_helper.py | cut -c1-8)" = "3094f0b6"
OUT_TMP=/tmp/a18_s53_v2_$(date +%Y%m%dT%H%M%S)_$$
export OUT_TMP
PYTHONPATH=scripts/acquire:docs/v2/audit/daily_basic_a18_20261026 \
  python3 docs/v2/audit/daily_basic_a18_20261026/a18_s53_driver_v2_dest_monthly.py
# expect: BASELINE_WRITTEN … 或 RECONCILE_FAIL … A9（rc=9）；禁盲写
```

**Arch 本拍不签、不代跑。** 请主 MATCH 本审 → 排独立签窗（错开叶30）→ 新 `.ok` → 令 Eng。

## 5. 禁区复述

不签新 `.ok`；不代跑 §5.3；不 lift 叶30 QUIET；不动叶30 `.ok`；不复用 `6de02e74`/`4377eb59`；不 seed / allow_run / 物化 / 带病 baseline；不改生产；不报 Leo。live=false。

---
文档结束（Arch A18 §5.3 DEST_ISOMORPH_REVIEW）
