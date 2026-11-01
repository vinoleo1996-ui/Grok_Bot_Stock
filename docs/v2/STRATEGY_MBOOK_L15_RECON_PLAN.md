# 两引擎对账计划 — 多袖套 L≤1.5 BOOK（研究级，未启动）

日期：2026-10-11 · promotion_approved=false

## 为什么对账
X2 探索窗 BOOK（marp 40% + cb 30% + xd 30%）相对 C0/STATIC 收益更高、回撤更小（见 output/strategy_mbook_L15/COMPARE_ZH.md）。在晋升前需两引擎交叉验证。

## 范围（轻量）
| 臂 | 引擎 A | 引擎 B | 窗口 |
|---|---|---|---|
| SA_xd | Strategy `run_book` + FuturesLeg | Eng `EXECUTION_FUTURES_CASH` / hand-check 路径（同 X-D 已对过） | X1, X2 |
| SA_marp | Strategy sleeve_marp → run_weight_schedule | Eng 同 ExecConfig.strategy_v1 | X1, X2 |
| SA_cb | Strategy sleeve_cb | Eng 同口径（注意 CB X2 与 Beta 仍有 ~0.8pp 差） | **仅 X2**（X1/密封禁止 CB 新跑） |
| BOOK | Strategy combine | 用 A 臂的 target_weights 喂 Eng ledger / run_weight_schedule + FuturesLeg | X1, X2 |

不做：全池股票重任务、FUT-RP、密封窗、ind_mom（非候选）。

## 步骤（预计 <10 分钟，ETF/期货轻量）
1. 从 `output/strategy_mbook_L15/{X1,X2}/{BOOK,SA_*}/target_weights.parquet` + `nav.csv` 取出目标权重。
2. 对 SA_xd：复用已完成的 X-D 两引擎对账口径（真实 IC 行情、roll 5d、现金计息）；确认 Eng 期货边界 bug 已修版本。
3. 对 SA_marp / BOOK spot 腿：同一 ExecConfig.strategy_v1(impact_k=1.0, min_trade_value=2000, corporate_actions=True, no_limit_codes={'sh.510300'})。
4. 比对：日净值差、CAGR/MDD/Sharpe、成本拆分、futures margin/fees/rolls。通过标准：日净值 max|Δ| < ¥5（500万本金）或相对 NAV < 1bp；CAGR 差 < 1bp。
5. CB 单独核对：与 Beta `sleeve_compare.csv` 的 X2 16.92% vs 17.69% 做 fills 级 diff（若仍存在）。

## 前置
- Eng 期货边界修复已确认（X-D X2 = 20.47%）。
- 不启 MarginConfig；max_gross=1.5。
- Leo 未批准前不对账结果写入 promotion_ledger。

## CLI 草稿（未执行）
```
# after Eng confirms recon harness path:
python3 -m quantlab.portfolio.v2_multisleeve_book --arms BOOK,SA_marp,SA_xd,SA_cb --windows X2 \
  --out output/strategy_mbook_L15   # already produced targets
# then Eng-side: feed target_weights.parquet into run_weight_schedule / FuturesLeg twin
```
