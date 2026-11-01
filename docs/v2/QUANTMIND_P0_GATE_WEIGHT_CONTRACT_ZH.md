# QuantMind P0：闸门字段 + 日更权重消费约定

**日期**：2026-10-12 · America/New_York  
**版本**：`factor_evolve_v2_qm_p0_20261012` / `weight_long_v1_qm_p0_20261012`  
**门锁**：`promotion_approved=false`；Alpha **不启 GP**；不下单；不开密封  
**对照**：`docs/v2/QUANTMIND_DEEP_READ_ZH.md` §7 P0；`docs/_context/QUANTLAB_FACTORY_CONTEXT_FOR_QUANTMIND.md`

---

## 1. 分工

| 角色 | 做什么 | 不做什么 |
|---|---|---|
| QuantLab AI | 搜索/演化；产出完整日更 `date,instrument,target_weight` + 候选闸门字段 | 不改硬闸规格；不把 10 日 stub 当生产 |
| QuantLab Alpha | 硬闸核可；列 alias → Book-Smoke / 辩论消费；短清单裁决 | 不启 `gp_reopen` / dense_micro；不 vendor QuantMind |
| Data | PIT 面板 / 宇宙 / 资金流等（另单） | — |

**一句话**：AI 出权重与候选字段，Alpha 核可后才可接；gate pass ≠ 密封 ≠ 晋级。

---

## 2. 闸门字段表（`FactorCandidate` → `gate_candidate`）

实现：`quantlab/agents/factor_evolve/{schemas,hard_gates}.py`  
`HARD_GATE_VERSION = factor_evolve_v2_qm_p0_20261012`

| 字段 / 规则 | 类型 | 失败码 / 标签 | 说明 |
|---|---|---|---|
| `who_pays_zh` | str，非空 | `missing_who_pays_zh` | **强制**；缺则 fail |
| `mechanism_tag` | str，非空 | `missing_mechanism_tag` | **强制**；辩论/评级证据入口 |
| `universe_kind` | enum | `universe_banned_or_missing` | 仅 mid_large_stock / etf_* |
| `capital_cny` | 运行参 | `capital_not_in_60_100万` | 仅 60万 ∨ 100万 |
| 教材 / 小盘主仓 | blob 扫描 | `textbook_*` / `smallcap_main_banned` | 既有 |
| **`icir_eps_gate`** | float，有限 | `missing_icir_eps_gate` / `icir_eps_gate_nonpositive` | 闸内残差 ICIR；**必须 >0** |
| **`icir_eps_posthoc`** | float，可选 | `DEMOTE_RESID_sign_flip` | 与 gate **异号** → fail；同号但 \|posthoc\|>1.0 且 gate<0.15 → 仍可 pass，打标 `EDGE_WARN_ICIR_DUAL_GAP`（**勿只信事后**） |
| **`impact_flat25_pct_60万`** | float | `missing_impact_flat25_pct_60万` | 与 100万 **同时** 要求 |
| **`impact_flat25_pct_100万`** | float | `missing_…100万` / `impact_flat25_below_10pct` | 两档均 **≥10.0** |
| overnight 精神 | expr/mech/dir | `HARD_BAN_OVERNIGHT_SPIRIT` | 命中 `overnight` / `ind_rel_overnight` / 隔夜* → fail |
| `score_rows` | list | `no_score_rows` | 无截面分不发权重 |
| `PROMOTION_APPROVED` | const | — | **恒 False**；pass ≠ sealed |

`--smoke`：合成候选 **必须自带** 合法双读+冲击数字；**无 smoke_exempt 旁路**——闸门路径与生产相同，仅窗口短。

---

## 3. 权重长表消费约定

### 3.1 列名

| 侧 | 列 |
|---|---|
| **AI 日更（入口）** | `date`, `instrument`, `target_weight` |
| **内部权威（出口 / Book-Smoke / 辩论）** | `session`, `instrument_id`, `weight` |
| 可选 | `mechanism_tag`（从过闸候选带入） |

**Alias（ingest）**：`date|trade_date → session`；`instrument|ts_code|code → instrument_id`；`target_weight → weight`。  
实现：`normalize_weight_frame` / `scores_to_long_table`（`weights_from_scores.py`）。  
`column_contract_version = weight_long_v1_qm_p0_20261012`。

### 3.2 完整日更 ≠ 10 日 stub

- 生产：AI 必须交 **完整交易日序列** 的日更长表（覆盖约定回测窗，非演示切片）。  
- `--smoke`：允许短窗（如 10 个 bday）演示闸门；`smoke=true` 时 **不** 记 `stub_window` WARN。  
- 非 smoke 且 `n_distinct_sessions ≤ 10`：meta 写 `stub_window=true` + `stub_window_warn`，**不当成功 KPI**，辩论/Book-Smoke 可拒作生产输入。

### 3.3 与辩论 / 评级映射

1. 权重行经 alias 规范化后，Runner 按 `session ≤ asof` 查 `instrument_id` → `weight`（既有 weight-context 路径）。  
2. **`mechanism_tag` 必进 evidence**：thesis/refs 带 `mechanism:<tag>`；**缺 tag 的权重包拒消费**（与闸门 `missing_mechanism_tag` 一致——过闸候选本就有 tag；外部裸权表格若无 tag，Alpha 侧拒接）。  
3. 权重 **只作研究上下文**，不当成交价、不写 Strategy、不改 sealed parquet。

---

## 4. 给 AI 的三句消费约定

1. **列名**：请交完整日更 `date,instrument,target_weight`；Alpha 映射为权威列 `session,instrument_id,weight`（`column_contract_version=weight_long_v1_qm_p0_20261012`）。  
2. **机制 tag**：每条候选/权重包必须带非空 `mechanism_tag`（及 `who_pays_zh`、双读 ICIR、冲击两档）；缺 tag → 拒消费进辩论。  
3. **禁 stub**：禁止用 ≤10 日演示窗冒充生产日更；非 smoke 短窗只打 WARN，不算 KPI 成功。

---

## 5. 明确不做

- git clone / vendor / 整仓粘贴 `opensource/QuantMind`（AGPL）  
- Alpha 启 GP / `gp_reopen` / `dense_micro`  
- `promotion_approved=true` / 下单 / 开密封  
- 把事后 ICIR 单独当晋级依据（双读 + EDGE_WARN）  
