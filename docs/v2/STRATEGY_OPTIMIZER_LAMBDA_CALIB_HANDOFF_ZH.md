# Eng 交接：OPTIMIZER_V1 密封窗 λ 标定（Strategy）

- **时间**：2026-10-14 ≈08:13 ET（**HARD 已按 Leo Core-concentrate 更新**）
- **状态**：BLOCKING for FROZEN；**禁止**用标定结果直接改纸面 / 开 X2 优化器正式臂
- **上游**：`STRATEGY_OPTIMIZER_PREREG_DRAFT_ZH.md` §3.4 / §4；β HARD ±0.10 vs \(w_b\)
- **live / promotion**：false / false
- **产物目录（不变）**：`output/strategy_optimizer/calib/`

> **作废通知**：任何在旧 HARD（单票 2.5%/3.0%、Neff 40–70、行业 ±5%、Size/MidCap ±0.25σ）下已完成或在跑的标定产物 **一律作废**，须按下方 **NEW HARD** + **两步截断** 重标。Eng 已确认按 Core-concentrate 重标。

## 产出（必须落盘）

| 文件 | 内容 |
|---|---|
| `calib_lambda_risk.json` | 密封窗内使典型 \(\lvert w-w_b\rvert\) 下 \(\lambda_{\mathrm{risk}}(w-w_b)^\top\Sigma(w-w_b)\) 与 \(w^\top\alpha_{\mathrm{res}}\) **同量级**；记录方法、分位数、选用单点 |
| `calib_lambda_turn_60w.json` | AUM=60万；**优先**对齐同窗 **capacity_adv** 引擎换手中位数 **±20%**；中心目标≈月双边 50%（年化单边 4–6×）；B4 仅对照；实际换手非硬保 |
| `calib_lambda_turn_100w.json` | 同上 AUM=100万 |
| `calib_meta.json` | 窗=2018-01-02→2024-05-31；掩码 HI_LIQ_V1.1；引擎年化 244；HARD 指纹=Core-concentrate；**未**用 X2 收益挑参；两步截断开关=on |

## NEW HARD（标定必须遵守）

| 项 | 值 |
|---|---|
| \(w_b\) | HI_LIQ 池内 float_mktcap |
| 单票上限 | **100万 5.0% / 60万 6.0%** |
| Neff | **20–30** |
| 行业 vs \(w_b\) | **±8%**；单行业绝对 **≤20%** |
| Size / MidCap | **±0.35σ** + Path A；Slack **≤0.05σ**；行业相对 Slack **≤1pp**；绝对20%/单票/Neff/β **无 Slack** |
| 两步截断 | 全池初解 → 支撑集按 \(|w^{(0)}|\) 前 20–30 且单票 ≥**暂定 2.0%** → 二次重解 → 整手（科创 **200**） |
| β vs \(w_b\) | \(\lvert\beta-1\rvert\le 0.10\)（系统性 INFEASIBLE 可提案 ±0.15，停并回报） |
| TC | **仅** \(\lambda_{\mathrm{turn}}\|w-w_0\|_1\)；禁 3/2、双阈 |
| ν | 未定保持 0 |
| INFEASIBLE | **不松**行业/单票/Neff/β；Size/MidCap 可走 Slack |

## 硬规则

1. **只在密封窗**标定；**禁止**用 X2（2024-06→）收益 / CAGR / MDD 选 λ。
2. 优化内 TC **仅** L1；禁 3/2、双阈。
3. 标定只看：约束可行性、换手、主动暴露、Neff 落带、两步截断后持仓数。
4. 可行域系统性 INFEASIBLE 时**停**并回报 Strategy/Beta（可提案 β→±0.15 或 Size Slack 策略，须 dated）；不得私自松行业/单票/Neff。
5. 标定臂 = **Core**（无域预算、无快门卫、无拥挤度）。

## 最小可接受烟测

- 密封窗任抽 ≥20 个再平衡日：INFEASIBLE 率报告；Core 目标可解为主；Neff 落在 20–30。
- 写出选用 \(\lambda_{\mathrm{risk}},\lambda_{\mathrm{turn}}\) 单点及敏感性表（±50%），**不**据此挑收益。

完成后回 Strategy；由 Strategy 写入 DRAFT 修订记录 + 催 Beta/Arch 重签后再报 Leo 申请 FROZEN。


## 双口径（标定/报告）

密封窗 λ 标定仍按优化器 HARD（股票求解层）。**报告/对标**须准备两套权重出口：①纯股票 100%；②80% 股票 + 20% 510300。主对比 capacity_adv 只用②。主指标补算 Sharpe/MDD/IR（若记分卡缺字段）。

## 再平衡写死（Leo ≈08:20 / Strategy ≈08:22）

- cadence = **`month_end_plus_first_last`**（与 capacity_adv 一致）。**禁止**密封窗试周频。
- \(\lambda_{\mathrm{turn}}\) 标定**优先**用 capacity_adv 同窗同 AUM 换手中位数 ±20%；若 capadv 同窗样本不足，可用「月双边≈50%」中心目标（折合单边≈25%）并在 `calib_meta.json` 注明 `turn_target_src`。
- 成本 / 实际换手 = X2 观测，不做事前硬承诺。
- 标定日历必须与 capacity_adv 再平衡日集合一致（含窗首/末日规则）。

