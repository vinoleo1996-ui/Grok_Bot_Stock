# Arch 复审：叶30 CRR α 构建脚本 R2 chunk 降峰补丁（只审不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态复审） |
| 时刻 | `2026-10-26T18:30:20-04:00`（America/New_York；墙钟 `2026-10-26 18:30 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 本回合动作 | **不签**任何叶30 `.ok`；**不挂**新 QUIET；**不代跑** `--execute` / `--allow-real-data`；**不改**脚本/r1/`a2cef5af`/AI 回执；**不 lift / 不触** A18 QUIET **`bf4548d4`** / `.ok` **`a62881b9`**（Eng EXEC_V2 另线 pid 已跑）；禁 RESTORED `5ae077fa`；禁抬帽；叶26 不交审；28/29 FROZEN；**≠X2 ACCEPT**；live=false；**不推 Leo** |
| 触发 | 主 ~18:27–18:29 ET priority · 叶30 R2 chunk 复审（对照 VOID `ff30406f` / abort `40fd90e9` / AI `2618c688`） |
| 轻量复跑 | `py_compile` **PASS**；`--dry-compile-only` exit **0**（零大表）；未 `--allow-real-data` |

## 0. 一句话

新脚本 sha8 **`0a264402`**（r1 **`a2cef5af` 未改**）相对 VOID **`ff30406f`**（VmHWM 2429160 @ after_fund 后间隙）**降峰路径已闭环**：avail logmv **月桶** + 日度 **月 chunk** 落盘/`del`+`gc` + 密检 `peak_kb=max(ru_maxrss,VmHWM)`→Exit **95**；forbid∋**`5ae077fa`**；rss=1500 禁抬；`qend_ok_filter`/C2 OP+OCF/λ=1.0/掩码/HILIQ×x2/授权闸 **无回归**。**本拍仍不签** X2 `.ok`。残留 CONDITIONS：C3 签文禁 `--no-overlap-report`；真跑 **peak_proof**（含 `after_daily_concat` 残峰）；**独立签窗须错开 A18** QUIET `bf4548d4`。

## 1. 钉表再核（本机 sha256）

| 件 | 路径 | 期望 sha8 | 实测全长 | 结果 |
|---|---|---|---|---|
| R2 脚本 | `research/leaf30_crr_cfooe_volpen_alpha_build_r2_chunk.py` | `0a264402` | `0a2644021e8bbd16cbe7f69905a6a6dfcd47df3c798b6f5b272f7b6702220260` | **MATCH** |
| AI R2 回执 | `docs/v2/audit/AI_LEAF30_CRR_ALPHA_BUILD_R2_CHUNK_PATCH_RECEIPT_20261026_ZH.md` | `2618c688` | `2618c6880e44f537f761c045d8691a594619e0672961a56b70eec962dac07970` | **MATCH** |
| 对照 VOID | `docs/v2/audit/ARCH_LEAF30_CRR_ALPHA_BUILD_VOID_ABORT_PEAK_HWM_20261026_ZH.md` | `ff30406f` | `ff30406f804f265ccdbd7dc9eb64224c10ec89cbecc80ff527687ea6bdac7b88` | **MATCH** |
| 对照 abort | `docs/v2/audit/AI_LEAF30_CRR_ALPHA_BUILD_X2_RUN_RECEIPT_20261026_ZH.md` | `40fd90e9` | `40fd90e9389b9985df2179f66789021cc3b2e256255f8196a1e38b0f5ff85290` | **MATCH** |
| r1 脚本（禁改） | `research/leaf30_crr_cfooe_volpen_alpha_build_r1.py` | `a2cef5af` | `a2cef5affd67f874fad9e37f59efb9d7abacb3de0d0286d8443250aee5253c74` | **MATCH · 未改** |
| 前审 R1 | `docs/v2/audit/ARCH_LEAF30_CRR_ALPHA_BUILD_R1_QEND_REVIEW_20261026_ZH.md` | `02a8477a` | `02a8477a0df9064680d122bf3102641a3e6e2ceb2ad0303cb15d6ebe6a5f5756` | **MATCH** |
| 前审构建 | `docs/v2/audit/ARCH_LEAF30_CRR_ALPHA_BUILD_SCRIPT_REVIEW_20261026_ZH.md` | `d1c71ece` | `d1c71ece64f71f2927d766fa1bf6df45d19aaf53ec427d0ac7b0743704255635` | **MATCH** |
| 预注册审 | `docs/v2/audit/ARCH_LEAF30_CRR_WHO_PAYS_PREREG_REVIEW_20261026_ZH.md` | `f61ffb05` | `f61ffb052192810e908e931032442b6a62381e1ab1ad09fcb0245657893d47b0` | **MATCH** |
| FROZEN | `docs/v2/AI_LEAF30_CRR_CFOOE_VOLPEN_WHO_PAYS_FROZEN_20261026_ZH.md` | `93cad965` | `93cad965bd9aa34b6bb8dc5e43d6f0095c4d111420c5fa53b196ad4220d40fba` | **MATCH** |
| A18 EXEC_V2 `.ok` | `output/data/ARCH_RUN_AUTH_DAILY_BASIC_A18_SECTION_5_3_BASELINE_EXEC_V2.ok` | `a62881b9` | `a62881b9f9078cf3…`（本审只读核 sha8） | **live · 本审未触** |
| A18 QUIET | `output/loop/RESEARCH_QUIET.lock` | `bf4548d4` | `bf4548d48a8eb16c1cfc45d6f7d5245b45ed4cd60808faf0d8f8bcd8f34a57dd` | **live · 本审未 lift/未改** |

## 2. 降峰闭环逐项（对照 VOID after_fund 间隙）

| # | 要点 | 结果 | 证据 |
|---|---|---|---|
| R2-1 | **月桶 avail logmv** | **PASS** | `build_alpha_for_window`：`avail_days` 按 `(year,month)` 分桶 → `_load_logmv_t1` → 映射入 `logmv_by_end` → `del logmv_avail, sub` + `gc.collect()`；边界 `_rss(f"after_logmv_avail_{yy}{mm:02d}")` + 汇总 `after_logmv_avail`；注释钉禁 r1「注释 month-ends、实际全 avail densify」 |
| R2-2 | **日度按月 chunk + 显式释放** | **PASS** | `_month_chunks`；`--chunk-mode` 仅 `month`；每月写 `/tmp/quantlab_leaf30_crr_r2_chunk_*/*.parquet` 后 `del cdf, table, month_rows` + `gc.collect()` + `_rss(month_chunk_*)`；禁一次堆满全日 `daily_rows` |
| R2-3 | **密检 peak → Exit 95** | **PASS** | `peak_kb=max(ru_maxrss,VmHWM)`；`check_rss` hard → `SystemExit(95)`；soft/split → 94；采样：`after_fund` → `after_logmv_avail_*` → `vol_pen_end_*`（每 4 end）→ `after_vol_pen` → `after_logmv_rebal` → 再平衡中途 → 每月 chunk 边界 → `after_daily_concat`（密于 r1；闭合 VOID「last check=after_fund 后无检」洞） |
| R2-4 | **forbid∋`5ae077fa`** | **PASS** | `FORBID_OK_SHA8` **15** 票，首项 `5ae077fa`（VOID.ABORT_PEAK_HWM）；另含叶25/A18 `6de02e74` 等；dry `sign_notes.ban_restored_ok_5ae077fa=true` / `ban_blind_rerun_a2cef5af=true`；真跑 `ok_sha[:8] in FORBID` → STOP exit2 |
| R2-5 | **rss=1500 禁抬** | **PASS** | `RSS_LIMIT_MB=1500` / `HARD_KB=1536000`；`rss_limit_mb>1500` 或抬 C4/stop/hard → STOP；无抬帽后门 |
| R2-6 | **无回归机制钉** | **PASS** | 见 §3 |

## 3. 无回归 / 机制钉

| # | 要点 | 结果 | 证据 |
|---|---|---|---|
| 1 | `qend_ok_filter=true`（真滤） | **PASS** | `build_fund_quarter_panel` 缺列 STOP；`fin/cf = *[*.qend_ok]`；dry JSON `qend_ok_filter: true` |
| 2 | **C2** OP+OCF；禁 ocf 主源 | **PASS** | `operate_profit` + `n_cashflow_act`；名起 `ocf_to_profit` → STOP；`claims.ocf_to_profit_main=false` |
| 3 | **λ=1.0**；IC 正仅注释 | **PASS** | `LAMBDA_FROZEN=1.0`；`raw = r_crr - LAMBDA_FROZEN * r_vol`；不计算收益 |
| 4 | 银/地/非银掩码 | **PASS** | `EXCLUDE_SW` 801780/801180/801790 |
| 5 | C3 overlap 须消费；禁 `--no-overlap-report`（签文） | **PASS_WITH_CONDITIONS** | 真跑默认写 `overlap_vs_leaf19_25.json`；dry `ban_no_overlap_report=true` / `x2_sign_bans_no_overlap_report_flag=true`；CLI **仍保留** `--no-overlap-report`（help 钉签文将禁）→ **须入签文硬闸** |
| 6 | HILIQ×x2；授权双闸 | **PASS** | PRIMARY HILIQ×x2；FULLA/`window!=x2` STOP；`--allow-real-data` + 现存 `--arch-ok-path`；ok∉forbid；`--execute` 不旁路 |
| 7 | dry / compile | **PASS** | `py_compile` PASS；`--dry-compile-only` exit0；`r2_chunk=true` / `chunk_mode=month` / `schema=…_r2_chunk` |

## 4. 残留 CONDITIONS（另窗签新 X2 `.ok` 前）

1. **本拍不签**：须主另排**独立 X2 签窗**（**新** `.ok`；钉脚本 **`0a264402`**；**禁** RESTORED **`5ae077fa`**；禁盲重跑 r1 **`a2cef5af`**；禁复用叶25/`6de02e74` 等 forbid 十五票）。
2. **错开 A18 重进程**：现 QUIET **`bf4548d4`** / `.ok` **`a62881b9`** / Eng pid **`2950358`** STARTED（窗→**23:00** expires≈**23:02** ET）。签/真跑叶30 **须等** A18 QUIET 自然 ABSENT（或 Eng CONSUMED 后主排窗）；**禁 lift** `bf4548d4`；**禁动** `a62881b9`。
3. **C3 签文硬钉**：真跑**必须**写并消费 `overlap_vs_leaf19_25.json`；Jaccard≥0.7 → 硬拒票叙事；ρ>0.5 → 强度过滤；计数≠正式；签文 **禁** `--no-overlap-report`（CLI 仍在，靠签文/消费端闸）。
4. **peak_proof REQUIRED**：静态复审 ≠ 峰证明；真跑须披露 ru_maxrss/VmHWM/`RSS_CHECK` 全序列；破 soft/hard → Exit 94/95 停+上报，**禁抬帽**。残峰关注点：`after_daily_concat` 仍一次 `concat` 月分片入内存写 final parquet——若再破帽，下一票再削（流式写/分片出），**本拍不代改**。
5. **C2/λ/掩码/rss=1500/qend_ok_filter** 坚持入签文；sampler `/tmp/quantlab_leaf30_crr_r2_*`；out 隔离 `_leaf30_crr/<ET_TS>/`。
6. live=false · promotion=false · book_smoke=false · **x2_accept=false** · selfcheck=false · **≠X2 ACCEPT**。

## 5. 签窗建议（≠X2 ACCEPT）

```
A18 EXEC_V2 收口（QUIET bf4548d4 自然 ABSENT；.ok a62881b9 CONSUMED/归档）
  → 主另排独立叶30 X2 签窗（错开；禁与 A18 重进程叠峰）
      → Arch 签 **新** .ok（脚本 0a264402；禁 RESTORED 5ae077fa；钉 C3/peak_proof/rss=1500）
          → AI 真跑 HILIQ×x2（无 --no-overlap-report；peak_proof）
              → Arch CONSUME（≠X2 ACCEPT）
```

建议：A18 expires≈**23:02 ET** 之后或 Eng D1 后；勿与 A18 同窗抢 Mem。

## 6. 禁项 / 本回合非动作

- **未签**任何叶30 `.ok`；**未挂**新 QUIET
- **未** `--execute` / **未** `--allow-real-data` 真构建（仅 `py_compile` + dry）
- **未改** r2 脚本 / r1 `a2cef5af` / AI 回执 / FROZEN
- **未 lift / 未触** A18 QUIET **`bf4548d4`**；**未动** `.ok` **`a62881b9`**
- **未** RESTORED `5ae077fa`；**未**抬帽；**未**代跑
- **不推 Leo**；live=false；promotion=false；x2_accept=false

## 7. 结论

**PASS_WITH_CONDITIONS** — R2 chunk 降峰路径相对 VOID **`ff30406f`** 已静态闭环；钉全 MATCH；机制无回归；C3 签文闸 + 真跑 peak_proof + **错开 A18 `bf4548d4`** 仍开。**本拍不签** `.ok`；请主在 A18 重进程收口后排独立 X2 签窗。

live=false.

## 8. 本审钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/audit/ARCH_LEAF30_CRR_ALPHA_BUILD_R2_CHUNK_REVIEW_20261026_ZH.md` |
| 脚本 sha8 | **`0a264402`** |
| AI 回执 sha8 | **`2618c688`** |
| 结论 | **PASS_WITH_CONDITIONS**（降峰闭环；本拍不签；错开 A18） |

全文件 sha256 / sha8：以本机 `sha256sum` 为准（见 TEAM_STATE 顶条与父回报）。

live=false.
