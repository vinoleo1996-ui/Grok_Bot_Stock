# Alpha 复审：叶23 r2.3 / 叶24 r2 修复 diff（fix-2）

- 时间：2026-10-18 ET，QuantLab Alpha。**只读静态审**：未运行叶脚本、未跑测试、未 py_compile；只做 sha256sum、读文件，在 /tmp 用备份副本做了 `patch -p1` 逐位比对（随后删除），另用 pyarrow 读了 mask 的 parquet 元数据（不读数据行）。
- 依据：Arch 附录 `ARCH_LEAF23_24_FIXDIFF_REVIEW_ZH.md`（129d67c5）、Alpha 预读 `ALPHA_LEAF23_24_PREREAD_ZH.md`（8586ffd0）、主 Agent 02:23 ET 裁定。
- live=false；promotion_approved=false。

## 0. 总结论：**NEEDS_FIX**

1 个阻断项（两叶都有）：**`TOOL_CMDS` 路径少了 f 前缀**，脚本会拒绝 Arch 按草案签发的 .ok，运行不了。这是失败即拒跑，不会产出错误数字，但签 .ok 之前必须先修。

另有 3 项要在同一个补丁里处理或拿到裁定：
- 叶24 去掉 vol20，与预注册写明的机制相冲突，需要主 Agent 明确裁定；
- 叶23 的 capacity_adv 暴露取了当日值，没有取 t−1；
- logADV20 多滞后了一天。

其余（P1-1、P1-2、P1-3、P2-1～P2-6、产出字段、sha 清单）核对后正确。

## 1. sha 核对

| 项 | 期望 | 实测 |
|---|---|---|
| diff `AI_LEAF23_24_ARCH_FIX2_DIFF.patch` | 416e237a… | 416e237a7fd4e5e4c233b6dc061fd2ae1150ea56554222616d7731491c0254bd ✓ |
| 叶23 r2.3 `research/g1g5_sue_desens_cs_alpha.py` | f011b277… | f011b27714cd153f3e1a1ef6e6466ad855ca798942a9899ffb497b884fdfa14f ✓ |
| 叶24 r2 `research/g1g5_imax_intraday_alpha.py` | 6f57c82d… | 6f57c82d6e37e76308270dae4add51f0919912cdf296e6f7ea130d6366b7311c ✓ |
| 叶23 预注册 r2.1 | 8f5d8ac4…（不得改） | 8f5d8ac43ba49f11b4461a287addae8c0cf247fbe9d8e81d0b339764e843922e ✓ 未改 |
| 叶24 预注册 | c289e770…（不得改） | c289e77068be607c108359a87e1d17d6b2e8edac9e4cbcca865a9a49430133a8 ✓ 未改 |
| 备份 `_recovery/ai/pre_arch_fix2_0217/` 加 diff，能否还原新文件 | 逐位一致 | 备份 sha 为 81c2b4e6 / de87c839；在 /tmp 打补丁后 cmp，两份都 IDENTICAL ✓ |
| capacity_adv 腿权重 `g1g5_capacity_adv_hiliq_v1_1_daily_weights_20261014_195620.parquet` | 3b288c83… | 3b288c832b956820af9802f02861af459e215e7d4097a6420724b26cf2d31c4d ✓（与 check.json 的 weights_sha256 一致） |
| mask `universe_mask_hiliq_v1.parquet` | c5433e80… | c5433e80…af9 ✓；日期覆盖 2017-12-01～2026-10-14，含 st/suspended/young/adv_fail 列，全 A |

## 2. 逐项裁定

| # | 项 | 结论 |
|---|---|---|
| 1a | 冻结风格集的组成（SW L1 dummy + logmv + beta120 对 510300 + mom t−120→t−20 + logADV20） | **OK** |
| 1b | 全部取 t−1，没有当日值 | **ISSUE（P2，偏保守，不是前瞻）**：logADV20 多滞后一天，见 §3.2 |
| 2 | 叶23 的 capacity_adv 残差化 | **OK（确实是残差化，不是混合权重）**，附 **ISSUE（P2）**：暴露取当日值、不是 t−1；稀疏暴露要写明，见 §4 |
| 3a | P1-1：ST 和停牌分开处理沿用 | **OK**（另有 P3 说明） |
| 3b | P1-2：敏感性变体绑定 .ok | **OK** |
| 3c | P1-3：进程检查不被 Data 常驻抓数挡住 | **OK** |
| 3d | P2-1：.ok 白名单，拒未知键 | 逻辑 **OK**，但 **ISSUE（P1，阻断）**：`TOOL_CMDS` 少 f 前缀，见 §5 |
| 3e | P2-2～P2-6（含 302/689 涨停） | **OK** |
| 4 | `b3_pool_carry`、`forecast_branch_names_2024_06_08` 字段 | **OK** |
| 5 | prereg_sha_leaf23/24.txt | **OK** |
| 6 | 新的前瞻或事后改口径 | 未发现前瞻。**ISSUE（P2，需主 Agent 裁定）**：叶24 去掉 vol20，与预注册写明的机制冲突，见 §6 |

## 3. 第 1 项：风格集与 t−1

### 3.1 组成
两叶的 `style_feats` 逐字相同：
```
beta = R64.rolling(120, min_periods=60).cov(b).div(b.rolling(120, min_periods=60).var(), axis=0)
mom = np.expm1(np.log1p(R64).shift(21).rolling(100, min_periods=80).sum())
return {"lmv1": LM.shift(1), "beta120": beta.shift(1).astype("float32"), "mom_120_20": mom.astype("float32"),
        "ladv1": np.log(AD.clip(lower=1e4)).shift(1).astype("float32")}
```
回归项：`S = g[["lmv1", "beta120", "mom_120_20", "ladv1"]]`，加上行业 dummy D（叶23 第 501 行，叶24 第 1132 行，行号指 diff）。bench 是 510300.SH 的 `close_hfq.pct_change()`。mom20、mom60、vol20 都已删除。组成正确。

### 3.2 滞后逐项核对
- **logmv**：`LM.shift(1)`，面板 logmv 是 t 日收盘的流通市值，所以这里是 t−1。✓
- **beta120**：滚动窗口含 t，再 `shift(1)`，得到 [t−120, t−1]。✓（冻结版 `alpha_hiliq_s8_paradigm.py` 第 52 行没有滞后，叶脚本更严，没问题。）
- **mom**：`shift(21)` 加上 100 日求和，得到 ret[t−120..t−21]，即 C(t−21)/C(t−121)−1。这正是冻结口径 mom(t−120→t−20) 再取 t−1。s8 第 53 行是 `C.shift(20)/C.shift(120)−1`，叶脚本又多滞后了一天，可以接受。不含最近 20 日。✓
- **logADV20：多滞后一天（P2）。**
  - 面板的 `adv20_yuan` 来自 mask。mask 由 `research/all_a_universe_mask.py` 第 79–89 行生成：`prior = sess[sess < S][-ADV_WIN:]`，`adv20_yuan = A.mean(axis=1)`，也就是 t 日的值已经是 [t−20, t−1] 的均值，**不含 t 日**。重建脚本 `scripts/fix_sd1/build_cs_panel_v2_resumefix.py` 第 120、145 行原样沿用这一列。
  - 叶脚本再 `shift(1)`，实际用的是 [t−21, t−2]，比冻结 s8 版（第 31、67 行，直接用 mask 的 adv20_yuan）多滞后一天。
  - 方向偏保守，不构成前瞻，但与冻结集不一致。**修法：ladv1 直接取当日 adv20_yuan，不再 shift，并在注释写明它已是 t−1 口径。**
  - **Alpha 自我更正：** 预读 8586ffd0 §4 说「logADV20 取当日 adv20_yuan，未 shift(1)」，这个判断有误。该列本来就是 t−1 口径，以本节为准。
- **说明（P3）：** beta 的分母用的是 510300 全部 120 天的方差，分子是成对的 cov，个股有缺失日时两者不严格配对。s8 写法相同，不改，只披露。

## 4. 第 2 项（重点）：叶23 的 capacity_adv 是残差化，还是混合权重

**预注册原文（8f5d8ac4，未改）**
- §1 第 55 行：「本文「去敏」**只指残差化**（对风格、capacity_adv、行业、叶19/20 回归取残差），与叶20 用法一致。」
- §4 第 95 行：「回归项 = SW L1 dummy + 前一交易日 log 流通市值 + mom20 + mom60 + vol20 + log ADV20（capacity_adv 机制代理）+ 叶19 … + 叶20 …」
- 也就是说，预注册的意思是**残差化**，不是混合权重。§4 原本把 logADV20 当作 capacity_adv 的代理，主 Agent 02:23 裁定要求代码真正对 capacity_adv 做残差化。

**代码（f011b277）**
```
CAPLEG = R/"output/strategy_hiliq/legs/g1g5_capacity_adv_hiliq_v1_1_daily_weights_20261014_195620.parquet"
# prereg r2.1 §1 "去敏 = residualize on style, capacity_adv, industry, leaf19/20": capacity_adv exposure = its HI_LIQ v1.1 leg target weight
# on the same session (0 if not held; 510300 balance row dropped; PIT like the leaf19/20 α), demeaned in the daily OLS
CAPW = pd.read_parquet(CAPLEG, columns=["date", "instrument", "target_weight"], ...).rename(columns={"target_weight": "acap"})
P = P.merge(CAPW, on=["date", "instrument"], how="left")
P[["a19", "a20", "acap"]] = P[["a19", "a20", "acap"]].fillna(0.0)
X = np.column_stack([D, S, g.a19... - g.a19.mean(), g.a20... - g.a20.mean(), g.acap.to_numpy(float) - g.acap.mean()])
r1 = FE.ols_resid(raw, X[ok])
```

**结论**
- capacity_adv 腿的权重**作为回归自变量**进入第一段截面 OLS，对原始信号 `raw` 取残差，这是正交化，**不是**把 capacity_adv 腿混进组合权重。
- 选书 `pick_book` 和书收益都没有用到 acap。AI 说的「加入 capacity_adv 腿权重」措辞容易让人误解，实际做的是对它的持仓暴露做残差化，与预注册一致。✓
- 与叶19/20 α 的处理方式一样，acap 只进第一段 OLS；第二段（行业 + lmv1）不含 acap，所以最终 α 对 acap 不是严格正交。这是原设计的一部分，只作披露。

**问题**
- **(a) P2：当日值，不是 t−1。** 代码写的是 "on the same session"，按 `date` 当日合并。冻结规则是全部暴露取 t−1。该腿按 D1 的 asof ADV 生成，属于 t 日收盘时可得的信息，所以不构成交易前瞻。但它与风格集的 t−1 口径不一致。**修法：** 按每个名字把 acap 滞后一个交易日（t−1）再合并；或者由 Arch 书面认可「当日目标权重」口径。
- **(b) P3：暴露很稀疏，要写明。** check.json 显示每天 26 行有权重（25 只股票加 510300），HI_LIQ 池约 800 名，其余全记 0。这个回归项基本相当于「是否被 capacity_adv 持有」的哑变量，只能去掉持仓名与非持仓名之间的均值差，正交力度有限。连续的容量暴露已经由 logADV20 承担。预注册没有规定用哪种暴露（权重还是得分），选择权重属于运行前的实现决定，需要在回执里写明并冻结，以后不得换。
- **(c) .ok 新键。** 新增的 `dep_capadv_leg_sha256` 不在 Arch §6.1 的 .ok 草案里。按新的白名单逻辑，缺了这个键会拒跑，签发时要加上：`dep_capadv_leg_sha256=3b288c832b956820af9802f02861af459e215e7d4097a6420724b26cf2d31c4d`。prereg_sha_leaf23.txt 已经注明这一点。
- **(d) 关于文件时间。** 该腿文件的 mtime 是 10-18 01:14（重启时恢复的），sha 与 check.json 一致，可以使用。

## 5. 第 3 项：Arch P1/P2

- **P1-1 ✓**
  - `pool_benchmarks` 从 2018 年起逐年递推，状态向量 `sp` 跨年传递。
  - 判定规则：`carry = (~has) & (sus == 1.0)`；`A = val.where(has, 0.0).mask(carry)`。效果是：有面板行时取该行的 col；无行且 mask 停牌时沿用上一状态；无行但不是停牌（ST、成交额不足、次新）时记 False，沿用中断；mask 无行时也记 False（退市就是此后 mask 无行，窗口末尾停牌的名照常沿用）。
  - 流通市值只在停牌段内沿用：`B = lmv.where(has & lmv.notna(), -np.inf).mask(carry)`，-inf 表示中断。
  - `verify_panel` 核对 `pins.mask_sha256 == ok["data_mask_sha256"]`；eval 前执行 `repin(auth, "data_mask_sha256")`。
  - 停跑条件：`carry_mismatch` 或 `not_suspended` 任一大于 0。
  - 旧写法（不沿用）和 r2.2 写法（无行即沿用）的 EW/wb 年化差都写进了 b3，只作披露。
  - 与 Arch §3 第 1–8 条逐条对应。
  - **P3 说明：** `carried_by_mask_reason_x2["not_suspended"]` 按构造恒为 0（沿用本来就要求 mask 停牌），这项自检不会触发。真正有效的检查是「Mp == carry_col」。不用改，回执里写明即可。
- **P1-2 ✓** 非主口径要求 `allow_sensitivity == "true"`，且 `variant_tag(a) in ok["sensitivity_specs"].split(",")`。多因素组合会拼成 `a_b`，不在清单里，所以被拒。两叶的 tag 都与清单一致：叶23 是 sig-sue、denom-daily、nofc、bo40；叶24 是 src-total、k1、win60、exfin。
- **P1-3 ✓** 拦截条件：`hit = ("python" in cmd and "research/" in cmd) or any(t in cmd for t in BLOCK_CMDS)`，BLOCK_CMDS 是 fix_sd1/、scripts_eng/、nightly_update.py。`scripts/acquire/` 只记录不拦。整条祖先链都排除。另外要求 niceness ≥ 10、MemAvailable ≥ 2GB，ps 快照写进 meta。
  - Data 常驻抓数 94322、94403 只会被记录，不会挡住运行。
  - **运维提示：** 本审读 ps 时（约 02:3x ET）`scripts/nightly_update.py --date 20261016 --steps sw`（212762）正在跑，这时开跑会按设计被拒，要等它结束。
- **P2-1：逻辑 ✓，但有阻断 bug ✗。** 白名单的写法是 `unknown = sorted(set(ok) - allowed)` 就拒跑、缺键也拒跑，fixed 值全部核对，issued_at 要求带时区。问题在两叶的这一行：
  ```
  AIF = R/"output/ai_factory"; TOOL_CMDS = AIF/"ARCH_TOOL_CMDS_LEAF{LEAF_NO}_X2.cmd"
  ```
  - 字符串**不是 f-string**，路径里会留下字面的 `{LEAF_NO}`。`OK_FIXED["tool_cmds_path"] = str(TOOL_CMDS)` 因此等于 `…/ARCH_TOOL_CMDS_LEAF{LEAF_NO}_X2.cmd`，与 Arch 草案的 `…LEAF23_X2.cmd`、`…LEAF24_X2.cmd` 对不上。`TOOL_CMDS.is_file()` 也会是 False，所以两叶都会拒跑。
  - **修法：** 改成 `f"ARCH_TOOL_CMDS_LEAF{LEAF_NO}_X2.cmd"`，两叶都要改。另外，Arch §5-1 要求的 `<out_dir>/tool_run_log.txt` 由运行者负责写，脚本没有生成，这一点在回执里写明。
- **P2-2 ✓** 叶23 敏感性的首阶段（fund）先过 `verify_primary_eval`。叶24 首阶段先过 `verify_leaf23_complete`：叶23 主口径和 4 个敏感性的 eval_meta 都要在，链完整，panel manifest 相同，且来自同一份脚本 sha 和 .ok sha。叶24 的敏感性还要再过叶24 主口径的 eval_meta。
- **P2-3 ✓** 输出全部改用 `xtext` / `xparquet`（`open(..., "x"/"xb")`）。搜索结果显示，除了 docstring 外，已经没有 `write_text`、裸 `to_parquet` 或 `assert`。
- **P2-4 ✓** 见 P1-3。
- **P2-5 ✓（叶24）** `twenty = (c.str[:2].eq("30") & c.str.endswith(".SZ")) | (c.str[:3].isin(["688", "689"]) & c.str.endswith(".SH"))`，302 开头和 689 开头都按 20% 处理。另外补报了再平衡日口径 `held_limitup_share_in_imax_sample_rebal`（P3-3）。
- **P2-6 ✓** `PANEL_YEARS = tuple(range(2018, 2027))`，verify_panel 逐年核对 sha 和 build_version。v1 的 panel_cache 确实有 2018–2026 共九年。重建目录 `panel_cache_v2_resumefix` 目前**还不存在**（D1b 还没执行）。
- **P3 ✓** assert 已改为 raise；carry_col 按 FULLA/HILIQ 分别取；每个阶段开始时 `panel_recheck`；B4 补充说明和行业帽出处都写进了 notes。

## 6. 第 4、5、6 项

- **4 ✓** 叶23：`res[...]` 里有 `b3_pool_carry=b3` 和 `forecast_branch_names_2024_06_08=fc_early`，其中 `fc_early = ((A.src=="forecast") & (A.date<="2024-08-31")).groupby(A.instrument).any().sum()`。叶24：有 `b3_pool_carry=b3`，以及 `limitup_share_in_imax_sample_pool` 和持仓的再平衡日口径。
- **5 ✓** 两份 prereg_sha 清单都已追加 02:23:24 ET 的修订条目。旧脚本行（叶23 的 8bfc8d4b、81c2b4e6、35ab7938 草稿；叶24 的 4be361ee、de87c839、52bdd159 草稿）都标了 superseded。当前行 f011b277、6f57c82d 与实测一致。新增的 mask（c5433e80）、tool_closure 四项、129d67c5、416e237a、8586ffd0、3b288c83 也都与实测一致。
- **6 前瞻：未发现。** 风格项都是 t−1 或更早；acap 是 t 日收盘可得的信息（见 §4(a)，口径不一致但不是前瞻）；510300 的收益在 shift 之后才使用；warm-up 从 2023-06-01 和 (y−1)-05-01 开始，不读窗口之后的数据。
- **6 事后改口径：ISSUE（P2，需主 Agent 裁定）。叶24 去掉了 vol20。**
  - 叶24 预注册（c289e770）§4 第 50 行原文：「回归项 = … mom20 + mom60 + **vol20** + log ADV20 + 叶18 … 叶18v α。**vol20 留在回归里：本叶要的是「波动之外的右尾」**。」
  - 新代码把风格项**整体换成**冻结集，vol20 被删掉了。IMAX 和 vol20 截面高度相关，去掉 vol20 后，叶24 的 α 会重新带上波动暴露，机制从「波动之外的右尾」变成接近低波因子，与叶18/18v 和低波家族的重合风险也会上升。
  - 主 Agent 02:23 裁定的原文是「一律用 Alpha 冻结风格集（**含** β120、动量 t−120→t−20、logADV20 取 t−1）」，没有明说要删掉 vol20。
  - **建议：** 叶24 用「冻结集加 vol20_{t−1}」（取超集），这样既满足裁定，也保留预注册的机制定义。若主 Agent 明确要求删掉，就在回执和 summary 里写成「按裁定改变机制」并告知 Arch。
  - 叶23 同样去掉了 vol20，但预注册没有给 vol20 赋予机制含义，按裁定执行即可，只需披露。
  - 这些都发生在运行前，没有读过任何结果，不属于看了结果再改口径。

## 7. 要求 AI 修改的内容（同一补丁，报新 sha）

1. **P1（阻断，两叶）：** `TOOL_CMDS` 改为 f-string：`f"ARCH_TOOL_CMDS_LEAF{LEAF_NO}_X2.cmd"`。
2. **P2（两叶）：** `ladv1` 不再 `shift(1)`，因为面板的 adv20_yuan 已经是 [t−20, t−1]；注释里引用 mask 脚本第 79–89 行。
3. **P2（叶23）：** acap 按名字滞后一个交易日（t−1）再合并；或者请 Arch 书面认可当日口径。在 notes 里写明暴露是「腿目标权重（稀疏，每天约 25 名非零）」，并冻结这一选择。
4. **P2（叶24，等主 Agent 裁定）：** 默认建议是在冻结集之外保留 vol20_{t−1}。
5. **签 .ok 时（Arch）：** 叶23 的 .ok 加上 `dep_capadv_leg_sha256=3b288c83…4c4d`；`data_mask_sha256` 以 D1b 回执 pins 为准。

修完后由 Alpha 复核（静态审），再交 Arch 签 .ok。正式验收时，§8 在冻结风格集上另行重做，GATE_V3 以 Alpha 工具为准。

live=false；promotion_approved=false。本审没有建 .ok，没有运行任何项目代码或测试，FROZEN_CONFIG 和纸面轨都没有动。
