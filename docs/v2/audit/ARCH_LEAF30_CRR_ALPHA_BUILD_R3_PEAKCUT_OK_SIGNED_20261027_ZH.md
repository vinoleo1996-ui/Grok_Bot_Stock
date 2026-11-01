# Arch 叶30 CRR CFOOE vol_pen alpha 构建 R3 peakcut · 独立 X2 `.ok` 签发回执

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-27T00:27:29-04:00`（America/New_York） |
| 主令 | 主 00:24 ET priority · 叶30 R3 独立 X2 签窗 |
| 脚本审 | `d081054e…` **PASS_WITH_CONDITIONS** |
| 提案审 | `61830035…` **APPROVE_A** |
| live / promotion_approved | **false** / **false** |

## 结论

**SIGNED** — 独立叶30 CRR+CFOOE vol_pen HILIQ×x2 **r3_peakcut** alpha 构建（PRIMARY=A：脚本 `leaf30_crr_cfooe_volpen_alpha_build_r3_peakcut.py` → 按 rebal 日懒加载 `logmv_d` + del+gc + `after_logmv_rebal_YYYYMMDD`；废整窗预载；OP×16 季 CRR + λ=1.0 vol_pen + 银地非银掩码 + `qend_ok` 过滤 → `_leaf30_crr/<ET_TS>/`）`.ok` 已落盘；**≠ X2 ACCEPT**；**≠ selfcheck**；**≠ Book-Smoke**；**≠ RESTORED/VOID** 十六票（首项 R2 VOID `5af20222`；次项 leaf30 VOID `5ae077fa`；含叶25构建 `3c297052` / 叶25 selfcheck `ebc673bf` / A18 EXEC `6de02e74` 含已归档）；脚本全长 **`3ee9fed2…`**；脚本审 **`d081054e`**；AI落盘 **`4d951ea3`**；提案审 **`61830035` APPROVE_A**；提案 **`f111671a`**；void_ref `df47501c`；FROZEN `93cad965`；预注册 `f61ffb05`；R2 基盘 **`0a264402` 未改**（禁作新票脚本）；**`qend_ok_filter=true`**；**`primary_load=rebal_day`**；**禁** `--no-overlap-report`；真跑须写并消费 `overlap_vs_leaf19_25.json`（Jaccard≥0.7 硬拒；ρ>0.5 强度叙事；计数抽样≠正式）；rss 软/硬帽 **1500** 禁抬（硬 Exit **94/95**）；peak_proof **REQUIRED**（含 `after_daily_concat` 残峰 + 全序列 `after_logmv_rebal_*`；ru_maxrss/VmHWM/RSS_CHECK）；C2=OP+OCF only；**Arch 不代跑**；**禁盲重跑** r1 `a2cef5af` / R2-as-ticket `0a264402`；**禁触** A18 `.ok` `a62881b9`。QUIET **已挂且保留**供 AI prelaunch（本回合不 lift；≠旧 A18 QUIET）。PRIMARY only；**无同票 FALLBACK**；峰＞1500→Exit 94/95 停+上报（禁抬帽）。ALPHA_BUILD_EXECUTED@签=**false**。叶26 不交审；28/29 FROZEN。**≠A18**（`a62881b9` CONSUMED 未触；未 restore `_lifted`）。

## 钉点 MATCH 表

| 项 | 期望 | 实测 | 结果 |
|---|---|---|---|
| 脚本审 R3 | `d081054e` PASS_WITH_CONDITIONS | `d081054e342ef8fde0d249a338cb75d51c225cf765eda111cb9161bea0709d27` | **MATCH** |
| 脚本 | `3ee9fed2…` | `3ee9fed2c91a8c523128d9a0b0956f29a11fd2935d961e978aa07b9eafb0a182` | **MATCH** |
| AI落盘 | `4d951ea3` | `4d951ea3af8c4b81f21dde70d8679a26a5f8d1a0cd9a941a82bf410f19461a2b` | **MATCH** |
| 提案审 | `61830035` APPROVE_A | `61830035fb732ecc0e2d3277b22cee8ad6dcd0dce21988a685c537755d6f8b92` | **MATCH** |
| 提案 | `f111671a` | `f111671abc41dd954f59aa6945d378462f545522588b461af916697173be83c1` | **MATCH** |
| void_ref R2 | `df47501c` | `df47501c6c9f2b1406e346ed877f4abe754ee8f5981413843af339d9555d3822` | **MATCH** |
| FROZEN | `93cad965` | `93cad965bd9aa34b6bb8dc5e43d6f0095c4d111420c5fa53b196ad4220d40fba` | **MATCH** |
| 预注册 | `f61ffb05` | `f61ffb052192810e908e931032442b6a62381e1ab1ad09fcb0245657893d47b0` | **MATCH** |
| R2 脚本（未改/禁作票） | `0a264402…` | `0a2644021e8bbd16cbe7f69905a6a6dfcd47df3c798b6f5b272f7b6702220260` | **MATCH** |
| r1 脚本（禁改/禁跑） | `a2cef5af…` | `a2cef5affd67f874fad9e37f59efb9d7abacb3de0d0286d8443250aee5253c74` | **MATCH** |
| 拟 .ok 签前 | 不存在 | 不存在 | **MATCH** |
| QUIET 签前 | ABSENT | ABSENT | **MATCH** |
| ai_factory live `.ok` | 0 | 0 | **MATCH** |
| A18 `.ok` a62881b9 | 未触（已 CONSUMED） | 未触 | **MATCH** |
| pgrep leaf30/kline/… | 空 | 空 | **MATCH** |
| 窗期 | ≥90min prelaunch → expires | `2026-10-27T00:26:00-04:00` → `2026-10-27T01:56:00-04:00` / expires `2026-10-27T01:58:00-04:00`；签时 `2026-10-27T00:27:29-04:00` | **IN_WINDOW** |

## 钉

| 项 | 值 |
|---|---|
| `.ok` 路径 | `output/ai_factory/ARCH_RUN_AUTH_LEAF30_CRR_CFOOE_VOLPEN_ALPHA_BUILD_R3_PEAKCUT_HILIQ_X2.ok` |
| `.ok` sha8 / 全长 | `7e239487` / `7e2394879ff83f19c52e36895cbf200bffd9e957817026d2ed4a489b60359991` |
| QUIET 路径 | `output/loop/RESEARCH_QUIET.lock` |
| QUIET sha8 / 全长 | `69ea8560` / `69ea8560ebc88c0f5cd660d5e50823e3ca941820331f94e9f1f066d5af5b8bd0` |
| 脚本 | `research/leaf30_crr_cfooe_volpen_alpha_build_r3_peakcut.py` = `3ee9fed2c91a8c523128d9a0b0956f29a11fd2935d961e978aa07b9eafb0a182` |
| 脚本审 | `d081054e342ef8fde0d249a338cb75d51c225cf765eda111cb9161bea0709d27` PASS_WITH_CONDITIONS |
| AI落盘 | `4d951ea3af8c4b81f21dde70d8679a26a5f8d1a0cd9a941a82bf410f19461a2b` |
| 提案审 / 提案 | `61830035…` APPROVE_A / `f111671a…` |
| void_ref / FROZEN / 预注册 | `df47501c…` / `93cad965…` / `f61ffb05…` |
| 窗期 | `2026-10-27T00:26:00-04:00` → `2026-10-27T01:56:00-04:00`；expires `2026-10-27T01:58:00-04:00` |
| CLI PRIMARY | `--universe HILIQ --window x2 --x2-end 20261009 --out output/ai_factory/_leaf30_crr/<ET_TS>/` + `--allow-real-data --arch-ok-path <NEW_OK>`；**无** `--no-overlap-report` |
| FALLBACK | **无**；峰＞1500 / 失败 / ABORT → Exit 94/95 停+上报（禁抬帽） |
| rss 软/硬帽 | **1500** MB；禁抬帽；硬 Exit **94/95** |
| overlap | 强制 `overlap_vs_leaf19_25.json`；Jaccard≥0.7 硬拒；ρ>0.5 强度；count≠formal |
| PRIMARY load | **A rebal_day** 懒加载；禁整窗 `logmv_rebal=` 预载 |
| C2 / λ / 掩码 | OP+OCF only；λ=1.0；801780/801180/801790；`qend_ok_filter=true` |
| 产物 | `_leaf30_crr/<ET_TS>/` + `alpha_HILIQ_x2_<ET_TS>.parquet` + `run_meta.json` + `overlap_vs_leaf19_25.json` |
| 采样 | 仅 `/tmp/quantlab_leaf30_crr_r3_*` |
| 禁 RESTORED | 十六票：`5af20222,5ae077fa,3c297052,e107383f,2be59acd,1c32ab1e,ebc673bf,a7d98ac9,8e51de63,3a6caa4f,8bcd79dc,725be3e0,0f50daf7,3c19dd7d,6054b3bf,6de02e74` |
| Book-Smoke / X2 ACCEPT / selfcheck | **false** / **false** / **false** |
| peak_proof | **REQUIRED**（含 after_daily_concat + after_logmv_rebal_*；ru_maxrss/VmHWM/RSS_CHECK） |
| ban_touch_a18_ok_a62881b9 | **true** |
| ban_blind_rerun_a2cef5af / 0a264402-as-ticket | **true** / **true** |
| MemAvailable@签 | 6422468 kB |

## QUIET / pgrep

| 项 | 值 |
|---|---|
| QUIET 挂时 | `2026-10-27T00:27:29-04:00` reason=leaf30_crr_cfooe_volpen_alpha_build_r3_peakcut holder=leaf30_CRR_CFOOE_VOLPEN_ALPHA_BUILD_R3_PEAKCUT |
| do_not_lift_until_arch_or_consumed | **true**（本拍不 lift） |
| neq_a18 | **true**（未触 `_lifted` 旧 A18 QUIET） |
| pgrep kline/export_static/snapshot/gen | 空 |
| pgrep leaf30 | 空 |

## 下一跳

1. **主** MATCH `.ok`+`QUIET` 后令 AI prelaunch 单次 PRIMARY（须在 expires 前；Arch **不代跑**）
2. AI 交实峰回执（alpha sha + run_meta sha + overlap JSON + peak rss 含 after_daily_concat + after_logmv_rebal_*；峰＞1500→Exit 94/95 停；Jaccard≥0.7→硬拒票）→ Arch 核 CONSUME
3. ≠X2 ACCEPT；≠selfcheck；≠Book-Smoke；不解阻叶26/28/29；**≠A18**；不 RESTORED `5af20222`/`5ae077fa`；live=false

live=false。
