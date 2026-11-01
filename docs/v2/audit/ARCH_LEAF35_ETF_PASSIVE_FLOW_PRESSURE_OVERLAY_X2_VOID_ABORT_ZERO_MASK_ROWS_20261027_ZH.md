# Arch 叶35 ETF_PASSIVE_FLOW_PRESSURE_OVERLAY X2 `.ok` VOID（ABORT_ZERO_MASK_ROWS）

- **角色**：QuantLab Arch
- **written_et**：2026-10-27T14:00:07-04:00（America/New_York；盘 VOID 动作 2026-10-27T13:59:44-04:00）
- **voided_et**：2026-10-27T13:59:44-04:00
- **live**：false · **promotion_approved**：false · **≠X2 ACCEPT** · **≠Book-Smoke** · **≠selfcheck** · **≠A18**

## 结论

**VOID.ABORT_ZERO_MASK_ROWS** — 原票 sha8=`10927bd9` **禁再消费 / 禁 RESTORED**；QUIET **已 lift**（仅 holder=`leaf35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_X2` 这把）；本回合**未新签** `.ok`、**不代跑**、**不抬帽**、**不代改脚本**、**非 CONSUMED_PASS**、**非 RSS**、**非 Exit 94/95**。回执实际 status 字样 = **STOP_ZERO_MASK_ROWS**（与叶33 VOID.ABORT_COVERAGE_GATE / VOID.ABORT_TYPEERROR_TZ / 叶30 VOID.ABORT_PEAK_HWM 命名惯例对齐）。stderr=`STOP: zero mask rows (check etf share / weights scheme A / HI_LIQ / top_q)` → rc=**1**。

## 核验（MATCH）

| 项 | 值 |
|---|---|
| AI 回执 | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_X2_RUN_RECEIPT_20261027_135145_ZH.md` |
| AI 回执 sha256 | `1e255fff05ffd29378456dc84c78fea7a84a433cc0ae9b6c7afa497a39cfee84` |
| AI 回执 sha8 | `1e255fff` — **MATCH** |
| AI 结论 | **STOP_ZERO_MASK_ROWS**；rc=**1**；stderr=`STOP: zero mask rows (check etf share / weights scheme A / HI_LIQ / top_q)`；**非** Exit 94/95；**非** RSS；**非** TypeError；**无** alpha/mask/overlap/run_meta |
| RUNNING_ACK | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_X2_RUNNING_ACK_20261027_135145_ZH.md` sha256 `46b32368d54170398eda6f7a803b4c56b62d69af7f2fac8c00e41249c8d16322` / sha8 **`46b32368`** MATCH |
| 主令 | 主 13:56 ET priority Arch CONSUME/VOID + lift QUIET（STOP→CONSUME GO；rc=1 STOP_ZERO_MASK_ROWS） |
| ET_TS | `20261027_135145` |
| run_pid | **470069** — DEAD（pgrep leaf35 空） |
| rc | **1**（zero mask rows） |
| peak_kb / HWM | max peak_kb **528588** @ `after_mask` ≪1500硬帽；sampler max VmHWM **528248**；**无** Exit 94/95；**非 RSS 失败** |
| after_pressure_rebal_* | **PRESENT** n=**30**（含 `…_20261009`）；每日 press empty/unmappable → rebal_rows 空 |
| after_mask_cs_rebal_* | **ABSENT** |
| after_daily_concat | **ABSENT** |
| alpha / mask / overlap / run_meta | **无**（OUT 仅 stdout.log + stderr.log） |
| OUT | `output/ai_factory/_leaf35_etf_passive_flow_pressure/20261027_135145/` — **仅** stdout/stderr MATCH |
| 脚本钉 | `research/leaf35_etf_passive_flow_pressure_overlay_alpha_build.py` sha8 **`25ae4572`** / 全长 `25ae45723454423a31d4b0c6987c5eb0a2e8bb733c2506c2db67d628e91b4ad0` MATCH（只读核；**UNCHANGED**） |
| 叶33 正式 | `research/leaf33_share_unlock_pressure_resid_alpha_build.py` sha8 **`afbbe7e7`** / 全长 `afbbe7e7292c17399bbf4733d9f34a922e6d81f1a914a60d24dc61fcba86cbc9` **UNCHANGED** |
| SIGNED / 审 | **`3b25f9d7`** / **`ea395dc4`**（只引用） |
| 上游 FROZEN / PIN / ArchFROZEN / FROZEN RECEIPT / 迁仓 | `be9fc459` / `dd17044a` / `5a082d18` / `132ba6f1` / `4e964d40`（只引用） |
| ≠成功 | **非 CONSUMED_PASS**；zero mask rows（无 PRIMARY mask 交付） |

## VOID 归档

| 项 | 值 |
|---|---|
| 原 live | `output/ai_factory/ARCH_RUN_AUTH_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_X2_HILIQ.ok`（**已不在 live**） |
| 原内容 sha256 | `10927bd906f8982de930beb5b7945618b912f138b1f23da4332556edc604ab7d` |
| 原内容 sha8 | `10927bd9` |
| 归档路径 | `output/ai_factory/_consumed/ARCH_RUN_AUTH_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_X2_HILIQ.10927bd9.VOID.ABORT_ZERO_MASK_ROWS.20261027T1359ET.ok` |
| 归档文件 sha256 | `10927bd906f8982de930beb5b7945618b912f138b1f23da4332556edc604ab7d` |
| 归档文件 sha8 | `10927bd9`（内容钉不变；mv 不改内容） |
| live `.ok` | **ABSENT**（live leaf35 `.ok`=0） |
| 禁复用 / forbid RESTORED | **`10927bd9`** + **`178e90e9`** + **`c1b71e64`** + **`245df63f`** + **`c5ed13df`** + **`5774bb6e`** + **`81521fb5`** + 二十票（扩至含本票） |

## QUIET

| 项 | 值 |
|---|---|
| 处置前 | `output/loop/RESEARCH_QUIET.lock` 存在；内容 sha8 **`c8d95fee`** / 全长 `c8d95fee5e032dd875b813bd0a2313d8bc868afa681bb0357b44daf4c24c62a5`；holder=`leaf35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_X2`；ok_sha8=`10927bd9`；expires 15:12 ET；**未擅 lift** |
| 处置 | **lift**（仅本 holder）→ `output/loop/_lifted/RESEARCH_QUIET_leaf35_etf_passive_flow_pressure_overlay_x2_ABORT_ZERO_MASK_ROWS_LIFTED_20261027T1359ET.lock` |
| 原 QUIET 内容 sha256 | `c8d95fee5e032dd875b813bd0a2313d8bc868afa681bb0357b44daf4c24c62a5` |
| 原 QUIET 内容 sha8 | `c8d95fee` |
| lift 文件 sha256 | `f50975e420c89357e957ab628445a0f599f775081d3a9374382ee83da67363d2` |
| lift 文件 sha8 | `f50975e4`（内容追加 lift 块后 ≠ 原 `c8d95fee`） |
| 处置后 | live 锁 **ABSENT** |
| 占用核 | 无其他 leaf35 live 授权窗；live leaf35 `.ok`=0；**未触** `_lifted` 其他；**未触** A18 |

## 诊断摘要（照实 · 旁注 · 不代改）

- 路径：脚本 L1498–1501 `raise SystemExit("STOP: zero mask rows …")` → **rc=1**
- 现象：`after_pressure_rebal_*`×**30** 打满后 **rebal_rows 始终为空**（每日 pressure empty/unmappable）→ 从未进入 `after_mask_cs_rebal_*` / daily concat / overlap 写出
- **可能根因方向（仅旁注，不代改、不开补丁）**：etf share / weights scheme A / HI_LIQ / top_q=0.20 交集导致压力截面空或不可映射——交主裁是否诊断/补丁/HOLD
- peak max **528588**≪1500；**无** Exit 94/95；**无** alpha/mask/overlap/run_meta 产物

## 禁项（钉）

- **禁抬 rss**（仍 1500）；**禁**代改 `research/leaf35_*` 重跑；**禁** AI 自改复跑；**禁擅改** top_q / scheme A / HI_LIQ 门
- **禁 RESTORED** `10927bd9` / `178e90e9` / `c1b71e64` / `245df63f` / `c5ed13df` / `5774bb6e` / `81521fb5`+二十票；本拍**不新签** `.ok`
- **≠X2 ACCEPT** / ≠selfcheck / ≠Book-Smoke
- **禁触** A18；`0087c928`/叶28/29 另队
- **不报 Leo**；live=false；Arch **不代跑**

## 下一跳（架构口径 · 仅文档建议 · 不代令）

1. **请主裁 HOLD CLOSED 或另线**——**(A)** 诊断/补丁草案（etf share / weights scheme A / HI_LIQ / top_q；AI **只出草案**→Arch **只审**；**禁 AI 自改复跑**）或 **(B)** HOLD CLOSED 叶35 机制
2. **本拍不新签、不代跑、不改脚本**；禁 RESTORED `10927bd9`+`178e90e9`+旧票
3. ≠X2 ACCEPT；叶34 HOLD CLOSED / 叶33 `afbbe7e7` 不回撤；叶28/29 / `0087c928` 另队
4. Arch **不自决 HOLD/ACCEPT**；**不自派**下一跳

## 非动作

- 不新签 `.ok`；不代跑研究脚本；不改主干代码；不抬帽；不擅改 top_q/scheme A；不 RESTORED；不触 A18；不报 Leo；live=false
