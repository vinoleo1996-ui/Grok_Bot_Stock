# 下一张年化账的成本口径（2026-11-01）

岗位：测试。只读 `ExecConfig.strategy_v1`、扣费行、消融构造和现有样例。不改断言，不改实现，不跑账户，不重跑密封窗。`strategy_promotion_approved` 保持 false。下面是字段值，纸面年化未写成已实现盈利。

## 1. `strategy_v1` 构造出来的六个字段

`quantlab/platform/execution.py` 第 343–351 行：

```python
def strategy_v1(cls, impact_k: float = 1.0, **overrides) -> "ExecConfig":
    kw = dict(fill="next_open", price_tick="auto", impact_k=float(impact_k), participation_cap=0.10,
              unfilled="carry", lots=True, enforce_limits=True, order_rounding="target",
              corporate_actions=True)
    kw.update(overrides)
    return cls(**kw)
```

这张字典写入 `impact_k`。`slippage`、`commission`、`min_commission`、`stamp_before`、`stamp_after` 不在字典里，无 `overrides` 时用类默认。类默认在第 308–313 行。`impact_k` 的类默认是 0.0，被第 343 行参数默认 1.0 和第 347 行覆盖。

| 字段 | 构造结果 | 行号 |
| --- | ---: | --- |
| slippage | 0.0 | 312；347–349 未写入 |
| commission | 0.00025 | 308 |
| min_commission | 5.0 | 309 |
| stamp_before | 0.001 | 310 |
| stamp_after | 0.0005 | 311 |
| impact_k | 1.0 | 343、347 |

`research/rd_ablation_20261101.py` 第 151 行是 `config=ExecConfig.strategy_v1()`，没有 overrides，所以上表就是这本消融账的执行配置。同文件第 476–477 行的 `commission`、`min_commission` 写在配权 DataFrame 上，那个对象不是 `ExecConfig`。

扣费在 `run_weight_schedule` 的 `execute`：

- 第 764 行：`px = round_to_tick(px0 * (1 + side * cfg.slippage), TICK[j])`。滑点是价格的分数，买为正、卖为负，然后再按 tick 取整。
- 第 778 行：佣金 `comm = max(MINC[j], notional * COMM[j])`。股票用第 697 行的 `cfg.commission`。
- 第 779 行：印花税 `stamp = notional * _stamp(day, cfg)`，只在卖出且 `stamp_exempt` 为假时。`_stamp` 在第 619–620 行：`day < STAMP_CUT` 用 `stamp_before`，否则用 `stamp_after`。`STAMP_CUT` 在第 28 行，是 `2023-08-28`。
- 第 781–784 行：`KJ[j]`（即 `impact_k`）非 0 时，`imp = sqrt_impact_cost(qty * px0, ADV, SIG, KJ[j])`。公式在第 290–302 行，用的是滑点前的 `px0`。
- 第 796 行：`cash -= side * notional + comm + stamp + imp`。佣金、印花税、冲击从现金另扣。滑点已经在 `px` 里，从而在 `notional = qty * px` 里。
- 第 798–799 行：`cost["commission"]`、`cost["stamp"]`、`cost["impact"]` 累加；`cost["slippage"] += abs(px - px0) * qty`。这一行是记账。滑点为 0 时，参考价不在 tick 上仍会留下取整差额。那是第 764 行的取整，配置里的 `slippage` 仍是 0.0。

## 2. 草案第 70 行的「滑点 5bp」

`docs/v2/MANDATE_UNIFIED_STOCK_ETF_20261012_ZH.md` 第 70 行原文：

> 成本：佣金 2.5bp+最低 5 元；滑点 5bp；印花税历史卖出；`ExecConfig.strategy_v1`

`strategy_v1` 的构造字典没有 `slippage=0.0005`。构造结果的 `slippage` 是 0.0。5bp 没有写进 `strategy_v1`。

这一行是两句话并列。前半写滑点 5bp，后半点名 `ExecConfig.strategy_v1`。测试岗不把其中一句改写成另一句。

佣金 2.5bp 与最低 5 元，对应类默认 `commission=0.00025`、`min_commission=5.0`。印花税历史卖出，对应 `stamp_before=0.001`、`stamp_after=0.0005` 和第 28 行的分界日。`stamp_after=0.0005` 的字段名是印花税。`impact_k=1.0` 在 `strategy_v1` 里。第 70 行没有写 `impact_k`。

## 3. 现有测试没有把「5bp 是 strategy_v1 默认滑点」锁成红灯

`docs/rd/tasks/test_spec.md` 全文四条：申万 `available_at` 不早于决策日则不得返回该行业；面板与 510300 文件缺失时抛 `FileNotFoundError`；读取结果的 `promotion_approved` 为 false；复权 `bfill` 标记为预期失败。四条都不涉及滑点。

`tests/test_rd_contracts.py` 全文没有成本、`slippage`、`ExecConfig` 或 `strategy_v1` 的断言。没有。

最近的预设样例是 `tests/test_execution_costs_platform.py` 第 182–188 行。它比较的是 `fill`、`price_tick`、`impact_k`、`participation_cap`、`unfilled`、`lots`、`enforce_limits`、`order_rounding`。它不读 `slippage`，也不读佣金和印花税。同文件第 164 行要求 `slippage_10bp` 的 `cost_cny > 0`。该项来自 `execution.py` 第 1134 行 `dict(slippage=0.001)`，是 `cost_ladder` 的单项，数值是 10bp，调用的也不是 `strategy_v1()`。

因此，有人把 5bp 说成 `strategy_v1` 的默认滑点时，这些断言保持绿色。

缺的断言：`ExecConfig.strategy_v1().slippage == 0.0`，并且这个值不是 `0.0005`。这轮不加这条测试。

## 4. 和 12%–18% 门比较之前，实验设计要先写明的字段组合

测试岗要求先把选用的字段组合写进实验设计，然后才能把扣费后年化拿去和 12%–18% 门比较。下面两组都已经在代码里。测试岗不选定，不批准。`strategy_promotion_approved` 保持 false。

**组合 A。** `ExecConfig.strategy_v1()` 无 overrides。消融第 151 行已经这样调用。

- `slippage=0.0`
- `commission=0.00025`
- `min_commission=5.0`
- `stamp_before=0.001`
- `stamp_after=0.0005`
- `impact_k=1.0`

扣费行：第 764、778、779、784、796、799 行。

**组合 B。** Mandate 成本对象，字段名不是 `ExecConfig` 的那一组。

- `docs/v2/QuantLab-MANDATE_V2.json` 第 235–240 行：`commission_bps_one_way=2.5`，`commission_min_cny_per_order=5.0`，`stamp_tax_sell_only=true`，`slippage_bps_one_way=5.0`
- 同文件第 328–330 行 `defaults_table` 另有 `commission_bps=2.5`、`commission_min_cny=5`、`slippage_bps=5`
- `quantlab/mandate_v2.py` 第 345–349 行把 `costs` 读进 `MandateCostsV2`，`slippage_bps_one_way` 缺键时默认 5.0
- 扣费在 `quantlab/portfolio/v2_execution_costs.py` 第 330–331 行：`slip_bps = costs.slippage_bps_one_way / 10_000.0`，再乘买卖名义金额

组合 B 没有 `impact_k`。组合 A 的 `slippage` 没有写成 0.0005。两组都还不是下一张账已经采用的口径。
