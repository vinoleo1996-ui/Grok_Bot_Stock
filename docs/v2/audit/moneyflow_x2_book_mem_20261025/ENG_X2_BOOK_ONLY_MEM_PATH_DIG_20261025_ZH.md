# Eng 预挖：X2 单档 BOOK-only 内存通路（moneyflow / book-smoke）

- **角色**：QuantLab Eng（主→Eng P2 预挖）
- **时刻（America/New_York）**：2026-10-25 ≈05:35 ET
- **live=false** · **禁抬帽** · **不改生产** · **不跑** moneyflow / book-smoke / 行情实跑
- **依据**：代码只读 + 既有回执/meta/manifest；**未**打开真实面板做 schema/内容读（Arch 06:45 规则）

## 0. 一句话结论

1. **lowmem v1.1 VOID（VmHWM=2320.9@≈3s）发生在主进程读 trunk 权重/混合阶段**，book-smoke 子进程尚未形成有效产物；根因是 trunk 权重表 **`n_rows=3,595,176`（含大量非正权）整表 `pd.read_parquet`**，不是「单档 BOOK 仍必然 >2GB」。
2. **X2 单档 BOOK-only 引擎路径**在既有同类跑次上 peak≈0.65–0.78GB（entry_meta）；再叠加「父进程仍持有 3.6M 行 trunk」才会把**进程树**顶到 4.5GB（v0 VOID）。
3. **判断（非实测）**：在 **P0 复用 blended（或改为读 pos_weights / 列裁剪+weight>0 下推）+ 父进程在子进程前 `del`+`gc` 释放 trunk/sat** 前提下，单档 BOOK-only **有望稳定 ≤2GB**；仅靠 v1.1 的串行/去 C0/档间 gc **不够**（未触权重加载）。
4. 引擎侧仍有杠杆（`load_merged_panel` 整文件读、无 mmap、无日期下推），属 P2 补强；**等 Arch code_change**，本轮只落盘侧稿。

## 1. 证据链（sha / 行号）

### 1.1 VOID 与阶段归因

| 项 | 值 | 来源 sha8 |
|---|---|---|
| lowmem v1.1 VOID VmHWM | **2320.9 MB** @≈3.0s；样例 7.3→81.7→531.5→1225.7→1775.7→2320.9 | 回执 `489978db…` |
| out_dir 产物 | 仅 `VOID.json`；**无** blended / summary | 同上 |
| Strategy 归因 | 峰值在**主进程读权重/混合**；book-smoke 串行未形成有效产物 | 更深方案 `19b36b00…` |
| v0 VOID | VmHWM≈**4511.5**；blended **已写出**后 book-smoke 启动约 12s 内杀 | 旧回执 + Arch 裁定 `bffb843b…` |

### 1.2 关键源文件（本挖时 sha256）

| 文件 | sha256 |
|---|---|
| `research/strategy_moneyflow_stack_diag_v1.py` | `2dae9a91eb2caf11e3d08d46fa1f025dba4b83a1a497b5c1ab2ad16d70166616` |
| `quantlab/portfolio/book_smoke.py` | `1a5fa1aa6ab847bd1ecda4d01bd4bda88b23535edceb91021520261be3e8251b` |
| `quantlab/portfolio/v2_multisleeve_book.py` | `6adefbeb4e66bdd8856c748180b09fa0fbf071d8fe20f6ccdd70ff37a4a603b4` |
| `quantlab/platform/execution.py` | `373fed309f055888e83572d3fbef8f5b5052ebfcb208307962a272bca6fc486c` |
| `quantlab/data/v2_readers.py` | `84f07b1f94e2edf0c8bbff7cfcec63d75936908b01dc562d4403a879357e1f54` |
| `scripts_eng/core_x2_book_smoke.py` | `5d83ecaaa77a773a1f1940c23bf2361138d73f2248203802ec24c4ce0efd6332` |
| lowmem DIFF | `e5e0b6da101f3dc7b7c6c9b6d8d39959f309a146ac0c3909916d1ee3cc2d5739` |
| VOID 回执 | `489978dbeb3a80421244357776903191bb327062cf51d2471ff0672bc21c7729` |
| 更深方案 | `19b36b00facb9d09b033fbdd8690c12d42a7b0f73f8a14465986549f179e12e5` |

### 1.3 权重表体量（meta / check；未开 parquet 内容）

| 表 | 磁盘 | n_rows | 正权行 | n_instruments | 备注 |
|---|---|---|---|---|---|
| trunk `…capacity_adv_hiliq_v1_1_daily_weights…parquet` | 12 278 694 B | **3 595 176** | **17 368** | 5382 | `.parquet.meta.json` + `.check.json` |
| sat `g1g5_moneyflow_resid_…parquet` | 33 430 B | 32 732 | （稠密） | 49 | sat meta |
| blended（recovery） | 52 440 B | （log：**31 311** 行 / 570 sessions） | — | — | v0 `book_smoke/run.log` |
| **已有** `…_pos_weights.parquet` | **44 406 B** | （正权子集） | — | — | 同 legs 目录，诊断脚本**未用** |

### 1.4 诊断脚本加载（混合阶段 = 2320 窗口）

`strategy_moneyflow_stack_diag_v1.py`：

- L280–307 `_load_weights`：`d = pd.read_parquet(path)` → **无 columns / 无 filters** → 再 `d[weight>0].copy()`  
  → trunk 先物化 **359 万行** 再裁到 1.7 万正权行；峰值由整表决定。
- L768–787：`trunk_w`/`sat_w` 常驻 → `blend_weights` → `prepare_smoke_weights`；**无** `del trunk_w` / 无 reuse-blended 捷径。
- L823：`turnover_2s_mean(blended)` 会 `pivot_table`（宽表临时峰，相对 trunk 整表次要）。
- lowmem v1.1 DIFF **只改** `run_book_smoke` 调用环（单档串行、`--arms BOOK`、档间 `gc`）；**未改** `_load_weights` / 混合路径 → 与 2320@3s「未写出 blended」一致。

### 1.5 X2 BOOK-only 引擎路径（book-smoke 子进程）

调用链（diag → CLI → 引擎）：

1. `quantlab.cli book-smoke --run-nav --windows X2 --capitals <单档> --arms BOOK --stock-path <blended>`  
2. `book_smoke.run` L105：`D = Data(with_cb=False, with_ind_etf=False)`  
   - L76：`pd.read_parquet(etf_daily_adj.parquet, filters=[ts_code in ETF_CODES])`（文件约 **69MB**；有 pyarrow filter，但仍可能按 row group 放大）  
   - **不**读 CB 日表（`with_cb=False`）  
3. `WeightLongTableSleeve._load` L349：`pd.read_parquet(weights)` **整文件**（blended≈52KB 可忽略；若误传 trunk 则再炸）  
4. `run_book` L492–495：对 HFQ 外个股调 `load_execution_panels(codes, a, b, corporate_actions=True)`  
5. `load_execution_panels` L1257–1269：对每个 id **`load_merged_panel` 后**再窗切 `[lo,hi]`  
6. `load_merged_panel` L1769–1786：`pd.read_parquet(d0_path)` + `pd.read_parquet(ext_path)` → **按标的整文件、无日期下推、无 mmap、无列裁剪**；D0 panels 目录合计 ≈1.3GB / 6026 文件，单文件均 ≈227KB  
7. `run_weight_schedule(..., record_weights=True)`：目标/实际权重 float32 矩阵常驻

既有对照（非本轮实测）：

| 跑次 | peak_rss_mb（entry_meta RUSAGE_SELF） | 窗/臂 |
|---|---|---|
| `_dryrun_capadv_hiliq_60w` | **655** | X2 / strategy_v1 |
| `book_smoke_v1_3_equity_100_60w` | **774** | X2 |
| `book_smoke_v1_3_equity_100_100w` | **758** | X2 |
| capadv_x2 BOOK summary | `n_codes=**233**`, `n_signals=570` | 全窗并集码 |

v0 `book_smoke/run.log`（双档+BOOK,C0）：sleeve 已 consumable（31311×570）后进程树被杀 → 与「父持 trunk + 子启 Data/panels」叠加模型一致。

## 2. A–E 答题

### A. X2 / BOOK-only 加载了什么？

| 层 | 表/对象 | 全列？ | 引擎 | mmap？ | 日期窗 | 副本/扇出 |
|---|---|---|---|---|---|---|
| 诊断主进程 | trunk 359 万行权重 | 是（整表） | pandas parquet | 否 | 否（先全读） | `.copy()`×多次；与 sat/blended 并驻 |
| 诊断主进程 | sat ≈3 万行 | 是 | pandas | 否 | 否 | 剥舱再 copy |
| book-smoke | `etf_daily_adj`（≈7 码 filter） | ETF 宽列→pivot HFQ/AMT | pandas+filters | 否 | 否（filter 码） | E + HFQ + AMT |
| book-smoke | blended 权重长表 | 是（小） | pandas | 否 | schedule 内再切窗 | sleeve 探测+每臂可能再读 |
| book-smoke | D0+asof 每股整文件 → 再切 X2 | 全列 merge | pandas 逐文件 | 否 | **读后**才 `[lo,hi]` | 逐标的临时峰 + 宽面板并集 |
| book-smoke | dividend CA | 事件表再 unstack | pandas | 否 | 按 index 对齐 | cash_div/share_ratio 宽表 |
| book-smoke | TW/AW/nav | float32 | numpy/pandas | — | X2 | `record_weights=True` |

**不是** moneyflow_stock_daily_pit 面板进 book-smoke；moneyflow 只以 **卫星权重 parquet** 进入混合。

### B. 峰值驱动排序（研究披露）

1. **P0（已观测）**：trunk **359 万行**整表进内存（2320@3s；无 blended）  
2. **P0′（v0 树峰）**：父进程保留 trunk/sat/blended **同时** 子进程 `Data()`+`load_execution_panels`（→4511）  
3. **P1**：`load_merged_panel` 每股全历史 D0+extend（无日期下推）；码并集≈**233** 时串行放大分配器碎片 / 临时副本  
4. **P2**：`etf_daily_adj` 69MB 文件 + pivot 双份（HFQ/AMT）；`turnover_2s_mean` pivot；双档/双臂同进程（v1.1 已去掉）  
5. **P3**：宽执行面板 + `record_weights`（量级通常远小于 1–2；对照 entry_meta <1GB）

### C. 不抬帽杠杆（具体）

| # | 杠杆 | 落点 | 预期 |
|---|---|---|---|
| L1 | **复用钉死 blended**（硬链/拷贝+sha MATCH；不 `read_parquet` trunk/sat） | diag 脚本 / run.ok `reuse_blended_path` | 直接消灭 2320 根因；对齐更深方案 P0 |
| L2 | 若必须重算：读 **`…_pos_weights.parquet`** 或 `read_parquet(columns=[…], filters=[('weight','>',0)])` | `_load_weights` | 3.6M→≈1.7 万行级 |
| L3 | 写出 blended 后 **`del trunk_w,sat_w,blended; gc.collect()`**，再 `subprocess`；可选 `posix_spawn`/新解释器已满足隔离 | diag | 树峰≈子进程单峰 |
| L4 | 引擎：`load_merged_panel` / 执行加载支持 **session 下推或按年分片**；列白名单；可选 `memory_map=True` | `v2_readers` / `execution` | 降子进程尖峰与碎片 |
| L5 | book-smoke：权重只读三列；`Data()` 后尽快丢原始 `E` 长表只留 HFQ 所需；档间已有子进程退出 | book_smoke / Data | 次要 |
| L6 | 单档试探（更深方案 P1） | run.ok tiers | 披露级，不替代两档终跑 |

**明确不做**：把 `rss_cap_mb` 抬过 2048；并行双档；恢复 C0；扩 CMC。

### D. 相对 lowmem v1.1 的缺口

v1.1 **已宣称且落地**：分档串行、`--arms BOOK`、`aum_*` 子目录、档间 `gc`（DIFF `e5e0b6da…`）。

**未覆盖**：

- trunk 整表加载 / 无 reuse-blended  
- 父进程在子进程生命周期内释放权重  
- 引擎面板日期下推 / mmap / 列裁  

故：**v1.1 解决的是「双档+C0 同驻」；2320 死在更上游的混合阶段** → BOOK-only 尚未被本次 VOID 证伪，但「只靠 v1.1」不能保证 ≤2GB。

### E. 侧稿

见同目录：

- `SIDE_diag_reuse_or_posweights_NOTES_ZH.md` + `strategy_moneyflow_stack_diag_v1_SIDE.py.draft`（仅示意片段，**不覆盖** `research/*.py`）  
- `SIDE_engine_windowed_merged_panel_NOTES_ZH.md`（引擎杠杆说明；无生产补丁落地）

**await Arch code_change**；本轮不请求 Arch `.ok`（侧稿 `py_compile` 可选，见 DIFF 笔记）。

## 3. 判断：BOOK-only 能否 ≤2GB？

| 条件 | 判断 |
|---|---|
| 维持现状（整表读 trunk + 父持对象跑子进程） | **不能**（已见 2320 / 4511） |
| P0 reuse-blended **或** pos_weights/下推 + 父释放后再单档 BOOK | **大概率能**（对照单进程 book-smoke entry_meta 0.65–0.78GB，留余量给树监控） |
| 仅引擎窗口化、仍整表读 trunk | **不能**（死在混合） |

此为代码+回执判断，**非本轮实测**。

## 4. 约束遵守

- 禁抬帽 · 不改生产脚本 · 不跑 moneyflow/book-smoke/行情  
- 未更新 `TEAM_STATE`（交父 Agent）  
- 未开真实面板 schema  

## 5. 请 Arch / 主下一步（Eng 不擅自执行）

1. 废/归档 live `42a16384…`（若尚未）；采纳 **reuse-blended（主裁 P0）** 并签 code_change。  
2. 可选并行：diag `_load_weights` 防呆（禁再吞 359 万行 dense 表）+ Eng 引擎窗口读（本目录侧稿）。  
3. 新 run.ok：`rss_cap_mb=2048` 不变；避叶25。

live=false。
