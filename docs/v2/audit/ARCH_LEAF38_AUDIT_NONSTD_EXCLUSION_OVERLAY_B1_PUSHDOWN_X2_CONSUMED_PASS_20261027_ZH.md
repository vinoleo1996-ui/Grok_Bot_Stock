# Arch 叶38 Audit Nonstd Exclusion Overlay HILIQ×x2 · B1_PUSHDOWN · CONSUMED_PASS

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-27T22:34:32-04:00`（America/New_York） |
| 主令 | 主 ~22:30 ET · 叶38 B1_PUSHDOWN X2 CONSUME GO（主盘证 MATCH：RECEIPT `5e68af78`；`.ok` `794f6578` / 脚本 `3a44471d`；rc=0；peak≈967.7≤1500；mask `1d3d0d88` / meta `81068e47` / overlap `7d224a42`；leaf36 `1913e011`/`72ab602b` n=5745；hard_jaccard=false；median=48） |
| 结论 | **CONSUMED_PASS**（rc=**0**；exclusion_mask **PRESENT**；`hard_reject_jaccard=false`；thickness median=**48.0** PASS；peak_rss_mb=**967.7**≤1500；rss 未抬；无 Exit94/95；QUIET **ABSENT** 无需 lift） |
| live / ≠X2 ACCEPT / ≠Book-Smoke / ≠fund 混线 | **false** / **true** / **true** / **true** |
| leo_notify | **false** |

## 0. 一句话

叶38 B1_PUSHDOWN（脚本 `3a44471d` only；审 `1b98470f` / LAND `37f55893` / VOID `167996dd`）X2 PRIMARY DONE（rc=0；mask `1d3d0d88`；meta `81068e47`；overlap `7d224a42`；hard_reject_jaccard=**false**；median=**48**；peak≈**967.7**≤1500）已 **CONSUME**：live `.ok` **`794f6578`** 归档至 `_consumed/`（内容字节不变；pre/post sha 同）；QUIET **ABSENT**（本窗禁挂；无需 lift；**未新建**）。脚本 **`3a44471d` UNCHANGED**；禁 RESTORED `62acf9fc`+`57ab9096`+`b5be1164`+`4096d401`+…；**未**代改脚本；**未**代跑；**未**新签；**未**改产物/mask/meta/overlap；**未**碰 fund BS `.ok` `f08ce32c`。**仍 ≠X2 ACCEPT**；下一跳交主。

## 1. 核盘 MATCH

| 件 | sha8 / 值 | 结果 |
|---|---|---|
| AI RUN_RECEIPT | `5e68af78` = `5e68af78acf7bbc315495d8238569bff0d5fa8453e1848b0385a18d1a30c5ad5` | **MATCH** · DONE rc=**0** |
| `.ok`（消费前 live） | `794f6578` = `794f6578c26e2e8bf77fbc5528d1d11f1fe4388a575629108d8fee07c1233974` | **MATCH** → 归档（内容字节不变） |
| SIGNED | `e6e30511` = `e6e30511f571c0d31bddc8cb41376f007322d03cfd7144365fb13cb22db2939f` | **MATCH** |
| 脚本 B1_PUSHDOWN | `3a44471d` = `3a44471d263fb2709db80145da33a1a155ea8f300afe5ba4e75089488a9a9027` | **MATCH · UNCHANGED · only** |
| 脚本审（pushdown） | `1b98470f` = `1b98470f2006d14099becc84bed67d62a01cb1ee27effe0330d1e195fcc47968` | **MATCH** |
| LAND pushdown | `37f55893` = `37f5589324e4947ffe9970efe489699b5853b148876ddd9298dfa8262e40ae9f` | **MATCH** |
| VOID ABORT_EXIT95 | `167996dd` = `167996dd66ae0637da17da44503b6ae1f0a0093f806fb9fd4785ee9a2e4c1895` | **MATCH**（禁复活） |
| mask | `1d3d0d88` = `1d3d0d88e367c4348c3f2bb88a11c06dcd798ba7fccaa63c7ba185287f92eaa8` | **MATCH** · PRESENT |
| run_meta | `81068e47` = `81068e479916420551f346568dfd82425ba8943b865a0c2dc372b54066b61e25` | **MATCH** |
| overlap disclose | `7d224a42` = `7d224a4243adaec4c5131e06a2372fd2d76b70fb7e1d69cd972630c417010868` | **MATCH** · hard_reject=**false** |
| leaf36 staging jsonl / pairs.npy | `1913e011` / `72ab602b`；n_pairs=**5745** | **MATCH**（RECEIPT+staging_meta） |
| OUT / 内层 run / rc / pgrep | `20261027_222656` / `20261027_222658` / **0** / 空 | **MATCH** |
| QUIET | **ABSENT**（`output/loop/RESEARCH_QUIET.lock` 不存在） | **MATCH** · 无需 lift · **未新建** |
| Exit94/95 / Traceback / ABORT_PEAK | **无**（本窗 DONE） | **MATCH** |
| x2_accept / live / leo_notify / fund 混线 | false / false / false / 未碰 `f08ce32c` | **MATCH** |

## 2. peak_proof / thickness / overlap

| 项 | 值 |
|---|---|
| peak_rss_mb（run_meta / peak_proof） | **967.67578125**（≈967.7） |
| peak_kb @ after_mask_expand→final | **990900** |
| soft / split / c4 / hard | **1536000** / **1131520** / **1331200** / **1536000** |
| vs soft/hard / rss_limit_mb | peak **≪** soft/hard；rss_limit_mb=**1500**（**未抬**）；peak_proof_le_1500=**true** |
| Exit 94/95 / ABORT_PEAK | **无** |
| thickness median / frac_ge10 / zero_frac | **48.0** / **1.0** / **0.0** · pass_thickness=**true** |
| `hard_reject_jaccard` | **false** |
| jaccard hard（negevent / leaf36）max | **0.0** / **≈0.0649** |
| disclose leaf34/35/37 max | ≈0.0177 / ≈0.0088 / ≈0.0546 |
| PRIMARY | HILIQ · mask-only · B1_PUSHDOWN · ≠X2 ACCEPT |

## 3. 归档 / QUIET

| 项 | 值 |
|---|---|
| `.ok` 归档 | `output/ai_factory/_consumed/ARCH_RUN_AUTH_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_B1_PUSHDOWN_X2_HILIQ.794f6578.CONSUMED_PASS.20261027T2234ET.ok` |
| `.ok` 内容 sha8 / 全长 | **`794f6578`** / `794f6578c26e2e8bf77fbc5528d1d11f1fe4388a575629108d8fee07c1233974`（pre=post；内容字节不变；**禁 RESTORED**） |
| QUIET | **ABSENT** → 记录无需 lift；**未新建 QUIET**；未触 `_lifted/` |
| live `.ok` | **ABSENT**（`ARCH_RUN_AUTH_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_B1_PUSHDOWN_X2_HILIQ.ok` 空） |
| live QUIET | **ABSENT** |
| fund BS `.ok` | **`f08ce32c` UNTOUCHED**（旁线；禁混） |

## 4. 硬钉

- 本票叶38 Audit Nonstd Exclusion Overlay X2 PRIMARY（HI_LIQ **mask-only**；**B1_PUSHDOWN**）alpha 构建收口；**仍 ≠X2 ACCEPT**；**≠Book-Smoke**；本拍**不解阻 ACCEPT**；KEEP **不解阻**
- PRIMARY 纪律：HI_LIQ mask-only；脚本 **`3a44471d` only**；PIN / 产物未改
- 禁复跑本票；禁抬帽（rss=1500）；禁代跑；禁代改脚本/mask/产物；禁新签
- 禁 RESTORED：本票内容 **`794f6578`** + 旧票 `62acf9fc`+`57ab9096`+`b5be1164`+`4096d401`+…；禁把 VOID `167996dd`/`62acf9fc` 复活
- **禁混 fund**：`ARCH_RUN_AUTH_FUND_PORTFOLIO_WHO_PAYS_BOOK_SMOKE_DARK_HORSE_ADD.ok` **`f08ce32c`** 旁线未开/未改
- **下一跳交主决策**（是否 Alpha 组合接线 / selfcheck 另票 / HOLD）——**Arch 不自决 ACCEPT、不自派 selfcheck、不自派下一叶**
- **不报 Leo**（leo_notify=false）

## 5. 下一跳（听主）

```
CONSUMED_PASS（本回执）
  → 请主裁：Alpha/组合接线 或 selfcheck 另票 或 HOLD
      → Arch 不自派；≠X2 ACCEPT；禁混 fund BS；禁 RESTORED 794f6578+62acf9fc+57ab9096+b5be1164+4096d401+旧票
```

live=false。
