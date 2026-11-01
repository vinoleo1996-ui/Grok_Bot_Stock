# 技术/拥挤/状态复合分 who_pays · 闸门预审（DRAFT）

- **日期**：2026-10-25 ≈11:55 ET · America/New_York
- **作者**：QuantLab Alpha（闸门预审；**非**叶级 ACCEPT / 非 FROZEN / 非纸面）
- **对象**：主 Agent（排号 P1-(A)）、AI、Arch（知会）
- **输入 DRAFT**：`docs/v2/AI_LEAF_TECH_CROWD_STATE_COMPOSITE_WHO_PAYS_DRAFT_20261025_ZH.md`
- **政策钉**：`docs/v2/ALPHA_GATE_RESEARCH_TECH_COMPOSITE_LLM_DEBATE_20261025_ZH.md`（Leo 纠正：可作残差候选叶+WF/闸门；**禁**页面 TOP 当超额）
- **对照**：`docs/v2/ALPHA_LEAF27_WHO_PAYS_SLOT_FILL_REVIEW_20261025_ZH.md` · `docs/v2/ALPHA_NEXT_ORTHO_LEAF_DEFS_20261025_ZH.md`
- **锁**：`live=false` · `promotion_approved=false` · `forbid_paper_handoff=true` · **不签 .ok** · **不开跑** · 不跑实数据 · 不排号（主裁） · **不挡**叶25 X2 / mem_probe / 叶27 LOWMEM

## 结论先行

| 项 | Alpha 裁定 |
|---|---|
| **预审裁决** | **ACCEPT_DRAFT_WITH_PATCHES** |
| 语义 | DRAFT 可进主排号排队与正式预注册起草；**不是**叶级 RESEARCH_ACCEPT；**不是** FROZEN |
| Leo 口径 | **MATCH**：残差候选叶路径 + 硬拒页面 TOP 当超额 |
| 六条硬钉 | **全 MATCH**（见 §2） |
| 叶25 | **仍优先**等全叶 X2 / mem_probe；本预审不抢窗、不复用 `1c32ab1e` |
| 叶27 | LOWMEM 另窗；本预审不挡 |
| 晋级/纸面/live | **全部 false** |

## 1. 钉核验表（独立 sha256sum）

| 物 | 声称 sha8 | 盘面 sha256 | 结果 |
|---|---|---|---|
| AI who_pays DRAFT (A) | `655d2a3c` | `655d2a3c447b12fcb741938f4f15659a1da91b98c175d460fcb5ca73d1a32a0f` | **MATCH** |
| Alpha 政策文（Leo） | `e671dee6` | `e671dee6660f159669ad6589b346822ec714c8b83d3c41c97a8d48f2f0670c26` | **MATCH** |

## 2. 六条硬钉核对（主催 / P1-(A)）

| # | 硬钉 | DRAFT 落点 | Alpha |
|---|---|---|---|
| 1 | **截面残差 = SW + style** | §3.2：SW L1 demean/dummies → logmv → 滚动β → mom → vol → logADV20；合成后再 SW+style 一次得 base-α | **MATCH** |
| 2 | **HI_LIQ 判决** | §1 / §4：判决宇宙 **HI_LIQ**；FULLA 仅研究披露，不得代 HI_LIQ 过门 | **MATCH** |
| 3 | **walk-forward** | §4：密封/X2 分窗；X2 内≥3 折；禁全样本一次拟合状态表 | **MATCH**（折界待 FROZEN） |
| 4 | **Gate B / GATE_V3** | §4：CMC v1.2 / `leaf_selfcheck_v3.py`；sha 申 `.ok` 时重钉；本 DRAFT 不跑任一闸 | **MATCH**（预审级预留） |
| 5 | **机制 who_pays 写清** | §0 / §1：拥挤兑现+状态切换错配；H1/H2/H3 可检验；主交付日度 α 向量非 Top-N | **MATCH** |
| 6 | **禁页面 TOP 当超额证明** | §0 失效条件 / §1 禁止 / §5 首条；禁 AlphaLens OOS 纸面当本叶证据 | **MATCH** |

## 3. 通过点

1. who_pays 是**可检验价量/状态错配**（拥挤兑现、状态切换、反转袖），非精神/情绪/「页面好看」叙事。
2. 残差对象写清：SW L1 + style（logmv/β/mom/vol/ADV）+ 披露 vs capacity_adv / moneyflow_resid / expand / 叶18·24·27。
3. PIT/前视意识到位：volume PIT 缺则 GAP；广度禁幸存者池；筹码 POC=GAP 禁编造；状态权重禁读收益翻档。
4. 硬拒页面 TOP / 强烈看多榜 / 无残差 Top-N / AlphaLens 纸面 OOS 复刻——与 Leo 政策文一致。
5. 与 moneyflow_resid / 叶18·24·27 近等权换皮有 Jaccard/ρ 闸；拥挤维与 Beta A6「拥挤进 β 预算」分轨（本叶=选股 α）。
6. WF / Gate A·B / GATE_V3 / 成本 30bp 惯例已预留；明确本 DRAFT 不跑闸。
7. 状态=DRAFT、未排号、live=false、不挡叶25/27——边界正确。

## 4. 补丁点（升 FROZEN / 正式预注册前）

| # | 级别 | 补丁 | Owner |
|---|---|---|---|
| P1 | **必须** | §5 正交硬闸表**显式**纳入叶25 / 叶26 / capacity_adv / moneyflow_resid（现文 §3.7 有披露、§5 列表偏薄；FROZEN 须 Jaccard≪0.7∧近等权拒） | AI→Alpha 复核 |
| P2 | **必须** | 正式预注册写死：方向、状态档数与权重表、β/mom/vol 窗、停牌涨跌停剔除；**禁**冻结后读收益翻档/翻号 | AI 起草→Arch 审 |
| P3 | **必须** | 资金维默认 **OFF 或仅敏感性**，直至主裁相对 moneyflow_resid 裁定启用；启用则强制残差+Jaccard | 主 + Arch |
| P4 | **必须** | 筹码 POC：**默认关闭**；无 PIT 不得编造；不得静默进主 α | Data + AI |
| P5 | **必须** | OHLC / volume / 复权价 / 指数（状态臂）**available_at / as-of** 契约重钉；广度若 GAP→状态臂降级为「指数趋势+波动」并**回执披露降级** | Data |
| P6 | **必须** | 动量维 vs style mom 臂：FROZEN 须披露是否双重计分及处理（残差前剔除/降权/仅披露） | AI→Arch |
| P7 | **建议** | 状态指数单一钉（510300 vs 000300）写死；与叶25 共用 `sw_l1_asof_with_gap_carry` 一旦落地禁私造 | Data / Arch |
| P8 | **建议** | FROZEN 正文保留一句 vs Beta A6：本叶选股 α ≠ Mandate 降仓旋钮 | AI |

无上述必须项 → 不得升 FROZEN / 不得申本叶独立 `.ok`。

## 5. 硬拒边界重申

1. **硬拒**：把页面 TOP / 强烈看多 / 演示榜 / AlphaLens OOS 配置表当作超额或闸审通过证据。
2. **硬拒**：主交付退化为无 α 向量的 Top-N 名单；无 SW+style 残差的 ret20/60 合成换皮。
3. **硬拒**：状态权重或方向在读本叶收益/IC 后翻档；冻结后翻号。
4. **硬拒**：筹码峰等未入库字段静默编造；用当日可交易池冒充全历史 HI_LIQ 广度/宇宙。
5. **硬拒**：与 moneyflow_resid / 价量快叶近等权换皮；LLM「模型说多就买」进本叶（本预审只审 (A)，不审 (B)）。
6. **硬拒**：复用叶25 step_m1 `.ok` `1c32ab1e` 或叶27 VOID `725be3e0` 冒充本叶授权。

## 6. 非动作 / 不挡

- **不**签 `.ok`；**不**开跑；**不**跑实数据；**不**改脚本；**不**改 `alpha_labels` / FROZEN_CONFIG；**不**排号（主裁）；**不**升纸面。
- **不挡**叶25 全叶 X2 / mem_probe；**不挡**叶27 LOWMEM@另窗。
- 本预审 **≠** 叶级 ACCEPT；排号后仍须：正式预注册 FROZEN → Arch 审脚本 → **独立**新窗 `.ok` → X2/密封分签 → Alpha 闸审。

## 7. 状态动作

- 落盘本文；`TEAM ### Alpha` 覆盖预审结论 + 叶25/27 等待态。
- `ql_bus` type=`gate` verdict=`ACCEPT_DRAFT_WITH_PATCHES`；refs=本文。
- 只审 (A)；不审 (B) LLM 辩论 who_pays 稿。

live=false；promotion_approved=false；forbid_paper_handoff=true。
