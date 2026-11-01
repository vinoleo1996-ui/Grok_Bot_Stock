# OPTIMIZER Core 冻结卡（**FROZEN** · 2026-10-14 ≈08:29 ET）

- **时间**：2026-10-14 ≈08:25 ET（**已授权**只跑 Core；禁 Full；纸面不动）
- **live / promotion**：false / false
- **纸面**：FROZEN_CONFIG / capacity_adv / B4 / S6 **不动**

## 共签清单

| 项 | 状态 |
|---|---|
| Leo G0（浓缩+双口径+月末+开跑指令） | ✅ ≈08:20 |
| Arch FINAL_COSIGN_PASS | ✅ ≈08:23 `ARCH_OPTIMIZER_CORE_FINAL_COSIGN_ZH.md` |
| Beta FREQ_ACK（三项 ACCEPT） | ✅ ≈08:24 `BETA_OPTIMIZER_CORE_FREQ_ACK_ZH.md` |
| Beta 终签 PASS_PENDING_ENG_LAMBDA | ✅ ≈08:25 `BETA_OPTIMIZER_CORE_FINAL_COSIGN_ZH.md`（Stage1 授权待 FROZEN） |
| Eng 合格 λ（≥20 有效调仓日；turn 优先 capacity_adv） | **✅ ≈08:28** `ENG_OPTIMIZER_LAMBDA_CALIB_RECEIPT_ZH.md` |

## 冻结规格摘要

- cadence = `month_end_plus_first_last`（对齐 capacity_adv；禁双试）
- HARD：Neff 20–30；单票 5%/6%；两步+整手；行业 ±8%/绝对≤20%；Size/MidCap ±0.35σ+Slack；L1-only；池内 \(w_b\)；β±0.10
- λ_turn 中心：月双边≈50% / 年化单边 4–6×；优先 capadv ±20%；成本=X2 观测非硬保
- 双口径①纯股100% + ②80/20+510300（主结论②）
- **三列包装**：A Core(HI_LIQ) / B 现行 capadv(mid_large) / C capadv Top-25@HI_LIQ 同池
- **X2 漂亮数不得晋级**；**FWD 2026-11-02** 才是试金石；B4/S6 事后挑选纪律不变

## λ 单点（Eng 落盘后填）

| 参数 | 60万 | 100万 | 来源文件 |
|---|---|---|---|
| \(\lambda_{risk}\) | **117.213** | **117.213** | `calib_lambda_risk.json` |
| \(\lambda_{turn}\) | **0.6**（ach≈0.284） | **0.6**（ach≈0.288） | `calib_lambda_turn_{60,100}w.json` |
| turn_target_src | monthly_two_way_50pct_fallback | same | `calib_meta.json` |

## 升 FROZEN 后立刻执行

1. PREREG 状态 → **FROZEN**；本卡改名/盖戳
2. 只跑 **Core** @60万∧100万 × 密封披露 + X2；双口径 + 三列并表
3. 主指标 Sharpe/MDD/IR；报 CAGR/Calmar/胜率/换手/成本/填单/Neff
4. **禁止**因 X2 漂亮改纸面或晋级；回执 + 报 Leo/主 Agent

> **FROZEN ✅**：Eng λ 齐；授权立刻开跑 Core（双口径+三列）。X2 漂亮数不得晋级。
