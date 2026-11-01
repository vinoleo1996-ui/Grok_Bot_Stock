# Arch 审查：叶23 r2.10（静态审查）

- 审查时间：2026-10-18T06:28:58-04:00
- 审查人：QuantLab Arch
- 方式：只读静态审查。diff 只在 /tmp 新目录里打。没有运行或 import 项目代码，没有跑测试。真实数据只用 pyarrow 读元数据。
- 结论：**PASS**。推荐**方案 A**（主口径只重跑 eval_HILIQ → eval_FULLA → merge，fund/build 沿用 r2.9 产物）。没有 P0/P1。.ok 和 .cmd 草稿见第 9 节，未安装。

## 1. sha 链
- 基线 _recovery/ai/pre_r2_10_0605/ = d199b778（r2.9）。diff ac1adb91 在 /tmp 副本上 patch -p1 干净打上，结果 f13443240e204a54611e9c9123d9367f1365d99b07c09534fceebfbfe50fda10，与工作区逐字相同。
- diff 实际是 27 个 hunk，不是 24 个（P3，只是描述不准）。
- 预注册 8f5d8ac4 未变。pyflakes 0 条；py_compile（cfile 在 /tmp）通过。

## 2. 续跑判定（关键）
fund 和 build 的代码路径有改动，但逐条证明输出不变：
- fund：只改了 to_session 的 NaT 写法（np.datetime64("NaT", 日历单位)）。dtype 本来就是日历的 [us]，填进去的都是 NaT，数组逐元素相同。fund 用到的其他函数（ymd、calendar、read_panel、current_records）未改。
- build：ev/evo 的 astype 从年循环里挪到循环前，单位取自 read_panel(panel, 2024, ["date"], X2S) 的 dtype。read_panel 的转换与循环里 P 的读法相同，都是 [us]；循环里加了 dtype 不同就 STOP 的检查。merge_asof 的键和结果都不变。
- pool_benchmarks、pick_book、trim、缓存这些改动只在 eval 里。build/fund 不调用它们。
- 全局多了 import pyarrow、ctypes 和 trim()：不影响任何值。
- 输入：b21e9952 里 22 个 TOOLS、4 个 TOOL_CLOSURE、prereg、panel manifest 与今天重测的值逐个相同；forecast f1e59284、manifest 0bdabc47 未变。
- **所以 fund/build 产物仍然有效，方案 A 成立。**

r2.9 产物核对（Data/Arch 移走 5 个半截 eval_weights 之后）：
- fund_meta f393b3e9…、build_HILIQ_meta fb4b2ad4…、build_FULLA_meta 07391924…，三个文件 sha 都对。
- 三份 meta 的 stage、variant=primary、script=d199b778、arch_ok=b21e9952、prereg、panel manifest 都对。
- 列出的输出 3 + 7 + 7 = 17 个文件，sha 全部对。upstream 链（build_HILIQ←fund，build_FULLA←fund+build_HILIQ）全部对。
- out_dir 里没有 meta 之外的文件。外部 g1g5_sue_desens_cs_* 半截文件已在 _void，output/ai_factory 下没有残留。

续跑校验是否严格、失败即拒：
- 五个 resume 键必须全是 "none" 或全是 64 位小写 hex，混着写就拒。
- 钉了值时：每个 meta 先比文件 sha，再按 check_meta 比字段（script/arch_ok 换成 r2.9 值，其余同本次）、每个输出 sha、每个 upstream sha。任何一项不对就 SystemExit。两个 universe 都覆盖。
- 钉了值时，主口径 fund/build 不许启动；resume 脚本 sha 不能等于本脚本。
- 不填 resume 时，主口径 eval 要求同脚本 meta，r2.9 meta 会被拒。也是失败即拒。
- 半截产物：meta 只在阶段末写，半截阶段没有 meta，会被拒；eval 的 guard_fresh 会拒绝已有的 eval_weights_<uni>_*。
- 敏感性一律不走 resume，自己从 fund 开始全新跑，且要求主口径 eval_HILIQ、eval_FULLA、eval 三个 meta 都是本脚本。
- 缺口（P3）：脚本不比较 r2.9 .ok 和本次 .ok 的数据 pin。本次我手工核过全部相同。下一轮建议加一条代码检查。

## 3. 各项改动
- (a) eval 按 universe 拆进程，加 merge：链条 eval_HILIQ ← fund+build×2，eval_FULLA ← 同上 + eval_HILIQ，merge ← 两个 eval。正确。
- (b) 只减列，没有改 dtype：PX 去掉 logmv 和 <col>（eval 和 pool_benchmarks 都不读这两列，已核）；叶20 α 只读首个 W20 日期之后（左表是 W20，早于它的行本来就匹配不到）；pick_book 只喂调仓日的 A/G（byd 只在 d∈rd 时用，选股逐行相同）。
- (c) pool_benchmarks 逐年 del：pre 提到 del pr 之前取，pr 在两处之间没被改；A/B/sus 删除后不再使用（pyflakes 0 条）；cat 逐键 pop。不改数值。
- trim()（范围外）：gc + pyarrow 池 release_unused + glibc malloc_trim(0)。只把空闲内存还给系统，不碰任何对象，没有数值副作用。libc 加载失败时跳过。
- 收益缓存保留（范围外）：
  - 键都是 (2024, 2025, 2026)，eval 开头加载一次。
  - book_ret 只做 reindex / .loc 取副本，不原地改 rr/on；bal 那处也是取副本再 astype。原来每本书后清掉再读，读的是同一份钉住的面板，数据相同。所以保留缓存不改数值。
  - 缓存内存约 2×13 MB（float32），AI 的估算里算了（"FE.rets 预载约 760"那一段）。
- (d) 看门狗：从 /proc/self/status 读 VmRSS 和 VmHWM（kB），任一超过 1536000 就打印 RSS_GUARD_KILL 并 os._exit(137)。peak_check 在每年末、每个 universe 末、merge 末再看 VmHWM 和 ru_maxrss（Linux 下单位 kB），同样退出 137。读法和标记都对。
  - P3：看门狗循环里 except Exception: pass，读 /proc 失败会悄悄失效。建议失败也退出。

## 4. 内存
- AI 方法：用自写脚本在真实文件上复现 eval 的内存大头。注意：这一步读了真实数据，虽然没有 import 项目代码，是否需要 .ok 交主 Agent 定。
- 余量 122 MB 的算法单位混了：复现脚本被杀时 VmHWM 1473688 kB = 1439 MiB，不是 1474；实跑 HILIQ 段 ru_maxrss 1596 MiB。而且复现脚本是被 1.45GB 线中途杀掉的，它的真实峰值只知道 ≥1439。所以"实跑比复现高多少"的上界是 1596 − 1439 ≈ **157 MiB**，不是 122。
- 我的粗略上界（按 AI 的 v4 读数加 157 MiB）：HILIQ ≈ 1220 MiB，FULLA ≈ 1320 MiB。限值 1536000 kB = 1500 MiB。FULLA 余量约 180 MiB，可以接受。
- 真实规模核对：A/G 行数 HILIQ 1,618,456 / 1,628,867，FULLA 2,698,355 / 2,719,070；面板 2024–2026 共 3,327,827 行（PX 截到 2024-05-20 后约 2.88M）；ret/close 存盘就是 float32。与 AI 表格一致。
- merge 只读两个 json，内存很小。
- 评级 P2（文档口径问题，不阻塞）：以后估算统一用 kB 或 MiB，并写明复现脚本是否被截断。

## 5. merge
- 只读 eval_HILIQ_meta、eval_FULLA_meta 和它们列出的 summary_<uni>_<stamp>.json；先核 sha，再核每份只含自己那个 universe。
- 输出 summary_<stamp>.json：结构与旧单进程 summary 相同（res 含 HILIQ、FULLA 两项）；新增 auth_by_uni、stamps_by_uni；peak_rss_mb_eval 从数字改成按 universe 的字典。CMC、selfcheck、decay 工具都不读 summary 或 eval_meta（已 grep），不受影响。
- eval_meta 的 outputs 只列 merge 的 summary；eval_weights 列在 eval_<uni>_meta 里，经 upstream 链覆盖（P3：说明一下即可）。外部输出从两份 eval meta 合并。

## 6. .ok 解析
- 白名单 = OK_FIXED 19 + OK_REQUIRED 9 + OK_RESUME 5 + TOOLS 22 + TOOL_CLOSURE 4 = 59，互不重叠。多一个或少一个键都会拒。
- resume 五键全 none 或全 hex，否则拒。
- serial_order 在 OK_FIXED 里，必须存在且等于新值。
- 解析器仍是严格的 ^[a-z0-9_]+=\S+$，拒 BOM、空值、重复键。

## 7. .cmd 和步骤表
- TOOL_CMDS 路径和 cmc_cmd_ok 规则都没改。正式 .cmd 仍放在 output/ai_factory/ARCH_TOOL_CMDS_LEAF23_X2.cmd，内容只有 CMC 一行（不变）加注释。
- 步骤表（AI_LEAF23_R2_10_PROPOSED_CMD.txt，不被脚本钉住）：每行 env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python，顺序 A01 eval HILIQ → A02 eval FULLA → A03 merge → 4 个敏感性各 6 步（fund、build×2、eval×2、merge），--uni 用法和脚本一致。正确。
- P3：步骤表只按退出码判断成败。建议每步后再核：对应 meta 文件生成、stdout 有 peak_check 和 STAMP 行、没有 RSS_GUARD_KILL。

## 8. 模式类检查
- 带过滤读取：新增的叶20 α filters date ≥ datetime，列是 timestamp[us]，对；read_panel 求 pdt 对；其余不变。
- 日期 merge：ev/evo 转成 pdt，与 P.date 同为 [us]，有 STOP 守卫；IXr reindex 对。
- 漏写 f 前缀：AST 扫描所有字符串常量，没有发现带 {变量} 但没写 f 的情况。
- 只看退出码：脚本里所有拒绝都是 SystemExit（非 0）或 os._exit(137)；见第 7 节建议。

## 9. 草稿（未安装）
- _review/leaf23_r2_10_ok_draft/ARCH_RUN_AUTH_LEAF23_R2_10_X2.ok.draft：59 个键，LF，live=false，promotion=false，方案 A（resume 钉 r2.9 值）。
- _review/leaf23_r2_10_ok_draft/ARCH_TOOL_CMDS_LEAF23_X2.cmd：只改首行注释（written_at、script_sha256=f1344324…），其余与当前 493cc03c 逐字相同。
- 相对 b21e9952 的变化：script_sha256、tool_cmds_sha256（新 .cmd 的 sha）、serial_order、issued_at；新增 5 个 resume 键。其余全部重测不变。
- 安装：先把现行 .cmd（493cc03c）归档，再把新 .cmd 放到固定路径；issued_at 改成实际签发时间；签前重测 forecast 和 manifest。
