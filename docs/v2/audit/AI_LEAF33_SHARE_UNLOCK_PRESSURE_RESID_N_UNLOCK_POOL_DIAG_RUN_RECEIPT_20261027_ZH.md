# AI RUN_RECEIPT · 叶33 A1 n_unlock_pool 诊断探针 DONE

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI |
| 时刻 | `2026-10-27T08:30:58-04:00`（America/New_York；墙钟 2026-10-27 08:30 ET） |
| **结论** | **DIAG_PROBE DONE** · rc=**0** · ≠正式 α · ≠X2 ACCEPT · θ **未自决** |
| ET_TS | `20261027_082801` |
| pid | `71737` · nice=10 · **DEAD** |
| `.ok` | **`81521fb5` 仍在**（live；本拍未归档） |
| QUIET | **`7fc1e7b7` 未擅 lift**（live） |
| SIGNED | **`a7c0bc2b`** |
| 探针脚本 | **`083d09fe` UNCHANGED** |
| 正式脚本 | **`afbbe7e7` UNCHANGED** |
| Arch 审 | **`b037404a`** |
| DRAFT/COVER/RECEIPT(票) | **`6a22123d`** / **`92262b70`** / **`0fb1942d`** |
| RUNNING_ACK | **`d8ee702a`** |
| 上游 VOID/RUN/alpha | **`6826c01d`** / **`a1b426f5`** / **`ea17e173`** |
| 复议 DRAFT/Arch审 | **`b84496fe`** / **`29166bf7`** |

## 0. 一句话

诊断探针 rc=0 已写出 summary/per_rebal；`n_unlock_pool` median=**81.0**；`n_alpha` median=**30.0**；`ratio` median=**0.336538**（再平衡日 n=**29**）。peak（launch pid `71737`）VmRSS=**5245088** KB / VmHWM=**5361952** KB → **超** rss=1500MB 软顶（本探针脚本无 Exit94/95 硬闸；如实盘证）。θ **未自决**；gate=300 **未降**；正式脚本 **未改**；QUIET **未擅 lift**。请主→Arch **CONSUME**。

## 1. 产物钉

| 件 | 路径 | sha8 |
|---|---|---|
| summary | `output/ai_factory/_leaf33_share_unlock/diag_n_unlock_pool_v1/summary_n_unlock_pool_diag.json` | **`de69554a`** |
| per_rebal | `output/ai_factory/_leaf33_share_unlock/diag_n_unlock_pool_v1/per_rebal_n_unlock_pool_diag.json` | **`86949aaa`** |
| log | `output/ai_factory/_leaf33_share_unlock/diag_n_unlock_pool_v1_logs/20261027_082801.log` | — |
| sampler | `/tmp/quantlab_leaf33_n_unlock_pool_diag_20261027_082801` | peak_proof |

## 2. 分布（只报数 · **不钉 θ**）

| 度量 | 分布 |
|---|---|
| `n_unlock_pool` | n=29; median=**81.0**; p10=59.0; p25=72.0; p75=102.0; p90=126.4; min=53.0; max=1907.0 |
| `n_alpha` | n=29; median=**30.0**; p10=16.8; p25=25.0; p75=35.0; p90=41.39999999999999; min=15.0; max=72.0 |
| `ratio=n_alpha/n_unlock_pool` | n=29; median=**0.33653846153846156**; p10=0.2620619344972601; p25=0.31746031746031744; p75=0.3950617283950617; p90=0.42913580246913574; min=0.015731515469323543; max=0.972972972972973 |

- 再平衡日数（有限 ratio / 汇总 n）= **29**
- θ 讨论区间仍为 **0.5–0.8**（**等主钉**；本回执**不**建议具体 θ）
- `coverage_median_hiliq_readonly=300`；`gate_changed=false`
- summary.`theta_self_decided=false` MATCH

## 3. peak_proof

| 项 | 值 |
|---|---|
| launch_pid | `71737` |
| sampler VmRSS peak_kb（仅 launch pid） | **5245088** |
| sampler VmHWM peak_kb（仅 launch pid） | **5361952** |
| rss_limit | 1500 MB = **1536000** KB |
| over_soft_1500 | **true** |
| Exit 94/95 | **无**（探针脚本未实施硬 ABORT；非正式 X2） |
| sampler 干扰 pid | ['72192']（ACK 补写误触进程；**已从 peak 剔除**；主 peak 仅 launch pid） |
| duration_s（sampler） | ~45 |

## 4. 状态自检

| 项 | 状态 |
|---|---|
| 正式脚本 `afbbe7e7` | **UNCHANGED** |
| 探针 `083d09fe` | **UNCHANGED** |
| live `.ok` `81521fb5` | **仍在**（待 Arch CONSUME 归档） |
| live QUIET `7fc1e7b7` | **仍在 · 未擅 lift** |
| gate=300 | **未降** |
| θ | **未自决** |
| RESTORED 禁票 | **未触** |
| ≠X2 ACCEPT / ≠selfcheck / ≠Book-Smoke | **true** |

## 5. 下一跳

```
DIAG RUN_RECEIPT（本文件）
  → 主令 Arch CONSUME（归档 .ok / lift QUIET）
      → 主据 ratio/n_unlock_pool 分布钉 θ∈0.5–0.8 或改 C HOLD / 另窗 FROZEN
```

**DIAG_EXECUTED=true** · **leo_notify=false** · **live=false** · **ok_requested=false** · **≠X2 ACCEPT** · **θ_undecided=true**

