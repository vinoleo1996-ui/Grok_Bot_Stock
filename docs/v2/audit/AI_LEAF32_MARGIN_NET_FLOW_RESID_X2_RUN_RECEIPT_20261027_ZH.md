# AI 回执：叶32 Margin Net Flow Resid X2 PRIMARY · DONE（rc=0）

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI 后台执行器 |
| 时刻 | **2026-10-27 04:44:20 EDT**（America/New_York） |
| **结论** | **DONE**（log 末行 `OK leaf32_margin_net_flow_resid … peak_kb=929300 overlap_hard_reject=False pin_gap=False`；无 Exit 94/95；无 Traceback；samp `DONE` 已写） |
| ET_TS | `20261027_042805` |
| run_pid | `3952200`（已退出；全程未换 pid；pgrep 现空） |
| **rc** | **0**（推断：`main()` 成功路径 OK 收尾；产物齐全；无 STOP/ABORT/Exit 94/95 文案；samp `DONE` 已写） |
| status | **DONE** |
| script | `research/leaf32_margin_net_flow_resid_alpha_build.py` sha8 **`4e0f3c00`**（全长 `4e0f3c002057393c031598e0379c6622afe8ca4a18579c9ab3b9f3d7ba4ae187`；现核 MATCH；未改） |
| `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF32_MARGIN_NET_FLOW_RESID_X2_HILIQ.ok` sha8 **`02426b73`** / 全长 `02426b73d253237127772bd0023c52938ad58bdb76204feeddac87ceb385d736`（现核 MATCH；**仍在位**；未自申/未改） |
| QUIET | `output/loop/RESEARCH_QUIET.lock` sha8 **`6d62911f`**（现核 MATCH；holder=`leaf32_MARGIN_NET_FLOW_RESID_X2`；**未擅 lift / 未删 / 未改**） |
| SIGNED | sha8 **`39baa28e`**（钉） |
| 审 | sha8 **`814939b8`**（钉） |
| RUNNING_ACK | sha8 **`3c4d0124`**（钉） |
| FROZEN / ArchFROZEN | **`6b8de5e9`** / **`7c0d864f`**（钉） |
| out | `output/ai_factory/_leaf32_margin_flow/20261027_042805/` |
| log | `output/ai_factory/_leaf32_margin_flow/20261027_042805_logs/run_20261027_042805.log`（21879 B） |
| samp | `/tmp/quantlab_leaf32_margin_flow_20261027_042805` |
| CLI | approved_cmd 原样 + 推荐 `--sample-dir`；**无** `--no-overlap-report`；rss=1500 **禁抬且未抬** |
| live | false |
| leo_notify | false |
| ≠ | X2 ACCEPT / Book-Smoke；`0087c928` 另队；forbid∋`4bb141c9`+`fdbaa512`+`aa25e989`+`7e239487`+`5af20222`+`5ae077fa` |

## 1. peak_proof 摘要（REQUIRED 齐全）

| 源 | 值 |
|---|---|
| 全局 peak_kb（log / run_meta） | **929300** |
| hard / soft / split / c4 | hard=1536000 soft=1536000 split=1131520 c4=1331200（rss_limit_mb=1500 **未抬**） |
| sampler peak VmHWM | **929300** kB（`peak_hwm_kb`） |
| sampler peak VmRSS | **915276** kB（`peak_rss_kb`） |
| sampler.log | `sampler_start 2026-10-27T16:28:05+08:00` → `sampler_end_no_pid 2026-10-27T16:42:17+08:00` |
| **`after_mask`** | **PRESENT** peak_kb=**513296** vmrss_kb=**513296** |
| **`after_sw`** | **PRESENT** peak_kb=**516368** vmrss_kb=**516368** |
| **`after_margin_rebal_*`** | **PRESENT** n=**30** 点（20240603→20261009） |
| **`after_float_rebal_*`** | **PRESENT** n=**30** 点（20240603→20261009） |
| **`after_bars_rebal_*`** | **PRESENT** n=**30** 点（20240603→20261009） |
| **`after_logmv_rebal_*`** | **PRESENT** n=**30** 点（20240603→20261009）；全程 log peak_kb=929300；rebal 期 max vmrss=**871420** @ `after_logmv_rebal_20260918`；末点 `after_logmv_rebal_20261009` vmrss=603696 |
| **`after_daily_concat`** | **PRESENT** peak_kb=**929300** vmrss_kb=**640640** |
| 相对硬帽 | 929300 / 1536000 ≈ **60.5%**；远低于 split=1131520（无 Exit 94）；sampler HWM 929300 ≪ hard |
| ABORT_PEAK | **无**（非 rc 94/95） |

### RSS_CHECK 序列要点

1. `build_start` peak≈105696
2. `after_mask` peak=513296
3. `after_sw` peak=516368
4. `after_margin/float/bars/logmv/alpha_rebal_*`（各 30 点）peak 升至 **929300**
5. `month_chunk_000`…`028`（29 点）peak=929300
6. **`after_daily_concat` peak=929300 vmrss=640640** → OK 收尾

## 2. overlap 结果（已写出并消费）

- 路径：`output/ai_factory/_leaf32_margin_flow/20261027_042805/overlap_vs_leaf19_25_27_30_31_margin_delta.json` sha8 **`a643d71a`**
- schema=`leaf32_overlap_vs_leaf19_25_27_30_31_margin_delta`；n_rows=6；live=false；`any_jaccard_hard_reject=false`
- vs leaf19：ρ min/max/mean ≈ **−0.063 / 0.071 / −0.016**；j20 max ≈ **0.026**；**无** jaccard_hard_reject；**无** strength_filter
- vs leaf25：ρ min/max/mean ≈ **0.009 / 0.122 / 0.053**（4/6 日期有值；2 日 ρ=null）；j20 max=**0.0**；**无** hard reject
- vs leaf27：ρ min/max/mean ≈ **−0.171 / 0.034 / −0.038**；j20 max=**0.0**；**无** hard reject
- vs leaf30：ρ min/max/mean ≈ **−0.079 / 0.018 / −0.016**；j20 max=**0.0**；**无** hard reject
- vs leaf31：ρ min/max/mean ≈ **−0.063 / 0.071 / 0.028**；j20 max=**0.0**；**无** hard reject
- vs margin_delta：ρ min/max/mean ≈ **−0.432 / 0.162 / −0.159**；j20 max=**0.0**；**无** hard reject；**无** strength_filter（|ρ|≤0.5）
- PIN_GAP：**无**（n_pin_gaps=0）
- 声明：本次 **未** 使用 `--no-overlap-report`；文件已写出并可交 Arch 消费

## 3. 产物

| 文件 | size | sha8 |
|---|---|---|
| `alpha_HILIQ_x2_20261027_044214.parquet` | 1982530 | **`13eee6fd`** |
| `overlap_vs_leaf19_25_27_30_31_margin_delta.json` | 7210 | **`a643d71a`** |
| `run_meta.json` | 4942 | **`e510f346`** |

- run_meta 钉：script_sha8=`4e0f3c00`；arch_ok_sha8=`02426b73`；peak_kb=929300；rss_limit_mb=1500；primary_load=`rebal_day_lazy_margin_float_bars`；coverage_median=2454.0（gate≥300 PASS）；n_daily_rows=1234632；mechanism=`g1g5_ashare_margin_net_flow_resid_v1`；live=false；x2_accept=false；promotion_approved=false；ok_requested=false；overlap_any_jaccard_hard_reject=false；created_et=`2026-10-27T04:42:14-0400`
- alpha 全长 sha256=`13eee6fdf0922b14756cf22985964dcd177810772a2ee4ec3bdb7c1668646ed2`
- overlap 全长 sha256=`a643d71ad77e3ae06eab2dc1fb20a0b99bf3d572db9310821b00ba8627bfe5fe`
- meta 全长 sha256=`e510f346bed46e6ca64f802de3aaed5f28f469f0a2fbf68ee2d5f2fffc4f6610`
- 无独立 `peak_proof*` 文件；peak_proof 以 log `RSS_CHECK` + run_meta.peak_kb + samp `peak_hwm_kb` 为证（REQUIRED：`after_mask` / `after_sw` / `after_margin_rebal_*` / `after_float_rebal_*` / `after_bars_rebal_*` / `after_logmv_rebal_*` / `after_daily_concat` 均 PRESENT）

## 4. 钉与禁止项声明

| 项 | 状态 |
|---|---|
| `.ok` `02426b73` | **仍在**（交 Arch CONSUME；AI 未自申） |
| QUIET `6d62911f` | **仍在；未擅 lift** |
| rss=1500 | **未抬**；无 Exit 94/95 |
| `--no-overlap-report` | **未用** |
| RESTORED 六票 | **未触**（`4bb141c9`/`fdbaa512`/`aa25e989`/`7e239487`/`5af20222`/`5ae077fa`） |
| `0087c928` | **未夹带**（另队） |
| 脚本 | **未改**（`4e0f3c00` MATCH） |
| ≠X2 ACCEPT / ≠Book-Smoke | **成立**；live=false；leo_notify=false |

## 5. 请主

请排 **Arch CONSUME**（`.ok`/`QUIET` 仍在位等 Arch；AI **未** 擅 lift）。≠X2 ACCEPT。**勿报 Leo**。live=false。
