# OPTIMIZER_V1 冻结后开跑清单（Strategy · 预写 · 未授权执行）

> **横幅**：本文是 **看结果前** 的操作清单。当前 **FROZEN ≈08:29**；**授权**执行 Core 回测 / book-smoke，直至 Leo 明确过关 + Eng λ 标定落盘（NEW HARD）+ Beta/Arch **Core-concentrate 重签** + 状态改为 FROZEN。

- **时间**：2026-10-14 ≈08:13 ET
- **口径**：Leo Core-concentrate（≈08:09 via 主 Agent）
- **live / promotion**：false / false
- **纸面**：不改 FROZEN_CONFIG / capacity_adv / B4 / S6

## 0. 开跑前门（全绿才动）

| # | 门 | 现状 |
|---|---|---|
| G0 | Leo 书面过关本 DRAFT（Core-concentrate + 频率/换手终签） | **✅ ≈08:20 ET**（月末对齐 capadv；λ_turn 标定目标；开跑授权） |
| G1 | Arch **按 Core-concentrate + ≈08:22 频率/换手终签** | **✅ FINAL_COSIGN_PASS**（`ARCH_OPTIMIZER_CORE_FINAL_COSIGN_ZH.md`） |
| G2 | Beta **按 Core-concentrate + ≈08:22 频率/换手终签** | **✅ PASS_PENDING_ENG_LAMBDA**（FINAL + FREQ_ACK） |
| G3 | Eng `calib_lambda_*.json` + `calib_meta.json`（**NEW HARD**） | **✅ ≈08:28** |
| G4 | DRAFT → 盖 `FROZEN` 戳 + 修订记录写入 λ 单点 | **✅ ≈08:29** |

## 1. 冻结后正式臂（仅列顺序，未跑）

1. **Core only @60万 ∧ 100万**（先跑）：密封窗披露；X2 样本内报告（**漂亮数不得晋级**）；**FWD 2026-11-02** 才是试金石。**双口径**①+②（主结论②）。**三列并表**：A Core(HI_LIQ) / B 现行 capadv(mid_large) / C capadv Top-25@HI_LIQ。再平衡=`month_end_plus_first_last`。
2. **Full**（**稍后**）：同窗同 AUM，与 Core **分开**报告；事件腿 vs **B4**；禁止把 Full 增益回贴 Core 选参。
3. 对照（非主路径）：既有 HI_LIQ B4 Top-N X2、纸面 capacity_adv/B4——**只并表，不替换纸面**。
4. 必报：CAGR/MDD/Calmar/胜率/换手/成本/填单/\(N_{eff}\)（20–30）；申万一 + 电子/计算机/通信/医药；Size/MidCap；vs 510300 纸面 β；两步截断前后持仓；MDD≤25% 硬关注，另报 ≤15%。

## 2. 明确不做

- 不把裸 HI_LIQ / FULLA capacity_adv 单腿挂纸面（X2 已破 MDD25%）。
- 不用 Top-N / 50/25/25 作新主路径。
- 不恢复优化器内 3/2 冲击或外部双阈进 Core。
- 不在 Core 臂开事件门卫。
- 不改 live / strategy_promotion。
- 不在 G 门未齐时开跑。

## 3. 过渡结论（已完成 · 非主路径）

HI_LIQ_V1.1 Eng book-smoke X2：capadv 两档破门；B4 22.44%/−16.51% · 14.90%/−20.19%。密封 N/A。回执 `STRATEGY_HILIQ_CAPADV_X2_ZH.md`。
