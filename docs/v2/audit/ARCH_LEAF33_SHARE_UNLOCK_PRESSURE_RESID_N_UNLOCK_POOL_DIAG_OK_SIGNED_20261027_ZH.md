# Arch 叶33 A1 `n_unlock_pool` 诊断探针 · 独立 `.ok` 签发回执

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-27T08:22:48-04:00`（America/New_York） |
| 主令 | 主 ~08:15 ET priority · 叶33 A1 探针签窗 OPEN→SIGN（诊断票只审 `b037404a` PASS_WITH_CONDITIONS；钉诊断脚本 `083d09fe`；正式 `afbbe7e7` UNCHANGED；gate=300 不降；θ 不钉） |
| 诊断票只审 | `b037404a…` **PASS_WITH_CONDITIONS** |
| DRAFT / COVER / RECEIPT | `6a22123d…` / `92262b70…` / `0fb1942d…` |
| 复议审 / VOID / RUN / alpha | `29166bf7…` / `6826c01d…` / `a1b426f5…` / `ea17e173…` |
| live / promotion_approved / leo_notify | **false** / **false** / **false** |

## 结论

**SIGNED** — 叶33 A1 只读 `n_unlock_pool`/`n_alpha`/`ratio` **诊断探针**（mechanism=`g1g5_ashare_share_unlock_pressure_resid_v1`；kind=`research_leaf_diagnostic_probe`；**≠正式 α 构建**；**≠ X2 ACCEPT**；**≠ selfcheck**；**≠ Book-Smoke**）**新** `.ok` 已落盘：`output/ai_factory/ARCH_RUN_AUTH_LEAF33_N_UNLOCK_POOL_DIAG_v1.ok`。诊断脚本 **`083d09fe…` only**；正式脚本 **`afbbe7e7…` UNCHANGED**（禁改）；coverage gate=**300** 只读不降；θ **未钉 / 禁自决**。上游钉 MATCH：审 `b037404a` / DRAFT `6a22123d` / COVER `92262b70` / RECEIPT `0fb1942d` / 复议审 `29166bf7` / VOID `6826c01d` / RUN `a1b426f5` / alpha `ea17e173`。**禁 RESTORED** `245df63f`+`c5ed13df`+`5774bb6e`+二十票（**n=23**）。rss 软/硬帽 **1500** 禁抬；peak_proof **REQUIRED**。真跑须 `--allow-real-data` + `--arch-ok-path <NEW_OK>`；out=`output/ai_factory/_leaf33_share_unlock/diag_n_unlock_pool_v1/`。**Arch 不代跑**；QUIET **已挂且保留**供 AI prelaunch（本拍不 lift；holder=`leaf33_N_UNLOCK_POOL_DIAG`；reason=`leaf33_a1_n_unlock_pool_diag_probe_v1`）。`0087c928`/叶28/29 **另队不夹带**；**禁触 A18**。DIAG_EXECUTED@签=**false**；ALPHA_BUILD_EXECUTED@签=**false**。leo_notify=**false**。

## 钉点 MATCH 表

| 项 | 期望 | 实测 | 结果 |
|---|---|---|---|
| 诊断票只审 | `b037404a` PASS_WITH_CONDITIONS | `b037404a22af0acd18135cdcb89cb7f9a4647c702a62039a28f8581e838f79cb` | **MATCH** |
| DRAFT | `6a22123d…` | `6a22123dae4a36b5bc21e25a9f92091ccc0d297c50842b46dc6cbcabc3a557be` | **MATCH** |
| COVER | `92262b70…` | `92262b709f5a9244618b8d0c5f73ec242432bdf94871db568ca2cf6e08d79607` | **MATCH** |
| RECEIPT（AI） | `0fb1942d…` | `0fb1942d657f49df5d055952d8d86251a0a65b14232a42b33197fc12e5208dde` | **MATCH** |
| 诊断脚本 | `083d09fe…` only | `083d09feaf5cca609b8d18657685c8d42c0e75295af18532807ea7fb4ab6a746` | **MATCH** |
| 正式脚本 | `afbbe7e7…` UNCHANGED | `afbbe7e7292c17399bbf4733d9f34a922e6d81f1a914a60d24dc61fcba86cbc9` | **MATCH** |
| 复议审 | `29166bf7…` | `29166bf7ab27431b9240b0af5f1d182e52bffce21b65cc33bbf4ad2d8a89d4dc` | **MATCH** |
| VOID | `6826c01d…` | `6826c01d80383cb92eb97104b0525d3495054151e4360603eba9d82fe840ef92` | **MATCH** |
| RUN | `a1b426f5…` | `a1b426f53c2552370bc5e7f7a268ca8d7445f961cffacf375c8ba2f528cec092` | **MATCH** |
| alpha | `ea17e173…` | `ea17e173d4e7b5f4945c9a8930945fecf2bde78f3b22b63fa3c2e8b4f90ad69d` | **MATCH**（旁证；无新 alpha） |
| 拟 .ok 签前 | ABSENT（禁 RESTORED） | ABSENT | **MATCH** |
| QUIET 签前 | ABSENT | ABSENT | **MATCH** |
| 新 `.ok` sha8 ∉ forbid23 | ≠`245df63f`/`c5ed13df`/`5774bb6e` 且 ∉ 二十 | `81521fb5` ∉ forbid23 | **MATCH** |
| forbid 含三钉 | 含 `245df63f`+`c5ed13df`+`5774bb6e`；n=23 | n=23 且三钉在列 | **MATCH** |
| pgrep leaf33 | 空 | 空 | **MATCH** |
| 窗期 | ≥90min prelaunch → expires | `2026-10-27T08:22:00-04:00` → `2026-10-27T09:52:00-04:00` / expires `2026-10-27T09:56:00-04:00`；签时 `2026-10-27T08:22:48-04:00` | **IN_WINDOW** |

## 钉

| 项 | 值 |
|---|---|
| `.ok` 路径 | `output/ai_factory/ARCH_RUN_AUTH_LEAF33_N_UNLOCK_POOL_DIAG_v1.ok` |
| `.ok` sha8 / 全长 | `81521fb5` / `81521fb559370ae773807eb0bbb7c4bf17f992e2efe6307aa025a4530b43a4d9` |
| QUIET 路径 | `output/loop/RESEARCH_QUIET.lock` |
| QUIET sha8 / 全长 | `7fc1e7b7` / `7fc1e7b7465b45f1f1a7f94d34dcb53584fa2160d5c47b556db2e25990cfb90d` |
| 诊断脚本 | `research/leaf33_n_unlock_pool_diag_probe_v1.py` = `083d09feaf5cca609b8d18657685c8d42c0e75295af18532807ea7fb4ab6a746` |
| 正式脚本 | `research/leaf33_share_unlock_pressure_resid_alpha_build.py` = `afbbe7e7292c17399bbf4733d9f34a922e6d81f1a914a60d24dc61fcba86cbc9` **UNCHANGED** |
| 诊断票只审 | `b037404a22af0acd18135cdcb89cb7f9a4647c702a62039a28f8581e838f79cb` PASS_WITH_CONDITIONS |
| DRAFT / COVER / RECEIPT | `6a22123d…` / `92262b70…` / `0fb1942d…` |
| 复议审 / VOID / RUN / alpha | `29166bf7…` / `6826c01d…` / `a1b426f5…` / `ea17e173…` |
| kind / purpose | `research_leaf_diagnostic_probe` / `leaf33_A1_n_unlock_pool_diag_probe_v1_NOT_formal_alpha_NOT_x2_accept` |
| gate / θ | coverage_median_hiliq_readonly=**300**（禁降）；theta_undecided=**true**（禁自决） |
| 窗期 | `2026-10-27T08:22:00-04:00` → `2026-10-27T09:52:00-04:00`；expires `2026-10-27T09:56:00-04:00` |
| CLI dry | `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf33_n_unlock_pool_diag_probe_v1.py --dry-run` |
| CLI PRIMARY（诊断真跑） | `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf33_n_unlock_pool_diag_probe_v1.py --allow-real-data --arch-ok-path output/ai_factory/ARCH_RUN_AUTH_LEAF33_N_UNLOCK_POOL_DIAG_v1.ok --out output/ai_factory/_leaf33_share_unlock/diag_n_unlock_pool_v1/` |
| FALLBACK | **无**；峰＞1500 / 失败 / ABORT → Exit 94/95 停+上报（禁抬帽） |
| out | `output/ai_factory/_leaf33_share_unlock/diag_n_unlock_pool_v1/` |
| rss 软/硬帽 | **1500** MB；禁抬帽；硬 Exit **94/95** |
| peak_proof | **REQUIRED** |
| 禁 RESTORED | **23** 票：`245df63f,c5ed13df,5774bb6e,02426b73,4bb141c9,fdbaa512,aa25e989,7e239487,5af20222,5ae077fa,3c297052,e107383f,2be59acd,a7d98ac9,8e51de63,3a6caa4f,8bcd79dc,725be3e0,0f50daf7,3c19dd7d,1c32ab1e,6054b3bf,6de02e74`（含 `245df63f`+`c5ed13df`+`5774bb6e`） |
| Book-Smoke / X2 ACCEPT / selfcheck / 正式 α | **false** / **false** / **false** / **≠** |
| `0087c928` / 叶28/29 | 另队；**不在**本 `.ok` |
| MemAvailable@签 | 12228872 kB |
| DIAG_EXECUTED@签 / ALPHA_BUILD_EXECUTED@签 | **false** / **false** |

## QUIET / pgrep

| 项 | 值 |
|---|---|
| QUIET 挂时 | `2026-10-27T08:22:48-04:00` reason=`leaf33_a1_n_unlock_pool_diag_probe_v1` holder=`leaf33_N_UNLOCK_POOL_DIAG` |
| do_not_lift_until_arch_or_consumed | **true**（本拍不 lift） |
| neq_a18 | **true** |
| pgrep leaf33 | 空 |
| Arch 代跑 `--allow-real-data` | **未执行**（DIAG_EXECUTED=false） |

## 下一跳

1. **主** MATCH `.ok`+`QUIET`+本 SIGNED 后令 AI prelaunch **单次诊断探针**真跑（须在 expires 前；Arch **不代跑**）
2. AI 交诊断分布回执（`n_unlock_pool` / `n_alpha` / `ratio` 分位数 + peak_proof；峰＞1500→Exit 94/95 停）→ 主再钉 θ / 是否另窗 FROZEN
3. ≠正式 α；≠X2 ACCEPT；≠selfcheck；≠Book-Smoke；不解阻 `0087c928`/叶28/29；**≠A18**；不 RESTORED 23 票（含 `245df63f`/`c5ed13df`/`5774bb6e`）；不降 gate；θ 不自决；live=false；leo_notify=false

live=false.
