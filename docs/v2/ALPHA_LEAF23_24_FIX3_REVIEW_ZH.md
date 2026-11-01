# Alpha 复审：叶23 r2.4 / 叶24 r3（fix-3 diff）

- 时间：2026-10-18 约 02:45 ET，QuantLab Alpha。**只读静态审**：没有运行项目代码、测试或 py_compile。只做了 sha256sum 和读文件；在 /tmp 用备份副本做 `patch -p1` 逐字节比对，比完已删除；用 pyarrow 读了 delisted_master 的 schema（元数据，不读数据行）。
- 承接 `ALPHA_LEAF23_24_FIX2_REVIEW_ZH.md`（77441f16）。那份文档已被两份 prereg_sha 清单钉住，所以不在原文追加，另开本文件。
- 依据：Arch `ARCH_LEAF23_24_FIX2_REVIEW_ZH.md`（bd3abe5c），以及主 Agent 约 02:33/02:38 ET 关于叶24 保留 vol20_{t−1} 的裁定。
- live=false；promotion_approved=false。

## 0. 结论：**READY_FOR_ARCH_OK**（Alpha 侧）

- 77441f16 提的四项（f-string、ladv1、acap 取 t−1、叶24 vol20）都已按要求改好。
- Arch bd3abe5c 的新项（P1-A 退市截断、P2-A expires_et、P2-B 窗口末沿用断言、P3-A～D）没有给信号带来前瞻，也没有事后改口径。
- 两份预注册都没改；sha 清单已更新，旧版本都标了 superseded。
- 剩下的只有 P3 级的披露事项（§3），不需要再改代码。
- 签 .ok 的前提不变，都不在 Alpha 范围内：
  - Data 的 D1b 重建 execute 要完成，回执要经 Arch 审过；
  - Arch 要写好 `.cmd`；
  - 空值键要在签发时实测回填：manifest、mask、`data_delisted_sha256`（当前实测 63590f23…）、tool_cmds、issued_at、expires_et。

## 1. sha 核对

| 项 | 期望 | 实测 |
|---|---|---|
| diff `AI_LEAF23_24_ARCH_FIX3_DIFF.patch` | e77262de… | e77262de08202e52ab7f095afba066e71733c76692865866ccbd618c50bafdd3 ✓ |
| 叶23 r2.4 | ccde59eb… | ccde59eb299fe3ae339d8c75ba0b4d761d5aa5c0e320e2a711dc228c86608ae6 ✓ |
| 叶24 r3 | 101600f6… | 101600f67b9447f5a13291a10b4e6eefbd2567c950d005e6647ab09d84424f12 ✓ |
| 备份 `_recovery/ai/pre_arch_fix3_0233/` 加 diff | 还原后与现文件逐字节相同 | 备份为 f011b277 / 6f57c82d；在 /tmp 打补丁后 cmp，两份都 IDENTICAL ✓ |
| 叶23 预注册 | 8f5d8ac4… | 8f5d8ac43ba4… ✓ 未改 |
| 叶24 预注册 | c289e770… | c289e77068be… ✓ 未改 |
| delisted_master | 63590f23…（Arch 审时实测） | 63590f23171dbaaaf29ff51edce564130d2e8296630e1f448396fe9b8191d6fd ✓；schema 含 ts_code、last_trade_date、delist_date |

## 2. 逐项裁定

**(1) TOOL_CMDS — OK**
- 两叶都改成了 `TOOL_CMDS = AIF/f"ARCH_TOOL_CMDS_LEAF{LEAF_NO}_X2.cmd"`（叶23 第 85 行、叶24 第 73 行）。
- `R = Path(__file__).resolve().parents[1]`，`readlink -f` 实测为 `/workspace/QuantLab`。所以 `str(TOOL_CMDS)` 等于 `/workspace/QuantLab/output/ai_factory/ARCH_TOOL_CMDS_LEAF23_X2.cmd`（叶24 是 `…LEAF24_X2.cmd`），与 Arch bd3abe5c 草案第 133、190 行逐字一致。

**(2) ladv1 — OK**
- 现在是 `"ladv1": np.log(AD.clip(lower=1e4)).astype("float32")`，已去掉多余的 shift。
- 面板的 `adv20_yuan` 来自 mask（`all_a_universe_mask.py` 第 79–89 行，`prior = sess[sess < S][-ADV_WIN:]`），t 日的值就是 t−20..t−1 的均值，属于 t−1 口径，与冻结的 s8 一致。
- 两叶相同，注释也写明了出处。

**(3) 叶23 acap — OK**
- `CAPW["acap"] = CAPW.groupby("instrument", sort=False).acap.shift(1)`，先按 `["instrument","date"]` 排序；读入时多读 20 个日历日，滞后之后再截到 X2 起点。
- capacity 腿文件是矩形网格：5382 名 × 668 日 = 3,595,176 行，与 meta 的 n_rows 一致。所以按名 shift(1) 正好是上一交易日的腿权重，未持有记 0。
- acap 只进第一段 OLS（`X = …, g.acap… - g.acap.mean()` 后接 `r1 = FE.ols_resid(raw, X[ok])`），第二段仍然只对 `D[ok], S[ok][:, :1]` 回归。
- 稀疏性已在 notes 里写明（每日约 25 名非零，HI_LIQ 池约 800 名，相当于一个哑变量，力度弱，最终 α 对它不严格正交），也写明了这是事先冻结的选择。

**(4) 叶24 vol20 — OK**
- `feats["vol20"] = RW.astype("float64").shift(1).rolling(20, min_periods=15).std()`：取 t−20..t−1 共 20 个交易日总收益的标准差，至少 15 个有效值。
- 这与 r1 原来的 vol20 定义逐字相同，也与预注册 §4 第 50 行一致（「vol20 留在回归里：本叶要的是「波动之外的右尾」」）。
- 回归项是 `S = g[["lmv1","beta120","mom_120_20","ladv1","vol20"]]`，即冻结集取超集；vol20 也加进了 dropna。
- IMAX 窗口是 [t−19, t]，vol20 是 [t−20, t−1]，两者重叠 19 天。预注册本来就这样设计（剥离的是同期波动），不算前瞻。
- e_id 仍然只对 SW L1 + logmv_{t−1} 回归（Arch §3.3 裁定），与预注册 §3 一致。
- 叶23 没有加 vol20，因为预注册没有给它机制含义，已在 notes 里披露。

**(5) Arch 新项 — OK，没有前瞻，也没有事后改口径**
- **P1-A 退市截断。** 对 `d > last_trade_date` 的日子（last_trade_date 缺失时用 delist_date），状态 S 记 False，市值链断开。这一步只影响 **pool EW/wb 基准成员**，不进信号、α、选书。被截断的名·日数（`delisted_cut_name_days_x2`）和 NaT 回退数都有披露。
  - 这里用到了一项「事后」信息：某名停牌后再也没有复牌。这是基准口径的问题，不是信号前瞻。退市后的持仓在现实中也无法再计收益，Arch 已经裁定。
  - 预注册「停牌记 0、不剔分母」不受影响，因为退市不是停牌，notes 已写明。
- **P2-A expires_et。** 已加入 OK_REQUIRED，要求带时区，在 authorize 和每个阶段开始（panel_recheck）各核一次，且 `expires_et > issued_at`。属运维约束，与口径无关。
- **P2-B 窗口末沿用断言。** 如果有名沿用到窗口末尾、但它在 delisted_master 里，就停跑。只会导致停跑，不会改变数字（P3 说明见 §3）。
- **P3-A～D。** not_suspended 恒为 0 已注明；与 s8 的锚点差异已披露（见本审 B 部分，`ALPHA_S8_LAG_SELFCHECK_ZH.md`）；nv120 只作披露，不进回归；遇到 .BJ 就停跑。都只是披露或停跑，不改口径。
- **TOOLS 与 repin。** delisted 加进了 TOOLS，读之前用 `repin_file` 重新核对。`AUTH_TOOLS` 在 authorize 末尾填好，不会出现空字典导致误放行：值为空时 `.get()` 返回 None，不会等于 sha，结果是拒跑，属于失败即拒。
- **sha 清单。**
  - 叶23：r2.3 f011b277 已标「superseded by script r2.4」，当前是 r2.4 ccde59eb。
  - 叶24：r2 6f57c82d 已标「superseded by script r3」，当前是 r3 101600f6。
  - 两份都把 FIX2 diff 416e237a 标为 superseded，FIX3 e77262de 标为 current，并新增了 bd3abe5c、77441f16、63590f23（delisted，注明「签发时重测」）。

## 3. P3 披露事项（不阻断，不要求改代码）

1. **P2-B 可能误停。** 判定条件是 `set(end_carry_names) & set(cut.index)`，只要名字在 delisted_master 里就算命中，不管退市日是否晚于窗口末。如果某名在 10-09 前停牌、在窗口之后才退市（也就是窗口内的停牌是真的），也会被停跑。这是失败即拒，不产出错误数字，与 Arch P2-B 原文一致。若真的触发，由 Arch 逐名裁定。
2. **退市截断用了事后信息。** 只用于基准，见 §2(5)。回执里应写一句：「基准成员在 last_trade_date 之后剔除，使用了事后才知道的退市信息，不进信号。」
3. **vol20 进 dropna 会少量缩小覆盖。** 窗口 20 天、至少 15 个有效值，ST 或停牌后的头几天会被丢掉。由 build meta 的 coverage 和 p3c 字段披露即可。
4. **正式验收口径不变。** §8 在冻结风格集上另行重做，GATE_V3 以 Alpha 工具为准，还要另报对池 EW 的超额。

live=false；promotion_approved=false。本审没有建 .ok，没有运行任何项目代码，FROZEN_CONFIG 和纸面轨都没有动。
