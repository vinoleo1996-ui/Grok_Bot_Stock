# Arch 叶35 mapping recon 真值只读探针 · 独立 `.ok` 签发回执

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-27T14:37:14-04:00`（America/New_York） |
| 主令 | 主 ~14:31 ET priority · 叶35 VTRUE 只读探针签窗 OPEN→SIGN（VTRUE 审 `bbbf809b` PASS_WITH_CONDITIONS MATCH；钉探针 `2c2226e0`；正式 `25ae4572` UNCHANGED；禁 RESTORED `10927bd9`+）；主 14:34 ET 再令 YES SIGN 立即执签 |
| VTRUE 只审 | `bbbf809b…` **PASS_WITH_CONDITIONS** |
| DRAFT / COVER / CMD / RECEIPT / pending | `b7b9c61d…` / `554bc027…` / `cd0c6c56…` / `fefbfa7d…` / `1f17fee8…` |
| recon 审 / PIN C3 / VOID / void `.ok` | `cb3ca975…` / `dd17044a…` / `dfafff28…` / `10927bd9…` |
| live / promotion_approved / leo_notify | **false** / **false** / **false** |

## 结论

**SIGNED** — 叶35 ETF 被动资金流压力 overlay **mapping recon 真值只读诊断探针**（mechanism=`g1g5_ashare_etf_passive_flow_pressure_overlay_v1`；kind=`research_leaf_diagnostic_probe`；**≠正式 α 构建**；**≠ X2 ACCEPT**；**≠叶36**；**≠ selfcheck**；**≠ Book-Smoke**）**新** `.ok` 已落盘：`output/ai_factory/ARCH_RUN_AUTH_LEAF35_MAPPING_RECON_VTRUE_PROBE.ok`。诊断探针脚本 **`2c2226e0…` only**；正式脚本 **`25ae4572…` UNCHANGED**（禁改）；骨架 **`c2f2ca94…` UNCHANGED**；叶33 **`afbbe7e7…` UNCHANGED**。上游钉 MATCH：VTRUE 审 `bbbf809b` / DRAFT `b7b9c61d` / COVER `554bc027` / CMD `cd0c6c56` / RECEIPT `fefbfa7d` / pending `1f17fee8` / recon 审 `cb3ca975` / PIN `dd17044a` / VOID `dfafff28` / void `.ok` `10927bd9`。**禁 RESTORED** `10927bd9`+`178e90e9`+`c1b71e64`+`245df63f`+`c5ed13df`+`5774bb6e`+`81521fb5`+二十票（**n=27**）。rss 软/硬帽 **1500** 禁抬；peak_proof **REQUIRED**。真跑须 `--allow-real-data` + `--arch-ok-path <NEW_OK>`；out=`output/ai_factory/_leaf35_mapping_recon_vtrue/<ET_TS>/`；**禁写** alpha/mask/overlap。**Arch 不代跑**；QUIET **已挂且保留**供 AI prelaunch（本拍不 lift；holder=`leaf35_MAPPING_RECON_VTRUE_PROBE`；reason=`leaf35_mapping_recon_vtrue_readonly_probe`）。`0087c928`/叶28/29 **另队不夹带**；**禁触 A18**；**禁复跑 X2**。DIAG_EXECUTED@签=**false**；ALPHA_BUILD_EXECUTED@签=**false**。leo_notify=**false**。

## 钉点 MATCH 表

| 项 | 期望 | 实测 | 结果 |
|---|---|---|---|
| VTRUE 只审 | `bbbf809b` PASS_WITH_CONDITIONS | `bbbf809bacecd1c2a2a8ab81945c7d84def9cbd1d788b1eda65f3c0cb921f49d` | **MATCH** |
| DRAFT | `b7b9c61d…` | `b7b9c61d28857fedf78c45de44dae1ddcc92208807f2624601dd91749010d523` | **MATCH** |
| COVER | `554bc027…` | `554bc027080c7910523db3251cec6d42b9808a33ced289f221ce8003faa0f63b` | **MATCH** |
| CMD | `cd0c6c56…` | `cd0c6c56f97cb963aa72379f5f67320c58592fb4e280937b376dc5ac1c88d169` | **MATCH** |
| RECEIPT（AI） | `fefbfa7d…` | `fefbfa7d67d82c55f016c36ef5d22ec8bba8975a98988ab5fe36b462bad535eb` | **MATCH** |
| pending JSON | `1f17fee8…` | `1f17fee87a5cf91114fd9d51ea64c387ffe8a9c5fc27ff5ef61227977258100f` | **MATCH** |
| 探针脚本 | `2c2226e0…` only | `2c2226e00a232ad1caf61f9d456990e5b7abe2c0040976371d0036f5480cca67` | **MATCH** |
| 正式脚本 | `25ae4572…` UNCHANGED | `25ae45723454423a31d4b0c6987c5eb0a2e8bb733c2506c2db67d628e91b4ad0` | **MATCH** |
| 骨架 | `c2f2ca94…` UNCHANGED | `c2f2ca94993ac6d74a352f07353dc5384d96d166069d46e8f1b9c146b66d65d4` | **MATCH** |
| 叶33 | `afbbe7e7…` UNCHANGED | `afbbe7e7292c17399bbf4733d9f34a922e6d81f1a914a60d24dc61fcba86cbc9` | **MATCH** |
| recon 审 | `cb3ca975…` | `cb3ca975da2c965a03bad2b591aa812836bdd6e57da3cce8119eb5c6ff411bd4` | **MATCH** |
| PIN C3 | `dd17044a…` | `dd17044ab6f2890283f226112609eebfdb5dddcc10df8fda8e8565de8ac77a36` | **MATCH** |
| VOID | `dfafff28…` | `dfafff2887bbbe831821a54f6834ba3bbf31bdb9804b7bca2873bf4f0f3168c7` | **MATCH** |
| void `.ok` | `10927bd9…` | `10927bd906f8982de930beb5b7945618b912f138b1f23da4332556edc604ab7d` | **MATCH**（禁 RESTORED） |
| 拟 .ok 签前 | ABSENT（禁 RESTORED） | ABSENT | **MATCH** |
| QUIET 签前 | ABSENT | ABSENT | **MATCH** |
| 新 `.ok` sha8 ∉ forbid27 | ≠`10927bd9`/`178e90e9`/`c1b71e64`/`245df63f`/`c5ed13df`/`5774bb6e`/`81521fb5` 等 | `00eec671` ∉ forbid27 | **MATCH** |
| forbid 含七钉 | 含 `10927bd9`+`178e90e9`+`c1b71e64`+`245df63f`+`c5ed13df`+`5774bb6e`+`81521fb5`；n=27 | n=27 且七钉在列 | **MATCH** |
| pgrep leaf35/mapping_recon | 空 | 空 | **MATCH** |
| 窗期 | ≥90min prelaunch → expires | `2026-10-27T14:37:00-04:00` → `2026-10-27T16:07:00-04:00` / expires `2026-10-27T16:11:00-04:00`；签时 `2026-10-27T14:37:14-04:00` | **IN_WINDOW** |

## 钉

| 项 | 值 |
|---|---|
| `.ok` 路径 | `output/ai_factory/ARCH_RUN_AUTH_LEAF35_MAPPING_RECON_VTRUE_PROBE.ok` |
| `.ok` sha8 / 全长 | `00eec671` / `00eec671fc904ac745752070fd4b84b8939715d350d5b089dd5de09b6c19b291` |
| QUIET 路径 | `output/loop/RESEARCH_QUIET.lock` |
| QUIET sha8 / 全长 | `bf3470cb` / `bf3470cba95c5a487c37981099d016b07bf5dcb970b8384a716752b1f28ac402` |
| 探针脚本 | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_MAPPING_RECON_PROBE_VTRUE_DRAFT_20261027.py` = `2c2226e00a232ad1caf61f9d456990e5b7abe2c0040976371d0036f5480cca67` |
| 正式脚本 | `research/leaf35_etf_passive_flow_pressure_overlay_alpha_build.py` = `25ae45723454423a31d4b0c6987c5eb0a2e8bb733c2506c2db67d628e91b4ad0` **UNCHANGED** |
| 骨架 / 叶33 | `c2f2ca94…` UNCHANGED / `afbbe7e7…` UNCHANGED |
| VTRUE 只审 | `bbbf809bacecd1c2a2a8ab81945c7d84def9cbd1d788b1eda65f3c0cb921f49d` PASS_WITH_CONDITIONS |
| DRAFT / COVER / CMD / RECEIPT / pending | `b7b9c61d…` / `554bc027…` / `cd0c6c56…` / `fefbfa7d…` / `1f17fee8…` |
| recon 审 / PIN / VOID / void `.ok` | `cb3ca975…` / `dd17044a…` / `dfafff28…` / `10927bd9…` |
| kind / purpose | `research_leaf_diagnostic_probe` / `leaf35_mapping_recon_vtrue_readonly_probe_NOT_formal_alpha_NOT_x2_accept_NOT_leaf36_NOT_book_smoke` |
| 窗期 | `2026-10-27T14:37:00-04:00` → `2026-10-27T16:07:00-04:00`；expires `2026-10-27T16:11:00-04:00` |
| CLI dry | `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_MAPPING_RECON_PROBE_VTRUE_DRAFT_20261027.py --dry-compile-only` |
| CLI PRIMARY（诊断真跑） | `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_MAPPING_RECON_PROBE_VTRUE_DRAFT_20261027.py --universe HILIQ --window x2 --x2-end 20261009 --allow-real-data --arch-ok-path output/ai_factory/ARCH_RUN_AUTH_LEAF35_MAPPING_RECON_VTRUE_PROBE.ok --out output/ai_factory/_leaf35_mapping_recon_vtrue/<ET_TS>` |
| FALLBACK | **无**；峰＞1500 / 失败 / ABORT → Exit 94/95 停+上报（禁抬帽） |
| out | `output/ai_factory/_leaf35_mapping_recon_vtrue/<ET_TS>/` |
| rss 软/硬帽 | **1500** MB；禁抬帽；硬 Exit **94/95** |
| peak_proof | **REQUIRED** |
| 禁 RESTORED | **27** 票：`10927bd9,178e90e9,c1b71e64,245df63f,c5ed13df,5774bb6e,81521fb5,02426b73,4bb141c9,fdbaa512,aa25e989,7e239487,5af20222,5ae077fa,3c297052,e107383f,2be59acd,a7d98ac9,8e51de63,3a6caa4f,8bcd79dc,725be3e0,0f50daf7,3c19dd7d,1c32ab1e,6054b3bf,6de02e74`（含 `10927bd9,178e90e9,c1b71e64,245df63f,c5ed13df,5774bb6e,81521fb5`） |
| Book-Smoke / X2 ACCEPT / selfcheck / 叶36 / 正式 α | **false** / **false** / **false** / **≠** / **≠** |
| `0087c928` / 叶28/29 | 另队；**不在**本 `.ok` |
| MemAvailable@签 | 13050600 kB |
| DIAG_EXECUTED@签 / ALPHA_BUILD_EXECUTED@签 | **false** / **false** |

## QUIET / pgrep

| 项 | 值 |
|---|---|
| QUIET 挂时 | `2026-10-27T14:37:14-04:00` reason=`leaf35_mapping_recon_vtrue_readonly_probe` holder=`leaf35_MAPPING_RECON_VTRUE_PROBE` |
| do_not_lift_until_arch_or_consumed | **true**（本拍不 lift） |
| neq_a18 | **true** |
| pgrep leaf35/mapping_recon | 空 |
| Arch 代跑 `--allow-real-data` | **未执行**（DIAG_EXECUTED=false） |

## 下一跳

1. **主** MATCH `.ok`+`QUIET`+本 SIGNED 后令 AI prelaunch **单次真值只读探针**真跑（须在 expires 前；Arch **不代跑**）
2. AI 交 mapping recon 诊断回执（per_rebal / PIT 对照列 + peak_proof；峰＞1500→Exit 94/95 停；禁写 alpha/mask/overlap）→ 主再裁补丁窗 / HOLD
3. ≠正式 α；≠X2 ACCEPT；≠叶36；≠selfcheck；≠Book-Smoke；不解阻 `0087c928`/叶28/29；**≠A18**；不 RESTORED 27 票（含 `10927bd9`/`178e90e9`/`c1b71e64`/`245df63f`/`c5ed13df`/`5774bb6e`/`81521fb5`）；不改正式 `25ae4572`；禁复跑 X2；live=false；leo_notify=false

live=false.
