# Arch 审结：A18 §5.2 只读盘点空档（只审不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行手） |
| 时刻（America/New_York） | `2026-10-26T13:41:00-04:00`（墙钟 2026-10-26 13:41 ET） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 本回合动作 | **不签**任何 live `.ok`；不写生产 parquet/manifest；不跑 ref_build / 物化 / seed；不复用 enable `4377eb59`；勿动叶25 CONSUMED `.ok`；**不** SendToAgent / SendToUser；live=false；promotion=false；≠X2 |
| 触发 | 主采纳方案 A（`output/d1/MAIN_A18_SCHEME_A_GO_20261026_1337_ET.md`）；Eng dig sha8 **`bd188832`** |
| 设计钉 | `docs/v2/DATA_DAILY_BASIC_INCREMENTAL_DESIGN_v3_1_ZH.md` sha **`5c6a3a1d…`**（§5.2 / §5.3 / C8 / 决定(e) / A18） |

## 0. 一句话

Eng dig **MATCH**；现场 dest/manifest/无 baseline/无 pending·quarantine·stale tmp·parts **对齐 dig**；无真实数据进程；叶25 QUIET **已 lift**（`a4857568`）；live `.ok`=0。审计树内 **无** 正式 §5.2 命令清单 → **本审新建** 只读命令清单。结论 **PASS_WITH_CONDITIONS**：可排签 §5.2 空档 `.ok`，但须主排窗 + 签文禁读行/写盘/物化/seed/ref_build；**本回合未签发 `.ok`**。

## 1. 依据精读（本审）

| 源 | 要点 | 结果 |
|---|---|---|
| 设计 §5.2 | C8：空档 + **无其他真实数据进程**；**命令清单先交 Arch**；仅 `read_metadata`/`stat`/文件 sha256；**不读数据行**；列 tmp/parts/成品·manifest·status·backups·raw `*.tmp.parquet`；残留只列，隔离另签；D1 UTF-8+LF 原子写回执 | **采纳为签文硬闸** |
| 设计 §5.3 前提 | 盘点无未处理残留；「新表+过时 manifest」→ 两边都不信，直接 ref_build 定基线；对账不一致不写基线（A18/A9） | **本票不授权 §5.3**；仅清前提 |
| C8 / 决定(e) | 新表+过时 manifest 两边都不信；基线只能由 ref_build 产生 | **复述有效**；拒盲 seed / 拒代码 bootstrap |
| Dig 方案 A 步骤1–2 | 1) Arch 签 §5.2 空档 `.ok`（命令清单先审）；2) Data/Eng 只读盘点确认无残留并记 dest sha | **本审 = 步骤1 的审稿**；步骤2 等主排签后执行 |
| Dig sha8 | `bd188832` 全长 `bd1888328bcedcb5a90b071b81207fe02b38f3b4c1d6adef85fb5b0fea9188c9` | **MATCH**（本机复算） |

### 1.1 命令清单来源

- 搜 `docs/v2/audit/**`、`daily_basic_a18_20261026/`、相关 nightly/enable 包：**无** Data/Eng 交来的正式「§5.2 只读命令清单」草案。
- Dig 仅原则性列举（`stat` / `sha256sum` / `read_metadata`；禁读行），**不足**作可执行签文附件。
- **本审新建**完整可复制命令清单（见 §3）；签 `.ok` 时须钉本审稿 sha8。

## 2. 现场只读核盘（本机；与 dig 对齐；未改生产）

| 项 | 期望（dig） | 实测 | 结果 |
|---|---|---|---|
| dest | `data/v2/valuation/daily_basic_full_tushare.parquet` sha8 `f6bbf9e5` | size=745129744；sha256=`f6bbf9e51af78dfab2c021fa8809c58ad0d36df7293f8a488200b9dd5ceaf948`；sha8 **`f6bbf9e5`** | **MATCH** |
| `pq.read_metadata` | num_rows=12309945；rg=18；未读行 | num_rows=12309945；num_row_groups=18；num_columns=22；schema 22 列名已取；**未** `read`/`to_pandas`/`take` | **MATCH** |
| manifest | sha8 `8c2c978b`；**无 `build`**；date_max=`2026-10-16`；built_at=`2026-10-18T00:21:47-0400`；rows=12309945 | sha256=`8c2c978b384e8d3206da0876686fa214d7960353f472e81151a7acc3b0c74ac8`；顶层键无 `build`；date_max/built_at/rows **同 dig** | **MATCH** |
| `build_baseline.json` | 不存在 | **ABSENT** | **MATCH** |
| pending | 无 | `data/v2/valuation/*pending*` **无** | **MATCH** |
| `_quarantine` | 无 | 目录 **不存在** | **MATCH** |
| stale tmp / parts | 无 | valuation 下无 `*.tmp` / `*.part*` / `_daily_basic_parts_*`；raw `data/v2/tushare_raw/daily_basic/*.tmp.parquet` 计数=**0** | **MATCH** |
| backups（清单） | dig 未逐列；设计 §5.2 要求列清单 | `backups/valuation/`：`20261014_1136`、`20261014_1137_dupbug`、`20261014_1803`、`20261017_2357`、`20261018_0020`（=manifest.backup_path，存在）；`backups/valuation_pinned/`：1136+1137_dupbug（nlink=2，决定(a)） | **列出；未动** |
| 真实数据进程 | 签前须无 | `pgrep`/`ps`：acquire/nightly/daily_basic/ref_build/materialize/tier1/eng_daily/run_nightly → **无匹配**（仅本审自检） | **干净** |
| live `.ok` | 叶25 后应为 0 | `output/ai_factory/*.ok` **空**；计数=**0** | **MATCH** |
| QUIET | 叶25 应已 lift | `output/loop/RESEARCH_QUIET.lock` **无**；lift 档 `…PASS_LIFTED_20261026T1326ET.lock` sha8 **`a4857568`** | **MATCH** |
| 叶25 CONSUMED | 勿动 `3c297052`/`d37a157e` | `_consumed/…3c297052.CONSUMED_PASS…ok` 仍在；归档 sha8 **`d37a157e`**；本审未改 | **未触碰** |
| enable `.ok` | `4377eb59` allow_run=false；勿复用 | `output/data/ARCH_RUN_AUTH_DAILY_BASIC_INCR_V3_1_ENABLE.ok` sha=`4377eb592c18c3bed067c9a7dc775330a3d78f811adb6f51f550b0fa54ccbd73`；allow_run/write/backfill=false | **确认；本票不复用** |
| Mem（旁证） | — | MemAvailable≈6.3Gi（13:40 ET）；非峰证明 | 旁证 |

**A18 状态判定（本审）**：manifest **无 `build`** + 无合格 `build_baseline.json` + 设计/代码 A18 闸 → 属「须 §5.2→§5.3 ref_build 重定基线」路径；rows/date_max 与 metadata **一致**（非行级冲突），但 **不能** 据此信任过时 manifest 作前置（C8/决定(e)）。成品墙钟 mtime（箱内同步痕迹 2026-10-25）相对 `built_at` 不可单独当「新表」铁证；以 dig 根因 + 无 build/无 baseline 为准。

## 3. 拟 §5.2 只读命令清单（新建；签后 Data/Eng 原样执行）

**允许工具**：`stat` / `ls` / `sha256sum` / `find`（只列） / `python3` + `pyarrow.parquet.read_metadata`（元数据） / `python3` 读 manifest **JSON 键**（不解析 parquet 行）。

**禁止**：`pq.read_table` / `read_row_group` / `to_pandas` / `take` / 任何列扫描读行；写/改/删/移动生产文件；生产路径 `os.replace`；跑 `daily_basic_incremental` / `ref_build` / `tier1_materialize` / nightly；写 `build_baseline.json`；改 manifest；seed `manifest.build`；复用 enable `.ok`；触碰叶25 CONSUMED `.ok`。

```bash
# === A18 §5.2 READ-ONLY INVENTORY (America/New_York) ===
# Prereq: Arch .ok signed; re-check no real data procs; live=false
set -euo pipefail
cd /workspace/QuantLab
TS=$(date '+%Y%m%dT%H%M%S%z')
OUT_DIR=docs/v2/audit/daily_basic_a18_20261026

# 0) 空档门：无真实数据进程（有则 ABORT，不继续）
if pgrep -af 'acquire|nightly|daily_basic|ref_build|materialize|tier1_materialize|eng_daily_panels|run_nightly' \
  | grep -vE 'pgrep|rg |grep '; then
  echo "ABORT: real data process present"; exit 2
fi
test ! -e output/loop/RESEARCH_QUIET.lock || { echo "ABORT: QUIET hung"; exit 2; }

DEST=data/v2/valuation/daily_basic_full_tushare.parquet
MAN=data/v2/valuation/daily_basic_full_tushare_manifest.json
BASE=data/v2/valuation/daily_basic_full_tushare_build_baseline.json
RAW=data/v2/tushare_raw/daily_basic
VAL=data/v2/valuation

# 1) 存在性 + stat（禁读行）
stat -c 'path=%n size=%s mtime=%y inode=%i' "$DEST" "$MAN"
stat -c 'path=%n size=%s mtime=%y' "$BASE" 2>&1 || echo "BASELINE_ABSENT"
ls -lad "$VAL"/_daily_basic_parts_* 2>&1 || echo "NO_PARTS_DIRS"
ls -la "$VAL"/*pending* 2>&1 || echo "NO_PENDING"
ls -lad "$VAL"/_quarantine 2>&1 || echo "NO_QUARANTINE_DIR"
find "$VAL" -maxdepth 2 \( -name '*.tmp' -o -name '*.tmp.*' -o -name '*.part*' -o -name '*pending*' \) -ls 2>/dev/null || true
find "$RAW" -maxdepth 1 -name '*.tmp.parquet' -ls 2>/dev/null || echo "NO_RAW_TMP_PARQUET"
ls -la backups/valuation/ | sed -n '1,30p'
ls -la backups/valuation_pinned/ | sed -n '1,20p'

# 2) sha256（整文件；非行）
sha256sum "$DEST" "$MAN"
test ! -e "$BASE" && echo "baseline_sha=ABSENT" || sha256sum "$BASE"

# 3) parquet 只读元数据（禁 read/to_pandas/take）
python3 - <<'PYMETA'
import json
from pathlib import Path
import pyarrow.parquet as pq
dest = Path("data/v2/valuation/daily_basic_full_tushare.parquet")
man_p = Path("data/v2/valuation/daily_basic_full_tushare_manifest.json")
md = pq.read_metadata(dest)
print("num_rows", md.num_rows)
print("num_row_groups", md.num_row_groups)
print("num_columns", md.num_columns)
print("schema_names", list(md.schema.names))
man = json.loads(man_p.read_text(encoding="utf-8"))
print("manifest_keys", sorted(man.keys()))
print("has_build", "build" in man)
print("rows", man.get("rows"))
print("date_min", man.get("date_min"))
print("date_max", man.get("date_max"))
print("built_at", man.get("built_at"))
print("backup_path", man.get("backup_path"))
print("rows_match_meta", man.get("rows") == md.num_rows)
print("baseline_exists", Path("data/v2/valuation/daily_basic_full_tushare_build_baseline.json").exists())
PYMETA

# 4) 回执：Python UTF-8+LF 原子写至 docs/v2/audit/daily_basic_a18_20261026/
#    （D1：先 .tmp 再 os.replace；禁止 shell heredoc 写回执正文）
#    回执须含：上表全部输出摘要、dest/manifest sha 全长、baseline ABSENT、
#    pending/quarantine/tmp/parts 结论、pgrep 空、Arch .ok sha、本命令清单来源审稿 sha8。
# 5) 禁区复述：本清单执行完毕 ≠ §5.3；发现残留只列，隔离另签 .ok。
```

## 4. 拟 `.ok`（本回合**不落盘**；供主排签）

| 字段 | 拟值 |
|---|---|
| **拟路径** | `output/data/ARCH_RUN_AUTH_DAILY_BASIC_A18_SECTION_5_2_INVENTORY.ok` |
| format | `quantlab_run_auth_v1` |
| auth_type / kind | `section_5_2_inventory` / `read_only_inventory` |
| signed_by / issuer | arch / QuantLab Arch |
| feature | `daily_basic_a18_section_5_2` |
| verdict | `SECTION_5_2_INVENTORY_AUTHORIZED`（签窗落地时填） |
| design_sha256 | `5c6a3a1dcc0fdcba279cafbbacf64c829fc50ee9ed3faf0d8095b6dc4b8c17fc` |
| eng_dig_sha256 | `bd1888328bcedcb5a90b071b81207fe02b38f3b4c1d6adef85fb5b0fea9188c9` |
| arch_review_sha256 | **\<本审稿签发后全长\>** |
| dest_sha256_pin | `f6bbf9e51af78dfab2c021fa8809c58ad0d36df7293f8a488200b9dd5ceaf948` |
| manifest_sha256_pin | `8c2c978b384e8d3206da0876686fa214d7960353f472e81151a7acc3b0c74ac8` |
| allow_readonly_inventory | **true** |
| allow_read_rows | **false** |
| allow_write_production | **false** |
| allow_materialize | **false** |
| allow_ref_build | **false** |
| allow_seed_manifest_build | **false** |
| allow_write_baseline | **false** |
| allow_quarantine_move | **false**（隔离另签） |
| allow_run / allow_backfill / allow_enable | **false** |
| forbid_reuse_ok_sha8 | `4377eb59`（enable）；叶25 `3c297052`/`d37a157e` 禁 RESTORED/改动 |
| single_use | true（建议） |
| live / promotion / promotion_approved | false / false / false |
| research_only | true |
| window_et | **由主排**（见 §5）；签文填写 `not_before_et` / `expires_et` |
| prereq | 执行前无真实数据进程；无 `RESEARCH_QUIET.lock`；live `.ok` 冲突票不并存 |
| note | `scheme_A_step1_only; command_list_from_arch_review; D1_atomic_utf8_receipt; not_section_5_3` |

### 4.1 拟签文草稿（键值；签窗由 Arch 落盘，本回合勿写文件）

```
format=quantlab_run_auth_v1
auth_type=section_5_2_inventory
kind=read_only_inventory
signed_by=arch
issuer=QuantLab Arch
ok_path=output/data/ARCH_RUN_AUTH_DAILY_BASIC_A18_SECTION_5_2_INVENTORY.ok
feature=daily_basic_a18_section_5_2
verdict=SECTION_5_2_INVENTORY_AUTHORIZED
design_sha256=5c6a3a1dcc0fdcba279cafbbacf64c829fc50ee9ed3faf0d8095b6dc4b8c17fc
eng_dig_sha256=bd1888328bcedcb5a90b071b81207fe02b38f3b4c1d6adef85fb5b0fea9188c9
arch_review_sha256=<FILL_ON_SIGN>
dest_sha256_pin=f6bbf9e51af78dfab2c021fa8809c58ad0d36df7293f8a488200b9dd5ceaf948
manifest_sha256_pin=8c2c978b384e8d3206da0876686fa214d7960353f472e81151a7acc3b0c74ac8
command_list_ref=docs/v2/audit/daily_basic_a18_20261026/ARCH_A18_SECTION_5_2_INVENTORY_REVIEW_20261026_ZH.md#section-3
allow_readonly_inventory=true
allow_read_rows=false
allow_write_production=false
allow_materialize=false
allow_ref_build=false
allow_seed_manifest_build=false
allow_write_baseline=false
allow_quarantine_move=false
allow_run=false
allow_backfill=false
allow_enable=false
forbid_reuse_ok_sha8=4377eb59
forbid_touch_consumed_ok_sha8=3c297052|d37a157e
single_use=true
live=false
promotion=false
promotion_approved=false
research_only=true
not_before_et=<MAIN_WINDOW>
expires_et=<MAIN_WINDOW_END>
prereq_no_real_data_procs=true
prereq_no_research_quiet_lock=true
note=scheme_A_step1_only;C8_decision_e_A18;D1_receipt;not_section_5_3;no_blind_seed;no_code_bootstrap
archive_by=Arch only
```

## 5. 空档建议（ET）与前置

| 项 | 建议 |
|---|---|
| 窗类型 | **短只读盘点窗**（预计 ≤15–30 min；sha256 dest≈745MB 占大头） |
| 建议窗 | **2026-10-26 14:15–16:00 America/New_York**（主可改排；避开任何 nightly/acquire/叶级重任务） |
| 前置 | 签前与开跑前各做一次：无 acquire/nightly/daily_basic/ref_build/materialize 进程；无 `RESEARCH_QUIET.lock`；live `.ok` 无冲突实跑票 |
| 现场（本审） | 进程干净；QUIET 已 lift；live `.ok`=0 → **可排** |
| 后续 | 盘点回执 PASS 且无未处理残留 → 主再令 Arch 审/签 **§5.3**（另票）；**勿**本票顺带授权 |

## 6. C8 / 决定(e) / A18 复述（签文必带）

1. **C8**：只读盘点须在 Arch 指定空档；当时无其他真实数据进程；命令清单先审后跑；只 metadata/stat/sha，**不读行**。
2. **决定(e)**：新表+过时 manifest → **两边都不信**；过时 manifest 不作前置依据；基线只能由 §5.3 ref_build 产生。
3. **A18**：无合格基线 / 未重定基线 → incr 拒绝启动 exit 20；直至 ref_build 重定基线。拒盲 seed（方案 B）；拒代码 bootstrap（方案 C）；勿复用 enable `4377eb59`（allow_run=false）。
4. **本票边界**：仅授权 §5.2 只读盘点；**不**等于 §5.3、不写 baseline、不 seed `manifest.build`、不 allow_run 补缺口。

## 7. CONDITIONS（PASS_WITH_CONDITIONS 清单）

1. 命令清单为 **Arch 本审新建**（非 Eng/Data 预交）→ 签文必须钉本审稿 sha8 + §3 清单。
2. **主排签窗**后方可落盘 `.ok`；本回合审稿 ≠ 签发。
3. 执行中若发现残留：回执只列；**隔离另签**（本 `.ok` `allow_quarantine_move=false`）。
4. 回执必须 D1（Python UTF-8+LF 原子写）；禁止 heredoc 写正文。
5. 开跑前复检进程/QUIET；若脏则 ABORT，不「带病盘点」。
6. 禁区：读行 / 写盘 / 物化 / ref_build / seed / 复用 `4377eb59` / 动叶25 CONSUMED。
7. ≠X2；live=false；promotion=false。

## 8. 禁区回执（本回合）

- **未**创建/写入任何 `ARCH_RUN_AUTH_*.ok` live 文件
- **未**改 dest parquet / manifest / baseline
- **未**跑 ref_build / incr / nightly / materialize
- **未** SendToAgent / SendToUser
- **未**触碰叶25 CONSUMED `.ok` `3c297052`/`d37a157e`
- **未**复用 enable `4377eb59`

## 9. 下一步（听主）

1. 主核本审稿 → 排 §5.2 签窗 → Arch **再**落盘拟 `.ok`（按 §4 草稿）。
2. Data/Eng 按 §3 清单执行并 D1 写盘点回执。
3. 回执 PASS 后，主令 Arch 审签 **§5.3**（另票；真实 raw、输出 `/tmp`、单进程逐年）。
4. 再签 baseline→manifest.build 种子；另签 incr allow_run（1019–23+1026）；勿复用 enable。

---
文档结束（Arch A18 §5.2 审结；**未签 .ok**）
