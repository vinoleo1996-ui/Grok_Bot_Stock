# Arch：叶23 r2.11 静态审查（QuantLab AI）

- 审查时间：2026-10-18 约 06:50–06:59 ET（UTC−4）。只做静态审查：没有 import 或运行项目代码，没有读任何价格、收益、权重、因子、面板或 mask 的值；只读了代码、文档、.ok/.cmd/meta JSON，以及 parquet 的 schema 与 footer 元数据（行数、编码）。工作目录 /tmp/l23r211.qO6G；py_compile 输出写到 /tmp；pyflakes 在 /tmp 副本上用 PYTHONPATH=/tmp/pf 运行。没有写 output/、data/、.ok、.cmd，没有动 git，没有碰 94322。
- 对象：research/g1g5_sue_desens_cs_alpha.py **4aa19627cd65e62cad1544e4cab75d9f9d1db593c5066f13bbb7c2780871b0a1**（未提交）。基线 r2.10 f1344324（commit 821a9107，归档 _recovery/ai/pre_r2_11_0643/，sha 一致）。
- DIFF docs/v2/AI_LEAF23_R2_11_DIFF.patch 9cd94387c4223a243e614da7559301f7d7cea0737d251aac440c9f46b8f6a7da。
- 步骤表 docs/v2/AI_LEAF23_R2_11_PROPOSED_CMD.txt **14899dc8011e008a3b23ac96bda45f8a7f10e7357b499fb8b4774e57cb1d1793**（取代 b44ad8b6，见 §6）。
- 条件增补 docs/v2/audit/leaf23_r2_11_run/AI_LEAF23_R2_11_CONDITIONS_ADDENDUM_ZH.md **876ee6b09f7e44d76afb8f3ab7737556d383f5a64d2ef55321609819809317d3**（取代 01339cb5，见 §6）。
- 依据：B3 诊断 fd6367f7（AI 引用的 561219c7 是追加主 Agent 裁定附节之前的版本）、r2.10 审查 d804aa0e、叶24 r9 审查 b771b4be（P1-1）。
- live=false；promotion=false。

## 0. 结论
**通过（PASS，P0=0，P1=0，P2=1，P3=6）。可以签 .ok。** 草案见 §8；签发前要先完成 §9 的安装步骤和开跑前提。
- B3 修复与 Arch 诊断 §4、叶24 r9 审查 P1-1 的五条要求逐条一致。诊断里那两条不一致记录按新代码推演后 Mp=True=fulla_carry，B3 预期 0 不一致。
- 新硬断言在钉住的数据上**按构造成立**，不会在合法数据上误触发（§2.3）。
- 三个 P3 修复正确；docstring 改动经 AST 比对确实只改注释。
- 唯一 P2 是内存文档口径：FULLA 的「≤约1195 MiB」只覆盖到 pool_benchmarks 结束为止。另外敏感性全新链里 build FULLA 的峰值约 1374 MiB，AI 的估算没有覆盖。两者都在硬线 1536000 kB 以下，不阻塞。

## 1. sha 链与 diff
- 在 /tmp 用 r2.10 原件 f1344324 执行 patch -p1：dry-run 和实际打补丁都干净，结果 sha=4aa19627，与仓库文件 cmp 逐字节相同。
- 共 13 个 hunk，1 个文件：
  1. 模块 docstring 加 r2.11 段；
  2. rss_watchdog（docstring + except 改为 fail-closed）+ peak_check docstring；
  3. trim docstring；
  4. authorize 加 resume_upstream_ok_pins_equal；
  5. 新增 RESUME_PIN_KEYS + resume_pins_equal；
  6. pool_benchmarks docstring；
  7. 每年多读 row_origin → _rs；
  8. rst / bad_rs 硬断言 + 新 carry_nc；
  9. del A, B（保留 sus）；
  10. 沿用名·日改按 S & sus==1；
  11. 年末 del 增加 sus；
  12. diag 的 rule / not_suspended_note 文字；
  13. merge docstring。
- 都在 AI 的摘要里，只有第 12 项（写入 summary 的 diag 说明文字）没有单列，见 P3-3。
- AST 比对：函数层面改动的只有 rss_watchdog、peak_check、trim、authorize、pool_benchmarks、merge，新增函数只有 resume_pins_equal。其中 peak_check、trim、merge 去掉 docstring 后与 r2.10 的 AST 完全相同，**确实只改注释**；rss_watchdog 的代码改动只在 except 分支。

## 2. B3 修复逐项
- carry_nc = (sus == 1.0) & (~has | rst) ✓。
  - rst 来自 pr.row_origin.eq(“restored”).astype(“float64”)，读入后立即 drop 字符串列 ✓。
  - pivot 后 .fillna(0.0) == 1.0，没有面板行的位置为 False ✓。
- B / B_dd：代码行没变，但遮罩用的是 carry = carry_nc & ~gone、carry_dd = carry_nc & ~gone_dd，都从新的 carry_nc 派生。restored 行在 B 中为 NaN，ffill 后沿用停牌前的 MV，不取当行 logmv ✓。
- A_nc、A_dd、carry_dd 都从新 carry_nc 派生 ✓。
- 硬断言 bad_rs = (has & ((sus == 1.0) != rst)) | (has & sus.isna())：
  - 两个方向都覆盖：mask 停牌但不是 restored，或是 restored 但 mask 未停牌。
  - sus 为 NaN（面板有行、mask 无行）也算违反 ✓。
  - 违反就 SystemExit，信息里带前 5 个样例 ✓。
  - 断言只在面板有行处检查；mask 有行而面板无行时不断言，按设计走沿用（sus=1）或断链（sus=0）✓。
- 沿用名·日：cw = S & (sus == 1.0) ✓。sus 保留到年末，年末 del ✓。
- 没改的部分：
  - 退市截断 gone / gone_dd、cut_fail 断言、P2-B（nd_x2）、B3 的 Mp vs carry_col 比对、.BJ 计数逐字不变。
  - 不改面板，没有白名单 ✓。

### 2.1 两条记录推演（取诊断 §2 的序列）
- **002868.SZ（col=fulla）**：
  - 04-21 v1 行（sus=F）：S=True，MV=lmv(04-21)。
  - 04-22～04-25 无行（sus=T）：沿用 True。
  - 04-28 restored（sus=T，rst=T，断言通过）：沿用 True，MV 仍是 04-21 的值。
  - 04-29 无行：沿用 True。
  - 04-30 restored/resume：Mp(04-30)=S(04-29)=**True = fulla_carry ✓**。
  - 该名不在 delisted_master 里；04-30 起 st=True 不影响这一天的 T−1 判断。
- **603056.SH**：
  - 01-08 v1 行：S=True。
  - 01-09 restored/intraday_halt（sus=T，rst=T）：沿用 True；旧规则在这里置 False。
  - 01-12、01-13 无行：沿用 True。
  - 01-14 resume：Mp=**True = fulla_carry ✓**。
  - delist_date 是 2026-03-31，截断不早于 03-31，不影响。
- HILIQ：诊断核对过窗口内同类记录为 0。新规则只在「同一段停牌里夹着 restored 行」时改变复牌当天的 Mp，所以 HILIQ 侧 B3 不会新增不一致。

### 2.2 边界情形
- **年段首日的复牌行**：递推每年用 p0 行注入上一年末的 sp / mp_，然后 ffill。首日沿用时 A、B 为 NaN，取上年末状态，状态跨年传递 ✓。names 包含 sp.index ✓。
- **退市且 mask 停牌**：delist_date 之后 carry=False，A=val.where(has,0)=0，S=False，cut_fail 照常兜底 ✓。
  - restored 行要求当天有成交，不会出现在退市日之后。
  - last_trade_date 之后到 delist_date 之间按停牌沿用，与原规格一致。
- **之前没有任何行的代码**：sp 缺失时 fillna(0)，S=False，MV=-inf（权重 0）。
  - Data 侧 classify_restore 只在有「上一个有成交且 mask 未停牌的交易日」、并且 hiliq/fulla carry 至少一个为 True 时才生成 restored 行，所以不会出现「首行就是 restored」的情况 ✓。
- **restored 但 mask 未停牌**：断言拦截。按构造不可能出现，见 §2.3。
- **mask 有行、面板无行**：属于设计分支，不断言 ✓。
- **复牌后 d+1**：新规则下 Mp(d+1)=S(复牌日)=停牌前的成员状态，诊断 §3 指出的「复牌后掉出池子一天」副作用随之消失（HILIQ 也一样）。这正是数字会变的原因，AI 增补 §7 已如实说明。

### 2.3 断言会不会在合法数据上触发（只读代码和 schema 核对）
- 面板构建（scripts/fix_sd1/build_cs_panel_v2_resumefix.py）：
  - 面板行 = 钉住的 mask 中 keep_v1 | restored 的行，其中 keep_v1 = fulla | in_universe。
  - 面板用的 mask 就是本叶钉的 c5433e80：verify_panel 要求 D1b 回执 pins.mask_sha256 == .ok data_mask_sha256。
  - 因此**每个面板行都有 mask 行**，sus 为 NaN 不会发生。
- v1 行不会是 mask 停牌：
  - fulla = ~st & ~suspended & ~young & adv20≥3e6（L101）。
  - in_universe = ~(st | suspended | young | adv_fail)（research/strategy_hiliq_universe_v1.py L152）。
- restored 行一定是 mask 停牌：sd1_common.classify_restore 的候选条件第一项就是 suspended（L353），intraday_halt 类 restored 行也一样。
- row_origin 只有 “v1” / “restored” 两个取值（构建 L117），restore_reason 为 “resume” / “intraday_halt” / 空串。
- 结论：**「面板行 mask 停牌 ⟺ restored」在钉住的数据上按构造成立**，断言方向正确，不会误触发。若真触发，说明面板或 mask 被换过，应当停跑。

## 3. 三个 P3 修复
- **看门狗**：异常时打印 RSS_WATCHDOG_ERROR <类型>: <信息> 并 os._exit(137) ✓。peak_check 本身不吞异常。
- **resume 时比对上游数据 pin**：
  - RESUME_PIN_KEYS 共 15 个：prereg、cs_panel_dir、cs_panel_manifest_sha256、cs_panel_build_version、data_mask/delisted/forecast/financials/etf_daily_adj、dep_fe、dep_l19_hiliq/fulla、dep_l20_hiliq/fulla、dep_capadv_leg。
  - 对照 fund / build 实际读取的输入：fund repin dep_fe、financials、forecast；build repin dep_fe、l19、l20、etf、capadv_leg；panel_recheck 覆盖 mask、delisted 和面板年文件。FE 模块没有导入其他 research 模块。**15 个正好覆盖 fund/build 的全部输入** ✓。
  - 不比的 44 个键：script_sha256（按设计必须不同）、resume_*、固定值键、管理键（out_dir、issued_at、expires_et、tool_cmds_*、allow_*），以及只在 eval 或下游用的键（dep_l20w_*、capadv600/1000 tw/nav、selfcheck、adg、lc、combo、combo_legacy、tool_closure_*）。这些键 eval 重跑时会按本 .ok 重新核对，排除合理。
  - 查找方式：在 output/ai_factory 和 _consumed 下 glob ARCH_RUN_AUTH_LEAF23_*.ok，按 sha 匹配。_consumed/ARCH_RUN_AUTH_LEAF23_R2_9_X2.b21e9952_CONSUMED_20261018_0603ET.ok 能匹配上（sha=b21e9952 ✓）；找不到或不一致就 SystemExit（fail-closed）。
  - 实测：r2.9 .ok 的 15 个值与本草案逐值相同 ✓。
- **resume 仍接受与当前脚本不同的上游脚本**：检查项 resume_upstream_is_other_script 要求 d199b778 ≠ 4aa19627，成立 ✓。verify_upstream 用上游的 script/.ok sha 校验 r2.9 的三份 meta（f393b3e9 / fb4b2ad4 / 07391924，现场实测 sha 一致，stage、variant、manifest 5c44019d 也对）✓。
- **步骤表五条判定**：C1 exit 0；C2 meta 写出且字段和 outputs sha 正确；C3 9 行 pool_benchmarks peak_check + peak_check eval <uni> + STAMP（merge 为 peak_check merge + STAMP）；C3b 无 RSS_GUARD_KILL / RSS_WATCHDOG_ERROR / STOP / refused / Traceback；C4 VmHWM ≤ 1536000 kB 且 meta peak_rss_mb < 1500；C5 无其他读真实数据的进程。
  - 与代码核对：peak_check 标签 L579 / L1010 / L1036、STAMP 在 L1014 / L1036、年循环 2018–2026 共 9 段（idx 截止 2026-10）一致 ✓。
  - **不是只看退出码** ✓。

## 4. 与叶24 r10 必须逐字节相同的函数（供后续核对）
- 必须一致：vm_status、rss_watchdog、peak_check、trim、pool_benchmarks（含新断言）、merge、verify_primary_eval。
- 同时建议保持一致：read_ok、check_meta、same_run、write_meta、panel_recheck、verify_panel、repin、repin_file、guard_fresh、xtext、xparquet、process_check、ancestors、not_expired、tz_iso、cmc_cmd_ok、ic_tstat_hac、hac_t、rank_ind、pick_book、style_feats、bench_ret、load_fin、read_panel、out_dir。
- 预览：对仓库当前的 research/g1g5_imax_intraday_alpha.py（53d3f8b1）做函数源码切片比对，上面这些全部逐字相同。不同的只有 authorize、build、evaluate、is_primary、variant_tag、verify_upstream，这些是叶专属，属于预期差异。
- 叶24 r10 正式送审时要按其送审 sha 重做这项比对。

## 5. 检查清单
- **dtype**：
  - 面板 2018–2026 的 row_origin、restore_reason 都是 large_string（parquet 字典编码），date 为 timestamp[us]，instrument 为 large_string，fulla/hiliq 为 bool，logmv 为 float32，ind 为 int16。
  - mask 的 date 为 timestamp[us]、suspended 为 bool。
  - 新读取没有新增过滤条件；rst 与 has 出自同一个 pr pivot，对齐方式相同；沿用名·日 merge 的两侧 date 都是 us。**通过**。
- **缺 f 前缀的字符串**：AST 扫描 0 条。
- **pyflakes**：0 条。py_compile 在 qlvenv 3.12 和系统 3.13 下都通过，cfile 写在 /tmp。
- **只看退出码**：否，五条判定 ✓。
- **内存**：
  - row_origin 按年读入。面板最大年 2025 为 1,204,703 行（footer 元数据）。
  - pandas 3.0.6 / pyarrow 25 下 str 列由 arrow 存储：偏移 8 B/行 ≈ 9.6 MB，值约 2.4 MB，加上解码时的字典索引约 4.8 MB（瞬时）；转成 float64 标志约 9.6 MB；rst pivot 约 10.6 MB；sus 保留到年末约 10.6 MB。
  - 每个年段新增约 25–45 MiB，与 AI 的 +20–60 一致；HILIQ ≤ 约 1144 MiB 可信。FULLA 见 P2-1。

## 6. 步骤表 / 增补的新版本（06:57 ET AI 更新）
- 步骤表 14899dc8：去掉 # 行后有 27 条命令。逐字节对照审过的 27 条（按 b44ad8b6 原文的固定前缀 + 各步参数逐行重建），**完全相同**。
  - 顺序注释写的是「主口径 A01–A03 → 敏感性 A04–A27 → 叶24 内存复测 → 叶24 正式运行 → CMC」（主 Agent 06:55 ET 书面确认），**符合裁定** ✓。
  - 说明：两个旧版文件没有入 git，手头没有逐字节副本，所以是对照审过的命令内容重建比对。
- 增补 876ee6b0：
  - §5 代码块里的 27 条 A 行与 14899dc8 的命令行逐字节相同 ✓。
  - §1 钉的步骤表已改为 14899dc8 ✓。
  - §2 顺序文字同上 ✓。
- 与 .ok 的 serial_order 固定值 fund>build_HILIQ>build_FULLA>eval_HILIQ>eval_FULLA>merge>sensitivities>leaf24 一致；脚本门禁 verify_primary_eval 要求主口径三份 eval meta 齐全后才允许跑敏感性 ✓。
- 增补仍有勘误（不改命令和判定，由本审查记录、取代原文），见 P3-1：
  1. §9 末行「结果 sha = {S}」是没有填的占位符，正确值是 4aa19627cd65e62cad1544e4cab75d9f9d1db593c5066f13bbb7c2780871b0a1；
  2. 诊断依据 561219c7 应读作现行 fd6367f7（同一文件，后者追加了主 Agent 06:45 裁定附节）。

## 7. 问题清单
### P2
- **P2-1（内存文档口径，不阻塞）**：
  - (a) FULLA「≤约1195 MiB」只覆盖到 pool_benchmarks 结束：r2.10 A02 在 B3 处就停了，B3 之后的 FULLA 各段（books、分位、叶20 rho 等）没有实测记录。可用的上界是 r2.10 审查 d804aa0e §4 的 FULLA ≈ 1320 MiB，加本次 +60，约 1380 MiB。低于硬线 1536000 kB（1500 MiB），超过 1300 目标；按主 Agent 裁定，1300 只是目标值，以实跑确认。
  - (b) A04–A27 敏感性是全新链，要重跑 fund/build。r2.9 主口径 meta 实测 peak_rss_mb：fund 1237.7、build_HILIQ 1230.8、**build_FULLA 1373.7**。AI 的估算完全没有覆盖 fund/build。按 r2.9 的读数在硬线以下，余量约 126 MiB；sig-sue / denom-daily 变体可能读得更多，没有实测。
  - 处理：看门狗、peak_check 和 C4 会兜底，超线就停。回执里按这两个上界写，不要写「≤1195」。

### P3
- **P3-1**：增补的两处勘误，见 §6；以本审查为准，不要求重出增补（重出会改 sha）。
- **P3-2**：carried_to_window_end 披露清单仍按 VAL 为空判定。窗口末如果是 restored 沿用行，不会列进清单。只影响披露，AI 已在增补 §6 中自行披露。
- **P3-3**：diag 里写入 summary 的 rule / not_suspended_note 文字改了，没有在 AI 摘要中单列。只改文字。
- **P3-4**：现行 .cmd（6c65f6c3）头注释里的 script_sha256 还是 r2.10 的 f1344324。脚本不读这个注释（cmc_cmd_ok 只看 CMC 行），但卫生上应更新。已重拟，见 §8。
- **P3-5**：.ok 解析器的白名单 = 必填集合，共 59 键，**没有可用来钉条件增补或步骤表的键**，加新键会被当作 unknown 拒绝。因此改为在 .cmd 头注释里写明两者的 sha，经由 .ok 的 tool_cmds_sha256 间接钉住。脚本运行时不核对这两个 sha，执行方在 A01 前必须人工 sha256sum 核对（列入 §9）。
- **P3-6**：时间窗。增补沿用 r2.7 条件文档 §3「10-19 04:30 ET 后不起新步」（原因：nightly 之后要重新钉 forecast）。草案 expires_et 因此取 2026-10-19T04:30:00-04:00，不取 16:30。若要放宽，须由 Arch 在增补中明文改写 §3，并确认 forecast pin 在 nightly 之后仍有效。参考耗时：r2.10 A01 eval HILIQ 用时 49 s。

## 8. .ok / .cmd 草案（未安装）
- 位置：/tmp/l23r211.qO6G/ok_draft/。
- **.cmd 草案** ARCH_TOOL_CMDS_LEAF23_X2.cmd，sha **9ce882871a0f773fefcdbc5461665029d6d6d1dee5f138f3db6298e3f7a18c7e**：
  - 头行 script_sha256 改为 4aa19627，written_at=2026-10-18T06:58:00-04:00；
  - 新增一行注释，钉步骤表 14899dc8 和增补 876ee6b0，写明单次有效、勘误见本文档；
  - 其余内容（CMC v1.1 行等）与 6c65f6c3 逐字相同。
- **.ok 草案** ARCH_RUN_AUTH_LEAF23_R2_11_X2.ok（草案 sha df866a21e50ccc8fdc09ea2b09d05339abf300f07c24e4f9a6dd7d68a5802806；填写 issued_at 后 sha 会变）：
  - 以 97964bb1 为底，59 键，键序不变，每行都符合 ^[a-z0-9_]+=\S+$，无 BOM。
  - 改动的键只有三个：script_sha256=4aa19627…；tool_cmds_sha256=9ce88287…；issued_at=PLACEHOLDER_FILL_AT_INSTALL（tz_iso 会拒绝占位值，未填写之前 fail-closed）。
  - expires_et=2026-10-19T04:30:00-04:00。
  - serial_order 保持解析器要求的固定值。
  - 其余 pin 全部现场重测：prereg 8f5d8ac4、manifest 5c44019d、mask c5433e80、delisted 63590f23、forecast f1e59284 等，以及全部 22 个 TOOLS 和 4 个 closure 键，与 97964bb1 相同。
  - resume 键保留：d199b778 / b21e9952 / f393b3e9 / fb4b2ad4 / 07391924。

## 9. 安装步骤（由 Arch 执行，本审查没有执行）
1. 前提：
   - 94322 已由 Data 重新 STOP（状态 T）并留证据；
   - leaf23_sue_desens_cs/ 里只有 r2.9 的 fund/build 产物（现场核对：没有 summary_HILIQ / eval_* 文件，A01 产物已在 _void）；
   - 没有其他读真实数据的进程。
2. 作废 97964bb1：把 output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_10_X2.ok 移到 output/ai_factory/_consumed/ARCH_RUN_AUTH_LEAF23_R2_10_X2.97964bb1_CONSUMED_<YYYYMMDD_HHMM>ET.ok；把现行 .cmd 移到 _consumed/ARCH_TOOL_CMDS_LEAF23_X2.6c65f6c3_SUPERSEDED_<YYYYMMDD_HHMM>ET.cmd。移动前后都核对 sha。
3. sha256sum 复核：
   - 脚本 = 4aa19627、步骤表 = 14899dc8、增补 = 876ee6b0；
   - .cmd 草案 = 9ce88287；
   - 重跑 /tmp/l23r211.qO6G/mkok.py 的校验部分，确认 pin 没变、15 个 resume pin 与 b21e9952 相同。
4. 用 python 写临时文件再 os.replace，把 .cmd 草案装到 output/ai_factory/ARCH_TOOL_CMDS_LEAF23_X2.cmd，装后核对 sha = 9ce88287。
5. 在 .ok 草案里把 issued_at 填成当时的 ISO 时间（带 -04:00，早于 expires_et），同样用 tmp + os.replace 写到 output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_11_X2.ok。记下新 sha，通知 AI，并写进回执。
6. 安装后自检：
   - 59 行、正则全过、无 BOM、无重复键；
   - tool_cmds_sha256 == 实际 .cmd 的 sha；
   - script_sha256 == 实际脚本的 sha。
7. AI 按 14899dc8 从 A01 起逐步执行，每步按五条判定，有一条不满足就停。按主 Agent 06:45 裁定 ③，前一个进程确认退出之前不得启动下一步。

## 10. 本审查自身披露
- 读 parquet footer 元数据（9 个面板年文件和 mask 的行数、编码、schema）的进程，用 qlvenv 运行，约 0.4 s，不读任何列值。
- 读取期间 94322 在运行（按指令没有碰），按规则这不算运行。
- 那次元数据读取的 python 是用 shell heredoc 传入的（不是写文档）。本文档用 python 写临时文件再 os.replace 写入，没有用 heredoc。
