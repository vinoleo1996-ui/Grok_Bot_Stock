# AI_FACTOR_L1b_STRUCTURAL 预注册（修正）：制度/结构算子搜索空间

状态：**explore amendment — Leo 于 2026-10-11 经 New Bot（Alpha 可见）否决 L1 Top-K（教科书反转/低波，ICIR 0.17），要求立刻改主线并重跑探索。**
研究级，`promotion_approved=false` 全程强制。密封窗 **不跑**。不碰 V3-A1 持有层密封。
父预注册：`docs/prereg/AI_FACTOR_L1.md`（本文件为其 **L1b 修正案**，不擦除 L1 账本 N=280）。

登记：2026-10-11 ~23:45 ET（先于本修正搜索）。SHA256 见文末。

## 0. 否决与动机
L1 v1 探索窗 Top-K 收敛到 `neg(ret_20)` / `neg(rv_20)` 等公开教科书因子，ICIR≈0.17，未过闸门，且不符合「AI 挖非公开结构」主线。L1b **禁止**将此类表达式作为主结果/晋级候选。

## 1. 禁令（主 Top-K / 晋级候选）
下列 **不得** 进入主 Top-K 或 promotion 候选（仅允许显式 **CONTROL** 臂，本跑可不跑对照）：
- 动量 / 反转：`ret_n`、`resid_ret_*`、纯 `neg(ret_*)`、`ts_max(ret_*)` 等价物
- 低波：`rv_*` / `vol_*` / `neg(rv_*)`
- 估值教科书：EP、BP、纯 PE/PB 排序
- 换手教科书：`turnover` / `turn_20` / Amihud 单独作为因子主体
- 其他公开截面教科书的同义改写（rank/zscore/delay 包一层仍算教科书，若叶节点全集落在禁叶）

检测：表达式叶集合 ⊆ `TEXTBOOK_BANNED_LEAVES` → 拒绝计为候选（仍计次 N）；或与公开因子面板 `|corr|>0.5` → 适应度重罚且不得进主 Top-K。

## 2. 新搜索空间 = 制度/结构叶（仅这些进 GP 叶集）
| 族 | 叶（示例） | 钱从谁来（机制要点） | 数据 |
|---|---|---|---|
| 涨跌停状态序列 | `limit_up_flag`, `limit_down_flag`, `lu_streak`, `ld_streak`, `lu_count_5`, `days_since_lu` | 打板/砸板流动性与 T+1 约束下的被迫对手方 | `stk_limit` + close；scratch `limit_up` |
| T+1 隔夜/日内 | `overnight_ret`, `intraday_ret`, `on_minus_id` | 隔夜信息 vs 日间流动性提供；T+1 无法当日平仓者支付 | open/close 复权 |
| 被动/ETF 份额冲击 | `etf_major_flow`, `etf_theme_flow`, 与涨停交互叶 | 被动创设/赎回冲击由承接的股票多头支付 | `etf_share_flow_pit_major` + `industry_theme`（PIT `available_at`） |
| 解禁供给 | `lockup_S_20` | 原始股东解禁减持，二级多头折价承接 | `share_float_2018plus`（ann_date PIT） |
| 期货贴水条件 | `if_basis`, `if_basis_x_on` | 贴水时对冲/期现资金行为改变隔夜风险溢价 | `IFL1.CFX` vs CSI300 |
| 公告文本嵌入交互 | — | — | **缺口**：`anns_d` 无 2024–2026 文件；无 embedding → 本跑不进叶集 |

每个存活候选必须附写「钱从谁来」机制注；无机制注不得晋级。

## 3. 适应度（进函数，非事后）
主目标：探索窗中大盘 long-only top50 **扣成本净超额代理** `ann_net`（单边默认 25bp × 换手），减去：
- 复杂度惩罚 `λ_c * n_nodes`
- 换手惩罚（已含成本路径）
- **公开因子相关惩罚**：对 `{ret_20, rv_20, turn_20, (-ret_20), size}`（及 EP/BP 若加载）任一 `|ρ|>0.5` → `fitness -= 2.0 * (|ρ|-0.5)` 且标记 `novelty_fail`
ICIR 仅作诊断，**不再单独作主适应度**。

## 4. 新颖性闸门（主 Top-K）
同时满足才进主 Top-K：
1. 非禁令叶构造（结构叶占比 100% 或显式结构交互）
2. 对所有公开对照面板 `|corr| ≤ 0.5`
3. `ann_net > 0`（扣 25bp）
4. 有非空「钱从谁来」
5. 过程 ICIR 诊断可报，但 **不** 用 ICIR≥0.3 单独放行教科书

若搜索无法产生任何通过新颖性+适应度的表达式 → 报告 **MECHANISM FAILURE**（原因），**不得**再交反转/低波。

## 5. 宇宙 / 窗口 / PIT / 账本
- 宇宙：流通市值前 1500 或沪深300/中证500；禁小盘主线
- 探索：2024-06-03→latest；密封 2018-01～2024-05 **不用于标签**
- 标签：open→open，`open[t+2]/open[t+1]-1`
- ETF 份额：`available_at` 后才用；入场不早于可得日后次日开盘（与宽基表口径一致：T+1 日终可得 → T+2 开盘）
- 解禁：仅 `ann_date` 已过的记录
- 账本：`output/ai_factor/ledger.jsonl` **续写**（不擦除旧 N=280）；本块预声明 `max_evaluations=320`（L1b 块）
- 内存：峰值 RSS < 2500 MB

## 6. 输出
- `output/alpha/AI_FACTOR_L1b_STRUCTURAL_EXPLORE_ZH.md`
- `output/ai_factor/gp_explore_l1b/`（run_meta / top_k / summary / ledger_run）
- `promotion_approved=false`；不申请密封

## 7. Kill lines
- 主 Top-K 含教科书禁令表达式
- 无计次 / 触碰密封标签 / 小盘主线 / 高杠杆
- 仅靠与公开因子高相关「假装」结构因子

## 8. Hash
（写入文件后由脚本填充）

---

## 9. 对齐 `/workspace/QuantLab-AI_STACK_RETHINK_ZH.md` §6 Alpha（本修正优先）

若与先前 L1b 短简报冲突，**以 §6 + Leo 禁令表为准**。

1. **主线：** L1 价量 GP 降为对照臂；**主结果**必须 `ban_textbook=true` + 结构/文本叶子（涨跌停、T+1 隔夜/日内、ETF 份额冲击、解禁、期货贴水、公告/舆情文本——文本缺口如实标注）。
2. **RD-Agent 式闭环（最小自研）：** Synthesis（假设/表达式）→ Implementation（`apply_expr`/面板）→ Validation（扣成本、容量、禁教科书、公开因子相关）→ Analysis（账本计次 / Bandit 位占位）。本跑 GP+seed = Synthesis/Implementation；适应度+新颖性闸门 = Validation；ledger = Analysis。完整五单元与 `rdagent` 依赖评估另开 Eng 任务。
3. **Prompt/算子注入：** 禁止输出等价于动量/反转/低波/EP/BP/换手的单调变换；V3 制度机制 + 前视陷阱写入候选「钱从谁来」。
4. **适应度：** 扣成本净超额为主；`|corr|>0.5` vs 公开因子惩罚；IC 不作晋级故事。
5. **禁止：** 未批准密封窗；教科书 Top-K 申请晋级；高杠杆；小盘主线。
6. **本周验收口径（§5 D6–D7）：** 是否出现非教科书 Top-K 且扣费有希望；若无 → **MECHANISM / 工厂失败**，改叶子/闭环，不许粉饰。

文件 SHA256（含 §6 修正）：`9f1b7193b3afc944858f2e874a3ae6f31088fdc19ced1dff6f259889ed639a7a`
