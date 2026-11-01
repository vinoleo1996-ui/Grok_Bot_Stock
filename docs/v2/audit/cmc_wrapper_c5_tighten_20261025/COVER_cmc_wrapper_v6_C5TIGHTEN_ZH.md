# COVER：cmc_wrapper v6 C5TIGHTEN（侧稿，未钉）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Eng |
| 时刻 | `2026-10-25T13:00:00-04:00`（America/New_York） |
| 基线钉 | `docs/v2/audit/cmc_v1_1_leaf24/cmc_wrapper_v5_4240ce82.sh` sha256 **`4240ce82f0929085ab4bcb37e2400a3414e70e162c9e697cf02d97103342f882`**（前缀 `4240ce82`，**未改动**） |
| Arch 裁定 | `docs/v2/audit/ARCH_LEAF25_MEM_PROBE_R3_FAIL_C5_VOID_RULE_20261025_ZH.md` sha **`43fe482e462bb6e3f3c64c687f8dcda9693cbb7849d67593f23f9653f780b0ce`** |
| 侧稿 | `cmc_wrapper_v6_C5TIGHTEN.draft.sh`（本目录） |
| DIFF | `DIFF_cmc_wrapper_v5_to_v6_C5TIGHTEN.diff` |
| live / promotion | **false** / **false** |

## 1. 变更面（仅 wrapper C5 监视 + 子进程日志落点）

| 杠杆 | 内容 | 触及文件 |
|---|---|---|
| **A** 本跑白名单 | `c5watch` 在把 cwd/fd 记为 hit 前：若目标 `readlink -f` ∈ 本跑 `--logdir`/`--outdir` 绝对前缀 → `C5_SKIP own_logdir/outdir`（写 sampler，**不** kill） | 侧稿 `c5_under_own` + `c5watch` |
| **B** 良性 cmdline | hit 后若 cmdline（nul→空格）仅为 `sleep`/`true`/裸 `cat`（及常见绝对路径变体）→ `C5_SKIP benign_cmd`；含 `python`/`research`/`scripts`/`scripts_eng`/`-m quantlab`/`data*`/`output*` **永不** skip | 侧稿 `c5_benign_cmd` |
| **C** stdout→/tmp | `setsid` 重定向落到 `/tmp/quantlab_wrapper_logs/${TAG}.log`；`$L/${TAG}.log` 为指向该文件的 symlink；exit/c5/ps/marker 仍在 `$L`；sampler 仍强制 `/tmp` | 侧稿 LOGTMP + `ln -sfn` |

**未改**：C4 限 1331200、STOP/HARD、guard 默认-on、PGID 校验、cmdline assert、`--c5-ignore` **refuse-91**（实跑无 `allow_c5_ignore=true`）、void 归档逻辑、默认 ASSERT、sampler 禁 output*/data*。

**未改生产钉**：v5 文件字节不动；本包为 **SIDE DRAFT**，等 Arch 审 + 新 pin 后方可替换。

## 2. 风险

| 风险 | 缓解 / 残留 |
|---|---|
| A 过宽：本跑 outdir 下真并发读者被 skip | B 不覆盖 python/research；maps/cmd 命中仍杀；仅 cwd/fd 路径白名单 |
| B 过宽：恶意伪装 `sleep` 实为包装 | 仅匹配良性 argv 前缀；嵌 python/路径即 return 1 |
| C：AI/脚本硬读 `$L/${TAG}.log` 当普通文件 | symlink 对 grep/cat/peak 抽取透明；sampler 记 `WRAPPER_STDOUT_LOG … -> /tmp/…` |
| C：/tmp 清理丢日志 | 与 sampler 同策略；exit/c5 证据仍在 `$L` |
| 误以为可开 `--c5-ignore` 实跑 | **硬禁**；refuse-91 与 v5 同文；本 COVER/回执明示 |

## 3. 自测点（合成 only；禁对真实 leaf 跑）

1. **假阳性回归**：无关 `sleep 0.2` 持 fd→本跑 `$L`/`$OD` 下日志 → sampler 见 `C5_SKIP`，子进程 **不被** kill，rc≠96。
2. **真阳性保留**：异 PGID 的 `python` 打开 `/workspace/QuantLab/data/…` 或 cmdline 含 `research/` → 仍 `C5_HIT` + killgrp → rc=96。
3. **refuse-91**：带 `--arch-ok` 实跑形参 + `--c5-ignore` 且 `.ok` 无 `allow_c5_ignore=true` → rc=91，`launched=0`。
4. **杠杆 C**：`$L/${TAG}.log` 为 symlink → `/tmp/quantlab_wrapper_logs/…`；peak 字段仍可从 `$LOG` 解析。

辅助：`selftest_c5_tighten_synthetic.sh`（本目录；**勿**接 leaf25/27）。

## 4. 明确禁项 / 排窗

- **禁**实跑开 `--c5-ignore`；禁把本侧稿当已钉生产；禁消费 VOID `c5e54085…`。
- **禁**本 DIFF 解阻 X2；X2 仍挡至实峰 probe **PASS**（另签新 `.ok`）。
- **错开叶27**：**14:00–14:45 ET**（America/New_York）勿挤同一窗实跑/签票。
- AI r3b / 新 pin：**另审另签**；Eng 本包只交 DIFF+COVER+回执，**不**跑叶探针、**不**消费 `.ok`、**不**改 TEAM_STATE。

## 5. 本包指纹

见同目录 `SHA256SUMS.txt`。

live=false；promotion_approved=false。
