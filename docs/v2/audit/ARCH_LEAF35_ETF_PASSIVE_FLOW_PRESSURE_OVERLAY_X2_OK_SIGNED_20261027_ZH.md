# Arch 叶35 ETF 被动资金流压力 overlay · 独立 X2 `.ok` 签发回执

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-27T13:44:07-04:00`（America/New_York） |
| 主令 | 主 13:38 ET priority · 叶35 独立 X2 签窗 OPEN→SIGN（脚本审 `ea395dc4` PASS_WITH_CONDITIONS；钉脚本 `25ae4572` only） |
| 脚本审 | `ea395dc4…` **PASS_WITH_CONDITIONS** |
| FROZEN / ArchFROZEN / PIN / FROZEN RECEIPT | `be9fc459…` / `5a082d18…` / `dd17044a…` / `132ba6f1…` |
| COVER / CMD / DIFF / RECEIPT | `eee0866b…` / `c6d3b9ed…` / `dc503904…` / `d9758eb6…` |
| 迁仓 / COUNT RECEIPT / COUNT JSON | `4e964d40…` / `cbca88e7…` / `a17b75fb…` |
| who_pays 审 / WHO / who COVER | `ee7ec307…` / `05942769…` / `f41d7db8…` |
| live / promotion_approved / leo_notify | **false** / **false** / **false** |

## 结论

**SIGNED** — 叶35 ETF 被动资金流压力 overlay（mechanism=`g1g5_ashare_etf_passive_flow_pressure_overlay_v1`；PRIMARY=HILIQ×x2→20261009；**mask-only** top_q=**0.20**；soft-penalty **非 PRIMARY**；再平衡=20；**C3 方案 A**=月末权重点→次月首个交易日 09:00 Asia/Shanghai=`weight_available_at` ∧ 份额 `available_at≤t` ∧ 映射三件套 `510300→000300`/`510500→000905`/`512100→000852` ∧ `percent_div100` ∧ **禁**静默月末向后 asof；PIN **`dd17044a`**；primary_load=`rebal_day_lazy_etf_share_x_weight_scheme_A_pit`；**C11** overlay≠叶26 完整残差 α（禁 moneyflow/行业 ETF 持仓主输入） → `_leaf35_etf_passive_flow_pressure/<ET_TS>/`）**新** `.ok` 已落盘；**≠ RESTORED** `178e90e9`+`c1b71e64`+`245df63f`+`c5ed13df`+`5774bb6e`+二十票(+`81521fb5`)（**26**）；**≠ X2 ACCEPT**；**≠ selfcheck**；**≠ Book-Smoke**；脚本全长 **`25ae4572…`**；脚本审 **`ea395dc4` PASS_WITH_CONDITIONS**；COVER `eee0866b` / CMD `c6d3b9ed` / DIFF `dc503904` / RECEIPT `d9758eb6`；FROZEN `be9fc459` / ArchFROZEN `5a082d18` / FROZEN RECEIPT `132ba6f1`；PIN `dd17044a`；迁仓 `4e964d40` / COUNT RECEIPT `cbca88e7` / COUNT JSON `a17b75fb`；who_pays 审 `ee7ec307` / WHO `05942769` / who COVER `f41d7db8`；叶33 **`afbbe7e7` UNCHANGED**；叶32 HOLD **`45dd87dc`** 不回撤；叶34 HOLD CLOSED（`.ok` `178e90e9` / 回执 `a37257b9` / lift `3fce510e`）不回撤；模板 `4e0f3c00` 只读；**禁** `--no-overlap-report`；真跑须 `--allow-real-data` + `--arch-ok-path <NEW_OK>` 并写/消费 `overlap_vs_moneyflow_leaf26resid_8a_25_27_30_31_32_33_34.json`（Jaccard≥0.7 硬拒；ρ>0.5 强度；leaf26-like raw 诊断不硬拒；缺→PIN_GAP）；rss 软/硬帽 **1500** 禁抬（硬 Exit **94/95**）；peak_proof **REQUIRED**（`after_mask` / `after_weight_pin` / `after_pressure_rebal_*` / `after_mask_cs_rebal_*` / `after_daily_concat` + ru_maxrss/VmHWM/`RSS_CHECK`）；**Arch 不代跑**；叶30 KEEP/衰减修复 `0087c928` / 叶28/29 **另队不夹带**；KEEP **不解阻** X2 ACCEPT；COUNT APPROX **≠** ACCEPT；**禁触 A18**。QUIET **已挂且保留**供 AI prelaunch（本回合不 lift；holder=`leaf35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_X2`；reason=`leaf35_etf_passive_flow_pressure_overlay_x2_hiliq`）。PRIMARY only；FULLA 仅 `--also-fulla-research` 研究旁路；**无同票 FALLBACK**；峰＞1500→Exit 94/95 停+上报（禁抬帽）。ALPHA_BUILD_EXECUTED@签=**false**。**≠A18**。leo_notify=**false**。

## 钉点 MATCH 表

| 项 | 期望 | 实测 | 结果 |
|---|---|---|---|
| 脚本审 | `ea395dc4` PASS_WITH_CONDITIONS | `ea395dc42520c3840c5b14a443000246c937f34ad05408f436ffb2e446287b8e` | **MATCH** |
| 脚本 | `25ae4572…` only | `25ae45723454423a31d4b0c6987c5eb0a2e8bb733c2506c2db67d628e91b4ad0` | **MATCH** |
| COVER | `eee0866b` | `eee0866bb08af9b2bb8acca9dbc1799005fd2c0e0c8d8fc044b4f1290d4c04a4` | **MATCH** |
| CMD | `c6d3b9ed` | `c6d3b9ede7abef7172479205b7a6252f8556629a211046ccdeeb764b41f5220c` | **MATCH** |
| DIFF | `dc503904` | `dc50390418a18e373bdde712466c356ef57232b3210b088acd6c190d67b1a60f` | **MATCH** |
| RECEIPT | `d9758eb6` | `d9758eb600ea9d78c1ae9cf094b618677b8c97507cadfa04430cbafdd43ac23a` | **MATCH** |
| FROZEN | `be9fc459` | `be9fc4593249928460ec5a118a0bd79e033fd446ec921a64f6d47bdd09b01ed6` | **MATCH** |
| ArchFROZEN | `5a082d18` | `5a082d181f469ec49bab2efb73f6fb14976fc6d01a4a548de23eabe098cfd660` | **MATCH** |
| FROZEN RECEIPT | `132ba6f1` | `132ba6f1f78be22bd3e22c6214eaf5c2f3c0f92ebb6501161f0ec7ed674c676a` | **MATCH** |
| PIN C3 | `dd17044a` | `dd17044ab6f2890283f226112609eebfdb5dddcc10df8fda8e8565de8ac77a36` | **MATCH** |
| 迁仓 COUNT 脚本 | `4e964d40` | `4e964d4024115b3a73f97d7789dac22e328e6eed519ca4935fcd2dcf5ba82538` | **MATCH** |
| COUNT RECEIPT | `cbca88e7` | `cbca88e797c4c423e082d8db189ef1e0265747e90990817bbfd823f09798b431` | **MATCH** |
| COUNT JSON | `a17b75fb` | `a17b75fbb383620ed7e39470056f83031708a7f8b9ae9d4013583a4718aa28e6` | **MATCH** |
| who_pays 审 | `ee7ec307` | `ee7ec307e22bb5e6b98b6521d76e5f62a04311ffc9917efafde24524861a6f93` | **MATCH** |
| who_pays draft | `05942769` | `0594276917a88969456ed3b7103d7f51ca26d4b2923125295507f1a8f2802997` | **MATCH** |
| who COVER | `f41d7db8` | `f41d7db8f0632a8433972def18bd92b6f76f625fdabd9603b5fe18be74ca92a1` | **MATCH** |
| 叶33 正式 | `afbbe7e7` UNCHANGED | `afbbe7e7292c17399bbf4733d9f34a922e6d81f1a914a60d24dc61fcba86cbc9` | **MATCH** |
| 叶32 HOLD | `45dd87dc` 不回撤 | `45dd87dc915b89e887e2b02dd1fae2cdcbe3b40695db6f9dce22b89e42ec5d9e` | **MATCH** |
| 叶34 HOLD CLOSED | `178e90e9`/`a37257b9` 不回撤 | consumed `.ok`/`a37257b9` 在盘 | **MATCH** |
| 拟 .ok 签前 | ABSENT（禁 RESTORED） | ABSENT | **MATCH** |
| QUIET 签前 | ABSENT | ABSENT | **MATCH** |
| ai_factory live `.ok` | 0→1（本签） | 签前 0 / 签后 1 | **MATCH** |
| 新 `.ok` sha8 ∉ forbid26 | ≠`178e90e9`/`c1b71e64`/`245df63f`/`c5ed13df`/`5774bb6e`/`81521fb5` 等 | `10927bd9` ∉ forbid26 | **MATCH** |
| pgrep leaf35 | 空 | 空 | **MATCH** |
| 窗期 | ≥90min prelaunch → expires | `2026-10-27T13:38:00-04:00` → `2026-10-27T15:08:00-04:00` / expires `2026-10-27T15:12:00-04:00`；签时 `2026-10-27T13:44:07-04:00` | **IN_WINDOW** |

## 钉

| 项 | 值 |
|---|---|
| `.ok` 路径 | `output/ai_factory/ARCH_RUN_AUTH_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_X2_HILIQ.ok` |
| `.ok` sha8 / 全长 | `10927bd9` / `10927bd906f8982de930beb5b7945618b912f138b1f23da4332556edc604ab7d` |
| QUIET 路径 | `output/loop/RESEARCH_QUIET.lock` |
| QUIET sha8 / 全长 | `c8d95fee` / `c8d95fee5e032dd875b813bd0a2313d8bc868afa681bb0357b44daf4c24c62a5` |
| QUIET holder / reason | `leaf35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_X2` / `leaf35_etf_passive_flow_pressure_overlay_x2_hiliq` |
| 脚本 | `research/leaf35_etf_passive_flow_pressure_overlay_alpha_build.py` = `25ae45723454423a31d4b0c6987c5eb0a2e8bb733c2506c2db67d628e91b4ad0` |
| 脚本审 | `ea395dc42520c3840c5b14a443000246c937f34ad05408f436ffb2e446287b8e` PASS_WITH_CONDITIONS |
| COVER / CMD / DIFF / RECEIPT | `eee0866b…` / `c6d3b9ed…` / `dc503904…` / `d9758eb6…` |
| FROZEN / ArchFROZEN / FROZEN RECEIPT / PIN | `be9fc459…` / `5a082d18…` / `132ba6f1…` / `dd17044a…` |
| 迁仓 / COUNT RECEIPT / COUNT JSON | `4e964d40…` / `cbca88e7…` / `a17b75fb…` |
| who_pays 审 / WHO / who COVER | `ee7ec307…` / `05942769…` / `f41d7db8…` |
| 叶33 / 叶32 HOLD / 叶34 HOLD CLOSED | `afbbe7e7` UNCHANGED / `45dd87dc` 不回撤 / `178e90e9`+`a37257b9` 不回撤 |
| 窗期 | `2026-10-27T13:38:00-04:00` → `2026-10-27T15:08:00-04:00`；expires `2026-10-27T15:12:00-04:00` |
| CLI PRIMARY | `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf35_etf_passive_flow_pressure_overlay_alpha_build.py --universe HILIQ --window x2 --x2-end 20261009 --allow-real-data --arch-ok-path output/ai_factory/ARCH_RUN_AUTH_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_X2_HILIQ.ok --out output/ai_factory/_leaf35_etf_passive_flow_pressure/<ET_TS>`；**无** `--no-overlap-report` |
| FALLBACK | **无**；峰＞1500 / 失败 / ABORT → Exit 94/95 停+上报（禁抬帽） |
| rss 软/硬帽 | **1500** MB；禁抬帽；硬 Exit **94/95** |
| overlap | 强制 `overlap_vs_moneyflow_leaf26resid_8a_25_27_30_31_32_33_34.json`；Jaccard≥0.7 硬拒；ρ>0.5 强度；leaf26-like raw 不硬拒；缺→PIN_GAP；forbid_no_overlap_report=true |
| PRIMARY load | **rebal_day_lazy_etf_share_x_weight_scheme_A_pit** |
| C3 | 方案 A；PIN `dd17044a`；`c3_mode=weight_pit_scheme_A`；月末权重点→次月首个交易日 09:00 Asia/Shanghai；禁静默月末向后 asof |
| C11 | forbid_leaf26_full_resid_alpha_as_primary；forbid_moneyflow_main_input；forbid_industry_etf_holdings_main |
| mechanism / top_q / delivery / 再平衡 | `g1g5_ashare_etf_passive_flow_pressure_overlay_v1`；0.20；mask-only；20 |
| 产物 | `_leaf35_etf_passive_flow_pressure/<ET_TS>/` + exclusion_mask parquet + `run_meta.json` + overlap JSON |
| 采样 | 仅 `/tmp/quantlab_leaf35_etf_passive_*` |
| 禁 RESTORED | **26** 票：`178e90e9,c1b71e64,245df63f,c5ed13df,5774bb6e,81521fb5,02426b73,4bb141c9,fdbaa512,aa25e989,7e239487,5af20222,5ae077fa,3c297052,e107383f,2be59acd,a7d98ac9,8e51de63,3a6caa4f,8bcd79dc,725be3e0,0f50daf7,3c19dd7d,1c32ab1e,6054b3bf,6de02e74` |
| Book-Smoke / X2 ACCEPT / selfcheck | **false** / **false** / **false** |
| peak_proof | **REQUIRED**（after_mask / after_weight_pin / after_pressure_rebal_* / after_mask_cs_rebal_* / after_daily_concat + ru_maxrss/VmHWM/RSS_CHECK） |
| `0087c928` / 叶28/29 | 另队；**不在**本 `.ok`；KEEP 不解阻；COUNT APPROX ≠ ACCEPT |
| MemAvailable@签 | 11956716 kB |

## QUIET / pgrep

| 项 | 值 |
|---|---|
| QUIET 挂时 | `2026-10-27T13:44:07-04:00` reason=`leaf35_etf_passive_flow_pressure_overlay_x2_hiliq` holder=`leaf35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_X2` |
| do_not_lift_until_arch_or_consumed | **true**（本拍不 lift） |
| neq_a18 | **true** |
| pgrep leaf35 | 空 |
| 签时 web | **empty**（无 kline/export_static/snapshot/gen）；**未触 A18**；AI prelaunch 仍须 healthz quiet + 再验 pgrep 后跑 |
| Arch 代跑 `--allow-real-data` | **未执行** |

## 下一跳

1. **主** MATCH `.ok`+`QUIET` 后令 AI prelaunch 单次 PRIMARY（须在 expires 前；Arch **不代跑**）
2. AI 交实峰回执（mask/alpha sha + run_meta sha + overlap JSON 含 vs moneyflow/叶26resid/8a/25/27/30–34 + peak rss 含 after_mask / after_weight_pin / after_pressure_rebal_* / after_mask_cs_rebal_* / after_daily_concat；峰＞1500→Exit 94/95 停；Jaccard≥0.7→硬拒票）→ Arch 核 CONSUME
3. ≠X2 ACCEPT；≠selfcheck；≠Book-Smoke；不解阻 `0087c928`/叶28/29 另队；KEEP 不解阻；COUNT APPROX ≠ ACCEPT；**≠A18**；不 RESTORED 26 票；live=false；leo_notify=false

live=false.
