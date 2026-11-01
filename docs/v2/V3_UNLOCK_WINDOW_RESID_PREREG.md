# V3_UNLOCK_WINDOW_RESID_PREREG — 解禁窗口残差

研究级，**promotion_approved=false**。写于 **2026-10-12 07:35 ET**；路径于 **2026-10-12 ~19:45 ET** 更新为 PIT 权威表（跑前）。  
批次：`unlock_rerun_pit`（仅本臂；**不磨** LIMITUP-FADE-REV）。主线：**个股+ETF**。残差 **510300**。

## 独特收益来源（谁付钱）
限售股 **解禁（unlock / share_float）** 窗口，大股东/机构存在可预期的抛压或减持预期；股价常在解禁前走弱或解禁日承压。本臂在解禁 `available_at` 之后，持有「解禁前相对 510300 残差为负」的中大盘，吃的是被迫/知情卖盘的流动性折价。付钱的是：解禁窗口的减持方与接飞刀短线。

## 数据审计（跑前）
| 路径 | 覆盖 | 结论 |
|---|---|---|
| `data/v2/share_float/share_float_pit.parquet` | `float_date` **20150105→20261030**；X1 解禁行≈38530 | **权威 PIT**；本臂唯一读源 |
| `data/v2/share_float/share_float_2015_2017.parquet` | 20150105→20171229 | sidecar；勿单独替代 pit |
| `data/v2/share_float/share_float_2018plus.parquet` | 2018-01-02→… | **勿单独用于 X1** |
| 报告 | `docs/v2/SHARE_FLOAT_X1_2015_2017.md` | Data 回执 |

`available_at` = `ann_date` 18:00 Asia/Shanghai；缺 ann → null（不前视）。不可前移。

## 冻结规则
1. 事件：`share_float_pit` 按 `(ts_code, float_date)` 聚合 `float_share`；过滤 CSI300∪CSI500 宇宙（禁小盘）。
2. PIT：用表内 `available_at`（=ann 18:00 SH）→ 下一开盘可知；交易窗以 **float_date** 为锚。
3. **残差规则（冻结一条）**：评估日 = float_date 前第 1 个交易日；过去 20 日个股收益 − 510300 收益 **< 0**（解禁前相对弱势）→ 入选。不搜索替代定义。
4. 入场：评估日收盘后下一开盘（且 ≥ available_at 下一开盘）；持有至 float_date 后第 2 个交易日平仓（冻结）。
5. 等权；N 帽 25；`w_stock=min(0.70,0.028*n)`；余 510300。AUM 60/100万；禁小盘/CB/金/债主仓。

## 闸门
X1 Sharpe≤0 或 avg_names==0 → fail_precheck；仅 explore-pass 且非 near_relative 才交接。`promotion_approved=false`。

## 产出
`output/v3/unlock_window_resid/`。
