# Arch 审阅：叶35 ETF 被动压力 overlay 正式构建脚本（只审不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审脚本） |
| 时刻 | `2026-10-27T13:33:00-04:00`（America/New_York；墙钟 `2026-10-27 13:33 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 对照 | PREREG_FROZEN **`be9fc459`** · FROZEN 审 **`5a082d18`**（C1–C13 / C2 正式脚本）· who_pays 审 **`ee7ec307`** · PIN **`dd17044a`** · FROZEN RECEIPT **`132ba6f1`** · 迁仓 **`4e964d40`** |
| 本回合动作 | **不签**任何 `.ok`；**不挂** QUIET；**不代跑** `--allow-real-data` / `--execute` / 真构建（仅 `py_compile` + `--dry-compile-only`）；**不改**脚本/FROZEN/RECEIPT/COVER/CMD/DIFF/PIN/who_pays；**不触** A18；叶30 衰减修复 **`0087c928` 未审**（另队）；叶28/29 **另队不夹带**；禁 RESTORED `178e90e9`+`c1b71e64`+`245df63f`+`c5ed13df`+`5774bb6e`+二十票(+`81521fb5`)；叶34 HOLD CLOSED（`a37257b9`/`178e90e9`/`3fce510e`）不回撤；叶33 正式 **`afbbe7e7` UNCHANGED**；叶32 HOLD **`45dd87dc`** 不回撤；**≠X2 ACCEPT**；live=false；**不报 Leo**；**leo_notify=false** |
| 触发 | 主 ~13:29 ET · 叶35 C2 正式脚本只审（脚本 `25ae4572` / COVER `eee0866b` / CMD `c6d3b9ed` / DIFF `dc503904` / RECEIPT `d9758eb6`） |
| 轻量复跑 | `py_compile` **PASS**；`--dry-compile-only` exit **0**（零大表；JSON 含 mechanism/mask_only/top_q=0.20/C3 方案 A PIN/forbid26/peak_proof/overlap vs moneyflow+26resid+8a+25/27/30–34/decay KEEP）；`--universe FULLA` dry → STOP PRIMARY exit **2**；无授权 flag → STOP exit **2** |

## 0. 一句话

脚本 **`25ae4572` MATCH**：mechanism=`g1g5_ashare_etf_passive_flow_pressure_overlay_v1`；PRIMARY=**mask-only** top_q=**0.20**（高 `|pressure|` mask=0；可计算其余 mask=1；不可映射不填假 0）；soft-penalty **默认关、非 PRIMARY**（`--enable-soft-penalty` 须 SW+style，缺列 PIN_GAP）；**C3 方案 A**=月末权重点→**次月首个交易日 09:00 Asia/Shanghai**=`weight_available_at` ∧ 份额 `available_at≤t_ts` ∧ 映射三件套 `{510300→000300,510500→000905,512100→000852}` ∧ `percent_div100` ∧ **禁**静默月末向后 asof；再平衡=20；X2 2024-06-03→2026-10-09；PRIMARY=HILIQ；`--universe FULLA` STOP；`--also-fulla-research` 可选且不得作 PRIMARY；C7 overlap vs moneyflow/叶26残差(若有)/8a(若有)/25/27/30–**34** + Jaccard≥0.7 exit4 + ρ>0.5 强度 + leaf26-like raw 诊断不硬拒 + 缺 required→PIN_GAP；rss=1500 硬 ABORT + peak_proof（after_mask / after_weight_pin / after_pressure_rebal_* / after_mask_cs_rebal_* / after_daily_concat）；再平衡日懒加载 ETF 份额×权重方案 A；forbid∋`178e90e9`+`c1b71e64`+`245df63f`+`c5ed13df`+`5774bb6e`+二十票+`81521fb5`（**26** sha8）；真跑须 `--allow-real-data` + **已实现** `--arch-ok-path`（现存且∉forbid）；CMD 拟 cmd 含未来新 `.ok`（现不可跑）；decay KEEP 三闸+**KEEP 不解阻**仅钉；**C11** overlay≠叶26 完整残差 α（禁 moneyflow/行业 ETF 持仓主输入）；C12 APPROX≠ACCEPT；C10 `0087c928`/28/29 另队；禁 `--force` / 盲 seed；dry-compile PASS；DIFF **重建字节≡脚本**（同 sha `25ae4572`）；叶33 **`afbbe7e7` UNCHANGED**；叶34 HOLD CLOSED / 叶32 HOLD **`45dd87dc`** 不回撤；live `.ok`/QUIET **ABSENT**；EXECUTED=false。**本拍不签**；请主另排独立 X2 签窗。

## 1. 钉表再核（本机 sha256）

| 件 | 路径 / 值 | 期望 sha8 | 实测全长 | 结果 |
|---|---|---|---|---|
| **正式脚本** | `research/leaf35_etf_passive_flow_pressure_overlay_alpha_build.py` | `25ae4572` | `25ae45723454423a31d4b0c6987c5eb0a2e8bb733c2506c2db67d628e91b4ad0` | **MATCH** · 1989 行 |
| SCRIPT_RECEIPT | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_ALPHA_BUILD_SCRIPT_RECEIPT_20261027_ZH.md` | `d9758eb6` | `d9758eb600ea9d78c1ae9cf094b618677b8c97507cadfa04430cbafdd43ac23a` | **MATCH** · EXECUTED=false |
| COVER DRAFT | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_ALPHA_BUILD_COVER_DRAFT_20261027_ZH.md` | `eee0866b` | `eee0866bb08af9b2bb8acca9dbc1799005fd2c0e0c8d8fc044b4f1290d4c04a4` | **MATCH** |
| CMD DRAFT | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_ALPHA_BUILD_CMD_DRAFT_20261027_ZH.md` | `c6d3b9ed` | `c6d3b9ede7abef7172479205b7a6252f8556629a211046ccdeeb764b41f5220c` | **MATCH** |
| DIFF DRAFT | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_ALPHA_BUILD_DIFF_DRAFT_20261027.diff` | `dc503904` | `dc50390418a18e373bdde712466c356ef57232b3210b088acd6c190d67b1a60f` | **MATCH** · NEW；重建字节 **≡脚本**（同 `25ae4572`） |
| PREREG_FROZEN | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_PREREG_FROZEN_20261027_ZH.md` | `be9fc459` | `be9fc4593249928460ec5a118a0bd79e033fd446ec921a64f6d47bdd09b01ed6` | **MATCH** |
| Arch FROZEN 审 | `docs/v2/audit/ARCH_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_PREREG_FROZEN_REVIEW_20261027_ZH.md` | `5a082d18` | `5a082d181f469ec49bab2efb73f6fb14976fc6d01a4a548de23eabe098cfd660` | **MATCH** |
| FROZEN RECEIPT | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_PREREG_FROZEN_RECEIPT_20261027_ZH.md` | `132ba6f1` | `132ba6f1f78be22bd3e22c6214eaf5c2f3c0f92ebb6501161f0ec7ed674c676a` | **MATCH** |
| PIN 决议（C3） | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_WEIGHT_PIT_PIN_20261027_ZH.md` | `dd17044a` | `dd17044ab6f2890283f226112609eebfdb5dddcc10df8fda8e8565de8ac77a36` | **MATCH** |
| 迁仓 COUNT 脚本 | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_COUNT_GATE_SCRIPT_20261027.py` | `4e964d40` | `4e964d4024115b3a73f97d7789dac22e328e6eed519ca4935fcd2dcf5ba82538` | **MATCH** |
| Arch who_pays 审 | `docs/v2/audit/ARCH_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_WHO_PAYS_REVIEW_20261027_ZH.md` | `ee7ec307` | （只读引用；上游） | **MATCH**（只读） |
| WHO / COVER / COUNT / JSON（上游） | who_pays 链 | `05942769` / `f41d7db8` / `cbca88e7` / `a17b75fb` | — | **只读引用** |
| 叶33 正式（只读） | `research/leaf33_share_unlock_pressure_resid_alpha_build.py` | `afbbe7e7` | `afbbe7e7292c17399bbf4733d9f34a922e6d81f1a914a60d24dc61fcba86cbc9` | **MATCH UNCHANGED** |
| 叶34 模板（只读） | `research/leaf34_high_accrual_exclusion_overlay_alpha_build.py` | `482009dc` | （只读未改） | **UNCHANGED** |
| 叶34 HOLD CLOSED（只读） | `a37257b9` / `.ok` `178e90e9` / lift `3fce510e` | — | — | **不回撤** |
| 叶32 HOLD（只读） | `docs/v2/ALPHA_LEAF32_MARGIN_NET_FLOW_RESID_X2_SELFCHECK_GATE_REVIEW_20261027_ZH.md` | `45dd87dc` | — | **不回撤** |
| 对照模板（只读） | `docs/v2/audit/ARCH_LEAF34_…_ALPHA_BUILD_SCRIPT_REVIEW_20261027_ZH.md` | （形态对照） | — | **只读** |
| live leaf35 `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF35*` | ABSENT | — | **ABSENT** |
| live QUIET | `output/loop/RESEARCH_QUIET.lock` | ABSENT | — | **ABSENT** |
| live `.ok` 计数 | `output/ai_factory/*.ok`（非 `_consumed`） | 0 | 0 | **MATCH** |
| 叶30 KEEP `0087c928` | 衰减修复 DRAFT | 另队 | 本拍**未打开/未审** | **未审声明** |

哈希闭环：脚本/RECEIPT/COVER/CMD/DIFF 互指 sha8 与盘上一致；脚本常量钉 FROZEN `be9fc459` / FROZEN 审 `5a082d18` / who_pays `ee7ec307` / PIN `dd17044a` / FROZEN RECEIPT `132ba6f1` / 迁仓 `4e964d40` / 叶33 `afbbe7e7` / 叶34 HOLD CLOSED `178e90e9` / 叶32 HOLD `45dd87dc`。DIFF 自 `/dev/null` NEW 重建内容 **字节等于** 脚本（sha 同 `25ae4572`）。

## 2. 必审清单（脚本 vs FROZEN `be9fc459` / 审 `5a082d18` / PIN `dd17044a`）

| # | 审点 | 结果 | 证据 |
|---|---|---|---|
| 1 | **C2** 哈希闭环 + 机制对齐：mask-only overlay；`pressure_raw=Σ w×flow_est_proxy`；top_q=0.20；再平衡 20；≠叶26 完整残差 / moneyflow / 行业 ETF 持仓主输入；避 25/27/30–34 同构主叶 | **PASS** | `MECHANISM_TAG`；`PRIMARY_DELIVERY=mask_only`；`TOP_Q=0.20`；`REBAL_EVERY=20`；`ALPHA_SIGN=high_abs_pressure_mask0_exclusion`；dry bans：`ban_leaf26_full_residual_alpha_main` / `ban_moneyflow_main_input` / `ban_industry_etf_holdings_main` / …；常量钉 FROZEN/PIN/ArchFROZEN |
| 2 | **PRIMARY 纪律（C4/C6）**：HI_LIQ mask-only；禁静默 FULLA；soft-penalty 非 PRIMARY | **PASS** | dry/run `--universe FULLA` STOP exit2；`ban_silent_fulla_as_primary=true`；`SOFT_PENALTY_DEFAULT=False`；`soft_penalty_is_primary=false`；`--enable-soft-penalty` 可选且须 style 列，缺→PIN_GAP |
| 3 | **C3 方案 A** 脚本落地：次月首个交易日 09:00 Asia/Shanghai + 份额 PIT + 映射三件套 + percent_div100；禁静默月末向后 asof | **PASS** | `_load_weight_pin_scheme_a` + `_asof_weight_scheme_a` + `_pressure_on_day`：`weight_available_at=d_star+09:00`；`available_at_clock≤t_ts(15:00 SH)`；`ETF_INDEX_MAP` 三件套；`percent_div100`；`ban_silent_month_end_asof_as_pit_complete=true`；`C3_FORMULA_PIN` / `c3_scheme=A_…` |
| 4 | **C5** top_q=0.20；高 `|pressure|`=剔除 | **PASS** | `TOP_Q=0.20`；`_cross_section_mask`：`|pressure|≥Q_(1-q)` → mask=0；dry `alpha_sign=high_abs_pressure_mask0_exclusion`；`ban_posthoc_q_or_sign_flip` |
| 5 | **C7 / X2 前重叠**：vs moneyflow/叶26resid(若有)/8a(若有)/25/27/30–34 + Jaccard≥0.7 硬拒 + ρ>0.5 强度 + leaf26-like raw 不硬拒；CMD/COVER 可见（本拍不签不跑） | **PASS_WITH_CONDITIONS** | `write_overlap_report` → `overlap_vs_moneyflow_leaf26resid_8a_25_27_30_31_32_33_34.json`；required 缺→`any_required_pin_gap`；Jaccard 硬拒 return **4**；真跑 `--no-overlap-report` 硬 STOP；CLI 仍保留 flag → **仍须入签文硬闸**（双保险） |
| 6 | **C9** 内存：rss=1500 + peak_proof；禁抬 | **PASS** | `RSS_LIMIT_MB=1500`；抬 rss → STOP；`peak_proof_required`：after_mask / after_weight_pin / after_pressure_rebal_* / after_mask_cs_rebal_* / after_daily_concat；`primary_load=rebal_day_lazy_etf_share_x_weight_scheme_A_pit` |
| 7 | **C8** forbid `178e90e9`+`c1b71e64`+`245df63f`+`c5ed13df`+`5774bb6e`+二十票+`81521fb5`；禁 RESTORED；禁 `--force`/盲 seed；`--arch-ok-path` 已实现 | **PASS** | `FORBID_OK_SHA8` **26** 项含六硬钉+二十票；真跑须现存 `--arch-ok-path` 且 sha8∉forbid；无写 `.ok` 逻辑；argparse **无** `--force` |
| 8 | **C13** decay KEEP 三闸+KEEP 不解阻仅钉（本脚本不执行闸） | **PASS** | `DECAY_KEEP_PIN`（三闸合取；near=252；`keep_does_not_unblock_x2_accept=true`；钉叶32 HOLD `45dd87dc` / 叶34 HOLD CLOSED `178e90e9`）；meta note 不跑 decay；`ban_selfcheck=true` |
| 9 | **C10**：`0087c928` 另队未审、未夹带；叶28/29 另队 | **PASS（未审声明）** | `LEAF30_KEEP_REPAIR_SHA8_SEPARATE=0087c928`；本拍未打开/未审该 DRAFT；叶28/29 不夹带 |
| 10 | **C11/C12**：overlay≠叶26 完整残差 α；APPROX≠X2 ACCEPT | **PASS** | 交付 exclusion mask；`ban_leaf26_full_residual_alpha_main` / `ban_moneyflow_main_input` / `ban_industry_etf_holdings_main`；`count_approx_not_x2_accept=true`；文钉 ≠X2 ACCEPT |
| 11 | 模板/DIFF：相对叶34 形态合理（机制换皮，非乱改主干）；叶33/34/32 未回撤 | **PASS** | DIFF `dc503904` 标 NEW；语义=mask-only ETF passive flow pressure overlay；叶33 **`afbbe7e7` UNCHANGED**；叶34 HOLD CLOSED / 叶32 HOLD **`45dd87dc`** 只读 |
| 12 | dry-compile PASS；CMD 拟 approved_cmd 含未来新 `.ok`；禁不当旗标；EXECUTED=false；live ok/QUIET ABSENT；COVER/CMD/RECEIPT 互钉 MATCH | **PASS** | 本机复跑见上；CMD 拟 `…LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_X2_HILIQ.ok`（未创建）；禁 `--no-overlap-report` / 禁 FULLA PRIMARY；RECEIPT EXECUTED=false；五件互钉 MATCH |

## 3. 残留风险（知情接受 · 签窗监控）

| 风险 | 等级 | 备注 |
|---|---|---|
| `after_daily_concat` 残峰仍可能逼近 split | **中** | 月分片后一次 concat；须 peak_proof；破→停+上报；**禁抬帽** |
| 再平衡日懒加载 ETF 份额×权重 I/O | **低–中** | `primary_load=rebal_day_lazy_etf_share_x_weight_scheme_A_pit`；可接受 |
| CLI `--no-overlap-report` 仍在（真跑已硬 STOP） | **管控** | 靠脚本硬 STOP + 签文双闸；消费端须读 overlap JSON（含 vs moneyflow/叶34） |
| soft-penalty 启用路径（非 PRIMARY） | **管控** | 默认关；启用须另窗+SW+style；不得抬作 PRIMARY 判决 |
| FULLA 研究失败仅 WARN | **低** | PRIMARY HILIQ 已写；研究失败不抬 PRIMARY |
| 叶26resid / 叶8a 路径常 GAP | **管控** | 可选 PIN_GAP 披露；不得伪造 Jaccard；leaf26-like raw 不得硬拒 |
| COUNT APPROX / KEEP 被误读为 ACCEPT | **管控** | 文钉+脚本钉均明示不解阻；签窗再钉 |
| C3 权重 percent vs fraction 自适应 | **低** | 以 `sample_sum>2` 判 percent_div100；与 PIN 一致；签窗回执须披露 `weight_unit` |

## 4. CONDITIONS（另窗签新 X2 `.ok` 前）

1. **本拍不签**：须主另排**独立 X2 签窗**；**新** `.ok`（建议名 `output/ai_factory/ARCH_RUN_AUTH_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_X2_HILIQ.ok` 或主定新名）；钉脚本 sha8 **`25ae4572` only**。
2. **禁 RESTORED `178e90e9`+`c1b71e64`+`245df63f`+`c5ed13df`+`5774bb6e`+二十票(+`81521fb5`)**：forbid∋26 sha8；禁复用叶25/27/30–34 任一 `.ok`。
3. **真跑前主 MATCH**：script sha256 全长 `25ae45723454423a31d4b0c6987c5eb0a2e8bb733c2506c2db67d628e91b4ad0`；dry-compile PASS；FROZEN `be9fc459` / FROZEN 审 `5a082d18` / PIN `dd17044a` / FROZEN RECEIPT `132ba6f1` / 本审回执。
4. **peak_proof REQUIRED**：回执须含 `after_mask` / `after_weight_pin` / `after_pressure_rebal_*` / `after_mask_cs_rebal_*` / `after_daily_concat`（及 ru_maxrss/VmHWM/`RSS_CHECK`）；破 soft/hard → 停+上报；**rss=1500 禁抬**。
5. **C7 签文硬钉**：真跑**必须**写并消费 `overlap_vs_moneyflow_leaf26resid_8a_25_27_30_31_32_33_34.json`；Jaccard≥0.7 → 硬拒；ρ>0.5 → 强度；required 缺→PIN_GAP；leaf26-like raw 诊断不得硬拒；签文 **禁** `--no-overlap-report`（脚本已硬 STOP，签文双保险）。
6. **C3 签文硬钉**：方案 A（次月首个交易日 09:00 Asia/Shanghai）+ 份额 `available_at≤t` + 映射三件套 + percent_div100；禁事后改方案 / 静默月末向后 asof 当 PIT 完备；COUNT APPROX ≠ 方案 A PIT。
7. **PRIMARY 纪律**：判决=HILIQ **mask-only** top_q=0.20；FULLA 仅 `--also-fulla-research`；不得静默改 FULLA 作 PRIMARY；soft-penalty 启用须另窗+SW+style，**不得**作 PRIMARY。
8. **C11 签文硬钉**：交付=exclusion mask overlay 叠主干；禁输出叶26 完整残差 α；禁 moneyflow/行业 ETF 持仓主输入；raw 同幅持续披露。
9. **PRIMARY CLI 钉**（无 `--no-overlap-report`）：
   `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf35_etf_passive_flow_pressure_overlay_alpha_build.py --universe HILIQ --window x2 --x2-end 20261009 --allow-real-data --arch-ok-path <NEW_OK> --out output/ai_factory/_leaf35_etf_passive_flow_pressure/<ET_TS>/`
10. sampler `/tmp/quantlab_leaf35_etf_passive_*`；out `_leaf35_etf_passive_flow_pressure/<ET_TS>/`；Arch **不代跑**；可挂 leaf35 自有 QUIET（当前 QUIET **ABSENT**）。
11. **C10 仍另队**：`0087c928` / 叶28/29 不得借本脚本/签窗夹带。
12. **C13 另窗**：decay KEEP 硬验收不在本构建脚本；X2/selfcheck 另窗；失败最多 WATCH/HOLD；**KEEP 不解阻** X2 ACCEPT。
13. live=false · promotion=false · book_smoke=false · **x2_accept=false** · selfcheck=false · **≠X2 ACCEPT** · COUNT APPROX 不解阻。

## 5. 禁项 / 本回合非动作

- **未签**任何 `.ok`（含新叶35 / RESTORED `178e90e9`+`c1b71e64`+`245df63f`+`c5ed13df`+`5774bb6e`+二十票+`81521fb5`）
- **未挂** QUIET；live QUIET **ABSENT**（未改）
- **未改** 脚本 `25ae4572` / COVER / CMD / DIFF / RECEIPT / FROZEN / PIN / who_pays
- **未** `--allow-real-data` / **未** `--execute` / **未**代跑真构建（仅 `py_compile` + dry）；repo `__pycache__/leaf35*` 本拍未依赖；未写 `output/ai_factory/_leaf35*` 真产物
- **未** RESTORED；**未**抬 rss；**未**触 A18 产物
- **未审**叶30 衰减修复 `0087c928`（另队）；**未打开**该 DRAFT；**未夹带**叶28/29
- **未改** 叶33 正式 `afbbe7e7`；**未回撤** 叶34 HOLD CLOSED / 叶32 HOLD `45dd87dc`
- **≠X2 ACCEPT** / ≠selfcheck / ≠Book-Smoke
- **未** SendToUser / **未**报 Leo（leo_notify=false）

## 6. 硬钉下一跳

```
脚本 25ae4572（本审 PASS_WITH_CONDITIONS · FROZEN be9fc459 / 审 5a082d18 / PIN dd17044a / RECEIPT 132ba6f1 / who_pays ee7ec307 / 迁仓 4e964d40）
  → 请主另排独立 X2 签窗（新 .ok；钉 25ae4572；§4 CONDITIONS）
      → AI prelaunch→execute（无 --no-overlap-report；peak_proof；overlap 含 moneyflow/叶26resid/8a/25/27/30–34；C3 方案 A；mask-only PRIMARY；C11≠叶26）
          → Arch CONSUME（≠X2 ACCEPT）
```

**本拍不签**。

## 7. 结论

| 项 | 值 |
|---|---|
| VERDICT | **PASS_WITH_CONDITIONS** |
| 脚本 | **`25ae4572` MATCH** |
| RECEIPT / COVER / CMD / DIFF | **`d9758eb6`** / **`eee0866b`** / **`c6d3b9ed`** / **`dc503904`** MATCH（DIFF≡脚本） |
| FROZEN / FROZEN 审 / PIN / FROZEN RECEIPT / 迁仓 / who_pays 审 | **`be9fc459`** / **`5a082d18`** / **`dd17044a`** / **`132ba6f1`** / **`4e964d40`** / **`ee7ec307`** MATCH |
| 叶33 正式 / 叶34 HOLD CLOSED / 叶32 HOLD | **`afbbe7e7` UNCHANGED** / 不回撤 / **`45dd87dc`** 不回撤 |
| dry-compile | **PASS**（exit0）；FULLA PRIMARY STOP exit2；无授权 STOP exit2 |
| EXECUTED | **false** |
| live `.ok` / QUIET | **0** / **ABSENT** |
| 请主 | **另排独立 X2 签窗**（钉 `25ae4572`；本拍不签） |
| live | **false** |
| leo_notify | **false** |

live=false · leo_notify=false · ≠X2 ACCEPT · 只审不签不挂不代跑.

## 8. 本审钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/audit/ARCH_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_ALPHA_BUILD_SCRIPT_REVIEW_20261027_ZH.md` |
| 脚本 sha8 | **`25ae4572`** |
| RECEIPT / COVER / CMD / DIFF | **`d9758eb6`** / **`eee0866b`** / **`c6d3b9ed`** / **`dc503904`** |
| FROZEN / FROZEN 审 / PIN / FROZEN RECEIPT / 迁仓 / who_pays 审 | **`be9fc459`** / **`5a082d18`** / **`dd17044a`** / **`132ba6f1`** / **`4e964d40`** / **`ee7ec307`** |
| 结论 | **PASS_WITH_CONDITIONS**（本拍不签；请主另排独立 X2 签窗） |

全文件 sha256 / sha8：以本机 `sha256sum` 为准（见 TEAM_STATE 顶条与父回报）。

live=false.
