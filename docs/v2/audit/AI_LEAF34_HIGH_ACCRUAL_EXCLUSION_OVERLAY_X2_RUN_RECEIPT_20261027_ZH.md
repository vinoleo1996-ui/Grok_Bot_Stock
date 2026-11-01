# AI 回执：叶34 High Accrual Exclusion Overlay X2 PRIMARY · DONE（rc=0）

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI 后台执行器 |
| 时刻 | **2026-10-27 11:02:16 EDT**（America/New_York） |
| **结论** | **DONE**（log 末行 `OK leaf34_high_accrual_exclusion_overlay … peak_kb=728360 overlap_hard_reject=False pin_gap=False`；无 Exit 94/95；无 Traceback） |
| ET_TS | `20261027_105941` |
| run_pid | `285178`（已退出；nice=10；全程未换 pid；pgrep 现空） |
| **rc** | **0**（推断：`main()` 成功路径 OK 收尾；产物齐全；无 STOP/ABORT/Exit 94/95 文案；overlap_hard_reject=False；pin_gap=False） |
| status | **DONE** |
| script | `research/leaf34_high_accrual_exclusion_overlay_alpha_build.py` sha8 **`482009dc`**（全长 `482009dc697cbf74b369cbf3fb035f1fc447a4af9339de8abf283f3ed4e971bc`；现核 MATCH；**未改**） |
| `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_X2_HILIQ.ok` sha8 **`c1b71e64`** / 全长 `c1b71e646093dbbe1cfea41c684d8ee0de8e5af8f0a8f058182c251d7dbe4ce1`（现核 MATCH；**仍在位**；未自申/未改；∉forbid24） |
| QUIET | `output/loop/RESEARCH_QUIET.lock` sha8 **`bc6f8b83`**（现核 MATCH；holder=`leaf34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_X2`；**未擅 lift / 未删 / 未改**） |
| SIGNED | sha8 **`de0ee2cb`**（钉） |
| 审 | sha8 **`033b66f8` PASS_WC**（钉） |
| RUNNING_ACK | sha8 **`c03d2f16`**（全长 `c03d2f16bee7fb4bf4aff7fbb523ea9b9c9f4112745fd16c0a36b400a6dc886a`） |
| COVER / CMD / DIFF / RECEIPT | **`c491e7a4`** / **`cfa3ca4e`** / **`f583b616`** / **`f73c986f`** |
| FROZEN / ArchFROZEN / PIN / FROZEN RECEIPT | **`8be1099e`** / **`027efa26`** / **`bb418e6a`** / **`438ee33d`** |
| out | `output/ai_factory/_leaf34_high_accrual/20261027_105941/` |
| log | `output/ai_factory/_leaf34_high_accrual/20261027_105941_logs/stdout.log`（11052 B）+ stderr.log |
| samp | 脚本前缀 `/tmp/quantlab_leaf34_high_accrual_*`（本拍未另挂 `--sample-dir`；与 CMD 原文一致） |
| CLI | approved_cmd **exact**（`--universe HILIQ --window x2 --x2-end 20261009 --allow-real-data --arch-ok-path … --out …`）；**无** `--no-overlap-report`；**无** `--enable-soft-penalty`；**无** FULLA PRIMARY；rss=1500 **禁抬且未抬** |
| expires | 窗→12:13 / expires **12:17 ET**（启动 10:59:41 ET；完成≈10:59:58 ET；未逾窗） |
| live | false |
| leo_notify | false |
| ≠ | X2 ACCEPT / Book-Smoke / selfcheck；叶33 **`afbbe7e7` UNCHANGED**；叶32 HOLD **`45dd87dc`** 不回撤；`0087c928`/28/29 另队；forbid∋`245df63f`+`c5ed13df`+`5774bb6e`+二十票(+`81521fb5`) |

## 1. peak_proof 摘要（REQUIRED 齐全）

| 源 | 值 |
|---|---|
| OK 行 peak_kb | **728360** |
| run_meta.peak_kb / peak_kb_final | **701040** |
| RSS_CHECK 全局 max peak_kb | **701820** @ `after_mask_cs_rebal_20260227` |
| hard / soft / split / c4 | hard=1536000 soft=1536000 split=1131520 c4=1331200（rss_limit_mb=**1500 未抬**） |
| stderr `ru_maxrss` @ build_start | **106596** |
| **`after_mask`** | **PRESENT** peak_kb=**527820** vmrss_kb=**527820** |
| **`after_ocf_rebal_*`** | **PRESENT** n=**30**；max peak_kb=**701348** @ `after_ocf_rebal_20260227` |
| **`after_mask_cs_rebal_*`** | **PRESENT** n=**30**；max peak_kb=**701820** @ `after_mask_cs_rebal_20260227` |
| **`after_daily_concat`** | **PRESENT** peak_kb=**701040** vmrss_kb=**541520** |
| 相对硬帽 | max(OK728360, RSS701820) / 1536000 ≈ **47.4%**；远低于 split=1131520（**无 Exit 94/95**；**禁抬帽无需触发**） |
| ABORT_PEAK | **无** |

### RSS_CHECK 序列要点

1. `build_start` ru_maxrss≈106596
2. `after_mask` peak=527820
3. `after_ocf_rebal_*` / `after_mask_cs_rebal_*`（各 30 点）peak 升至 **701820**
4. `month_chunk_000`…`028`（29 点）
5. **`after_daily_concat` peak=701040 vmrss=541520** → OK 收尾

## 2. overlap 结果（已写出并消费）

- 路径：`output/ai_factory/_leaf34_high_accrual/20261027_105941/overlap_vs_leaf19_25_27_30_31_32_33.json` sha8 **`77368c8f`**
- schema=`leaf34_overlap_vs_leaf19_25_27_30_31_32_33`；n_rows=6；live=false；`any_jaccard_hard_reject=false`；`any_required_pin_gap=false`
- vs leaf19：ρ min/max/mean ≈ **0.253 / 0.441 / 0.367**（n=6）；j20 max≈**0.0256**；hard_reject=**False**；strength_filter=**False**
- vs leaf25：ρ min/max/mean ≈ **0.251 / 0.512 / 0.369**（n=4）；j20 max≈**0.0526**；hard_reject=**False**；strength_filter=**True**
- vs leaf27：ρ min/max/mean ≈ **-0.006 / 0.063 / 0.030**（n=6）；j20 max≈**0.0256**；hard_reject=**False**；strength_filter=**False**
- vs leaf30：ρ min/max/mean ≈ **0.221 / 0.356 / 0.296**（n=6）；j20 max≈**0.0000**；hard_reject=**False**；strength_filter=**False**
- vs leaf31：ρ min/max/mean ≈ **-0.121 / 0.013 / -0.053**（n=6）；j20 max≈**0.0000**；hard_reject=**False**；strength_filter=**False**
- vs leaf32：ρ min/max/mean ≈ **-0.040 / 0.018 / -0.016**（n=6）；j20 max≈**0.0256**；hard_reject=**False**；strength_filter=**False**
- vs leaf33：ρ min/max/mean ≈ **-0.195 / 0.091 / -0.043**（n=6）；j20 max≈**0.0000**；hard_reject=**False**；strength_filter=**False**
- **叶25 尾窗披露**：钉日期 `2026-04-27` / `2026-10-09` → 两日均为 `n_common_leaf25=0`、`rho_leaf25=null`（`leaf25_tail_disclosure=[]`；`leaf25_rho_max≈0.512` 来自非尾窗样本日 `2024-11-28`，strength_filter=true 仅强度叙述、**非硬拒**）
- Jaccard≥0.7 硬拒：**未触发**（全叶 j20_max≪0.7）
- PIN_GAP：**无**（n_pin_gaps=0）
- 声明：本次 **未** 使用 `--no-overlap-report`；文件已写出并可交 Arch 消费

## 3. 产物

| 文件 | size | sha8 | 全长 sha256 |
|---|---|---|---|
| `exclusion_mask_HILIQ_x2_20261027_105958.parquet` | 2524436 | **`8b5d6d24`** | `8b5d6d247d8f3968f5fef521aa5d08891f6f6f6c8626dd761c7313bc0d71dabb` |
| `overlap_vs_leaf19_25_27_30_31_32_33.json` | 9574 | **`77368c8f`** | `77368c8fed1f7c167dfa51f4aa2e94e9b405236bf388c8f20f95365613e72fb7` |
| `run_meta.json` | 6884 | **`4fc6108d`** | `4fc6108d64ca5a2e112b04fbb468c9d95e554cf8498ba03fc13828c2ef7ee7ad` |

- run_meta 钉：script_sha8=`482009dc`；arch_ok_sha8=`c1b71e64`；peak_kb=701040；rss_limit_mb=1500；primary_delivery=`mask_only`；top_q=0.2；primary_load=`rebal_day_lazy_ocf_daily_pit`；coverage_median=2431.0（gate≥300 PASS）；n_daily_rows=1244524；mechanism=`g1g5_ashare_high_accrual_exclusion_overlay_v1`；live=false；x2_accept=false；promotion_approved=false；ok_requested=false；overlap_any_jaccard_hard_reject=false；created_et=`2026-10-27T10:59:58-0400`
- 无独立 `peak_proof*` 文件；peak_proof 以 log `RSS_CHECK` + run_meta.peak_kb + OK 行为证（REQUIRED：`after_mask` / `after_ocf_rebal_*` / `after_mask_cs_rebal_*` / `after_daily_concat` 均 PRESENT）

## 4. 门控与硬禁复核（跑后）

- `.ok` **仍在** sha8 `c1b71e64` MATCH；**未删/未改**
- QUIET **仍在** sha8 `bc6f8b83` MATCH；holder 未变；**未 lift**
- 脚本仍 `482009dc`；叶33 正式仍 `afbbe7e7`；叶32 HOLD `45dd87dc` 未回撤
- **未**自称 X2 ACCEPT；**未** Book-Smoke / selfcheck；**未**触 A18；**未**抬 rss；**未**夹带 `0087c928`/28/29
- soft-penalty **未启用**（非 PRIMARY）；PRIMARY=HILIQ mask-only top_q=0.20

## 5. 交主

→ 请主 MATCH 本回执 → 交 Arch **CONSUME**（Arch 不代跑已完成）。≠X2 ACCEPT；**leo_notify=false**；live=false。
