# Alpha CMC v1.2 交接（只改内存，数值不变）

- 日期：2026-10-18（ET）；作者：Alpha；依据：Arch→Alpha 10-18 v1.2 规格 + 主 Agent 追加要求（峰值目标 ≤1331200 kB）
- 状态：**已写好，未运行**。静默窗口内未起任何 python 进程（py_compile / pyflakes / pytest 都没跑），只做了人工阅读核对、`sha256sum -c`、`diff`、`patch --dry-run`。未 git commit（需 commit .ok）。research/__pycache__ 未动（22 个）。
- live=false；promotion=false。

## 文件

| 文件 | 说明 |
|---|---|
| research/alpha_combo_marginal_v1_2.py | 新脚本，TOOL_VERSION="v1.2" |
| docs/v2/ALPHA_V1_2_IMPORT_CLOSURE.manifest | = v1_1 清单原样 + 1 行（v1_2 本体），sha256sum 格式；`sha256sum -c` 84 行全部 OK |
| tests/test_alpha_v1_2_equiv_selftest.py | 新增的合成数据等价性 selftest（v1_1 的 selftest 文件 6966a5d9 不动） |
| docs/v2/ALPHA_CMC_V1_2.patch | 对 v1_1 脚本 / v1_1 清单的 diff，加上新测试文件（/dev/null → 新建） |

不动的文件：research/alpha_combo_marginal_v1_1.py（5658f612…）、docs/v2/ALPHA_V1_1_IMPORT_CLOSURE.manifest（ab91f3e0…）、runguard research/alpha_v1_1_runguard.py（35991407，原样复用）、叶24 脚本、.cmd 和已消费的 .ok。sha 见文末，交 Arch 时以 sha256sum 现算为准。

## 逐项改动（行号指 v1_2）

1. **P 改成逐只取（M1）**，L268–283。改为逐只 `ADG._close(i).reindex(days)` 写进 float64 矩阵，用完立刻 `ADG._cache.pop(i)`（L275）；AP._F 保留。每只都断言索引唯一（L272），并要求 dtype=float64（L273，这是等价前提，不满足就拒跑，不会悄悄出不同的数）。不再在约 3100 日的并集索引上对齐。
2. **sig() 读入时滤掉 0 权重（M2）**，L314–328。`filters=[("target_weight","!=",0.0)]`；pivot_table(sum)、`reindex(index=ev, columns=U)`、`fillna(0.0)` 都保留。不加 instrument∈U 过滤，`reindex(columns=U)` 已经做了这件事，这样也少一个 dtype 风险。STAGE 行附带 rows_nonzero 和 dup_keys_nonzero（非零行中重复的 (date, instrument) 数）。全为 0 的文件直接返回 0.0 网格（L325）。
3. **mem 改成 ev×U 布尔矩阵（M3）**，L254–267。ctx 里存 mem_mask、U_arr、ev_pos，不再存 570 个 str 集合。`_pool()`（L166）返回 `U_arr[mem_mask[k]].tolist()`。4 处调用都已改：ctx 覆盖率 L305 → check_ind_coverage(IND, mem_mask, U_arr, ev)（L208）、resid_z L335、pool_ew L177。
4. **阶段间加 del + gc.collect()（M4）**。mk 在 L266 删除；全日期的 F 在 L281、P 在 L282、beta 在 L287、R/rb 在 L288 删除，只保留 ev 窗口切片（v1.1 存的也只是切片）。b0 的 Z 在 L394 删除。ctx 内部顺序有调整：F 和 check_f_truncated 挪到 P 之后、R 之前，好让 P 早点释放。公式和输入都没变。
5. **STAGE 行（M5）**。`_stage()` 在 L99，往 stderr 写 `STAGE <name> ru_maxrss=<kB>`，后面可以跟 k=v 诊断，stdout 仍只输出 JSON。打点位置：imports L151、mk/mem L267、_factors L276（第一只 _close 之后，即复权因子加载完）、P L283、beta L289、FMC L301、IND L307、每个 sig L327（sig:capacity_adv / earnings_event / insider_increase / leaf / leaf_style）、b0 L396、每个资金档一次 tiers:<tier>（L451）。
6. **门禁和清单**。MANIFEST 指向 v1_2 清单（L87），启动校验和计算后的 closure 校验都用它，CODE_DEPS["closure_manifest"] 随之改变。runner key 由文件名自动得出：`runner_sha256_alpha_combo_marginal_v1_2`。runguard 仍是 research/alpha_v1_1_runguard.py。__main__ 回执新增 memory_refactor_of 字段（L493），里面写明 v1_2≠5658f612。
7. **legacy_column 小改（只是守卫，不涉及数值）**，L464。除了 v1.2 的输出，也拒收 v1.1 的输出作为 legacy JSON。v1_1、diff_v1_1_minus_legacy 等字段名保留，保持 schema 连续。

明确没有做的：float32、按年分块、改 panel_stitch、按资金档分进程。

## 为什么数值不变

- **P**：v1.1 是 `DataFrame({i:s})` 先按并集对齐，再 `reindex(days)`，每格的值就是 s[d]（不存在就 NaN）。v1.2 直接 `s.reindex(days)`，逐格相同，没有任何算术。列顺序（U）、index（days）都一样。如果 s 有重复索引，v1.1 自己也对不齐，会报错；v1.2 提前拒跑。
- **sig**：0 行在 pivot sum 里贡献 0，被滤掉后对应格变成 NaN，再 fillna(0.0) → +0.0。整组都是 0 时，v1.1 的 groupby sum 从 +0.0 起加，结果也是 +0.0（含 -0.0 输入），两边一致。-0.0 != 0 在 IEEE 下为假，所以 -0.0 行同样被滤掉。日期解析：v1.1 能成功解析，说明全部行都符合从首行推断出的格式；子集的格式与之相同（YYYY-MM-DD / YYYYMMDD 都无歧义）。
- **pools**：ev_pos 由 ev 本身构造，对每个 d∈ev，`U_arr[row]` 与 v1.1 的 `[i for i in U if i in mem[d]]` 成员相同、顺序同为 U，`.tolist()` 返回的就是同一批 str 对象。mask 里不在 ev 上的日期（非交易日），v1.1 从来不会被查到，v1.2 直接丢弃。d∉ev 时两边都会在 `.loc[d]` 报 KeyError。
- **del / gc / 重排**：都是纯函数之间的顺序调整，输入和公式相同。
- **AP._F 不清**：清了会重读因子表。ADG._cache 被 pop 后，tiers 阶段 LC._px 会对账本里的股票重新调用 ADG._close。这是同一文件的确定性重读，值相同，只多一点 I/O。

## 数值等价风险（如实披露）

1. **Kahan 求和与 0 行**：pandas 的 group sum 用 Kahan 补偿。如果某个 (date, instrument) 同时有 ≥2 条非零行和 1 条 0 行，v1.1 里那条 0 行会把补偿项加回去，可能差最后 1 ulp。dup_keys_nonzero==0 时可以证明逐位相同：单个非零值无论配多少 0 行都是精确的。因此建议 Arch 在 memtest/全量 .ok 里写明：各 sig 行的 dup_keys_nonzero 必须为 0，否则披露。
2. **dtype**：close 必须是 float64，否则拒跑，见上。如果 target_weight 在文件里是 float32，v1.1 和 v1.2 的 pivot 都保留 float32，两边相同；只有全为 0 的文件，v1.2 返回的是 float64 的 0 网格，值相同。
3. **NaN 权重**：Arrow 中 NaN != 0 为真，会保留，pivot 求和时跳过；null 会被滤掉。两种情况结果都是 0.0。
4. **报错顺序**：check_f_truncated 提前了，数据异常时报的错可能和 v1.1 不同，成功路径不受影响。
5. **pandas 3.0.6 / numpy 2.5.3 / pyarrow 25.0.1** 的具体行为（filters 逐行过滤、`DataFrame(arr, copy=False)` 不拷贝、group sum 的初值）是按代码推断的，要靠 selftest 实测确认。

## 合成等价 selftest（tests/test_alpha_v1_2_equiv_selftest.py）

- 门禁在模块顶层：`enforce(__file__, [output/alpha/ARCH_RUN_AUTH_SELFTEST_CMC_V1_2.ok], modes=["selftest"], deps=TEST_DEPS)` 先于任何被测模块导入，之后是 `RG.ok_selfcheck(mode="selftest")`。.ok 需要钉 `runner_sha256_test_alpha_v1_2_equiv_selftest`，以及 combo_v1_1、combo_v1_2、ok_runner_pin、runguard、adg、selfcheck_v3、selfcheck_common、manifest_v1_1、manifest_v1_2 的 dep_sha256。
- 读 parquet 有守卫，只允许读 mkdtemp 下的合成文件。ADG.bench/_close 换成合成版（cache-through，和真实的一样会写 _cache）；LC._ret 换成合成净值，两边共用同一个。
- v1_1 和 v1_2 在同一份合成文件上跑完整个 cmc()。合成数据覆盖：晚上市、缺行、NaN 收盘，in_universe=False 行和周六 mask 行，成员逐日变化，未分类股票和一次申万改分类，满格腿（含 0.0、-0.0、NaN），稀疏腿（含显式 0 行），(x,0) 和 (x,y) 两种重复键，整天无行，三种日期编码。
- **判定规则**：去掉元数据（tool_version 单独断言为 "v1.1"/"v1.2"、definition_notes(=__doc__)、peak_rss_kb、vm_peak_kb、gate、ok_selfcheck、closure、watchdog、env、memory_refactor_of）后，浮点按 struct '<d' 逐位比较，NaN==NaN（JSON 不保留 payload），类型必须一致；最后要求 `json.dumps(…, ensure_ascii=False, indent=2, default=str)` 逐字节相同。
- **±0 单独处理**：数值差异和"只差零的符号"分两组收集。`test_output_json_values_equal` / `test_ctx_sig_values_equal` 只在真有数值差异时失败；`test_output_json_signed_zero_and_bytes` / `test_ctx_sig_signed_zero` 只在出现 ±0 差异时失败，并列出路径，交 Arch 裁定。两组都通过才算逐位相同。
- 其他测试：pools 逐日一致；v1_2 的 ADG._cache 已 pop、v1_1 未 pop；重复索引和非 float64 被拒（v1_1 遇重复索引也报错）；zero 过滤只出现在 v1_2 的腿读取中；STAGE 行齐全且顺序正确；legacy 列两边一致，且 v1_2 拒收 v1.x 输出；v1_2 清单 = v1_1 + 1 行，且 sha 全对；runner key；--arch-ok 必填；只加载钉住的模块。
- 运行（拿到 .ok 后单独一个进程跑，不要和 v1_1 selftest 同一次收集）：
  `cd /workspace/QuantLab && PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python -m pytest tests/test_alpha_v1_2_equiv_selftest.py -q -p no:cacheprovider`
- 静默窗口解除后，先在 /tmp 拷贝上跑 py_compile 和 pyflakes（不读真实数据）。

## 分阶段内存估算（**静态估算，未实测**；目标 ≤1331200 kB，硬线 1536000 kB）

假设：U≈2000（HI_LIQ 历史成员，未读真实数据核实），days≈760（2023-09-01..END），ev≈570，收盘全历史并集约 3100 日；import 底座约 300 MB（参照 v1.1 selftest 峰值约 0.27 GB）。各分项沿用 Arch 的估算。单位 MB，表中"峰值"指该阶段累计的 ru_maxrss。

| 阶段 | v1.1 常驻/瞬时 | v1.1 阶段峰值（估） | v1.2 常驻/瞬时 | v1.2 阶段峰值（估） |
|---|---|---|---|---|
| imports | 底座 250–350 | 250–350 | 同 | 250–350 |
| mk/mem | mk 长表瞬时 100–150；mem 集合常驻 150–250 | 450–700 | mk 瞬时 100–150 后删除；mem_mask ≈1 | 400–500 |
| _factors（AP._F 首次加载） | 长表到 pivot 瞬时 150–250；_F 常驻 30–60 | 600–900 | 同 | 450–650 |
| P | ADG._cache 常驻 150–230 并持续增长；并集 DataFrame 瞬时 200–350；约 9000 次 parquet 读取的碎片 200–400 | **1300–1650**（实测 ≥1630960 kB 时被 STOP） | cache 逐只 pop，≈0；arr ≈12；碎片仍有 200–400 | 650–950 |
| beta | rolling 瞬时 30–60（P/R/beta/F 全日期各约 12） | ≥ 上一行 | 用完即删 | 650–950 |
| FMC | 长表瞬时 50–100 | ≥ 上一行 | 同 | 650–950 |
| IND | IND object 约 10 | ≥ 上一行 | 同 | 650–950 |
| sig:capacity_adv | 360 万行满格读入 + astype(str) + pivot，瞬时 400–700 | 未跑到（估计 >1700） | Arrow 解码后过滤，瞬时 120–250 | 800–1150 |
| 其他 sig / b0 / resid_z | 每个 sig 结果约 9；Z 约 3×9 | — | Z 删除 | 800–1150 |
| tiers | LC._px 缓存，加上 ADG 重新缓存账本股票，20–40 | — | 同 | 820–1200 |
| **全程峰值** | | **≥1.63 GB（实测）** | | **约 0.85–1.2 GB ≈ 870000–1258000 kB** |

对照两条线：
- 估算上界约 1258000 kB，比 1331200 kB 低约 73000 kB（约 5%）；比 1536000 kB 低约 278000 kB。
- 中值约 1.0 GB，约 1024000 kB，余量约 300000 kB。
- 最大的不确定项是碎片（200–400 MB，v1.2 没有消除，parquet 读取次数不变）和真实的 U。如果 U 是 4000，arr/R/beta/MC/F/IND/S 每个都翻倍，但每个只有 10–20 MB 量级，主要风险仍在碎片和 sig 瞬时。
- **结论**：预计能达到 ≤1331200 kB，但上界余量很薄，必须由 memtest 实测证实。建议 memtest 的 .ok 判据用 VmHWM ≤1331200 kB（主 Agent 目标），而不是 1484800。如果实测超过 1331200 kB 但低于 1536000 kB，按 STAGE 行定位是碎片还是 sig 引起的，再请 Arch 决定是否追加措施（规格内不做 float32 和分块）。

## 叶24 CMC 回执必须披露

- 工具 sha：v1_2（bba212af…）**≠ 5658f612**（叶 23/24 .ok 里钉的 dep_combo_sha256）。v1.2 是只改内存的重构，阈值和定义不变，数值等价由合成 selftest 断言。叶24 的脚本、.cmd 和已消费的 .ok 都没有改。
- 10-18 09:04 的 v1.1 叶24 全量运行被 runguard rc=3 停下，峰值 ≥1630960 kB，没有产出。
- 披露里注明各 sig 的 dup_keys_nonzero（见风险 1）。

## 下一步

1. 静默窗口解除后，在 /tmp 跑 py_compile 和 pyflakes。
2. Arch 静态复审 docs/v2/ALPHA_CMC_V1_2.patch。
3. Arch 签 selftest .ok（output/alpha/ARCH_RUN_AUTH_SELFTEST_CMC_V1_2.ok），跑等价 selftest。
4. Arch 签真实数据 memtest .ok。
5. Arch 签全量 .ok（runner_sha256_alpha_combo_marginal_v1_2）。

提交需要 commit .ok；10-19 16:40–18:40 不跑也不提交。

## sha（写本文时）
```
bba212afadefce68dcd1bf76919f91de39402658e4398e925e3d80c6f01592c4  research/alpha_combo_marginal_v1_2.py
440ea3eab2b53e4791d8637b92191c23c9499c6616a6cfd6ef20592d395310b1  docs/v2/ALPHA_V1_2_IMPORT_CLOSURE.manifest
6f6895b3e1a90b0d51daca2bd30b5dd1ff0838dc30c48ec5ccd0eba9fae78dd1  tests/test_alpha_v1_2_equiv_selftest.py
4aab116885a39d6a08979a1ccb04792dacc6a09cacea284ee589c592249ee273  docs/v2/ALPHA_CMC_V1_2.patch
5658f612fef313fc5b818fc4cb9d594d757377e0dbf7c7dc86a6e31788b88911  research/alpha_combo_marginal_v1_1.py   (未改)
ab91f3e0cc3c81013a46da3fee2432f61fe717e3c8c3b16a8ea930b29dbc538c  docs/v2/ALPHA_V1_1_IMPORT_CLOSURE.manifest   (未改)
6966a5d99ad3fa6e66078fea248a1cac539ceb18d122a845697f2f07bc2e2a41  tests/test_alpha_v1_1_selftest.py   (未改)
35991407875094fd9a456b69fda2b48a059f6a140ed48c6f84a9fc2cda8267b6  research/alpha_v1_1_runguard.py   (未改，复用)
```
patch 回放已核实：对 v1_1 脚本、v1_1 清单和空文件打补丁后，sha 分别等于上面 v1_2 脚本、v1_2 清单和新测试文件的 sha。

## 补充（10-18 09:50 ET）：Arch P3 和测试修订 r2

**Arch P3：怎么回放 patch。** docs/v2/ALPHA_CMC_V1_2.patch 里 v1_2 脚本和 v1_2 清单的两段 hunk 都是"v1_1 → v1_2"的形式，不是"新建文件"。回放前要先复制：`cp research/alpha_combo_marginal_v1_1.py research/alpha_combo_marginal_v1_2.py`，`cp docs/v2/ALPHA_V1_1_IMPORT_CLOSURE.manifest docs/v2/ALPHA_V1_2_IMPORT_CLOSURE.manifest`，然后再对这两份副本打补丁。新测试文件那段是 /dev/null → 新建，需要先 `touch` 一个空文件再打补丁。我在 /tmp 照这个步骤回放过，得到的 sha 分别是 bba212af、440ea3ea、6f6895b3，与仓库里的文件一致。

**selftest r1 的结果。** tests/test_alpha_v1_2_equiv_selftest.py（6f6895b3，未改）在 10-18 09:44 跑了一次，Arch 的 .ok 已消费。日志 output/alpha/selftest_v1_2/run_20261018.log（4654d320）：rc=1，12 passed，2 failed（test_output_json_values_equal、test_output_json_signed_zero_and_bytes）。
- 日志里看得到的差异只有路径字段：$.leaf_file，以及一个 book_60w.parquet 路径（即 $.tiers.60w.base_track）。两边的不同之处只是 tmp 子目录 v1_1/ 和 v1_2/，这是测试给两个版本各写一份合成文件造成的，不是 v1.2 的数值问题。
- 但日志不能证明没有别的差异：diffs[:20] 的 repr 被 pytest 截断（显示为 "..."），字节比较的 diff 也写着"133 lines hidden"。**这 133 行不在日志里**，所以日志里看不到任何非路径字段的差异，也无法排除有。要靠 r2 的完整差异文件来定论。

**r2：tests/test_alpha_v1_2_equiv_selftest_r2.py（新文件，r1 不动）**
- 只改了输出 JSON 的比较方式，合成数据、其余 12 个测试、门禁顺序（enforce(modes=["selftest"]) 在任何被测模块导入之前）都和 r1 相同。
- 新门禁文件：output/alpha/ARCH_RUN_AUTH_SELFTEST_CMC_V1_2_R2.ok。需要钉 `runner_sha256_test_alpha_v1_2_equiv_selftest_r2`，以及和 r1 相同的 9 个 dep_sha256。
- 路径白名单用的是精确的 JSON 路径，按 cmc() 代码逐个列出（v1_1 L336–337、L361；v1_2 L423–424、L448）：
  - $.leaf_file：str(wf)
  - $.universe_mask：ctx()["mask"]，即 _rel(mask 路径)，在 ROOT 之外所以是 str(path)
  - $.b0_legs.capacity_adv、$.b0_legs.earnings_event、$.b0_legs.insider_increase：str(v)
  - $.tiers.60w.base_track、$.tiers.100w.base_track：str(trk)
- 白名单之外不做任何关键字、正则或通配剥离。替换前先断言 v1_1 的值恰好是 `<OUT_DIR>/v1_1/<tail>`，v1_2 的值恰好是 `<OUT_DIR>/v1_2/<tail>`，且 tail 相同；之后两边都换成 `<TMP>/<tail>`。替换后还断言 JSON 里不再出现 OUT_DIR。浮点逐位比较、±0 分开报告、字节比较都没变。
- 完整差异清单写进 <OUT_DIR>/equiv_diffs.json，内容包括：替换前的全部差异、替换后的全部差异、±0 清单，字节不一致时还有完整 unified diff。stdout 打印一行 `EQUIV_DIFFS raw=… after_placeholder=… … sha256=…`；失败时用 pytest.fail（pytrace=False）输出完整清单，不截断。
- 通过条件：替换前的差异路径只能落在白名单内；替换后差异必须恰好为 0，±0 差异为 0，序列化 JSON 逐字节相同。
- 运行：`cd /workspace/QuantLab && PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python -m pytest tests/test_alpha_v1_2_equiv_selftest_r2.py -q -p no:cacheprovider -rA`。加 -rA 是为了让通过时打印的 EQUIV_DIFFS 行也进回执。
- 目前只在 /tmp 拷贝上做过 ast.parse（PYTHONDONTWRITEBYTECODE=1，没有 import 任何项目代码）。没有运行，也没有跑 pyflakes（未安装）。
- diff：docs/v2/ALPHA_CMC_V1_2_TEST_FIX1.patch（r1 6f6895b3 → r2）。对 r1 副本打补丁可逐位复现 r2。

```
8136e25ee58fbeca44b8a818af4c48c6d54713d773060f7f9c6f1e923836f6f2  tests/test_alpha_v1_2_equiv_selftest_r2.py
5ae44f163b32d422c1d8313c1b29bf8ff73a49ab13eb77164d31a880baac8051  docs/v2/ALPHA_CMC_V1_2_TEST_FIX1.patch
6f6895b3e1a90b0d51daca2bd30b5dd1ff0838dc30c48ec5ccd0eba9fae78dd1  tests/test_alpha_v1_2_equiv_selftest.py   (r1，未改)
bba212afadefce68dcd1bf76919f91de39402658e4398e925e3d80c6f01592c4  research/alpha_combo_marginal_v1_2.py   (未改)
440ea3eab2b53e4791d8637b92191c23c9499c6616a6cfd6ef20592d395310b1  docs/v2/ALPHA_V1_2_IMPORT_CLOSURE.manifest   (未改)
```
