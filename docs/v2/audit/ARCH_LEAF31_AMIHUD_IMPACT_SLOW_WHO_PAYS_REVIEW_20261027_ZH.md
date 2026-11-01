# Arch 审阅：叶31 Amihud 冲击慢 α who_pays + COVER（只审 DRAFT；不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审） |
| 时刻 | `2026-10-27T02:06:00-04:00`（America/New_York；墙钟 `2026-10-27 02:06 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 本回合动作 | **不签**任何 `.ok`；**不挂 QUIET**；**不代跑**；不改 DRAFT/脚本；**不触** A18；叶30 衰减修复 **`0087c928` 未审**（主明令本拍不审/另队）；**≠X2 ACCEPT**；live=false；**不推 Leo** |
| 触发 | 主 02:02 ET 确认叶号=**31** → 令 Arch 只审 who_pays+COVER（TEAM_STATE 顶条 + 主令） |

## 0. 一句话

WHO_PAYS **`b1a60f07`** / COVER **`4ff55996`** 本机 sha256 **MATCH**；mechanism=`g1g5_ashare_amihud_impact_slow_v1` 可检验（Amihud mean_W(|r|/amount)→SW+style 残差→α=−rank；W/再平衡 DRAFT=20；符号冻结纪律；失效条件齐）；与叶25/27/30 正交意向写清（零会计主轴；禁 on_minus_id；Jaccard≥0.7 硬拒 / ρ_excess>0.5 强度过滤）；HI_LIQ 主 / FULLA 研究双轨；禁卖方/金股/survey/TP/LLM/GP/高杠杆；rss=1500；DRAFT **NOT FROZEN** / EXECUTED=false / ok_requested=false；`research/leaf31*` **ABSENT**；live `.ok`=0 / QUIET **ABSENT**。开放项见 §3（须另窗冻结预注册等）。**本拍不签**。

## 1. 钉表再核（本机 sha256）

| 件 | 路径 | 期望 sha8 | 实测全长 | 结果 |
|---|---|---|---|---|
| WHO_PAYS DRAFT | `docs/v2/audit/AI_LEAF31_AMIHUD_IMPACT_SLOW_WHO_PAYS_DRAFT_20261027_ZH.md` | `b1a60f07` | `b1a60f074c07ea5107bc2a38b6d542cdcaec1b54f5cb2b0ec7fc32f6dc64ee2a` | **MATCH** |
| COVER DRAFT | `docs/v2/audit/AI_LEAF31_AMIHUD_IMPACT_SLOW_COVER_DRAFT_20261027_ZH.md` | `4ff55996` | `4ff55996b6471dee2207ef10ba0e079fc589679254f54c6adae718d973f469b8` | **MATCH** |
| 叶30 HOLD（只读） | `docs/v2/ALPHA_LEAF30_CRR_X2_SELFCHECK_GATE_REVIEW_20261027_ZH.md` | `f00536b9` | `f00536b9978eed619cf672bb327c4c898c9a998dbbeda167814762e3ecdac0dd` | **MATCH**（本拍只读对照） |
| 构建脚本 `research/leaf31*` | — | ABSENT | ABSENT | **MATCH 预期** |
| 叶31 live `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF31*` | ABSENT | ABSENT | **MATCH** |
| live QUIET | `output/loop/RESEARCH_QUIET*` | ABSENT | ABSENT | **MATCH** |

对照模板：`docs/v2/audit/ARCH_LEAF30_CRR_WHO_PAYS_PREREG_REVIEW_20261026_ZH.md`（叶30 当时 **FROZEN**；本叶仍是 **DRAFT** → CONDITIONS 含「须另窗冻结预注册」）。

## 2. 必审清单

| # | 要点 | 结果 | 证据 |
|---|---|---|---|
| 1 | 机制可检验：Amihud→SW+style 残差→α=−rank；W/再平衡 DRAFT=20；符号冻结纪律；失效条件清晰 | **PASS** | WHO_PAYS §0/§2/§3/§9：公式、合成、禁事后翻/冻结前未读收益选号、失效条件（未残差 ADV/换手动量、与叶27 近等权、混入隔夜−日内、卖方/LLM、事后翻等） |
| 2 | 与叶25/27/30 正交；Jaccard≥0.7 硬拒；ρ_excess>0.5 强度过滤；禁 on_minus_id 主输入 | **PASS** | WHO_PAYS §1/§3.6/§8；COVER 对照钉；避应计·CRR / overnight−idio |
| 3 | HI_LIQ 主 / FULLA 研究双轨；PRIMARY 判决=HI_LIQ | **PASS_WITH_CONDITIONS** | WHO_PAYS §5：PRIMARY=HI_LIQ；FULLA 研究对照；预注册须同时冻结两池规格 → C5 |
| 4 | 禁卖方/金股/survey/TP/LLM/GP/高杠杆 | **PASS** | WHO_PAYS 文首禁项 + §11；COVER 禁止清单 |
| 5 | rss=1500 禁抬意向 | **PASS** | WHO_PAYS §5/§9；COVER rss 意向 |
| 6 | DRAFT NOT FROZEN / EXECUTED=false / ok_requested=false / 无 `.ok` / QUIET ABSENT / 无构建脚本 | **PASS** | 文钉 + 盘证 §1；本拍未签未挂 |
| 7 | decay KEEP 意向（latest_resid_α>0 ∧ H2_net_cagr>510300）合理写入 CONDITIONS | **PASS_WITH_CONDITIONS** | WHO_PAYS §7；意向合理（对齐叶30 HOLD 教训）；预注册须写死近端窗/口径 → C6 |
| 8 | 数据 PIT / GAP；日度 base-α 非 Top-N；30bp；X2 窗 2024-06-03→2026-10-09 | **PASS** | WHO_PAYS §4/§5；GAP 勿静默编造 |
| 9 | 备选质量切片未混 PRIMARY | **PASS** | WHO_PAYS §1/§12：ΔNOA/CCC 仅备案不升 PRIMARY |
| 10 | 叶30 衰减修复 `0087c928` **本拍不审** | **PASS（未审声明）** | 主令「叶31 优先」；本回执**未打开/未审** `0087c928`；另队 |

## 3. 条件（冻结预注册 / 脚本 / X2 前必须满足）

1. **C1 须另窗冻结预注册**：本拍审的是 **DRAFT NOT FROZEN**（≠叶30 当时 FROZEN 审）。PASS ≠ 可签 `.ok`。请主排预注册冻结窗（或令 AI 出 FROZEN）→ Arch 再审 FROZEN → 再谈脚本/X2。
2. **C2 正式构建脚本尚未写**：`research/leaf31*` ABSENT（预期）。另窗 AI 写脚本 → Arch 审脚本 → 独立 X2 `.ok`；**本拍禁签**。
3. **C3 X2 前重算重叠**：须用完整 α 重算 vs 叶19/25/27/30 的 Jaccard/ρ；DRAFT 硬拒意向不能替正式重叠证明。
4. **C4 残差清单写死**：冻结时钉 SW L1 + log 流通市值 + style（mom20/vol20/logADV20 或等价）；缺列 → PIN_GAP，勿静默跳过；后加项须补丁。
5. **C5 FULLA 双钉规格**：预注册须同时冻结 HI_LIQ（PRIMARY 判决）与 FULLA（研究对照）规格；PRIMARY 不得静默改 FULLA。
6. **C6 decay KEEP 冻结口径**：预注册写死 `latest_resid_alpha>0` ∧ `H2_net_cagr>510300` + 近端窗定义（与 `alpha_decay_gate` H2 对齐）；失败 → 最多 WATCH/HOLD，不派烟、≠X2 ACCEPT。
7. **C7 禁 RESTORED / 禁复用旧窗**：forbid∋`aa25e989`+`7e239487`+`5af20222`+`5ae077fa`；禁复用叶25/27/30 `.ok`；禁 `--arch-ok-path` 自开。
8. **C8 rss=1500 + peak_proof**：未来执行窗硬 ABORT；禁抬。
9. **C9 叶30 修复另队**：`0087c928` 本拍未审；不得借本审窗口夹带签跑。

## 4. 禁项（本回合）

- 不签 / 不改任何 `.ok`；不挂 QUIET；不代跑 python 重活
- 不改 WHO_PAYS / COVER DRAFT；不把 DRAFT 当 FROZEN
- 不触 A18；不解阻 X2；不当 X2 ACCEPT；≠Book-Smoke
- 不审 `0087c928`；不推 Leo；live=false

## 5. 硬钉下一跳

```
who_pays DRAFT b1a60f07 + COVER 4ff55996（本审 PASS_WITH_CONDITIONS）
  → 请主排预注册冻结窗（或令 AI 出 FROZEN）
      → Arch 审 FROZEN / 正式脚本（另窗）
          → 独立新窗 .ok（禁 RESTORED；禁复用叶25/27/30）
              → X2（完整 α；重叠重算；decay KEEP 硬验收）
```

**本拍不签**。

## 6. 本回合非动作声明

- **未签**任何 `.ok`
- **未挂** QUIET
- **未代跑**构建/X2/selfcheck/count
- **未改** DRAFT / COVER
- **未审**叶30 衰减修复 `0087c928`（另队）
- **不推 Leo**；live=false；promotion=false；x2_accept=false；ok_requested=false

## 7. 结论

**PASS_WITH_CONDITIONS** — who_pays+COVER DRAFT 契约可收；钉 MATCH；机制/正交/双轨/禁项/rss/PIT 齐。开放项见 §3（C1–C9），首要 **另窗冻结预注册**。**可请主排预注册冻结**；本回合不签、不挂、不代跑。

live=false.
