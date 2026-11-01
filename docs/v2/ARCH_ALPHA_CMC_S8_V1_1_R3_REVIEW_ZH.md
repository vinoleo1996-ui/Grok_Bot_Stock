# Arch 审查：Alpha CMC / s8 v1.1 r3（2026-10-18 ET）

- 审查人：QuantLab Arch；审查时间：2026-10-18 03:15–03:25 ET；上一轮：`docs/v2/ARCH_ALPHA_CMC_S8_V1_1_R2_REVIEW_ZH.md`（6ab489c8）
- 依据：主 Agent 02:44（风格项一律 t−1）、02:59（P2-3：只读 2024-05-31 一张申万一级快照；除继承回看外不读 2024-06 前行情）、03:10 补充（β120/动量价格回看继承）、**03:22 确认（P2-1：t−1 平移后最早触及 d−121 仍在旧读取范围内，属 03:10 补充覆盖，前提是文档明确写出；修法 (b) 为正式裁定）**；规范 1aa43bdd；ok_runner_pin c7805d9a。
- 审查方式：只读。sha256sum、patch 回放（在 /tmp 对 FROZEN 原件回放）、AST 闭包扫描与 f 前缀扫描（只 ast.parse，不 import、不编译进仓库），临时目录 /tmp/arch_r3v11.* 用后删除。**没有运行任何项目代码，没有读取任何真实数据。** research/__pycache__ 仍为 22 个文件。
- live=false，promotion=false

## 0. 结论
- **结论：通过（无 P1 / P2）。selftest .ok 已于本轮签发。**
- P1-1（窗前流通市值）已按修法 (b) 完整修复，两个脚本一致；断言真实、位置正确；测试能抓住回退。
- P2-1 **关闭**（主 Agent 03:22 确认；交接 L64–66、L211 与两个 docstring 已明确写出 d−121）。
- 可选 P3-1/2/3 全部落实。新增 4 条 P3（§6），均不阻断。
- 叶 23/24 全量 .ok 钉 `dep_combo_sha256=5658f612fef313fc5b818fc4cb9d594d757377e0dbf7c7dc86a6e31788b88911`（不再是 0dbd91ed）。

## 1. sha 核验（03:16 ET 实算，全部与交审一致）
| 文件 | sha256 |
|---|---|
| research/alpha_combo_marginal_v1_1.py | 5658f612fef313fc5b818fc4cb9d594d757377e0dbf7c7dc86a6e31788b88911 |
| research/alpha_hiliq_s8_paradigm_v1_1.py | 455fdf826ef1aa95b3c4084d5222c0f83f40163526869c419994dfb8df82458a |
| research/alpha_v1_1_runguard.py | 35991407875094fd9a456b69fda2b48a059f6a140ed48c6f84a9fc2cda8267b6 |
| tests/test_alpha_v1_1_selftest.py | 6966a5d99ad3fa6e66078fea248a1cac539ceb18d122a845697f2f07bc2e2a41 |
| docs/v2/ALPHA_V1_1_IMPORT_CLOSURE.manifest | ab91f3e0cc3c81013a46da3fee2432f61fe717e3c8c3b16a8ea930b29dbc538c |
| docs/v2/ALPHA_S8_CMC_V1_1.patch | 9d608f255652aa3a016cf5e38ef9d17542f4ad1432b52ad90f38ea5e0d6a9438 |
| docs/v2/ALPHA_S8_CMC_V1_1_HANDOFF_ZH.md | ab6d1e82e319326ad93271e92f749d0334dd926c48604e8c07c467c1bf6d77cc |
| 不变：bee23019 / af48bc05、ok_runner_pin c7805d9a、ADG a877cec5、v3 ecaa30d8、common 218b61cf、规则文档 13e13c4b | 实算均一致 |

- **patch 回放：** 在 /tmp 拷贝 FROZEN 的 bee23019、af48bc05 后 `patch -p1`，得到的 combo、s8、runguard 三个文件 sha 与上表逐字节一致。
- **闭包清单：** 82 条，`sha256sum -c` 全部 OK。Arch 独立做 AST 闭包扫描（起点 combo、s8、runguard，包含函数内 import 与相对 import），结果 82 个文件，与清单**集合完全相同**。动态 `__import__` 仍只有 3 处，都是标准库（os、json、pathlib）。
- **r2 副本：** r2 文件没有归档，所以 r2→r3 的对比依据是 r2 审查记录 6ab489c8 中的行号与描述，加上对 FROZEN 原件的 patch 回放（见 P3-D）。

## 2. P1-1 修复核实（修法 b）
| 项 | bee23019 / af48bc05 | v1.1 r3 | 结论 |
|---|---|---|---|
| FMC 读取下界 | CMC L95、s8 L61：`trade_date >= START` | CMC L220–221、s8 L161–162：`trade_date >= START`，逐字同口径 | ✔ |
| 实际读到的行 | — | `check_fmc_lower_bound(fm["trade_date"])`：在 pivot 之前对实际读到的行断言 min ≥ START，否则 RuntimeError（CMC L222、s8 L163） | ✔ |
| mc 日历 | ev | CMC L225 `cal = days[days >= START]`；s8 L167 `cal` 取 [START, END] | ✔ |
| START 日 mc_{t−1} | — | `.shift(1)` 后 START 行全 NaN，并断言 `notna().any()` 为假（CMC L227、s8 L169） | ✔ |
| START 日处理 | — | CMC resid_z：行不完整，ok.sum()<30 → 跳过；s8 xmat(X_sig)：pool 为空，<50 → 跳过。B 集合 X（close d，r−1 锚定）不受影响 | ✔ |
| 价格起点常量 | CMC "2023-09-01"（L82）；s8 "2023-06-01".."2026-11-30"（L36） | CMC L207 在 `ADG.bench()` 之前断言；s8 L133 在 `ADG.bench()` 之前断言 | ✔（性质见 P3-C；s8 位置见 P3-B） |
| 披露 | — | 输出 `reads`（price_start、fmc_earliest_trade_date、start_day_skipped）和 `diff_vs_*`；交接 L64–67、L212 已改为如实表述 | ✔ |

- **没有新增的 2024-06 前读取。** 逐个检查两个脚本的所有 read_parquet、ADG.bench/_close、_load_sw_members 和 open 调用：
  - mask 读取限定在 [START, END]；
  - 价格读取范围与旧工具逐字相同；
  - 申万表只取 2024-05-31 一张快照，`sw_snapshot_dates` 有断言；
  - FMC 从 START 起读；
  - 叶子和腿的权重文件不是行情数据，`reindex(ev)` 截到窗内。
- **以前的修复没有回退：** `sw_snapshot_dates`、`check_ind_coverage`、`check_f_truncated`、`legacy_column`（5 类拒绝）、门禁顺序、`--out` 与 out_dir 的预检和独占写入、看门狗参数、写前复查 .ok，都保持 r2 状态。
  - CMC 的门禁顺序：enforce → runguard → out 预检 → ok_selfcheck → **启动时清单 sha 核对** → 看门狗 + RLIMIT → 重 import。s8 相同。

## 3. 测试（6966a5d9）
- 新用例 `test_fmc_read_from_start_only_and_start_day_skipped` 是真实有效的：
  - 合成 FMC 从 2023-06-01 开始造，并先断言确实存在窗前行，所以下界过滤真的被测到；
  - `READS` 记录每次 read_parquet 的 filters，并断言 FMC 读取的 trade_date 下界 ≥ START；没有下界也判失败；
  - 断言 `reads.fmc_earliest_trade_date == START`，以及 price_start 等于旧常量；
  - 断言 START 日 mc 全 NaN、resid_z 在 START 日全 NaN、次日有值；s8 断言 X_sig 在 START 日为 NaN，而 B 集合有值；
  - 把窗前 FMC 乘以 3，MC / X_sig / X 必须完全不变；
  - 直接喂入 2024-05-31 时，`check_fmc_lower_bound` 必须抛错。
- **回退检测：** 如果把下界改回 2024-04-01，至少 4 处会失败：check_fmc_lower_bound 抛错、下界断言、START NaN 断言、扰动不变性。即使代码断言被一起删掉，后 3 处仍然会失败。✔
- P3 用例：RLIMIT 环境变量的 0、−1、abc、等于 RSS 上限的值都被拒绝；合法值会记入 env_snapshot；vm_peak_kb 正常。✔
- 测试文件不硬钉 sha，sha 全部由 .ok 提供。TEST_DEPS 仍为 7 个，`test_only_pinned_project_modules_loaded` 不变。✔
- **f 前缀扫描（AST，4 个文件）：** 不带 f 前缀但含 `{…}` 的字符串共 10 处，全部是 `mc_{t−1}` / `beta_{t−1}` 这类字面数学记号或 docstring，不是漏写的 f。所有带变量的消息都已是 f-string。✔

## 4. P3 落实核实
- **P3-1 ✔：** `rlimit_as_kb()` 拒绝非整数、0、负数和 ≤ 1,536,000 KB 的值。`env_snapshot` 记录原始环境变量和实际生效值，看门狗回执记录 `rlimit_as_bytes`。看门狗的 RSS 上限不能用环境变量改写，所以 1.5GB 的 RSS 规则**没有新的绕过路径**。剩下的是上限过大的问题，见 P3-A。
- **P3-2 ✔：** `verify_manifest_shas(MANIFEST, "startup")` 在 ok_selfcheck 之后、重 import 之前执行，失败即拒跑。计算后的 `verify_closure` 仍然保留（核对 sha 和已加载的模块）。
- **P3-3 ✔：** `vm_peak_kb()` 读 /proc/self/status，CMC 写在输出顶层，s8 写在 `run_guard.before_write`。

## 5. P2-1：关闭
- 主 Agent 03:22 确认：t−1 平移后最早触及 d−121，仍在旧读取范围内，属 03:10 补充的覆盖范围，条件是文档明确写出。
- r3 已经写明：交接 L64–66（「最早触及的价格比旧版早 1 个交易日（d−121，旧版为 d−120），仍在相同的已读范围内」）、L106、L211；CMC docstring L19–22；s8 docstring L13、L26–29。**P2-1 关闭。**
- 交接 L66 括号里「Arch 将请主 Agent 确认」已过时，下一版顺手改成「主 Agent 03:22 已确认」即可（P3-E），不影响签发。

## 6. 新 P3（不阻断）
- **P3-A｜RLIMIT 环境变量没有上限。** 设一个很大的合法值（例如 10^12 KB），RLIMIT_AS 兜底实际上就失效了。这不绕过 RSS 规则（看门狗才是主控，而且不可改写），实际值也会记入回执。建议下一版加上限（例如 ≤ 16 GiB），或直接去掉这个环境变量。全量运行时，Arch 的 .cmd 不设这个变量，回执中它必须为 null。
- **P3-B｜s8 价格范围断言只在没有缓存的分支里。** L133 在 `if cp.exists()` 的 else 分支里。但 `__main__` 要求 out_dir 为空（L104、L352），测试也每次新建目录，所以缓存命中的分支实际上走不到。建议把断言挪到 `if` 之前。
- **P3-C｜常量断言的性质。** PRICE_START 断言检查的是同一个文件里定义的常量，作用是防止有人改了常量却没改断言，不检查数据本身。真正约束窗前读取的，是 FMC 的 filter、对实际读到的行做的 `check_fmc_lower_bound`、START NaN 断言，以及测试中的扰动不变性。这样的组合足够，接受。
- **P3-D｜被替换的 rN 版本没有归档。** 本轮 r2→r3 只能对照审查记录推断。建议以后把被替换的版本放到 `research/_superseded/<file>.r2_<sha8>.py` 这类位置（不进 import 路径，也不进清单），方便逐字节对比。
- **P3-E：** 交接 L66 改为「主 Agent 03:22 已确认」，见 §5。

## 7. 签发（selftest，单次）
- 路径：`output/alpha/ARCH_RUN_AUTH_SELFTEST_CMC_S8_V1_1.ok`（此前不存在，无需归档）。
- sha256：`fa45bf7f39dc40c06d9c45a19df74a6a4aa9499d5e37cfbfc212a1d50b0b1fe6`
- signed_et 2026-10-18T03:22:17-04:00；expires_et 2026-10-19T03:30:00-04:00；scope=selftest；只有 allow_selftest=true，其余 7 个 allow_* 都显式为 false；allow_real_data=false；out_dir=mkdtemp；live=false；promotion=false；single_use=true。
- 格式已自检：无 BOM、无 CR、LF 结尾；只有整行 `#` 注释，没有行内注释；键名都符合 runguard 的 KEY 规则，且不重复。
- 键名对照：
  - runner 键为 `runner_sha256_test_alpha_v1_1_selftest`，与 ok_runner_pin `_pins` 中的 script.stem 一致；
  - 7 个 dep 键与 TEST_DEPS 一一对应；
  - `dep_sha256_closure_manifest` 和 `gate_ok_runner_pin_sha256` 只是记录字段，两个解析器都忽略。
- 运行条件（写在 .ok 注释里）：
  - 串行，nice 10，RSS ≤ 1536MB；
  - 不得与 Eng SD0 parity 或任何 Data 重任务同时运行（nightly_update、relay_outage_backfill、sw_pit_refresh、v3 dry-run 等），开跑前 pgrep，结果写入回执；
  - 回执交 Arch，内容包括通过/失败数、告警（含 fork DeprecationWarning）、峰值 RSS、VmPeak、pgrep 输出，以及 research/__pycache__ 文件数 = 22；
  - 这份 .ok 不授权全量运行，也不授权读取真实数据。
