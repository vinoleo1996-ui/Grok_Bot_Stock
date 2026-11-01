# Arch 叶33 Share Unlock Pressure Resid · **HOLD 叶33 机制**

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-27T08:38:28-04:00`（America/New_York） |
| 主令 | 主改判 **(C) HOLD 叶33 机制**（诊断探针已实跑收口后改判；**非**仅 CONSUMED_PASS 后等主择 θ） |
| **结论** | **HOLD 叶33**（机制暂搁；不钉 θ；不降 gate；不开另窗 FROZEN；不派 Eng） |
| live / ≠X2 ACCEPT / ≠selfcheck / ≠Book-Smoke | **false** / **true** / **true** / **true** |
| leo_notify | **false** |

## 0. 一句话

叶33 A1 `n_unlock_pool` 诊断探针已 DONE（rc=0；RUN `ee0ba09d`）并完成归档/lift；主据分布 **ratio median=0.3365 ≪ 0.5** 改判 **HOLD 叶33 机制**——**不钉 θ**、**不降** gate=300、**不开**另窗 FROZEN、**不派 Eng**。peak VmRSS=**5245088** / VmHWM=**5361952** KB 超 rss=1500MB 软顶如实记（无 Exit94/95）。live `.ok`/QUIET **ABSENT**；归档已 **rename→HOLD**。正式脚本 `afbbe7e7` UNCHANGED；禁 RESTORED；**≠X2 ACCEPT**。

## 1. 主因（HOLD）

| 项 | 值 |
|---|---|
| ratio median | **0.3365**（p10≈0.262 / p90≈0.429） |
| 相对 θ 讨论下沿 0.5 | **0.3365 ≪ 0.5** |
| 主裁定 | **(C) HOLD 叶33 机制** |
| θ | **不钉**（区间 0.5–0.8 不再推进） |
| gate=300 | **不降** |
| 另窗 FROZEN / 新 X2.ok | **不开** |
| Eng | **不派** |

## 2. 钉表 MATCH

| 件 | sha8 | 全长 / 注 |
|---|---|---|
| AI RUN_RECEIPT | `ee0ba09d` | `ee0ba09d4e8ef9cb1f454d933c7851b06bc28f660fd70445d828c550b2f302f1` · rc=0 · pid `71737` DEAD |
| RUNNING_ACK | `d8ee702a` | `d8ee702a57af6660b4e6a46e1c8c84f69808fc6937562940fa976e47e9607f40` |
| summary | `de69554a` | `de69554a1d812e35fc5d3d923528f6c74ce91ed6fe1f6bccbbebfcff21d129f2` |
| per_rebal | `86949aaa` | `86949aaa6f9e2806e4687f747efa98dee96a994fe24241d2752707de34bfb3c8` |
| 探针脚本 | `083d09fe` | `083d09feaf5cca609b8d18657685c8d42c0e75295af18532807ea7fb4ab6a746` **UNCHANGED** |
| 正式脚本 | `afbbe7e7` | `afbbe7e7292c17399bbf4733d9f34a922e6d81f1a914a60d24dc61fcba86cbc9` **UNCHANGED** |
| 复议审 | `29166bf7` | 上游 A→A1 路径审 |
| VOID | `6826c01d` | 上游 X2 tz-align coverage VOID |
| SIGNED（探针 .ok） | `a7c0bc2b` | `a7c0bc2b2cbb9576d7f52210edfe58ccfb30caad9c370e68b28a92bd736c5793` |
| 原 `.ok` 内容 | `81521fb5` | `81521fb559370ae773807eb0bbb7c4bf17f992e2efe6307aa025a4530b43a4d9` |
| 原 QUIET 内容 | `7fc1e7b7` | `7fc1e7b7465b45f1f1a7f94d34dcb53584fa2160d5c47b556db2e25990cfb90d` · holder=`leaf33_N_UNLOCK_POOL_DIAG` |
| 诊断票只审 | `b037404a` | PASS_WITH_CONDITIONS（上游） |

## 3. 分布旁证（只报 · **不钉 θ**）

| 度量 | n | median | p10 | p90 |
|---|---|---|---|---|
| `n_unlock_pool` | 29 | **81.0** | 59.0 | 126.4 |
| `n_alpha` | 29 | **30.0** | 16.8 | 41.4 |
| `ratio` | 29 | **0.3365** | ≈0.262 | ≈0.429 |

## 4. peak_proof（如实）

| 项 | 值 |
|---|---|
| VmRSS peak | **5245088** KB ≈ 5122.16 MB |
| VmHWM peak | **5361952** KB ≈ 5236.28 MB |
| rss 软顶 | 1500 MB = 1536000 KB |
| 倍数 | RSS≈**3.415×** / HWM≈**3.491×** 软顶 |
| Exit 94/95 | **无** |
| 定性 | **PEAK_SOFT_EXCEEDED_NO_HARD_ABORT**（探针无硬 Abort 闸；非正式 α Exit94/95） |

## 5. 归档 / lift（HOLD rename）

| 项 | 值 |
|---|---|
| `.ok` 归档（HOLD） | `output/ai_factory/_consumed/ARCH_RUN_AUTH_LEAF33_N_UNLOCK_POOL_DIAG_v1.81521fb5.HOLD.DIAG_CONSUMED.20261027T0836ET.ok` |
| `.ok` 内容钉 | sha8=`81521fb5` 全长不变（**禁 RESTORED**） |
| 先前名 | `…81521fb5.CONSUMED_PASS.20261027T0836ET.ok` → 已 rename |
| QUIET lift（HOLD） | `output/loop/_lifted/RESEARCH_QUIET_leaf33_n_unlock_pool_diag_HOLD_DIAG_CONSUMED_LIFTED_20261027T0836ET.lock` |
| QUIET 原内容可追溯 | sha8=`7fc1e7b7` |
| lift 文件（HOLD 后）sha8 / 全长 | `ee5235e6` / `ee5235e67791edfb9a105e32a06312b4cfd34d3ec99cfd605b39f584b5242219` |
| live `.ok` | **ABSENT** |
| live QUIET | **ABSENT** |

## 6. 与先前 CONSUMED_PASS 回执关系

- 先前机械 CONSUME 回执：`docs/v2/audit/ARCH_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_N_UNLOCK_POOL_DIAG_CONSUMED_PASS_20261027_ZH.md`（sha8=`9d6796ab` / 全长 `9d6796abc5a579ccd46da307b2e0a8d79890103ed7d39ac2f03a015b2cdc7334`）记录 rc=0 归档动作与 peak 披露。
- **Arch 机制结论以本 HOLD 回执为准**（主改判 (C) HOLD 叶33；非“等主择 θ”悬置）。

## 7. 硬钉 / 非动作

- **未**降 gate=300
- **未**钉 θ
- **未**新签 `.ok`
- **未**代跑
- **未**改探针/正式脚本
- **未**开另窗 FROZEN
- **未**派 Eng
- **未**改 TEAM_STATE（交父）
- **未** RESTORED（含 `245df63f`+`c5ed13df`+`5774bb6e`+二十票；本票内容 `81521fb5` 亦禁 RESTORED）
- **≠X2 ACCEPT**；≠selfcheck；≠Book-Smoke；禁触 A18；`0087c928`/叶28/29 另队

live=false · leo_notify=false · **HOLD 叶33**
