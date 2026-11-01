# moneyflow 80/20 叠仓 P0 诊断 — 门B / GATE_V3 研究披露

- **日期**：2026-10-25 ≈05:53 ET · America/New_York
- **作者**：QuantLab Alpha（研究披露，非纸面/晋级）
- **来源**：`output/strategy_hiliq/moneyflow_stack_8020_reuse_blended_20261025/summary.json`
- **summary sha256**：`5718de4cea59ff8e76af76eb2733051a0e9c425b48c645f2ad08b0c917cafd5e`（sha8 `5718de4c`）
- **blended 权重 sha256**：`3f8a2b33a995f381ee9e7060858a2029c1a8854a31a32b48ab4842281f188103`（reuse hardlink；P0 钉死，不重算混合）
- **锁**：`live=false` · `promotion_approved=false` · `forbid_paper_handoff=true` · `research_only=true` · 禁 GP · 不改 FROZEN_CONFIG / 纸面轨
- **预注册**：`ALPHA_GATE_AB_PREREG_20261014_ZH.md`（门B）；`GATE_V3_MDD25_PREREG_ZH.md`（门V3）
- **叠法**：trunk 80% + moneyflow_resid 卫星 20%（剥 510300）；Strategy deeper P0 / Arch run.ok `b5425d53…`

## 结论先行

| 门 | 结果 | 一句话 |
|---|---|---|
| **门B** | **FAIL** | 两档 Calmar 均胜 trunk，但两档 MDD 均破 −15% |
| **GATE_V3** | **FAIL** | 两档 CAGR 均胜 trunk，但两档 MDD 均破 −25%；`decay_outcome=REJECT` |
| **纸面** | **勿升** | 研究披露仅；`forbid_paper_handoff=true`；不派烟、不改 paper |

相对 trunk：**CAGR / Calmar 上行**，但 **MDD 仍破门锁**（门B −15%、门V3 −25%）。moneyflow_resid 叠仓路径当前 **不能** 作为抬年化纸面候选。

## 读数（X2 BOOK；summary 原值）

| 档 | 角色 | CAGR | MDD | Calmar |
|---|---|---|---|---|
| 60万 | trunk | −0.58% | −29.93% | −0.019 |
| 60万 | **80/20 combo** | **+2.56%** | **−25.63%** | **0.100** |
| 100万 | trunk | +1.71% | −32.99% | 0.052 |
| 100万 | **80/20 combo** | **+3.52%** | **−28.22%** | **0.125** |

换手：`turnover_2s_mean≈4.4%`（≤20% 子检通过）；`n_ret_days=569`。

### 门B（不去β；Calmar>trunk ∧ MDD≥−15%，两档）

| 档 | calmar>trunk | mdd≤15% | 档结论 |
|---|---|---|---|
| 60万 | ✓（0.100 > −0.019） | ✗（−25.63%） | 不过 |
| 100万 | ✓（0.125 > 0.052） | ✗（−28.22%） | 不过 |
| **总** | | | **FAIL**（`gate_b.pass=false`） |

### GATE_V3（MDD≤25% ∧ CAGR>trunk，两档；decay KEEP；换手≤20%）

| 档 | CAGR>trunk | mdd≤25% | mdd≤15%（参考） | 档结论 |
|---|---|---|---|---|
| 60万 | ✓ | ✗（−25.63% 破 −25%） | ✗ | 不过 |
| 100万 | ✓ | ✗（−28.22%） | ✗ | 不过 |
| decay | `REJECT` / `decay_keep=false` | | | 不过 |
| 换手 | ≤20% ✓ | | | 子检过 |
| **总** | | | | **FAIL**（`gate_v3.pass=false`） |

## 口径备注（披露边界）

1. summary 自注：本诊断混合 **未做** GATE_V3 预注册叠仓的 topN(6/10) / 单名≤6%；结果 **仅研究披露**，终判仍以 Eng Book-Smoke（整手、分档、strategy_v1 成本）为准——本包已内嵌 BOOK 两档 X2（`book_smoke.ok=true`），Alpha 以上述 summary 门字段为研究披露依据。
2. trunk 对照来自本诊断 `trunk_ref`（非历史 HI_LIQ capacity_adv 密封锚）；相对增益成立，**绝对 MDD 仍深于门锁**。
3. 与先前单独 Book-Smoke WATCH（moneyflow_resid 9.75%/9.70%）一致方向：收益端有相对改善，回撤端不过门 → **保持 RESEARCH_ACCEPT + 叠仓 FAIL；勿再单独派烟；勿升纸面**。
4. 叶25 闸审独立：现盘钉 `.ok` `7b279d47` + cmd R5c_v3 `be7f5e5a`；窗 10:00–10:45 ET；**无包不预判**。

## 状态动作

- `alpha_labels`：**不动**（非新叶裁决；moneyflow_resid 标签维持 RESEARCH_ACCEPT / Book-Smoke WATCH·DONE_FAIL）
- 纸面 / promotion / live：**全部 false**；不 handoff Eng 晋级
- 下一步（研究侧，不授权跑）：若继续冲年化，优先正交新叶（叶25 accruals、叶26 ETF-flow who_pays）或 Strategy/Arch 再裁「更浅 MDD」叠法；**本 80/20 P0 路径关闭为研究 FAIL**

live=false；promotion_approved=false。

## 补记（2026-10-25 05:56 ET）

Leo（经主 Agent 转达）**否掉** moneyflow×capacity_adv 80/20 叠仓晋级路径。Alpha **停推**该叠仓；本文维持研究级披露即可；勿再派烟、勿升纸面、不改标签。后续冲年化改盯叶25 等正交新叶。live=false。
