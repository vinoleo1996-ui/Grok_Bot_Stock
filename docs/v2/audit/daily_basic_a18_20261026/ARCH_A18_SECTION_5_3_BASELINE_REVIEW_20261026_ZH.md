# Arch 审结：A18 §5.3 引导基线（只审不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行手） |
| 时刻（America/New_York） | `2026-10-26T14:29:14-04:00`（墙钟 2026-10-26 14:29 ET） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 本回合动作 | **不签**任何 live `.ok`；不写生产 parquet/manifest/baseline；不跑 ref_build / 物化 / seed；不复用 enable `4377eb59`；勿动叶25 CONSUMED `.ok`；**不** SendToAgent / SendToUser；live=false；promotion=false；≠X2 |
| 触发 | 主令 A18 §5.2 盘点 PASS → 审 §5.3（方案 A 下一步；另票）；Data 回执 sha8 **`b21066a1`**；Eng dig sha8 **`bd188832`** |
| 设计钉 | `docs/v2/DATA_DAILY_BASIC_INCREMENTAL_DESIGN_v3_1_ZH.md` sha **`5c6a3a1d…`**（§5.3 / §4.1 / §4.1b / §4.2 / C8 / 决定(e) / A9 / A13 / A18 / D4） |

## 0. 一句话

Data §5.2 **PASS MATCH**（残留无；baseline ABSENT；has_build=false）；设计/dig/现场钉 **全部复算 MATCH**；无真实数据进程；QUIET 无；live `.ok`=0。审计树内 **无** Eng/Data 交来的正式 §5.3 命令清单 → **本审新建**（真实 raw、输出 `/tmp`、单进程逐年、§4.2 对账、一致才原子写 baseline、不一致不写并列差异 A9）。结论 **PASS_WITH_CONDITIONS**：可排签 §5.3 引导基线 `.ok`，但须主排窗（**错开叶25 16:15–17:45**）+ 签文禁 seed/allow_run/物化/改 parquet·manifest；**本回合未签发 `.ok`**。

## 1. 依据精读（本审）

| 源 | 要点 | 结果 |
|---|---|---|
| 设计 §5.3 | 单独签 `.ok`；C8/决定(e)：新表+过时 manifest **两边都不信**；基线**只能**由 ref_build 全年份对账产生；对账不一致 → **不写基线、不启用增量**（A18/A9） | **采纳为签文硬闸** |
| 设计 §5.3 执行边界 | 前提=§5.2 无未处理残留；只读成品元数据 + ref_build 2014..Y（**真实 raw**、只读、输出 **`/tmp`**、空档、**单进程逐年**）；原子写 `build_baseline.json`（成品 sha / rows_by_year / row_groups_by_year / **year_sorted_content_col_hashes**(D4) / schema / transform_sha / runtime_versions / 内容 sha 版 raw_inventory / 对账结果） | **写进拟命令清单** |
| 设计 §4.1 / §4.1b | ref_build=模块级 `_one`+月循环；不写成品；A13 VmHWM ≤ 1,000,000 kB（C9） | **签文钉 A13；超线不得签后续** |
| 设计 §4.2 / D4 | 逐年行数+rg 序列；year_sorted_content_col_hashes（排序内容 hash）；file_physical_row_hash；null/NaN；不变量；schema；文件 sha 只记录不作一致标准；不一致按月定位 | **对账规格钉入清单** |
| 设计 §5.2 前提 | Data 盘点无未处理残留 | **已满足**（回执 `b21066a1` PASS） |
| 设计 §5.4 / §6.1 | 首晚对基线成品 sha；顺序 …→§5.2→**§5.3**→…→另签 enable；本票 ≠ seed `manifest.build` ≠ allow_run | **本票只到写 baseline；种子/allow_run 另票** |
| C8 / 决定(e) / A18 | 两边都不信；无合格基线 → incr exit 20；拒盲 seed（B）；拒代码 bootstrap（C） | **复述有效** |
| Dig 方案 A 步骤3–4 | 3) Arch 签 §5.3；4) Eng 跑 ref_build，一致则原子写 baseline | **本审 = 步骤3 的审稿**；步骤4 等主排签后执行 |
| Dig / Data / 设计 sha8 | dig `bd188832`；Data `b21066a1`；设计 `5c6a3a1d`；§5.2 审 `abe5a3c5`；SIGNED `40304dda`；`.ok` `dc51a0b3` | **本机复算全部 MATCH** |

### 1.1 命令清单来源

- 搜 `docs/v2/audit/daily_basic_a18_20261026/` 与相关 nightly/enable 包：**无** Data/Eng 交来的正式「§5.3 引导基线命令清单」草案。
- Dig 仅原则性列举（真实 raw、`/tmp`、单进程逐年、§4.2、一致写 baseline），**不足**作可执行签文附件。
- **本审新建**完整可复制命令清单（见 §3 / §3.1）；签 `.ok` 时须钉本审稿 sha8。

## 2. 现场只读核盘（本机；与 Data/dig 对齐；未改生产；未跑 ref_build）

| 项 | 期望 | 实测 | 结果 |
|---|---|---|---|
| Data §5.2 回执 | sha8 `b21066a1` PASS | 全长 `b21066a18c2ef72907fa00f3bdfae8e6b519b41c4e1912adf5dc833d2a3faad5`；结论 PASS；残留无 | **MATCH** |
| §5.2 `.ok` | sha8 `dc51a0b3` | `dc51a0b30fdddbbf94234ad346ec15a180bd5b256d5772cdf1c4fc24efcc68ed`；窗 14:15–16:00；allow_ref_build=false | **MATCH** |
| §5.2 审 / SIGNED | `abe5a3c5` / `40304dda` | 复算 MATCH | **MATCH** |
| Eng dig | sha8 `bd188832` | 全长 `bd1888328bcedcb5a90b071b81207fe02b38f3b4c1d6adef85fb5b0fea9188c9` | **MATCH** |
| 设计 v3.1 | sha8 `5c6a3a1d` | 全长 `5c6a3a1dcc0fdcba279cafbbacf64c829fc50ee9ed3faf0d8095b6dc4b8c17fc` | **MATCH** |
| dest | sha8 `f6bbf9e5` | `f6bbf9e51af78dfab2c021fa8809c58ad0d36df7293f8a488200b9dd5ceaf948`；size=745129744 | **MATCH** |
| manifest | sha8 `8c2c978b`；无 `build` | `8c2c978b384e8d3206da0876686fa214d7960353f472e81151a7acc3b0c74ac8`；has_build=false；rows=12309945；date_max=`2026-10-16` | **MATCH** |
| `build_baseline.json` | ABSENT | **ABSENT** | **MATCH** |
| pending / quarantine / tmp / parts / raw `*.tmp.parquet` | 无（§5.2） | 本审未复扫行；采信 Data PASS + 本审抽检 pgrep/QUIET/baseline | **采信 PASS** |
| 真实数据进程 | 须无 | `pgrep` acquire/nightly/daily_basic/ref_build/materialize/tier1/eng_daily/run_nightly → **空** | **干净** |
| live `.ok` | 0 | `output/ai_factory/*.ok` **空** | **MATCH** |
| QUIET | 无 | `RESEARCH_QUIET.lock` **无** | **MATCH** |
| 叶25 CONSUMED | 勿动 `3c297052`/`d37a157e` | `_consumed/…3c297052.CONSUMED_PASS…ok` 仍在；归档内容 sha8 **`d37a157e`**；本审未改 | **未触碰** |
| 叶25 selfcheck 拟 `.ok` | 未创建；签窗 16:15–17:45 | `ARCH_RUN_AUTH_LEAF25_X2_SELFCHECK_V2_HILIQ_X2.ok` **未创建**；TEAM_STATE 钉 16:15–17:45 | **确认；须错开** |
| enable `.ok` | `4377eb59` allow_run=false；禁复用 | sha=`4377eb592c18c3bed067c9a7dc775330a3d78f811adb6f51f550b0fa54ccbd73`；allow_run/write/backfill=false；expires `2026-10-26T16:37:21-04:00` | **确认；本票不复用** |
| incr / transform / runtime（旁证） | dig 钉 | incr `a7ac54b3…`；transform `308b5054…`；runtime python=3.13.5/pandas=3.0.6/pyarrow=26.0.0/numpy=2.5.4 | **MATCH** |
| raw 跨度（旁证） | 2014..Y | `20140102`..`20261026`；3113 文件；年 2014–2026（13 年） | **旁证** |
| Mem（旁证） | — | MemAvailable≈8.6Gi（审时）；非峰证明 | 旁证 |

**A18 路径判定（本审）**：§5.2 已清残留；manifest **无 `build`** + baseline **ABSENT** → 属方案 A「签 §5.3 → ref_build 定基线」正轨。dig P1-4 提醒：现成品可能早于现行 raw 恢复 → **对账不一致时按 A9 不写 baseline**（不得盲 seed）。

## 3. 拟 §5.3 引导基线命令清单（新建；签后 Eng 原样执行）

**允许**：
- `pgrep` / `stat` / `sha256sum` / `ls` / `find`（只列）
- `python3` + `scripts/acquire/daily_basic_incremental.ref_build_year`（真实 raw；中间结果只写 **`/tmp`**）
- 为 §4.2 对账：按年读 dest 以计算 `year_sorted_content_col_hashes` / 行数 / row group 序列（**仅**对账）
- 对账**完全一致**时：原子写 **仅** `data/v2/valuation/daily_basic_full_tushare_build_baseline.json`
- D1：回执 Python UTF-8+LF 原子写至本审计目录

**禁止**：
- 盲 seed `manifest.build`（方案 B）；改 `_precheck` / 代码 bootstrap（方案 C）
- 复用 enable `.ok` `4377eb59`；写/改 dest parquet；改 manifest；物化 / nightly / incr 实跑；`allow_run` 补缺口
- 并行多进程 ref_build；对账失败仍写 baseline
- 触碰叶25 CONSUMED `3c297052`/`d37a157e`；与叶25 selfcheck **16:15–17:45** 重叠跑重任务
- 本票顺带 seed / enable / 物化

### 3.0 空档门（bash；每次开跑前）

```bash
# === A18 §5.3 GUIDE BASELINE GATES (America/New_York) ===
set -euo pipefail
cd /workspace/QuantLab
HHMM=$(date '+%H%M')
if [ "$HHMM" -ge 1615 ] && [ "$HHMM" -lt 1745 ]; then
  echo "ABORT: inside leaf25 selfcheck window 16:15–17:45 ET"; exit 2
fi
if pgrep -af 'acquire|nightly|daily_basic|ref_build|materialize|tier1_materialize|eng_daily_panels|run_nightly' \
  | grep -vE 'pgrep|rg |grep '; then
  echo "ABORT: real data process present"; exit 2
fi
test ! -e output/loop/RESEARCH_QUIET.lock || { echo "ABORT: QUIET hung"; exit 2; }
test ! -e data/v2/valuation/daily_basic_full_tushare_build_baseline.json \
  || { echo "ABORT: baseline already exists"; exit 2; }
```

### 3.1 权威驱动脚本（Eng 签后执行；写 `/tmp`；一致才写 baseline）

将以下脚本落 `/tmp/a18_s53_driver.py` 后执行：
`OUT_TMP=/tmp/a18_s53_$(date +%Y%m%dT%H%M%S)_$$ PYTHONPATH=scripts/acquire python3 /tmp/a18_s53_driver.py`

```python
# a18_section_5_3_guide_baseline.py — Arch 审新建权威清单
from __future__ import annotations
import hashlib, json, os, sys, time
from pathlib import Path

ROOT = Path("/workspace/QuantLab")
os.chdir(ROOT)
sys.path.insert(0, str(ROOT / "scripts/acquire"))

import pyarrow as pa
import pyarrow.parquet as pq
import daily_basic_incremental as dbi

DEST = ROOT / "data/v2/valuation/daily_basic_full_tushare.parquet"
MAN = ROOT / "data/v2/valuation/daily_basic_full_tushare_manifest.json"
BASE = ROOT / "data/v2/valuation/daily_basic_full_tushare_build_baseline.json"
RAW = ROOT / "data/v2/tushare_raw/daily_basic"
END = "20261016"
YEARS = list(range(2014, 2027))  # 2014..2026
Y0 = YEARS[0]
DEST_PIN = "f6bbf9e51af78dfab2c021fa8809c58ad0d36df7293f8a488200b9dd5ceaf948"
MAN_PIN = "8c2c978b384e8d3206da0876686fa214d7960353f472e81151a7acc3b0c74ac8"
INCR_PIN = "a7ac54b3ecdf33d338710df5c96f447fbec51affdcfbf167fb3e00648f678dd8"
TRANSFORM_PIN = "308b5054c39801116fd0eb19b4e4bd10bdccd4b4d40bfb67dd06a58fa67ab974"
A13_LIMIT_KB = 1_000_000


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def abort(msg: str, code: int = 2) -> None:
    print("ABORT:", msg, file=sys.stderr)
    sys.exit(code)


def main() -> int:
    hhmm = int(time.strftime("%H%M"))
    if 1615 <= hhmm < 1745:
        abort("inside leaf25 selfcheck window 16:15-17:45 ET")
    if BASE.exists():
        abort("baseline already exists; refuse overwrite")
    for label, path, exp in [
        ("dest", DEST, DEST_PIN),
        ("man", MAN, MAN_PIN),
        ("incr", ROOT / "scripts/acquire/daily_basic_incremental.py", INCR_PIN),
    ]:
        got = sha256_file(path)
        if got != exp:
            abort(f"{label} sha mismatch got={got}", 3)
    man = json.loads(MAN.read_text(encoding="utf-8"))
    if "build" in man:
        abort("manifest unexpectedly has build")
    if man.get("date_max") != "2026-10-16":
        abort(f"date_max drift: {man.get('date_max')}")

    tsha = dbi.compute_transform_sha()
    if tsha != TRANSFORM_PIN:
        abort(f"transform_sha drift: {tsha}", 3)
    rt = dbi.runtime_versions()

    out_tmp = Path(os.environ.get("OUT_TMP") or f"/tmp/a18_s53_{time.strftime('%Y%m%dT%H%M%S')}_{os.getpid()}")
    out_tmp.mkdir(parents=True, exist_ok=True)

    ref_by_year = {}
    peak_all = 0
    for y in YEARS:
        print(f"REF_BUILD_YEAR_BEGIN {y}", flush=True)
        r = dbi.ref_build_year(y, RAW, END)
        ref_by_year[str(y)] = r
        peak_all = max(peak_all, int(r.get("peak_vmhwm_kb") or 0))
        (out_tmp / f"ref_year_{y}.json").write_text(
            json.dumps(r, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(
            f"REF_BUILD_YEAR_END {y} rows={r.get('rows')} peak_kb={r.get('peak_vmhwm_kb')}",
            flush=True,
        )

    md = pq.read_metadata(DEST)
    pf = pq.ParquetFile(DEST)
    dest_rows_by_year = {}
    dest_ysch = {}
    dest_rg_by_year = {}
    schema_names = list(md.schema.names)
    try:
        col_idx = schema_names.index("trade_date")
    except ValueError:
        abort("trade_date missing in schema")

    for rg_idx in range(md.num_row_groups):
        rg = md.row_group(rg_idx)
        stats = rg.column(col_idx).statistics
        if stats is None or not stats.has_min_max:
            abort(f"row_group {rg_idx} missing trade_date stats")
        dmin = str(stats.min)[:10]
        dmax = str(stats.max)[:10]
        y0, y1 = int(dmin[:4]), int(dmax[:4])
        if y0 != y1:
            abort(f"row_group {rg_idx} spans years {y0}-{y1}")
        dest_rg_by_year.setdefault(str(y0), []).append(
            {"rg": rg_idx, "num_rows": rg.num_rows, "dmin": dmin, "dmax": dmax}
        )

    for y in YEARS:
        ys = str(y)
        rgs = dest_rg_by_year.get(ys) or []
        tables = [pf.read_row_group(info["rg"]) for info in rgs]
        if not tables:
            dest_rows_by_year[ys] = 0
            dest_ysch[ys] = {}
            continue
        tbl = pa.concat_tables(tables)
        df = tbl.to_pandas()
        df = df.drop_duplicates(["ts_code", "trade_date"], keep="last")
        df = df.sort_values(["trade_date", "ts_code"]).reset_index(drop=True)
        dest_rows_by_year[ys] = int(len(df))
        out_cols = list(dbi.TRANSFORM_CONSTANTS["out_cols"])
        col_hashes = {}
        for c in out_cols:
            if c not in df.columns:
                continue
            col_hashes[c] = hashlib.sha256()
            col_hashes[c].update(c.encode("utf-8"))
            col_hashes[c].update(b"\0")
            if c in tbl.column_names:
                col_hashes[c].update(str(tbl.schema.field(c).type).encode("utf-8"))
            col_hashes[c].update(b"\0")
        tbl2 = pa.Table.from_pandas(df, preserve_index=False)
        ph = dbi._row_group_physical_col_hashes(tbl2)
        for c, dig in ph.items():
            if c not in col_hashes:
                col_hashes[c] = hashlib.sha256()
                col_hashes[c].update(c.encode())
            col_hashes[c].update(bytes.fromhex(dig))
        dest_ysch[ys] = {c: h.hexdigest() for c, h in col_hashes.items()}
        del df, tbl, tbl2, tables, ph

    diffs = []
    for y in YEARS:
        ys = str(y)
        rr = ref_by_year.get(ys) or {}
        r_rows = int(rr.get("rows") or 0)
        d_rows = int(dest_rows_by_year.get(ys) or 0)
        if r_rows != d_rows:
            diffs.append({"year": y, "kind": "rows", "ref": r_rows, "dest": d_rows})
        r_h = rr.get("year_sorted_content_col_hashes") or {}
        d_h = dest_ysch.get(ys) or {}
        for c in sorted(set(r_h) | set(d_h)):
            if r_h.get(c) != d_h.get(c):
                diffs.append(
                    {
                        "year": y,
                        "kind": "year_sorted_content_col_hashes",
                        "col": c,
                        "ref": r_h.get(c),
                        "dest": d_h.get(c),
                    }
                )

    inv = {}
    for p in sorted(RAW.glob("????????.parquet")):
        stem = p.stem
        if stem < f"{Y0}0101" or stem > END:
            continue
        inv[stem] = sha256_file(p)
    inv_blob = json.dumps(inv, sort_keys=True, separators=(",", ":")).encode()
    raw_inventory_sha = hashlib.sha256(inv_blob).hexdigest()
    (out_tmp / "raw_inventory.json").write_bytes(inv_blob + b"\n")

    reconcile = {
        "ok": len(diffs) == 0,
        "diff_count": len(diffs),
        "diffs_sample": diffs[:100],
        "peak_vmhwm_kb_all_years": peak_all,
        "a13_limit_kb": A13_LIMIT_KB,
        "a13_ok": peak_all <= A13_LIMIT_KB,
        "end": END,
        "years": YEARS,
    }
    (out_tmp / "reconcile.json").write_text(
        json.dumps(reconcile, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    product_sha = sha256_file(DEST)
    baseline_obj = {
        "format": "daily_basic_build_baseline_v1",
        "product_path": str(DEST.relative_to(ROOT)),
        "product_sha256": product_sha,
        "rows": int(sum(dest_rows_by_year.values())),
        "rows_by_year": dest_rows_by_year,
        "row_groups_by_year": {
            k: [x["num_rows"] for x in v] for k, v in dest_rg_by_year.items()
        },
        "year_sorted_content_col_hashes": dest_ysch,
        "schema_names": schema_names,
        "transform_sha": tsha,
        "runtime_versions": rt,
        "raw_inventory_sha256": raw_inventory_sha,
        "raw_inventory_end": END,
        "ref_build": {
            "end": END,
            "years": YEARS,
            "by_year": {
                ys: {
                    "rows": ref_by_year[ys].get("rows"),
                    "peak_vmhwm_kb": ref_by_year[ys].get("peak_vmhwm_kb"),
                    "year_sorted_content_col_hashes": ref_by_year[ys].get(
                        "year_sorted_content_col_hashes"
                    ),
                    "year_sorted_content_col_hashes_stub": ref_by_year[ys].get(
                        "year_sorted_content_col_hashes_stub"
                    ),
                }
                for ys in ref_by_year
            },
            "reconcile_ok": reconcile["ok"],
            "peak_vmhwm_kb_all_years": peak_all,
        },
        "design_sha256": "5c6a3a1dcc0fdcba279cafbbacf64c829fc50ee9ed3faf0d8095b6dc4b8c17fc",
        "section": "5.3",
        "note": "scheme_A_step_section_5_3;A9_no_write_on_mismatch;not_manifest_seed;not_allow_run",
        "built_at_et": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }

    # A9
    if not reconcile["ok"]:
        (out_tmp / "DIFFS.json").write_text(
            json.dumps(diffs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print("RECONCILE_FAIL diff_count=", len(diffs), "baseline_NOT_written A9")
        print("OUT_TMP", out_tmp)
        return 9

    tmp_base = out_tmp / "build_baseline.json"
    tmp_base.write_text(
        json.dumps(baseline_obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    os.replace(tmp_base, BASE)
    print("BASELINE_WRITTEN", BASE, "sha8", sha256_file(BASE)[:8])
    print("OUT_TMP", out_tmp)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

**执行后回执（D1）**：Eng/Data 将 `OUT_TMP` 摘要 + `reconcile_ok` + baseline sha（或 A9 DIFFS）+ peak VmHWM + 本审稿 sha8，用 Python UTF-8+LF 原子写至：
`docs/v2/audit/daily_basic_a18_20261026/ENG_A18_SECTION_5_3_BASELINE_RECEIPT_20261026_ZH.md`（或 Data 命名对等）。

**A9 硬闸**：`reconcile_ok=false` → **不写** `build_baseline.json`；列差异（每类最多 100 样例）交 Arch/主；**不得**改走盲 seed。

**本清单执行完毕 ≠ seed `manifest.build` ≠ incr allow_run ≠ 物化**。

## 4. 拟 `.ok`（本回合**不落盘**；供主排签）

| 字段 | 拟值 |
|---|---|
| **拟路径** | `output/data/ARCH_RUN_AUTH_DAILY_BASIC_A18_SECTION_5_3_BASELINE.ok` |
| format | `quantlab_run_auth_v1` |
| auth_type / kind | `section_5_3_baseline` / `guide_baseline_ref_build` |
| signed_by / issuer | arch / QuantLab Arch |
| feature | `daily_basic_a18_section_5_3` |
| verdict | `SECTION_5_3_BASELINE_AUTHORIZED`（签窗落地时填） |
| design_sha256 | `5c6a3a1dcc0fdcba279cafbbacf64c829fc50ee9ed3faf0d8095b6dc4b8c17fc` |
| eng_dig_sha256 | `bd1888328bcedcb5a90b071b81207fe02b38f3b4c1d6adef85fb5b0fea9188c9` |
| data_s52_receipt_sha256 | `b21066a18c2ef72907fa00f3bdfae8e6b519b41c4e1912adf5dc833d2a3faad5` |
| arch_review_sha256 | **\<本审稿签发后全长\>** |
| dest_sha256_pin | `f6bbf9e51af78dfab2c021fa8809c58ad0d36df7293f8a488200b9dd5ceaf948` |
| manifest_sha256_pin | `8c2c978b384e8d3206da0876686fa214d7960353f472e81151a7acc3b0c74ac8` |
| incr_sha256_pin | `a7ac54b3ecdf33d338710df5c96f447fbec51affdcfbf167fb3e00648f678dd8` |
| transform_sha_pin | `308b5054c39801116fd0eb19b4e4bd10bdccd4b4d40bfb67dd06a58fa67ab974` |
| allow_ref_build | **true**（真实 raw；输出 `/tmp`；单进程逐年） |
| allow_write_baseline | **true**（**仅**对账一致时原子写 `build_baseline.json`） |
| allow_write_baseline_on_mismatch | **false**（A9） |
| allow_read_dest_for_reconcile | **true** |
| allow_write_production_parquet | **false** |
| allow_write_manifest | **false** |
| allow_seed_manifest_build | **false** |
| allow_materialize | **false** |
| allow_run / allow_backfill / allow_enable | **false** |
| allow_quarantine_move | **false** |
| forbid_reuse_ok_sha8 | `4377eb59` |
| forbid_touch_consumed_ok_sha8 | `3c297052\|d37a157e` |
| forbid_overlap_leaf25_window | `16:15–17:45 America/New_York` |
| a13_vmhwm_limit_kb | `1000000` |
| ref_build_end | `20261016` |
| ref_build_years | `2014..2026` |
| single_use | true（建议） |
| live / promotion / promotion_approved | false / false / false |
| research_only | true |
| window_et | **由主排**（见 §5） |
| note | `scheme_A_step_section_5_3_only;command_list_from_arch_review;A9_no_baseline_on_mismatch;not_seed;not_allow_run;no_blind_seed;no_code_bootstrap` |

### 4.1 拟签文草稿（键值；签窗由 Arch 落盘，本回合勿写文件）

```
format=quantlab_run_auth_v1
auth_type=section_5_3_baseline
kind=guide_baseline_ref_build
signed_by=arch
issuer=QuantLab Arch
ok_path=output/data/ARCH_RUN_AUTH_DAILY_BASIC_A18_SECTION_5_3_BASELINE.ok
feature=daily_basic_a18_section_5_3
verdict=SECTION_5_3_BASELINE_AUTHORIZED
design_sha256=5c6a3a1dcc0fdcba279cafbbacf64c829fc50ee9ed3faf0d8095b6dc4b8c17fc
eng_dig_sha256=bd1888328bcedcb5a90b071b81207fe02b38f3b4c1d6adef85fb5b0fea9188c9
data_s52_receipt_sha256=b21066a18c2ef72907fa00f3bdfae8e6b519b41c4e1912adf5dc833d2a3faad5
arch_s52_ok_sha256=dc51a0b30fdddbbf94234ad346ec15a180bd5b256d5772cdf1c4fc24efcc68ed
arch_review_sha256=<FILL_ON_SIGN>
dest_sha256_pin=f6bbf9e51af78dfab2c021fa8809c58ad0d36df7293f8a488200b9dd5ceaf948
manifest_sha256_pin=8c2c978b384e8d3206da0876686fa214d7960353f472e81151a7acc3b0c74ac8
incr_sha256_pin=a7ac54b3ecdf33d338710df5c96f447fbec51affdcfbf167fb3e00648f678dd8
transform_sha_pin=308b5054c39801116fd0eb19b4e4bd10bdccd4b4d40bfb67dd06a58fa67ab974
command_list_ref=docs/v2/audit/daily_basic_a18_20261026/ARCH_A18_SECTION_5_3_BASELINE_REVIEW_20261026_ZH.md#section-3
allow_ref_build=true
allow_write_baseline=true
allow_write_baseline_on_mismatch=false
allow_read_dest_for_reconcile=true
allow_write_production_parquet=false
allow_write_manifest=false
allow_seed_manifest_build=false
allow_materialize=false
allow_run=false
allow_backfill=false
allow_enable=false
allow_quarantine_move=false
forbid_reuse_ok_sha8=4377eb59
forbid_touch_consumed_ok_sha8=3c297052|d37a157e
forbid_overlap_window_et=2026-10-26T16:15:00-04:00/2026-10-26T17:45:00-04:00
a13_vmhwm_limit_kb=1000000
ref_build_end=20261016
ref_build_years=2014..2026
ref_build_out_tmpdir=/tmp
ref_build_single_process=true
single_use=true
live=false
promotion=false
promotion_approved=false
research_only=true
not_before_et=<MAIN_WINDOW>
expires_et=<MAIN_WINDOW_END>
prereq_section_5_2_pass=true
prereq_no_real_data_procs=true
prereq_baseline_absent=true
note=scheme_A_section_5_3_only;C8_decision_e_A18;A9_no_write_on_mismatch;D4_year_sorted_content_col_hashes;no_blind_seed;no_code_bootstrap;not_seed_manifest;not_allow_run;no_QUIET_default
archive_by=Arch only
```

## 5. 建议签窗（ET）与 QUIET

| 项 | 建议 |
|---|---|
| 墙钟（本审） | 2026-10-26 14:29 ET → **仍早于 15:00**，优先窗可用 |
| **优先签窗** | **2026-10-26 15:00–16:00 America/New_York**（Arch SIGN 短窗；**错开**叶25 **16:15–17:45**） |
| 执行约束 | 签后 Eng **不得**在 16:15–17:45 跑 ref_build；若 SIGN 后不足空档，Eng **推迟到 17:45 之后**开跑（或主裁合并窗） |
| **备选合并窗** | **2026-10-26 18:00–23:00 America/New_York**（selfcheck 后；SIGN+执行同窗；主可另裁） |
| QUIET | **默认不挂**（书面未要求短窗；与叶25 错开即可） |
| 前置 | 签前/开跑前：无真实数据进程；无 `RESEARCH_QUIET.lock`；baseline 仍 ABSENT；dest/manifest/incr/transform 钉 MATCH；§5.2 回执仍 PASS |
| 签窗确认 | **听主确认后再 SIGN**；本回合审稿 ≠ 签发 |

## 6. C8 / 决定(e) / A9 / A18 复述（签文必带）

1. **C8**：基线只能由 ref_build 产生；盘点已完成且无未处理残留。
2. **决定(e)**：新表+过时 manifest → **两边都不信**；过时 manifest 不作前置依据。
3. **A9**：ref_build 与现成品差异 → **不写** `build_baseline.json`，列差异交 Arch/主。
4. **A18**：无合格基线 → incr 拒绝启动 exit 20，直到 ref_build 重定基线。
5. **A13**：最大年 VmHWM ≤ 1,000,000 kB；回执必记；超线不得进入后续启用签。
6. **本票边界**：仅授权 §5.3 引导基线（ref_build+/tmp/单进程逐年 + 条件写 baseline）；**≠** seed `manifest.build`、≠ allow_run、≠ 物化、≠ 复用 enable `4377eb59`、≠ 盲 seed（B）、≠ 代码 bootstrap（C）。

## 7. CONDITIONS（PASS_WITH_CONDITIONS 清单）

1. 命令清单为 **Arch 本审新建**（非 Eng/Data 预交）→ 签文必须钉本审稿 sha8 + §3/§3.1。
2. **主排签窗**后方可落盘 `.ok`；本回合审稿 ≠ 签发。
3. 签窗须 **错开叶25 selfcheck 16:15–17:45**；优先 15:00–16:00 SIGN，执行避开该段；或主裁 18:00+ 合并窗。
4. **默认不挂 QUIET**（除非主书面另令短窗并说明理由）。
5. 对账失败 → **不写 baseline**（A9）；不得改走盲 seed / bootstrap。
6. 成功路径 **只**允许原子写 `build_baseline.json`；禁改 parquet/manifest；禁 seed；禁 allow_run/物化。
7. 开跑前复检进程/QUIET/钉/baseline ABSENT；漂移或脏则 ABORT。
8. 禁区：复用 `4377eb59`；动叶25 CONSUMED `3c297052`/`d37a157e`；≠X2；live=false；promotion=false。
9. dig P1-4：现成品可能早于现行 raw → 预期存在对账失败风险；失败即停，交主裁，不「带病写基线」。

## 8. 禁区回执（本回合）

- **未**创建/写入任何 `ARCH_RUN_AUTH_*.ok` live 文件（含拟 §5.3 `.ok`）
- **未**改 dest parquet / manifest / baseline
- **未**跑 ref_build / incr / nightly / materialize / seed
- **未** SendToAgent / SendToUser / UpdateRoutine
- **未**触碰叶25 CONSUMED `.ok` `3c297052`/`d37a157e`
- **未**复用 enable `4377eb59`
- **未**挂 QUIET

## 9. 下一步（听主）

1. 主核本审稿 → 确认签窗（建议 **15:00–16:00** SIGN，执行错开 16:15–17:45；或 **18:00–23:00** 合并）→ Arch **再**落盘拟 `.ok`（按 §4 草稿）。
2. Eng 按 §3.1 驱动执行；D1 写回执（PASS 写 baseline / FAIL=A9 不写）。
3. baseline PASS 后，主令 Arch 另票审签 **baseline→manifest.build 种子**（≠本票）。
4. 再另签 incr **allow_run**（缺口日如 1019–23+1026）；**勿**复用 enable `4377eb59`。

---
文档结束（Arch A18 §5.3 审结；**未签 .ok**）
