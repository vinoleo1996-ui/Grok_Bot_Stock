# Alpha §8 / CMC v1.1 交接（2026-10-18 ET，r3：对应 Arch 审查 31b4b8ba 和 r2 审查 6ab489c8）

- 依据：
  - 主 Agent 2026-10-18 02:44 ET 裁定（v1.1）；
  - 主 Agent 2026-10-18 裁定 P2-3 = **修**；
  - Arch 审查 `docs/v2/ARCH_ALPHA_CMC_S8_V1_1_REVIEW_ZH.md`（31b4b8ba：逻辑通过，无 P0/P1）；
  - 自测规范 `docs/v2/ARCH_RUN_AUTH_SELFTEST_SPEC_ZH.md`（1aa43bdd）。
- 运行状态：**只写了代码，没有运行任何东西**（没有 python 运行、py_compile 或测试）。静态检查只做了三项，都不 import、不运行项目代码：
  - `ast.parse` 语法解析；
  - pyflakes 静态检查，装在 /tmp，只解析源码；
  - 自写的 AST 闭包扫描。
  research/__pycache__ 仍是 22 个文件。
- 阈值不变。旧工具 af48bc05 / bee23019 冻结、未改、不被 import。

## 1. 文件集与 sha256（r3）
| 文件 | sha256 | 说明 |
|---|---|---|
| `research/alpha_combo_marginal_v1_1.py`（CMC v1.1） | `5658f612fef313fc5b818fc4cb9d594d757377e0dbf7c7dc86a6e31788b88911` | r1 为 f1abd3ed，r2 为 0dbd91ed |
| `research/alpha_hiliq_s8_paradigm_v1_1.py`（s8 v1.1） | `455fdf826ef1aa95b3c4084d5222c0f83f40163526869c419994dfb8df82458a` | r1 为 10b28463，r2 为 c1b50b93 |
| `research/alpha_v1_1_runguard.py`（新） | `35991407875094fd9a456b69fda2b48a059f6a140ed48c6f84a9fc2cda8267b6` | r2 为 5c4d0180。两个脚本共用。只用标准库，enforce 钉住后、重 import 之前导入 |
| `docs/v2/ALPHA_V1_1_IMPORT_CLOSURE.manifest`（新） | `ab91f3e0cc3c81013a46da3fee2432f61fe717e3c8c3b16a8ea930b29dbc538c` | r2 为 b128dae1。sha256sum 格式，82 个文件（文件集合与 r2 相同，只是 sha 更新），`#` 开头的为整行注释；`grep -v '^#' … \| sha256sum -c` 已通过 |
| `tests/test_alpha_v1_1_selftest.py`（新） | `6966a5d99ad3fa6e66078fea248a1cac539ceb18d122a845697f2f07bc2e2a41` | r2 为 d5fbdbfc。合成数据自测 |
| `docs/v2/ALPHA_S8_CMC_V1_1.patch` | `9d608f255652aa3a016cf5e38ef9d17542f4ad1432b52ad90f38ea5e0d6a9438` | s8 对 af48bc05、CMC 对 bee23019、runguard 对 /dev/null 的 diff；在 /tmp 回放后，三个文件与仓库字节一致 |
| `docs/v2/ALPHA_HILIQ_S8_PARADIGM_RULES_20261014_ZH.md` | `13e13c4b0cce836238d743b379fd66113b44c38816dfeb397aa3263daf6ccc8a` | r2、r3 均未改 |

- 未改动的文件核验：
  - af48bc05fbcf…966c / bee230199ac2…5c51c；
  - ok_runner_pin c7805d9a78e4…2485；
  - leaf_selfcheck_v3 ecaa30d8… / common 218b61cf…；
  - alpha_decay_gate a877cec5…。
- **`leaf_selfcheck_v3` / `common` 不需要 v1.1**（Arch §5 已核 ✔）。

## 2. r2 改动逐项（对应 Arch 31b4b8ba）
### P2-1 依赖闭包
- 两个脚本的 `CODE_DEPS` 新增以下 dep：
  - `ai_debate_memory_runner`（e1736d80…）、`g1g5_wiring`（ff510148…）、`g1g5_expand_g6`（b2d26c0d…）；
  - `ok_runner_pin`（c7805d9a…，门禁自身）、`runguard`；
  - `closure_manifest`（上表的 manifest）。
- quantlab/* 采用**闭包清单**方式：manifest 列出 82 个文件，含 quantlab/*、`quantlab/platform/execution.py` 373fed30 等，以及两个脚本自身。
- 运行时检查：`RG.verify_closure` 在计算之后（s8 在 build 之后）和写出之前各检查一次，要求：
  - (a) 清单内每个文件的 sha 都没变；
  - (b) 本进程 `sys.modules` 中凡是位于仓库内的 .py，都必须在清单里。
  任何一项不符就拒绝（fail closed）。
- 局限：如果运行时通过 importlib 动态加载了清单外的模块，会在算完之后被拒，白算一遍，但不会产出结果。

### P2-2 .ok 自查（enforce 之后、重 import 之前）
- 照搬叶23 `read_ok` 和 SD1 测试的 `_selftest_selfcheck` 做法，见 `RG.ok_selfcheck(mode="full")`：
  - 无 BOM，只用 LF；整行 `#` 注释可以有，行内注释不行；不得重复键或空值；
  - `format=quantlab_run_auth_v1`、`signed_by=arch`、`scope=full`；
  - `signed_et` 和 `expires_et` 都带时区；expires_et 未过期，且晚于 signed_et；
  - `allow_{selftest,real_data,dryrun,full,execute,smoke,diagnostic,disclosure_only}` 全部显式写为 true 或 false；只有 allow_full=true，allow_real_data 可以是任一值；
  - 若 .ok 写了 out_dir，必须等于实际输出位置（CMC 为 `--out` 的父目录，s8 为 `--out-dir`）。
- 写出前 `RG.recheck_expiry` 再查一次：.ok 字节未变，且仍未过期。

### P2-3 首月行业（主 Agent 裁定：修）
- **改动：** 两个脚本都新增**唯一一个**窗口前申万快照 `SW_PRE_SNAPSHOT=2024-05-31`。s8 的 X_sig 和 B 集合 X 共用同一个 IND。
- **断言：** `sw_snapshot_dates()` 检查三点：
  - 2024-05-31 是日历上 START 之前的最后一个交易日；
  - 它是**唯一**早于 START 的快照日；
  - 快照序列单调、不重复。
  该快照只查申万成员表，**不为它读取任何价格、收益或市值**。
- **覆盖检查：** `check_ind_coverage()` 发现窗口内任何一天池内全部没有行业（全 `_UNK`）就拒绝；输出中带 `ind_coverage` 和 `sw_snapshot_dates_head`。
- **与 bee23019 / af48bc05 的差异（披露）：** 旧版在 2024-06-03..06-27 共 18 个交易日 IND 全为 NaN，被 fillna 成同一个 `_UNK`，等于没做行业中性化。v1.1 这段改用 2024-05-31 的成员。受影响的是这 18 天的残差化：CMC 的 resid_z，s8 的 A/A′/C 和 B。这 18 天约占窗口的 3%，因此对 IC 和中性收益的影响应当很小，但不为零；以 legacy 对照列披露。
- **窗前行情读取（r3 更正；主 Agent 02:59 / 03:10，Arch 6ab489c8 P1-1）：** v1.1 唯一的窗前行情读取，是继承旧工具的 β120 和 mom **价格**回看：
  - 读取范围、窗口长度、数据源、公式都与旧工具相同。价格起点 CMC 为 `PRICE_START="2023-09-01"`（bee23019 L82），s8 为 `"2023-06-01".."2026-11-30"`（af48bc05 L36），代码断言这两个常量与旧工具逐字相同。β 窗口为 120（min 60），mom 跨度为 100，数据源都是 ADG.bench / ADG._close。
  - **按 02:44 平移到 t−1 后，最早触及的价格比旧版早 1 个交易日（d−121，旧版为 d−120），仍在相同的已读范围内。**（Arch r2 P2-1；Arch 将请主 Agent 确认这属于 03:10 补充的覆盖范围。）
  - r2 曾从 2024-04-01 起读流通市值，**这是错的，已撤回**。r3 的流通市值与旧工具一样从 START 读（CMC L95 / s8 L61 的口径），mc 的日历也从 START 起。`check_fmc_lower_bound` 断言实际读到的最早 trade_date ≥ START，并另外断言 START 当日的 mc_{t−1} 全为 NaN。
  - **START 当日被跳过（与旧工具的差异，披露）：** 2024-06-03 没有 d−1 的流通市值，所以 mc_{t−1} 为 NaN。CMC 的 resid_z 和 s8 的信号侧（A/A′/C）当天不做残差化，窗口少 1 天。s8 的 B（X 在 r−1）不受影响。输出的 `reads` 和 `diff_vs_*` 字段都记录了这一点。

### P3
| 项 | 处理 |
|---|---|
| P3-1 恒真断言 | 改为 `check_f_truncated()`：P 不超过 END，且 F 在窗口最后 H 行全为 NaN。s8 同样调用 |
| P3-2 --out 预检 | CMC 在 .ok 自查之后、计算之前调 `precheck_out_file`；s8 调 `precheck_out_dir`；写出仍用 "x" |
| P3-3 legacy | `legacy_column(path, new, pinned_sha256)`：读入的字节必须等于 `_GATE["deps"]["legacy_json"]`；v1.1 输出、universe 不一致、leaf 文件名不一致、任一档 base 缺失或不一致，**一律拒绝** |
| P3-4 看门狗 | 两个脚本都用 `RG.start_watchdog`：每 0.5 s 轮询一次峰值 RSS，上限 1,536,000 KB，超限 exit 3；另设 `RLIMIT_AS` 兜底，默认 6 GiB。环境变量 `ALPHA_V11_RLIMIT_AS_KB` 可以覆盖，但 r3 起必须是大于 RSS 上限的整数，0、负数、非整数都会被拒绝；该变量的值和实际生效值记入 env_snapshot。RLIMIT_AS 限的是虚拟内存而不是 RSS，pandas/pyarrow 会预留不实际使用的虚拟内存，所以取值远高于 RSS 上限；它只是硬兜底，RSS 轮询仍可能在 0.5 s 内超出 |
| P3-5 / P3-6 表述 | docstring 和 exposure_anchor 已改：月末当日用当日生效成员（in_date ≤ 快照日 < out_date）；池的 ADV 和前一根 bar 取 d 之前，ST 和停牌取 d 当日状态（盘前已知） |
| P3-7 | ok_runner_pin 已作为 dep 钉住。它自身的宽松处（CRLF、BOM、同值重复键）由 runguard 的严格解析补上 |
| P3-8 | §5 模板已去掉行内注释 |
| P3-9 | `QL_X2_EXTEND_END`：`research/g1g5_x2_panel_stitch.py` 允许用它改写 X2_END。v1.1 的 P 和 F 都截到 END，所以它不影响结果，但每次输出都会记录它的值（`env.QL_X2_EXTEND_END`）。建议运行时不设置 |
| P3-10（另立工单，只写文档） | `research/leaf_selfcheck_v3.py` L138 的 `F = P.shift(-h)/P-1` 有两个问题：没有截到 END；P 已 reindex 到叶日期，所以叶 parquet 缺日时，h 行不等于 h 个交易日。不属于 v1.1 范围，未改。建议 AI/Alpha 另出 v3 新版本，sha 另审 |

### r3（Arch 6ab489c8）
| 项 | 处理 |
|---|---|
| P1-1 窗前流通市值 | 选方案 (b)：流通市值和 mc 的日历都从 START 起；START 当日 mc_{t−1} 为 NaN，当天跳过。新增两项断言：价格起点常量与旧工具相同；流通市值最早读取日 ≥ START。文档已如实更正，见上文「窗前行情读取」和下面附录的更正 |
| P2-1 回看表述 | 已改为「读取范围、窗口长度、数据源相同，平移后最早触及点早 1 日」，由主 Agent 确认 |
| P3-1 RLIMIT 环境变量 | 拒绝 0、负数、非整数和不超过 RSS 上限的值；env_snapshot 记录 |
| P3-2 启动时核对清单 | 新增 `RG.verify_manifest_shas(MANIFEST, "startup")`，在 .ok 自查之后、重 import 之前执行；计算后和写出前的完整闭包检查保留 |
| P3-3 VmPeak | `RG.vm_peak_kb()` 写入输出（CMC 写在顶层 `vm_peak_kb`，s8 写在 `meta.run_guard.before_write.vm_peak_kb`），首次全量运行的回执请一并记录 |
| P3-4 s8 价格读到 2026-11-30 | 继承旧工具，不改。F 截到 END，暴露只用到 d−1 |
| P3-5 fork 告警 | Python 3.12 及以上，在多线程的 pytest 进程里 fork 会出 DeprecationWarning，请在回执里记录 |

## 3. CMC：每个暴露的信息日期（d = 信号日；IC 用收盘 d 到收盘 d+20）
| 暴露 | bee23019 | v1.1 r2 |
|---|---|---|
| β120 vs 510300 | 收益 d−119..d（含收盘 d）；价格从 2023-09-01 起 | 收益 d−120..d−1；价格读取范围相同，最早触及点早 1 日 |
| log 流通市值 | 收盘 d（从 START 起读） | 收盘 d−1（同样从 START 起读；START 当日为 NaN，当天跳过） |
| 申万一级 | 不晚于 d 的最近窗口内月末，当日生效成员；**6/03–6/27 无行业** | 同左；6/03–6/27 用 2024-05-31 快照 |
| 池 | mask `in_universe[d]` | 不变（ADV / 前一根 bar 取 d 之前；ST / 停牌取 d 当日，盘前已知） |
| 叶 / 腿信号、额外回归量 | d 当日权重 | 不变 |
| F | 截到 END（断言是恒真式） | 截到 END，并检查最后 H 行为 NaN |
| mom / liq / vol20 | 不用 | 不用 |

s8 v1.1：
- **信号侧**：mc 取收盘 d−1；β 取收益 d−120..d−1；mom 取 C(d−21)/C(d−121)−1；liq 取 mask adv20[d]，即成交额 d−20..d−1；申万同上表。
- **B**：用收益日的前一日 r−1 的原 X 集合（申万同样用了首月快照修复）。
- **F**：截到 END。

## 4. 自测文件（交 Arch 签 selftest .ok）
- 路径：`tests/test_alpha_v1_1_selftest.py`，sha `6966a5d99ad3fa6e66078fea248a1cac539ceb18d122a845697f2f07bc2e2a41`。
- **门禁顺序：**
  1. 检查 PYTHONDONTWRITEBYTECODE；
  2. `enforce(modes=["selftest"])`；
  3. `RG.ok_selfcheck(mode="selftest")`：scope=selftest，allow_real_data=false，out_dir 为 mkdtemp 或 /tmp/<tag>，其余同 §2 P2-2；
  4. 用 mkdtemp 建 out_dir，并确认不在仓库内；
  5. 以上都通过后，才 import numpy、pandas、pytest 和被测模块。
- **不读真实数据：**
  - `pd.read_parquet` 被包装，读 out_dir 以外的任何路径都会 AssertionError；
  - `ADG.bench` / `ADG._close` 被 monkeypatch；
  - `research.g1g5_nontextbook_weights` / `g1g5_x2_panel_stitch` / `hiliq_v1_universe` 用内存 stub 模块替代，真实模块不被 import；
  - mask 和 FMC 是 mkdtemp 里的合成 parquet。
- **覆盖：**
  - CMC 的 mc/β、s8 X_sig 的 mc/β/mom/liq：只改 d 当日数据，暴露不变；改 d−1（mom 改 d−21），暴露随之变化；
  - B 集合 X 的 mc 仍随 d 当日变化，证明测试本身是灵敏的；
  - F 最后 H 行为 NaN，倒数第 H+1 行有值；
  - 首月：唯一的窗口前快照是 2024-05-31；**窗口内没有任何一天全为 `_UNK`**，且 START 当日全部有行业；负例（成员 6/10 才生效）会被拒；日历缺 5/31 时也被拒；
  - `--out` 和 out_dir 拒绝覆盖，"x" 方式写入；
  - legacy：匹配时接受；v1.1 输出、universe 不一致、base 不一致、leaf 不一致、sha 与门禁钉的不符，都拒绝；
  - 看门狗在 fork 子进程里触发（exit 3）；RLIMIT_AS 在 fork 子进程里触发 MemoryError；
  - 缺 `--arch-ok` 时两个 `_cli()` 都拒绝；
  - full 模式 .ok 自查的 9 个负例：过期、无时区、scope 错、缺 allow、多余的 true、行内注释、BOM、CRLF、重复键；
  - r3 新增：
    - 包装后的 read_parquet 记录每次读取的 filters，测试断言流通市值读取的 trade_date 下界 ≥ START。合成流通市值从 2023-06-01 起造，所以这个过滤确实被检验到；
    - START 当日 mc_{t−1} 为 NaN，resid_z 跳过 START、次日正常残差化；s8 X_sig 的 mc 在 START 当日为 NaN，B 集合不受影响；
    - 只改窗前流通市值时，CMC 的 MC 和 s8 X_sig/X 的 mc 完全不变；
    - `check_fmc_lower_bound` 负例；
    - 价格起点：CMC 为 2023-09-01，s8 为 2023-06-01；
    - RLIMIT 环境变量的校验（0、-1、abc、等于 RSS 上限都拒绝），以及 vm_peak；
  - 最后检查本进程加载的项目模块不超出 TEST_DEPS。
- **脚本的 `__main__` 仍只接受 full**：测试 import 函数，不走 `__main__`，因此不需要 selftest 钩子。
- **测试 import 到的项目模块**（selftest .ok 需全部 pin）：

| key | 文件 | sha256 |
|---|---|---|
| runner（测试文件） | tests/test_alpha_v1_1_selftest.py | 6966a5d99ad3fa6e66078fea248a1cac539ceb18d122a845697f2f07bc2e2a41 |
| combo_v1_1 | research/alpha_combo_marginal_v1_1.py | 5658f612fef313fc5b818fc4cb9d594d757377e0dbf7c7dc86a6e31788b88911 |
| s8_v1_1 | research/alpha_hiliq_s8_paradigm_v1_1.py | 455fdf826ef1aa95b3c4084d5222c0f83f40163526869c419994dfb8df82458a |
| runguard | research/alpha_v1_1_runguard.py | 35991407875094fd9a456b69fda2b48a059f6a140ed48c6f84a9fc2cda8267b6 |
| ok_runner_pin | scripts_eng/ok_runner_pin.py | c7805d9a78e4f5478fa4c9e3becda48e76453ee0889b4f7027009a676c3e2485 |
| adg | research/alpha_decay_gate.py | a877cec51dbb96c75a6d071e222caf35f62fd14f101741a03be117e0e6076a97 |
| selfcheck_v3 | research/leaf_selfcheck_v3.py | ecaa30d8760f7ae5f53c330c128e6702476d01d8d69112b1dbf2fe769b7eaebe |
| selfcheck_common | research/leaf_selfcheck_common.py | 218b61cfbf2bf0b6bb133ef030aa2d7ff20b3eafda9724aa98c9f3b1fa5cb054 |

- **.ok 路径**：按 Arch 模板为 `output/alpha/ARCH_RUN_AUTH_SELFTEST_CMC_S8_V1_1.ok`（测试里写死）。模板中的键已全部被 runguard 认可。
- **运行命令**（规范 §5）：`PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python -m pytest tests/test_alpha_v1_1_selftest.py -q -p no:cacheprovider`。

## 5. 全量运行与叶23/24 重签 .ok 的键位建议（Arch 定稿；无行内注释）
CMC v1.1 全量运行 .ok：
```
format=quantlab_run_auth_v1
signed_by=arch
signed_et=<带时区>
scope=full
runner_sha256_alpha_combo_marginal_v1_1=5658f612fef313fc5b818fc4cb9d594d757377e0dbf7c7dc86a6e31788b88911
dep_sha256_runguard=35991407875094fd9a456b69fda2b48a059f6a140ed48c6f84a9fc2cda8267b6
dep_sha256_closure_manifest=ab91f3e0cc3c81013a46da3fee2432f61fe717e3c8c3b16a8ea930b29dbc538c
dep_sha256_ok_runner_pin=c7805d9a78e4f5478fa4c9e3becda48e76453ee0889b4f7027009a676c3e2485
dep_sha256_ai_debate_memory_runner=e1736d80c589ecd717731dc38ae99a52f3d448da9841b2c3794ee008f59613ea
dep_sha256_g1g5_wiring=ff510148a8d0c571680986c8345b5d83e70fd572eca80206b1383f3c35da8c54
dep_sha256_g1g5_expand_g6=b2d26c0d26933778df62af99828dc58e17d37f94432004ca2d2de94ed2ba1a16
dep_sha256_<adg|selfcheck_v3|selfcheck_common|nontextbook|panel_stitch|adj_price|metrics>=<64 hex>
dep_sha256_<mask|float_mktcap|leaf|leg_capacity_adv|leg_earnings_event|leg_insider_increase|base_60w|base_100w>=<64 hex>
dep_sha256_legacy_json=<64 hex>
allow_selftest=false
allow_real_data=true
allow_dryrun=false
allow_full=true
allow_execute=false
allow_smoke=false
allow_diagnostic=false
allow_disclosure_only=false
live=false
promotion=false
out_dir=<--out 的父目录>
expires_et=<带时区>
```
- `dep_sha256_legacy_json` 只在传 `--legacy-json` 时需要。
- s8 v1.1 全量 .ok 键位相同。差别是：runner 改为 `runner_sha256_alpha_hiliq_s8_paradigm_v1_1=455fdf826ef1aa95b3c4084d5222c0f83f40163526869c419994dfb8df82458a`；另加 `dep_sha256_combo_v1_1`、`dep_sha256_hiliq_universe`、`dep_sha256_capacity_adv_leg`；每个 `--leaf` 一项 `dep_sha256_leaf_<NAME>`；out_dir 填 `--out-dir`。

叶23/24 重签 .ok：
```
dep_combo_sha256=5658f612fef313fc5b818fc4cb9d594d757377e0dbf7c7dc86a6e31788b88911
dep_combo_legacy_sha256=bee230199ac27bf9730aa77c63b104a67bb104229622c57524867a9b54a5c51c
```
- `dep_combo_legacy_sha256` 只用于对照披露列。
- 叶子**不 import s8**，s8 的 sha 只放在 Alpha 自己的 §8 验收 .ok 里。
- **AI 仍需改动**（Arch §5 已确认）：
  - `research/g1g5_sue_desens_cs_alpha.py` L74 和 `research/g1g5_imax_intraday_alpha.py` L62 写死了旧 CMC 路径，要改为 `research/alpha_combo_marginal_v1_1.py`，并新增 legacy 键；
  - `ARCH_TOOL_CMDS_LEAF{23,24}_X2.cmd` 目前不存在，需要 Arch 写好：用 v1_1，加 `--arch-ok`（可选 `--legacy-json`）；
  - L580/L518 的 docstring 和 L713/L646 的披露文字，要改为引用 s8 v1.1。
- **注意：** CMC v1.1 的 sha 经过两次变化：f1abd3ed（r1）→ 0dbd91ed（r2）→ **5658f612（r3）**。叶子 .ok 一律以 r3 为准。

## 6. 验收备注
- 基准池退市截断按 **delist_date** 处理（与预注册一致，主 Agent 02:44 裁定）。
- 首月行业修复属于事后改动，只对叶23/24 及以后生效；v4/v4.1 的判定不变。legacy 对照列会如实显示这一差异。
- 已知局限：没有运行过，可能有运行期错误，需由 selftest 首次验证。闭包检查是在算完之后做的。RLIMIT_AS 只是虚拟内存兜底。

## 附：窗前回看口径（主 Agent 2026-10-18 03:10 ET 确认）
- P2-3「不读 2024-06 前任何价格/收益/因子值」只约束行业快照一步：只取 2024-05-31 那一张申万一级成员表标签。
- β120 与动量 t−120→t−20 的窗前回看**继承旧工具 bee23019 / af48bc05 口径**：读取范围（CMC 价格自 2023-09-01、s8 自 2023-06-01，常量逐字相同并有断言）、窗口长度、数据源、计算公式与旧工具一致；按 02:44 平移到 t−1 后，最早触及的价格比旧版早 1 个交易日（d−121），仍在相同已读范围内（Arch 6ab489c8 P2-1，待主 Agent 确认）。
- 【r3 更正】此前写的「v1.1 未新增任何 2024-06 前读取」对 r2 不成立：r2 曾从 2024-04-01 起读流通市值（Arch 6ab489c8 P1-1）。r3 已改为与旧工具一样从 START 读，并断言最早读取日 ≥ START；代价是 START 当日（2024-06-03）没有 mc_{t−1}，当天在信号侧残差化中跳过，属于与旧工具的差异，已披露。r3 中除继承的价格回看和唯一一张 2024-05-31 申万成员快照外，不读任何 2024-06 前的数据。
- 窗前价格只用于计算暴露，不进入任何收益、IC 或回测净值窗口（前瞻收益 F 起于 d+1、截至 END）。
