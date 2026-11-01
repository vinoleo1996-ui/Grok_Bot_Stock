# Arch 审阅：叶30 CRR α 构建 R3 降峰提案（只审不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审阅） |
| 时刻 | `2026-10-27T00:07:30-04:00`（America/New_York；墙钟 `2026-10-27 00:07 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| **A vs B 裁择** | **APPROVE_A**（PRIMARY=按 rebal **日**懒加载）；B 仅文档可选，**不得**默默混入无闸 |
| 本回合动作 | **只审不签**；**不**签任何 `.ok`；**不**挂 QUIET；**不**创建/修改任何 `research/leaf30_*` 脚本；**不**改 R2 `0a264402`；**不**代跑；**不** RESTORED `5af20222`/`5ae077fa`；禁抬 rss；**≠X2 ACCEPT**；live=false；**不报 Leo** |
| 触发 | 主 ~00:04 ET priority · 叶30 R3 降峰提案只审不签（提案 `f111671a`） |

## 0. 一句话

提案 **`f111671a` MATCH**：根因钉「整窗 `logmv_rebal` 预载 → `after_logmv_rebal` peak=1433684≥split → rc=94」与基盘 R2 **`0a264402`** L1099–1101 / `_load_logmv_t1` 区间语义 **自洽且复核成立**。PRIMARY 意向废除整窗预载 → **APPROVE_A**（按 rebal 日懒加载 + 用完 del+gc + 日界 `_rss`）。月桶 B 仅作可选退路文档；落脚本须钉 PRIMARY=A，禁无闸混入 B。本拍 **不签 / 不挂 / 不落脚本**；下一跳由主排 AI 落 `…_r3_peakcut.py` → Arch 再只审脚本 → 另排独立 X2 签窗。

## 1. 钉表再核（本机 sha256）

| 件 | 路径 / 值 | 期望 sha8 | 实测全长 | 结果 |
|---|---|---|---|---|
| AI R3 提案 | `docs/v2/audit/AI_LEAF30_CRR_ALPHA_BUILD_R3_PEAKCUT_PROPOSAL_20261026_ZH.md` | `f111671a` | `f111671abc41dd954f59aa6945d378462f545522588b461af916697173be83c1` | **MATCH** |
| R2 脚本（基盘·禁改） | `research/leaf30_crr_cfooe_volpen_alpha_build_r2_chunk.py` | `0a264402` | `0a2644021e8bbd16cbe7f69905a6a6dfcd47df3c798b6f5b272f7b6702220260` | **MATCH · 未改** |
| 拟 R3 脚本 | `research/leaf30_crr_cfooe_volpen_alpha_build_r3_peakcut.py` | ABSENT | — | **ABSENT** |
| AI R2 跑回执 | `docs/v2/audit/AI_LEAF30_CRR_ALPHA_BUILD_R2_X2_RUN_RECEIPT_20261026_ZH.md` | `fe5a2c1e` | `fe5a2c1e049c5c2f45af91a1d20a3389855a4a438920e6bd5087802967bafb09` | **MATCH** |
| Arch R2 VOID | `docs/v2/audit/ARCH_LEAF30_CRR_ALPHA_BUILD_R2_VOID_ABORT_PEAK_HWM_20261026_ZH.md` | `df47501c` | `df47501c6c9f2b1406e346ed877f4abe754ee8f5981413843af339d9555d3822` | **MATCH** |
| Arch R2 chunk 审 | `docs/v2/audit/ARCH_LEAF30_CRR_ALPHA_BUILD_R2_CHUNK_REVIEW_20261026_ZH.md` | `1b672b67` | `1b672b6732d00b31410ce53e403e93e19876c0025e8a357c7f96aa8fdd75b240` | **MATCH** |
| QUIET lift | `output/loop/_lifted/RESEARCH_QUIET_leaf30_r2_ABORT_PEAK_HWM_LIFTED_20261026T2358ET.lock` | `41edf798` | `41edf798569dfe165f5c43ba1a7a211930290eecade7a744f562bb9537ae0c9f` | **MATCH** |
| VOID `.ok` R2 archived | `_consumed/…R2_HILIQ_X2.5af20222.VOID.ABORT_PEAK_HWM.20261026T2358ET.ok` | 内容 `5af20222` | live **ABSENT**；archived **在位** | **OK** |
| VOID `.ok` R1 archived | `_consumed/…HILIQ_X2.5ae077fa.VOID.…ok` | 内容 `5ae077fa` / VOID 审 `ff30406f` | live **ABSENT**；archived **在位** | **OK** |
| live leaf30 `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF30*` | ABSENT | — | **ABSENT** |
| live QUIET | `output/loop/RESEARCH_QUIET.lock` | ABSENT | — | **ABSENT** |

## 2. 根因核验（对照 R2 只读）

| # | 主张（提案） | Arch 核 | 证据 |
|---|---|---|---|
| R-1 | abort 标签 `after_logmv_rebal`；peak_kb=**1433684** ≥ split=**1131520** → rc=**94** | **PASS** | AI 回执 `fe5a2c1e`；VOID `df47501c`；提案 §1 Abort 事实表与主令一致 |
| R-2 | avail logmv 已月桶疏散；daily month-chunk 已写但 **未到达** | **PASS** | R2 L1058–1082 月桶 + `del`+`gc`+`_rss(after_logmv_avail_*)`；abort 早于 expand → `after_daily_concat` 未检（提案自洽） |
| R-3 | 再平衡侧仍 **整窗一次** `_load_logmv_t1(..., rebal_days, codes)` | **PASS** | R2 L1099–1101：`logmv_rebal = _load_logmv_t1(...); _rss("after_logmv_rebal")`；`del logmv_rebal` 仅在整窗循环后 L1160 |
| R-4 | `_load_logmv_t1` 对 dates 取 **连续** `[min−10d, max]` 并对 **全部** codes 拼盘 | **PASS** | R2 L615–671：`dmin/dmax` 连续区间 + ids 分批读 parquet → concat → `by_code` 按日 T−1；即便 `rebal_days` 稀疏（~20td），`min→max` 仍近全窗 float 驻留 |
| R-5 | 尖峰叠加已驻留 `panel`/`sw`/`by_day` → 破 split | **PASS** | 序列末 `after_vol_pen` peak=921616 → `after_logmv_rebal` 1433684 STOP；归因合理 |
| R-6 | **一句话根因**：疏散了 avail/daily，**未疏散**整窗 `logmv_rebal` 预载 | **PASS** | 与脚本结构一致；提案无夸大、无甩锅 daily |

**根因结论**：**APPROVE 归因**。R3 必须废除整窗 `logmv_rebal` 预载；否则重跑 `0a264402` 必再现 Exit 94（禁盲重跑）。

## 3. A vs B 裁择

| 路径 | 定义 | 峰值 | I/O | 实现 | Arch |
|---|---|---|---|---|---|
| **A** | 按 **每个** rebal 日 `_load_logmv_t1([d], …)` → 用完 `del`+`gc` → `_rss(after_logmv_rebal_YYYYMMDD)` | **最低**（日期窗缩至 ~10d） | 更高（~20 次读） | 更碎 | **PRIMARY · APPROVE** |
| **B** | 按日历月桶分组 rebal_days（镜像 avail）→ 月内循环消费 → 月界释放 | 可能略高（月内仍连续区间） | 更省 | 与 R2 avail 同构 | **仅文档可选** |

### 裁择理由（APPROVE_A）

1. **失败模式是峰值不是 I/O**：R2 已在 split 闸硬停；首要目标是 peak≪split（提案设计目标 peak≪1000MB 留裕；硬帽仍 1500 禁抬）。
2. **A 直接收缩 `_load_logmv_t1` 区间**：单日 `dates=[d]` → `[d−10d, d]`，避免整窗 float 面板驻留——对症。
3. **B 仍可能叠峰**：月桶在 x2 跨多月时单月区间仍宽；叠加 `panel`/`sw`/`alpha_rebal_rows` 累积，峰值裕度不确定；可作为 I/O 过慢时的 **显式退路**，不得默认。
4. 提案已把 A 作 preferred、B 作 throughput 选项——**同意该分层**；CONDITIONS 钉死落脚本/签文 PRIMARY=A。

**VERDICT 裁择行**：**APPROVE_A**（PRIMARY）；B=optional-doc-only。

## 4. 硬保留闸（须入落脚本 + 签文）

| # | 闸 | 提案是否写入 | Arch |
|---|---|---|---|
| H1 | overlap **必产** `overlap_vs_leaf19_25.json`；签文 **禁** `--no-overlap-report`；Jaccard≥0.7 硬拒；ρ>0.5 强度 | §3.5 / §5 **有** | **须入** |
| H2 | `peak_proof` **REQUIRED**（ru_maxrss/VmHWM/`RSS_CHECK` 全序列）；**含** `after_daily_concat` + 新 `after_logmv_rebal_*` | §3.4–3.5 / §5 **有** | **须入** |
| H3 | 硬 Exit **94/95** on peak；**rss=1500 禁抬**；禁抬 C4/stop/hard | §3.5 **有** | **须入** |
| H4 | forbid∋**`5af20222`**+**`5ae077fa`** + 既有十五票基 → **16**；禁 RESTORED；禁盲重跑 r1 `a2cef5af` / 以 R2 `0a264402` 作新票脚本（可作复制源，新文件须新 sha） | §3.5 **有** | **须入**（落脚本时 FORBID 首项增 `5af20222`） |
| H5 | `qend_ok_filter=true`；C2 OP+OCF；λ=1.0；银/地/非银掩码；HILIQ×x2；授权双闸；live=false；≠X2 ACCEPT | §3.5 **有** | **须入** |
| H6 | sampler `/tmp/quantlab_leaf30_crr_r3_*`；out `_leaf30_crr/<ET_TS>/` | §3.6 **有** | **须入** |

## 5. CONDITIONS（落脚本 / 签文硬闸）

1. **PRIMARY=A 钉死**：落盘 `…_r3_peakcut.py` 必须实现 **按 rebal 日**懒加载；循环内 `logmv_d = _load_logmv_t1(..., [d], …)` → 仅消费当日 → `del logmv_d; gc.collect(); _rss(f"after_logmv_rebal_{YYYYMMDD}")`。**禁止**整窗 `logmv_rebal = _load_logmv_t1(..., rebal_days, …)` 残留。
2. **B 不得默默混入**：月桶 B 仅提案/文档可选；若落脚本采用 B，须 **显式** `load_mode=month_bucket`（或等价 CLI/常量）+ dry-compile 钉 + Arch **另审**；默认路径 **无闸混 A+B 禁止**。
3. **新文件新 sha**：由 R2 `0a264402` **复制派生**；r1 `a2cef5af` / R2 **均不改**；schema=`…_r3_peakcut`；`prev_script_sha8=0a264402`；void_ref 含 `df47501c` / `fe5a2c1e` / VOID ok `5af20222`。
4. **forbid 扩至 16**：`FORBID_OK_SHA8` 须含 **`5af20222`**（建议首项）+ **`5ae077fa`** + 原十五票其余；dry/真跑 STOP on forbid。
5. **C3 / peak_proof / Exit / rss**：同 §4 H1–H3；签文硬禁 `--no-overlap-report`；真跑须披露含 `after_daily_concat` 的 peak_proof。
6. **PIT / 对齐**：懒加载须保持 T−1（`trade_date < asof`）语义与 R2 一致；若取可选「codes=当日 HI_LIQ members」削峰，须证明与全宇宙 codes 映射结果在成员交集上 **数值一致**，且不引入未来函数。
7. **可选 alpha_rebal 月 flush**：非 PRIMARY；若做，须证明对最终 α 数值语义无变（仅改驻留形态），并加 `_rss(rebal_flush_YYYYMM)`；**不得**借 flush 改写出 schema / 改 λ / 改掩码。
8. **残留峰预案（文档级，本拍不扩 scope）**：R2 未到 `after_daily_concat`；即使 A 过 `after_logmv_rebal_*`，concat 残峰仍可能逼近 split → 真跑 peak_proof 监控；破闸 → 94/95 上报，**禁抬帽**；下一票再削（流式写/分片出），本提案/本拍不预改写出格式。
9. **本拍非动作坚持**：不签 `.ok`；不挂 QUIET；不落/不改脚本；不代跑；不 RESTORED；不报 Leo；≠X2 ACCEPT。
10. **下一跳（仅文档；本拍不执行）**：主令 AI 落 `…_r3_peakcut.py` → Arch **只审脚本** → 主另排独立 X2 签窗 → 新 `.ok`（钉 r3 sha8；forbid∋`5af20222`+`5ae077fa`；rss=1500；C3/peak_proof）→ AI prelaunch→execute → Arch CONSUME。

## 6. 残留风险（知情接受）

| 风险 | 等级 | 备注 |
|---|---|---|
| `after_daily_concat` 残峰未在 R2 实测 | **中** | 须 peak_proof；破则下票削，禁抬帽 |
| 按日 I/O 变慢 | **低–中** | 可接受；若不可用再 **显式** 走 B 另审 |
| 可选 codes 收窄破坏 PIT/覆盖 | **中（若启用）** | 默认建议先全 codes 按日；收窄须数值对照票 |
| alpha_rebal 月 flush 改语义 | **中（若启用）** | 须等价证明；默认可不做 |
| 单进程 RSS≤1.5GB 仍紧 | **中** | A 为必要非充分；密检 + 94/95 硬停保留 |
| 盲重跑 / RESTORED | **管控** | forbid+签文+本审禁项 |

## 7. 禁项 / 本回合非动作

- **未签**任何 `.ok`（含新叶30 / RESTORED `5af20222` / `5ae077fa`）
- **未挂** QUIET；live QUIET **ABSENT**（未改）
- **未创建 / 未改** `research/leaf30_*`；R2 **`0a264402` 未改**；R3 脚本仍 **ABSENT**
- **未** `--allow-real-data` / **未**代跑 / **未**抬 rss
- **未**触 A18 产物；**≠X2 ACCEPT** / ≠selfcheck / ≠Book-Smoke
- **未** SendToUser / **未**报 Leo（leo_notify=false）

## 8. 结论

| 项 | 值 |
|---|---|
| VERDICT | **PASS_WITH_CONDITIONS** |
| CHOICE | **APPROVE_A**（PRIMARY=按 rebal 日懒加载） |
| B | 文档可选 only；默默混入 **禁** |
| 提案 | **`f111671a` MATCH** |
| 基盘 | **`0a264402` 未改**；拟 r3 **ABSENT** |
| 请主 | 排 AI **落脚本窗**（`…_r3_peakcut.py`，PRIMARY=A + §5 CONDITIONS）→ 再令 Arch 只审脚本 → 另排独立 X2 签窗 |
| live | **false** |
| leo_notify | **false** |

live=false · leo_notify=false · ≠X2 ACCEPT · 只审不签不挂不落.
