# Arch：叶23 r2.10 A02（eval FULLA）B3 停跑诊断

- 写入：Arch 调查（只读），2026-10-18T06:41:23-04:00。live=false；promotion=false。
- 对象：research/g1g5_sue_desens_cs_alpha.py f1344324（commit 821a9107）；.ok 97964bb1；证据 output/ai_factory/leaf23_sue_desens_cs/B3_carry_mismatch_FULLA.json（f82f5ee0）；回执 AI_LEAF23_R2_10_X2_RUN_RECEIPT_ZH.md（2d4599b0）。
- 方法：读代码、git show 9b1d2349（r2.9 = d199b778）、pyarrow 按代码/行过滤只读面板、mask、delisted_master。没有 import 项目代码，没有跑项目代码，没有写 output/、data/、.ok、.cmd 或 git。

## 0. 结论
- **根因：B3 两侧对「被补回行（row_origin=restored）」的口径不一致，属于规格缺口，检查是真阳性。** 不是 build FULLA 产物的问题，也不是 r2.10 少读列、叶20 α 起读日或只读再平衡日行带来的回归。
  - Data 的 fulla_carry（重建计划 P1-3）：取「复牌前最后一个**有成交且 mask 未判停牌**的交易日」的 fulla_v1。被补回行本身是 mask 停牌日，会被跳过。
  - pool_benchmarks 的递推（Arch 129d67c5 §3）：「面板有行 → S = 该行 col（restored 行为 False）」。被补回行会把 S 置 False、断开沿用链。
  - 两者只在一种情况下分歧：在同一段停牌里，最后一个正常交易日和复牌行之间还夹着一条 restored 行。这种行有两类：先复牌又停牌（第一次复牌那天就是 restored 行），以及先盘中停牌再全天停牌（盘中停牌那天是 restored/intraday_halt 行）。
- 窗口内恰好 2 条，就是这 2 条；HILIQ 窗口内同类为 0，所以 HILIQ 过了检查。
- **Plan B 重跑结果相同；r2.9 若跑到这里也一样会停。** B3 的输入只有 cs_panel、mask、delisted_master 和 PX.ret，fund/build 产物不参与；pool_benchmarks 的递推在 r2.9 与 r2.10 之间只有内存位置调整，没有逻辑差异。
- 建议：r2.11 只改 pool_benchmarks 的 B3 锚点规则，需 Arch 审。叶24 r9（b83cb8e6）的递推与此逐字相同，需同步改。
- 不能用现有脚本从 A02 续跑：输入和逻辑都是确定的，必然再停。改到 r2.11 之后，fund/build 仍可沿用 r2.9 的 meta（方案 A 有效），但 A01 eval HILIQ 要重跑（Mp 规则变了，HILIQ 基准也随之变化），然后跑 A02、A03。

## 1. B3 到底比什么（代码位置，f1344324）
- 调用：L842 `carry_col = "hiliq_carry" if uni == "HILIQ" else "fulla_carry"`；L850 `pb = pool_benchmarks(panel, PX, col, carry_col, rr, s, e)`；L851–853：carry_mismatch≠0 时写 B3_carry_mismatch_<uni>.json，然后 `raise SystemExit("STOP (B3) …")`。
- **Mp 一侧（eval 现算）**，L468–566：
  - 2018–2026 逐年读 cs_panel 的 [date, instrument, col(=fulla), logmv, ind]，以及 mask 的 suspended/st/young/adv_fail。
  - L510 `carry_nc = (~has) & (sus == 1.0)`，只在面板无行且 mask 停牌时沿用；L515 `A = val.where(has, 0.0).mask(carry)`，有行就取该行 col；L518 用 ffill 递推得到 S。
  - L566 `Mp = S.shift(1)`，即 T−1 的成员状态。
- **fulla_carry 一侧（Data 面板列）**，L575–580：读 cs_panel 中 row_origin==restored 且 restore_reason==resume 的行，取 [date, instrument, fulla_carry]；只比 idx[0] 之后的行（idx 来自 PX.ret 的 pivot，起点 2024-05-20）；逐行要求 Mp(d,i) == fulla_carry(d,i)。
- 两侧都来自面板目录 output/ai_factory/panel_cache_v2_resumefix（manifest 5c44019d），mask 来自 output/strategy_hiliq/universe_mask_hiliq_v1.parquet（c5433e80）。**fund/build 的任何产物都不进 B3。**
- r2.9（d199b778）里同样有这项检查（L775–778，逻辑同上），只在 eval 里；build 阶段没有 B3。r2.9 的 eval 是一个进程依次跑 HILIQ、FULLA（L760）：HILIQ 段跑完（ru_maxrss 1596 MB），进入 FULLA 段后在 B3 之前就被 RSS 看门狗杀掉（exit 137），所以 r2.9 从来没执行过 FULLA 的 B3。「r2.9 build FULLA 是否通过 B3」这个问题不成立。
- r2.9 → r2.10 的 pool_benchmarks diff 只有三处：`pre` 提前到 `del pr` 之前计算（pr 在两处之间未被修改，结果相同）；`del A, B, sus` 提前；cat 改为 pop。递推和校验逻辑逐字相同。

## 2. 两条不一致行的实测（只读）
mask 显示，restored 行当天全部是 suspended=True。

**002868.SZ（不在 delisted_master 里）**
| 日期 | 面板行 | fulla | fulla_carry | mask suspended | 递推 S |
|---|---|---|---|---|---|
| 2025-04-21 | v1 | True | False | False | True |
| 04-22 至 04-25 | 无行 | — | — | True | 沿用 True |
| 04-28 | restored/resume，halt_sessions=4，prev_traded=04-21 | False | **True** | True | **False（有行取 col）** |
| 04-29 | 无行 | — | — | True | 沿用 False |
| 04-30 | restored/resume，halt_sessions=1，prev_traded=04-28 | False | **True** | True | Mp=S(04-29)=**False ≠ True** |

- 04-28 那一行：Mp = S(04-25) = True，与 carry 一致，所以没报。
- 04-30 这一行：Data 跳过 04-28（mask 停牌），回溯到 04-21 的 fulla=True。递推却在 04-28 断了链。
- 另外 04-30 起 mask 的 st=True，不影响这一天的 T−1 判断。

**603056.SH**（delist_date 2026-03-31，last_trade_date 2026-01-20，不在退市截断范围内）
| 日期 | 面板行 | fulla | fulla_carry | mask suspended | 递推 S |
|---|---|---|---|---|---|
| 2026-01-08 | v1 | True | False | False | True |
| 01-09 | restored/**intraday_halt**，prev_traded=01-08 | False | True | True | **False** |
| 01-12、01-13 | 无行 | — | — | True | 沿用 False |
| 01-14 | restored/resume，halt_sessions=2，prev_traded=01-09 | False | **True** | True | Mp=**False ≠ True** |

**全量核对**（restored 行共 3579 条：resume 3533 条，intraday_halt 46 条）：resume 行中「fulla_carry=True 且 prev_traded_date 那天本身是 restored 行」的，窗口内（>2024-05-20）恰好 2 条，就是上面两条；hiliq_carry 窗口内为 0 条。全样本自 2018 年起 fulla 38 条、hiliq 13 条，都在窗口外，不进校验，但会影响递推状态。
- 这两条不涉及 SW 行业变动；也不涉及退市截断（603056 的 cut 日是 2026-03-31，晚于 01-14）。

## 3. 检查本身对不对
- **对，是真阳性。** 它如实抓到了「池成员递推」和「Data 记账 carry」两套定义的分歧。Arch 在 FIX2 审查（bd3abe5c §5 第 2 条）里写过「Data classify_restore 的 carry 定义与本叶一致」，这个假设不完全成立：中间夹 restored 行时两者不一致。这是本叶第三次「缺行或特殊行当作状态」的假设错误，前两次是 B3 C1「无行=停牌」和 P1-A「mask 无行=退市」。
- 按经济含义，Data 的口径更符合预注册 §6.6（「T−1 成员 × T 收益，含复牌行，停牌 0 收益不剔分母」）：持有人一直持有到真正复牌，夹在中间的那一天恢复交易不应把它踢出池子。
- 现行递推还有一个副作用：每次复牌（restored 行）之后的 d+1 天，Mp 都等于 restored 行的 col，也就是 False，相当于每段停牌复牌后掉出池子一天。HILIQ 也受影响，只是 HILIQ 的校验只比复牌行当天，抓不到。
- Plan B：同样停。B3 不读任何 fund/build 产物，输入的 sha 都已钉住且没变。

## 4. 修复建议（r2.11，代码修复，须 Arch 审；不是数据修复，也不是放宽检查）
1. pool_benchmarks 的锚点改为：只要 mask 当天停牌就沿用上一状态，不管面板有没有行（即 restored 行也沿用）。
   - 建议写法：`carry_nc = (sus == 1.0) & (~has | restored)`，其中 restored 来自面板 row_origin（只多读一列，或用已读列推出）。
   - MV 在 restored 行沿用停牌前的值，与「停牌段内沿用流通市值」一致；如果要改用当行 logmv，请 Arch 另行裁定。
   - 退市截断（gone）、P2-B、cut_fail 断言都不变。
2. 加硬断言：面板中凡是 mask suspended=True 的行，row_origin 必须是 restored，反之亦然。否则停跑。
3. 「沿用名·日」的原因计数改为按 (S & sus==1) 计。HILIQ 和 FULLA 两侧 B3 检查保留，修后预期 0 不一致。可以再加一项：「复牌后 d+1 的 Mp 等于复牌行 carry」，作为披露计数。
4. 叶24 r9（research/g1g5_imax_intraday_alpha.py，b83cb8e6）的递推与此逐字相同，FULLA 会以同样的 2 行停跑，须同步改。
5. 不建议的做法：改 Data 面板（Data 的列符合它自己的书面定义）；把这 2 行加白名单或放宽检查（属于事后改规则）。
- 影响评估（未实测，不编造数值）：HILIQ 中，B3 与「旧不沿用」写法的 EW/wb 年化差分别约为 −5.5bp 和 +1.4bp。按量级推断，本次修复对基准的影响应在 bp 级；而 HILIQ 两档 CAGR（3.18% / 4.39%）比 wb（11.60%）低约 7 个百分点。所以判定方向几乎不可能改变，但正式数值必须以 r2.11 重跑为准。

## 5. 续跑判定
- 用 f1344324 从 A02 续跑：无效，必然复现同样的 STOP。
- r2.11 只改 eval 内的 pool_benchmarks，fund/build 不读这些列（脚本 L21 有断言），所以 r2.9 的 fund/build meta（f393b3e9 / fb4b2ad4 / 07391924）仍可通过 resume 键沿用，方案 A 成立。
- 需要新签 .ok（97964bb1 单次有效；script_sha256 改为 r2.11）。
- 主口径须重跑 A01 eval HILIQ → A02 eval FULLA → A03 merge。A01 的 meta 7c382b89 绑定 f1344324，而且 HILIQ 的 Mp 会变，不能沿用。
- A01 现有产物（summary_HILIQ_20261018_063101 等）在新签前要由 Arch 移到 _void，否则 guard_fresh 会拒绝；外部 daily_weights/run_meta 的 _063101 也一样，CMC 不得引用它们。

## 6. 预注册（8f5d8ac4）：主口径未过时敏感性怎么办
- 判定只看 HI_LIQ 主口径。§9：「唯一判定规格：HI_LIQ_V1.1、主口径 ΔE/P（MV_fix 分母、行业内秩变换）、预告信息禁入 20 日、17.5bp、60万 top-6 / 100万 top-10。」
- 敏感性（以及 FULLA 本身）都只披露。§9：「其余一切——FULLA、敏感性 A（σ 分母 SUE）、敏感性 B（日更分母）、S_F（含密封窗读数）、禁入 40 日、top-20 书……——一律标注『未做多重检验校正，仅披露』，不进判定。」以及：「结论以主口径为准；敏感性与主口径方向不一致时，在回执中写明，但不改判定。」
- 预注册**承诺了要报**这些敏感性，而且没有写「主口径不过就跳过」的条款：
  - §6.5a：「S_F 在 X2 上与完整规格并列计算并报告（仅披露，不进判定 t）。」
  - §2：「另报 40 日禁入期敏感性（仅披露）。」
  - §1：「日更 MV_{t−1} 版只作敏感性。」
  - §0.1：「敏感性 = 历史标准差 SUE，不进判定。」
- 唯一带条件跳过的是密封窗。§6 第 5 条：「X2 不过，就完全不读。」§6.5a：「密封窗只在 X2 完整规格通过全部硬闸（§7）之后读一次。」
- 硬闸 §7：「60万、100万两档净 CAGR 都要 > HI_LIQ wb，否则判 FAIL。」
- §10 禁止：「冻结后改任何规则、阈值、口径……；事后挑选规格。」
- **Arch 解读**：4 个敏感性是**预先承诺的披露项，不进判定，但也不是可选项**；预注册没有「主口径失败即跳过」的规定。不跑不会改变判定，但属于偏离预注册交付，需要主 Agent 书面同意，并在回执里写明「看到主口径 FAIL 之后决定不跑」。
- 建议：主口径（r2.11 的 A01–A03）先跑完，得出正式判定；敏感性延后到叶24 之后、资源空闲时补跑，不必为它们挤占叶24。
- 因为 FULLA 只是披露项，严格说 HILIQ 半边已经足以确定判定（wb 地板未过，FAIL）。但脚本要等 merge 才写正式 summary 和 eval_meta，而且 B3 停跑说明基准口径本身要修，所以正式判定须等 r2.11 主口径三步跑完。

## 7. .cmd 与步骤表核对
- 固定路径 output/ai_factory/ARCH_TOOL_CMDS_LEAF23_X2.cmd = 6c65f6c3（mtime 06:29:41 ET，1325 B）。内容是 4 行注释加 1 行 CMC v1.1（--arch-ok …CMC_V1_1_FULL_LEAF23.ok），**没有任何叶23 阶段命令**。与 _review/leaf23_r2_10_ok_draft/ 中的草稿逐字相同（sha 一致）。
- 往期的 19db13cc（r2.7）和 493cc03c（r2.9）结构相同，也只有 CMC 行。
- 脚本怎么用这个文件（L104–113、L276–281、L300–301）：
  - TOOL_CMDS 是固定路径；.ok 的 tool_cmds_path 是固定值（OK_FIXED），tool_cmds_sha256 是必填项，并要求等于该文件的实际 sha。
  - cmc_cmd_ok 只检查 CMC v1.1 行是否带 --arch-ok。
  - 依据 Arch 129d67c5 §5-1，「工具命令放在钉住的 .cmd 里」，指的是下游工具（CMC），**不是叶的阶段命令**。脚本既不读也不钉阶段命令。
- 阶段命令的授权来源：
  - 条件文档 cc16c599（docs/v2/audit/leaf23_r2_7_run/ARCH_LEAF23_RUN_CONDITIONS_ZH.md）§4 列了「每个阶段的确切命令」。但它是 r2.7 的版本：--arch-ok 指向 R2_7 .ok；eval 不带 --uni，也没有 merge，不适用于 r2.10 的拆分。§10 还写明「单次有效」。
  - r2.9 回执自称「条件文档继续生效，命令按 §4 原文执行，.ok 换 r2.9 版」。
  - r2.10 **没有新的条件文档**。r2.10 审查 d804aa0e §7 写道：「正式 .cmd …… 内容只有 CMC 一行（不变）」；「步骤表（AI_LEAF23_R2_10_PROPOSED_CMD.txt，不被脚本钉住）……顺序 A01 eval HILIQ → A02 eval FULLA → A03 merge → ……正确。」
- 核对 644ce1f6：A01–A27（方案 A）和 B01–B30（方案 B）。A01 是 `--stage eval --uni HILIQ`，A02 是 `--stage eval --uni FULLA`，--arch-ok 指向 R2_10 .ok，前缀为 env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python。日志显示，AI 只执行了 A01、A02，且 A02 一失败就停了，符合「非 0 即停」。
- **结论：**
  - AI 的说法属实：.cmd 只有 CMC 行，阶段命令取自 Arch 已审为「正确」的步骤表。
  - 但这份步骤表**不是**由 Arch 签发、钉 sha 的授权文件。r2.10 依据的条件文档仍是 r2.7 版，§4 的命令和 §10 的单次有效条款在字面上都已不适用。授权链有文书缺口，记 **P3**：执行本身在 .ok、脚本门禁和审查范围之内，没有越权；缺的是一份 r2.10 条件文档。
  - 之前审稿人说「方案 A 每一行都在 .cmd 里」，这一说法**不对**，应更正为「方案 A 每一行都在步骤表 644ce1f6 里，.cmd 只含 CMC」。
  - 下次（r2.11）由 Arch 发条件文档增补，钉步骤表 sha，写明 A01–A03 等命令原文和单次有效，取代对 r2.7 条件文档的继承。

## 8. HILIQ 半边数字核对（summary_HILIQ_20261018_063101.json，af3f29ab）
| 项 | AI 报 | 文件原值 |
|---|---|---|
| 60万 CAGR244 / 252 | 3.18% / 3.28% | 0.031790 / 0.032849 ✓ |
| 60万 MDD | −21.96% | −0.219603 ✓ |
| 60万 vs_wb t_hac | −1.41 | −1.408983 ✓ |
| 100万 CAGR244 / 252 | 4.39% / 4.54% | 0.043915 / 0.045387 ✓ |
| 100万 MDD | −22.72% | −0.227234 ✓ |
| 100万 vs_wb t_hac | −0.83 | −0.829348 ✓ |
| poolEW / wb CAGR244 | 12.68% / 11.60% | 0.126796 / 0.116042 ✓ |
| decisive | 三项 False | wb_floor_pass=False，t_hac_ge_2_50=False，beats_poolEW=False，beats_capadv_hiliq_recomputed=True，verdict_cap=FAIL，report_to_leo_allowed=False ✓ |
- t_hac 的 lag：L122 定义 HAC_H=20；L449 `hac_t(x, h=HAC_H)`；L444 `lag = max(h − 1, 1)`，即 **lag 19**，Newey-West Bartlett 核，与预注册 §6.6、§9 一致 ✓。
- AI 漏报一项：beats_capadv_hiliq_recomputed=True（capadv 重算 1.26%）。
- 这些数都基于现行 B3 口径，r2.11 后会变（预计 bp 级），只作参考。

## 9. 本次调查自身披露
- 两次过滤读取的进程峰值 RSS 约 391MB 和 411MB，超出 300MB 预算。原因是 pyarrow 按 instrument 过滤仍要解码整个 row group。没有与叶的运行重叠（A02 06:32:24 已结束），时长都在 1 秒以内。
- 临时文件在 /tmp/arch_b3_Xq2q；仓库只写本文件。
- 94322：Data 在 06:37:02 ET 按 Arch 06:36 指令已经 CONT（cont_94322_20261018_r2_10.md）；06:38 实测状态为 S。r2.11 开跑前须重新 STOP。


## 附：主 Agent 书面裁定（2026-10-18 06:45 ET）

- FIX2 审查（bd3abe5c §5-2）时，Arch 把 Data 的 fulla_carry 和本叶的成员递推判成同一口径，判断有误，记 **Arch P2**。
- 修复方式：出 r2.11，成员递推跨过 restored 行沿用上一日成员，并加一条硬断言；叶24 r9 同步修改。
- A01 产物（12 个文件）已移到 output/ai_factory/_void/leaf23_r2_10_b3_stop_20261018/，按 SHA256SUMS.before 核对过。
- 仍走 Plan A，A01–A03 重跑，先签 .ok 再跑。
- HILIQ 半边的「大概率 FAIL」只作内部记录，对外结论以 r2.11 的正式回执为准。
