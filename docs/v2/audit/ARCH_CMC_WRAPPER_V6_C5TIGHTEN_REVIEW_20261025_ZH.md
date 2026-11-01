# Arch 审阅：cmc_wrapper v6 C5TIGHTEN（Eng 主包）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器落盘） |
| 时刻 | `2026-10-25T13:06:31-04:00`（America/New_York） |
| 对照裁定 | `docs/v2/audit/ARCH_LEAF25_MEM_PROBE_R3_FAIL_C5_VOID_RULE_20261025_ZH.md` sha256 **`43fe482e462bb6e3f3c64c687f8dcda9693cbb7849d67593f23f9653f780b0ce`**（sha8 **`43fe482e`**） |
| 基线 live wrapper | `docs/v2/audit/cmc_v1_1_leaf24/cmc_wrapper_v5_4240ce82.sh` sha256 **`4240ce82f0929085ab4bcb37e2400a3414e70e162c9e697cf02d97103342f882`**（sha8 **`4240ce82`**；审阅前后**未改动**） |
| Eng 主包目录 | `docs/v2/audit/cmc_wrapper_c5_tighten_20261025/` |
| AI 并行草案（对照） | `docs/v2/audit/leaf25_step_m1/cmc_wrapper_v6_c5_tighten_DRAFT.sh` + `DIFF_cmc_wrapper_v5_to_v6_c5_tighten.diff` |
| live / promotion | **false** / **false** |

## 1. 结论枚举

| 字段 | 值 |
|---|---|
| **裁定** | **PASS_WITH_CONDITIONS** |
| 主包 | **Eng** `cmc_wrapper_c5_tighten_20261025/`（以本包为准） |
| AI 并行包是否等价 | **否**（语义/实现不等价；**勿混签**；仅作对照） |
| 对照 43fe482e 最低杠（A∨B∨C） | **满足且超额**：Eng 同时实现 **A+B+C** |
| C4/STOP/HARD 是否抬帽 | **否**（与 v5 同：C4=1331200、STOP=1484800、HARD=1536000、DT=0.2） |
| 实跑 `--c5-ignore` | **仍硬拒**（合成测 refuse **rc=91**，`launched=0`） |
| 是否解阻 X2 | **否** |
| 是否可并入 r3b | **可**——须满足 §6 条件后 **另审另签** 新 probe `.ok`（禁复用 `c5e54085`） |
| 主干 live wrapper | **未改**（仍钉 v5 `4240ce82`） |

## 2. 包指纹（Eng 主包）

| 文件 | sha256 | sha8 |
|---|---|---|
| `cmc_wrapper_v6_C5TIGHTEN.draft.sh` | `b1208d3c075b0ea06ba9a484d8a42833f3efb223defbada02d135dfe624f88d5` | `b1208d3c` |
| `DIFF_cmc_wrapper_v5_to_v6_C5TIGHTEN.diff` | `a3a228a95bc76d2372f928c23da73e15dcaa25f0b7de58d421f3b2235c9aefac` | `a3a228a9` |
| `COVER_cmc_wrapper_v6_C5TIGHTEN_ZH.md` | `6339f298e249b1aee97983f3859d22831a025bf34638ef9e73ff6167d5d7bd34` | `6339f298` |
| `ENG_C5_TIGHTEN_DIFF_RECEIPT_20261025_ZH.md` | `dabe75ec6c289bf12895b810c45bd897c916dbcd6161e77c21bb9137c9e72da9` | `dabe75ec` |
| `selftest_c5_tighten_synthetic.sh` | `38ecef7839401c81c5b84d75f992ec13fde0badef6f81f9a461e75ee06bc36bf` | `38ecef78` |
| `SHA256SUMS.txt` | `a6a5197d5b152dd2889a8d5fc00f8211f07c46e0581673ee311603ad56f1c524` | `a6a5197d` |
| 基线 v5（未改） | `4240ce82f0929085ab4bcb37e2400a3414e70e162c9e697cf02d97103342f882` | `4240ce82` |
| 对照裁定 | `43fe482e462bb6e3f3c64c687f8dcda9693cbb7849d67593f23f9653f780b0ce` | `43fe482e` |

与包内 `SHA256SUMS.txt` 对 draft/DIFF/COVER/receipt/selftest/v5：**一致**。

## 3. DIFF 还原核验

- 在隔离临时树对 v5 施加 Eng DIFF（`patch -p0`）：补丁成功；补丁后内容与 `cmc_wrapper_v6_C5TIGHTEN.draft.sh` **字节一致**（sha `b1208d3c`）。
- 说明：DIFF 头为 `--- v5` / `+++ draft` 路径；`patch` 就地改存在的 `---` 文件，语义仍是 **v5→本 draft**。
- AI DIFF 对 AI draft 同样可还原（字节一致），但 **≠ Eng draft**（见 §5）。

## 4. 对照 43fe482e 验收表

| 验收条（裁定原文） | Eng 主包 | 结果 |
|---|---|---|
| 根因：`sleep 0.2` 持 fd→本跑 `…_logs/wrapper_stdout.log`（output* 下） | r3 回执路径：`output/ai_factory/_leaf25_mem_probe_r3/20261025_125124_logs/wrapper_stdout.log`（属 **本跑 logdir**） | 对照成立 |
| 杠杆：忽略 cmdline 仅为 sleep/true/cat 等无数据读者 | **B** `c5_benign_cmd`（sleep/true/裸 cat；python/research/scripts/quantlab/data|output **永不** skip） | **PASS** |
| 杠杆：忽略 fd∈本跑 `--logdir`/`--outdir` 白名单 | **A** `c5_under_own`：LABS+**ODABS** 前缀 | **PASS**（且含 outdir，贴合裁定字面） |
| 杠杆：wrapper_stdout→`/tmp/quantlab_*` | **C**：setsid 落 `/tmp/quantlab_wrapper_logs/${TAG}.log`；`$L/${TAG}.log` 为 symlink | **PASS**（注：外层 CMD 另写的 `wrapper_stdout.log` 不靠 C 单独消除，靠 A/B） |
| 禁实跑开 `--c5-ignore` | 与 v5 同文 refuse-91；隔离测：带 `.ok` 无 `allow_c5_ignore` → **rc=91** | **PASS** |
| 禁抬 C4/stop/hard | 阈值逐字同 v5 | **PASS** |
| ≠解阻 X2；live=false | COVER/回执明示；本审阅重申 | **PASS** |
| 关闭 sleep+fd→wrapper_stdout 误杀路径 | A（logdir 白名单）∨ B（sleep）任一即可关；Eng 双保险；C 降低内部 LOG 再入 output* | **PASS**（静态+逻辑） |
| 仍能杀真并发读 output/research 的进程 | 异 run 的 output*/data* cwd/fd 仍 hit；maps/cmd 的 python/research/scripts 路径仍 hit；benign 不放行 python | **PASS**（静态；合成真阳性未在本窗实跑） |

## 5. Eng 主包 vs AI 并行草案（不等价）

| 维 | Eng 主包（`b1208d3c…`） | AI 草案（`e03a61b6e706c0b49765cc117a1e4d915fd2924170c281aa5d805d5a716b3cb0` / sha8 `e03a61b6`） |
|---|---|---|
| 权威性 | **主交 / 审阅对象** | 并行提案；**非**主包 |
| 白名单 | logdir **+ outdir** | **仅 logdir**（无 ODABS） |
| 良性命令 | sleep / true / 裸 cat（字符串 case） | **仅** pure-sleep（argv0=`sleep` + 可选单数字时长；更严） |
| stdout 落点 | `/tmp/quantlab_wrapper_logs/${TAG}.log` + logdir **symlink** | `/tmp/quantlab_wrapper_${TAG}/${TAG}.log` + `$L/${TAG}_stdout.path` 指针（**无** symlink） |
| COVER / 回执 / selftest / SHA256SUMS | **有** | 盘上仅 draft+DIFF（本审阅时未见对等 COVER） |
| 阈值 / refuse-91 | 同 v5 | 同 v5 |
| 字节等价 | — | **否** |

**裁定**：以 **Eng 主包** 为准进入后续 pin/r3b 链路。AI 草案可作「pure-sleep 更严 / 仅 logdir 白名单」备选讨论，**不得**与 Eng 混用或当作已审附件自动升级。

## 6. 条件（PASS_WITH_CONDITIONS）

1. **未钉生产**：侧稿标注 SIDE DRAFT；在 Arch **正式 pin**（新文件名/sha 钉入 CMD）前，**禁**替换 v5 live 路径、禁实跑 leaf 探针消费本 draft。
2. **r3b 另包另签**：AI 须交 r3b COVER+CMD（wrapper 指向 **已 pin** 的 v6 或经 Arch 明示可用的本 draft 路径）→ Arch 另审 → **新** `.ok`（禁 `c5e54085` / `cd230f9c` / `1c32ab1e`）。
3. **合成自测缺口（非否决）**：`selftest_c5_tighten_synthetic.sh` CASE1 的 logdir/outdir 在 `/tmp` 下，**不会**触发 `output*` 分支，故不能单独当作 A 的盘证；本审阅以 **helpers 单元逻辑 + refuse-91 + symlink C** 为静态证据。建议 Eng/AI 在 pin 前补一条：**伪造** `/workspace/QuantLab/output/...` 树下的 fd+sleep 合成（仍禁真行情/因子）。
4. **残留（可接受）**：`c5_benign_cmd` 对「单字符串」`sleep 0.2; evil` 会 over-skip（真实 argv 不会如此拼接；`bash -c 'sleep…'` **不会**被当成 benign——单元已证）。
5. **A 过宽残留（COVER 已披露）**：本跑 outdir 下非 python 的异 PGID 读者可能被 cwd/fd 白名单 skip；maps/cmd 仍可杀真研究读者。接受为裁定字面杠杆的已知代价。
6. **排窗**：错开叶27 **14:00–14:45 ET**；本审阅不挂 QUIET、不签 `.ok`。

## 7. 本窗已做静态动作（禁项遵守）

| 动作 | 结果 |
|---|---|
| `bash -n` Eng draft / AI draft | 均 OK |
| DIFF→draft 还原 | Eng/AI 均可 |
| v5 sha 核对 | `4240ce82…` 匹配；文件未改 |
| helpers 单元（/tmp） | under_own logdir/outdir=0、other=1；benign sleep/true/cat OK；python/research/cat-with-path/bash-c-sleep **非** benign |
| refuse-91（/tmp `.ok` 无 allow_c5_ignore） | **rc=91**，`launched=0` |
| 杠杆 C 短跑 `--selftest --no-guard` | rc=0；`$L/synlink.log` **是 symlink** → `/tmp/quantlab_wrapper_logs/synlink.log` |
| 读真行情/因子 / 挂 QUIET / 签 `.ok` / 改主干 v5 | **未做** |

## 8. 禁项（重申）

- 禁实跑开 `--c5-ignore`；禁抬 C4/STOP/HARD；禁本包解阻 X2。
- 禁复用 VOID `c5e54085…`；禁把本 FAIL/侧稿报为 real_peak PASS。
- 禁改/覆盖 live `cmc_wrapper_v5_4240ce82.sh` 直至正式 pin。
- 禁将 AI 并行草案当作 Eng 主包混签。
- Arch 不代跑叶探针。

## 9. 建议下一跳

1. **（可选加固）** Eng：补 output* 树下的合成 A 证明，或 Arch 接受 §7 静态证据直接 pin。
2. **Pin**：Arch/主令确认后，将 Eng draft **钉**为 `cmc_wrapper_v6_…sh`（新 sha），v5 保留只读基线。
3. **AI r3b**：交 r3b CMD+COVER（脚本可 UNCHANGED 若仅换 wrapper；须写明新 wrapper sha）→ Arch 另审 → **新签** probe `.ok` → 错开叶27 窗开跑。
4. X2：仍挡至实峰 probe **PASS**。

## 10. 缺口清单

| 缺口 | 级别 | 谁补 |
|---|---|---|
| 合成自测未在 `output*` 路径证明杠杆 A | 条件/建议（不挡 PASS_WITH_CONDITIONS） | Eng 可选 |
| r3b CMD/COVER/新 `.ok` | **NEED_R3B_PACKAGE**（期望下一跳，非本 wrapper 包内缺失） | AI |
| AI 并行包无对等 COVER 且 ≠ Eng | 信息项；以 Eng 为准 | — |
| 正式 pin 文件名/路径尚未落盘 | 条件 | Arch/主令 |

**非缺口**：Eng 主包已含 COVER / DIFF / draft / 回执 / SHA256SUMS / selftest 草图 → **不**标 `NEED_COVER`。

live=false；promotion_approved=false。
