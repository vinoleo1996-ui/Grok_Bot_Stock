# moneyflow 诊断 — 更深降内存方案（交 Arch；禁抬帽）

- **时刻**：2026-10-25 ≈05:28 ET · America/New_York
- **作者**：QuantLab Strategy
- **依据**：lowmem v1.1 回执 `docs/v2/STRATEGY_MONEYFLOW_STACK_DIAG_LOWMEM_V11_RECEIPT_20261025_ZH.md` sha `489978db…`
- **观测**：显式 `--out-dir` 后约 **3.0s** VmHWM 爬至 **2320.9MB**（>2048）被外挂杀死；out_dir **仅 VOID.json**（无 blended/summary）→ 峰值发生在 **主进程读权重/混合阶段**，book-smoke 串行尚未形成有效产物
- **对照**：v0 双档+BOOK,C0 曾见 VmHWM≈4511；v1.1 已降到≈2321，仍破 2GB
- **锁**：禁自行把 rss_cap 抬过 2048；禁复用废签；live=false

## 请 Arch 裁（按优先）

### P0 — 复用已冻结 blended，跳过再读 trunk+sat
- recovery 已有 `blended_weights_8020.parquet` sha **`3f8a2b33…`**（与 .ok expected 一致）
- 改脚本：若 run.ok 钉 `reuse_blended_path` + sha MATCH，则 **只拷贝/硬链到 out_dir**，不 `read_parquet` 两张腿、不重算混合
- 预期：主进程峰值大幅下降；随后仍要面对 **单档 book-smoke** 是否单独 >2048

### P1 — 单档试探（仅 60万）另签
- 若 P0 后 book-smoke 仍破 2048：先只跑 `tiers=600000` 出门B 敏感性；100万另签
- 主结论若必须两档，则此为披露级，不替代两档终跑

### P2 — Eng 查 book-smoke / 面板加载
- 请 Eng：X2 单档 BOOK-only 为何仍可能冲 >2GB；是否整表进内存、可否列裁剪/mmap/分窗
- Strategy 不擅改引擎；需 Eng 补丁 + Arch code_change/run

### P3 — 非 book-smoke 轻量净值（仅当 Arch 裁定另口径可接受）
- 用已混合权重 × 已有日收益面板估相对 capadv 的差（**默认仍以 book-smoke 为准**；本项仅备选）

## 明确不做
- 把帽抬到 2.4/4.5GB 硬跑（除非 Leo/主 Agent 改口且 Arch 重签）
- 并行双档、恢复 C0、扩 CMC、动纸面

## 请 Arch 下一步
1. 作废/归档 run.ok `42a16384…`（仍在 live 路径）  
2. 是否采纳 **P0 reuse-blended**（Strategy 交 DIFF 前要 code_change .ok）  
3. P0 后若仍破帽：签 P1 单档或转 P2 Eng  

Strategy：等废签+新裁前不跑、不抬帽。
