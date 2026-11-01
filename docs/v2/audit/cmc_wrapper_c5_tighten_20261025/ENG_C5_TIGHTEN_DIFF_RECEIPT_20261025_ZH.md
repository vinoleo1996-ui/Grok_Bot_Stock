# Eng 回执：C5 收紧 DIFF（v5→v6 侧稿）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Eng |
| 时刻 | `2026-10-25T13:00:00-04:00`（America/New_York） |
| Arch 裁定 | `docs/v2/audit/ARCH_LEAF25_MEM_PROBE_R3_FAIL_C5_VOID_RULE_20261025_ZH.md` sha256 **`43fe482e462bb6e3f3c64c687f8dcda9693cbb7849d67593f23f9653f780b0ce`**（前缀 `43fe482e`） |
| 基线 v5 | `docs/v2/audit/cmc_v1_1_leaf24/cmc_wrapper_v5_4240ce82.sh` sha256 **`4240ce82f0929085ab4bcb37e2400a3414e70e162c9e697cf02d97103342f882`**（交付前后均为此值，**未覆写**） |
| 目录 | `docs/v2/audit/cmc_wrapper_c5_tighten_20261025/` |
| COVER | `COVER_cmc_wrapper_v6_C5TIGHTEN_ZH.md` |
| live | **false** |

## 1. 根因（一段）

叶25 mem_probe r3 在 peak_kb=359224（C4=PASS）时被 wrapper v5 `c5watch` 以 rc=96 误杀：异 PGID 的无关 `sleep 0.2` 继承/持有指向本跑 `output/…/wrapper_stdout.log`（位于 `/workspace/QuantLab/output*`）的 fd，触发「fd→output* → killgrp」。该 sleep **不是**并发研究读者；属监视面 false positive（Arch：`VOID_FAIL_C5_FALSE_POSITIVE`）。收紧须在**不**开放实跑 `--c5-ignore` 的前提下，排除本跑日志白名单与良性短命令，并把 setsid 日志默认挪出 output*。

## 2. 改了什么（A/B/C 全做）

| 杠杆 | 实现要点 |
|---|---|
| **A** | 启动时 `LABS`/`ODABS`=`readlink -f`（失败则 abspath）本跑 `--logdir`/`--outdir`；cwd/fd 命中 output*|data* 前若 `_abs(目标)` 前缀属于 LABS/ODABS → `C5_SKIP own_logdir/outdir` |
| **B** | `c5_benign_cmd`：仅 `sleep`/`true`/裸 `cat`（含 /bin /usr/bin）；任何 python/research/scripts/quantlab/data|output 读者 → 不 skip；skip 时 `C5_SKIP benign_cmd` |
| **C** | `/tmp/quantlab_wrapper_logs/${TAG}.log` 为 setsid 实际落点；`$L/${TAG}.log`=`ln -sfn`；sampler 记 `WRAPPER_STDOUT_LOG`；exit/c5/ps/marker 仍在 `$L` |

其余 C4/STOP/guard/PGID/assert/`--c5-ignore` refuse-91 与 v5 **同语义**。

## 3. 交付物

| 文件 | 用途 |
|---|---|
| `cmc_wrapper_v6_C5TIGHTEN.draft.sh` | 侧稿（禁当生产钉） |
| `DIFF_cmc_wrapper_v5_to_v6_C5TIGHTEN.diff` | `diff -u` v5→侧稿 |
| `COVER_cmc_wrapper_v6_C5TIGHTEN_ZH.md` | 变更面/风险/自测/禁项/排窗 |
| `selftest_c5_tighten_synthetic.sh` | 合成自测草图（**未**对 leaf 执行） |
| `SHA256SUMS.txt` | 本包指纹 |
| 本回执 | Eng 落盘 |

## 4. 明确声明

- **禁**实跑开 `--c5-ignore`；await **Arch review + 新 pin**；AI r3b **另包另签**（禁复用 `c5e54085`）。
- 本包 **不解阻 X2**；**不**跑叶探针；**不**消费 `.ok`；**不**改 TEAM_STATE。
- 排窗：错开叶27 **14:00–14:45 ET**。

## 5. 自测草图（如何证明）

1. 合成：wrapper `--selftest --no-guard`（需 allow 或 synthetic 路径按 v5 规）跑长 `sleep 30` 为子进程；另起 `sleep 0.2` 并持本跑 `$OD`/`$L` 下文件 fd → 期望 sampler 出现 `C5_SKIP`，子进程存活至自然结束，**无** `C5_HIT`/rc=96。
2. 合成真阳性：异 PGID `python3` 打开 `/workspace/QuantLab/data/…` 或 cmdline 含 `research/` → 期望 `C5_HIT` + rc=96。
3. refuse-91：`--arch-ok` 无 `allow_c5_ignore=true` + `--c5-ignore <pid>` → rc=91。

详见同目录 `selftest_c5_tighten_synthetic.sh`（草图；Eng **未**在本窗对真实 leaf 执行）。

## 6. sha256

见同目录 `SHA256SUMS.txt`（侧稿/DIFF/COVER/回执/自测草图 + 未改 v5）。本文不内嵌自哈希以免循环。

live=false；promotion_approved=false。
