# D21：v1.3 按口径 C 重算（送审稿 r4，只 py_compile，未运行）

- r1 起草：QuantLab Strategy，2026-10-18 02:18 ET（git 提交 b975819e 时间）。r1 正文快照：docs/v2/audit/snapshots/STRATEGY_D21_V1_3_BASISC_RECALC_ZH.8b7a29f0775de8e325a3105001d309cf40624221eb60b576d409536e75382753.md。
- r3：2026-10-18 02:44 EDT（ce45f3da）。r3 正文快照：docs/v2/audit/snapshots/STRATEGY_D21_V1_3_BASISC_RECALC_ZH.043911da2bd2c564a879947f763e61a0068d226c5811b1d6e95b08387ea3fec5.md。
- **r4 修改：2026-10-18 02:56 EDT（`date` 实测）**。依据：Arch 对 r3 待裁定点的裁定（1）缺行原因、（4）手数一致优先用 v1.3 ckpt pkl；主 Agent 02:48 ET 改向（CLARIFY-2 已落盘）、02:49 ET 改向（ceil(0.8×n) 用整数 `(4*n+4)//5`）。live=false，promotion=false。
- **CLARIFY-2 已钉**：docs/v2/LOTFIX_V1_4_FREEZE_RECORD_APPENDIX_CLARIFY_2_ZH.md = **85e843cd6c68d7a0d8c0035ebeab7c34e00e4ea76a799c95de0655c20445651b**（sha256sum 实测）。D21 的 `PINNED_DOCS` 也直接钉它（D 53，取 R 的常量），并仍走 `R.check_clarify2`（D 173）。
- **只写了代码，没有执行。** 只跑过 `python -m py_compile`（.venv_opt、qlvenv 都通过，pyc 已删）。没有建 .ok，没有改 b6238254，没碰任何 v1.3 / v1.4 产物，没碰 research/ai_debate_memory_runner.py、research/g1g5_x2_panel_stitch.py。**没有反序列化过任何 pkl**（只用了 ls 和 sha256sum）。
- 文件：`research/optimizer_core_v1_3_basisC_recalc_d21.py` = **497f9a2b59fa314adc54341f5f942a924c12fce6616ecf11694eb65d94e9fc6f**（下文 D@497f9a2b；r3 = 86c6f7bb，快照在 research/_runner_archive/）。
- combined_sha256（D21 + R + V + C，公式同前）= **ffa812fd05f8526345b3613227aec97038ab00a56a4338449a328a8db431a416**（R = c844dbb4…；R 再改，此值随之变）。

## 1. 做什么（D@497f9a2b 行号）
1. **主结果 = §8 基线（CLARIFY-2 §2.1）**：`replay(decide="A")`（217–276）按 b6238254 第 312–366 行重放 v1.3 决策：prepare_day → v1.3 ① 一手成本剔除 → `V.solve_v11`（POOL_STD=IND_POOL=True）→ 每袖 `V.lot_round_greedy` → v1.3 采用规则（口径 A 的 lot_flag，两袖耦合）。持仓与 w0 链条沿用口径 A 的决策；**只**把可行性标签按口径 C 重判。r4：每行另记该持仓的成书日 `_held_day`（209–215、269），供手数反推用当天收盘价。
2. **§8**：用与 v1.4 **同一份** `R.post_run_disclosures`（R@c844dbb4 1422–1500）：CLARIFY-1 两袖同日 + CLARIFY-2（无数据日留在 29 天分母、记不可证可行并列日期与原因、绝对 <24 → 升级 6% 单票帽问题至 Leo、对照 `ceil(0.8×n)` 只披露、judgeable 恒为 true、有效日 <24 直接升级）。**对照阈值由 R 第 1467 行 `ctrl_thr = (4 * nvalid + 4) // 5` 算（整数，等于 ceil(0.8n)）；D21 不另写一份，直接复用这一行。**
3. **缺行（Arch 裁定 1）**：disclosure 缺行仍算「不可证可行」，原因码 `disclosure_missing`，与 `NO_DATA` 分开计数（每档 `n_no_data_days` / `n_disclosure_missing_days`）；任一 >0 → `integrity_warning=true`，不阻断判定。D21 的 summary 顶层给 `integrity_warning`（三份 §8 任一为真即真）和 `integrity_warning_by_source`（D 450–452）。
4. **第二披露列（CLARIFY-2 §2.2）**：`replay(decide="C")`，唯一区别是第 266 行采用条件。反事实路径，**不是 v1.3**，只披露。
5. **复现核对 + 可引用标准（CLARIFY-2 §2.3）**：`repro_check`（334–398），见第 2 节。核对本身只披露、不作废。

## 2. 「手数一致」：两条路径（Arch 裁定 4）
**路径 1（优先，r4 采用）：v1.3 ckpt pkl。**
- 位置（ls 实测）：`output/strategy_optimizer/core_x2/_ckpt_v1_3_poolind/`，107 个文件 `20180102.pkl … 20261009.pkl`，无其他条目。由 canonical 29b38cf8（research/_runner_archive/optimizer_core_x2_run.29b38cf8.py，sha 29b38cf880ebb7c3c648b1f5a7936bedd14468d2ad472f9da96f087099bfc40a）写出。
- 逐文件 sha256 清单：`docs/v2/audit/V13_CKPT_V1_3_POOLIND_SHA256.txt`（每行 `文件名=sha256`，按文件名排序）。**该清单文件本身的 sha256 = 合并 sha = 95831abf30e406264a1986a6c3055dd91bdb874a403065b97f3f5d1a5d8c45aa**（合并规则同 combined：排序后 `name=sha\n` 逐行拼接再 sha256；D 125–128）。首尾两个：20180102.pkl=5706a49e1a29d308e667fd6a8df0111fb4ce457ba361022366d2a557bc42b447，20261009.pkl=70e2336a7fac48c4ff0ee8b8aabdda33ecd4713a01a77fe7546931d0f4c0a58d。
- **这是 pickle，只读仓库内已钩文件。** 新 .ok 键 `v13_ckpt_combined_sha256`（D 57–58）。启动前只算 sha、不反序列化（`ckpt_shas`，130；preflight 178–180）；运行中 `load_v13_ckpts`（137–148）一次读入每个文件的字节，先对这些字节算 sha、合并后与 .ok 比对，**一致才从同一份内存字节 `pickle.loads`**（146），不一致就 RuntimeError → VOID，什么都不反序列化。目录必须只含 `\d{8}.pkl` 普通文件、不得是符号链接（116–123）。加载放在 `R.end_of_run_recheck` 之前（430），所以加载模块检查也覆盖反序列化可能引入的模块；之后再核一次 ckpt 合并 sha（434）。
- pkl 里存了什么（只读源码得出，未反序列化）：29b38cf8 第 234 行 `rec = {"day", "w", "sleeves", "log"}`，第 276 行 `sl[sleeve] = {"w": wl, **li, **exposure_drift(wl, D)}`，第 283 行只在采用日写 `rec["sleeves"][a] = sl`，第 290 行 `pickle.dump`；b6238254 第 344–372 行结构相同（另加 version / smoke / code_sha256）。`li` 来自 `V.lot_round_greedy`（optimizer_core_v1_1.py b500c21b 第 210 行），键只有 `lot_flag / style_excess / cash / n / no_price`；`wl` 是 `q*P/aum`（第 128、197 行）。**结论：pkl 存的是整手后的权重簿，不存股数 / 手数。**
- 持仓展开（`ckpt_held`，316–328）与 29b38cf8 write_daily 第 140–151 行一致：某档当天有 `sleeves` 就换簿，否则沿用。

**路径 2（因此在路径 1 内部使用）：精确反推手数，不允许容差。**
- `exact_lots`（294–313）：对每个有有效价格的名字，取 `k = floor(w*aum/(P*L) + 0.5)`，**只有 `np.float64(k) * L * P / aum == w` 逐位相等**（正是 lot_round_greedy 第 128 行的同一表达式）才接受；否则记为「不可精确反推」，该日算手数不一致。P 用成书日（不是当天）的 PIT 收盘价（与 v1.3 同一调用 `_px`）；无价格的名字（lot_round_greedy 第 198 行保留目标权重）单独计数、只比权重；510300 压舱不算手数。
- 两边（复现簿、ckpt 簿）都用同一方法反推；成书日不同直接算不一致。

**可引用标准（代码 386）**：标签与 core_v1_3_disclosure.csv 逐行一致；每个调仓日对 parquet 权重和对 ckpt 簿的最大绝对差都 ≤ 1e-6；持仓集合三方一致；手数（双方精确反推、同一成书日）一致；ckpt 天数 = 调仓日 → `VALID`；否则 `VALID_WITH_DISCLOSURE`，「解释前不得引用」。

## 3. 门禁（与 v1.4 同规则）
- .ok：`output/strategy_optimizer/core_x2/ARCH_RUN_AUTH_D21_v1_3C.ok`（Arch 写；Strategy 不建），`--auth-sha256` 必填且等于其 sha。解析同 r3（D 82–97）。
- 启动检查（151–188）：4 份文档 sha（lotfix、停跑规则、CLARIFY-1、**CLARIFY-2**）、`R.check_clarify2`、掩码、输入路径、确定性环境、λ、全部 sha 全长比对、v1.3 产物、**ckpt 合并 sha**、解释器、out_dir、锁。
- 结束前复核（432–434）：`R.end_of_run_recheck` + v1.3 产物 + ckpt 合并 sha，变了就作废。排他写同 r3。

### .ok 键白名单模板（ARCH_RUN_AUTH_D21_v1_3C.ok；白名单 = 必填，共 40 个键；r3 为 39 个，r4 增 1 个）
```
format=quantlab_run_auth_v1
version=d21_v1_3_basisC
signed_by=arch
signed_et=<ISO8601 带时区，不得在未来>
expires_et=<ISO8601 带时区，晚于 signed_et>
allow_full=true
allow_smoke=false
live=false
promotion=false
python_exe=/workspace/QuantLab/.venv_opt/bin/python
out_dir=output/strategy_optimizer/core_x2/v1_3_basisC_d21
runner_sha256=497f9a2b59fa314adc54341f5f942a924c12fce6616ecf11694eb65d94e9fc6f
combined_sha256=ffa812fd05f8526345b3613227aec97038ab00a56a4338449a328a8db431a416
lotfix_sha256=d921dd3f0f698deb822a59e40aa643f1efc7f43f6c36eaed30c7a672dbdf9425
stoprule_sha256=41f29825c85a66c889474460605b45a19f5fa475ae46570f299416535cb3559b
clarify_sha256=d075a2a68f2d5c42c750669cdff2dd51f93794e11ea907f08ffc29c39c724d85
clarify2_sha256=85e843cd6c68d7a0d8c0035ebeab7c34e00e4ea76a799c95de0655c20445651b
<v1.4 的 7 个数据键、10 个 nt_* 闭包键、4 个 v13_w_* 键：与 STRATEGY_V1_4_RUNNER_CHANGES_ZH.md §r3.2 逐行相同>
v13_disclosure_sha256=9586e5f3ecde6580c5b232a4823fe167814f49a697c823acaea46be688bc2c1b
v13_ckpt_combined_sha256=95831abf30e406264a1986a6c3055dd91bdb874a403065b97f3f5d1a5d8c45aa
```
r4 增量：新增 `v13_ckpt_combined_sha256`；`clarify2_sha256` 由占位改为实值（键名不变，现在挂在 PINNED_DOCS 里）；`runner_sha256`、`combined_sha256` 换新值。

## 4. 启动命令（只在 Leo 定 Core 继续之后；D21 先于 v1.4、串行；D21 回执经 Arch 审过再签 v1.4 .ok；CLARIFY-1 §4、CLARIFY-2 §3）
```
cd /workspace/QuantLab && PYTHONHASHSEED=0 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 nohup /workspace/QuantLab/.venv_opt/bin/python research/optimizer_core_v1_3_basisC_recalc_d21.py --auth-sha256 <ARCH_RUN_AUTH_D21_v1_3C.ok 的 sha> > output/strategy_optimizer/core_x2/d21_run.log 2>&1 &
```
PYTHONPATH/PYTHONHOME/PYTHONSTARTUP/PYTHONUSERBASE 不得设置。

## 5. 待裁定 / 知悉
1. 精确反推只在 v1.3 运行时的浮点表达式与现在完全一致时成立（同一 numpy 版本、同一表达式顺序）。如果 canonical 用的 numpy 与 .venv_opt 不同导致个别名字不能逐位还原，会计入 `n_days_lots_not_exactly_reconstructible`，结论为 VALID_WITH_DISCLOSURE，不会放宽成容差。
2. 合成单测 T 加了一个 D21 纯函数测试（`exact_lots` 逐位还原、差 1 ulp 即拒；ckpt 合并规则；新键在白名单里）；按规定未运行。
3. R 每改一次，D21 的 combined 和 .ok 都要重签。
