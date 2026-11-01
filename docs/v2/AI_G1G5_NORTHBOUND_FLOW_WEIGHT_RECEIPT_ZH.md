# AI G1G5 北向持股变化流 权重回执（X2）

- **时间：** 2026-10-13 ~11:12 ET（America/New_York；箱内 CST 同拍）
- **Leo 指令：** 「A、B同时展开调研」→ 叶 B（本线）
- **promotion_approved：** false；不下单；不交 Strategy；禁 stub 前推；不开 GP
- **who_pays 预注册：** `docs/v2/AI_G1G5_NORTHBOUND_FLOW_WHO_PAYS_PREREG_ZH.md`

## 1) 权重产物

| 项 | 值 |
|---|---|
| **路径** | `output/ai_factory/g1g5_northbound_flow_daily_weights_20261013_111252.parquet` |
| 行数 / sessions / 标的 | **34068 / 668 / 51**（个股活跃 + 510300 压舱名位） |
| 日期跨度 | 2024-01-02 → **2026-10-09** |
| reaches_x2_end | **true** |
| stub_window / stub_forward_fill | false / false |
| 名义结构 | 个股预算均值 **≈0.767** / 510300 压舱均值 **≈0.233** |
| mechanism_tag | `g1g5_ashare_northbound_flow_v1` |
| universe_id | expand mid_large（轻量 top50 评分池 / 活跃 top20） |
| 列契约 | `weight_long_v1_20261012` + 别名 |
| meta sidecar | `output/ai_factory/g1g5_northbound_flow_daily_weights_20261013_111252.parquet.meta.json` |
| run meta | `output/ai_factory/g1g5_northbound_flow_run_meta_20261013_111252.json` |
| ledger / G6 proof | `debate_ledger_g1g5_northbound_flow_20261013_111252.jsonl` (+`_g6_proof`) |
| G6 | **pass** |
| peak_rss | **2017.3 MB**（目标尽量 ≤1.5GB；略超，已记；主因 margin 分块加载） |
| 日均单向换手 | **≈0.0236**（月频；34 个非零再平衡日） |
| 行业硬顶 | 申万一级 ≤**30%** |
| 信号分窗 | hk_hold 再平衡 **17** 日；margin_fallback **18** 日（hk_hold 断档/陈旧>45日） |

脚本：`research/g1g5_northbound_flow_weights.py`

## 2) 机制（相对九败正交）

| 约束 / 臂 | 定义 |
|---|---|
| **主信号** | 北向 `hk_hold` PIT `Δratio`（增持侧）；密窗≈20 日，稀疏窗取最近两观测点 |
| **断档补窗** | 最近 hk asof 距 session >45 日 → 两融 `Δrzye/lag`（融资余额上升侧）；arm 标 `source=margin_fallback` |
| **PIT** | `available_at.normalize()≤session` |
| **持仓** | 增持侧 top20 等权；行业硬顶 ≤30%；压舱 510300 |
| **再平衡** | 月末 + 首日 |

### who_pays（一句）

北向配置流：沪深港通北向对个股的边际增持与持股占比上升由境外配置与被动跟踪资金支付相对510300的持有窗；本叶吃持股变化与流入的对手盘；hk_hold断档后再平衡日以两融融资余额变化作同族补窗；明确非相对强弱截面排序、非估值残差、非OCF、非调仓事件、非份额流乘残差、非ETF-core直接持有。

## 3) 相对已败九包 Jaccard（样例月活跃个股集）

| 对照包 | Jaccard 均值 | Jaccard 最大 |
|---|---:|---:|
| expand | 0.285 | 0.379 |
| nontextbook / friction_monthly | 0.245 | 0.290 |
| lowturn | 0.192 | 0.296 |
| resid_etf | 0.256 | 0.379 |
| etf_core | 0.120 | 0.217 |
| friction_cost_redesign | 0.274 | 0.538 |
| idx_rebal_flow | **0.000** | 0.000 |
| indcap_momneut_ocf | 0.255 | 0.310 |
| d1_val_resid | 0.250 | 0.333 |

全部 **≪0.7** → 非换皮。

## 4) 明确不做 / 边界

- 不开 GP；不交 Strategy；不下单；不密封
- 禁 OCF 主轴；禁估值残差主轴；禁九败同构
- Book-Smoke 由 New Bot / Beta 派 @60万∧100万 vs 510300
- `promotion_approved=false`；若 any_pass=false → 入 WATCH，不交 Strategy

## 5) 请 New Bot / Beta

主测本包：

`output/ai_factory/g1g5_northbound_flow_daily_weights_20261013_111252.parquet`
