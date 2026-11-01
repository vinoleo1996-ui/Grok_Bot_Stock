# Arch 叶35 Mapping Recon VTRUE 只读探针 · CONSUMED_PASS

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-27T14:49:51-04:00`（America/New_York） |
| 主令 | 主 ~14:46 ET · 叶35 VTRUE 探针 CONSUME GO（AI DONE MATCH：RUN `107a72b1` / ACK `6dbe12d3` / JSON `446b60d1` / TSV `f1ef19ca`；rc=0；pid `517908` DEAD；ET_TS=`20261027_144200`） |
| 结论 | **CONSUMED_PASS**（诊断真跑成功填数；rc=**0**；peak **512264**≪1500；**证实** X2 `STOP_ZERO_MASK_ROWS` 根因=份额 PIT/`available_at` 晚于 15:00 SH） |
| live / ≠X2 ACCEPT / ≠正式 α / ≠叶36 / ≠Book-Smoke | **false** / **true** / **true** / **true** / **true** |
| leo_notify | **false** |

## 0. 一句话

VTRUE 只读探针 DONE（rc=0；n_rebal=**30**；空压 **30/30=`share_avail_late`**；主因 **A**；B 非主因；peak=**512264**≪1500；OUT 仅 diag JSON/TSV/stdout/stderr；**无** alpha/mask/overlap）已 **CONSUME**：live `.ok` **`00eec671`** 归档至 `_consumed/`（结论名 **CONSUMED_PASS**；内容字节不变）；QUIET **`bf3470cb`**（holder=`leaf35_MAPPING_RECON_VTRUE_PROBE`）已 lift。正式脚本 **`25ae4572` UNCHANGED**；骨架 **`c2f2ca94` UNCHANGED**；叶33 **`afbbe7e7` UNCHANGED**；禁 RESTORED `00eec671`+`10927bd9`+旧票；**未**代改正式脚本；**未**复跑 X2；**未**新签。**≠X2 ACCEPT**。

## 1. 核盘 MATCH

| 件 | sha8 / 值 | 结果 |
|---|---|---|
| AI RUN_RECEIPT | `107a72b1` = `107a72b1987d912d45bd490cf4d483711d49cd3e25e06723bc35c42379588c81` | **MATCH** · EXECUTED_PROBE_DONE rc=**0** |
| RUNNING_ACK | `6dbe12d3` = `6dbe12d316b25e3516e0d1d846251daaf75b63313ef8f250592aec333bb44727` | **MATCH** |
| per-rebal JSON | `446b60d1`（`output/ai_factory/_leaf35_mapping_recon_vtrue/20261027_144200/mapping_recon_vtrue_per_rebal.json`） | **MATCH** |
| per-rebal TSV | `f1ef19ca` | **MATCH** |
| OUT 目录 | `output/ai_factory/_leaf35_mapping_recon_vtrue/20261027_144200/`（仅 json/tsv/stdout/stderr；**无** alpha/mask/overlap） | **MATCH** |
| `.ok`（消费前 live） | `00eec671` = `00eec671fc904ac745752070fd4b84b8939715d350d5b089dd5de09b6c19b291` | **MATCH** → 归档（内容字节不变） |
| QUIET（lift 前 live） | `bf3470cb` = `bf3470cba95c5a487c37981099d016b07bf5dcb970b8384a716752b1f28ac402`；holder=`leaf35_MAPPING_RECON_VTRUE_PROBE` | **MATCH** → lift |
| SIGNED | `97a84fa7` = `97a84fa7d34dfa16e8150399a689ef271280ee067b1c3678dce5fd5e884eaa4c` | **MATCH** |
| VTRUE 审 | `bbbf809b` PASS_WITH_CONDITIONS | **MATCH** |
| recon 审 | `cb3ca975` PASS_WITH_CONDITIONS · Option A | **MATCH** |
| 探针脚本 | `2c2226e0` = `2c2226e00a232ad1caf61f9d456990e5b7abe2c0040976371d0036f5480cca67` | **MATCH · UNCHANGED** |
| 骨架探针 | `c2f2ca94` | **MATCH · UNCHANGED** |
| 正式脚本 | `25ae4572` = `25ae45723454423a31d4b0c6987c5eb0a2e8bb733c2506c2db67d628e91b4ad0` | **MATCH · UNCHANGED** |
| 叶33 正式 | `afbbe7e7` | **MATCH · UNCHANGED** |
| PIN C3 / VOID | `dd17044a` / `dfafff28`（ok VOID `10927bd9`） | **MATCH** |
| DRAFT/COVER/CMD/RECEIPT/pending | `b7b9c61d` / `554bc027` / `cd0c6c56` / `fefbfa7d` / `1f17fee8` | **MATCH**（上游） |
| ET_TS / pid / rc / peak_kb | `20261027_144200` / `517908`（**DEAD**；pgrep 空） / **0** / **512264** | **MATCH** |
| Exit94/95 / Traceback | **无** | **MATCH** |
| EXECUTED_PROBE | **true** | **MATCH** |
| x2_accept / leaf36 / live / leo_notify | false / false / false / false | **MATCH** |

## 2. 诊断核验（主因 A · 份额 PIT / `available_at`）

| 核验项 | 值 | 判读 |
|---|---|---|
| n_rebal | **30** | JSON `rows` 长度 MATCH |
| `empty_reason` 分布 | **`share_avail_late` × 30/30（100%）** | **主因 A 证实** |
| `n_share_rows` | **3**（全 rebal 同） | 同日份额行存在 |
| `n_share_rows_avail_le_tts` | **0**（全 rebal 同） | 全部 `available_at_clock` **>** t_ts(15:00 SH) |
| `n_share_rows_count_approx_style` | **3**（全 rebal 同） | COUNT 风格同日行=3（未滤 available_at） |
| `n_share_rows_pin13_avail_only` | **4695–6405**（随 rebal 升） | PIN§1.3 仅 `available_at≤t_ts`（不限 trade_date==rebal）仍有大量行 → 与正式窄口径张力 |
| `n_weight_rows_schemeA` | **1800**（全 rebal 同） | **B 非主因**（权重方案 A 行充足） |
| `n_mapped` / `n_pressure_nonnull` / `n_hiliq_intersect` | **0 / 0 / 0** | 空压直接后果；解释 X2 `STOP_ZERO_MASK_ROWS` |
| `empty_reason_detail` | `same-day share rows exist but all available_at_clock > t_ts(15:00)` | 与主称一致 |
| peak_kb / rss | **512264** / 1500MB 软顶 **未抬**；无 Exit94/95 | 资源 OK |

**根因结论（诊断成功）**：正式脚本份额 PIT 口径（`trade_date==rebal ∧ available_at≤15:00`）在 X2 窗 30 个 rebal 上 **零行可用**（虽同日 `n_share_rows=3`），故 pressure 空 → mask 零行 → X2 `STOP_ZERO_MASK_ROWS`。COUNT 近似与 PIN§1.3 avail-only 对照列证实缺口在 **available_at 时点/口径**，不在权重方案 A、不在 top_q。

## 3. 归档 / lift

| 项 | 值 |
|---|---|
| `.ok` 归档 | `output/ai_factory/_consumed/ARCH_RUN_AUTH_LEAF35_MAPPING_RECON_VTRUE_PROBE.00eec671.CONSUMED_PASS.20261027T1449ET.ok` |
| `.ok` 内容 sha8 / 全长 | **`00eec671`** / `00eec671fc904ac745752070fd4b84b8939715d350d5b089dd5de09b6c19b291`（内容字节不变；**禁 RESTORED**） |
| QUIET lift | `output/loop/_lifted/RESEARCH_QUIET_leaf35_mapping_recon_vtrue_probe_CONSUMED_PASS_LIFTED_20261027T1449ET.lock` |
| QUIET 原内容 sha8 / 全长 | **`bf3470cb`** / `bf3470cba95c5a487c37981099d016b07bf5dcb970b8384a716752b1f28ac402`（可追溯） |
| lift 文件 sha8 / 全长 | **`9306ceff`** / `9306ceffba28eca00ac9f61b7a393e43a9f3b989b3105004e6898d2c34b30ea5`（尾加 `# ARCH_QUIET_LIFTED`；lifted_by=arch / CONSUMED_PASS / consumed_ok_sha8=00eec671 / do_not_restore=true） |
| live `.ok` | **ABSENT**（`ARCH_RUN_AUTH_LEAF35_MAPPING_RECON_VTRUE_PROBE*` 空） |
| live QUIET | **ABSENT**（`output/loop/RESEARCH_QUIET.lock` 不存在） |

## 4. Option 审意见（交主 · Arch 不自决）

### Option B（endorse · 建议）

**建议主令 AI 开补丁 DRAFT**：对齐正式脚本份额 PIT 口径与 COUNT/数据现实——候选方向包括但不限于：(1) 放宽到 PIN§1.3 `available_at≤t_ts`（不强制 `trade_date==rebal`）；(2) 改用 T+1 可用份额；(3) 映射层修正 `available_at` 时点。**须**另票只审 → 新签窗；**禁**本拍代改 `25ae4572`；**禁** RESTORED `00eec671`+`10927bd9`+`178e90e9`+`c1b71e64`+旧票；**禁**复跑 X2；**≠X2 ACCEPT**；≠叶36。

### Option C（并列合法）

若主**不**修口径，则叶35 X2 维持 **HOLD CLOSED**（VOID `dfafff28` / `.ok` `10927bd9`）合法；不强制开补丁。

## 5. 硬约束（本拍与下一跳默认）

- 正式脚本 **`25ae4572` UNCHANGED**（本拍未改；下一跳若需改须另窗只审+新签）
- 骨架 **`c2f2ca94` UNCHANGED**；叶33 **`afbbe7e7` UNCHANGED**
- 禁 RESTORED：本票内容 **`00eec671`** + `10927bd9`+`178e90e9`+`c1b71e64`+`245df63f`+`c5ed13df`+`5774bb6e`+`81521fb5`+旧票
- **≠X2 ACCEPT**；≠叶36；≠Book-Smoke；≠selfcheck
- 禁复跑 X2；禁新签本拍；禁触 A18
- `leo_notify=false`；`live=false`

## 6. 非动作（本拍）

- **未**代跑探针 / 正式 α / X2
- **未**改探针 `2c2226e0` / 正式 `25ae4572` / 骨架 `c2f2ca94` / 叶33 `afbbe7e7`
- **未**写 alpha/mask/overlap
- **未** RESTORED 任何禁票（含 `00eec671`/`10927bd9`/`178e90e9`/`c1b71e64`）
- **未**签新 `.ok`
- **未** SendToUser / 不报 Leo

## 7. 钉表（速查）

| 钉 | sha8 |
|---|---|
| RUN_RECEIPT | `107a72b1` |
| RUNNING_ACK | `6dbe12d3` |
| per-rebal JSON | `446b60d1` |
| per-rebal TSV | `f1ef19ca` |
| `.ok` 内容（归档） | `00eec671` |
| QUIET 原内容 | `bf3470cb` |
| QUIET lift 文件 | `9306ceff` |
| SIGNED | `97a84fa7` |
| VTRUE 审 | `bbbf809b` |
| recon 审 | `cb3ca975` |
| 探针脚本 | `2c2226e0` |
| 骨架 | `c2f2ca94` |
| 正式脚本 | `25ae4572` |
| 叶33 | `afbbe7e7` |
| PIN / VOID | `dd17044a` / `dfafff28` |

---
*Arch · 叶35 VTRUE CONSUMED_PASS · 2026-10-27T14:49:51-04:00 · leo_notify=false · live=false · ≠X2 ACCEPT*
