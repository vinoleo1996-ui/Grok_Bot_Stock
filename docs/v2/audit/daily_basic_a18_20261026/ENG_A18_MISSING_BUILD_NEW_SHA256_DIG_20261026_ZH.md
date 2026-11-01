# Eng 深挖：daily_basic A18 missing build.new_sha256（D=20261026）

- 角色：QuantLab Eng
- 时区：America/New_York（ET）
- 落盘时刻（ET）：2026-10-26T13:36:06-0400
- live=false；promotion_approved=false
- **范围**：只读深挖 + 侧稿方案；**未**实跑物化、**未**改生产表/manifest、**未**伪造 .ok、**未**消费 `9e4359f9`、**未** `--c5-ignore`、**未**抬帽

## 0. 一句话根因

现网 `daily_basic_full_tushare_manifest.json` 仍是 2026-10-18 **全量时代**产物（**无 `build` 块**）；enable `.ok` `4377eb59` 仅授权代码路径且 **从未完成 §5.3 引导基线**；nightly 已走 incr → `_precheck` 按设计 A18 以 rc=20 拒绝（非脚本误伤）。

## 1. 现场核对（只读）

| 项 | 值 |
|---|---|
| dest parquet | `data/v2/valuation/daily_basic_full_tushare.parquet` |
| dest sha256（`sha256sum`） | `f6bbf9e51af78dfab2c021fa8809c58ad0d36df7293f8a488200b9dd5ceaf948` |
| dest size | 745129744 B |
| `pq.read_metadata` num_rows | 12309945（== manifest.rows；**未**读数据行） |
| num_row_groups | 18 |
| manifest | `data/v2/valuation/daily_basic_full_tushare_manifest.json` |
| manifest sha256 | `8c2c978b384e8d3206da0876686fa214d7960353f472e81151a7acc3b0c74ac8` |
| manifest 顶层键 | path/rows/instruments/date_min/date_max/…/**无 `build`** |
| date_max / built_at | `2026-10-16` / `2026-10-18T00:21:47-0400` |
| `build_baseline.json` | **不存在** |
| pending / _quarantine | **无** |
| incr 脚本 sha | `a7ac54b3ecdf33d338710df5c96f447fbec51affdcfbf167fb3e00648f678dd8` MATCH enable 钉 |
| transform_sha（现盘 AST） | `308b5054c39801116fd0eb19b4e4bd10bdccd4b4d40bfb67dd06a58fa67ab974` MATCH pin |
| runtime_versions（现盘） | python=3.13.5；pandas=3.0.6；pyarrow=26.0.0；numpy=2.5.4 |
| nightly_update.py | `2b4704e8…`（enable 包已把 daily_basic 步钉成 `--mode incremental`） |
| driver `run_nightly_v1_dbincr_v3_1.py` | **不在** `scripts/`；仅 `docs/v2/audit/nightly_20261019/`（`.ok` 写 `routine_switch_to_new_driver=false`） |
| raw `20261026.parquet` | 在；sha `23f697ec0bdd4981948beb6ae07c736ace15c04197d1ff9457e74d6f48149713` |
| raw 缺口日（相对 dest max） | 20261019–23、20261026（另有 20261016） |
| 夜更回执 | `docs/v2/audit/nightly_20261026/NIGHTLY_RECEIPT_20261026_ZH.md` sha8 `4013af82` |

manifest 结构：仅有 path/rows/date_*/built_at/schema/history_diff_rows/backup_path 等；**没有** `build.new_sha256` / `transform_sha` / `runtime_versions` / `raw_inventory`。

## 2. `build.new_sha256` 本应何时写入（设计 / enable / 代码）

### 2.1 设计 v3.1（sha `5c6a3a1d…`）

- **常态写入点**：incr **成功 `_commit`** 时写入 `manifest.build`（含 `prev_sha256`、`new_sha256`、`transform_sha`、`runtime_versions`、`raw_inventory` 等）——§2.10 / §2.14。
- **首晚前置**：§5.4「成品 sha == 上一版 `manifest.build.new_sha256`；**首晚 == 基线文件成品 sha**」。
- **引导基线**：§5.3 单独签 `.ok`，用 **ref_build** 对 2014..Y 对账后原子写 `data/v2/valuation/daily_basic_full_tushare_build_baseline.json`。对账不一致 → **不写基线**（A9）。
- **A18 / C8 / 决定 (e)**：「新表+过时 manifest」**两边都不信**；无合格基线 → incr **拒绝启动 exit 20**，直到 ref_build 重定基线。
- **启用顺序** §6.1：… → selftest → §5.2 盘点 → **§5.3 引导基线** → 驱动重钉 → Arch 另签 enable。现网跳过「引导基线」却已让 nightly 走 incr。

### 2.2 代码（`daily_basic_incremental.py` a7ac54b3）

- `_precheck`（约 L567–595）：`build = man.get("build") or {}`；缺 `new_sha256` → `DB_INCR_PRECOND: missing build.new_sha256 (A18)` rc=20。
- `_commit`（约 L901–997）：组装 `build{… new_sha256 …}` 写回 manifest——**生产路径唯一写入点**。
- **无**「无 build 则 bootstrap」；**无**读取 `build_baseline.json` 的回退（与 §5.4「首晚对基线文件」有缝：即便有 baseline，仍须授权填 `manifest.build`，或另 DIFF 让 precheck 认 baseline）。

### 2.3 enable 包 / SHA_KEYS / driver / enable `.ok`

| 钉 | 状态 |
|---|---|
| design `5c6a3a1d…` | `.ok` 内已钉 |
| enable pack review `fc6a41aa…` | PASS_WITH_CONDITIONS |
| driver `f1910e8a…` | audit 路径；**未**切例程 |
| incr `a7ac54b3…` | 现盘 MATCH |
| transform `308b5054…` | 现盘 MATCH |
| enable `.ok` `4377eb59…` | allow_enable=true；**allow_run/write/backfill=false** |
| note | enable_codepath_only；实跑须另签 |

结论：enable **不**写 `manifest.build`；也 **未**授权 §5.3 / 实跑。A18 拒跑与 `.ok` 边界一致。

## 3. 方案对比（侧稿；待 Arch）

### 方案 A — 合设计：§5.2 → §5.3 ref_build → 授权填 `manifest.build` → 另签 allow_run（**推荐**）

1. **Arch** 签 §5.2 只读盘点空档 `.ok`（命令清单先审）。
2. **Data/Eng** 只读：`stat` / `sha256sum` / `read_metadata`（禁读行）；确认无 stale tmp/parts/pending；记录 dest sha=`f6bbf9e5…`。
3. **Arch** 签 §5.3 引导基线 `.ok`（ref_build 真实 raw、输出 `/tmp`、单进程逐年）。
4. **Eng** 跑 ref_build 2014..Y（§4.2）；一致则原子写 `daily_basic_full_tushare_build_baseline.json`。
5. **Arch** 签「baseline → manifest.build 种子」`.ok`（现 precheck **只认** `manifest.build.new_sha256`）。在不改 parquet 字节前提下原子写入示意：

```json
"build": {
  "mode": "baseline_seed",
  "prev_sha256": null,
  "new_sha256": "<baseline 成品 sha == dest sha>",
  "transform_sha": "308b5054c39801116fd0eb19b4e4bd10bdccd4b4d40bfb67dd06a58fa67ab974",
  "runtime_versions": {"python": "3.13.5", "pandas": "3.0.6", "pyarrow": "26.0.0", "numpy": "2.5.4"},
  "raw_inventory": "<内容 sha 版，来自 baseline>",
  "rows_by_year": {},
  "seeded_from": "daily_basic_full_tushare_build_baseline.json",
  "seeded_at": "<ET>"
}
```

6. **Arch** 另签 incr **allow_run**（缺口日如 1019–23+1026）；**Data** 再跑物化。
7. 成功后 `_commit` 将 mode 翻成 `incremental` 并更新 `new_sha256`。

风险：ref_build 耗时/内存（A13）；对账失败则 **不能** 种子。  
需 Arch `.ok`：**是（多枚）**——盘点、基线、manifest 种子、incr 实跑分开签。

### 方案 B — 一次性盲 seed：`new_sha256=当前 dest sha`（**不推荐**）

- 不跑 ref_build，直接写入 `f6bbf9e5…`。
- 风险：违反 C8/决定(e)/A18；设计已记 P1-4（现成品可能早于现行 raw）；旧年偏差可能被冻结。
- 需 Arch `.ok`：**是，且须明示豁免 §5.3**；Eng 不建议默认走此路。

### 方案 C — 代码「无 build → 首次 bootstrap」（**不推荐**）

- 改 `_precheck` 放行缺 build：废除 A18 硬闸；与 enable blockers 自测相反；须设计修订 + 生产 DIFF + Arch `.ok`。
- **本回不改 prod 脚本**。

### 方案 D — 实现缝补丁（可与 A 并行提案）

- 侧稿 DIFF（待 Arch）：`_precheck` 在缺 `build.new_sha256` 时，若合格 `build_baseline.json` 且 product_sha==dest_sha 且 transform/runtime 匹配，则允许首晚；仍缺 baseline → 20。
- 对齐 §5.4 字面，**不能**替代 §5.3。本回不落生产代码。

## 4. 建议下一步（Eng → Arch / Data）

1. **Eng→Arch**：采纳 **方案 A**；请签 §5.2 盘点空档 `.ok`。拒绝无条件盲 seed（B），除非书面豁免。
2. **Arch→Data/Eng**：盘点通过后签 §5.3；Eng 执行 ref_build（`/tmp`）。
3. **Arch**：基线一致后签 manifest.build 种子写（或先裁示 D）。
4. **Arch→Data**：另签 incr allow_run / 缺口补跑；**勿**复用 enable `.ok`（`allow_run=false`；且 `expires_et=2026-10-26T16:37:21-04:00`）。
5. **Eng**：Arch 裁示前冻结对 prod manifest/脚本的写入；本侧稿作交办附件。

## 5. 禁区回执

未消费 `9e4359f9`；未补跑物化；未 enable 切换；未 `--c5-ignore`；未抬帽；未动 CONSUMED `.ok`；未改 incr/nightly/生产 parquet/manifest。

## 6. 钉与旁证清单

```
dest_sha256     f6bbf9e51af78dfab2c021fa8809c58ad0d36df7293f8a488200b9dd5ceaf948
manifest_sha256 8c2c978b384e8d3206da0876686fa214d7960353f472e81151a7acc3b0c74ac8
incr_sha256     a7ac54b3ecdf33d338710df5c96f447fbec51affdcfbf167fb3e00648f678dd8
transform_sha   308b5054c39801116fd0eb19b4e4bd10bdccd4b4d40bfb67dd06a58fa67ab974
nightly_sha256  2b4704e88a45e8bb173aa8f3375de9d9dc67a13b8c5501292ddf0a0fa3ebfd5b
tier1_sha256    7205ba43b4e4dc50c1ca9f546f6f54c359ad8c78f4707c2d2bb161d46829e65c
enable_ok       4377eb592c18c3bed067c9a7dc775330a3d78f811adb6f51f550b0fa54ccbd73
design_v3_1     5c6a3a1dcc0fdcba279cafbbacf64c829fc50ee9ed3faf0d8095b6dc4b8c17fc
nightly_receipt 4013af824a51504b0f591df4b444e0b17bf211750497b3ffcaa49584d6232525
raw_20261026    23f697ec0bdd4981948beb6ae07c736ace15c04197d1ff9457e74d6f48149713
driver_pin      f1910e8ab054c30628184f6e451a77db9c7e3487c31023f0761e50e510e87f05
```
