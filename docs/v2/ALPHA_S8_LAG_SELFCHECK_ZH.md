# Alpha 自查：`research/alpha_hiliq_s8_paradigm.py`（af48bc05）风格暴露的时点（回应 Arch bd3abe5c P3-B）

- 时间：2026-10-18 约 02:50 ET，QuantLab Alpha。**只读**：没有运行任何项目代码。核对了 `alpha_hiliq_s8_paradigm.py` 的 sha 为 af48bc05fbcfb55e72336806c03455dbf4f0b52079c833aed9f141bece00966c。另外只读了几份已有产物的元数据和数值：`_panel_close.parquet` 的日期索引、`ALPHA_HILIQ_S8_run20261017.json`（cea7cff0）。
- 一并看了直接复用 s8 的脚本：`alpha_s8_errata_fullsleeve_b_v41.py`（e88b88e7）、`alpha_s8_errata_sparse_ic.py`；以及判定工具 `alpha_combo_marginal.py`（bee23019，与 s8 是同一套风格写法）。
- live=false；promotion_approved=false。没有改任何代码或冻结物。

## 0. 结论

1. **没有真正的前瞻。** 在所有用途里（A、A′、CMC、B、step_c 的 (i)/(ii) 两种读法），每一项风格暴露使用的信息都严格早于对应的收益窗口，没有任何重叠。
2. **差异只是「t」锚在哪一天。** 有两种约定：
   - s8 冻结实现按**收益日**定 t−1：B 部分对收益日 r 使用 r−1 的暴露；A、A′、CMC 部分对前瞻窗口 [d+1, d+20] 使用信号日 d 收盘的暴露。
   - 叶脚本（主 Agent 02:23 裁定）按**信号日**定 t−1。
   - 在 A、A′、CMC 中，logmv 和 beta120 比叶脚本晚一天（用到 d 日收盘），mom 也以 d 为锚，比叶脚本晚一天。**logADV20 已经是 t−1，两种约定下都合规。**
3. **对已有 §8 判定的影响：** B 部分本来就是 t−1，不受影响。A、A′、CMC 部分改一天，暴露截面相关大于 0.99，数值变化预计在 1e-4 量级。v4/v4.1 各腿的总判定（all_pass / status）**不可能翻转**，只有个别分项的余量很薄（见 §3）。
4. **建议：不在原文件上改。** 原因是 v4.1 复现脚本 e88b88e7 和 step_c 都 `import research.alpha_hiliq_s8_paradigm as S8`，改动会破坏刚被 Arch 判为 VALID_WITH_DISCLOSURE 的复现链。做法如下：
   - 在 S8 规则文档里写一条澄清：t−1 指相对收益日；
   - 后续叶子另开 v1.1（新文件，新 sha），信号残差化改按信号日 t−1 取暴露，标注「事后、只适用于后续叶子、阈值不变」；
   - 运行要拿 Arch 的 .ok，先报主 Agent。

## 1. 记号

- 信号日 d：腿权重 `sig(c, path)` 和风格暴露都按 `ev` 索引在 d 行。
- 前瞻收益（第 54 行）：`F = C.shift(-H)/C - 1`，从 d 日收盘到 d+20 日收盘，也就是**收益日 d+1..d+20**。
- B 部分的收益（第 101–111 行 `resid_ret`）：收益日 r 用 `xmat(c, d0)` 回归，其中 d0 是 r 的前一个 ev 日，即 r−1。`neut_net` 再用 `W.shift(2)`，权重在 r−2 决定，在 r 日计收益。
- step_c 读法 (ii)：`FN = E.shift(-2).rolling(H).sum().shift(-(H-1))`，d 行对应收益日 d+2..d+21 的中性化收益之和。

## 2. 逐项暴露：d 行实际用到哪些日期

| 暴露 | 代码行 | d 行使用的数据 | A/A′/CMC（`resid_multi` → `xmat(c, d)`，对 F 的收益日 d+1..d+20） | B（`resid_ret` → `xmat(c, r−1)`，对收益日 r） | 相对冻结规则「全部 t−1」 |
|---|---|---|---|---|---|
| log 流通市值 mc | 59–63 | d 日收盘的 float_mktcap（缺失时向前填） | 最晚到 d 日收盘，**早于** d+1 收益日，无重叠 | r−1 日收盘，无重叠 | 按收益日算是 t−1 ✓；按信号日算是 t（差一天） |
| beta120 | 52 | 收益日 d−119..d（含 d），需要 d 日收盘 | 最晚到 d，无重叠 | 收益 r−120..r−1，无重叠 | 同上：按收益日 ✓，按信号日差一天 |
| mom | 53 | `C.shift(20)/C.shift(120)−1`，即收益日 d−119..d−20 | 截止 d−20，无重叠 | 截止 r−21，无重叠 | 文字「t−120→t−20」以 d 为锚逐字一致；叶脚本的 t−1 版是 C(d−21)/C(d−121)，s8 比它晚一天 |
| logADV20（liq） | 31、67 | mask 的 `adv20_yuan[d]`，是 d−20..d−1 的成交额均值（`all_a_universe_mask.py` 第 79–89 行，`sess < S`） | 截止 d−1，无重叠 | 截止 r−2（比 t−1 还多滞后一天，偏保守） | **已经是 t−1 ✓**，不用改 |
| SW L1 | 64–66 | 不晚于 d 的最近一个月末的成员（月中向前填） | 无重叠 | 无重叠 | ✓ |
| 池 INU | 29 | mask 的 `in_universe[d]`，用 d 之前的数据构造 | — | 用 r−1 的池 | ✓ |

**另外查了一项窗口边界（P3，不是前瞻）**
- `_panel_close.parquet` 的日期截到 2026-10-14，比 X2 末日 10-09 多出 3 个交易日（10-12、10-13、10-14）。
- 所以最后几个 d 的 F（d+20 落在 10-12～10-14 的那 3 个信号日）用到了 X2 末日之后 1–3 天的收益。对 IC 序列的影响可以忽略。
- 以后在 v1.1 里把 F 截到 END，并在披露里写明。

**结论**
- s8 冻结实现中，A、A′、CMC 和 step_c 的信号残差化，用的是**信号日 d 收盘时已知**的暴露，前瞻收益从 d+1 开始，没有重叠。
- B 的中性化收益用的是 r−1 的暴露，与 v4.1 脚本头部和 LEGS_ACCEPT 第 88 行写的「冻结风格集使用 t−1 暴露」一致，那条说法指的就是 B。
- 但规则文档 `ALPHA_HILIQ_S8_PARADIGM_RULES_20261014_ZH.md` 第 6 行只列了风格，没有写锚点。团队摘要里的「全部取 t−1」容易被理解成按信号日算，这正是 Arch P3-B 指出的不一致。
- 判定工具 `alpha_combo_marginal.py` 也是同样的写法：第 90 行 beta 含 d 日，第 97 行 MC 取 d 日收盘，第 115 行按 d 取用。同样不是前瞻，同样只是约定差一天。它的 sha 已钉进叶23/24 的 .ok，**这次不动**。

## 3. 改了会不会影响 v4/v4.1 的 §8 判定（定性，不运行）

- **B（vB，以及 v4.1 的全袖套 B）：不受影响**，因为本来就用 `xmat(c, d0=r−1)`。
- **A、A′、CMC：** mc 的日间自相关约 0.999；beta120 只换了 1/120 的窗口；mom 的窗口重叠 99%；liq 和 IND 不变。残差化后的 z 只会有很小的变化，IC 差异预计在 1e-4 量级。
- **对照 run20261017 的各腿余量（cea7cff0）：**
  - 所有腿的 A′ 都没过：dIC 在 −0.0023～+0.0010 之间，门槛是 ≥0.003；dICIR 不超过 0.021，门槛是 ≥0.05。差距远大于 1e-4。
  - 有四条腿的 B 也没过。
  - 所以 **all_pass 和 status 都不可能翻转**。
- **余量很薄的分项（可能翻转，但不影响总判定）：**
  - insurer_surv 的 A：icir_roll252_median 为 0.0038 > 0；
  - earnings_event 的 A：IC 0.0030，icir 0.024。
  - 两条腿的 A′ 和 B 都没过，insurer_surv 还受类型帽限制，所以仍然是 WATCH。
- **v4.1 中 equity_incentive 的 CMC +0.0026（门槛 0.003）：** 来自 CMC 工具，也是同样的锚点。若要把它推到门槛，需要多出 +0.0004，比预期的影响大好几倍，可能性很小，但不运行无法证伪。不管怎样，按「事后、只适用于后续叶子、阈值不变」的原则，v4/v4.1 已有判定保持不变。

## 4. 修法建议（新文件 v1.1，不改 af48bc05）

1. **文档澄清（马上做，不涉及运行）：** 在 `ALPHA_HILIQ_S8_PARADIGM_RULES_20261014_ZH.md` 追加一行勘误：「风格暴露 t−1 指相对收益日：B 用 r−1；A/A′/CMC 用信号日 d 收盘时已知的暴露（前瞻窗口自 d+1 起）；logADV20 来自 mask，已是 d−20..d−1。」并注明是事后澄清，不改判定。
2. **代码，新文件 `research/alpha_hiliq_s8_paradigm_v1_1.py`：**
   - 第 52 行之后：信号用的 beta 取 `beta_sig = beta.shift(1)`（在交易日索引上 shift 后再 `.reindex(ev)`）；
   - 第 53 行：信号用的 mom 取 `mom_sig = C.shift(21) / C.shift(121) - 1`；
   - 第 63 行：信号用的 mc 取 `MC_sig = MC.shift(1)`（在 ev 索引上）；
   - 第 67 行：另建 `X_sig = dict(mc=MC_sig, beta=beta_sig.reindex(ev), mom=mom_sig.reindex(ev), liq=<原 liq 不变>)`。原来的 `X` 留给 `resid_ret`，否则 B 会变成 t−2；
   - 第 74–83 行：`xmat(c, d, key="X")` 增加参数，缓存键改为 `(d, key)`；
   - 第 90 行：`resid_multi` 改用 `xmat(c, d, key="X_sig")`，池仍取 d；
   - 第 54 行：F 截到 END，`F = (C.shift(-H)/C - 1)`，并对 `d+H > END` 的样本设为 NaN（或单独披露）。
3. **CMC 工具 `alpha_combo_marginal.py`（第 90、97、115 行）** 按同样方式另出新版本。旧 sha bee23019 已钉进叶23/24 的 .ok，换版本需要 Arch 重新签发，先报主 Agent 裁定是否需要。
4. **v1.1 运行前提：** 先报主 Agent，拿到 Arch 的 .ok；用 `nice -n 10` 串行跑，自己记录峰值 RSS（≤1.5GB，按年分块）。结果只作「事后、只适用于后续叶子」的对照披露，v4/v4.1 不改写。

live=false；promotion_approved=false。本次自查没有运行代码，FROZEN_CONFIG 和纸面轨都没有动。
