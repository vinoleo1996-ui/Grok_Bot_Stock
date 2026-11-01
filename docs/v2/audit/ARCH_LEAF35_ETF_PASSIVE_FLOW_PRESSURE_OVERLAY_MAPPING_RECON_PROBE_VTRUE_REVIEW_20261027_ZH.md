# Arch 审阅：叶35 ETF_PASSIVE_FLOW_PRESSURE_OVERLAY · mapping recon 真值只读探针版（VTRUE · Option A · 只审不改不签不代跑）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审 Option A 真值只读探针版） |
| 时刻 | `2026-10-27T14:27:51-04:00`（America/New_York；墙钟 `2026-10-27 14:27 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 对照 | 探针 py **`2c2226e0`** · DRAFT ZH **`b7b9c61d`** · COVER **`554bc027`** · CMD **`cd0c6c56`** · RECEIPT **`fefbfa7d`** · pending JSON **`1f17fee8`** · Arch recon 审 **`cb3ca975`** · 骨架 **`c2f2ca94` UNCHANGED** · 正式脚本 **`25ae4572` UNCHANGED** · VOID **`dfafff28`** · ok VOID **`10927bd9`** · QUIET lift **`f50975e4`** · PIN C3 **`dd17044a`** · COUNT JSON **`a17b75fb`** · COUNT script **`4e964d40`** · 叶33 **`afbbe7e7` UNCHANGED** |
| 本回合动作 | **只审**；**不签**任何 `.ok`；**不挂** QUIET；**不代跑**真值探针/X2；**不改**正式脚本 `25ae4572`；**不改**骨架 `c2f2ca94`；**不** RESTORED `10927bd9`+`178e90e9`+`c1b71e64`+旧票；**不降门**；**不开叶36**；**≠X2 ACCEPT**；live=false；**不报 Leo** |
| 触发 | 主 · 叶35 Option A 真值只读探针版（VTRUE）只审 GO（诊断票；非叶36；≠X2 ACCEPT；EXECUTED_PROBE=false） |
| Arch 推荐（讨论向） | **PASS 后请主裁是否新签只读探针 `.ok`**（钉本 VTRUE py **`2c2226e0`**；禁 RESTORED **`10927bd9`**）；本拍**不**代签、**不**真跑 |

## 0. 一句话

叶35 Option A **真值只读探针版（VTRUE）PASS_WITH_CONDITIONS**：探针/DRAFT/COVER/CMD/RECEIPT/pending/上游 recon 审/骨架/正式/VOID/PIN/COUNT/叶33 **MATCH**；Arch C2 只读诊断成立（禁写 alpha/mask/overlap；禁改 `25ae4572`）；PIN §1.3 / COUNT 对照列（`n_share_rows` / `n_share_rows_avail_le_tts` / `n_share_rows_count_approx_style` / `n_share_rows_pin13_avail_only`）钉齐；VOID/`10927bd9` → **STOP rc=5**；缺 `.ok` → **STOP rc=4**；无 `--allow-real-data` → **rc=3**；`--dry-compile-only` / `py_compile` **PASS**；`--allow-real-data` 路径**已实现**真跑（不再骨架 rc=3）；本拍 **EXECUTED_PROBE=false**（未真跑）。**请主裁是否新签只读探针 `.ok`**（禁 RESTORED）。本拍未签/未挂/未代跑/未改 `25ae4572`。

## 1. 钉表再核（本机 sha256）

| 件 | 路径 / 值 | 期望 sha8 | 实测全长 | 结果 |
|---|---|---|---|---|
| VTRUE 探针 py | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_MAPPING_RECON_PROBE_VTRUE_DRAFT_20261027.py` | `2c2226e0` | `2c2226e00a232ad1caf61f9d456990e5b7abe2c0040976371d0036f5480cca67` | **MATCH** |
| VTRUE DRAFT ZH | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_MAPPING_RECON_PROBE_VTRUE_DRAFT_20261027_ZH.md` | `b7b9c61d` | `b7b9c61d28857fedf78c45de44dae1ddcc92208807f2624601dd91749010d523` | **MATCH** |
| VTRUE COVER | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_MAPPING_RECON_PROBE_VTRUE_COVER_DRAFT_20261027_ZH.md` | `554bc027` | `554bc027080c7910523db3251cec6d42b9808a33ced289f221ce8003faa0f63b` | **MATCH** |
| VTRUE CMD | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_MAPPING_RECON_PROBE_VTRUE_CMD_DRAFT_20261027_ZH.md` | `cd0c6c56` | `cd0c6c56f97cb963aa72379f5f67320c58592fb4e280937b376dc5ac1c88d169` | **MATCH** · 本拍不执行真跑 |
| VTRUE RECEIPT（AI） | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_MAPPING_RECON_PROBE_VTRUE_RECEIPT_20261027_ZH.md` | `fefbfa7d` | `fefbfa7d67d82c55f016c36ef5d22ec8bba8975a98988ab5fe36b462bad535eb` | **MATCH** · EXECUTED_PROBE=false |
| pending JSON | `output/ai_factory/leaf35_etf_passive_flow_pressure_mapping_recon_vtrue_pending_20261027.json` | `1f17fee8` | `1f17fee87a5cf91114fd9d51ea64c387ffe8a9c5fc27ff5ef61227977258100f` | **MATCH** · executed_probe=false |
| Arch recon 审 | `docs/v2/audit/ARCH_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_MAPPING_RECON_REVIEW_20261027_ZH.md` | `cb3ca975` | `cb3ca975da2c965a03bad2b591aa812836bdd6e57da3cce8119eb5c6ff411bd4` | **MATCH** · Option A |
| 骨架探针 | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_MAPPING_RECON_PROBE_DRAFT_20261027.py` | `c2f2ca94` | `c2f2ca94993ac6d74a352f07353dc5384d96d166069d46e8f1b9c146b66d65d4` | **UNCHANGED** |
| 正式脚本 | `research/leaf35_etf_passive_flow_pressure_overlay_alpha_build.py` | `25ae4572` | `25ae45723454423a31d4b0c6987c5eb0a2e8bb733c2506c2db67d628e91b4ad0` | **UNCHANGED** |
| Arch VOID | `docs/v2/audit/ARCH_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_X2_VOID_ABORT_ZERO_MASK_ROWS_20261027_ZH.md` | `dfafff28` | `dfafff2887bbbe831821a54f6834ba3bbf31bdb9804b7bca2873bf4f0f3168c7` | **MATCH** |
| `.ok` VOID 归档 | `output/ai_factory/_consumed/…10927bd9.VOID.ABORT_ZERO_MASK_ROWS…ok` | `10927bd9` | `10927bd906f8982de930beb5b7945618b912f138b1f23da4332556edc604ab7d` | **MATCH** · live ABSENT |
| QUIET lift | `output/loop/_lifted/…ABORT_ZERO_MASK_ROWS_LIFTED_20261027T1359ET.lock` | `f50975e4` | `f50975e420c89357e957ab628445a0f599f775081d3a9374382ee83da67363d2` | **MATCH** |
| PIN C3 | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_WEIGHT_PIT_PIN_20261027_ZH.md` | `dd17044a` | `dd17044ab6f2890283f226112609eebfdb5dddcc10df8fda8e8565de8ac77a36` | **MATCH** |
| COUNT JSON | `output/ai_factory/leaf35_etf_passive_flow_pressure_count_20261027.json` | `a17b75fb` | `a17b75fbb383620ed7e39470056f83031708a7f8b9ae9d4013583a4718aa28e6` | **MATCH**（引用核） |
| COUNT script | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_COUNT_GATE_SCRIPT_20261027.py` | `4e964d40` | `4e964d4024115b3a73f97d7789dac22e328e6eed519ca4935fcd2dcf5ba82538` | **MATCH**（引用核） |
| 叶33 正式 | `research/leaf33_share_unlock_pressure_resid_alpha_build.py` | `afbbe7e7` | `afbbe7e7292c17399bbf4733d9f34a922e6d81f1a914a60d24dc61fcba86cbc9` | **UNCHANGED**（本票未触） |
| live leaf35 `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF35*` | 0 | 0 | **ABSENT** |
| live QUIET | `output/loop/RESEARCH_QUIET.lock` | ABSENT | ABSENT | **ABSENT** |
| VTRUE 真跑 out | `output/ai_factory/_leaf35_mapping_recon_vtrue/` / `mapping_recon_vtrue_per_rebal*` | ABSENT | ABSENT | **ABSENT**（未真跑） |

交叉引用：DRAFT↔COVER↔CMD↔RECEIPT↔pending 均钉 VTRUE py/`2c2226e0`、Arch recon/`cb3ca975`、正式/`25ae4572`、骨架/`c2f2ca94`、PIN/`dd17044a`、VOID/`dfafff28`、禁 RESTORED `10927bd9`、Option A、EXECUTED_PROBE=false。

## 2. 必审清单（架构裁决）

| # | 审点 | 结果 | 证据 |
|---|---|---|---|
| 1 | **Arch C2**：只读诊断；禁写 alpha/mask/overlap；禁改正式脚本 | **PASS** | 探针住 `docs/v2/audit/`（非 `research/`）；`FORMAL_SHA8_PIN=25ae4572` drift→STOP；`load_formal_module` 只读 import；out 仅写 `mapping_recon_vtrue_per_rebal.json/.tsv`；payload/`ban_write_alpha_mask_overlap=true`；禁 `--force`/抬 rss。**条件见 C3**（out 目录名扫描为 no-op，但写路径钉 diag 名）。 |
| 2 | **PIN §1.3 / COUNT 对照列**：正式份额 PIT vs COUNT APPROX vs PIN「仅 available_at≤t_ts」 | **PASS** | 钉列齐：`n_share_rows`（trade_date==rebal）/`n_share_rows_avail_le_tts`（再 avail≤15:00）/`n_share_rows_count_approx_style`（同日未滤 avail）/`n_share_rows_pin13_avail_only`（仅 avail≤t_ts，无 trade_date==rebal）；dry payload `share_pit_contrast` 三口径明文；`n_weight_rows_schemeA` 次嫌疑列齐。 |
| 3 | **VOID/`10927bd9` STOP**；缺 `.ok` STOP；禁 RESTORED | **PASS** | `FORBIDDEN_OK` n=**27** 含 `10927bd9`+`178e90e9`+`c1b71e64`+二十四；本机 `--allow-real-data`+VOID ok → **STOP rc=5**；缺/空 `.ok` → **STOP rc=4**；无 diag out 新产物。 |
| 4 | `--allow-real-data` 真跑路径已实现（≠骨架 rc=3）；无 allow / dry 行为正确 | **PASS** | 默认无 allow → **rc=3**；`--dry-compile-only` → **rc=0** `executed_probe=false`；`--allow-real-data`+合法新 `.ok`+`--out` → 进入 `run_real_probe`（本拍**未**持新 `.ok` 真跑）。 |
| 5 | py_compile / dry-compile；**禁止**本拍真跑；EXECUTED_PROBE=false | **PASS** | 本机 `python3 -m py_compile` **PASS**；`--dry-compile-only` **PASS** rc=0（formal=`25ae4572` / skel=`c2f2ca94` / leaf33=`afbbe7e7`）；pending/`1f17fee8` `executed_probe=false`；无 `mapping_recon_vtrue*` 真跑产物；本拍**未**加载份额/权重大表重算。 |
| 6 | 正式脚本 / 骨架 / 叶33 UNCHANGED；≠X2 ACCEPT；≠叶36 | **PASS** | 审后正式仍 **`25ae4572`**；骨架仍 **`c2f2ca94`**；叶33 **`afbbe7e7`**；票面/JSON `x2_accept=false` / `not_leaf36=true` / live=false / leo_notify=false。 |
| 7 | 状态干净：live `.ok`=0；QUIET ABSENT；禁代改代跑代签 | **PASS** | live leaf35 `.ok`=0；`RESEARCH_QUIET.lock` ABSENT；lift `f50975e4` MATCH；本拍未签/未挂/未代跑/未改字节。 |
| 8 | 与上游 recon 审 `cb3ca975` Option A CONDITIONS 对齐 | **PASS** | 本版即 C2「后续真值探针版」落地；列钉=Arch C2；禁 RESTORED；真跑须**新** `.ok`（本拍不签）。 |

## 3. CONDITIONS（采纳后 / 探针签窗前）

1. **C1 本拍不落地**：不签 `.ok`；不挂 QUIET；不代跑真值探针/X2；不改正式脚本 **`25ae4572`**；不改骨架 **`c2f2ca94`**；不降门；不开叶36。PASS ≠ 可签 / 可真跑 / ≠X2 ACCEPT。
2. **C2 请主裁是否新签只读探针 `.ok`（YES 路径）**：若主要填 per-rebal 真数，须发**新**只读探针 `.ok`（建议名由主定，如 `ARCH_RUN_AUTH_LEAF35_MAPPING_RECON_VTRUE_PROBE.ok`）；钉 VTRUE 探针 sha8 **`2c2226e0`**（全长 `2c2226e00a232ad1caf61f9d456990e5b7abe2c0040976371d0036f5480cca67`）；CLI 须 `--allow-real-data` + `--arch-ok-path <NEW_PROBE_OK>` + `--out <diag>`；**禁** RESTORED **`10927bd9`** / **`178e90e9`** / **`c1b71e64`** / **`245df63f`** / **`c5ed13df`** / **`5774bb6e`** / **`81521fb5`**+二十票；**禁**改/覆盖正式脚本 `25ae4572`；rss=1500 禁抬；peak_proof REQUIRED；**禁**写 alpha/mask/overlap。
3. **C3 真跑范围仅诊断**：out 拟 `output/ai_factory/_leaf35_mapping_recon_vtrue/<ET_TS>/` 或 `/tmp/quantlab_leaf35_mapping_recon_vtrue_<ET_TS>`；仅 `mapping_recon_vtrue_per_rebal.json` + `.tsv`；**≠**正式 α / **≠**X2；全窗 share 表加载须受 rss=1500/`RSS_CHECK` 硬停约束（peak_proof）。
4. **C4 Option B 仍次步**：探针填数后再开补丁 DRAFT（PIN §1.3↔实现张力）；**仍禁本拍改正式脚本**；补丁落地须新脚本 sha8 + 新 X2 `.ok`（与探针窗分离）。
5. **C5 禁 RESTORED / 禁夹带**：禁复用 `10927bd9`+`178e90e9`+`c1b71e64`+旧票；禁触 A18；`0087c928`/叶28/29 另队；禁 `--force`；禁 Book-Smoke。
6. **C6 口径**：≠X2 ACCEPT；leo_notify=false；live=false；ok_requested=false（本审不代申；是否新签由主裁）。

## 4. 轻量 compile / 门控结果（本机）

| 调用 | 结果 |
|---|---|
| `python3 -m py_compile` VTRUE py | **PASS** |
| `--dry-compile-only` | **PASS** rc=**0**；`executed_probe=false`；formal=`25ae4572`；skel=`c2f2ca94`；leaf33=`afbbe7e7` |
| 无 `--allow-real-data`（非 dry） | **STOP** rc=**3** |
| `--allow-real-data` 缺/空 `.ok`（有 `--out`） | **STOP** rc=**4** |
| `--allow-real-data` + VOID `.ok` `10927bd9` | **STOP** rc=**5**（forbid） |
| `--force` | **STOP** rc=**9** |
| `--rss-limit-mb 2000` | **STOP** rc=**9**（禁抬） |
| `--allow-real-data` 真跑（持新 `.ok`） | **本拍未执行**（EXECUTED_PROBE 保持 false） |

## 5. 禁项 / 本回合非动作

- **未签**任何 `.ok`（含探针新签 / RESTORED `10927bd9`+旧票）
- **未挂** QUIET；live QUIET **ABSENT**
- **未** `--allow-real-data` 真跑（仅验证 STOP 门）；**未**复跑 X2
- **未改**正式脚本（仍 **`25ae4572`**）；**未改**骨架（仍 **`c2f2ca94`**）；**未改** VTRUE 探针字节（仍 **`2c2226e0`**）
- **未改** PIN `dd17044a` / VOID `dfafff28` / AI DRAFT·COVER·CMD·RECEIPT·pending
- **未** RESTORED `10927bd9`+`178e90e9`+`c1b71e64`+旧票
- **未**抬 rss；**未**触 A18；**未开**叶36；**未改**叶33 `afbbe7e7`
- **≠X2 ACCEPT** / ≠selfcheck / ≠Book-Smoke
- **未** SendToUser / **未**报 Leo（leo_notify=false）

## 6. 硬钉下一跳

```
VTRUE 探针只审 PASS_WITH_CONDITIONS（本回执）
  → 请主裁：是否新签只读探针 .ok（钉 2c2226e0；禁 RESTORED 10927bd9；rss=1500；peak_proof；禁改 25ae4572）
      → 若 YES：Arch 新签探针窗 → AI 持新 .ok 真跑 → per-rebal JSON/tsv 填空
          → 主裁是否开 Option B 补丁 DRAFT（对照 PIN §1.3）
      → 若 NO / HOLD：保持 EXECUTED_PROBE=false；不解阻 X2；≠叶36
```

**本拍不签 / 不挂 / 不代跑 / 不改 `25ae4572` / 不复跑 X2**。

## 7. 结论

| 项 | 值 |
|---|---|
| VERDICT | **PASS_WITH_CONDITIONS** |
| VTRUE py / DRAFT / COVER / CMD / RECEIPT / pending | **`2c2226e0`** / **`b7b9c61d`** / **`554bc027`** / **`cd0c6c56`** / **`fefbfa7d`** / **`1f17fee8`** MATCH |
| Arch recon 上游 / 骨架 / 正式 | **`cb3ca975`** / **`c2f2ca94` UNCHANGED** / **`25ae4572` UNCHANGED** |
| VOID / ok VOID / QUIET lift | **`dfafff28`** / **`10927bd9`** / **`f50975e4`** MATCH |
| PIN / COUNT / COUNT script / 叶33 | **`dd17044a`** / **`a17b75fb`** / **`4e964d40`** / **`afbbe7e7` UNCHANGED** |
| Arch C2 / PIN§1.3·COUNT 列 / VOID-STOP / 缺.ok-STOP | **PASS** / **PASS** / **rc=5** / **rc=4** |
| py_compile / dry / 无 allow / allow 真跑 | **PASS** / **PASS** rc=0 / **STOP** rc=3 / **本拍未跑** |
| EXECUTED_PROBE | **false** |
| 请主裁新签只读探针 `.ok`？ | **请主裁**（Arch 推荐 YES 路径；本拍不代签；禁 RESTORED `10927bd9`） |
| live `.ok` / QUIET | **0** / **ABSENT** |
| live | **false** |
| ≠X2 ACCEPT | **true** |
| leo_notify | **false** |

## 8. 本回执钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/audit/ARCH_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_MAPPING_RECON_PROBE_VTRUE_REVIEW_20261027_ZH.md` |
| VERDICT | **PASS_WITH_CONDITIONS** |
| 上游钉 | VTRUE/`2c2226e0` · DRAFT/`b7b9c61d` · COVER/`554bc027` · CMD/`cd0c6c56` · RECEIPT/`fefbfa7d` · pending/`1f17fee8` · recon审/`cb3ca975` · skel/`c2f2ca94` · formal/`25ae4572` · PIN/`dd17044a` · VOID/`dfafff28` |

**EXECUTED=false** · **EXECUTED_PROBE=false** · **leo_notify=false** · **live=false** · **ok_requested=false** · **≠X2 ACCEPT**
