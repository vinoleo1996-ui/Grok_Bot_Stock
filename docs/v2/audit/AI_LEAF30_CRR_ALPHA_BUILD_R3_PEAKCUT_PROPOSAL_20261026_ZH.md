# AI 提案：叶30 CRR α 构建 R3 降峰补丁（研究稿 · 不执行）

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI（后台执行器） |
| 时刻 | `2026-10-27T00:03:47-04:00`（America/New_York；墙钟 `2026-10-27 00:03 ET`） |
| 触发 | 主 · 叶30 R2 VOID.ABORT_PEAK_HWM **CLOSED MATCH** → 另窗只写 **R3 降峰补丁提案** |
| **本拍结论** | **PROPOSAL READY**（仅文档；**不**落盘新脚本 / **不**改 `0a264402` / **不**申 `.ok` / **不**抬 rss / **不**开跑） |
| live | **false** |
| leo_notify | **false** |
| ≠ | X2 ACCEPT / selfcheck / Book-Smoke |

## 1. 背景钉（只读核对）

| 件 | 路径 / 值 | sha8 |
|---|---|---|
| R2 脚本（只读基盘 · **本拍未改**） | `research/leaf30_crr_cfooe_volpen_alpha_build_r2_chunk.py` | **`0a264402`**（全长 `0a2644021e8bbd16cbe7f69905a6a6dfcd47df3c798b6f5b272f7b6702220260`） |
| Arch R2 审 | `docs/v2/audit/ARCH_LEAF30_CRR_ALPHA_BUILD_R2_CHUNK_REVIEW_20261026_ZH.md` | **`1b672b67`** |
| AI R2 abort 回执 | `docs/v2/audit/AI_LEAF30_CRR_ALPHA_BUILD_R2_X2_RUN_RECEIPT_20261026_ZH.md` | **`fe5a2c1e`** |
| Arch VOID 回执 | `docs/v2/audit/ARCH_LEAF30_CRR_ALPHA_BUILD_R2_VOID_ABORT_PEAK_HWM_20261026_ZH.md` | **`df47501c`** |
| QUIET lift | `output/loop/_lifted/RESEARCH_QUIET_leaf30_r2_ABORT_PEAK_HWM_LIFTED_20261026T2358ET.lock` | **`41edf798`** |
| VOID `.ok`（archived） | `_consumed/…R2_HILIQ_X2.5af20222.VOID.ABORT_PEAK_HWM.…ok` | 内容钉 **`5af20222`**（live **ABSENT**） |
| 前代 VOID `.ok` | （R1/首跑 VOID） | **`5ae077fa`** |

### Abort 事实（R2 X2 PRIMARY）

| 项 | 值 |
|---|---|
| ET_TS | `20261026_231925` |
| **rc** | **94**（非 95 hard） |
| abort 标签 | **`after_logmv_rebal`** |
| peak_kb | **1433684** ≥ split=**1131520**（0.85×C4）→ Exit 94 |
| sampler | HWM=**1433684** / RSS=**1207320** |
| RSS 序列末 | `after_vol_pen` peak=921616 → **`after_logmv_rebal` 1433684 STOP** |
| `after_daily_concat` | **未到达** |
| out | 空；**无** `overlap_vs_leaf19_25.json`；**无** peak_proof 全序列收口 |
| VOID forbid | 禁 RESTORED **`5af20222`** / **`5ae077fa`**；禁抬 rss；禁无 `.ok` 自跑；禁盲重跑 `0a264402`/`a2cef5af` |

### R2 已做（仍保留）

1. avail logmv **按月桶**加载 → `del`+`gc` + 边界 `_rss(after_logmv_avail_YYYYMM)`
2. 日度按月 chunk → 临时 parquet → `del`+`gc` + `_rss(month_chunk_*)`
3. denser `check_rss`（`peak_kb=max(ru_maxrss,VmHWM)` → hard Exit **95**；soft/split Exit **94**）

## 2. 根因（对照 R2 已疏散的 avail / daily）

R2 在 `build_alpha_for_window` 中，**avail** 侧已按日历月桶疏散；**daily expand** 已按月 chunk 落盘。但再平衡侧仍保留：

```text
# research/leaf30_crr_cfooe_volpen_alpha_build_r2_chunk.py ~L1099–1101（只读引）
logmv_rebal = _load_logmv_t1(Path(args.float_mktcap), rebal_days, codes)
_rss("after_logmv_rebal")
# … 整窗 rebal 循环消费 logmv_rebal …
del logmv_rebal   # 释放发生在整窗循环之后
```

`_load_logmv_t1` 对传入 `dates` 取 `[min(dates)−10d, max(dates)]` **连续区间**，并对 **全部** `codes` 分批读 parquet 后在内存拼 `df` + `by_code` 再按日查 T−1。  
因此：即便 `rebal_days` 稀疏（~20td），**整窗一次预载**仍会把 HI_LIQ×x2 近全窗 float_mktcap 读入，再叠加已驻留的 `panel` / `sw` / `by_day` → 在 `_rss("after_logmv_rebal")` 尖峰 **1433684 ≥ split**。  
日度 month-chunk 路径 **尚未执行**（abort 早于 expand），故 R2 的 daily 疏散未获检验机会。

**一句话**：R2 疏散了 avail logmv 与 daily expand，**未疏散整窗 `logmv_rebal` 预载**——此即 Exit 94 根因。

## 3. R3 拟改意向（diff 级 · **本拍不落盘脚本**）

### 3.1 拟新脚本（意向名 · **本拍不创建**）

- 路径意向：`research/leaf30_crr_cfooe_volpen_alpha_build_r3_peakcut.py`
- 基盘：只读复制/派生自 R2 **`0a264402`**（r1 `a2cef5af` / R2 均**不改**）
- schema 意向：`leaf30_crr_cfooe_volpen_alpha_build_r3_peakcut`
- `prev_script_sha8` 意向：`0a264402`；`void_ref` 意向含 `df47501c` / abort `fe5a2c1e`；VOID `.ok` 钉 `5af20222`

### 3.2 PRIMARY：废除整窗 `logmv_rebal` 预载 → 按 rebal 日或按月桶懒加载

**拟删 / 替换块（意向）**：

```diff
- # Preload logmv for rebal days (T−1) — still sparse (~20td)
- logmv_rebal = _load_logmv_t1(Path(args.float_mktcap), rebal_days, codes)
- _rss("after_logmv_rebal")
-
- for d in rebal_days:
-     …
-     latest["logmv"] = latest["ts_code"].map(
-         lambda c, dd=d: logmv_rebal.get((pd.Timestamp(dd), c))
-     )
-     …
- del logmv_rebal
- gc.collect()

+ # R3 PRIMARY: ban whole-window logmv_rebal preload.
+ # Lazy-load _load_logmv_t1 per rebal day OR per calendar-month bucket of rebal_days;
+ # keep only that day/month's needed codes; del+gc immediately after consume;
+ # _rss at each rebal / month-bucket boundary (label after_logmv_rebal_*).
+
+ # Option A (preferred for peak): per-rebal-day
+ for d in rebal_days:
+     logmv_d = _load_logmv_t1(Path(args.float_mktcap), [d], codes_needed_or_all)
+     … use logmv_d for this d only …
+     del logmv_d
+     gc.collect()
+     _rss(f"after_logmv_rebal_{pd.Timestamp(d).strftime('%Y%m%d')}")
+
+ # Option B (throughput): month-bucket rebal_days (mirror avail path)
+ # buckets = group rebal_days by (year, month)
+ # for (yy, mm), dates_m in buckets:
+ #     logmv_m = _load_logmv_t1(..., dates_m, codes)
+ #     for d in dates_m: … consume …
+ #     del logmv_m; gc.collect()
+ #     _rss(f"after_logmv_rebal_{yy}{mm:02d}")
```

设计目标峰值：**显著低于** split=1131520（建议设计目标 peak≪**1000MB** 量级留裕）；**硬帽仍 1500 禁抬**。

说明：单日懒加载使 `_load_logmv_t1` 的 `[dmin,dmax]` 收缩为约 10 日窗，避免整窗 float 面板驻留；月桶则为 I/O 与峰值折中（仍远小于整窗）。实现拍由 Arch 审择 A/B；提案默认推荐 **A（按日）** 作峰值优先，若 I/O 过慢再退 **B（按月）**。

### 3.3 可选加固（非 PRIMARY，审后可取）

1. **rebal 循环避免累积大 list**：`alpha_rebal_rows` 按月 flush → 临时 parquet（对齐 daily month-chunk），再读拼 `A`；禁一次堆满全窗 rebal 行 dict。
2. 或：循环内只累积当月 rows，月界写盘 + `del`+`gc` + `_rss(rebal_flush_YYYYMM)`。
3. `_load_logmv_t1` 微优化（可选另票）：按日加载时限制 `codes` 为当日 HI_LIQ members（非全宇宙），进一步削峰——须保持 T−1 PIT 语义不变。

### 3.4 日度 month-chunk 路径保持 + peak_proof

- **保持** R2 日度 `_month_chunks` → 临时 parquet → concat 路径。
- 在 **`after_daily_concat` 前后** 保留 `RSS_CHECK`（peak_proof **REQUIRED** 含该标签）。
- 若 concat 残峰仍逼近 split：下一票再削（流式写 final / 分片出）；**本提案不预扩 scope 改写出格式**。

### 3.5 forbid / dry-compile / 机制钉（无回归）

| 钉 | R3 意向 |
|---|---|
| forbid | **扩展**：∋ **`5af20222`**（R2 VOID）+ **`5ae077fa`** + 既有十五票（R2 已 15，含 `5ae077fa`；R3 增 `5af20222` → **16**） |
| rss | 硬帽 **1500 禁抬**；C4/stop/hard 同 R2；Exit **94/95** 硬保留 |
| overlap | **必产** `overlap_vs_leaf19_25.json`；禁 `--no-overlap-report`（签文硬闸）；Jaccard≥0.7 硬拒 |
| peak_proof | REQUIRED；序列须含 `after_daily_concat`（及新 `after_logmv_rebal_*` 边界） |
| qend_ok_filter | **true**（真滤） |
| universe / window | HI_LIQ × x2；FULLA / 非 x2 STOP |
| dry-compile 钉 | `qend_ok_filter=true` / `chunk_mode=month` / `rss_limit_mb=1500` / `forbid` 含 **`5af20222`**（及 `5ae077fa`） |
| C2 / λ / 掩码 | 无回归：OP+OCF；λ=1.0；银/地/非银 |
| live / promotion | false / false；≠X2 ACCEPT |

### 3.6 拟 CLI / sampler（意向）

- sampler 前缀意向：`/tmp/quantlab_leaf30_crr_r3_*`
- out 隔离：`output/ai_factory/_leaf30_crr/<ET_TS>/`
- 真跑仍双闸：`--allow-real-data` + 现存 `--arch-ok-path`（sha8∉forbid）
- `--dry-compile-only` 零大表

## 4. 本拍明确非动作

| 非动作 | 状态 |
|---|---|
| 执行 / `--allow-real-data` / 开跑 | **未做** |
| 申 / 签 / RESTORED 任何 `.ok` | **未做** |
| 抬 rss 帽（>1500） | **未做** |
| 改 R2 脚本 `0a264402` | **未做**（只读） |
| 新建 `…_r3_peakcut.py` | **未做**（仅意向名） |
| 盲重跑 `0a264402` / `a2cef5af` | **未做** |
| RESTORED `5af20222` / `5ae077fa` | **禁且未做** |
| 触 A18 / X2 ACCEPT / selfcheck / Book-Smoke | **未做** |
| 报 Leo / SendToUser | **未做**（leo_notify=false） |

## 5. 验收闸（他日真跑 · 非本拍）

1. **峰值**：真跑 peak_kb（max ru_maxrss/VmHWM）**显著低于** split=1131520；设计目标 peak≪1000MB 留裕；硬帽仍 1500，破 soft/split→94、破 hard→95，**禁抬帽**。
2. **overlap**：必须产出并消费 `overlap_vs_leaf19_25.json`；禁 `--no-overlap-report`；Jaccard≥0.7 → 硬拒。
3. **peak_proof**：REQUIRED 全序列；**必须含** `after_daily_concat`；并含新 `after_logmv_rebal_*`（日或月界）。
4. **机制无回归**：`qend_ok_filter=true`；HILIQ×x2；C2/λ/掩码；forbid∋`5af20222`+`5ae077fa`+十五票基。
5. **授权**：仅新 `.ok`（主排签窗；Arch 另签）；禁 RESTORED VOID 钉；禁无 `.ok` 自跑。

## 6. 下一跳

```text
本提案（AI）→ priority 回主
  → Arch **只审不签**（对照本提案 + 基盘 0a264402；可要求落盘 r3 脚本后再审）
    → 主另排独立签窗 → Arch 签 **新** `.ok`（钉 r3 脚本 sha8；forbid∋5af20222+5ae077fa；rss=1500；C3/peak_proof）
      → AI prelaunch→execute（仅新 .ok；approved_cmd；禁改 CLI）
        → Arch CONSUME（≠X2 ACCEPT）
```

**本拍停于提案文档**；不落盘 r3 `.py`；不申 `.ok`；不开跑。

## 7. 本文件钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/audit/AI_LEAF30_CRR_ALPHA_BUILD_R3_PEAKCUT_PROPOSAL_20261026_ZH.md` |
| 基盘脚本 | **`0a264402`**（未改） |
| 对照 abort | **`fe5a2c1e`** rc=94 @ `after_logmv_rebal` peak=1433684 |
| 对照 VOID | **`df47501c`** / lift **`41edf798`** / VOID ok **`5af20222`** |
| 拟脚本 | `…_r3_peakcut.py`（**未创建**） |
| 结论 | **PROPOSAL READY · 不执行** |

live=false · leo_notify=false · ≠X2 ACCEPT.
