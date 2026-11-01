# Alpha 预读：叶23 r2.2 / 叶24 r1（为验收做准备）
- 时间：2026-10-18 02:21 ET，QuantLab Alpha。**只读**：只读文件和 sha256sum；没有运行任何项目代码、测试或 py_compile，没有读任何叶产出（盘上也没有）。live=false；promotion_approved=false。
- 依据：Arch 复审附录 `docs/v2/ARCH_LEAF23_24_FIXDIFF_REVIEW_ZH.md`（129d67c5…，结论**不放行，.ok 未签**，P0=0/P1=3/P2=6/P3=6）；前审 b997cba8；diff `AI_LEAF23_24_ARCH_FIX_DIFF.patch`。

## 0. sha 核验（实测）
| 对象 | 期望 | 实测 |
|---|---|---|
| 叶23 脚本 r2.2 `research/g1g5_sue_desens_cs_alpha.py` | 81c2b4e6… | 81c2b4e6a30e8b2f66773c1fcc163cf58f2eca1bbcf3aa84ddaf16b76aee635d ✓ |
| 叶24 脚本 r1 `research/g1g5_imax_intraday_alpha.py` | de87c839… | de87c839ec4e278d798d7789669b5e75dfc8e284399b590d38b9763d99d7ea47 ✓ |
| 叶23 预注册 r2.1 `docs/v2/AI_G1G5_SUE_DESENS_WHO_PAYS_PREREG_R2_1_ZH.md` | 8f5d8ac4… | 8f5d8ac43ba49f11b4461a287addae8c0cf247fbe9d8e81d0b339764e843922e ✓ |
| 叶24 预注册 `docs/v2/AI_G1G5_IMAX_OVERNIGHT_WHO_PAYS_PREREG_ZH.md` | c289e770… | c289e77068be607c108359a87e1d17d6b2e8edac9e4cbcca865a9a49430133a8 ✓ |
| diff | 92ede693… | ✓ |
| 前审 | b997cba8… | ✓ |
- **口径更正**：81c2b4e6 / de87c839 是**脚本** sha，不是预注册 sha（prereg_sha_leaf23/24.txt 里写的是「script r2.2 / r1 current」）。预注册本身是 8f5d8ac4 / c289e770，r2.2/r1 修补时未改、未重冻。

## 1. 叶23 sue_desens_cs（ΔE/P 价格标准化盈余变化）
- **定义**：主口径 ΔE/P = (NI_q − NI_{q−4}) / MV_fix，MV_fix = 盈利记录生效日前一交易日流通市值，在记录有效期内固定；行业内秩→正态分位；判定只用 C1 单分量。敏感性 σ-SUE、日更分母、关预告、blackout 40 只披露。
- **PIT**：正式报表 eff = available_at 之后第一个交易日（首版，first_version）；预告 eff = day1（available_at 的交易日）+ blackout；NI_{q−4} 只用已生效的正式报表；当前记录选择（B4）Arch 核对正确。遗留：正式报表首版回写未验证（snapshot_unverified，P3-7 披露）；forecast 只有 2024+ 文件。
- **残差化**：池内日度 OLS：SW L1 + logmv_{t−1} + mom20 + mom60 + vol20 + logADV20 + 叶19 α + 叶20 α → 分域 rank → 行业+logmv_{t−1} 再残差 → base-α。剔金融与 600519/002371（因子适用性，基准用完整池）。
- **同日 logmv bug**：✓ 已避免。残差化用 `lmv1 = LM.shift(1)`；池 wb 用 `MV.shift(1)·Mp`；分母用 MV_fix（生效日前一日）。
- **类型**：公司财报 + 公司业绩预告（一手披露），**非**研报/调研/金股/卖方一致预期 → 不触发自动拒。注意与 Intel 业绩预告事件的边界：预告信息设禁入窗（股票不剔），须披露持仓与禁入名·日交集。
- **宇宙**：HI_LIQ_V1.1 主，FULLA 披露 ✓。

## 2. 叶24 imax_intraday（剔隔夜分量的彩票 IMAX，低 IMAX 做多）
- **定义**：r_id = (1+ret)/(1+ret_on) − 1；每日池内对 r_id 回归 SW L1 + logmv_{t−1} 取残差 e_id；IMAX_t = [t−19,t] 内最大 5 个 e_id 均值（≥15 有效日）；α = −IMAX 行业内秩→残差化。只做多，无空头腿；家族第 3 次试验，|t|≥2.50；主口径不剔金融。
- **PIT**：纯价格列，t 收盘算、T+1 开盘成交；复牌首日 hiliq=False 不进信号；脚本断言不读 is_resume_day/hiliq_carry。涨停截断只披露（lu_share）。
- **残差化**：SW L1 + logmv_{t−1} + mom20 + mom60 + vol20 + logADV20 + 叶18 α + 叶18v α → 分域 rank → 行业+logmv_{t−1}。
- **同日 logmv bug**：✓ 已避免（e_id、gate、残差化都用 lmv1 = shift(1)）。
- **类型**：价格因子，非研报/调研/金股/卖方 → 不触发自动拒。
- **宇宙**：HI_LIQ_V1.1 主，FULLA 披露 ✓。
- **重合硬规则**：对叶18/18v ρ_excess>0.5 或 top-20 Jaccard 中位数 ≥0.5 → 最多 WATCH；≥0.7 硬拒。

## 3. Arch 发现的修复状况（两叶共用，据 129d67c5）
| 项 | 状态 |
|---|---|
| B1 FIN、B2 manifest、B4 当前记录（叶23）、N1/N2/N3(叶24)/N4(叶23)/N7(叶24)/N8 | ✓ 已修，Arch 核对正确 |
| **B3 池 EW/wb 沿用** | ✗ **P1-1**：把所有「无行日」当停牌沿用，HI_LIQ 沿用 20,088 名·日中 16,987 为 ST 日 → wb 硬地板和判定 t 被扭曲；摘帽日还会误 STOP。根源是 Arch C1 措辞，按 §3 执行口径改，预注册不重冻 |
| N5 .ok 解析 | 部分：**P1-2** 敏感性变体未绑定 sensitivity_specs；P2-1 未知键未拒 |
| N6 阶段链 | 部分：P2-2 顺序、P2-3 排他创建 |
| 进程检查 | **P1-3** 会永久拒跑（常驻抓数命中）；P2-4 祖先链/niceness |
| 叶24 涨停识别 | P2-5 漏 302 开头创业板 |
| verify_panel | P2-6 须核 2018–2026 全部年份 |
| P3-1…P3-6 | 披露/顺手修（assert→raise、carry_col、涨停再平衡日口径、行业帽出处、读前复核 sha、B4 回执说明） |
- 结论：**两叶目前都不可验收**，等 AI 出 r2.3 / r2 新 sha → Arch 复审 → .ok → Data D1b 重建 manifest 回填 → 运行。

## 4. 与 Alpha 冻结风格集 / capacity_adv 的对照（§8 关注点）
| 冻结风格集（t−1） | 叶内残差化 | 差距 |
|---|---|---|
| SW L1 | ✓ | — |
| log 流通市值 | ✓ logmv_{t−1} | — |
| β120 | ✗ 未含 | Alpha §8 A/B 须补残差 |
| mom(t−120→t−20) | ✗ 用 mom20+mom60（含最近 20 日） | 口径不同，§8 须按冻结集重做 |
| logADV20 | ✓ 但取当日 adv20_yuan，未 shift(1) | 与「t−1 暴露」不一致（t 收盘出 α、T+1 成交，非前瞻，但须统一） |
| capacity_adv | 只以 logADV20 作代理，**未把 capacity_adv α 放进回归**（叶23 预注册 §1 写了「对 capacity_adv 回归取残差」） | 文字与代码不一致，待 AI 说明；Alpha CMC 以 alpha_combo_marginal --base capadv 为准 |
- Alpha 验收时 §8 用冻结风格集 + 两套风格并列（AI 风格修正为前一日 logmv），稀疏腿勘误 (i)/(ii) 只适用后续叶（本两叶是稠密截面因子，主读 IC 口径照常）。

## 5. Alpha 验收清单（顺序固定）
1. **HC**：sha 链（脚本/预注册/.ok/manifest/tools）、meta 链完整、out_dir 排他、RSS≤1.5GB、nice≥10、无 is_resume_day/hiliq_carry 入信号。
2. **单叶**：rank IC、naive t / neff t / HAC t（lag 19，仅披露）；判定 t = 两档对 HI_LIQ wb 日度净超额 HAC t ≥2.50（叶23、叶24 同）；wb 硬地板（两档 CAGR > wb）。
3. **CMC**：`alpha_combo_marginal.py --universe hiliq --base capadv`（bee23019），ΔIC ≥ 0.003；输出 vs_poolEW、report_to_leo_eligible。
4. **§8**：A/A′ 残差与特质 IC（冻结风格集，t−1）、B 中性化后净超额（两套风格并列，异号记 PASS*）、C 快慢错配、CMC。
5. **decay v1.1**（alpha_decay_gate a877cec5）。
6. **GATE_V3**：MDD ≤25%，且两档都赢 capacity_adv HI_LIQ 单腿 Book-Smoke：**60万 −0.6% / MDD −29.9%；100万 1.7% / MDD −33.0%**（B4 只作诊断）；**另须披露对 HI_LIQ 等权池超额，赢 capadv 未赢池 EW 不报 Leo**。
7. **X2**：只是入场券，唯一晋级测试 FWD 2026-11-02 起；密封窗只读一次（叶23 只读 S_F）。
- 叶24 另加：对叶18/18v ρ_excess / Jaccard 硬规则先于 GATE_V3 判定。叶23 另加：对叶20 重复判定（重建面板 + 叶20 权重）。

## 6. 给 AI 的开放问题
1. 叶23 预注册 §1 说残差化含 capacity_adv，代码只有 logADV20，是否要加 capacity_adv α？若不加请改文字口径（披露）。
2. 残差化未含 β120、用 mom20/mom60 而非 mom(t−120→t−20)：是否同意 Alpha §8 按冻结风格集另做残差，以 Alpha 结果为准？
3. logADV20 取当日 adv20_yuan 未 shift(1)，是否改为 t−1 以与冻结集一致（或披露）？
4. P1-1 修法后 B3 沿用名·日按原因归类是否全为 suspended？请在 summary b3 中给计数及新旧 EW/wb 年化差。
5. 两叶外部工具（leaf_selfcheck_v3、alpha_combo_marginal）仍读 v1 panel_cache / 原始复权价，与叶内 FE.book_ret 不同引擎：Alpha 以哪个读数做 GATE_V3？建议 GATE_V3 用 Alpha 工具，叶内数只披露，请确认。
6. mom20/mom60/vol20 在重建面板上含复牌补回行收益，请披露与 v1 面板差异的规模。
7. 叶24 涨停识别 302 段修复后，lu_share（全池/持仓、再平衡日口径）请一并报。
8. 叶23 forecast 只有 2024+ 文件，2024-06→08 预告分支生效记录数（P3-6）请给出。
9. r2.3 / r2 新 sha 出来后，请同步更新 prereg_sha_leaf23/24.txt 并标 superseded，Alpha 届时复核。

live=false；promotion_approved=false。本预读未运行任何代码。
