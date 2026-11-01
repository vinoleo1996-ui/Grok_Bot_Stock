# Arch 审阅：叶30 CRR α 构建 R3 peakcut 脚本（只审不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审脚本） |
| 时刻 | `2026-10-27T00:22:00-04:00`（America/New_York；墙钟 `2026-10-27 00:22 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 对照裁择 | **APPROVE_A**（提案审 **`61830035`**） |
| 本回合动作 | **不签**任何 `.ok`；**不挂** QUIET；**不代跑** `--allow-real-data` / 真构建（仅 `py_compile` + `--dry-compile-only`）；**不改**任何脚本；R2 **`0a264402` 未改**；禁 RESTORED `5af20222`/`5ae077fa`；**≠X2 ACCEPT**；live=false；**不报 Leo** |
| 触发 | 主 ~00:17–00:20 ET priority · 叶30 R3 脚本只审（脚本 `3ee9fed2` / AI `4d951ea3` / 审 `61830035`） |
| 轻量复跑 | `py_compile` **PASS**；`--dry-compile-only` exit **0**（零大表；JSON 含 r3_peakcut/primary_load=rebal_day/forbid n=16） |

## 0. 一句话

脚本 **`3ee9fed2` MATCH**：自 R2 **`0a264402` 派生且基盘未改**；PRIMARY=A **按 rebal 日** `logmv_d=_load_logmv_t1(..., [d], codes)` → 用完 `del`+`gc` → `_rss(after_logmv_rebal_YYYYMMDD)` **已钉死**；整窗 `logmv_rebal = _load_logmv_t1(..., rebal_days, …)` **无残留**（R2 L1100 仍在、R3 无赋值）；B `load_mode` **未混入**；forbid 首项 **`5af20222`**+**`5ae077fa`**（n=**16**）；overlap/peak_proof/Exit94·95/rss=1500/qend_ok/C2/λ/掩码/HILIQ×x2/双闸 **无回归**。**本拍不签**；请主另排独立 X2 签窗。

## 1. 钉表再核（本机 sha256）

| 件 | 路径 / 值 | 期望 sha8 | 实测全长 | 结果 |
|---|---|---|---|---|
| **R3 脚本** | `research/leaf30_crr_cfooe_volpen_alpha_build_r3_peakcut.py` | `3ee9fed2` | `3ee9fed2c91a8c523128d9a0b0956f29a11fd2935d961e978aa07b9eafb0a182` | **MATCH** · 1569 行 |
| AI 落盘回执 | `docs/v2/audit/AI_LEAF30_CRR_ALPHA_BUILD_R3_PEAKCUT_SCRIPT_RECEIPT_20261026_ZH.md` | `4d951ea3` | `4d951ea3af8c4b81f21dde70d8679a26a5f8d1a0cd9a941a82bf410f19461a2b` | **MATCH** |
| 提案审 APPROVE_A | `docs/v2/audit/ARCH_LEAF30_CRR_ALPHA_BUILD_R3_PEAKCUT_PROPOSAL_REVIEW_20261026_ZH.md` | `61830035` | `61830035fb732ecc0e2d3277b22cee8ad6dcd0dce21988a685c537755d6f8b92` | **MATCH** |
| 提案 | `docs/v2/audit/AI_LEAF30_CRR_ALPHA_BUILD_R3_PEAKCUT_PROPOSAL_20261026_ZH.md` | `f111671a` | `f111671abc41dd954f59aa6945d378462f545522588b461af916697173be83c1` | **MATCH** |
| R2 基盘（禁改） | `research/leaf30_crr_cfooe_volpen_alpha_build_r2_chunk.py` | `0a264402` | `0a2644021e8bbd16cbe7f69905a6a6dfcd47df3c798b6f5b272f7b6702220260` | **MATCH · 未改** |
| r1（禁盲跑） | `research/leaf30_crr_cfooe_volpen_alpha_build_r1.py` | `a2cef5af` | （本机复核 sha8） | **MATCH · 未改** |
| Arch R2 VOID | `docs/v2/audit/ARCH_LEAF30_CRR_ALPHA_BUILD_R2_VOID_ABORT_PEAK_HWM_20261026_ZH.md` | `df47501c` | （void_ref） | **MATCH** |
| AI R2 跑回执 | `docs/v2/audit/AI_LEAF30_CRR_ALPHA_BUILD_R2_X2_RUN_RECEIPT_20261026_ZH.md` | `fe5a2c1e` | （void_ref） | **MATCH** |
| VOID `.ok` R2 archived | `_consumed/…R2_HILIQ_X2.5af20222.VOID.…ok` | 内容 `5af20222` | live **ABSENT**；archived **在位** | **OK** |
| VOID `.ok` R1 archived | `_consumed/…HILIQ_X2.5ae077fa.VOID.…ok` | 内容 `5ae077fa` | live **ABSENT**；archived **在位** | **OK** |
| live leaf30 `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF30*` | ABSENT | — | **ABSENT** |
| live QUIET | `output/loop/RESEARCH_QUIET.lock` | ABSENT | — | **ABSENT** |
| A18 EXEC_V2 `.ok` | `_consumed/…a62881b9.CONSUMED_PASS…` | `a62881b9` | live **ABSENT**（已 CONSUMED） | **本审未触** |

## 2. CONDITIONS 逐项（对照 `61830035` APPROVE_A）

| # | CONDITIONS | 结果 | 证据 |
|---|---|---|---|
| C1 | PRIMARY=A 按 rebal **日**懒加载；禁整窗 `logmv_rebal=` 预载 | **PASS** | L1116–1187：`for d in rebal_days:` → `logmv_d = _load_logmv_t1(..., [d], codes)`；各 early-continue / 正常路径均 `del logmv_d; gc.collect(); _rss(f"after_logmv_rebal_{YYYYMMDD}")`。`rg 'logmv_rebal\s*='` 于 R3 **空**；R2 L1100 仍有整窗赋值（对照） |
| C2 | B 月桶 **未**混入；无 silent `load_mode=B` | **PASS** | 无 `load_mode` 参数/分支；`month_bucket` 仅 docstring/dry `ban_month_bucket_load_mode_silent_mix=true`；`--chunk-mode` 仍仅 `month`（日度展开，≠B 月桶 logmv） |
| C3 | 新文件自 R2 派生、新 sha；禁盲跑 r1/r2 作新票 | **PASS** | 新路径 `…_r3_peakcut.py` sha8 **`3ee9fed2`≠`0a264402`**；dry `prev_script_sha8=0a264402` / `r3_peakcut=true` / `schema=…_r3_peakcut`；`sign_notes` 禁盲重跑 `a2cef5af` / `0a264402-as-ticket`；R2/r1 未改 |
| C4 | forbid∋**`5af20222`+`5ae077fa`**（计数≥16） | **PASS** | `FORBID_OK_SHA8` **n=16**；首项 `5af20222`、次项 `5ae077fa`；含原十五票其余至 `6de02e74`；dry/真跑 STOP on forbid |
| C5 | overlap 必产；dry/签文禁 `--no-overlap-report` | **PASS_WITH_CONDITIONS** | 真跑默认写 `overlap_vs_leaf19_25.json`；dry `ban_no_overlap_report=true` / `x2_sign_bans_no_overlap_report_flag=true`；CLI **仍保留** `--no-overlap-report`（help 钉签文将禁）→ **须入签文硬闸** |
| C6 | peak_proof：`after_daily_concat` + `after_logmv_rebal_*`；Exit 94/95；rss=1500 禁抬 | **PASS** | `_rss("after_daily_concat")` L1262；日界 `after_logmv_rebal_YYYYMMDD`；`check_rss` → SystemExit 94/95；`RSS_LIMIT_MB=1500`；`rss_limit_mb>1500` / 抬 C4/stop/hard → STOP；dry `peak_proof_required` 含二者 |
| C7 | 机制无回归：qend_ok / C2 OP+OCF / λ=1.0 / 银地非银 / HILIQ×x2 / 授权双闸 | **PASS** | `qend_ok` 真滤；`operate_profit`+`n_cashflow_act`；禁 ocf 主源；`LAMBDA_FROZEN=1.0`；`EXCLUDE_SW` 801780/801180/801790；PRIMARY HILIQ×x2（FULLA 缺席）；`--allow-real-data`+现存 `--arch-ok-path`；ok∉forbid |
| C8 | PIT/T−1；用完 del+gc；可选 codes 收窄/月 flush | **PASS**（可选未做） | `_load_logmv_t1`：`trade_date < asof` T−1；循环内 del+gc 齐。**本拍未做** codes=当日 members 收窄 / alpha_rebal 月 flush——**不强制**（提案可选） |
| C9 | `py_compile` + `--dry-compile-only` | **PASS** | 本机复跑：compile PASS；dry exit0；JSON 钉 `r3_peakcut=true` / `primary_load=rebal_day` / `script_sha8=3ee9fed2` / forbid 16 / void_ref / arch_review=`61830035` / proposal=`f111671a` |

## 3. 残留风险（知情接受 · 签窗监控）

| 风险 | 等级 | 备注 |
|---|---|---|
| `after_daily_concat` 残峰仍可能逼近 split | **中** | R2 未测到此点；A 过 `after_logmv_rebal_*` 后仍一次 concat 月分片；须 peak_proof；破→94/95，**禁抬帽** |
| 按日 I/O 变慢 | **低–中** | 可接受；若不可用再 **显式** B 另审（本脚本无 B） |
| CLI `--no-overlap-report` 仍在 | **管控** | 靠签文硬闸；消费端须读 overlap JSON |
| 化妆品：注释/assert 仍写 `r2-month-chunk-tmp` / `# …_r2_*` | **低** | `SAMPLER_PREFIX` 已是 `/tmp/quantlab_leaf30_crr_r3_`；**不强制**本拍改脚本 |
| 盲重跑 / RESTORED | **管控** | forbid+签文+本审禁项 |

## 4. 残留 CONDITIONS（另窗签新 X2 `.ok` 前）

1. **本拍不签**：须主另排**独立 X2 签窗**；**新** `.ok`（建议名 `…_R3_PEAKCUT_HILIQ_X2.ok` 或主定新名；**勿**复用旧 `…HILIQ_X2.ok` / R2 名）；钉脚本 sha8 **`3ee9fed2` only**。
2. **C3 签文硬钉**：真跑**必须**写并消费 `overlap_vs_leaf19_25.json`；Jaccard≥0.7 → 硬拒；ρ>0.5 → 强度；签文 **禁** `--no-overlap-report`（CLI 可保留）。
3. **peak_proof REQUIRED**：含 `after_daily_concat` + 全序列 `after_logmv_rebal_*`；ru_maxrss/VmHWM/`RSS_CHECK`；破 soft/hard → Exit **94/95** 停+上报；**rss=1500 禁抬**。
4. **forbid∋`5af20222`+`5ae077fa`**（及十六票）；**禁 RESTORED**；禁盲重跑 r1 `a2cef5af` / 以 R2 `0a264402` 作新票脚本；禁触已 CONSUMED A18 `a62881b9`。
5. **PRIMARY CLI 钉**（无 `--no-overlap-report`）：
   `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf30_crr_cfooe_volpen_alpha_build_r3_peakcut.py --universe HILIQ --window x2 --x2-end 20261009 --out output/ai_factory/_leaf30_crr/<ET_TS>/ --allow-real-data --arch-ok-path <NEW_OK>`
6. sampler `/tmp/quantlab_leaf30_crr_r3_*`；out `_leaf30_crr/<ET_TS>/`；Arch **不代跑**；可挂 leaf30 自有 QUIET（当前 QUIET **ABSENT**）。
7. live=false · promotion=false · book_smoke=false · **x2_accept=false** · selfcheck=false · **≠X2 ACCEPT**。

## 5. 禁项 / 本回合非动作

- **未签**任何 `.ok`（含新叶30 / RESTORED `5af20222` / `5ae077fa`）
- **未挂** QUIET；live QUIET **ABSENT**（未改）
- **未改** R3 / R2 `0a264402` / r1 `a2cef5af` / AI 回执 / 提案审
- **未** `--allow-real-data` / **未**代跑真构建（仅 `py_compile` + dry）；误生 repo `__pycache__` r3 已清 → **ABSENT**
- **未** RESTORED；**未**抬 rss；**未**触 A18 产物
- **≠X2 ACCEPT** / ≠selfcheck / ≠Book-Smoke
- **未** SendToUser / **未**报 Leo（leo_notify=false）

## 6. 硬钉下一跳

```
脚本 3ee9fed2（本审 PASS_WITH_CONDITIONS · APPROVE_A 落地）
  → 主另排独立 X2 签窗（新 .ok；钉 3ee9fed2；§4 CONDITIONS）
      → AI prelaunch→execute（无 --no-overlap-report；peak_proof）
          → Arch CONSUME（≠X2 ACCEPT）
```

## 7. 结论

| 项 | 值 |
|---|---|
| VERDICT | **PASS_WITH_CONDITIONS** |
| CHOICE 落地 | **APPROVE_A**（PRIMARY=按 rebal 日懒加载）已实现 |
| 脚本 | **`3ee9fed2` MATCH** |
| AI 落盘 | **`4d951ea3` MATCH** · EXECUTED=false |
| 提案审 | **`61830035` MATCH** · APPROVE_A |
| 基盘 | **`0a264402` 未改**；r1 `a2cef5af` 未改 |
| 请主 | **另排独立 X2 签窗**（本拍不签）；再令 AI prelaunch→execute |
| live | **false** |
| leo_notify | **false** |

live=false · leo_notify=false · ≠X2 ACCEPT · 只审不签不挂不代跑.

## 8. 本审钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/audit/ARCH_LEAF30_CRR_ALPHA_BUILD_R3_PEAKCUT_SCRIPT_REVIEW_20261026_ZH.md` |
| 脚本 sha8 | **`3ee9fed2`** |
| AI 回执 sha8 | **`4d951ea3`** |
| 提案审 sha8 | **`61830035`** |
| 结论 | **PASS_WITH_CONDITIONS**（APPROVE_A 落地；本拍不签；请主另排签窗） |

全文件 sha256 / sha8：以本机 `sha256sum` 为准（见 TEAM_STATE 顶条与父回报）。

live=false.
