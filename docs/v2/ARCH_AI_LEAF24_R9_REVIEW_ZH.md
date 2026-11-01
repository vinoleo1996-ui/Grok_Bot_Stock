# Arch 审核：叶24 r9（QuantLab AI）静态审查

- 审查时间：2026-10-18 约 06:40 ET（UTC−4）；06:46 ET 增补 P1-1（依据 Arch B3 诊断 561219c7）；只做静态审查，没有跑项目代码，也没读真实数据（只读了 parquet 元数据和 schema）。所有工作都在 /tmp/l24r9.NLBa 里做。
- 被审对象：research/g1g5_imax_intraday_alpha.py r9，sha256 b83cb8e65ce942a600a9ce985dd471a78c622f3676759955aa4cdf5f0a4ffa53（**未提交**，git status 显示 M）
- 基线：r7 = 已提交的 9b1d234:research/g1g5_imax_intraday_alpha.py（c5b79efa…，blob e1df8bb）；r8 归档 _recovery/ai/pre_r9_0627/（4135efba…）
- DIFF docs/v2/AI_LEAF24_R9_DIFF.patch 1452ccab…；内存估算 AI_LEAF24_R9_MEMORY_ESTIMATE_ZH.md 13ac4027…；CMD AI_LEAF24_R9_PROPOSED_CMD.txt 5bb2a02e…
- 参照：叶23 r2.10 脚本 f1344324…（commit 821a9107），Arch r2.10 审核 d804aa0e…
- 环境：qlvenv pandas 3.0.6 / pyarrow 25.0.1 / numpy 2.5.3

## 结论：代码 CONDITIONAL PASS，暂不签 .ok

P0 = 0。P1 = 1：pool_benchmarks 的递推在 restored 行处断开沿用，与叶23 逐字相同，依据 Arch 诊断 561219c7，见 P1-1；AI 将带修复重交 r9。P2 = 3，P3 = 7。
r9 各项改动按代码逐条看都是输出中性的。重合段按持仓名过滤（AI 请拍板的那一项）**同意**：最终输出和 held_alpha_missing_share 都逐行相同。签 .ok 之前必须满足三条：P1-1 按指定写法修好并复审、P2-1/P2-3 的实测补齐、P2-2 的五条判定写进 .cmd。

## 1. sha 链
- 在 /tmp 用 r7 原件 `git apply --check` 后再 apply，干净通过；结果 sha256 = b83cb8e6…，与仓库文件**逐字节相同**（cmp）。
- 和叶23 r2.10 逐函数（AST 源码段）比对：
  - pool_benchmarks、verify_primary_eval、trim、vm_status **逐字相同**。
  - merge、rss_watchdog、peak_check 都只差 docstring 第 2 行（"r9 (a) = leaf 23 r2.10 (a)" / "r8 (Arch P2; = leaf 23 r2.10 (d))"），代码相同。AI 说"merge 只差一行文档字符串"属实，另外两个函数也只差 docstring，没有披露，属 P3 级披露疏漏，不影响行为。
  - read_ok、check_meta、write_meta、panel_recheck、guard_fresh 也相同。verify_upstream / authorize 只少了叶23 专用的 resume 逻辑（叶24 全新跑、无 resume 键），属预期。
- py_compile（输出到 /tmp）：qlvenv 3.12 与系统 3.13.5 都通过。pyflakes（系统 python）0 条。AST 扫"缺 f 前缀但含 {name} 的字符串"0 条。

## 2. 逐项输出中性
### (a) build 按年读叶18/18v α
原写法一次读 date ≥ X2S；新写法每个 y 读 date ∈ [max(X2S, y-01-01), (y+1)-01-01)。合并时 P 已经过滤为 year==y、date ≥ gstart、≤ X2E。所以 P 能匹配到的 (date, instrument) 键集合完全落在新窗口内。原表 [X2S−10d, X2S) 的预热行原来就匹配不到（原表没有这些日期），两种写法都是 NaN → 0。
左连接保持左表顺序，右表重复键的展开顺序也相同（单文件 dataset 扫描保序）。**中性。**
dtype：叶18/18v 文件 date 为 timestamp[us]，instrument 为 large_string，与面板一致。过滤值是 python datetime，pyarrow 用 us 比较，没有 ns/us 或时区问题。

### (b) 【拍板项】重合段叶18/18v α 按"自身权重文件持有过的名字"过滤 —— **同意**
- 证明：Wls = Wl[Wl.instrument != BAL].merge(Al, how="left")，而 held_ = set(Wl.instrument) − {BAL}，取自**同一个**已过滤 target_weight>0 的 Wl。所以 Wls 每一行的 instrument 都在 held_ 里，Al 中所有可能匹配上的行都被保留，被丢掉的行本来就匹配不上。左连接结果的行数、行序、匹配值、NaN 位置（index 为 merge 后的 RangeIndex）全部相同。所以 held_alpha_missing_share = Wls.alpha.isna().mean() 相同，Jaccard（Wls 按 alpha 排序取前 N）也相同。
- 边界情况：
  1. 持有但 α 缺失：两种写法都是 NaN，计入 missing share，相同。
  2. 权重文件之外的日期：结果由左表驱动，与 Al 的日期范围无关。
  3. "先过滤还是先截日期窗"：只按 instrument 过滤、不截日期，不存在先后问题。
  4. PIT：过滤用的是全期持有名单（含未来持仓），但它只决定读哪些行，是匹配键的超集，不进入任何数值。
  5. Al 只在第 857–858 行被 Wls 使用，随即 del；不参与任何排名、z 值、截面统计或覆盖率计算。
- 不按"只读再平衡日行"实现，AI 的理由成立：Wls 覆盖全部持有日，只读再平衡日会把非再平衡日的持仓行变成 NaN，从而改变 held_alpha_missing_share。按名过滤才是等价写法。
- 极端情况（P3-2）：held_ 为空时 pyarrow 报 ArrowTypeError（large_string vs null，已用合成数据在 qlvenv 复现）；Wl.instrument 含 NaN 时 sorted() 报 TypeError。两者都会**失败退出、不会静默出错**。钉住的权重文件是 11,970 行 large_string，实际走不到这两个分支。

### (c) eval 面板不读 logmv/<universe 列>；选股只用再平衡日行
- PX 之后只用到 is_resume_day（blocked）、ret（rr）、close / is_resume_day / carry_col（H）。pool_benchmarks 有 PX 形参但函数体不用（与 r2.10 相同）。**中性。**
- pick_book：byd 只在 `d in byd and d in rd` 时读取。A_rd/G_rd 只是把 A/G 限制在 rd 上；对 rd 上的行，左连接匹配到的 gate 行也必在 rd 上，所以每个 rd 日的分组帧内容和行序相同（groupby 组内保序），sort_values 的输入数组相同，排序结果也相同。gate 列在子集上可能保持 int8（原来可能因 NaN 变 float），但只用于 `== 1` 比较，不影响结果。**中性。**

### (d) 提前释放、每年 trim、收益缓存每进程保留
- FE.rets 的 key 永远是 (2024, 2025, 2026)（X2 窗口），与预载调用相同。book_ret 里 rr.reindex(columns=...) / on.reindex 返回新对象，不原地改缓存。bal 取的是 `[BAL].loc[s:e].astype(float)` 的拷贝。pandas 3 默认 CoW，又多一层保护。FE.COST 临时切到 30bp 不影响缓存。**中性**，与 r2.10 (c) 结论相同。
- del Q / ER / Ee / Lu / IM / LS / RW 的位置：之后都没有再读（逐行核对）。trim() 只调 gc、pyarrow 内存池和 malloc_trim，不碰任何数值。

### (e) build 提前 drop logmv/adv20_yuan
- 第 647 行之后的 P 只用到 date、instrument、ret、ret_on、ind、col，以及之后 join 进来的 lmv1/beta120/... 列。logmv 只在 641/644 行出现，adv20_yuan 只在 641/645 行出现。**中性。**
- **但内存上没有效果（见 P2-1）。**

## 3. 阶段拆分与 meta 链
- 链条：
  - build_HILIQ：out_dir 必须为空，并跑 verify_leaf23_complete；敏感性口径另跑 verify_primary_eval（检查主口径 eval_HILIQ / eval_FULLA / eval 三份 meta）。
  - build_FULLA 需要 build_HILIQ。
  - eval_HILIQ 需要两个 build。
  - eval_FULLA 需要两个 build 加 eval_HILIQ。
  - merge 需要 eval_HILIQ 和 eval_FULLA。
  - 每一步都用 guard_fresh 防止覆盖。
  - check_meta 会核对每个 meta 的字段、全部 outputs 的 sha，以及 upstream 一层的 sha。build_HILIQ meta 的 upstream 记有叶23 五份 eval_meta 的 sha，所以叶24 **后续每一阶段都会通过 build_HILIQ meta 间接重核叶23 meta**。叶23 目录一旦变动，叶24 后续阶段就会拒跑。fail-closed。
- "after_leaf23_complete" 的执行方式：**由代码检查 meta，不是只写在文字里**。verify_leaf23_complete 要求叶23 主口径和 4 个敏感性的 eval_meta.json 都存在，并满足：
  - stage="eval"、variant 正确、面板 manifest 相同；
  - outputs 和 upstream 的 sha 都对；
  - 五份来自同一个（叶23 脚本 sha, 叶23 .ok sha）。
  叶23 没跑完时，S01 直接 SystemExit（meta 缺失）。r2.10 的 merge 写的就是 stage="eval" 的 eval_meta.json，接口对得上。serial_order 字符串只是 OK_FIXED 的固定值，真正起作用的是上面这些检查。
- P3-4：代码不钉"哪一个"叶23 脚本/.ok，只要求五份一致。签叶24 .ok 前 Arch 要人工核对叶23 五份 eval_meta 的 script_sha256 / arch_ok_sha256 就是已审版本和已签 .ok。

## 4. .ok 解析器白名单（共 54 个键，全部必填）
- OK_FIXED（20）：format, signed_by, scope, leaf, live, promotion, promotion_approved, allow_full, allow_smoke, allow_sealed, cs_panel_build_version, mechanism_tag, window_start, window_end, rss_limit_mb, serial_order, sensitivity_specs, run_niceness, tool_cmds_path, research_only
- OK_REQUIRED（9）：script_sha256, prereg_sha256, cs_panel_dir, cs_panel_manifest_sha256, out_dir, allow_sensitivity, tool_cmds_sha256, issued_at, expires_et
- TOOLS（21）：dep_fe, dep_selfcheck, dep_combo, dep_combo_legacy, dep_adg, dep_lc, dep_l18_{hiliq,fulla}, dep_l18v_{hiliq,fulla}, dep_l18w_{hiliq,fulla}, dep_l18vw_{hiliq,fulla}, dep_capadv600_{tw,nav}, dep_capadv1000_{tw,nav}, data_etf_daily_adj, data_mask, data_delisted（均为 *_sha256）
- TOOL_CLOSURE（4）：tool_closure_{adj_price, panel_stitch, moneyflow, nontextbook}_sha256
- 未知键拒、缺键拒、重复键拒、BOM 拒、空值拒。叶24 没有 resume 键（与叶23 r2.10 的 59 键不同），也没有 data_forecast / financials 键。
- 草案（**未安装**）：/tmp/l24r9.NLBa/ok_draft/ARCH_RUN_AUTH_LEAF24_R9_X2.ok.draft，sha256 ef0e0786e2a20af2136637659936d7d0eb9df288dc50ff1d5c6aab955fe1f07e。
  - 54 键齐全，OK_FIXED 20 项逐值相符（独立解析器校验），LF 换行、无 BOM。
  - live=false，promotion=false，promotion_approved=false。
  - issued_at=__ISSUED_AT__、expires_et=__EXPIRES_ET__ 都是占位，按现状会被 tz_iso 拒，fail-closed。expires_et 建议不晚于 2026-10-19T16:30:00-04:00（16:40–18:40 禁跑窗之前），具体由 Arch 定。
  - 所有 sha 都是 06:40 ET 实测，与 prereg_sha_leaf24.txt 和叶23 r2.10 .ok 的共有键（面板 manifest 5c44019d、mask c5433e80 = D1b 回执 pins、delisted 63590f23、etf 48b21e84、FE 2b49b10b、CMC 5658f612/bee23019、capadv、tool_closure）逐一一致。
- 配套 .cmd 草案（未安装）：/tmp/l24r9.NLBa/ok_draft/ARCH_TOOL_CMDS_LEAF24_X2.cmd，sha256 0db97de9…。按叶23 模板写，只含 CMC v1.1 top10_100w 一行并带 --arch-ok；top6_60w 那行等 Alpha 同意。注意：output/ai_factory/ARCH_TOOL_CMDS_LEAF24_X2.cmd 目前**不存在**。安装时 written_at 占位会被替换，tool_cmds_sha256 必须重测后写入 .ok。

## 5. 内存
- 红线 1536000 kB = 1500 MiB（1536000/1024，算式无误）。目标：峰值 + 180 MiB 余量 ≤ 1300 MiB，等价于复刻峰值 ≤ 1120 MiB。
- 各阶段：
  - eval HILIQ：1013 + 180 = 1193，达标（拆分复刻实测）。
  - merge：未测，只读两份 json，预计远低于目标，可接受。
  - build HILIQ：**只测到 2025 imax**（≥921），2026 年段没测；r8 复刻是 1063，推测 r9 低于这个数，**待补测**。
  - eval FULLA：实测 1262 的峰在重合段（读全量 2,821,833 行）。改成按持仓名读之后（FULLA 叶18 571,917 行 = 20.3%，叶18v 259,912 行 = 9.2%），下一个峰预计是 pool_benchmarks 2024 年段，约 1097，加余量约 1277。这是**推算**，**待补测**。
  - build FULLA：复刻实测 1135 + 180 = **1315 > 1300**。AI 估计 drop 能省 32 MiB、降到约 1283，**这个估计不成立**，见 P2-1。
- 备选方案的意见：
  - **(a) 用 unstack 代替 pivot_table**：AI 的前提不对。在 pandas 3.0.6 下，对 float32 值做 pivot_table（mean）**本来就返回 float32**（合成数据实测），unstack 也是 float32。所以中间结果和最终输出都**没有 dtype 变化**，数值完全相同（合成数据逐元素一致）。也因此它不能靠"float64 → float32"省内存，最多省掉 groupby 的中间开销，省多少要实测。
    - 重复键：pivot_table 对重复 (date, instrument) 静默取均值；unstack 会抛 ValueError("Index contains duplicate entries")，属于 fail-closed，相当于多了一道唯一性断言。ER 每天一组，键是否唯一取决于面板 (date, instrument) 是否唯一，现有写法也默认唯一。
    - 结论：**可以接受，不算 dtype 变化**，但优先级排在 (b) 之后，并且要实测。
  - **(b) 调换年份过滤和全量面板释放的先后**：按代码看输出中性。第 650–667 行之间 P 没有被修改，过滤条件只用 P 的 date/col/ind 和常量，Pf 照旧 `.copy()`。
    - 要求：Pf 必须放在 Q 建好**之后**、ER 循环**之前**，并立刻 `del P`（把 P 重新绑定到 Pf）；之前那版把 Pf 放在 Q 之前，峰值反而升到 1370。
    - 这样做以后，全量 P（含 logmv/adv20_yuan）在 e_id、pivot、imax 这个峰值段之前就被释放了，(e) 的 drop 也就没有必要了。
    - **推荐先做这一项并实测。**
  - 顺序建议：先把 P2-1 的 drop 改成真正释放（或直接做 (b)），实测 build FULLA；仍超 1300 再加 (a)；仍超就上报主 Agent。

## 6. 检查清单
- 过滤读取与合并两侧的类型：面板 / mask / 叶18 / 叶18v / 权重文件 / 叶23 产物的 date 都是 timestamp[us]、无时区，instrument 都是 large_string（读入 pandas 后为 str）。
  - 本脚本没有 merge_asof。
  - 所有 merge/join 两侧都经过 pd.to_datetime，单位都是 us。
  - 合成数据实测：在 pandas 3.0.6 里普通 merge 即使一侧 us、一侧 ns 也能正确匹配。
  - 过滤值都是 python datetime 或 str 列表，与列类型一致。**通过。**
- 缺 f 前缀的字符串：0 条。pyflakes：0 条。
- 只看退出码判成功：**是**，CMD 第 3 行写的是"前一步 exit 0 才跑下一步"，见 P2-2。
- 看门狗吞异常：`except Exception: pass` 仍在（与 r2.10 相同）。/proc 读取持续失败时看门狗会静默失效；段末的 peak_check 不吞异常（KeyError 会让进程崩溃退出），可以兜底。P3-1，沿用 r2.10 留待下一轮的条目。
- resume 与数据 pin 比对：叶24 没有 resume，25 步都是全新跑。数据 pin 与叶23 r2.10 .ok、D1b 回执逐一一致（见 §4）。

## 7. 问题清单
### P1
- **P1-1（阻断；pool_benchmarks 递推在 restored 行处断开沿用；与叶23 r2.10 逐字相同）**：依据 Arch 诊断 docs/v2/audit/leaf23_r2_10_run/ARCH_B3_FULLA_MISMATCH_DIAG_ZH.md（561219c7…）。
  - 现行写法（r9 第 465 行）是 `carry_nc = (~has) & (sus == 1.0)`。面板有行就取该行 col，而 restored 行的 col 恒为 False，所以只要同一段停牌里，最后一个正常交易日和复牌行之间夹着一条 restored 行（先复牌又停牌，或先盘中停牌再全天停牌），S 就会被置 False、沿用链断开。这与 Data 的 fulla_carry（取复牌前最后一个有成交且 mask 未判停牌的交易日）不一致。
  - 叶23 eval_FULLA 已于 06:32:24 ET 因此停跑：carry_mismatch=2，分别是 002868.SZ 2025-04-30 和 603056.SH 2026-01-14。叶24 r9 的 pool_benchmarks 逐字相同、输入相同（同一面板 5c44019d、mask c5433e80、delisted 63590f23，PX 自 2024-05-20 起，col=fulla，carry_col=fulla_carry），eval_FULLA 必然以同样的 2 行停跑。
  - 副作用（HILIQ 也受影响，只是校验抓不到）：每次复牌之后的 d+1 天，Mp 都等于 restored 行的 col，也就是 False，相当于每段停牌复牌后掉出池子一天。
  - **要求的修法（AI 重交 r9 时必须包含，并与叶23 r2.11 逐字一致）：**
    1. `carry_nc = (sus == 1.0) & (~has | restored)`，restored 取自面板 row_origin == "restored"。只要 pr 多读一列 row_origin，pivot 后按 has 对齐。
    2. 流通市值权重同样沿用：B / B_dd 的 `.mask(carry)` 要使用新的 carry，让 restored 行的 MV 沿用停牌前的值，不取当行 logmv。A_nc、carry_dd 等影子和披露写法统一从新的 carry_nc 派生。退市截断 gone、P2-B 与 cut_fail 断言不变。
    3. 硬断言（逐年，在面板有行处）：mask suspended=True ⟺ row_origin=restored，不成立就 SystemExit 停跑报 Arch。还要写明 mask 无行（sus 为 NaN）的面板行怎么处理（建议同样停跑）。
    4. 「沿用名·日」的原因计数改为按 (S & sus==1) 计，不再按 (S & ~has)。B3 校验两侧都保留，修后预期 0 不一致；可另加披露计数「复牌后 d+1 的 Mp == 复牌行 carry」。
    5. 不接受的做法：改 Data 面板，或者把这 2 行加白名单、放宽校验。
  - 对叶24 的连带影响：
    - pool_benchmarks 每年要多读一列 row_origin（large_string，2018–2026），eval 的 pb 段峰值会上升。eval FULLA「下一峰在 pb 2024 段，约 1097」的推算因此要在修后重新实测，eval HILIQ 的 1013 也要重测。
    - 修后 HILIQ 的 Mp 和基准也会变（诊断估计在 bp 级）。
    - 重交后 r9 的 sha 会变，§4 的 .ok 草案作废，需要重新生成（只换 script_sha256，其余 pin 重测）。
    - 复审范围：只看 pool_benchmarks 的 diff 和上述断言，同时核对与叶23 r2.11 的同名函数逐字一致。本审查其余结论（§2 的输出中性、拍板项 (b)、§5 的备选方案、P2/P3）不变，继续有效。
### P2
- **P2-1**：r9 (e) 的 `P = P.drop(columns=["logmv","adv20_yuan"])` **不释放内存**。
  - 在 pandas 3.0.6 下，P 的 ret/ret_on/logmv/adv20_yuan 合并在同一个 (4, N) float32 块里，drop 之后的新 P 是这个块的**视图**（合成数据实测 np.shares_memory = True）。原来的 4 列块会一直活到第 667 行 `.copy()`。
  - 另外这两列在面板里是 float32，不是 float64，所以就算真能释放，也只省约 15 MiB，不是 32 MiB。
  - 所以 build FULLA 仍按 1315 > 1300 计，内存估算 §2 说明里的"约 1283"作废。
  - 修法：做 §5 的 (b)；或者改成真正复制释放，例如 `P = P.drop(columns=[...]).copy()`，但复制本身会带来一个瞬时峰值，同样要实测。
- **P2-2**：AI 提议的 CMD 只看退出码。叶24 正式 .cmd 和运行条件必须照叶23 写入五条判定，每一步都要同时满足：
  1. exit 0；
  2. `<stage>_meta.json` 已写出，stage / script_sha256 / arch_ok_sha256 / variant 正确；
  3. 日志里每一段都有 peak_check 行，没有 RSS_GUARD_KILL / STOP / refused；
  4. meta 的 peak_rss_mb < 1500；
  5. meta outputs 列出的文件齐全，sha 与 meta 一致。

  有一条不满足就停，报 Arch。
- **P2-3**：三处内存未实测：build HILIQ 2026 段、eval FULLA（按名过滤后）、build FULLA（P2-1 修好以后）。实测要等叶23 跑完、主 Agent 放行，单任务，复刻里要包含 r9 的全部改动以及 P2-1 的修法。
### P3
- P3-1：看门狗 `except Exception: pass`（沿用 r2.10 的条目）。
- P3-2：held_ 为空或 instrument 含 NaN 时失败退出（fail-loud，实际走不到）。可以加一句显式检查、给出清楚的报错。
- P3-3：内存估算文档有两处与事实不符：logmv/adv20_yuan 写成 float64（实际 float32）；"pivot_table 中间结果是 float64"（pandas 3.0.6 下是 float32）。
- P3-4：verify_leaf23_complete 不钉叶23 的具体脚本/.ok sha，签字前由 Arch 人工核对。
- P3-5：r9 脚本还没提交（git status M）。提交内容必须正好是 b83cb8e6，.cmd 表头要记 commit。
- P3-6：rss_watchdog / peak_check 的 docstring 与 r2.10 有差异但没有披露（代码相同）。
- P3-7：流程方面。
  - research/__pycache__/g1g5_imax_intraday_alpha.cpython-313.pyc（mtime 10-18 05:53:45，sha 764d7090…）是早先记录过的 P3 残留 pyc，不是这次审查产生的；删不删由 Arch/主 Agent 决定。
  - AI 在叶23 运行期间跑了 schema 检查进程（约 515MB、约 1 秒），已自行披露。下不为例：叶23 运行期间连只读进程也不要跑。
  - 94322 在 06:37 ET 显示状态为 S（运行中），不是 T。process_check 只记录 scripts/acquire/、不拦截，所以"叶24 开跑前先 STOP 94322"这条只能靠流程保证。

## 8. 签 .ok 前还要做的事
1. P1-1：AI 按指定写法重交 r9：carry_nc = (sus==1)&(~has|restored)，市值同样沿用，加 mask 停牌 ⟺ restored 的断言。Arch 只复审 pool_benchmarks 的 diff，并核对与叶23 r2.11 逐字一致。另外，叶23 r2.11 的主口径加 4 个敏感性要全部跑完并通过 Arch 审，叶24 才能过 verify_leaf23_complete。
2. 实测（叶23 跑完、主 Agent 放行之后，单任务）：
   - build HILIQ 全程；
   - build FULLA，带 (b) 或 P2-1 的修法；
   - eval FULLA，按名过滤，并带 P1-1 修法（pb 段多读 row_origin）；
   - eval HILIQ 重测（pb 改了）。

   每一项都要 VmHWM + 180 ≤ 1300 MiB。
3. AI 提交脚本（sha 不变），Arch 安装 .cmd（实测 sha）。Arch 重测全部 pin 后签 .ok：issued_at / signed_et 用 `date +%Y-%m-%dT%H:%M:%S%:z` 生成，expires_et 带时区、在 10-19 16:40 之前。
4. .cmd / 运行条件写入 P2-2 的五条判定。每一步开跑前确认 94322 已 STOP。
