# 晋级路径讨论短报 · capacity_adv（纸面轨 · 不交 Strategy）

**日期**：2026-10-12 ~23:32 ET（America/New_York）  
**机制**：`g1g5_ashare_capacity_adv_v1`  
**性质**：**讨论 / 澄清路径与门槛** · **不**构成交 Strategy 授权 · **不**翻转 live 旗标  
**依据（只读）**：
- `docs/v2/AI_G1G5_CAPACITY_ADV_PAPER_PROMOTION_SHORTPACK_ZH.md`（stamp=`DRAFT_PENDING_LEO_ALPHA_CONFIRM`；`paper_active` **proposed**）
- `docs/v2/AI_G1G5_CAPACITY_ADV_WEIGHT_ACCEPT_ZH.md`（ACCEPT · RESEARCH_CANDIDATE）
- `docs/v2/BOOK_SMOKE_G1G5_CAPACITY_ADV_X2_RECEIPT_ZH.md` · run_id `book_smoke_20261013_111418`
- `docs/v2/CAPACITY_ADV_PAPER_ENG_ZH.md` · `docs/v2/BOOK_SMOKE_CAPACITY_ADV_PAPER_WIRE_ZH.md`
- 机读 stub：`output/alpha/AI_G1G5_CAPACITY_ADV_PAPER_PROMOTION_SHORTPACK_20261013.json`
- 纸面包：`output/strategy_paper_capacity_adv/`（STATUS=`PAPER_PACKAGE_READY`；live 仍 false）
- New Bot 转述「Leo 选晋级路径 · capacity_adv paper」：**可引用为纸面轨意向**；**不得**写成 Alpha 聊天最终盖章 live

| 旗标 | 值 |
|---|---|
| **promotion_approved（live）** | **false** |
| **strategy_promotion_approved** | **false** |
| **live_handoff / strategy_live_orders** | **NO / false** |
| **禁 GP / 不开新叶 / 不下单** | **true** |
| **本短报改戳 ledger** | **否**（短包 stamp 仍 DRAFT；本侧不擅自盖最终章） |

---

## 0. 一句话结论

**paper 轨可推进**：文档完备核验、ACCEPT/Book-Smoke/正交/容量硬顶复检、失败条件监控、Eng 纸面接线文档、归因加固（暴露/成本/容量）——**全部仍停在研究/纸面**。  
**绝不可做**：交 Strategy 新权重冒充晋级、实盘下单、升主书、启 GP、叠容量同构换皮新叶、把 New Bot 转述写成 live 最终授权、擅自把短包 stamp 从 DRAFT 改成最终盖章。

---

## 1. 当前状态表

| 项 | 值 | 含义 |
|---|---|---|
| research_candidate | **true** | ACCEPT + Book-Smoke 双端过研究门锁 → 研究候选 |
| any_pass | **true** | 60万∨100万至少一端过门 |
| both_aum_pass | **true** | 60万∧100万同向过门（13.82%/−10.07%；12.23%/−11.62%） |
| paper vs live | **paper proposed** / **live=false** | 短包 `promotion_path=paper_active` 仍为 **proposed**（`DRAFT_PENDING_LEO_ALPHA_CONFIRM`）；live 全线 false |
| handoff | **NO** | 不交 Strategy · 不升主书 · 不下单 |
| 禁 GP | **true** | 不开遗传编程叶 |
| sealed_claim | **false** | 不声称密封过关 |
| paper 包状态 | `PAPER_PACKAGE_READY` | NAV symlink 至已核验 Book-Smoke；**非**实盘 feed 授权 |
| 短包 stamp | `DRAFT_PENDING_LEO_ALPHA_CONFIRM` | 等 Leo 在本侧 Alpha 聊天明示后，**由父代理**改戳；本讨论短报**不**改戳 |

**澄清**：paper / 纸面晋级 ≠ 实盘下单。New Bot「启动纸面晋级轨」= 起草/协调意向；**本短报 = 路径讨论**，不是 Strategy 接线令。

---

## 2. 建议的 paper 晋级检查清单

（全部为 **纸面/研究门**；勾选通过 ≠ live · ≠ 交 Strategy）

| # | 检查项 | 当前（只读核验） | paper 要求 |
|---|---|---|---|
| 1 | **文档完备** | 短包 / ACCEPT / Book-Smoke 回执 / Eng 接线 / who_pays 预注册 / 机读 stub / 纸面包 README·STATUS 均在 | 路径引用齐全；stamp 标明 DRAFT 或最终 paper（仅父代理在 Leo 明示后改） |
| 2 | **ACCEPT** | `AI_G1G5_CAPACITY_ADV_WEIGHT_ACCEPT_ZH.md` → ACCEPT · RESEARCH_CANDIDATE | 无硬闸触发；who_pays 与机制一致 |
| 3 | **Book-Smoke** | X2 满窗成本开；both_aum_pass；vs C0 同向正 | 复跑不得 any_pass→false；不得 vs C0 同向转负 |
| 4 | **who_pays** | 容量/ADV 流动性分位 + 双硬顶；非估值残差/OCF/动量/四臂 | 叙事不得退化为十灭主轴 |
| 5 | **正交 vs 十灭** | 九败+北向 WATCH；Jaccard≥0.7∧EW 同构 **未触发** | 同构硬闸保持 false |
| 6 | **容量硬顶** | 单名≤4%；行业≤28%；600519/002371 正权=0；ADV k=2%@100万；压舱仅 510300 | 破顶即撤 paper |
| 7 | **Eng 纸面接线** | `CAPACITY_ADV_PAPER_ENG_ZH.md`：sleeves 必须 `{core:0,stock:1}`；禁叠 core overlay | 接线文档可消费；**不**启 uvicorn / 不翻转 promotion |
| 8 | **禁 Strategy 交接** | live_handoff=NO · strategy_promotion_approved=false | **本清单通过仍不得**交 Strategy 新权重；须 Leo **另行明示**「交 Strategy」才开交接 |
| 9 | **禁 GP / 不开新叶** | 门锁 true | 失败条件研究 / 正交对照可做；新叶等 Leo 再令 |
| 10 | **授权边界** | New Bot 转述 ≠ Alpha 最终盖章 | 最终 `paper_active` 戳须 Leo 在 Alpha 聊天明示 + 父代理改戳 |

---

## 3. 失败条件 / 回退触发

触发任一条 → **撤 paper / 回 WATCH**（或维持 DRAFT 不盖章）；**绝不**借机交 Strategy 或开 live。

1. **烟门回吐**：复跑 Book-Smoke @60万∧100万 `any_pass→false`，或相对 C0 ΔCAGR 同向转负。  
2. **容量顶破**：任一日个股单名权重 >0.04+ε，或行业名义 >0.28+ε。  
3. **巨头漏入**：`600519` / `002371` 出现正权重。  
4. **同构换皮**：vs 十灭任一 Jaccard≥0.7 **且** EW clone / 叙事退化为动量·估值残差·OCF·四臂·调仓·份额流。  
5. **stub / 前视**：`stub_forward_fill=true` 或 G6 fail / as_of 过滤失效。  
6. **权重合计破**：日 Σw 显著偏离 1，或负权 / NaN。  
7. **未授权 live**：未获 Leo Alpha 明示却宣称 live / Strategy handoff / 升主书 / 启 GP → **越权否决**（失败条件，不是晋级捷径）。  
8. **容量同构新叶**：在未过本清单且未获 Leo 再令时叠「容量换皮」新叶 → 禁；本侧只可做失败条件/正交对照**研究**，不开新叶。

回退动作（纸面级）：短包/STATUS 标回 WATCH 或 DRAFT；保留 Book-Smoke 与权重路径作审计；**不**删证据；**不**写生产 ledger 最终章。

---

## 4. 职责边界（New Bot / Strategy / Alpha / Eng / 本侧 AI）

| 角色 | 可做 | 不可做 |
|---|---|---|
| **本侧 AI（QuantLab AI）** | 研究与归因；paper 路径讨论；失败条件/正交对照短报；引用已有 ACCEPT/Smoke/Eng 文档 | 交 Strategy 新权重；改 Mandate；擅自改 ledger/短包为最终授权；开 GP；开新叶；下单 |
| **Alpha** | ACCEPT 裁决；研究门锁；who_pays / 正交核验 | 把 RESEARCH_CANDIDATE 写成 FactorCandidate 晋级；未明示 live 时发 handoff |
| **Eng** | 纸面接线文档；validate / coverage / sleeves 契约；`--skip-run` 接线绿检 | 启 uvicorn；翻转 `strategy_promotion_approved`；当 Strategy 交接人 |
| **New Bot** | 纸面轨协调；转述 Leo「paper 晋级（不下单）」意向；包 STATUS / 路径聚合 | **单独**构成 Alpha 聊天最终盖章；宣称 live；替 Strategy 接生产权重 |
| **Strategy** | **仅在 Leo 明示「交 Strategy」之后**接权重 / paper feed | 在本短报或 New Bot 转述下自行接新权重冒充晋级；实盘下单（须另有 live 明示） |

**handoff 公式**：  
`paper 讨论通过` ∧ `短包最终戳（Leo 明示）` **≠** `交 Strategy`。  
`交 Strategy` 须 Leo **单独明示**；`live` 须再单独明示。当前两者皆 **false**。

---

## 5. 授权声明（硬锁）

- **本短报不构成交 Strategy 授权。**  
- **`strategy_promotion_approved=false`**（实盘 / Strategy 晋级仍关）。  
- **`promotion_approved`（live）=`false`**。  
- **不下单 · 不升主书 · 不开 GP · 不开新叶 · 不交 Strategy 新权重冒充晋级。**  
- 短包 stamp 仍为 **`DRAFT_PENDING_LEO_ALPHA_CONFIRM`**；本侧**不**擅自改戳。  
- New Bot「Leo 选晋级路径 · capacity_adv paper」= **纸面轨意向引用**；**不是**「本聊天已最终盖章 live」。

---

## 6. 引用

- 短包：`docs/v2/AI_G1G5_CAPACITY_ADV_PAPER_PROMOTION_SHORTPACK_ZH.md`  
- ACCEPT：`docs/v2/AI_G1G5_CAPACITY_ADV_WEIGHT_ACCEPT_ZH.md`  
- Book-Smoke：`docs/v2/BOOK_SMOKE_G1G5_CAPACITY_ADV_X2_RECEIPT_ZH.md`  
- Eng：`docs/v2/CAPACITY_ADV_PAPER_ENG_ZH.md`  
- 机读：`output/alpha/AI_G1G5_CAPACITY_ADV_PAPER_PROMOTION_SHORTPACK_20261013.json`  
- 纸面包：`output/strategy_paper_capacity_adv/STATUS.json` · `SHORT_ZH.md`  
- ledger bak（只读，未写生产）：`output/promotion_ledger.json.bak_capacity_adv_paper`
