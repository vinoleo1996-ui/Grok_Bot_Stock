# Arch 裁定：叶25 mem_probe r3 FAIL rc=96（C5 误杀）→ VOID + r3b 路径

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-25T12:57:50-04:00`（America/New_York） |
| AI 回执 | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_MEM_PROBE_R3_RUN_RECEIPT_20261025_ZH.md` sha **`04552c3c83e3f2084ddeab35b6075f665536fdf4dc22b8952f6de01790e3e5f2`** |
| 原 `.ok` 票 | `c5e540855bc836b97b7395a53dd63a6d3c295860fdd11e72e77abd6cf3152011`（sha8 `c5e54085`） |
| 归档 | `output/ai_factory/_consumed/ARCH_RUN_AUTH_LEAF25_MEM_PROBE_R3.c5e54085.VOID.FAIL_C5.20261025T1257ET.ok`（归档文件 sha `3447df722157b82d74d66e659cb551bb76381b5f084683cc56a4a4da7a7b12f8`；**禁**当授权复用） |
| live / promotion | **false** / **false** |

## 1. 结论枚举

| 字段 | 值 |
|---|---|
| **裁定** | **VOID_FAIL_C5_FALSE_POSITIVE** |
| 滤子 Timestamp 修 | **已验证 exercised**（三 PIT 加载；非 r2 FAIL_TYPE） |
| RSS / C4 | **PASS**（peak_kb=**359224** ≪ 1331200；非 94/95） |
| C5 | **误杀**（命中无关 `sleep 0.2` + fd→本票 `wrapper_stdout.log`） |
| 是否解阻 X2 | **否**（未完成 real_peak） |
| 是否抬帽 | **否** |
| 是否 `allow_c5_ignore` 实跑 | **否**（wrapper 硬拒 real run） |
| AI 重试本票 | **禁**（`ai_no_retry`；禁消费 `c5e54085`） |

## 2. 旁证（盘）

- `WRAPPER_DONE … rc=96 … peak_kb=359224 C4=PASS`
- `leaf25_mem_probe_r3_c5.txt`：`C5_HIT pid=1005722 pgid=839980 fd:…/wrapper_stdout.log cmd=sleep 0.2`
- 阶段日志已过 `pit_*_loaded` 与 `cs_day_20240607` RSS_CHECK
- 进程现盘：**空**；`.ok` live 路径：**已空**；QUIET：**已 lift**

## 3. C5 根因（wrapper v5 `4240ce82`）

`c5watch`（约 L63–73）对**非本树**进程扫描：`cwd`/`fd`/`maps`/`cmdline` 触及 `/workspace/QuantLab/output*` 或 `research/*` 即 `killgrp`。

本票：某 `sleep 0.2`（pgid≠probe）持有指向本跑 `wrapper_stdout.log`（位于 `output/ai_factory/…`）的 fd → 触发 C5 → 杀掉研究 PGID。

**判定**：该 `sleep` **不是**并发研究读者（无 python/research/data 读）；属监视面 **false positive**。与 peak≪C4、滤子已过一致。

## 4. 下一跳（r3b / 监视修）

1. **Eng（或 AI 交 DIFF）**：wrapper C5 收紧——至少下列之一（须另审另签，**禁**实跑开 `--c5-ignore`）：
   - 忽略 `cmdline` 仅为 `sleep`/`true`/`cat` 等无数据读者；**或**
   - 忽略 fd 目标 ∈ **本跑** `--logdir` / `--outdir` 白名单；**或**
   - 启动包装把 `wrapper_stdout` 落到 `/tmp/quantlab_*`（与 sampler 同策略），避免 output 路径被路过进程继承。
2. **AI**：交 r3b 包（脚本可 UNCHANGED `8da4f2e6` 若仅 wrapper/启动侧修；若只改启动重定向亦须 COVER+CMD+DIFF）→ Arch 另审 → **另签新** probe `.ok`（禁复用 `c5e54085`/`cd230f9c`/`1c32ab1e`）。
3. **排窗**：错开叶27 **14:00–14:45 ET**；本 VOID 后 QUIET 已 lift，叶27 例程可按计划签。
4. **X2**：仍挡至实峰 probe **跑通 PASS**。

## 5. 明确禁项

- 禁复用 VOID `c5e54085…` / 归档变体当授权
- 禁抬 C4/stop/hard；禁 `--c5-ignore` 上实峰
- 禁把本 FAIL 报为 real_peak PASS；禁申 X2
- Arch 不代跑

live=false；promotion_approved=false。
