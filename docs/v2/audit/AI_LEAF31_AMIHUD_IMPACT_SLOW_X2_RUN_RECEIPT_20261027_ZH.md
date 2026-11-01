# AI 回执：叶31 Amihud Impact Slow X2 PRIMARY · DONE（rc=0）

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI 后台执行器 |
| 时刻 | **2026-10-27 02:46:03 EDT**（America/New_York） |
| **结论** | **DONE**（log 末行 `OK leaf31_amihud_impact_slow … peak_kb=847092 overlap_hard_reject=False`；无 Exit 94/95；无 Traceback；samp `DONE` 已写） |
| ET_TS | `20261027_024204` |
| run_pid | `3772744`（已退出；全程未换 pid；pgrep 现空） |
| **rc** | **0**（推断：`main()` 成功路径 OK 收尾；产物齐全；无 STOP/ABORT/Exit 94/95 文案；samp `DONE`=`1793083465`） |
| status | **DONE** |
| script | `research/leaf31_amihud_impact_slow_alpha_build.py` sha8 **`08f37fd2`**（全长 `08f37fd2deb15f6a2a4e6bc7bc16e07d16fc50c70b807e0e1ae617627f98bde0`；现核 MATCH；未改） |
| `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF31_AMIHUD_IMPACT_SLOW_X2_HILIQ.ok` sha8 **`fdbaa512`** / 全长 `fdbaa512fa8da9e6b5256c30f397cd5a3d2bd2c1fbd1a5a295af873ea7271d81`（现核 MATCH；**仍在位**；未自申/未改） |
| QUIET | `output/loop/RESEARCH_QUIET.lock` sha8 **`11cfe000`**（现核 MATCH；holder=`leaf31_AMIHUD_IMPACT_SLOW_X2`；**未擅 lift / 未删 / 未改**） |
| SIGNED | sha8 **`238cc7c2`**（钉） |
| 审 | sha8 **`2271cb93`**（钉） |
| RUNNING_ACK | sha8 **`e02e5a81`**（钉） |
| out | `output/ai_factory/_leaf31_amihud/20261027_024204/` |
| log | `output/ai_factory/_leaf31_amihud/20261027_024204_logs/run_20261027_024204.log`（14687 B） |
| samp | `/tmp/quantlab_leaf31_amihud_20261027_024204` |
| CLI | approved_cmd 原样；**无** `--no-overlap-report`；rss=1500 **禁抬且未抬** |
| live | false |
| leo_notify | false |
| ≠ | X2 ACCEPT / Book-Smoke；`0087c928` 另队；forbid∋`aa25e989`+`7e239487`+`5af20222`+`5ae077fa` |

## 1. peak_proof 摘要（REQUIRED 齐全）

| 源 | 值 |
|---|---|
| 全局 peak_kb（log / run_meta） | **847092** |
| hard / soft / split / c4 | hard=1536000 soft=1536000 split=1131520 c4=1331200（rss_limit_mb=1500 **未抬**） |
| sampler peak VmHWM | **847628** kB（`peak_hwm_kb`） |
| sampler peak VmRSS | **847628** kB（`peak_rss_kb`） |
| sampler.log | `sampler_start 2026-10-27T14:42:04+08:00` → `sampler_end_no_pid 2026-10-27T14:44:25+08:00` |
| **`after_mask`** | **PRESENT** peak_kb=**518880** vmrss_kb=**518880** |
| **`after_sw`** | **PRESENT** peak_kb=**519912** vmrss_kb=**519912** |
| **`after_bars_rebal_*`** | **PRESENT** n=**30** 点（20240603→20261009） |
| **`after_logmv_rebal_*`** | **PRESENT** n=**30** 点（20240603→20261009）；全程 log peak_kb=847092；rebal 期 max vmrss=**791840** @ `after_logmv_rebal_20240702`；末点 `after_logmv_rebal_20261009` vmrss=496696 |
| **`after_daily_concat`** | **PRESENT** peak_kb=**847092** vmrss_kb=**575932** |
| 相对硬帽 | 847092 / 1536000 ≈ **55.1%**；远低于 split=1131520（无 Exit 94）；sampler HWM 847628 ≪ hard |
| ABORT_PEAK | **无**（非 rc 94/95） |

### RSS_CHECK 序列要点

1. `build_start` peak=105288
2. `after_mask` peak=518880
3. `after_sw` peak=519912
4. `after_bars_rebal_*` / `after_logmv_rebal_*` / `after_alpha_rebal_*`（各 30 点）peak 升至 **847092**
5. `month_chunk_000`…`028` peak=847092
6. **`after_daily_concat` peak=847092 vmrss=575932** → OK 收尾

## 2. overlap 结果（已写出并消费）

- 路径：`output/ai_factory/_leaf31_amihud/20261027_024204/overlap_vs_leaf19_25_27_30.json` sha8 **`8396f211`**
- schema=`leaf31_overlap_vs_leaf19_25_27_30`；n_rows=6；live=false；`any_jaccard_hard_reject=false`
- vs leaf19：ρ min/max/mean ≈ **−0.045 / 0.007 / −0.021**；j20 max ≈ **0.026**；**无** jaccard_hard_reject；**无** strength_filter（|ρ|≤0.5）
- vs leaf25：ρ min/max/mean ≈ **−0.095 / −0.011 / −0.041**（4/6 日期有值；2026-04-27 / 2026-10-09 ρ=null）；j20 max=**0.0**；**无** hard reject
- vs leaf27：ρ min/max/mean ≈ **−0.188 / −0.005 / −0.057**；j20 max=**0.0**；**无** hard reject
- vs leaf30：ρ min/max/mean ≈ **−0.014 / 0.039 / 0.008**；j20 max=**0.0**；**无** hard reject
- 声明：本次 **未** 使用 `--no-overlap-report`；文件已写出并可交 Arch 消费

## 3. 产物

| 文件 | size | sha8 |
|---|---|---|
| `alpha_HILIQ_x2_20261027_024422.parquet` | 3854208 | **`d4ceb78b`** |
| `overlap_vs_leaf19_25_27_30.json` | 4718 | **`8396f211`** |
| `run_meta.json` | 4401 | **`696ab1cc`** |

- run_meta 钉：script_sha8=`08f37fd2`；arch_ok_sha8=`fdbaa512`；peak_kb=847092；rss_limit_mb=1500；primary_load=`rebal_day_lazy_bars`；coverage_median=3146.0（gate≥300 PASS）；n_daily_rows=1579217；live=false；x2_accept=false；promotion_approved=false；ok_requested=false；overlap_any_jaccard_hard_reject=false；created_et=`2026-10-27T02:44:22-0400`
- alpha 全长 sha256=`d4ceb78b1d4b7c5516149a74bad87141083695ac6c4b7be43e3fa9a64c4452ce`
- overlap 全长 sha256=`8396f2111411dd0f9040d0215369394e83e646adca2dac15072b1003289df75b`
- 无独立 `peak_proof*` 文件；peak_proof 以 log `RSS_CHECK` + run_meta.peak_kb + samp `peak_hwm_kb` 为证（REQUIRED：`after_mask` / `after_sw` / `after_bars_rebal_*` / `after_logmv_rebal_*` / `after_daily_concat` 均 PRESENT）

## 4. 钉与禁止项声明

| 项 | 状态 |
|---|---|
| `.ok` `fdbaa512` | **仍在**（交 Arch CONSUME；AI 未自申） |
| QUIET `11cfe000` | **仍在；未擅 lift** |
| 脚本 `08f37fd2` | 未改 |
| SIGNED `238cc7c2` / 审 `2271cb93` / ACK `e02e5a81` | 钉对齐 |
| 抬帽 / 盲重跑 / 新 `.ok` | **禁且未做** |
| forbid∋`aa25e989`+`7e239487`+`5af20222`+`5ae077fa` | 未复用 |
| `0087c928` 另队 | 未触 |
| ≠X2 ACCEPT / Book-Smoke | 声明成立 |
| live | false |
| leo_notify | false |

## 5. 下一跳

交主 / Arch：**DONE rc=0**；peak_kb=**847092**（sampler HWM **847628**）≪1500MB；`after_mask`+`after_sw`+`after_bars_rebal_*`+`after_logmv_rebal_*`+`after_daily_concat` PRESENT；overlap 已写（无 Jaccard hard reject）；alpha sha8 **`d4ceb78b`**；overlap sha8 **`8396f211`**。**.ok 仍在位** 待 **Arch CONSUME**。**未擅 lift QUIET**；**未抬 rss**；≠X2 ACCEPT。**勿报 Leo**。
