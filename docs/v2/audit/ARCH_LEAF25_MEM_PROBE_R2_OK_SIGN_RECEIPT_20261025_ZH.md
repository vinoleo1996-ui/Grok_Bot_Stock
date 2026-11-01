# Arch 叶25 mem_probe r2 实峰 probe `.ok` 签发回执

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-25T12:24:34-04:00`（America/New_York） |
| 主令 | 另审另签独立实峰 probe；对齐 (A) `14e9b6ba…` |
| 审阅 | `1b706f9b…` **PASS_WITH_CONDITIONS** |
| live / promotion_approved | **false** / **false** |

## 结论

**SIGNED** — 独立实峰 probe `.ok` 已落盘；**≠ X2.ok**；**Arch 不代跑**；X2 / NEED_MEM_PROBE **仍不解阻**，直至入窗实峰跑 PASS。

## 钉

| 项 | 值 |
|---|---|
| `.ok` 路径 | `output/ai_factory/ARCH_RUN_AUTH_LEAF25_MEM_PROBE_R2.ok` |
| `.ok` sha8 / 全长 | `cd230f9c` / `cd230f9c2aa9fc8de7fc538fb1f04ded8d9c20463f24b88b6c0f76950ec34279` |
| 脚本 | `research/leaf25_full_factor_mem_probe_r2.py` = `9dfe173a9104330287f6ebfe2f758c63891f3c92b5f9d112118b697898d50e0f` |
| wrapper v5 | `4240ce82f0929085ab4bcb37e2400a3414e70e162c9e697cf02d97103342f882` |
| 审阅 | `1b706f9b40054b69e4e25968f9a3d20ec530965a4dfaf3a61be7584d3296b0c7` PASS_WITH_CONDITIONS |
| COVER/CMD/DIFF | `4fa12c5a9876c2541bd062858a4e7464fea6e69650a75d53aade3d7342d5c92b` / `837078627aab3b93190607609ca3620c8b1d5decdabc62a866f53371836df74a` / `e0d9acdb973d80647fccd89aec8b27e59c2c1fd441a25aa87680a82629e1c6a8` |
| 拟短窗 | `2026-10-25T12:25:00-04:00` → `2026-10-25T13:05:00-04:00`；expires `2026-10-25T13:07:00-04:00`（Arch 提案；**请主确认/改排**） |
| CLI 核 | HI_LIQ · `--mode month` · `--start 2024-06-03 --end 2024-06-28 --chunk-id 0` · `--allow-real-data` |
| 帽 | C4/stop/hard **1331200/1484800/1536000**；阈 **1131520**；**禁抬帽** |
| 采样 | 仅 `/tmp/quantlab_*` |
| 禁复用 | `1c32ab1e5ffb9eb3ddf466f15b0cd778a1579eaca678f2f5fbe1dd1ae00e66f0`；禁 r1 dry；禁 X2/密封同张 |
| 披露 | dry_run=false；float32；densify=false；claims_full_cfacc=false；alpha_kind=crude_accrual_cs_zscore_probe_only；peak_kb |
| QUIET | 已挂锁留给 AI prelaunch（未 lift） |

## 预检旁证

`ARCH_LEAF25_MEM_PROBE_R2_PREOK_EVIDENCE_20261025_ZH.md` sha `cdb8c1b784b595be280ea9de01500878b302b54c0c874a9736e3715986ecc2ed`

## 下一跳

1. **主**确认/改排短窗后令 AI prelaunch 开跑  
2. AI 交实峰回执（peak_kb 等）→ Arch 核 → 才解阻 X2 内存键  
3. Arch 不代跑
