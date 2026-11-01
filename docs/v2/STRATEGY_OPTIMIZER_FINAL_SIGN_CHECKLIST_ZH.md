# OPTIMIZER Core 终签开跑检查单（Strategy · 2026-10-14 ≈08:22 ET）

live=false · strategy_promotion=false · 纸面 FROZEN_CONFIG 不动

## Leo 终签条款（已写入 PREREG）


1. 调仓写死 = `month_end_plus_first_last`（与 capacity_adv 完全一致；禁密封窗双试周/月末）
2. \(\lambda_{\mathrm{turn}}\) 密封标定中心 = 月双边≈50% 或年化单边 4–6×；优先对齐 capacity_adv；实际换手/成本 = X2 观测非硬保
3. 双口径对标：①纯股票 100% + ②80% 股票 + 20% 510300（主结论用②）

## 开跑门

| 门 | 状态 |
|---|---|
| G0 Leo 过关 | ✅ ≈08:20 |
| G1 Arch 终签本补丁 | **✅ FINAL_COSIGN_PASS ≈08:23** |
| G2 Beta 终签本补丁 | **✅ PASS_PENDING_ENG_LAMBDA ≈08:25**（FINAL + FREQ_ACK） |
| G3 Eng λ 落盘（≥20 有效调仓日 + turn 优先 capadv） | **✅ ≈08:28** risk=117.213 turn=0.6/0.6 prepared=24 |
| G4 DRAFT→FROZEN | 待 G1∧G2∧G3 |

## 齐后立刻执行

1. PREREG 盖 FROZEN；写入 λ 单点
2. Core only @60万∧100万 × 密封披露 + X2；双口径全套
3. 主指标 Sharpe/MDD/IR；报 CAGR/Calmar/胜率/换手/成本/填单/Neff
4. 回执 + 报 Leo / 主 Agent；**不**改纸面

文档：`STRATEGY_OPTIMIZER_PREREG_DRAFT_ZH.md` · `STRATEGY_OPTIMIZER_LAMBDA_CALIB_HANDOFF_ZH.md` · `STRATEGY_OPTIMIZER_POST_FREEZE_RUNBOOK_ZH.md`

## 主 Agent ≈08:24 包装纪律（已写入 PREREG §5.1.1）

- 三列：A Core(HI_LIQ) / B 现行 capadv(mid_large) / C capadv Top-25@HI_LIQ 同池
- X2 漂亮数不得晋级；FWD 2026-11-02 试金石；B4/S6 事后挑选纪律不变
- 冻结卡预写：`STRATEGY_OPTIMIZER_FREEZE_CARD_DRAFT_ZH.md`（禁开跑至 FROZEN）
