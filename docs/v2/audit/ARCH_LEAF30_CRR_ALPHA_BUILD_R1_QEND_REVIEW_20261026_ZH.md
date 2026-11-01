# Arch 复审：叶30 CRR α 构建脚本 R1 qend_ok 补丁（只审不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态复审） |
| 时刻 | `2026-10-26T18:04:30-04:00`（America/New_York；墙钟 `2026-10-26 18:04 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 本回合动作 | **不签**任何 `.ok`；**不挂 QUIET**；**不代跑** `--execute` / `--allow-real-data` 真路径；不改脚本/FROZEN；**不触** A18（live `.ok` 已由并行线归档至 `_consumed/`；本审零字节改）；叶26 不交审；28/29 FROZEN；**≠X2 ACCEPT**；live=false；**不推 Leo** |
| 触发 | 主 18:02 ET 令 Arch 复审 R1 补丁（对照前审 `d1c71ece` / AI 补丁 `2b8dee0b`） |
| 轻量复跑 | `--dry-compile-only` exit **0**；`qend_ok_filter=true`；缺授权 flag STOP exit **2**；零大表 |

## 0. 一句话

脚本 sha8 **`a2cef5af`**（prev `b903756f`）相对前审 **R1 已闭环**：`build_fund_quarter_panel` **真正过滤** `qend_ok`（缺列 STOP；双保险 merge 后再滤 QEND）；dry pins 钉 `qend_ok_filter=true`。C2/λ/掩码/rss=1500/授权双闸/HILIQ×x2/C4 **无回归**。**仍不签** X2 `.ok`。残留 CONDITIONS：C3 Jaccard/ρ **仅披露不中止** → 签文须强制消费 overlap JSON / **禁** `--no-overlap-report`；peak_proof REQUIRED；独立 X2 签窗。

## 1. 钉表再核（本机 sha256）

| 件 | 路径 | 期望 sha8 | 实测全长 | 结果 |
|---|---|---|---|---|
| 新脚本 | `research/leaf30_crr_cfooe_volpen_alpha_build_r1.py` | `a2cef5af` | `a2cef5affd67f874fad9e37f59efb9d7abacb3de0d0286d8443250aee5253c74` | **MATCH** · 1457 行 |
| AI R1 补丁回执 | `docs/v2/audit/AI_LEAF30_CRR_ALPHA_BUILD_R1_QEND_PATCH_RECEIPT_20261026_ZH.md` | `2b8dee0b` | `2b8dee0b77495dc4e3b9be0f3c7507dcbca28f5a069f58e57df7240d90195131` | **MATCH** |
| 对照前审 | `docs/v2/audit/ARCH_LEAF30_CRR_ALPHA_BUILD_SCRIPT_REVIEW_20261026_ZH.md` | `d1c71ece` | `d1c71ece64f71f2927d766fa1bf6df45d19aaf53ec427d0ac7b0743704255635` | **MATCH** |
| FROZEN | `docs/v2/AI_LEAF30_CRR_CFOOE_VOLPEN_WHO_PAYS_FROZEN_20261026_ZH.md` | `93cad965` | `93cad965bd9aa34b6bb8dc5e43d6f0095c4d111420c5fa53b196ad4220d40fba` | **MATCH** |
| 预注册审 | `docs/v2/audit/ARCH_LEAF30_CRR_WHO_PAYS_PREREG_REVIEW_20261026_ZH.md` | `f61ffb05` | `f61ffb052192810e908e931032442b6a62381e1ab1ad09fcb0245657893d47b0` | **MATCH** |
| A18 EXEC `.ok` | live `output/data/ARCH_RUN_AUTH_DAILY_BASIC_A18_SECTION_5_3_BASELINE_EXEC.ok` | `6de02e74` | — | **live ABSENT**（并行线已归档 `_consumed/…6de02e74…A9_RECONCILE_FAIL.20261026T1803ET.ok`）；脚本 `FORBID_OK_SHA8` **仍含** `6de02e74`；本审**未触** |

live `output/loop/RESEARCH_QUIET*` **无**；本审**未挂** QUIET；**无** leaf30 `.ok`；MemAvailable≈9.0Gi（旁证）。

## 2. R1 审点（相对 d1c71ece）

| # | 要点 | 结果 | 证据 |
|---|---|---|---|
| R1 | `build_fund_quarter_panel` **真正过滤** `qend_ok`（非只算不滤） | **PASS** | L679–685：缺 `qend_ok` → `SystemExit` STOP；`fin=fin[fin["qend_ok"]]` / `cf=cf[cf["qend_ok"]]`（在 `report_type=='1'` / `first_version` / rolling **之前**）；L693–694 merge 后再 `mmdd∈QEND` 双保险；`_norm_pit` L388 仍算 `qend_ok`（0331/0630/0930/1231） |
| R1-dry | dry-compile / `qend_ok_filter=true` | **PASS** | `--dry-compile-only` exit 0；JSON `qend_ok_filter: true`；`r1_arch_review_sha8: d1c71ece`；`sign_notes.ban_no_overlap_report/peak_proof_required/rss_limit_mb=1500` |
| 对照 | 前审 R1 洞已闭环 | **PASS** | prev `b903756f` 仅算不滤 → 本拍 `a2cef5af` 硬滤；行数 1433→1457 |

## 3. 前审 CONDITIONS 复检（相对 d1c71ece §2/§4）

| # | 要点 | 结果 | 证据 |
|---|---|---|---|
| 1 | **C2** OP+OCF；L=16/min12；vol 8/6；禁 ocf/净利润主源 | **PASS** | `KNOWN_PIT_COLS` 仅 `operate_profit`/`n_cashflow_act`；`_read_pit_projected` 名起 `ocf_to_profit` → STOP；`claims.ocf_to_profit_main=false`；全文无 `net_profit`/`n_income` |
| 2 | **λ=1.0**；IC 期望为正仅注释 | **PASS** | `LAMBDA_FROZEN=1.0`；合成 `raw = r_crr - LAMBDA_FROZEN * r_vol`；不计算收益 |
| 3 | 银地非银掩码；801230 不掩 | **PASS** | `EXCLUDE_SW` 801780/801180/801790；注释 801230 不在集合 |
| 4 | **rss=1500** 硬 ABORT；禁抬帽 | **PASS** | `RSS_LIMIT_MB=1500`；`check_rss` soft/hard/split → SystemExit 94/95；`rss_limit_mb>1500` 或抬 C4/stop/hard → STOP |
| 5 | **C3** Jaccard/ρ 仅披露不中止；签文须强制消费 / 禁 `--no-overlap-report` | **PASS_WITH_CONDITIONS**（条件仍开） | `write_overlap_report` 写 `jaccard_hard_reject_*` / `strength_filter_*` 注释 **disclosure only**；**不** `SystemExit`；CLI **保留** `--no-overlap-report`（help 钉 X2 签文将禁）；dry `sign_notes.ban_no_overlap_report=true` / `x2_sign_bans_no_overlap_report_flag=true` → **C3a/C3b 仍须入签文** |
| 6 | peak_proof REQUIRED | **PASS_WITH_CONDITIONS**（条件仍开） | 静态审 ≠ 峰证明；日度展开峰风险未消；签/真跑须 ru_maxrss/VmHWM；破 1500 → 停+上报，禁抬帽 |
| 7 | 授权双闸；HILIQ×x2 | **PASS** | `--allow-real-data` + 现盘 `--arch-ok-path`；ok∉forbid；缺旗 STOP exit2；argparse 无 FULLA / window 仅 x2 |
| 8 | **C4** SW L1 demean + logmv；无 mom/vol/ADV | **PASS** | `alpha_dm` + `ols_resid` vs logmv；`rg` 无 mom/vol20/logADV |

## 4. 无回归

| 检查 | 结果 |
|---|---|
| 未放开 execute 旁路 | **PASS** — `--execute` 仍要求 `--allow-real-data`+`--arch-ok-path`；无旗 STOP exit2 |
| 未抬 rss | **PASS** — 仍 1500；抬帽 STOP |
| 未复用叶25 `.ok` | **PASS** — `FORBID_OK_SHA8` 含 `3c297052`/`ebc673bf` 等 |
| 未触 A18 | **PASS** — 本审未读/改 live 或 `_consumed` 字节；forbid 仍钉 `6de02e74` |
| 未挂 QUIET / 未签 leaf30 `.ok` | **PASS** |

## 5. 残留 CONDITIONS（另窗签 X2 `.ok` 前）

1. **本拍不签**：须主另排**独立 X2 签窗**（禁复用叶25/`3c297052`/`ebc673bf`；禁复用 A18 `6de02e74` 含已归档票）。
2. **C3 签文硬钉**：真跑**必须**写并消费 `overlap_vs_leaf19_25.json`；Jaccard≥0.7 → 硬拒票；ρ>0.5 → 强度过滤叙事；计数抽样≠正式；签文 **禁** `--no-overlap-report`（CLI 仍在，靠签文/消费端闸）。
3. **peak_proof REQUIRED** + rss=1500 禁抬；破帽停+上报。
4. **C2 坚持**：financials_pit OP + cashflow_pit OCF；禁 ocf_to_profit / 净利润替代。
5. sampler `/tmp/quantlab_leaf30_crr_*`；out 隔离建议 `output/ai_factory/_leaf30_crr/<ET_TS>/`。
6. live=false · promotion=false · book_smoke=false · **x2_accept=false** · selfcheck=false。
7. **R1 已闭环**（本拍）；签文可钉 `qend_ok_filter=true` / 脚本 `a2cef5af`。

## 6. 禁项（本回合）

- 不签 / 不改任何 `.ok`；不挂 QUIET；不 `--execute` / 不读大 parquet 全表
- 不改脚本 / FROZEN / AI 回执
- 不触 A18 `6de02e74`（含 `_consumed`）
- 不解阻 X2；不当 X2 ACCEPT；叶26 不交审；28/29 FROZEN
- 不推 Leo；live=false

## 7. 本回合非动作声明

- **未签**任何 `.ok`
- **未挂** QUIET
- **未** `--execute` / **未** `--allow-real-data` 真构建（仅 dry-compile + 无授权 STOP）
- **未改**脚本 / FROZEN / 预注册文 / AI 回执
- **未触** A18（live ABSENT；`_consumed` 未动）
- **不推 Leo**；live=false；promotion=false；x2_accept=false

## 8. 硬钉下一跳

```
脚本 a2cef5af（本复审 PASS_WITH_CONDITIONS；R1 闭环）
  → 主另排独立 X2 .ok（禁 RESTORED/叶25/A18；钉 C3 禁 --no-overlap-report + peak_proof + qend_ok_filter）
      → 真跑 HILIQ×x2 16Q OP CRR + vol_pen（≠APPROX）
          → 回执（alpha sha + run_meta + overlap JSON + peak）
```

## 9. 结论

**PASS_WITH_CONDITIONS** — R1 `qend_ok` **真过滤**已验；钉全 MATCH；前审 C2/λ/掩码/rss/授权/宇宙窗/C4 **无回归**；C3 硬拒仍仅披露、peak_proof 仍须签文强制。**本拍不签** `.ok`；请主排独立 X2 签窗。

live=false.

## 10. 本审钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/audit/ARCH_LEAF30_CRR_ALPHA_BUILD_R1_QEND_REVIEW_20261026_ZH.md` |
| 脚本 sha8 | **`a2cef5af`** |
| 结论 | **PASS_WITH_CONDITIONS**（R1 闭环；本拍不签） |

全文件 sha256 / sha8：以本机 `sha256sum` 为准（见 TEAM_STATE 顶条与父回报）。

live=false.
