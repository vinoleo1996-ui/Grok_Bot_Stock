# Arch 叶25 mem_probe r3b CONSUMED_PASS 回执

- **角色**：QuantLab Arch
- **written_et**：2026-10-25T15:21:16-04:00（America/New_York）
- **live**：false · **promotion_approved**：false · **≠X2**

## 结论

**CONSUMED_PASS** — AI 回执 `a626000d` MATCH；rc=0；peak_kb=`323784`≪C4；**C4=PASS C5=PASS**；`.ok` `6054b3bf` 已成功消费归档（**禁 RESTORED**）；QUIET **已 lift**（healthz quiet=false）。

**闸门**：本票 PASS → 叶25 **mem_probe / real_peak 挡可清**（实峰证明已具备；对齐 NEED_MEM_PROBE `f389c394` §0/§3）。**仍 ≠ 自动签 X2.ok**；X2 须另包另审另签；本回合**未签**任何 X2 `.ok`。

## 核验（MATCH）

| 项 | 值 |
|---|---|
| AI 回执 | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_MEM_PROBE_R3B_RUN_RECEIPT_20261025_ZH.md` |
| AI 回执 sha256 | `a626000d80472da818f0f801a2b1d00a069af31986ae707942b68fec51996ff8` |
| AI 回执 sha8 | `a626000d` — **MATCH** |
| ET_TS | `20261025_151224` |
| rc / stopped | **0** / **0** |
| peak_kb（sampler） | **323784** ≪ C4=1331200 |
| C4 / C5 | **PASS** / **PASS**（无 c5-ignore；帽未抬） |
| `.ok` 内容 sha256 | `6054b3bfc44977614d299976da28e72d757885cf6a59fa26b361d4112060692b` |
| `.ok` sha8 | `6054b3bf` — **MATCH** |
| PIN wrapper | `b1208d3c…`（`cmc_wrapper_v6_C5TIGHTEN_b1208d3c.sh`） |
| probe | `8da4f2e6…`（`research/leaf25_full_factor_mem_probe_r3.py`） |
| 审阅 / 窗令 | `eaedd655…` PASS_WITH_CONDITIONS / `bd13c878…` 15:00–15:45 |
| 进程 | gone（pgrep bracket-escaped 空） |

## CONSUME 归档

| 项 | 值 |
|---|---|
| 原 live | `output/ai_factory/ARCH_RUN_AUTH_LEAF25_MEM_PROBE_R3B.ok`（**已不在 live**） |
| 原内容 sha256 | `6054b3bfc44977614d299976da28e72d757885cf6a59fa26b361d4112060692b` |
| 归档路径 | `output/ai_factory/_consumed/ARCH_RUN_AUTH_LEAF25_MEM_PROBE_R3B.6054b3bf.CONSUMED_PASS.20261025T1521ET.ok` |
| 归档文件 sha256 | `74b5f209c81eb3cbfc06ec67b8731770125cf517fa1804bdd79707a2cd1bed30` |
| 归档文件 sha8 | `74b5f209` |
| 命名 | **CONSUMED_PASS**（成功消费；**禁 RESTORED**；非 VOID） |
| 附注 | 归档文件末追加 `# ARCH_CONSUMED …` 注释块 |

## QUIET

| 项 | 值 |
|---|---|
| 处置前 | `output/loop/RESEARCH_QUIET.lock` 存在（`arch_quiet leaf25_mem_probe_r3b @2026-10-25T15:08:19-04:00`）；healthz quiet=true |
| 处置 | **lift** → `output/loop/_lifted/RESEARCH_QUIET_leaf25_r3b_PASS_LIFTED_20261025T1521ET.lock` |
| lift 文件 sha256 | `a08e06d15fee1e3a1a69417ee56c187841f24a79012b96dab32df9272d1b255c` |
| lift 文件 sha8 | `a08e06d1` |
| 处置后 | live 锁**无**；healthz `@2026-10-25T15:21:16-04:00`：`ok=True` · `quiet=False` · `live=False`；pgrep 空 |

## 闸门裁定（NEED_MEM_PROBE / real_peak）

| 项 | 裁定 |
|---|---|
| 源审 | `docs/v2/audit/ARCH_LEAF25_MEM_CHUNK_REVIEW_20261025_ZH.md` sha `f389c394…` = **NEED_MEM_PROBE**（§0/§3：须先 mem_probe 实峰再谈 X2） |
| ADOPT(A) | `docs/v2/audit/ARCH_LEAF25_MEM_PROBE_ADOPT_A_REJECT_REAL_PEAK_20261025_ZH.md` sha `14e9b6ba…`：拒签未实现实峰路径 |
| 本票 | r3b **real_peak 完成**（HI_LIQ · month · chunk0 · 2024-06-03→2024-06-28；peak≈324MB；C4/C5 PASS） |
| **mem_probe 挡** | **可清** — 实峰证明已具备；G1「无 mem_probe 实测峰」对本宇宙/粒度已闭合 |
| **X2 自动签** | **否** — 仍 ≠ 自动签 X2.ok；X2 另包（COVER+CMD+DIFF+脚本钉）→ 另审另签；禁本票复用为 X2；禁抬帽 |
| 仍挡 X2 的他因（非本票范围） | FROZEN §5/§8 PENDING_REVERIFY、全叶 build/chunk/merge/eval 实现、FULLA/更长窗峰外推等 — 见 `f389c394` §4 G2–G5；本回执**不**一并清 |

## 叶27 month 旁注（不代办）

- DRAFT READY·HOLD 盘：COVER `c8b33519` / CMD `5323d614` / DIFF `5fa2a29e` / HAND `9428fcbf`；脚本 `262f9bf6`
- QUIET 已 lift → **等主令 AI 交审**；Arch **只审不代跑**；**禁抬帽**；≠X2

## 下一跳

1. **请主令 AI** 交叶27 month DRAFT 审（本票已放行 QUIET）
2. 叶25 X2：**另包另审另签**；勿把本 PASS 当 X2 ACCEPT
3. 禁 RESTORED 本票 `6054b3bf`；禁复用 VOID `c5e54085`/`cd230f9c`/`1c32ab1e`/`3a6caa4f`

## 非动作

- 不新签 `.ok`（含 X2）；不代跑；不改主干；不抬帽；live=false

live=false。
