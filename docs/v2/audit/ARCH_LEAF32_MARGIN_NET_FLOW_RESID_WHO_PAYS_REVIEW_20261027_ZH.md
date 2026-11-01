# Arch 审阅：叶32 净融资流入强度残差慢 α who_pays + COVER（只审 DRAFT；不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审） |
| 时刻 | `2026-10-27T03:45:00-04:00`（America/New_York；墙钟 `2026-10-27 03:45 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 本回合动作 | **不签**任何 `.ok`；**不挂 QUIET**；**不代跑**；不改 DRAFT/脚本；**不触** A18；叶30 衰减修复 **`0087c928` 未审**（主明令本拍不审/另队）；叶30/31 HOLD **不回撤**；**≠X2 ACCEPT**；≠Book-Smoke；live=false；**不推 Leo** |
| 触发 | 主 03:41 ET 确认叶号=**32** → 令 Arch 只审 who_pays+COVER（TEAM_STATE 顶条 + 主令） |

## 0. 一句话

WHO_PAYS **`fad5911e`** / COVER **`ebda2603`** 本机 sha256 **MATCH**；mechanism=`g1g5_ashare_margin_net_flow_resid_v1` 可检验（net_rz=rzmre−rzche → flow_raw=mean_W(net_rz/float_mktcap_T−1) → SW+style 残差 → α=−rank(flow_resid)；W/再平衡 DRAFT=20/20；符号冻结纪律；失效条件齐，含 vs margin_delta / hk_hold / Amihud / on_minus_id / CRR）；与叶19/25/27/30/31 正交意向写清（零会计主轴；禁 Amihud/on_minus_id/hk_hold；≠Δrzye margin_delta 复刻；Jaccard≥0.7 硬拒 / ρ_excess>0.5 强度过滤）；HI_LIQ 主 / FULLA 研究双轨；禁卖方/金股/survey/TP/LLM/GP/高杠杆/moneyflow 80/20；rss=1500；DRAFT **NOT FROZEN** / EXECUTED=false / ok_requested=false；`research/leaf32*` **ABSENT**；live `.ok`=0 / QUIET **ABSENT**；margin/float schema 只读核 MATCH（含 `available_at`）。开放项见 §3（须另窗冻结预注册等）。**本拍不签**。

## 1. 钉表再核（本机 sha256）

| 件 | 路径 | 期望 sha8 | 实测全长 | 结果 |
|---|---|---|---|---|
| WHO_PAYS DRAFT | `docs/v2/audit/AI_LEAF32_MARGIN_NET_FLOW_RESID_WHO_PAYS_DRAFT_20261027_ZH.md` | `fad5911e` | `fad5911eec855a3b77d77971f8d44241798bfa4355adebd3f14aa67910fc6c44` | **MATCH** |
| COVER DRAFT | `docs/v2/audit/AI_LEAF32_MARGIN_NET_FLOW_RESID_COVER_DRAFT_20261027_ZH.md` | `ebda2603` | `ebda2603283198382c7225924f4105d9ec9891acad3ba83a022a2172a1dac9fc` | **MATCH** |
| 叶30 HOLD（只读） | `docs/v2/ALPHA_LEAF30_CRR_X2_SELFCHECK_GATE_REVIEW_20261027_ZH.md` | `f00536b9` | `f00536b9978eed619cf672bb327c4c898c9a998dbbeda167814762e3ecdac0dd` | **MATCH**（本拍只读对照；不回撤） |
| 构建脚本 `research/leaf32*` | — | ABSENT | ABSENT | **MATCH 预期** |
| 叶32 live `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF32*` | ABSENT | ABSENT | **MATCH** |
| live QUIET | `output/loop/RESEARCH_QUIET.lock` | ABSENT | ABSENT | **MATCH** |
| live `.ok` 计数 | `output/ai_factory/*.ok` | 0 | 0 | **MATCH** |

对照模板：`docs/v2/audit/ARCH_LEAF31_AMIHUD_IMPACT_SLOW_WHO_PAYS_REVIEW_20261027_ZH.md`（叶31 当时亦是 **DRAFT** → CONDITIONS 含「须另窗冻结预注册」）。

## 2. 必审清单

| # | 要点 | 结果 | 证据 |
|---|---|---|---|
| 1 | 机制可检验：net_rz→flow_raw→SW+style 残差→α=−rank；W/再平衡 DRAFT=20/20；符号冻结纪律；失效条件清晰（含 vs margin_delta / hk_hold / Amihud / on_minus_id / CRR） | **PASS** | WHO_PAYS §0/§2/§3/§9：公式、合成、禁事后翻/冻结前未读收益选号、失效条件齐；COVER 公式钉同构 |
| 2 | 与叶19/25/27/30/31 正交；Jaccard≥0.7 硬拒；ρ_excess>0.5 强度过滤；明确 ≠northbound/hk_hold 换皮；≠Δrzye margin_delta 复刻 | **PASS** | WHO_PAYS §1/§3.5–§3.6/§8；COVER 对照钉；避应计·CRR / overnight−idio / Amihud / hk_hold；历史 margin_delta 仅披露正交 |
| 3 | HI_LIQ 主 / FULLA 研究双轨；PRIMARY 判决=HI_LIQ | **PASS_WITH_CONDITIONS** | WHO_PAYS §5：PRIMARY=HI_LIQ；FULLA 研究对照；预注册须同时冻结两池规格 → C5 |
| 4 | 禁卖方/金股/survey/TP/LLM/GP/高杠杆/moneyflow 80/20 | **PASS** | WHO_PAYS 文首禁项 + §11；COVER 禁止清单 |
| 5 | rss=1500 禁抬意向 | **PASS** | WHO_PAYS §5/§9；COVER rss 意向 |
| 6 | DRAFT NOT FROZEN / EXECUTED=false / ok_requested=false / 无 `.ok` / QUIET ABSENT / 无构建脚本 | **PASS** | 文钉 + 盘证 §1；本拍未签未挂 |
| 7 | decay KEEP 意向（latest_resid_α>0 ∧ 非连降5季 ∧ H2_net_cagr>510300）合理写入 CONDITIONS | **PASS_WITH_CONDITIONS** | WHO_PAYS §7（合取三闸，对齐叶30/31 HOLD 教训）；预注册须写死近端窗/口径 → C6 |
| 8 | 数据 PIT / GAP；日度 base-α 非 Top-N；30bp；X2 窗 2024-06-03→2026-10-09；本拍禁实算 α | **PASS** | WHO_PAYS §4/§5；本机只读核 margin 5,786,686 行、列含 `rzmre/rzche/available_at`；float 11,711,361 行含 `float_mktcap`；HI_LIQ mask 存在；GAP 勿静默编造；**未**实算 α |
| 9 | 备选质量切片未混 PRIMARY | **PASS** | WHO_PAYS §1/§12：AlphaLens / 异常换手仅备案不升 PRIMARY |
| 10 | 叶30 衰减修复 `0087c928` **本拍不审**；叶30/31 HOLD 不回撤 | **PASS（未审声明）** | 主令本拍不审；本回执**未打开/未审** `0087c928`；另队；HOLD 只读对照 |
| 11 | forbid 六票写入 CONDITIONS | **PASS** | WHO_PAYS/COVER 钉 `4bb141c9`+`fdbaa512`+`aa25e989`+`7e239487`+`5af20222`+`5ae077fa` → C7 |

## 3. 条件（冻结预注册 / 脚本 / X2 前必须满足）

1. **C1 须另窗冻结预注册**：本拍审的是 **DRAFT NOT FROZEN**（对齐叶31 who_pays 审深度）。PASS ≠ 可签 `.ok`。请主令 AI 出 FROZEN → Arch 再审 FROZEN → 再谈脚本/X2。
2. **C2 正式构建脚本尚未写**：`research/leaf32*` ABSENT（预期）。另窗 AI 写脚本 → Arch 审脚本 → 独立 X2 `.ok`；**本拍禁签**。
3. **C3 X2 前重算重叠**：须用完整 α 重算 vs 叶19/25/27/30/31 的 Jaccard/ρ；**另须披露 vs 历史 `margin_delta`（Δrzye）**；DRAFT 硬拒意向不能替正式重叠证明。
4. **C4 残差清单写死**：冻结时钉 SW L1 + log 流通市值 + style（mom20/vol20/logADV20 或等价）；缺列 → PIN_GAP，勿静默跳过；后加项须补丁。
5. **C5 FULLA 双钉规格**：预注册须同时冻结 HI_LIQ（PRIMARY 判决）与 FULLA（研究对照）规格；PRIMARY 不得静默改 FULLA。
6. **C6 decay KEEP 冻结口径**：预注册写死 `latest_resid_alpha>0` ∧ `非连降5季` ∧ `H2_net_cagr>510300` + 近端窗定义（与 `alpha_decay_gate` H2 对齐）；失败 → 最多 WATCH/HOLD，不派烟、≠X2 ACCEPT。
7. **C7 禁 RESTORED / 禁复用旧窗**：forbid∋`4bb141c9`+`fdbaa512`+`aa25e989`+`7e239487`+`5af20222`+`5ae077fa`；禁复用叶25/27/30/31 `.ok`；禁 `--arch-ok-path` 自开。
8. **C8 rss=1500 + peak_proof**：未来执行窗硬 ABORT；禁抬。
9. **C9 叶30 修复另队**：`0087c928` 本拍未审；不得借本审窗口夹带签跑。

## 4. 禁项（本回合）

- 不签 / 不改任何 `.ok`；不挂 QUIET；不代跑 python 重活 / 不实算 α
- 不改 WHO_PAYS / COVER DRAFT；不把 DRAFT 当 FROZEN
- 不触 A18；不解阻 X2；不当 X2 ACCEPT；≠Book-Smoke
- 不审 `0087c928`；不回撤叶30/31 HOLD；不推 Leo；live=false

## 5. 硬钉下一跳

```
who_pays DRAFT fad5911e + COVER ebda2603（本审 PASS_WITH_CONDITIONS）
  → 请主令 AI 出 FROZEN 预注册
      → Arch 审 FROZEN / 正式脚本（另窗）
          → 独立新窗 .ok（禁 RESTORED；禁复用叶25/27/30/31；forbid 六票）
              → X2（完整 α；重叠重算含 vs margin_delta；decay KEEP 硬验收）
```

**本拍不签**。

## 6. 本回合非动作声明

- **未签**任何 `.ok`
- **未挂** QUIET
- **未代跑**构建/X2/selfcheck/count；**未实算** α
- **未改** DRAFT / COVER
- **未审**叶30 衰减修复 `0087c928`（另队）
- **不推 Leo**；live=false；promotion=false；x2_accept=false；ok_requested=false；EXECUTED=false

## 7. 结论

**PASS_WITH_CONDITIONS** — who_pays+COVER DRAFT 契约可收；钉 MATCH；机制/正交（含 ≠margin_delta / ≠hk_hold）/双轨/禁项/rss/PIT/decay KEEP 意向齐。开放项见 §3（C1–C9），首要 **另窗冻结预注册（请主令 AI 出 FROZEN）**。本回合不签、不挂、不代跑。

live=false.
