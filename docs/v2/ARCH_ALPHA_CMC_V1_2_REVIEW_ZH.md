# Arch 审阅：Alpha CMC v1.2（内存重构）+ 内存测试封装（cmc_wrapper v3 / rss_wrap）

- 审阅人：QuantLab Arch；时间：2026-10-18T09:41:22-04:00；基线 HEAD 0ec38296adbfb1fe691694879c2c042f3b45422d
- 方式：只做静态审阅。在 /tmp/arch_cmc12_Gibf 下工作，脚本带 set -euo pipefail，cd 后核对过路径。没有 import 项目代码，没有读真实数据，没有在仓库里 git apply。
- **结论：PASS with conditions（有条件通过）**。selftest .ok 现在就可以签。memtest .ok 必须满足第 5 节的条件后才能签。
- live=false；promotion=false

## 1. sha 核对（全部一致）

| 文件 | sha256 | 结果 |
|---|---|---|
| research/alpha_combo_marginal_v1_2.py | bba212afadefce68dcd1bf76919f91de39402658e4398e925e3d80c6f01592c4 | 一致 |
| docs/v2/ALPHA_V1_2_IMPORT_CLOSURE.manifest | 440ea3eab2b53e4791d8637b92191c23c9499c6616a6cfd6ef20592d395310b1 | 一致：84 行，等于 v1_1 清单 ab91f3e0 加上 v1_2 一行（排序后 diff 只多这一行）；sha256sum -c 全部 OK |
| tests/test_alpha_v1_2_equiv_selftest.py | 6f6895b3e1a90b0d51daca2bd30b5dd1ff0838dc30c48ec5ccd0eba9fae78dd1 | 一致 |
| docs/v2/ALPHA_CMC_V1_2.patch | 4aab116885a39d6a08979a1ccb04792dacc6a09cacea284ee589c592249ee273 | 一致；/tmp 重放可逐字节复现 3 个文件（见 P3-1） |
| docs/v2/ALPHA_CMC_V1_2_HANDOFF_ZH.md | af92d2e3ca31dac2e2a9c2a03e096319887da8970378a25c9c427b38c4ed7391 | 一致 |
| v1_1 / v1_1 清单 / v1_1 selftest / runguard / ok_runner_pin | 5658f612 / ab91f3e0 / 6966a5d9 / 35991407 / c7805d9a | 都没动 |
| adg / selfcheck_v3 / selfcheck_common | a877cec5 / ecaa30d8 / 218b61cf | 与清单一致 |

pyflakes 4.0.3 装在 /tmp 的一次性 venv 里，在 /tmp 副本上跑（不 import 代码）。v1_2、equiv selftest 和 v1_1 三个文件都是 0 条告警。

## 2. 规格逐项核对

1. **M1：P 逐只构建（L268–283）**。代码在 L269 先分配 days×U 的 float64 矩阵，然后逐只调用 ADG._close。L188 断言索引唯一，L189 断言 dtype 为 float64，接着 reindex(days) 写进矩阵，L275 执行 ADG._cache.pop。AP._F 保留。F 在 R 之前算（L279–281），公式与 v1.1 相同。列顺序是 U，和 v1.1 dict 插入顺序一致；索引就是 days。**符合。**
2. **M2：sig() 读入时过滤零权重（L314–328）**。读入时 filters=[("target_weight","!=",0.0)]。-0.0 被滤掉；v1.1 里 groupby sum 从 +0.0 开始累加，结果仍是 +0.0，所以两边一致。NaN 行在 Arrow 中满足 != 0，被保留，与 v1.1 相同。全零时（L325）得到 0.0 网格，与 v1.1 一致。reindex(ev,U) 和 fillna(0.0) 都保留了。**符合。**
3. **M3：mem 改成 ev×U 布尔矩阵**。构建在 L258–267。v1.1 里 mem 有 4 处引用：pool_ew、ctx 覆盖率、resid_z、_CTX 存储。v1.2 分别改为 _pool（L166、L177、L335）、check_ind_coverage(mask)（L208、L305）和 _CTX.mem_mask，全部改到。rg 确认没有遗留的 c["mem"]。池子的顺序仍然是 U 的顺序。**符合。**
4. **M4：del 和 gc**。分布在 L266、L282、L288、L300、L306、L394。只保留 ev 窗口的切片，和 v1.1 的存储内容相同。**符合。**
5. **M5：STAGE 行**。_stage 在 L99，只写 stderr，并且 flush。打点位置：imports、mk/mem、_factors、P、beta、FMC、IND、每个 sig（带 rows_nonzero 和 dup_keys_nonzero，L327）、b0、tiers:*。**符合。**
6. **额外改动：legacy_column（L464）**。只多拒绝一种情况，即 tool_version 为 v1.1 的 JSON；数值路径没变。selftest L447 断言两版的 legacy 列逐字节相同。**不改数值。**
7. **runguard 和 .ok 键名**。runner 键是 runner_sha256_alpha_combo_marginal_v1_2（来自 stem）。closure_manifest 指向 v1_2 清单。gate_deps 共 21 个，键名与 v1.1 相同。runguard 35991407 原样复用：signed_et 必填；整行 # 注释允许；值里不能有空白或 #，也就是不能有行内注释；除 allow_<mode> 和 allow_real_data 以外，所有 allow_* 必须为 false。看门狗每 0.5 s 读一次 ru_maxrss，超过 1536000 就 exit 3（L186–198），**保留了**。注意 STOP 行打在 stdout，所以封装必须把 stdout 和 stderr 合并进日志。
8. **新增读写**。没有新的真实数据读取，只是加了过滤。写入仍然只有 --out（L499 以 "x" 方式创建）。已有的旁路：adj_price.build_cache 会在缓存缺失时写 data/v2/adj（v1.1 也一样）。缓存现在存在，sha 为 4642ca8e，已钉进 memtest 草案。

## 3. 等价性与 selftest

- selftest 在 L84–92 包装了 pd.read_parquet，凡是 mkdtemp 以外的路径一律拒绝。ADG.bench 和 ADG._close 被打桩（cache-through）；SW、panel_stitch、hiliq 用内存模块替代。**不读真实数据。**
- v1.1 和 v1.2 在同一份合成数据上跑 cmc()，比较方式如下：
  - 浮点用 struct '<d' 逐位比较；
  - ±0 单独列出；
  - 最后要求 json.dumps 逐字节相同；
  - 中间量 R、beta、MC、F、IND 和 sig 也逐格比较。
- 合成数据覆盖了：晚上市、NaN、缺行、非交易日的掩码行、0.0、-0.0 和 NaN 权重、(x,0.0) 与 (x,y) 两类重复键、三种日期编码，并且断言 v1.2 已经 pop cache。**能证明逐位等价。**
- **Alpha 提的风险成立**。pandas 的 groupby sum 用 Kahan 补偿求和。同一个 (date,code) 下有多条非零行，中间又夹着零行时，删掉零行会让补偿项提前或推后生效，最后一位可能不同。只有一条非零行时结果是精确的。selftest 没有构造「两条非零加一条零」的组合。**运行条件：每条 sig 都要 dup_keys_nonzero==0**，否则结果按等价性 VOID。
- truncation 检查提前（L280）只会改变报错的先后顺序，不影响跑成功时的数值。

## 4. 发现

- **P2-1（运行风险，不改数值）**：
  - 某只股票既没有 D0 面板也没有 asof 面板时，load_panel_features_x2 返回空 DataFrame（g1g5_x2_panel_stitch.py L99–101），adj_close 再得到 object dtype，v1.2 会在 L189 RuntimeError 中止；v1.1 则会留一列全 NaN。
  - 另外，如果某只股票不在复权因子表里、原始 close 又是 float32，也会在 L189 中止。
  - 两种情况都是 fail-closed，不会悄悄改数值，但可能让 memtest 白跑。合成 _close 测不到这条路径。
  - 处理：先不改。如果真的触发，Alpha 出补丁交审，建议只把 len(s)==0 当作全 NaN 列处理。
- **P2-2（运行条件）**：dup_keys_nonzero==0 必须写进 memtest 和 full .ok（已写入草案）。
- **P2-3（解释器）**：
  - Eng 兼容说明里的命令用的是裸 python3，即 /usr/bin/python3.13（3.13.5）。它的 pyarrow 26.0.0 装在 user-site，10-18 01:08 ET 安装；pandas 3.0.6，numpy 2.5.4。
  - qlvenv 是 3.12.14，pyarrow 25.0.1，pandas 3.0.6，numpy 2.5.3。
  - AI 说「裸 python3 没有 pyarrow」**不成立**（09:01 时已经装上）。但仍然必须用 /workspace/qlvenv/bin/python，理由是版本要和 selftest 一致，不是缺包。.ok 里写明 interpreter=/workspace/qlvenv/bin/python。
- **P3-1**：补丁写成 a/v1_1 到 b/v1_2，没有 rename 或 copy 头，在只有 v1_1 的树上直接 git apply 会报 No such file。需要先复制 v1_1 为 v1_2、v1_1 清单为 v1_2 清单，再 apply，之后 3 个 sha 才全部相同（/tmp 已验证）。建议在交接文档里写明。
- **P3-2**：legacy 列的 role 字串仍写着 "verdict uses v1.1"，键名也还是 v1_1，L459 已注明这是为了 schema 连续。只影响披露。
- **P3-3（内存估算合理性）**：
  - days 约 760，U 约 2000，所以 arr、R、beta、F 每个约 12 MB。v1.1 的大头是 ADG._cache、并集 DataFrame 和 sig 满格读入加 astype(str)。v1.2 把这几项都消掉了。870000–1258000 kB 的估计**数量级合理**。
  - 但 ru_maxrss 单调不降，约 9000 次 parquet 读取造成的碎片仍在，上界只比 1331200 低约 5%，必须实测。
  - 如果超线，可以考虑 MALLOC_ARENA_MAX=2，但这超出本规格，要另审。

## 5. memtest 封装审阅（cmc_wrapper v3 61676a3c；v2 dcfef770 已被取代）

v3 相对 v2 已经修正：
- 防护 pid 94322 默认开启，启动前和每次采样都检查，状态是 T 或已退出才算通过，否则 rc 89；
- --no-guard 需要 .ok 里有 allow_no_guard=true，否则 rc 90；
- --c5-ignore 在真跑时需要 allow_c5_ignore=true，否则 rc 91；
- 测试钩子不带 --selftest 时 rc 92；
- 启动前的 ps 快照带 sha；
- PGID 不一致时不再把 PGID 改绑到别的组（v2 可能误杀自己所在的组）。
- 再核对 7 条硬规则：cd 单独一句（L56）；只有 setsid "$@" 放后台，所以 $! 就是命令本身（L57）；PGID 不一致 rc 97；cmdline 断言失败 rc 98；采样间隔 0.2 s；统一停止流程是 TERM、等 5 s、KILL，再用 pgrep -g 核实（L40–42）；C5 rc 96。**都满足。**
- **全进程组取 VmHWM 最大值（L69–70）：接受**。取的是单个进程的 HWM 最大值，等价于「任一单进程超线」，口径偏保守；VmRSS 求和单独记录。
- allow_no_guard=true 和 allow_c5_ignore=true 都不可能出现在 runguard 校验的 .ok 里（runguard 要求其他 allow_* 一律为 false），等于双保险，和 09:28 裁定一致。草案里两者都显式写成 false。

问题：
- **P1-W1**：peak_kb 取了 meta 里 vm_peak_kb 的最大值（L86–88）。vm_peak_kb 是 VmPeak，即虚拟内存峰值（runguard L114–122），pyarrow 进程通常远大于 RSS。只要传了 --meta，C4 就形同虚设，基本会误报 FAIL。处理：本次**不传 --meta**，wrapper 的 C4 行不作判定依据，判定由 Arch 按 .ok 公式计算。之后 wrapper 应把 P6 从 max 里去掉。
- **P2-W2**：C4 用的是 HARDKB 1536000，不是通过线 1331200；也不解析 STAGE 行的 ru_maxrss。由 .ok 公式补上。
- **P2-W3**：C5 的命令模式漏掉了 scripts_eng/、python -c "import research.x"（b4_paper_extend.py L172 就这样调用）和 -m quantlab。maps 检查对 .py 无效。真正可靠的只有 fd 检查，而且只是抽样。另外 deploy_loop.sh 的 kline.py 运行时 cwd 在 quantlab-web，但会读 /workspace/QuantLab/data 下的 parquet，只能靠 fd 偶然抓到，结果是随机 rc 96。处理：memtest 期间暂停 deploy_loop（见第 6 节）；wrapper 以后补上这几种模式。
- **P2-W4**：**rss_wrap 不能和 wrapper 叠用。**
  - rss_wrap 放外层：它的 cmdline「python3 … research/alpha_combo…」会命中 C5，如果 --out-dir 在 output/ 下还会命中 fd，结果是 rc 96 自杀。
  - rss_wrap 放内层：wrapper 采样的是 rss_wrap 本身，cmdline 断言也会被 rss_wrap 的 argv 骗过。
  - 结论：只钉一个封装。
- **P3-W5**：PGID 不一致而 setsid 又确实 fork 了的情况下，kill -PID 打不到任何进程，fork 出来的子进程会脱离监控，同时日志误记 PGREP_G_EMPTY。非交互 bash 下基本不会发生；建议补 pgrep -P。
- **P3-W6**：默认 --assert alpha_combo 也能匹配 v1_1；.ok 固定为 research/alpha_combo_marginal_v1_2.py。
- **P3-W7**：带 .ok 的真跑如果加了 --selftest，会跳过 _void 处理和 cmdline 断言；.ok 命令里禁止 --selftest。
- **P3-W8**：_void 写死在 output/ai_factory/_void；find "$OD" -newer 会搬走 OD 里的所有新文件，所以 OD 必须是新建的专用目录。
- **P3-W9**：94322 退出后如果 PID 被复用，可能误报 rc 89（fail-safe）。

**rss_wrap 852bfd5f**（兼容说明 18386da1 已核对 sha）：
- Popen 不经 shell，env、nice、python 依次 exec，所以 p.pid 就是 python，**满足「$! 是 python」**。
- 采样间隔 0.1 s。rusage_children 能给出精确的最终峰值，这正好解决了「1 s 采样漏掉最后峰值」的教训。
- **不满足**以下规则：没有 setsid 和 PGID 校验，杀进程是遍历进程树直接 SIGKILL，没有 TERM 宽限，也没有 pgrep -g 核实；没有 cmdline 校验；没有 C5；没有防护 pid。
- 兼容说明说「--cap-mb 1536 时 runguard 一定先触发」，这不保证：
  - 1536 MiB 是 1572864 kB，按当前 RSS 判断，每 0.1 s 一次；
  - runguard 每 0.5 s 轮询一次；leaf24 那次 STOP 时已经到 ≥1630960，超出约 95 MB；
  - 所以快速冲高时 rss_wrap 可能先杀（exit 1）；
  - 而且两条线都在硬线 1536000 之上。
- 兼容说明 §6 的通过线 1484800 已被 1331200 取代；它的命令用的是裸 python3（见 P2-3）。

**推荐**：memtest **只钉 cmc_wrapper v3 61676a3c**，满足 7 条硬规则，STOPKB 1484800；不叠用 rss_wrap。如果主 Agent 坚持用 Eng 方案，rss_wrap 必须单独使用，并满足：
- --cap-mb 1450（正好等于 1484800 kB）、--interval 0.1；
- 用 qlvenv 解释器；
- 启动前人工检查防护 pid 和 C5 情况，并留证；
- 回执里 distinct_pids_seen==1；
- 判定指标再加上 rusage_children_maxrss_mb×1024。

**判定公式（写进 .ok）**：
- M = max(所有 STAGE 行的 ru_maxrss, 采样器 VmHWM 最大值, runguard STOP 值, 输出 JSON 的 peak_rss_kb)；
- PASS 的条件：M ≤ 1331200，exit 0，没有 STOP、STOPLINE、C5、PGID、CMDLINE、GUARD 事件，每条 sig 的 dup_keys_nonzero 都为 0，并且最后 PGREP_G_EMPTY；
- 1484800 和 1536000 作为参考列；vm_peak_kb 只记录，不参与判定。

## 6. 运行环境（只读 ps 和 /proc 核对）

- 94322 是 python3 scripts/acquire/remaining_after_stk_surv.py。09:32 时状态为 Ssl（在跑），09:39 复核为 Tsl（Data 在 09:36:37 STOP）。
- 已有进程 /bin/bash ./deploy_loop.sh：
  - pid 2859825，父进程 deploy_supervise.sh pid 2859819，pgid 2859819，09:27:23 ET 启动，用户 box；
  - cwd 是 /workspace/quantlab-web，持有 /tmp/ql_start_all.lock，环境变量显示由一个子 agent 会话启动，是 Web 看板的部署循环；
  - 每 5 分钟运行一次 python3 export_static.py，它会逐个持仓起 kline.py 读 /workspace/QuantLab/data 下的面板和 etf_daily_adj（**读真实行情**），并用 freshness.py 读 output/ 和 data/v2，然后部署到 Vercel；
  - 它遵守 RESEARCH_QUIET.lock 和 quiet_windows.json（ql_quiet.sh）。
- 它自己的 cwd、fd 和 cmdline 都不会触发 C5，但 kline.py 打开 parquet 的那一刻会被 fd 检查命中（随机 rc 96），也违反「同时只跑一个真实数据进程」。现在 RESEARCH_QUIET.lock 已经存在，它会跳过导出；memtest 期间锁必须保持。

## 7. 草案（/tmp，未安装）

- selftest：/tmp/arch_cmc12_Gibf/ARCH_RUN_AUTH_SELFTEST_CMC_V1_2.ok.draft，安装路径 output/alpha/ARCH_RUN_AUTH_SELFTEST_CMC_V1_2.ok。9 个依赖按 test 文件里的 TEST_DEPS 键名钉定，scope=selftest，只有 allow_selftest=true，out_dir=mkdtemp，head_base=0ec38296。
- memtest：/tmp/arch_cmc12_Gibf/ARCH_RUN_AUTH_MEMTEST_CMC_V1_2_LEAF24.ok.draft，scope=full，21 个 gate 依赖都已重新计算 sha（与 leaf24 v1.1 .ok 相同，只有 closure_manifest 换成 440ea3ea），钉 wrapper 61676a3c。
- 两份都把 signed_et、issued_at、expires_et 留作占位，等 Arch 用 date 填写；expires_et 必须早于 2026-10-19T16:40:00-04:00。
