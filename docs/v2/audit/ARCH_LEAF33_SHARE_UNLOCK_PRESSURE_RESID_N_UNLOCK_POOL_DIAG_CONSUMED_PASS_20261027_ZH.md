# Arch 叶33 A1 `n_unlock_pool` 诊断探针 · CONSUMED_PASS

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-27T08:36:24-04:00`（America/New_York） |
| 主令 | 主 ~08:31 ET · 叶33 A1 探针 CONSUME（MATCH DIAG DONE：RUN `ee0ba09d` / ACK `d8ee702a` / summary `de69554a` / per_rebal `86949aaa`；rc=0；pid `71737` DEAD） |
| 结论 | **CONSUMED_PASS**（rc=**0**；有分布产物；**peak 超软顶如实披露** → `PEAK_SOFT_EXCEEDED_NO_HARD_ABORT`） |
| live / ≠X2 ACCEPT / ≠正式 α / ≠Book-Smoke / ≠selfcheck | **false** / **true** / **true** / **true** / **true** |
| leo_notify | **false** |

## 0. 一句话

诊断探针 DONE（rc=0；n_rebal=29；`n_unlock_pool` median=**81.0**；`n_alpha` median=**30.0**；`ratio` median=**0.3365**）已 CONSUME：live `.ok` **`81521fb5`** 归档至 `_consumed/`；QUIET **`7fc1e7b7`**（holder=`leaf33_N_UNLOCK_POOL_DIAG`）已 lift。peak VmRSS=**5245088** / VmHWM=**5361952** KB **超** rss=1500MB 软顶，但探针**无 Exit94/95**、无 Traceback、无硬 Abort → 记 **PEAK_SOFT_EXCEEDED_NO_HARD_ABORT**。gate=300 **未降**；θ **仍未钉**（Arch **不自钉**）；正式脚本 **`afbbe7e7` UNCHANGED**；禁 RESTORED。下一跳交主择：(1) 钉 θ∈0.5–0.8 后另窗 FROZEN/新脚本/新 X2.ok；(2) 改路径；(3) HOLD。**≠X2 ACCEPT**。

## 1. 核盘 MATCH

| 件 | sha8 / 值 | 结果 |
|---|---|---|
| AI RUN_RECEIPT | `ee0ba09d` = `ee0ba09d4e8ef9cb1f454d933c7851b06bc28f660fd70445d828c550b2f302f1` | **MATCH** · DIAG DONE rc=**0** |
| RUNNING_ACK | `d8ee702a` = `d8ee702a57af6660b4e6a46e1c8c84f69808fc6937562940fa976e47e9607f40` | **MATCH** |
| summary | `de69554a` = `de69554a1d812e35fc5d3d923528f6c74ce91ed6fe1f6bccbbebfcff21d129f2` | **MATCH** |
| per_rebal | `86949aaa` = `86949aaa6f9e2806e4687f747efa98dee96a994fe24241d2752707de34bfb3c8` | **MATCH** |
| `.ok`（消费前 live） | `81521fb5` = `81521fb559370ae773807eb0bbb7c4bf17f992e2efe6307aa025a4530b43a4d9` | **MATCH** → 归档（内容字节不变） |
| QUIET（lift 前 live） | `7fc1e7b7` = `7fc1e7b7465b45f1f1a7f94d34dcb53584fa2160d5c47b556db2e25990cfb90d`；holder=`leaf33_N_UNLOCK_POOL_DIAG` | **MATCH** → lift |
| SIGNED | `a7c0bc2b` = `a7c0bc2b2cbb9576d7f52210edfe58ccfb30caad9c370e68b28a92bd736c5793` | **MATCH** |
| 诊断票只审 | `b037404a` = `b037404a22af0acd18135cdcb89cb7f9a4647c702a62039a28f8581e838f79cb` PASS_WITH_CONDITIONS | **MATCH** |
| 探针脚本 | `083d09fe` = `083d09feaf5cca609b8d18657685c8d42c0e75295af18532807ea7fb4ab6a746` | **MATCH · UNCHANGED** |
| 正式脚本 | `afbbe7e7` = `afbbe7e7292c17399bbf4733d9f34a922e6d81f1a914a60d24dc61fcba86cbc9` | **MATCH · UNCHANGED** |
| ET_TS / pid / rc | `20261027_082801` / `71737`（**DEAD**；pgrep 空） / **0** | **MATCH** |
| DRAFT / COVER / RECEIPT(票) | `6a22123d` / `92262b70` / `0fb1942d` | **MATCH**（上游） |
| 复议审 / VOID / RUN(ABORT) / alpha | `29166bf7` / `6826c01d` / `a1b426f5` / `ea17e173` | **MATCH**（上游旁证） |

## 2. 分布摘要（只报 · **θ 仍未钉**）

| 度量 | n | median | p10 | p25 | p75 | p90 | min | max |
|---|---|---|---|---|---|---|---|---|
| `n_unlock_pool` | 29 | **81.0** | 59.0 | 72.0 | 102.0 | 126.4 | 53.0 | 1907.0 |
| `n_alpha` | 29 | **30.0** | 16.8 | 25.0 | 35.0 | 41.4 | 15.0 | 72.0 |
| `ratio=n_alpha/n_unlock_pool` | 29 | **0.3365** | ≈0.262 | ≈0.317 | ≈0.395 | ≈0.429 | ≈0.0157 | ≈0.973 |

- 再平衡日数 n_rebal = **29**
- θ 讨论区间仍为 **0.5–0.8**（**等主钉**；本回执**不**建议、**不**自钉具体 θ）
- `coverage_median_hiliq_readonly=300`；`gate_changed=false`
- summary.`theta_self_decided=false` / `theta_undecided=true` MATCH
- kind=`DIAGNOSTIC_PROBE_NOT_FORMAL_ALPHA`；`x2_accept=false`；`promotion_approved=false`

## 3. peak_proof 专节 · **PEAK_SOFT_EXCEEDED_NO_HARD_ABORT**

| 项 | 值 |
|---|---|
| launch_pid | `71737`（**DEAD**） |
| sampler VmRSS peak | **5245088** KB ≈ **5122.16** MB |
| sampler VmHWM peak | **5361952** KB ≈ **5236.28** MB |
| rss 软/硬帽（签时钉） | **1500** MB = **1536000** KB（**未抬**） |
| VmRSS / 软顶 | 5245088 / 1536000 ≈ **3.415×** |
| VmHWM / 软顶 | 5361952 / 1536000 ≈ **3.491×** |
| over_soft_1500 | **true** |
| Exit 94/95 | **无** |
| Traceback / STOP/ABORT（硬） | **无** |
| 探针脚本硬 Abort 闸 | **无**（与正式 α Exit94/95 硬闸**不同**；本探针未实施硬 ABORT） |
| 本拍定性 | **PEAK_SOFT_EXCEEDED_NO_HARD_ABORT** |
| 说明 | rc=0 且分布产物齐全 → 仍可 **CONSUMED_PASS**；peak 超顶**必须如实披露**，供主择下一跳时一并考虑（另窗硬闸 / 改路径 / HOLD 等）。**本拍不降 gate、不抬 rss、不改脚本。** |

## 4. 归档 / lift

| 项 | 值 |
|---|---|
| `.ok` 归档 | `output/ai_factory/_consumed/ARCH_RUN_AUTH_LEAF33_N_UNLOCK_POOL_DIAG_v1.81521fb5.CONSUMED_PASS.20261027T0836ET.ok` |
| `.ok` 内容 sha8 / 全长 | **`81521fb5`** / `81521fb559370ae773807eb0bbb7c4bf17f992e2efe6307aa025a4530b43a4d9`（内容字节不变；**禁 RESTORED**） |
| QUIET lift | `output/loop/_lifted/RESEARCH_QUIET_leaf33_n_unlock_pool_diag_CONSUMED_PASS_LIFTED_20261027T0836ET.lock` |
| QUIET 原内容 sha8 / 全长 | **`7fc1e7b7`** / `7fc1e7b7465b45f1f1a7f94d34dcb53584fa2160d5c47b556db2e25990cfb90d`（可追溯） |
| lift 文件 sha8 / 全长 | **`05a73b8f`** / `05a73b8fda87b12f3397d3c5267aee0b2e8e2334dda3a0fd6a041181ebf69c6a`（尾加 `# ARCH_QUIET_LIFTED` 元数据） |
| live `.ok` | **ABSENT**（`ARCH_RUN_AUTH_LEAF33_N_UNLOCK_POOL_DIAG*` 空） |
| live QUIET | **ABSENT**（`output/loop/RESEARCH_QUIET.lock` 不存在） |

## 5. CONDITIONS / 下一跳（交主 · Arch **不自钉 θ**）

请主择其一：

1. **钉 θ∈0.5–0.8** 后另窗 FROZEN / 新脚本 / 新 X2 `.ok`（正式 α；须另签；本诊断 `.ok` **禁 RESTORED**）
2. **改路径**（含是否针对 peak 超软顶另设硬闸 / 探针改写 / 资源策略——由主定；Arch 本拍不改）
3. **HOLD**

硬约束（本拍与下一跳默认）：

- gate=**300** **不降**
- θ **Arch 不自钉**；等主钉
- 禁 RESTORED：本票内容 **`81521fb5`** + `245df63f`+`c5ed13df`+`5774bb6e`+二十票（forbid n=23）
- **≠X2 ACCEPT**；≠正式 α 本拍；≠selfcheck；≠Book-Smoke
- `0087c928` / 叶28/29 **另队**；**禁触 A18**
- 正式脚本 **`afbbe7e7` UNCHANGED**（本拍未改；下一跳若需改须另窗）

## 6. 非动作（本拍）

- **未**代跑诊断 / 正式 α
- **未**改探针脚本 `083d09fe` / 正式脚本 `afbbe7e7`
- **未**降 coverage gate=300
- **未**自钉 θ
- **未** RESTORED 任何禁票（含 `245df63f`/`c5ed13df`/`5774bb6e`）
- **未**触 A18
- **未**改 TEAM_STATE
- **未**签新 `.ok`
- **未** SendToUser / 不报 Leo

## 7. 钉表（速查）

| 钉 | sha8 |
|---|---|
| RUN_RECEIPT | `ee0ba09d` |
| RUNNING_ACK | `d8ee702a` |
| summary | `de69554a` |
| per_rebal | `86949aaa` |
| `.ok` 内容（归档） | `81521fb5` |
| QUIET 原内容 | `7fc1e7b7` |
| QUIET lift 文件 | `05a73b8f` |
| SIGNED | `a7c0bc2b` |
| 审（诊断票） | `b037404a` |
| 探针脚本 | `083d09fe` |
| 正式脚本 | `afbbe7e7` |

live=false · leo_notify=false · ≠X2 ACCEPT · θ_undecided=true · CONSUMED_PASS
