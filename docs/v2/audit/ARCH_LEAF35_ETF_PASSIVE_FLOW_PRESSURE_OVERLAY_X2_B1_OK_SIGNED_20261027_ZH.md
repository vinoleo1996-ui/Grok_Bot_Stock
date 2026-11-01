# Arch 叶35 ETF 被动资金流压力 overlay · B1 份额 PIT 落地后独立 X2 `.ok` 签发回执

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-27T15:23:17-04:00`（America/New_York） |
| 主令 | 主 ~15:19 ET priority · 叶35 B1 新 X2 签窗 OPEN→SIGN（脚本审 `df19dd2a` PASS_WITH_CONDITIONS；钉脚本 `434ff42c` only；≠X2 ACCEPT；≠叶36） |
| 脚本审（落地） | `df19dd2a…` **PASS_WITH_CONDITIONS** |
| 补丁审 | `31a08790…` PASS_WC · endorse B1 |
| LANDED COVER / CMD / DIFF / RECEIPT | `fb514f52…` / `e2773c12…` / `06a202c3…` / `dd99468d…` |
| DRAFT / DIFF DRAFT | `bdfd3c56…` / `2d3abebd…` |
| FROZEN / ArchFROZEN / PIN / FROZEN RECEIPT | `be9fc459…` / `5a082d18…` / `dd17044a…` / `132ba6f1…` |
| 旧脚本（禁当活脚本） | `25ae4572…` · `ban_use_prior_script_as_live=true` |
| live / promotion_approved / leo_notify | **false** / **false** / **false** |

## 结论

**SIGNED** — 叶35 ETF 被动资金流压力 overlay（mechanism=`g1g5_ashare_etf_passive_flow_pressure_overlay_v1`；PRIMARY=HILIQ×x2→20261009；**mask-only** top_q=**0.20**；soft-penalty **非 PRIMARY**；再平衡=20；**C3 方案 A**；**份额 PIT B1**=`available_at≤t_ts` asof 最新行（取消 `trade_date==rebal` 硬过滤；对齐 PIN §1.3）；PIN **`dd17044a`**；primary_load=`rebal_day_lazy_etf_share_x_weight_scheme_A_pit`；**C11** overlay≠叶26 完整残差 α → `_leaf35_etf_passive_flow_pressure/<ET_TS>/`）**新** `.ok` 已落盘；脚本全长 **`434ff42c…` only**（≠旧 `25ae4572`；禁把 `25ae4572` 当活脚本）；脚本审 **`df19dd2a` PASS_WITH_CONDITIONS**；补丁审 **`31a08790`**；LANDED COVER `fb514f52` / CMD `e2773c12` / DIFF `06a202c3` / RECEIPT `dd99468d`；DRAFT `bdfd3c56` / DIFF DRAFT `2d3abebd`；FROZEN `be9fc459` / ArchFROZEN `5a082d18` / PIN `dd17044a`；叶33 **`afbbe7e7` UNCHANGED**；叶32 HOLD **`45dd87dc`** / 叶34 HOLD CLOSED **`178e90e9`** 不回撤。**禁 RESTORED** `00eec671`+`10927bd9`+`178e90e9`+`c1b71e64`+`245df63f`+`c5ed13df`+`5774bb6e`+`81521fb5`+二十票（**n=28**）。**≠ X2 ACCEPT**；**≠ selfcheck**；**≠ Book-Smoke**；**≠叶36**。rss **1500** 禁抬（硬 Exit **94/95**）；peak_proof **REQUIRED**；须 `--allow-real-data` + `--arch-ok-path <NEW_OK>` 并写/消费 overlap JSON；**禁** `--no-overlap-report`。**Arch 不代跑**；QUIET **已挂且保留**供 AI prelaunch（本回合不 lift；holder=`leaf35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_X2`；reason=`leaf35_etf_passive_flow_pressure_overlay_x2_hiliq_b1`）。ALPHA_BUILD_EXECUTED@签=**false**。**≠A18**。leo_notify=**false**。

## 钉点 MATCH 表

| 项 | 期望 | 实测 | 结果 |
|---|---|---|---|
| 脚本审（落地） | `df19dd2a` PASS_WITH_CONDITIONS | `df19dd2af1afa6b19cf571af1393bc0c71149c23fdcf62660389c014a0f861c5` | **MATCH** |
| 补丁审 | `31a08790` PASS_WC endorse B1 | `31a08790967f49fb25443e81d93c0dcb68dab46a7abaa378f89d6c2ede9b3eac` | **MATCH** |
| 脚本 | `434ff42c…` only | `434ff42c1ba7998e122e0ded4f984c98d40ecbfc12f124afe7ef99742bd69b0a` | **MATCH** |
| 旧脚本对照 | `25ae4572` 禁当活脚本 | `ban_use_prior_script_as_live=true` / prior=`25ae45723454423a31d4b0c6987c5eb0a2e8bb733c2506c2db67d628e91b4ad0` | **MATCH** |
| LANDED COVER | `fb514f52` | `fb514f526255072d1929d3a5bc72b24c1d7409fae735783d357a4a25672017d5` | **MATCH** |
| LANDED CMD | `e2773c12` | `e2773c12395f110b6293d4230d7d6848010ee63c13c457872f95f83c8d41b66a` | **MATCH** |
| LANDED DIFF | `06a202c3` | `06a202c3edcda56a687063a0ac6374f41761587681418ed8b5245d93b38e7347` | **MATCH** |
| LANDED RECEIPT | `dd99468d` | `dd99468d841617fc062ad868420fbbde4033d08395c132cbf9600fe737360402` | **MATCH** |
| DRAFT / DIFF DRAFT | `bdfd3c56` / `2d3abebd` | MATCH | **MATCH** |
| FROZEN / PIN | `be9fc459` / `dd17044a` | MATCH | **MATCH** |
| 叶33 | `afbbe7e7` UNCHANGED | MATCH | **MATCH** |
| 拟 .ok 签前 | ABSENT（禁 RESTORED） | ABSENT | **MATCH** |
| QUIET 签前 | ABSENT | ABSENT | **MATCH** |
| ai_factory live `.ok` | 0→1（本签） | 签前 0 / 签后 1 | **MATCH** |
| 新 `.ok` sha8 ∉ forbid28 | ≠`00eec671`/`10927bd9`/… | 新 sha8 ∉ forbid28 | **MATCH** |
| forbid n / 含双钉 | n=28；含 `00eec671`+`10927bd9` | n=28 且双钉在列首 | **MATCH** |
| pgrep leaf35 | 空 | 空 | **MATCH** |
| 窗期 | ≥90min → expires | `2026-10-27T15:19:00-04:00` → `2026-10-27T16:49:00-04:00` / expires `2026-10-27T16:53:00-04:00`；签时 `2026-10-27T15:23:17-04:00` | **IN_WINDOW** |

## 钉

| 项 | 值 |
|---|---|
| `.ok` 路径 | `output/ai_factory/ARCH_RUN_AUTH_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_X2_HILIQ.ok` |
| `.ok` sha8 / 全长 | `eb70eef4` / `eb70eef4386ae856f5f0b02733bca718ff96125765556fd72b70fefc82f94921` |
| QUIET 路径 | `output/loop/RESEARCH_QUIET.lock` |
| QUIET sha8 / 全长 | `ef9b69b4` / `ef9b69b486edb3ec8d679b7aae22d5d21e33cedff85db5cdfea331dfc80bac3b` |
| QUIET holder / reason | `leaf35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_X2` / `leaf35_etf_passive_flow_pressure_overlay_x2_hiliq_b1` |
| 脚本 | `research/leaf35_etf_passive_flow_pressure_overlay_alpha_build.py` = `434ff42c1ba7998e122e0ded4f984c98d40ecbfc12f124afe7ef99742bd69b0a` |
| 旧脚本（禁活） | `25ae45723454423a31d4b0c6987c5eb0a2e8bb733c2506c2db67d628e91b4ad0` · `ban_use_prior_script_as_live=true` |
| 脚本审 / 补丁审 | `df19dd2af1afa6b19cf571af1393bc0c71149c23fdcf62660389c014a0f861c5` / `31a08790967f49fb25443e81d93c0dcb68dab46a7abaa378f89d6c2ede9b3eac` PASS_WITH_CONDITIONS |
| LANDED COVER / CMD / DIFF / RECEIPT | `fb514f52…` / `e2773c12…` / `06a202c3…` / `dd99468d…` |
| DRAFT / DIFF DRAFT | `bdfd3c56…` / `2d3abebd…` |
| FROZEN / ArchFROZEN / FROZEN RECEIPT / PIN | `be9fc459…` / `5a082d18…` / `132ba6f1…` / `dd17044a…` |
| 叶33 / 叶32 HOLD / 叶34 HOLD CLOSED | `afbbe7e7` UNCHANGED / `45dd87dc` 不回撤 / `178e90e9` 不回撤 |
| 窗期 | `2026-10-27T15:19:00-04:00` → `2026-10-27T16:49:00-04:00`；expires `2026-10-27T16:53:00-04:00` |
| CLI PRIMARY | `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf35_etf_passive_flow_pressure_overlay_alpha_build.py --universe HILIQ --window x2 --x2-end 20261009 --allow-real-data --arch-ok-path output/ai_factory/ARCH_RUN_AUTH_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_X2_HILIQ.ok --out output/ai_factory/_leaf35_etf_passive_flow_pressure/<ET_TS>`；**无** `--no-overlap-report` |
| FALLBACK | **无**；峰＞1500 / 失败 / ABORT → Exit 94/95 停+上报（禁抬帽） |
| rss 软/硬帽 | **1500** MB；禁抬帽；硬 Exit **94/95** |
| overlap | 强制 `overlap_vs_moneyflow_leaf26resid_8a_25_27_30_31_32_33_34.json`；Jaccard≥0.7 硬拒；ρ>0.5 强度；leaf26-like raw 不硬拒；缺→PIN_GAP |
| PRIMARY load / 份额 PIT | **rebal_day_lazy_etf_share_x_weight_scheme_A_pit** / **B1** `available_at≤t_ts` asof |
| C3 / C11 | 方案 A；PIN `dd17044a`；forbid_leaf26_full_resid / moneyflow / 行业 ETF 持仓主输入 |
| mechanism / top_q / delivery | `g1g5_ashare_etf_passive_flow_pressure_overlay_v1`；0.20；mask-only |
| 禁 RESTORED | **28** 票：`00eec671,10927bd9,178e90e9,c1b71e64,245df63f,c5ed13df,5774bb6e,81521fb5,02426b73,4bb141c9,fdbaa512,aa25e989,7e239487,5af20222,5ae077fa,3c297052,e107383f,2be59acd,a7d98ac9,8e51de63,3a6caa4f,8bcd79dc,725be3e0,0f50daf7,3c19dd7d,1c32ab1e,6054b3bf,6de02e74` |
| Book-Smoke / X2 ACCEPT / selfcheck / 叶36 | **false** / **false** / **false** / **≠** |
| peak_proof | **REQUIRED** |
| MemAvailable@签 | 12831708 kB |
| ALPHA_BUILD_EXECUTED@签 | **false** |

## QUIET / pgrep

| 项 | 值 |
|---|---|
| QUIET 挂时 | `2026-10-27T15:23:17-04:00` reason=`leaf35_etf_passive_flow_pressure_overlay_x2_hiliq_b1` holder=`leaf35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_X2` |
| do_not_lift_until_arch_or_consumed | **true**（本拍不 lift） |
| neq_a18 | **true** |
| pgrep leaf35 | 空 |
| Arch 代跑 `--allow-real-data` | **未执行**（ALPHA_BUILD_EXECUTED=false） |

## 下一跳

1. **主** MATCH `.ok`+`QUIET` 后令 AI prelaunch 单次 PRIMARY（须在 expires 前；Arch **不代跑**）
2. AI 交实峰回执（mask/alpha sha + run_meta sha + overlap JSON + peak rss；峰＞1500→Exit 94/95 停；Jaccard≥0.7→硬拒票）→ Arch 核 CONSUME
3. ≠X2 ACCEPT；≠selfcheck；≠Book-Smoke；≠叶36；不解阻 `0087c928`/叶28/29；KEEP 不解阻；COUNT APPROX ≠ ACCEPT；**≠A18**；不 RESTORED 28 票；禁把 `25ae4572` 当活脚本；live=false；leo_notify=false

live=false.
