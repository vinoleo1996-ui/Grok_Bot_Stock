# moneyflow 剥舱+80/20 诊断 — 降内存重跑方案（交 Arch）

- **时刻**：2026-10-25 ≈05:04 ET · America/New_York
- **作者**：QuantLab Strategy（主 Agent 05:03 令）
- **依据**：VOID 回执 `docs/v2/STRATEGY_MONEYFLOW_STACK_DIAG_RECEIPT_20261025_ZH.md` sha `12a095bf…`；VOID.json（VmHWM 4511.5MB @ PID 214222，杀时 VmRSS≈290MB，历时≈11.8s）
- **目标**：重跑峰值 **≤2GB**（主 Agent 指定）；**禁止**把 `rss_cap_mb` 抬到 4.5GB 硬跑
- **锁**：live=false · promotion=false · 禁 paper · 禁再单独 moneyflow 烟 · 旧 `.ok` `68c04741` 须 Arch 作废后才能重签

## 1. 根因判断（研究披露，非引擎审计结论）

当前脚本一次调用：

`book-smoke --run-nav --windows X2 --capitals 600000,1000000 --arms BOOK,C0`

即 **双档 AUM + BOOK 与 C0 两臂** 同进程加载。VOID 发生在 book-smoke 启动后约 12s、尚未写出 summary。同仓已有先例：`strategy_fulla_b4_x2.py` 对每个 AUM **分开** `--capitals <单档>` 调 book-smoke。

对照门只需 trunk 参考 NAV（已 pin 的 capadv_x2 nav.csv），**C0 臂对本诊断的门B/GATE_V3 不是必需**（门B/GATE_V3 相对 capacity_adv 单跑，不是相对纯 510300）。

## 2. 方案（请 Arch 裁）

### 推荐：脚本小改 v1.1（先 code_change .ok，再 run .ok）

改 `research/strategy_moneyflow_stack_diag_v1.py`（另文件名或同文件增量由 Arch 定；Strategy 建议 **同路径 v1.1 补丁**，DIFF 只动 `run_book_smoke` 调用环）：

| # | 改动 | 预期作用 |
|---|---|---|
| 1 | **分档串行**：对 600000、1000000 各调一次 book-smoke，`--capitals` 只含一档；上一档结束后再开下一档 | 避免双档净值对象同驻 |
| 2 | **臂收窄**：`--arms BOOK`（去掉 C0）；对照仍用 `.ok` 钉死的 trunk_ref_nav_* | 少加载一条对照臂 |
| 3 | **子目录隔离**：`book_smoke/aum_600000/`、`book_smoke/aum_1000000/`，各有 `run.log` + summary；主进程汇总进 `summary.json` | 失败可单档 VOID/重跑 |
| 4 | **可选 gc**：每档结束后 `gc.collect()`；子进程自然退出释放 | 压峰值 |
| 5 | **外挂 runguard**：run .ok 写明 `rss_cap_mb=2048`（主目标 ≤2GB），任一相关 PID VmHWM>2048 → SIGTERM→VOID | 不抬到 4.5GB |

**不做**：抬帽硬跑；并行双档；扩 CMC；改 Eng book-smoke 内核（除非 Eng/Arch 另开）。

### 备选（若分档后仍 >2GB）

- **B1**：只跑 60万出门B 敏感性，100万另签（主结论仍要两档时不采用）。
- **B2**：Eng 侧查 book-smoke X2 面板是否整表进内存；由 Eng 出降载补丁（Strategy 不擅改引擎）。
- **B3**：若仅需相对 capadv 的收益差，评估「已混合权重 × 已有日收益面板」的轻量净值（须 Arch 裁定是否算另口径，默认仍以 book-smoke 为准）。

## 3. 产物与目录

- 旧 out_dir `output/strategy_hiliq/moneyflow_stack_8020_20261025/`（含 blended/VOID）**整目录移入** `_recovery/strategy/20261025T0502ET_moneyflow_stack_void/`，或新 out_dir：
  - 建议：`output/strategy_hiliq/moneyflow_stack_8020_lowmem_20261025/`
- 已写出的 `blended_weights_8020.parquet`：可在新 run .ok 中 **pin 其 sha 复用**（跳过再剥舱混合），或强制重算；Strategy 倾向 **复用**（省一步、行为不变），须 Arch 钉 sha。

## 4. 预注册式判定（不变）

- 门B：两档 Calmar 严格优于 capacity_adv 且 MDD≤15%
- GATE_V3：两档 MDD≤25%、CAGR>capacity_adv、**decay KEEP**、双边换手≤20%/日  
  - 若新 `.ok` 仍钉 `decay_outcome=REJECT`，则 GATE_V3 预期仍不过（只披露）
- 退出码不算数；失败写 VOID.md/VOID.json；`ARTIFACT_MANIFEST.txt` 必交

## 5. 窗口与禁区

- 避开叶25 `10:00–10:45 ET`（及 Arch 另列窗）
- `output/loop/RESEARCH_QUIET.lock` 不存在；`[k]line` 等 pgrep 空
- 禁 paper / live / handoff

## 6. 请 Arch 裁定

1. 作废 `.ok` `68c04741`（仍在 live 路径）→ `_consumed` 或 VOID 归档。  
2. 是否采纳 **推荐 v1.1 分档+BOOK-only**；`rss_cap_mb` 定为 **2048** 还是维持 1536（分档后若仍破 1536 再议，仍 ≤2048）。  
3. 签 **code_change .ok**（允许改 diag 脚本）→ Strategy 交 DIFF → 审后再签 **run .ok**（新 out_dir、pin blended 复用与否、decay、expires）。  
4. 是否要 Eng 并行查 book-smoke 启动 12s 内 VmHWM≈4.5GB 的加载路径。

Strategy：**等废旧签 + 新 .ok 之前不跑、不抬帽。**
