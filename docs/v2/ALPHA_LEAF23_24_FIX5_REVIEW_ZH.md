# Alpha 复核：叶23 r2.6 / 叶24 r5（FIX5 合并版）

- 复核人：QuantLab Alpha；时间：2026-10-18 03:4x ET；方式：只做静态审查（diff、grep、在 /tmp 跑 ast.parse 和 pyflakes），**没有运行任何项目代码**。research/__pycache__ 前后都是 22 个文件。
- 另外用自己的一行 pandas 只读了 delisted_master（339 行，0.4 秒），用来核对披露数字，没有 import 项目模块。
- 复核对象：
  - 叶23 `research/g1g5_sue_desens_cs_alpha.py` = 60393573925a84399f27c430009b3e5dc7c575b52e24cd36ed6c31ba73484bce ✔
  - 叶24 `research/g1g5_imax_intraday_alpha.py` = a2719e5c0778d3f1b912b8ecb553689b50476bea1498c6829f797262e15f84ba ✔
  - diff `docs/v2/AI_LEAF23_24_FIX5_DIFF.patch` = 6138dce5fbe90d9773f8ac3397787855f24632d1c9f7d670a75dcb7068777d2f ✔
  - 前一版（`_recovery/ai/pre_fix5_0325/`）：叶23 r2.5 = 07c99873…bfaa ✔，叶24 r4 = 1e8de734…e5dc ✔
- patch 回放：我用前一版对现版重新做 diff，增删行集合和 patch 完全一致（叶23 192 行、叶24 184 行 diff）。

## 裁定：**CONDITIONAL**（FIX5 合并的 7 项全部核实通过；另有 1 个**早已存在的** P1，修好之前不能签全量 .ok）

FIX5 本身没有引入新问题。P1-1 是 FIX3 起就有的模块级顺序错误，py_compile 查不出来，前几轮审查都漏了。修法只是挪一行，不动逻辑。修完出 r2.7 / r6，回放 diff 后即可 PASS。

## 逐项核对

| # | 项目 | 结论 | 位置 |
|---|---|---|---|
| 1 | CMC 路径改为 `research/alpha_combo_marginal_v1_1.py`；`CMC_V11_SHA` = 5658f612fef313fc5b818fc4cb9d594d757377e0dbf7c7dc86a6e31788b88911，和文件实际 sha 一致；authorize 断言 `.ok` 的 dep_combo_sha256 等于它 | ✔ | 叶23 L74/L84/L252；叶24 L62/L72/L248 |
| 2 | `dep_combo_legacy_sha256` → `alpha_combo_marginal.py`，`CMC_LEGACY_SHA` = bee230199ac2…c51c，和文件实际 sha 一致。它只用于 .ok 钉 sha 和 authorize 等值检查，判定代码里没有任何读取；披露写明「只作对照列，不进判定，不计家族次数」 | ✔ | 叶23 L74/L85/L252/L744；叶24 L62/L73/L248/L677 |
| 3 | TOOL_CMDS 仍是 f-string（`f"ARCH_TOOL_CMDS_LEAF{LEAF_NO}_X2.cmd"`）。新增 `cmc_cmd_ok()`，要求 .cmd 里至少有一行 v1_1 CMC，且每行 v1_1 都带 `--arch-ok`，并作为 authorize 的检查项。v1_1 工具确实有 `--arch-ok`（必填）和 `--legacy-json` 参数（v1_1 L99–100）。docstring 的命令示例也已改好 | ✔ | 叶23 L31/L87/L226–231/L251；叶24 L19附近/L222–227/L247 |
| 4 | 披露文字改称 v1.1：外部工具口径（叶23 L736，叶24 L668）、风格 t−1 对照 s8 v1.1（叶23 L743，叶24 L676）、新增「CMC v1.1」条（叶23 L744，叶24 L677）。原来的 L706/713 和 L638/646 因为前面插了代码，下移了约 30 行。引用的 sha 都对：s8 v1.1 = 455fdf82 ✔、旧 s8 = af48bc05 ✔、交接文档 = ab6d1e82 ✔ | ✔ | 同左 |
| 5 | 退市截断：主口径 `cut = delist_date`，不回退。影子口径 `cut_dd = last_trade_date`，只用于披露。X2 内缺 delist_date 就停跑，窗外只披露。字段名为 `poolEW/wb_cagr244_primary_cut_delist_date`、`*_shadow_cut_last_trade_date`、`*_diff_primary_minus_shadow`。旧的 `*_cut_delist_date` 键、`Mp_dd/wv_dd` 返回值和 evaluate 里对它们的引用都已删干净。截断断言 (S & gone) 现在按 delist_date 判。 | ✔ | 叶23 L408–412/L421–423/L480–482/L514–531/L770–778；叶24 L379–383/L392–394/L451–453/L485–502/L702–710 |
| 6 | 没有新增 s8 键：TOOLS / OK_FIXED / OK_REQUIRED 都没有 s8 项，s8 v1.1 只在文字里引用（「不 import，无 .ok 键」） | ✔ | grep 全文件 |
| 7 | 预注册没改：叶23 PREREG = 8f5d8ac4…922e ✔，叶24 PREREG = c289e770…33a8 ✔，文件 mtime 还是 01:43/01:44。风格集仍是冻结集：SW L1 + lmv1 = LM.shift(1)、beta120.shift(1)（对 510300）、mom = log1p(R).shift(21).rolling(100)（t−120..t−21）、ladv1 = 当日 adv20（mask 写入方已是 t−20..t−1，不再 shift）。叶23 另加 acap，按名 shift(1)（FIX3）；叶24 另加 vol20 = R.shift(1).rolling(20)。这些行都不在本次 diff 里，FIX3 的 ladv/acap 修法保留，没有前瞻回退 | ✔ | 叶23 L614–620/L646–648/L680/L689；叶24 L553–558/L586/L614 |
| — | 没有无关改动：diff 只涉及以上几项，外加 docstring 和注释同步 | ✔ | — |

pyflakes 新旧对比（在 /tmp 跑）：新增的只有 2 条 `undefined name 'RR'`（叶23 L526，叶24 L497）。这是 lambda 引用了随后被 del 的名字，但两次调用都在 `del RR` 之前、同一行执行，运行时没问题。旧的 `parts` / `r0` 告警也是同一类误报。

## 发现

### P1-1（早已存在，不是 FIX5 引入的；两叶都有）：模块一加载就会 NameError
- 叶23 L90–94 是模块级的 `OK_FIXED = {..., "window_start": X2S, "window_end": X2E, ...}`，但 `X2S, X2E` 到 **L99** 才赋值。叶24 也一样：L78–82 用到，**L87** 才定义。
- Python 在 import 时就会对 dict 字面量求值，所以脚本任何阶段（包括 `--help`）都会先抛 `NameError: name 'X2S' is not defined`。pyflakes 两版都报了（新旧各 1 条，叶23 L92、叶24 L80）；py_compile 查不出来。
- 来历：FIX3 patch（`AI_LEAF23_24_ARCH_FIX3_DIFF.patch` L38/L46）把 `window_start: X2S` 加进 OK_FIXED 的时候，没有把定义挪到前面。
- 影响：只会失败停跑，不会算出错误结果；但不修就跑不起来，全量 .ok 也无从验证。
- 修法：把 `X2S, X2E = "2024-06-03", "2026-10-09"`（叶23 连同 FUND_YEARS，叶24 连同 YEARS）挪到 OK_FIXED 之前，比如紧跟 `PANEL_VERSION` 之后。不改值、不改其他逻辑；新 sha 回放 diff 应只有这一处移动。

### P3-1：「约 8 名」是没跑之前写下的数字
- 叶23 L746、叶24 L679 写着「影子口径按最后交易日截断（约 8 名）」。delisted_master（63590f23）里 X2 窗内退市的有 93 名，其中 76 名 last_trade_date 和 delist_date 相差超过 1 天（中位数 25 天，最长 135 天）。真正影响基准池的名数要看池成员，跑之前算不出来。
- 建议：去掉「约 8 名」，改为引用 diag 里的计数。同时在 pool_benchmarks 里补一个影子口径截断的名·日计数（比如 `delisted_cut_name_days_x2_shadow_last_trade_date`）。现在 `delisted_cut_name_days_x2` 只记主口径。

### P3-2：pool_benchmarks 多建了一份全期收益透视表
- 叶23 L524、叶24 L495 新建的 `RR` 是 idx × U 的 float64 透视表，而 evaluate 里的 `rr`/`r0` 这时还在内存里，相当于同样大小的表存了两份，外加 `RR*M`、`RR*W_` 等临时数组。现有 1.5GB 守护会兜底停跑，但这部分增量没有估算过。
- 建议：下一版把 `r0` 传进去复用，或者只截到 X2 窗口段；或者在回执里记下峰值 RSS。不阻断。

### P3-3：「未签」状态的注释已过时
- 叶23 L84、叶24 L72 的注释「NOT yet Arch-signed for a full run」，以及披露里「该工具的全量 .ok 尚未经 Arch 签发」，事实上没错。但 CMC v1.1 r3 已经通过 Arch 审查（bbfcb7ef），selftest .ok fa45bf7f 也签了。建议下一版改成「r3 已过 Arch 审 bbfcb7ef，全量 .ok 未签」。

### P3-4（仅提示）：cmc_cmd_ok 只做子串检查
- 它只检查 v1_1 行里有 `--arch-ok`，不查 `--universe hiliq --base capadv`，也不查 legacy 行是否只作对照。.cmd 文件的整体 sha 已由 Arch 在 .ok 里钉住，人工审 .cmd 时一并看即可，不需要改代码。

### 记录（不算问题）
- delisted_master 里缺 delist_date 的有 0 名，所以「X2 内缺退市日即停跑」现在不会触发。缺 last_trade_date 的有 1 名（T600018.SH，2006 年退市），不在 2018–2026 递推范围内，影子口径不受影响。
- 主口径改成 delist_date 以后，最后交易日到退市日之间按停牌沿用、记 0 收益、留在分母里，比旧口径（按 last_trade_date 截断）的前瞻更少，符合主 Agent 02:44 的裁定。

## 结论
- FIX5 合并内容（项 1–7）：**通过**。
- 全量 .ok 的前提：修好 P1-1（挪一行，出 r2.7 / r6），Alpha 回放 diff 确认只有这一处移动。P3-1~P3-3 可以在同一版顺手处理，也可以留到下一版。
- 全量 .ok 应钉 dep_combo_sha256 = 5658f612…，dep_combo_legacy_sha256 = bee23019…（只作对照列）。
