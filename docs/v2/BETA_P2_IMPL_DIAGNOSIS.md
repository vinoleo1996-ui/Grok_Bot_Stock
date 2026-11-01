# P2.1 β 袖套 vs max_etf — 实现诊断

> 2026-10-10 · `promotion_approved=false`  
> 来源：`QuantLab-STRATEGY_RESCUE_PLAN_V1.md` §P2.1 / §5  
> 约束：**不抬 `max_etf`**；**不先改 Mandate**（禁止粉饰）

## 1. 今日 `implied_sleeve_beta` 代码路径

```
VolTargetBetaSleeveProvider.plan(session)
  ├─ load_etf_510300 panel closes ≤ session
  ├─ unit_beta = OLS(ETF daily ret, index sh.000300 ret) trailing 60d
  │     └─ 缺重叠则 unit_beta=1.0（flag: unit_beta_assumed_1_index_gap）
  ├─ realized_vol = ann.std(ETF ret, 60d)
  ├─ etf_pre_dd = min(target_vol/rv, target_beta/unit_beta, max_etf=0.40)
  ├─ drawdown scaler (L1–L4) may cut etf further (risk-off only)
  └─ implied_sleeve_beta = etf_sleeve_weight * unit_beta
```

文件：`quantlab/beta/sleeve.py`  
（`scale_etf_sleeve_weight` → `apply_drawdown_scaler_to_etf_weight` → gap 字段）

**测量校验（2026-06-30）**：自研 OLS 与 `numpy` cov/var 差 `<1e-15` → **β OLS 无 bug**。

## 2. 烟测 / 面板数字（`v2_beta_smoke`）

| session | etf_w | unit_β | sleeve β (implied) | gap→0.70 | max_etf×unit | DD tier |
|---|---|---|---|---|---|---|
| 2026-06-30 | 0.40 | ≈0.975 | ≈0.390 | ≈0.310 | ≈0.390 | L1（eff_vol=0.12；权重仍钉在 max_etf） |
| 2026-10-09 | 0.30 | ≈0.977 | ≈0.293 | ≈0.407 | ≈0.391 | L3（0.40→0.30） |

Mandate：`target_beta=0.70`，`max_etf_sleeve_weight=0.40`，band `[0.5, 0.85]`。

## 3. 袖套 β vs 组合「实现 β」

| 概念 | 定义 | 谁拥有 |
|---|---|---|
| **袖套 β** (`implied_sleeve_beta`) | `etf_w × unit_beta` | Beta |
| **组合实现 β** | 袖套 β + Σ residual 权重 × 个股/残差相对基准 β | Strategy（residual book） |
| **结构性天花板** (`max_sleeve_beta_at_max_etf`) | `max_etf × unit_beta ≈ 0.39` | Mandate 约束（本阶段不可改） |

行业中性**多头**残差账本通常仍带市场 β≈1（中性的是行业，不是市场）。  
在 `assumed_residual_unit_beta=1.0` 下：

```
residual_weight_to_hit_target_beta ≈ residual_beta_budget_for_strategy
implied_portfolio_beta_at_residual_fill ≈ 0.70   # 当 fill ≤ residual_book_weight_cap
```

注意：若 Strategy **填满**整个 `residual_book_weight_cap`（≈0.55）且 unit β≈1，  
组合 β ≈ 0.39+0.55 ≈ **0.94**（超调）。应 **按 `residual_weight_to_hit_target_beta` 定残差规模**，而非盲目用满 cap。

## 4. Bug 还是结构？

**结论：结构性（structural），不是测量/裁剪实现 bug。**

证据：
1. OLS 与 numpy 一致。  
2. 裁剪顺序正确：vol/β → `max_etf` → DD 只降不升。  
3. 算术必然：`0.40 × ~1.0 ≈ 0.40 < 0.70`。即使 unit_β 完美=1、无 DD，袖套也不可能单独到 0.70。  
4. 伪造「袖套 β=0.70」唯一捷径是抬 `max_etf` 或改 Mandate target → **§5 禁止**。

指数窗止于 2026-06-30 会造成晚会话 `beta_window_ends_before_session`，但 unit_β 仍≈0.98，**不是** gap 的主因。

## 5. 修复选项排序

| ID | 选项 | 评价 | P2.1 状态 |
|---|---|---|---|
| **A** | 只修测量 bug（OLS/窗/裁剪） | 已核对：无实质 bug；可保留诊断增强 | 已做校验；无「修完袖套就到 0.70」路径 |
| **B** | 在不抬 `max_etf` 前提下用 Mandate 已有杠杆加袖套 | Mandate 无第二 ETF 敞口杠杆；cash 只能更小不能抬 β | **不可行**（无已有杠杆可动） |
| **C** | Strategy 残差路径：按 `residual_weight_to_hit_target_beta` 使 **组合实现 β≈0.70** | 不改 Mandate、不抬 max_etf；与 industry-neutral residual 设计一致 | **推荐（下一步）** |
| **D** | 改 Mandate `target_beta` / `max_etf` | 粉饰实现失败 | **FORBIDDEN（§5）** 本阶段不做 |

## 6. 推荐（不抬 max_etf、不先改 Mandate）

1. **接受袖套天花板 ≈0.39**：`beta_gap_is_structural=true` 为正常旗标，不是故障。  
2. **Beta 交付诊断契约**（已落地字段）：  
   `max_sleeve_beta_at_max_etf`、`beta_gap_is_structural`、  
   `assumed_residual_unit_beta`、`residual_weight_to_hit_target_beta`、  
   `implied_portfolio_beta_at_residual_fill`。  
3. **Strategy 下一步**：在 `residual_book_weight_cap` 内按  
   `residual_weight_to_hit_target_beta` 定残差总权重（默认假设残差 unit β=1），  
   使组合实现 β 贴近 0.70；用持仓×个股 β 回算校验（P2 验收：持仓/β 诊断表）。  
4. DD L3 时袖套再降（0.30）→ gap 变大 → 残差预算同步增大；风险-off 优先于贴目标。

## 7. Smoke

```bash
cd /workspace/QuantLab
PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.v2_beta_smoke
```

相关：`docs/v2/BETA_VOL_TARGET_HANDOFF.md` · 救援计划  
`/workspace/QuantLab-STRATEGY_RESCUE_PLAN_V1.md`
