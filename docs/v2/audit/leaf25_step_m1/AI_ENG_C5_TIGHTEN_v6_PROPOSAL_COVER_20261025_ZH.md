# AI→Eng 提案 COVER：wrapper C5 收紧 v6（叶25 mem_probe r3b 前置）

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI（提案方；**Eng 拥有 wrapper 并主导采纳/改写**） |
| 写成时刻 | `2026-10-25 13:04:48 ET`（America/New_York） |
| 基盘 | `docs/v2/audit/cmc_v1_1_leaf24/cmc_wrapper_v5_4240ce82.sh` sha **`4240ce82f0929085ab4bcb37e2400a3414e70e162c9e697cf02d97103342f882`**（sha8 `4240ce82`） |
| Arch 裁定 | `docs/v2/audit/ARCH_LEAF25_MEM_PROBE_R3_FAIL_C5_VOID_RULE_20261025_ZH.md` sha **`43fe482e462bb6e3f3c64c687f8dcda9693cbb7849d67593f23f9653f780b0ce`**（sha8 `43fe482e`；裁定 **VOID_FAIL_C5_FALSE_POSITIVE**） |
| r3 回执 | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_MEM_PROBE_R3_RUN_RECEIPT_20261025_ZH.md` sha **`04552c3c83e3f2084ddeab35b6075f665536fdf4dc22b8952f6de01790e3e5f2`**（sha8 `04552c3c`） |
| 本提案 DRAFT | `docs/v2/audit/leaf25_step_m1/cmc_wrapper_v6_c5_tighten_DRAFT.sh` sha **`e03a61b6e706c0b49765cc117a1e4d915fd2924170c281aa5d805d5a716b3cb0`** |
| 本提案 DIFF | `docs/v2/audit/leaf25_step_m1/DIFF_cmc_wrapper_v5_to_v6_c5_tighten.diff` sha **`96e139e4875f9b71f02a382c734f5a4cc37d2a92050be78e903987edb6835ae5`** |
| live / promotion | **false** / **false** |
| 状态 | **PROPOSAL_ONLY** — Eng 未签字前 **禁** 实跑；**非** `.ok`；**非** 申请签票 |

## 1. 根因（已裁定，勿争论）

r3 `WRAPPER_DONE … rc=96` · `peak_kb=359224` · `C4=PASS`。  
`leaf25_mem_probe_r3_c5.txt`：

```text
C5_HIT pid=1005722 pgid=839980 fd:…/_logs/wrapper_stdout.log cmd=sleep 0.2
```

v5 `c5watch`（约 L63–73）对**非本树**进程扫 `cwd`/`fd`/`maps`/`cmdline`：凡触及 `/workspace/QuantLab/output*` 或 `data*` 即 `killgrp`。  
无关 `sleep 0.2`（pgid≠probe）持有指向**本跑** `logdir/wrapper_stdout.log` 的 fd → **误杀**研究 PGID。  
滤子修已 exercised；peak≪C4；**非**抬帽议题；**禁** `--c5-ignore` 实跑解法。

说明：`wrapper_stdout.log` 由**外层 CMD** 重定向产生（不在 v5 脚本内）；v5 内 `LOG="$L/${TAG}.log"` 亦落在 research logdir（同属 `output*`），同类风险并存。本提案三点同时处理监视面与落盘面。

## 2. 三点改动（Arch 要求；均已落入 DIFF）

| # | Arch 要求 | 提案落点（DRAFT） | DIFF 核对 |
|---|---|---|---|
| **(1)** 忽略纯 sleep | `is_pure_sleep`：argv0 basename=`sleep`；至多一个纯数字时长 argv；无第三 argv。`python … sleep` / `bash -c 'sleep…'` / 多参 **不**跳过 | `c5watch` 在 pgid 跳过后、cwd/fd 扫描前 `continue` | ✅ `is_pure_sleep` + 调用点 |
| **(2)** 本跑 logdir fd 白名单 | `LABS=readlink -f "$L"`；cwd/fd 命中 `output*`/`data*` 时，若 path ∈ `$LABS` 或 `$LABS/*` → **不计** C5；仍拦其它 `output*`/`data*` | cwd 与 fd 两支均加白名单分支 | ✅ `LABS` / `C5_LOGDIR_WHITELIST` / case 白名单 |
| **(3)** wrapper stdout→/tmp | `WLOGDIR=/tmp/quantlab_wrapper_${TAG}`；`LOG=$WLOGDIR/${TAG}.log`；`setsid … >"$LOG"`；`$L/${TAG}_stdout.path` 指针；exit/c5/ps_*/marker **仍在** `--logdir` | 替换原 `LOG="$L/${TAG}.log"` | ✅ `WLOGDIR` / `WRAPPER_STDOUT_PATH` |

**保持不变（非目标）**

- C4 / STOP / HARD 阈值与 peak 合成（含 ru_maxrss、排除 VmPeak）
- sampler **必须** `/tmp`；硬拒 `output*`/`data*`
- `--c5-ignore` 实跑拒绝（无 `allow_c5_ignore=true` → rc=91）
- guard / PGID_MISMATCH / cmdline assert / void-on-fail 语义
- maps / python-research cmdline 命中逻辑（真并发读者仍杀）

## 3. 非目标 / 禁项

- **禁** 将本 DRAFT 直接用于实峰 / r3b 开跑（须 Eng 采纳或改写 → 另审另签新 `.ok`）
- **禁** `--c5-ignore` / `allow_c5_ignore` 作实跑解法
- **禁** 抬 C4/stop/hard；**禁** 申 X2；**禁** 复用 VOID `c5e54085`
- **禁** 同票重跑；叶27 @14:00 ET **不抢**
- **禁** 本提案改 git / 申请 `.ok` / 开跑
- 不在此提案扩展忽略 `true` / `false` / `cat`（Arch VOID 文可选；留给 Eng）
- 不在此提案白名单 `--outdir`（`$OD`）（Arch 文曾提 logdir/或 outdir；本提案按主令只钉 `$L`；Eng 可加）

## 4. 外层 CMD 配合（r3b 包另交）

v6 只把**子进程** stdout/stderr 迁到 `/tmp/quantlab_wrapper_<tag>/`。  
r3 误杀文件名是外层 `wrapper_stdout.log`（落在 `$LOGDIR`）。r3b CMD **必须**：

- 外层重定向改为 `/tmp/quantlab_wrapper_<tag>/wrapper_stdout.log`（及 stderr 同策略），**禁**再写 `$LOGDIR/wrapper_stdout.log`
- 或依赖 (1)+(2) 兜底（即便误落 logdir，纯 sleep + 白名单不再杀）——仍建议迁 /tmp，与 Arch (3) 一致

本 COVER **不**附 r3b CMD（另票）；Eng 签字 wrapper 后 AI 再交 r3b 包。

## 5. 验收（Eng / Arch 合成时可对）

| 检项 | 期望 |
|---|---|
| `bash -n` DRAFT | **OK**（AI 本回合已跑） |
| `sha256sum` v5 基盘 | `4240ce82f0929085ab4bcb37e2400a3414e70e162c9e697cf02d97103342f882` |
| DIFF 相对 v5 可对照到 DRAFT（或 Eng 改写等价） | 三点均在 |
| 合成自测（Eng）：人造「旁路 `sleep 0.2` + fd→本跑 logdir 文件」 | **不**触发 rc=96 |
| 合成自测：旁路 `python … research/…` 或 fd→**其它** `output/*` | 仍 C5 / rc=96 |
| 合成自测：`--c5-ignore` + 真 `.ok` 无 allow | 仍 rc=91 |
| sampler 默认/显式仍拒 `output*` | 仍 rc=2 |
| 实跑 | **本提案不做**；待 Eng 签字 + Arch 新 `.ok` + 主排窗（错开叶27） |

## 6. 与 Eng 分工

| 方 | 职责 |
|---|---|
| **AI（本文件）** | 只交 COVER + DIFF + DRAFT；停在提案；不申签；不开跑 |
| **Eng** | 拥有 wrapper；审 DIFF、采纳或改写（可重命名去 DRAFT、钉最终 sha、补 outdir 白名单 / true|cat 等）；合成自测；回 Arch |
| **Arch** | 审 Eng 终稿；另签 r3b / wrapper 相关授权；**禁**复用 `c5e54085` |
| **主** | 排 r3b 短窗（错开叶27 14:00–14:45 ET） |

## 7. 不确定点（留给 Eng）

1. **`$OD` 白名单**：是否与 `$L` 一并豁免？本提案未加（防 outdir 被真读者挂住时漏杀；若 Eng 判断 probe 只会写本票 out，可加）。
2. **忽略集合**：是否扩展 `true` / `false` / `cat`（无参或只读本跑 log）？本提案仅 `sleep`。
3. **`/usr/bin/sleep` vs `sleep`**：本提案用 basename，路径前缀版会跳过；若需更严（仅无路径 `sleep`）可改。
4. **外层 wrapper stdout**：是否由 wrapper 自身 `exec` 重定向到 `$WLOGDIR/wrapper_own_stdout.log` 强制接管（避免 CMD 漏改）？本提案未 `exec`，仅迁子进程 `LOG` + 指针文件；强制接管会影响调用方捕获 `WRAPPER_DONE` 的习惯。
5. **`WLOGDIR` 命名**：现用 `/tmp/quantlab_wrapper_${TAG}`（无时间戳）。多跑同 tag 会覆写 stdout；若需并存可加时间戳或 `$$`。
6. **指针文件** `$L/${TAG}_stdout.path`：是否保留 / 改 symlink / 删——Eng 定。
7. **热路径开销**：`is_pure_sleep` 每轮每进程读 cmdline；0.5s 周期下可接受，Eng 可改用 `/proc/pid/comm` 快筛再精读。

## 8. 钉核表（本回合产物）

| 文件 | sha256 |
|---|---|
| `cmc_wrapper_v5_4240ce82.sh`（基盘，只读） | `4240ce82f0929085ab4bcb37e2400a3414e70e162c9e697cf02d97103342f882` |
| `cmc_wrapper_v6_c5_tighten_DRAFT.sh` | `e03a61b6e706c0b49765cc117a1e4d915fd2924170c281aa5d805d5a716b3cb0` |
| `DIFF_cmc_wrapper_v5_to_v6_c5_tighten.diff` | `96e139e4875f9b71f02a382c734f5a4cc37d2a92050be78e903987edb6835ae5` |
| Arch VOID 裁定 | `43fe482e462bb6e3f3c64c687f8dcda9693cbb7849d67593f23f9653f780b0ce` |
| r3 回执 | `04552c3c83e3f2084ddeab35b6075f665536fdf4dc22b8952f6de01790e3e5f2` |

`bash -n` DRAFT：**OK**

live=false；promotion_approved=false；**ai_no_retry** 对本 VOID 票仍有效；本文件不构成开跑授权。

---

**本 COVER sha256（上文至「不构成开跑授权。」，不含本脚注）**：`2961c868a3c33abdf1f1ea270a9497f385a9836cb88a32e45e1aabfb2b9cdf91`

父 agent / Eng 请以盘上 `sha256sum` 全文件为准（含脚注则不同）。
