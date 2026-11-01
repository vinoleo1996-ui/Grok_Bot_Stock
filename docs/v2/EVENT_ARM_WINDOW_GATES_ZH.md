# 事件臂窗口闸（双轨）

**日期**：2026-10-12 · ET  
**状态**：架构规则 · `strategy_promotion_approved=false`  
**动机**：复盘 S2 —— 用「完整 X1 2015–17=0」一票否决 2018+ 有密度机制，与密封窗错配。  
**机器可读配置**：`quantlab/beta/configs/event_arm_window_gates.json`  
**Python 辅助**：`quantlab.beta.event_arm_window_gates`

---

## 1. 双轨定义

| 轨 | 窗口 | 用途 | 失败时标签 |
|---|---|---|---|
| **`coverage_native`** | 该表/叶 **实际 PIT `available_at` 最早日** → 样本末日（或今） | **机制检验**：信号有无相对对照的可交易增量 | 稀疏 → `coverage_too_sparse`；勿伪造 |
| **`book_window`** | 与 Mandate 对齐：**探索默认 2024-06→今**；书级对照可用 **2018-01→今（跳过密封段或仅描述）** | **书级 / AUM 应力**：60万∧100万 · 成本开 | 缺覆盖 → 截断到有数段并标 `coverage_shifted` |
| **`x1_full`（可选对照）** | 2015-06-01 → 2017-12-29 | 历史完整 X1 对照；**默认不作为杀死条件** | `x1_full_events=0` → 仅记录，**不**单独 `reject` |

### 硬规则

1. **禁止**仅因「完整 X1 2015–17 事件行数=0」将提案标死 / `fail_precheck` / 拒写臂。  
2. 缺 X1 但 `coverage_native` 有密度 → 标 **`coverage_shifted`**，可跑 native + book_window 冒烟；**不伪造** `available_at`、不前移 PIT。  
3. `coverage_shifted` **≠** 过密封线；`strategy_promotion_approved` 仍 false；不开自动 X2 晋级。  
4. 自拒仍有效：无相对粗信号增量 / avg_names=0 / 空仓靠压舱主导 → `self_reject`。  
5. 冒烟搜索总闸仍服从 Leo：当前 **停 GP / 停新 STOCK 臂乱搜**；本文件只改闸门语义，不授权重开搜索。

---

## 2. 建议判定流（Beta pretest）

```
events_in_x1_full = count(available_at ∈ [2015-06, 2017-12])
events_native     = count(available_at ≥ table_pit_start)

if events_native == 0:
    → coverage_blocked (真无数据；停该维)
elif events_in_x1_full == 0 and events_native > 0:
    → coverage_shifted; 跑 coverage_native + book_window；x1_full 仅 optional_control
else:
    → coverage_ok; 可跑三窗；主判定以 book_window / native 为准
```

Pretest 默认：`gate_mode=dual_track`（见 JSON）。  
若需旧行为：显式 `gate_mode=x1_full_hard`（仅诊断回放，禁止作主线否决）。

---

## 3. 与 Mandate / Book-Smoke 的关系

- 单臂 Sharpe 只作 **叶子诊断**。  
- 主线进度只看：**可消费权重长表** + **Book-Smoke**（`quantlab.portfolio.book_smoke`）。  
- 详见 `MANDATE_UNIFIED_STOCK_ETF_20261012_ZH.md`。

---

路径：`docs/v2/EVENT_ARM_WINDOW_GATES_ZH.md`
