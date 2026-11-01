# Arch 叶35 ETF Passive Flow Pressure Overlay HILIQ×x2 · B1 份额 PIT · CONSUMED_PASS

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-27T15:36:52-04:00`（America/New_York） |
| 主令 | 主 ~15:32–15:35 ET · 叶35 B1 X2 CONSUME GO（AI DONE MATCH：RUN `e75c090b` / ACK `474320ee` / mask `576ca398` / overlap `54933299` / run_meta `2bb21a76`；rc=0；pid `561293` DEAD；ET_TS=`20261027_152756`） |
| 结论 | **CONSUMED_PASS**（rc=**0**；exclusion_mask **PRESENT**；overlap `any_jaccard_hard_reject=False`；coverage_median=**1552.5**≥300 PASS；peak max **714280**≪1500；无 Exit94/95） |
| live / ≠X2 ACCEPT / ≠Book-Smoke / ≠selfcheck / ≠叶36 | **false** / **true** / **true** / **true** / **true** |
| leo_notify | **false** |

## 0. 一句话

叶35 B1（份额 PIT 对齐 PIN §1.3）X2 PRIMARY DONE（rc=0；mask `576ca398`；overlap hard_reject=**False**；pin_gap=**False**；coverage_median=**1552.5** PASS；peak=**714280**≪1500）已 **CONSUME**：live `.ok` **`eb70eef4`** 归档至 `_consumed/`（内容字节不变）；QUIET **`ef9b69b4`**（holder=`leaf35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_X2`）已 lift。脚本 **`434ff42c` UNCHANGED**；叶33 **`afbbe7e7` UNCHANGED**；禁 RESTORED `eb70eef4`+`00eec671`+`10927bd9`+旧票；**未**代改脚本；**未**代跑；**未**新签。**仍 ≠X2 ACCEPT**；Alpha/selfcheck **另票听主**（Arch 不自派）；禁 Book-Smoke；≠叶36。

## 1. 核盘 MATCH

| 件 | sha8 / 值 | 结果 |
|---|---|---|
| AI RUN_RECEIPT | `e75c090b` = `e75c090b7bdf08f7c95d39566dfe1a96669bbf69e2e880250a966ee6cfe23829` | **MATCH** · DONE rc=**0** |
| RUNNING_ACK | `474320ee` = `474320ee312015cb44252c490fece778530c1312eee7ce7078e2ddb47ef72893` | **MATCH** |
| `.ok`（消费前 live） | `eb70eef4` = `eb70eef4386ae856f5f0b02733bca718ff96125765556fd72b70fefc82f94921` | **MATCH** → 归档（内容字节不变） |
| QUIET（lift 前 live） | `ef9b69b4` = `ef9b69b486edb3ec8d679b7aae22d5d21e33cedff85db5cdfea331dfc80bac3b`；holder=`leaf35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_X2` | **MATCH** → lift |
| SIGNED | `65d89851` | **MATCH** |
| 脚本审 / 补丁审 | `df19dd2a` PASS_WC / `31a08790` PASS_WC endorse B1 | **MATCH** |
| 脚本 | `434ff42c` = `434ff42c1ba7998e122e0ded4f984c98d40ecbfc12f124afe7ef99742bd69b0a` | **MATCH · UNCHANGED** |
| 叶33 | `afbbe7e7` | **MATCH · UNCHANGED** |
| mask | `576ca398` = `576ca398c0327d0ebbe434bada568ffc56bee8800f9a14ea177e2ba549d7e650` | **MATCH** · PRESENT |
| overlap | `54933299` = `54933299df35cb7941888eff3e59b1c08a0079854ef3d209b9d247ca3194e160` | **MATCH** · hard_reject=**False** |
| run_meta | `2bb21a76` = `2bb21a760a8dfb7cfa18787aa118f961138dd937e6da90c7e7b28906e22d6fbc` | **MATCH** |
| ET_TS / pid / rc / pgrep | `20261027_152756` / `561293`（**DEAD**） / **0** / 空 | **MATCH** |
| Exit94/95 / Traceback | **无** | **MATCH** |
| ALPHA_BUILD_EXECUTED（跑后） | **true**（AI DONE；Arch 签时为 false） | **MATCH** |
| x2_accept / leaf36 / live / leo_notify | false / false / false / false | **MATCH** |

## 2. peak_proof / 覆盖 / overlap

| 项 | 值 |
|---|---|
| peak_kb（OK 行 / sampler max VmHWM） | **714280** |
| run_meta `peak_kb` / `peak_kb_final` | **520976** / **520256** |
| RSS_CHECK max（至 after_daily_concat） | **520912** @ `after_daily_concat` |
| rss_limit_mb | **1500**（**未抬**） |
| 相对硬帽 | 714280 / 1536000 ≈ **46.5%**；≪1500MB |
| `after_mask` / `after_weight_pin` / `after_pressure_rebal_*` / `after_mask_cs_rebal_*` / `after_daily_concat` | **PRESENT**（pressure/mask_cs ×30） |
| Exit 94/95 / ABORT_PEAK | **无** |
| coverage_median / gate | **1552.5** / 300 · **PASS**（`coverage_gate_pass=True`） |
| n_pin_gaps / required pin_gap | **0** / **False** |
| `overlap_any_jaccard_hard_reject` | **False** |
| j20 硬拒同伴 max | ≪0.7（leaf25/30≈0.053；moneyflow/31/33=0）；leaf26_like_raw j=1.0 诊断-only **不硬拒** |
| PRIMARY | HILIQ · mask-only · top_q=0.20 · B1 share PIT · C3 方案 A · C11≠叶26 |

## 3. 归档 / lift

| 项 | 值 |
|---|---|
| `.ok` 归档 | `output/ai_factory/_consumed/ARCH_RUN_AUTH_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_X2_HILIQ.eb70eef4.CONSUMED_PASS.20261027T1536ET.ok` |
| `.ok` 内容 sha8 / 全长 | **`eb70eef4`** / `eb70eef4386ae856f5f0b02733bca718ff96125765556fd72b70fefc82f94921`（内容字节不变；**禁 RESTORED**） |
| QUIET lift | `output/loop/_lifted/RESEARCH_QUIET_leaf35_etf_passive_flow_pressure_overlay_x2_b1_CONSUMED_PASS_LIFTED_20261027T1536ET.lock` |
| QUIET 原内容 sha8 / 全长 | **`ef9b69b4`** / `ef9b69b486edb3ec8d679b7aae22d5d21e33cedff85db5cdfea331dfc80bac3b`（可追溯） |
| lift 文件 sha8 / 全长 | **`52a3bc4b`** / `52a3bc4bf378a77f3ef55d0a65379d208634aade69855eef4a7fb97a69199da4` · 尾加 `# ARCH_QUIET_LIFTED`；lifted_by=arch / CONSUMED_PASS / consumed_ok_sha8=`eb70eef4` / do_not_restore=true |
| live `.ok` | **ABSENT**（`ARCH_RUN_AUTH_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_X2_HILIQ.ok` 空） |
| live QUIET | **ABSENT**（`output/loop/RESEARCH_QUIET.lock` 不存在） |

## 4. 硬钉

- 本票叶35 ETF Passive Flow Pressure Overlay X2 PRIMARY（HI_LIQ **mask-only** top_q=**0.20**；**B1** 份额 PIT）alpha 构建收口；**仍 ≠X2 ACCEPT**；**≠Book-Smoke**；**≠selfcheck**；**≠叶36**；本拍**不解阻 ACCEPT**；KEEP **不解阻**
- PRIMARY 纪律：HI_LIQ mask-only；禁静默 FULLA PRIMARY；soft-penalty 非 PRIMARY；C3 方案 A；份额 PIT B1=`available_at≤t_ts` asof；PIN **`dd17044a`** / FROZEN **`be9fc459`** 未改
- 禁复跑本票；禁抬帽（rss=1500）；禁代跑；禁代改脚本/mask/产物；不触 A18；不审/不夹带 `0087c928`/28/29
- 禁 RESTORED：本票内容 **`eb70eef4`** + `00eec671`+`10927bd9`+`178e90e9`+`c1b71e64`+`81521fb5`+旧票；禁把 `25ae4572` 当活脚本
- 叶33 正式 **`afbbe7e7` UNCHANGED**；叶32 HOLD / 叶34 HOLD CLOSED 不回撤
- **下一跳交主决策**（是否 Alpha 组合接线 / selfcheck 另票 / HOLD）——**Arch 不自决 ACCEPT、不自派 selfcheck**
- **不报 Leo**（leo_notify=false）

## 5. 下一跳（听主）

```
CONSUMED_PASS（本回执）
  → 请主裁：Alpha/组合接线 或 selfcheck 另票 或 HOLD
      → Arch 不自派；≠X2 ACCEPT；≠叶36；禁 Book-Smoke；禁 RESTORED eb70eef4+00eec671+10927bd9+旧票
```

live=false。
