# Beta · AlphaLens 拥挤闸门/退出状态平滑 → β 预算与降仓袖套（研究级一页）

- 时间：2026-10-25 ≈11:45 ET（America/New_York；盒机 `date` 显示 EDT=UTC−4）
- 角色：QuantLab Beta（β / 风险预算 / 风格 / 袖套；**不**猎数、**不**挖 Alpha、**不**写 who_pays）
- 触发：主 Agent【主→Beta · Leo 批准吸收】A6 — 只读对照 AlphaLens WorkBuddy `crowding.py` + `exits.py`，评估拥挤闸门/状态平滑是否可进 **β 预算或降仓袖套**（**非**选股主 alpha）
- 对齐计划：`docs/v2/audit/MAIN_ALPHALENS_ABSORB_PLAN_20261025_ZH.md` sha `65c75937c0e980a4d228c37153b025e44fc0ef46add8b849ba052758c9b710ea`（A6=Beta）
- 源钉：`docs/v2/refs/alphalens_workbuddy/crowding.py` sha `e655d47afdee028ac64ded99f4d59e7bb4e66d0e2b3aaa0d7a28c55ffe95155c`；`exits.py` sha `0306b92b8c1c6bbd836ef399534bc6e0cff709ee745560778ef3518f4c582469`
- 性质：**机制对照 + 草稿研究开关**。全程只读（Read / rg / sha256sum / ls）。**未**跑 python / pytest / 读 parquet 算收益。未申请 Arch .ok。**未**改 Mandate JSON。未移植 AlphaLens 全站。
- **live=false；promotion_approved=false。** 研究开关**默认关**。不碰纸面轨。本页**无实证数字**（不做回测声称）。

---

## §0 结论三句

1. **拥挤闸门可提案进 β 预算/降仓袖套的研究开关（默认关），不能当选股主 alpha。** AlphaLens `crowd` 是 ETF 相对超额拥挤分；`entry_weight` 在 defensive_crowding / quality∈{partial_history,benchmark_missing} / crowd≥0.72 时拒建仓——落点是 **拒入 + 降 β^eff/vol^eff**，与既有 `BETA_ETF_FLOW…` 反拥挤降 β **同向、无 Mandate 硬冲突**。
2. **exits 只吸「状态平滑/迟滞」思想，不吸 ATR·MACD·板块评分卖股。** 可吸：止损只上不下（预算状态机迟滞）、长下影缩量 hold（避免闸门抖动误砍）。**不可**把吊灯/MA破位/分批止盈/时间止损/动量衰减/板块轮动当残差 α 或个股 exits 主引擎。
3. **不擅改 Mandate；Core v1.3 FAIL 去留仍等 Leo。** 组合层已 vol≈19.6–19.9%、β≈0.86–0.87——拥挤闸若开，方向只能是**进一步压风险**，不得借「吸收」顺流抬 β 冲年化。下一步须 Arch .ok 才可 smoke；本页未实证。

---

## §1 源机制摘要（以磁盘为准）

### 1.1 `crowding.py` · ETF 相对超额拥挤

宇宙行字段（百分比点收益/仓位）：`pos120`、`excess60`/`excess120`/`excess20`、`bias20`、`vol_ratio`；可选 `pos120_partial`。

横截面分位（对非空池）：

\[
r_k(\mathrm{sid})=\frac{\#\{v<x\}+0.5\,\#\{v=x\}}{N},\quad k\in\{\mathrm{excess60,120,20}\}
\]

合成（再 clip 到 \([0,1]\)）：

\[
\begin{aligned}
\mathrm{pos}&=\mathrm{pos120}/100,\quad
\mathrm{bias}=\mathrm{clip}(\mathrm{bias20}/12),\quad
\mathrm{vol}=\mathrm{clip}((\mathrm{vol\_ratio}-0.8)/1.4)\\
\mathrm{raw}&=0.32\,\mathrm{pos}+0.26\,r_{60}+0.14\,r_{120}+0.12\,r_{20}+0.10\,\mathrm{bias}+0.06\,\mathrm{vol}
\end{aligned}
\]

- `pos120_partial`：\(\mathrm{raw}\leftarrow 0.7\,\mathrm{raw}+0.3\times0.5\)
- **structural**：非 partial ∧ excess60≥15 ∧ pos≥0.75 → \(\mathrm{raw}\leftarrow\max(\mathrm{raw},0.78)\)
- **defensive_crowding**：名称∈{银行,煤炭,电力,公用事业,红利,红利低波} 或 secid=`1.512800`，且 (raw≥0.66 ∨ structural)
- `crowding_quality`：`partial_history` | `benchmark_missing`（excess60/120 缺）| `complete`
- 输出 `crowd=round(clip(raw),3)`；policy 标签 `etf-relative-excess-v1`

**建仓拒入 `entry_weight`：**

- action ∉ {建仓, 左侧试仓} → 0
- `defensive_crowding` → 0
- quality ∈ {partial_history, benchmark_missing} → 0
- `crowd ≥ 0.72` → 0
- 否则返回 plan.position_pct（≥0）

README 叙事对齐：拥挤度 >78%「持有不追」；structural 抬底与此同族。

### 1.2 `exits.py` · 买卖分离状态机

返回 `{action: hold|reduce|exit, reason, new_stop}`。卖出**不看**买入评分。动作优先级（源码顺序）：

| # | 条件（摘要） | action |
|---|---|---|
| 1 | last ≤ stop | exit（硬止损） |
| 2 | last ≤ hi−k·ATR 且 r_mult>0.5 | exit（吊灯） |
| 3 | 跌破 MA20 放量且 r<0.3 → reduce；跌破 MA60 → exit | reduce/exit |
| 4 | 1.5R 未半仓 → reduce；2.5R∧RSI>70 → reduce | reduce |
| 5 | 持有≥N 日未达 1R ∧ mom_rank<0.45 | exit（时间） |
| 6 | mom_rank<0.45 ∧ MACD 死叉 ∧ r>0 | reduce |
| 7 | sector_rank_pct<0.5 ∧ r<0.5 | exit（板块轮动） |
| 反人性 | 长下影>3% ∧ 缩量 ∧ 未破 stop | **hold**（不砍） |
| 默认 | 止损上移：MA20×0.985 / 保本；**只上不下** | hold + new_stop |

**Beta 可吸核心：迟滞与单向棘轮**（止损只上不下；恐慌长下影不机械砍）。ATR/MACD/板块评分路径**不可**当选股主 alpha。

---

## §2 QuantLab 落点对照表

| 项 | AlphaLens | 可进 β 预算 / 降仓袖套？ | 不可做 | Mandate / 近亲闸 |
|---|---|---|---|---|
| `crowd` 合成分 | ETF 相对超额拥挤 | **可提案**：研究开关映射 crowd 高 → 降 \(\beta^{\mathrm{eff}}/vol^{\mathrm{eff}}\) 或拒加仓 | 当残差 α / 8 维技术分主因子；顺流抬 β 冲年化 | 与 `BETA_ETF_FLOW` 反拥挤**同向**；近亲 SHARE-AC / IND-CROWD-REV / V3_BROAD_ETF_PXVOL_CROWD（价量）→ smoke 须差分报 |
| structural≥0.78 抬底 | 绝对超额护栏 | **可提案**：结构性拥挤时强制最低降档（拒追） | 用 structural 当「强趋势可加仓」借口 | 无冲突（降风险） |
| defensive_crowding | 防御名+拥挤 → 拒建 | **可提案**：防御袖套拒加仓 / 维持现金 | 把红利低波当进攻卫星 | 与 Mandate `low_vol` 意图软兼容 |
| crowding_quality 缺失 | partial / benchmark_missing → 拒 | **必须**：拒调预算、不伪造 complete | 缺 excess 时填 0.5 或静默放行 | 与 ETF_FLOW「quality 缺失拒调」同纪律 |
| entry_weight 拒入 | crowd≥0.72 等 → 0 | **可提案**：建仓拒入闸（β 袖套/宽基加仓边界） | 拒入后改用个股 exits 补仓 | 不改 `max_etf`；不绕 DD L1–L4 |
| 止损只上不下 | new_stop 棘轮 | **可吸为预算状态机迟滞**：\(\beta^{\mathrm{eff}}\) 降档后冷却期内禁立刻回补 | 棘轮用于抬 β 上限 | 与 DD hook「只降不升」同向 |
| 长下影缩量 hold | 反人性不砍 | **可吸**：闸门抖动抑制（单日噪声不翻档） | 当「永不减仓」豁免 | 软；须有冷却/确认日 |
| 吊灯 / MA / 分批止盈 / 时间止损 | 个股/ETF 卖出纪律 | **否**（本回合） | 当选股主 alpha 或替换 Book-Smoke 退出 | 禁抄计划 A 禁项；归 Strategy/纸面另单 |
| MACD 死叉 / 板块评分跌出前 50% | 动量衰减/轮动 exit | **否** | 8 维技术分 / 板块评分卖股当 α | 硬禁（吸收计划禁抄） |
| README OOS 数字 | 全样本/OOS 表 | **不采信为本页结论** | 抄其年化/Sharpe 当 QuantLab 候选 | 计划明文：不把其 OOS 负超额当候选叶 |

**落点一句话：** 可提案的是 **风险预算旋钮**（\(\beta^{\mathrm{eff}}\) / \(vol^{\mathrm{eff}}\) / DD 缩放触发 / 建仓拒入）与 **状态平滑**（迟滞、避免闸门抖动）；**不是** 8 维技术分，**不是**个股 exits 当 alpha。

---

## §3 冲突矩阵（相对 Mandate vol16% / β0.70 与近亲）

Mandate 锚点（`docs/v2/QuantLab-MANDATE_V2.json` sha `04afacc4…`）：`target_annual_vol=0.16`（带 0.14–0.18）；`target_beta_vs_benchmark=0.70`；`target_beta_band=[0.5,0.85]`。Core v1.3 门控（`BETA_CORE_V1_3_GATE_REVIEW_ZH.md` sha `8bff82f1…`）只读披露：组合 vol≈**19.6–19.9%**、对 510300 β≈**0.86–0.87**，门控 **FAIL**（去留等 Leo）。

| 动作 | 冲突级 | 理由 |
|---|---|---|
| crowd 高 / structural / entry 拒入 → 降 \(\beta^{\mathrm{eff}}\)（如 0.60）与 \(vol^{\mathrm{eff}}\)（如 0.14），或拒加仓 | **无冲突** | 落在报告带内；与 `BETA_ETF_FLOW` 反拥挤档、DD hook 只降不升同向 |
| quality 缺失 → 拒调预算、不伪造 | **无冲突** | 保守；与数据纪律一致 |
| exits 棘轮/长下影 → 预算状态机迟滞（降档后冷却） | **无冲突** | 抑制抖动；不抬风险上限 |
| 抽离/低拥挤后小幅回补 β，且组合 realized vol 已 ≤16% | **软冲突** | 同 ETF_FLOW 抽离档；须双门槛 |
| 与 SHARE-AC / IND-CROWD-REV / PXVOL_CROWD / ETF_FLOW 同开且仓位路径高度相关 | **软冲突（近亲）** | 机制近亲；smoke 须正交/差分闸，失败即关 |
| 顺 crowd 抬 β/vol 冲年化；或 Core 已超 vol 上再抬 | **硬冲突** | 越 Mandate 带 / 加剧已超标 vol；须 Leo 书面改 Mandate 且改门在看收益前 |
| 移植 ATR·MACD·板块评分 exits / 8 维技术分当主 alpha | **硬冲突（角色越权）** | 吸收计划禁抄；Beta 不做选股主 alpha |
| 擅改 Mandate JSON / 抬 `max_etf` / 绕过 DD | **硬冲突** | 本页明确禁；handoff 契约 |

**一行摘要：** 反拥挤降 β/拒入/迟滞 = **无冲突**；近亲叠仓与低拥挤回补 = **软**；顺流抬 β、技术 exits 当 α、擅改 Mandate = **硬**。

---

## §4 草稿研究开关（默认关）

只动 Beta 袖套有效目标与建仓边界；**不**改 Mandate 点目标 JSON；**不**改 Strategy 残差 α；**不**写实盘权重。

建议键（研究级命名，未接线）：

| 键 | 默认 | 含义 |
|---|---|---|
| `etf_crowd_gate_for_beta` | **false** | 总开关：拥挤闸是否映射到 \(\beta^{\mathrm{eff}}/vol^{\mathrm{eff}}\) |
| `etf_crowd_entry_reject` | **false**（随总开关） | crowd≥θ / defensive / quality 坏 → 拒加仓（权重增量=0） |
| `etf_crowd_theta` | 0.72（源码钉；可研） | 与 AlphaLens entry 拒入阈对齐作起点，**非**实证最优 |
| `etf_crowd_budget_hysteresis` | **false** | 吸 exits：降档后冷却 K 日禁回补；止损式「只上不下」→ 风险上限棘轮只收不放 |
| `etf_crowd_panic_hold` | **false** | 吸长下影缩量：单日噪声不翻档（确认日/缩量条件） |
| `absorb_alphalens_tech_exits_as_alpha` | **false 且禁开** | MACD/板块评分/吊灯卖股路径，本回合硬关 |

离散档（与 ETF_FLOW §2.1 同向，避免双开打架；若两开关皆研，须互斥或取更严）：

| 状态 | \(\Delta\beta\) | \(\Delta vol\) | 备注 |
|---|---|---|---|
| crowd≥θ 或 structural 或 defensive_crowding | −0.10 → 0.60 | −0.02 → 0.14 | 反拥挤；无冲突 |
| quality≠complete | 不调（保持上期） | 同 | **拒伪造** |
| 中性 | 0 | 0 | Mandate 点目标 |
| 低拥挤回补 | +0.05 → 0.75 **仅** vol̂≤16% | 0 | 软冲突；否则 0 |

再进入既有 `BETA_VOL_TARGET_HANDOFF`：\(w_{vol}=vol^{\mathrm{eff}}/\hat\sigma\)，\(w_\beta=\beta^{\mathrm{eff}}/\hat\beta_{\mathrm{unit}}\)，\(etf=\min(w_{vol},w_\beta,max\_etf)\)，仍叠 DD L1–L4（`BETA_DD_HOOK_FOR_COMBO_ZH.md` 默认关钩子；开时只降不升）。

---

## §5 非动作 / 下一步

1. **不改** `QuantLab-MANDATE_V2.json`；不抬 `max_etf`；不绕 DD。
2. **不申** Arch `.ok`；不跑回测；本页**零**年化/Sharpe/命中率声称。
3. **不移植** AlphaLens 全站 / NeoData / 8722；不把其 OOS 表当候选叶。
4. **不做** who_pays / 选股主 alpha / 个股 exits 接线。
5. **不挡**叶25/叶27 窗；Core FAIL 去留仍等 Leo——本开关与 Core 复活正交。
6. 下一步：若 Leo/主裁要 smoke → Arch 签研究/selftest `.ok` 后，优先只开 `etf_crowd_gate_for_beta` 降档臂 + quality 拒调；对照 ETF_FLOW / SHARE-AC 近亲闸；失败即保持 false 并归档。

---

## §6 引用钉（写时 sha256）

| 文件 | sha256 |
|---|---|
| docs/v2/audit/MAIN_ALPHALENS_ABSORB_PLAN_20261025_ZH.md | 65c75937c0e980a4d228c37153b025e44fc0ef46add8b849ba052758c9b710ea |
| docs/v2/refs/alphalens_workbuddy/crowding.py | e655d47afdee028ac64ded99f4d59e7bb4e66d0e2b3aaa0d7a28c55ffe95155c |
| docs/v2/refs/alphalens_workbuddy/exits.py | 0306b92b8c1c6bbd836ef399534bc6e0cff709ee745560778ef3518f4c582469 |
| docs/v2/BETA_ETF_FLOW_PREMIUM_BETA_SIGNAL_DRAFT_ZH.md | 0fa22cd818bdd2c348a9e71842babd4cdab4caed0d47f1d722b01c98797e9efd |
| docs/v2/BETA_VOL_TARGET_HANDOFF.md | 3872d1a449b8704ae398f79881194aa7ab6b49cfe7e9fc2689893b62f0ddedfa |
| docs/v2/BETA_DD_HOOK_FOR_COMBO_ZH.md | 52127c65c56b0fc8d64b6c4d92a012f4ecc756dafb3ad23646aa891a26615bb9 |
| docs/v2/QuantLab-MANDATE_V2.json | 04afacc45778bfcdcfbcc7b8ff73098f2ec843cd49fea6ef406d297e05e68f0f |
| docs/v2/BETA_CORE_V1_3_GATE_REVIEW_ZH.md | 8bff82f1b30c92898fb5cc8c681dd8c3440925a71eef1bdd72918db72990a4fa |
| docs/v2/V3_BROAD_ETF_PXVOL_CROWD_PREREG.md | 6beb4d1e67f02e71b1996c3ddc9a60e685bcbf917db90dd1a96641567ce02332 |
| docs/v2/V3_IND_CROWD_REV_PREREG.md | 50f27484fb2fd1465af37e1eb851d26a60fe8a3fbdaa3ac039b159bd934bfc5d |

## §7 落盘与门锁

- 路径：`docs/v2/BETA_ALPHALENS_CROWDING_EXIT_BETA_BUDGET_ZH.md`（写前确认不存在；未覆盖任何旧文）
- `etf_crowd_gate_for_beta=false`；`live=false`；`promotion_approved=false`
- 不改 Mandate JSON；未申 Arch .ok；未跑实数据；未移植 AlphaLens 全站
- 最终 sha256：以落盘后 `sha256sum` 实测为准（R3；正文至此结束，避免自指改哈希）。完整文件 sha 以 TEAM_STATE / 回执 R3 为准。

---

*Beta A6 · live=false · promotion_approved=false · 不改 Mandate · 未实证*
