# AI 回执：叶33 X2 tz-align PRIMARY · ABORT_COVERAGE_GATE（rc=5；coverage median 30<300）

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI 后台执行器 |
| 时刻 | **2026-10-27 07:28:42 EDT**（America/New_York；ISO `2026-10-27T07:28:42-04:00`） |
| 主令 | ~07:18 ET GO MATCH；RUNNING_ACK **`170f71e1`**；`.ok` **`245df63f`** / QUIET **`ca492c09`** / SIGNED **`731f05d7`** / 落地审 **`069ba364`** / 补丁审 **`19cc790f`** / 脚本 **`afbbe7e7`** / VOID **`8a3b25ba`** / 前次 ABORT RUN **`481bacda`** / FROZEN **`8ed43721`** / PIN **`4e17ccfc`** |
| **结论** | **ABORT_COVERAGE_GATE**；rc=**5**；已写出 alpha/overlap/run_meta；**越过**前次 L818 TypeError；**无** Exit 94/95；**无** Jaccard hard reject；coverage_gate_pass=**false**（median=**30.0** < gate=**300**）→ 脚本 `return 5`；**未**擅改脚本；**未** lift QUIET；**未**申新 `.ok`；**未**复跑 |
| ≠X2 ACCEPT | **true** |
| ≠selfcheck / ≠Book-Smoke | **true** |
| live / leo_notify | **false** / **false** |
| 禁 RESTORED | **`c5ed13df`**（本拍未触；`.ok` 为新签 **`245df63f`**） |

## 0. 一句话

tz-align PRIMARY（脚本 **`afbbe7e7`** / `tz_align_mode=naive_calendar_day` / 基线钉 `05c45917`）按钉开跑并跑完：产物齐全、peak_kb=**963232**≪1500、overlap **无** Jaccard hard reject；但 **coverage median 30.0 < gate 300** → rc=**5** / **ABORT_COVERAGE_GATE**。`.ok` **`245df63f`** / QUIET **`ca492c09`** 仍在（do_not_lift）。**交主→Arch CONSUME**；AI **禁自改复跑**。

## 1. 运行钉

| 项 | 值 |
|---|---|
| ET_TS | `20261027_072135` |
| pid | `4194000`（已退出；nice=10；全程未换 pid；现 pgrep 空） |
| **rc** | **5**（coverage gate；非 94/95；非 TypeError） |
| status | **ABORT_COVERAGE_GATE** |
| 脚本 | `research/leaf33_share_unlock_pressure_resid_alpha_build.py` sha8 **`afbbe7e7`**（全长 `afbbe7e7292c17399bbf4733d9f34a922e6d81f1a914a60d24dc61fcba86cbc9`；基线钉 `05c45917`；`tz_align_mode=naive_calendar_day`；**UNCHANGED**） |
| `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_X2_HILIQ.ok` sha8 **`245df63f`** / 全长 `245df63f5c8e39052da15a4f2338132382d6e60751c2f22df316a7d71575e4cc`（**仍在**；**≠** RESTORED `c5ed13df`） |
| QUIET | `output/loop/RESEARCH_QUIET.lock` sha8 **`ca492c09`** / 全长 `ca492c09202addb0af5ab13ad078a99eeefb53f34305d41476068788183cdf72`（holder=`leaf33_SHARE_UNLOCK_PRESSURE_RESID_X2`；expires **08:45 ET**；**未擅 lift / 未删 / 未改**；do_not_lift） |
| SIGNED / 落地审 / 补丁审 | **`731f05d7`** / **`069ba364`** / **`19cc790f`** |
| RUNNING_ACK | **`170f71e1`** |
| VOID / 前次 ABORT RUN | **`8a3b25ba`** / **`481bacda`** |
| FROZEN / PIN | **`8ed43721`** / **`4e17ccfc`** |
| approved_cmd | `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf33_share_unlock_pressure_resid_alpha_build.py --universe HILIQ --window x2 --x2-end 20261009 --allow-real-data --arch-ok-path output/ai_factory/ARCH_RUN_AUTH_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_X2_HILIQ.ok --out output/ai_factory/_leaf33_share_unlock/20261027_072135/ --sample-dir /tmp/quantlab_leaf33_share_unlock_20261027_072135` |
| `--no-overlap-report` | **未加**（禁） |
| rss 帽 | 1500；**未抬**；无 Exit 94/95 |
| out | `output/ai_factory/_leaf33_share_unlock/20261027_072135/` |
| log | `output/ai_factory/_leaf33_share_unlock/20261027_072135_logs/run_20261027_072135.log` sha8 **`921dd5f3`**（25854 B） |
| samp | `/tmp/quantlab_leaf33_share_unlock_20261027_072135`（`DONE` 已写；sampler 见下） |

## 2. peak_proof 摘要（REQUIRED 齐全）

| 源 | 值 |
|---|---|
| 全局 peak_kb（OK / run_meta） | **963232** |
| log RSS_CHECK peak_kb 最大值 | **964220**（单点 `after_float_mktcap_rebal_20241226`；其后日志行 peak 记为 963232；以 run_meta/OK/samp HWM 为准） |
| hard / soft / split / c4 | hard=1536000 soft=1536000 split=1131520 c4=1331200（rss_limit_mb=1500 **未抬**） |
| STAGE build_start ru_maxrss | **107512** |
| sampler peak VmHWM | **963232** kB（`peak_hwm_kb`） |
| sampler peak VmRSS | **957704** kB（`peak_rss_kb`） |
| sampler.log | `sampler_start 2026-10-27T19:21:35+08:00 → sampler_end_no_pid 2026-10-27T19:25:53+08:00` |
| **`after_mask`** | **PRESENT** peak_kb=**515908** vmrss_kb=**515908** |
| **`after_sw`** | **PRESENT** peak_kb=**525132** vmrss_kb=**525132** |
| **`after_share_float_rebal_*`** | **PRESENT** n=**30**（20240603→20261009） |
| **`after_float_mktcap_rebal_*`** | **PRESENT** n=**30** |
| **`after_close_rebal_*`** | **PRESENT** n=**30** |
| **`after_bars_rebal_*`** | **PRESENT** n=**30** |
| **`after_logmv_rebal_*`** | **PRESENT** n=**30** |
| **`month_chunk_*`** | **PRESENT** n=**29** |
| **`after_daily_concat`** | **PRESENT** peak_kb=**963232** vmrss_kb=**611968** |
| 相对硬帽 | 963232 / 1536000 ≈ **62.7%**；远低于 split=1131520 |
| ABORT_PEAK | **无**（非 rc 94/95） |

### RSS_CHECK 序列要点

1. `build_start` peak≈107604；ru_maxrss=107512
2. `after_mask` / `after_sw` PRESENT（已越过前次 L818 tz TypeError）
3. rebal 期 `after_share_float/float_mktcap/close/bars/logmv/alpha_rebal_*` 各 30 点；month_chunk 29 点
4. `after_daily_concat` → OK 行写出 → **STOP coverage**（rc=5）

## 3. overlap 结果（已写出并消费）

- 路径：`output/ai_factory/_leaf33_share_unlock/20261027_072135/overlap_vs_leaf19_25_27_30_31_32_margin_delta_hk_hold_moneyflow.json` sha8 **`473b339e`**
- schema=`leaf33_overlap_vs_leaf19_25_27_30_31_32_margin_delta_hk_hold_moneyflow`；n_rows=6；live=false；`any_jaccard_hard_reject=false`
- vs leaf19：ρ min/max/mean ≈ **-0.365 / 0.438 / 0.087**（6/6 日期有值）；j20 max ≈ **0.0256**；**无** jaccard_hard_reject；**无** strength_filter
- vs leaf25：ρ min/max/mean ≈ **-0.137 / -0.072 / -0.109**（4/6 日期有值）；j20 max ≈ **0.0256**；**无** jaccard_hard_reject；**无** strength_filter
- vs leaf27：ρ min/max/mean ≈ **-0.038 / 0.222 / 0.091**（6/6 日期有值）；j20 max ≈ **0**；**无** jaccard_hard_reject；**无** strength_filter
- vs leaf30：ρ min/max/mean ≈ **-0.005 / 0.190 / 0.083**（6/6 日期有值）；j20 max ≈ **0**；**无** jaccard_hard_reject；**无** strength_filter
- vs leaf31：ρ min/max/mean ≈ **-0.065 / 0.308 / 0.136**（6/6 日期有值）；j20 max ≈ **0.0256**；**无** jaccard_hard_reject；**无** strength_filter
- vs leaf32：ρ min/max/mean ≈ **-0.273 / 0.153 / -0.033**（6/6 日期有值）；j20 max ≈ **0.0256**；**无** jaccard_hard_reject；**无** strength_filter
- vs margin_delta：ρ **null**（全部日期无有效相关）；j20 max ≈ **0**；**无** jaccard_hard_reject；**无** strength_filter
- vs hk_hold：ρ **null**（全部日期无有效相关）；j20 max ≈ **0**；**无** jaccard_hard_reject；**无** strength_filter
- vs moneyflow：ρ **null**（全部日期无有效相关）；j20 max ≈ **0**；**无** jaccard_hard_reject；**无** strength_filter
- PIN_GAP：**无**（n_pin_gaps=0；`any_required_pin_gap=False`）
- 声明：本次 **未** 使用 `--no-overlap-report`；文件已写出并可交 Arch 消费
- **无** Jaccard hard reject（非 exit 4）

## 4. 产物

| 文件 | size | sha8 |
|---|---|---|
| `alpha_HILIQ_x2_20261027_072552.parquet` | 22054 | **`ea17e173`** |
| `overlap_vs_leaf19_25_27_30_31_32_margin_delta_hk_hold_moneyflow.json` | 10087 | **`473b339e`** |
| `run_meta.json` | 6104 | **`f4702783`** |

- run_meta 钉：script_sha8=`afbbe7e7`；arch_ok_sha8=`245df63f`；peak_kb=963232；rss_limit_mb=1500；primary_load=`rebal_day_lazy_share_float_close_mktcap_bars`；coverage_median=30.0（gate=300 **FAIL**）；n_daily_rows=16106；mechanism=`g1g5_ashare_share_unlock_pressure_resid_v1`；live=false；x2_accept=false；promotion_approved=false；ok_requested=false；overlap_any_jaccard_hard_reject=false；frozen_sha8=`8ed43721`；pin_sha8=`4e17ccfc`；created_et=`2026-10-27T07:25:52-0400`
- decay_keep_pin.note 含 `tz_align_mode=naive_calendar_day`；base_script=`05c45917`；VOID=`8a3b25ba`；RUN=`481bacda`
- alpha 全长 sha256=`ea17e173d4e7b5f4945c9a8930945fecf2bde78f3b22b63fa3c2e8b4f90ad69d`
- overlap 全长 sha256=`473b339ec0c79d9c52400b2cbbf57059097cf288a6496ec733e2c0649765c76d`
- meta 全长 sha256=`f470278310233a6dc196d621c20782019053dadaa5fe0fd5406536e8b16058c9`
- log 全长 sha256=`921dd5f30db13258fc612994f8ae36bf8e2d45489e629b3a3228593db81329c1`
- 无独立 `peak_proof*` 文件；peak_proof 以 log `RSS_CHECK` + run_meta.peak_kb + samp `peak_hwm_kb` 为证

### 错误摘录（log 末）

```
OK leaf33_share_unlock_pressure_resid universe=HILIQ window=x2 final=output/ai_factory/_leaf33_share_unlock/20261027_072135/alpha_HILIQ_x2_20261027_072552.parquet peak_kb=963232 overlap_hard_reject=False pin_gap=False
STOP: coverage median 30.0 < gate 300
```

根因（只报不改）：HILIQ×x2 上 share-unlock pressure 有效覆盖 median=**30**（rebal 日 n≈15–72）远低于脚本钉门 `COVERAGE_MEDIAN_HILIQ=300`。tz 对齐本身已生效（产物写出；非 TypeError）。**禁 AI 自改复跑 / 禁擅改门限 / 禁 lift QUIET**。

## 5. 钉点 MATCH（跑后）

| 项 | sha8 | 状态 |
|---|---|---|
| 脚本 | `afbbe7e7` / `afbbe7e7292c17399bbf4733d9f34a922e6d81f1a914a60d24dc61fcba86cbc9` | **UNCHANGED** |
| `.ok` | `245df63f` / `245df63f5c8e39052da15a4f2338132382d6e60751c2f22df316a7d71575e4cc` | **仍在；≠ RESTORED c5ed13df；未复用他叶** |
| QUIET | `ca492c09` / `ca492c09202addb0af5ab13ad078a99eeefb53f34305d41476068788183cdf72` | **仍在；未擅 lift**；holder=`leaf33_SHARE_UNLOCK_PRESSURE_RESID_X2`；expires 08:45 ET |
| SIGNED / 落地审 / 补丁审 | `731f05d7` / `069ba364` / `19cc790f` | 上游 |
| VOID / 前次 RUN | `8a3b25ba` / `481bacda` | 上游 |
| FROZEN / PIN | `8ed43721` / `4e17ccfc` | 上游 MATCH（run_meta） |
| forbid∋`5774bb6e`+二十 | `.ok`∉forbid | MATCH |
| pgrep kline/export_static/snapshot/gen / leaf33 | 空 | MATCH |
| C3 / KEEP / 0087c928 | 未改定义；另队不夹带 | MATCH |

## 6. 禁令自检

- **未**改脚本 `afbbe7e7` / **未**改基线对照 `05c45917` 语义外的 C3/α/H/W/rebal/rss
- **未**申新 `.ok` / **未** lift QUIET / **未** RESTORED `c5ed13df`
- **未**盲复跑 / **未** `--no-overlap-report` / **未**抬 rss
- **未**报 Leo / **未**派 Eng / **未**宣称 X2 ACCEPT
- `0087c928` / 叶28/29 **另队**；未触 A18

## 7. 下一跳（请主排）

1. **Arch CONSUME** 本回执（**ABORT_COVERAGE_GATE**；rc=5；产物在 out；`.ok`/`QUIET` 仍在位等 Arch；AI **未** 擅 lift）
2. 是否另开 coverage 诊断/门限或数据侧补丁 → 听 Arch/主令；**禁 AI 自改复跑**
3. 当前 QUIET **保留**至 Arch/主令 lift；expires **08:45 ET**；do_not_lift

**EXECUTED_ATTEMPTED=true** · **SUCCESS=false** · **X2_ACCEPT=false** · live=false · leo_notify=false
