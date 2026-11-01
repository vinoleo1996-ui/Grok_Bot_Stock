# Arch 审阅：叶30 CRR 正式 α 构建脚本（只审不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审） |
| 时刻 | `2026-10-26T17:55:00-04:00`（America/New_York；墙钟 `2026-10-26 17:55 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 本回合动作 | **不签**任何 `.ok`；**不挂 QUIET**；**不代跑** `--execute` / `--allow-real-data` 真路径；不改脚本/FROZEN；**不触** A18 `.ok` `6de02e74`（仅 forbid 抽检 STOP）；叶26 不交审；28/29 FROZEN；**≠X2 ACCEPT**；live=false；**不推 Leo** |
| 触发 | 主 17:52 ET 令 Arch 只审脚本不签（TEAM_STATE 顶条 + 父令）；对照 FROZEN `93cad965` / 预注册 `f61ffb05` / AI 回执 `2b85c4c4` |
| 轻量复跑 | `--dry-compile-only` exit **0**；缺授权 flag STOP exit **2**；forbid 含 A18 `6de02e74` → STOP exit **2**（零大表） |

## 0. 一句话

脚本 `b903756f`（1433 行）与 AI 回执 / FROZEN / 预注册钉全 **MATCH**；C2 主源 `operate_profit`+`n_cashflow_act`、L=16/min12、vol_pen 8/6、禁 ocf 主源（路径硬拒+claims）、λ=1.0、银地非银掩码、rss=1500 硬 ABORT、授权双闸、HILIQ×x2 窗、C4 最低残差、C3 overlap 预留均齐。**本拍仍不签** X2 `.ok`。CONDITIONS：C3 Jaccard/ρ 仅披露旗标**不中止**构建；`qend_ok` 算而未滤；日度展开峰风险须 peak_proof；须主另排独立 X2 签窗并错开 A18。

## 1. 钉表再核（本机 sha256）

| 件 | 路径 | 期望 sha8 | 实测全长 | 结果 |
|---|---|---|---|---|
| 脚本 | `research/leaf30_crr_cfooe_volpen_alpha_build_r1.py` | `b903756f` | `b903756fddf152814e617358c242a3e991dc955217dba62eaa704a7b30f3830b` | **MATCH** · 1433 行 |
| AI 回执全文 | `docs/v2/audit/AI_LEAF30_CRR_ALPHA_BUILD_SCRIPT_RECEIPT_20261026_ZH.md` | `2b85c4c4` | `2b85c4c4a1ea975b0294e2112dca52671a96908e8f4d6aa2e2636d553a68e06a` | **MATCH**（正文另钉 `04dfd0f9` 采信 AI） |
| FROZEN | `docs/v2/AI_LEAF30_CRR_CFOOE_VOLPEN_WHO_PAYS_FROZEN_20261026_ZH.md` | `93cad965` | `93cad965bd9aa34b6bb8dc5e43d6f0095c4d111420c5fa53b196ad4220d40fba` | **MATCH** |
| 预注册审 | `docs/v2/audit/ARCH_LEAF30_CRR_WHO_PAYS_PREREG_REVIEW_20261026_ZH.md` | `f61ffb05` | `f61ffb052192810e908e931032442b6a62381e1ab1ad09fcb0245657893d47b0` | **MATCH** |
| A18 EXEC `.ok` | `output/data/ARCH_RUN_AUTH_DAILY_BASIC_A18_SECTION_5_3_BASELINE_EXEC.ok` | `6de02e74` | `6de02e7421fae731be0ee5ab68443ba514b908b34ec03a6ec049b88e42524eca` | **MATCH 未触**（mtime 仍 15:18 ET；forbid 抽检 STOP） |
| leaf25 α（对照） | `…/alpha_HILIQ_x2_20261026_125138.parquet` | `8be12024` | （本机复核 sha8） | **MATCH** |

live `output/loop/RESEARCH_QUIET*` **无**；本审**未挂** QUIET；**无** leaf30 `.ok`；A18 Eng pid **2902104** 仍跑中（C5 错开，本审仅轻量）。MemAvailable≈8.0Gi（旁证）。

## 2. 必审清单（静态 + dry-compile）

| # | 要点 | 结果 | 证据 |
|---|---|---|---|
| 1 | **C2** 主源 OP+OCF；L=16/min12；vol 8/6；禁 ocf 主 CRR | **PASS** | `PIT_FIN`/`PIT_CF`；`KNOWN_PIT_COLS`；`build_fund_quarter_panel` 只读 `operate_profit`/`n_cashflow_act`；`_read_pit_projected` 名起 `ocf_to_profit` → STOP；`claims.ocf_to_profit_main=false`；无 `net_profit`/`n_income` 替代路径 |
| 2 | **λ=1.0** FROZEN；IC 期望为正仅注释 | **PASS** | `LAMBDA_FROZEN=1.0`；`IC_SIGN_EXPECTED="positive"`；docstring/meta notes「script does NOT compute returns」；合成 `raw = r_crr - LAMBDA_FROZEN * r_vol` |
| 3 | 行业掩码 801780/801180/801790；801230 不掩 | **PASS** | `EXCLUDE_SW` + 注释；`_exclude_set_asof` 用于 CFOOE CS 与再平衡日；801230 不在集合 |
| 4 | **rss=1500** + 硬检查/peak；禁抬帽 | **PASS** | `RSS_LIMIT_MB=1500`；`check_rss` soft/hard/split → SystemExit 94/95；`rss_limit_mb>1500` 或抬 C4/stop/hard → STOP |
| 5 | **C3** overlap 预留；Jaccard≥0.7 / ρ>0.5；计数≠正式 | **PASS_WITH_CONDITIONS** | `write_overlap_report` + 真跑默认写 `overlap_vs_leaf19_25.json`；note 钉 count≠formal；**旗标仅披露**（`jaccard_hard_reject_*` / `strength_filter_*`）——**不中止**构建 → C3a；`--no-overlap-report` 可跳过 → C3b |
| 6 | 授权闸门：`--allow-real-data` + 现盘 `--arch-ok-path`；ok∉forbid；dry 零大表 | **PASS** | `main`/`run_build` 双闸；本机复跑：dry exit0（pins 含 forbid/`6de02e74`）；无 flag STOP exit2；A18 ok 作 path → forbid STOP exit2 |
| 7 | 宇宙/窗：PRIMARY HILIQ×x2；2024-06-03→2026-10-09；20td；FULLA STOP | **PASS** | argparse `choices` 无 FULLA / window 仅 x2；`X2_START/END`；`REBAL_EVERY=20`；FULLA/`x2-end` 错钉 → STOP；HI_LIQ mask 缺/空 → STOP（拒静默降级） |
| 8 | **C4** 残差最低集 SW L1 demean + logmv；未静默加 mom/vol/ADV | **PASS** | 再平衡：`alpha_dm` 组均 demean + `ols_resid` vs logmv；全文无 mom/vol20/logADV 残差项 |
| 9 | 隔离：forbid 含 `3c297052`/`ebc673bf`/`6de02e74` 等；未签 .ok；未挂 QUIET；未触 A18 | **PASS** | `FORBID_OK_SHA8` 14 票含三者；本回合非动作见 §6 |
| 10 | 残差风险扫（逻辑洞） | **PASS_WITH_CONDITIONS** | 见 §3（YTD→单季差分实装；PIT `available_at`+次日 avail；分母≤0 无效；rank 合成；产物 `alpha_HILIQ_x2_<ET>.parquet`+`run_meta.json`；**禁**净利润替代 OP；`qend_ok` 未滤 → R1；日度展开峰 → R2） |

## 3. 残差风险（须入签条件）

1. **R1 `qend_ok` 未滤**：`_norm_pit` 计算 `qend_ok`（0331/0630/0930/1231），但 `build_fund_quarter_panel` **未**按之过滤；若 PIT 混入非季末行，16 行 rolling 可能≠16 个日历季。签 `.ok`/真跑前须确认 PIT 仅季末或补滤。
2. **R2 日度展开峰**：再平衡 α 以 Python 行列表展开至全窗日度；静态审 ≠ 峰证明；peak_proof REQUIRED（ru_maxrss/VmHWM）；破 1500 → 停+上报，禁抬帽。
3. **R3 C3 披露≠硬中止**：Jaccard≥0.7 / ρ>0.5 只写 JSON 旗标，**不** `SystemExit`；X2 签文/消费端须把硬拒当闸（或后补脚本 abort）。
4. **R4 CFOOE 行业 asof 代理**：CS 用 `avail` 中位数作 SW asof；logmv_by_end 经 avail 键回填，缺键则丢截面点——coverage 须入回执。
5. **R5 sampler 双层**：`assert_tmp_quantlab` 宽允 `/tmp/quantlab_*`，其后再钉 `leaf30_crr`；签文硬钉 `/tmp/quantlab_leaf30_crr_*` only。
6. **≠X2 ACCEPT / ≠APPROX**：即使 α 落盘成功亦不自动晋级；计数 APPROX 不得冒充本票主交付。

## 4. 条件（另窗签 X2 `.ok` 前必须满足）

1. **本拍不签**：须主另排独立 X2 签窗（禁复用叶25/`3c297052`/`ebc673bf`；禁复用 A18 `6de02e74`）。
2. **C2 坚持**：真跑主源必须 financials_pit OP + cashflow_pit OCF；禁 ocf_to_profit；缺列 STOP（脚本已硬）。
3. **C3 正式重叠以跑后 JSON 为准**：消费 `overlap_vs_leaf19_25.json`；Jaccard≥0.7 → 硬拒票；ρ>0.5 → 强度过滤叙事；计数抽样≠正式；建议 `.ok` **禁** `--no-overlap-report`。
4. **C4**：若后加 mom/vol/ADV 正交须补丁文件，不得静默改脚本声称。
5. **C5 错开 A18**：Eng 正开 §5.3（`.ok` `6de02e74` 仍在；pid 见盘）；签/真跑须等 A18 收口或主明示错峰；本审未挂 QUIET、未抢 mem 重活。
6. **peak_proof REQUIRED** + rss=1500 禁抬；sampler `/tmp/quantlab_leaf30_crr_*`；out 隔离建议 `output/ai_factory/_leaf30_crr/<ET_TS>/`。
7. **R1**：签前确认 `qend_ok` 过滤策略（补丁或 PIT 保证）。
8. live=false · promotion=false · book_smoke=false · **x2_accept=false** · selfcheck=false。

## 5. 禁项（本回合）

- 不签 / 不改任何 `.ok`；不挂 QUIET；不 `--execute` / 不读大 parquet 全表
- 不改脚本 / FROZEN / AI 回执
- 不触 A18 `6de02e74` 字节（forbid 抽检除外，未改 mtime）
- 不解阻 X2；不当 X2 ACCEPT；叶26 不交审；28/29 FROZEN
- 不推 Leo；live=false

## 6. 本回合非动作声明

- **未签**任何 `.ok`
- **未挂** QUIET
- **未** `--execute` / **未** `--allow-real-data` 真构建（仅 dry-compile + 无授权 STOP + forbid STOP）
- **未改**脚本 / FROZEN / 预注册文
- **未触** A18 `.ok`（sha/mtime 不变）
- **不推 Leo**；live=false；promotion=false；x2_accept=false

## 7. 硬钉下一跳

```
脚本 b903756f（本审 PASS_WITH_CONDITIONS）
  → 主另排独立 X2 .ok（避 A18；禁 RESTORED；钉 C3 硬拒消费 + peak_proof + R1）
      → 真跑 HILIQ×x2 16Q OP CRR + vol_pen（≠APPROX）
          → 回执（alpha sha + run_meta + overlap JSON + peak）
```

## 8. 结论

**PASS_WITH_CONDITIONS** — 构建脚本可收；钉全 MATCH；C2/λ/掩码/rss/授权/宇宙窗/C4 主体 PASS；C3 预留齐但硬拒仅披露；R1–R5 见 §3–§4。**本拍不签** `.ok`；可请主在 A18 错峰后排 X2 签窗。

审阅文 sha8：落盘后由执行器钉（见文末）。

live=false.

## 9. 本审钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/audit/ARCH_LEAF30_CRR_ALPHA_BUILD_SCRIPT_REVIEW_20261026_ZH.md` |
| 脚本 sha8 | **`b903756f`** |
| 结论 | **PASS_WITH_CONDITIONS**（本拍不签） |

全文件 sha256 / sha8：以本机 `sha256sum` 为准（见 TEAM_STATE 顶条与父回报）。

live=false.
