# Arch 审阅：叶30 CRR who_pays 预注册（只审 FROZEN；不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审） |
| 时刻 | `2026-10-26T17:42:00-04:00`（America/New_York；墙钟 `2026-10-26 17:42 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 本回合动作 | **不签**任何 `.ok`；**不挂 QUIET**；**不代跑**；不改 FROZEN/DRAFT/脚本/JSON；**不触** A18 `.ok` `6de02e74`；叶26 不交审；28/29 FROZEN；**≠X2 ACCEPT**；live=false；**不推 Leo** |
| 触发 | 主 17:38 ET 交审 who_pays FROZEN（TEAM_STATE 顶条 + 主令） |

## 0. 一句话

FROZEN `93cad965` 与基盘/计数钉全 **MATCH**；λ=**1.0**、IC 对次期特质收益**期望为正**、禁事后翻、冻结前未读收益均写死；Jaccard≥0.7 硬拒 / ρ_excess>0.5 强度过滤 / 银地非银 `801780`/`801180`/`801790`（`801230` 不掩）齐；APPROX/GAP 醒目钉完整 16 季 OP CRR+vol_pen，禁 ocf_to_profit 冒充 X2；机制分家成立；宇宙/窗/再平衡/30bp/日度 base-α 钉齐；正式构建脚本 **ABSENT**（仅 count_gate `ad524f9e`）→ **CONDITIONS**（预期）；计数 gate_pass=true APPROX **≠晋级/≠X2**；残差最低集 SW L1+log 流通市值，mom/vol/ADV 不强制 → CONDITIONS；本拍隔离成立（无 `.ok`/无 QUIET/未触 A18）。

## 1. 钉表再核（本机 sha256）

| 件 | 路径 | 期望 sha8 | 实测全长 | 结果 |
|---|---|---|---|---|
| FROZEN | `docs/v2/AI_LEAF30_CRR_CFOOE_VOLPEN_WHO_PAYS_FROZEN_20261026_ZH.md` | `93cad965` | `93cad965bd9aa34b6bb8dc5e43d6f0095c4d111420c5fa53b196ad4220d40fba` | **MATCH** |
| 基盘 DRAFT | `docs/v2/AI_LEAF30_CRR_CFOOE_VOLPEN_WHO_PAYS_DRAFT_20261026_ZH.md` | `e00ba1b7` | `e00ba1b7171cd5621c3250881d731d331e1da33f7a80154c2cc0d1979e6c6c00` | **MATCH** |
| 计数回执 | `docs/v2/audit/AI_LEAF30_CRR_COUNT_GATE_RECEIPT_20261026_ZH.md` | `24d1bcfd` | `24d1bcfdffb1bdc2188e7e6a8168604077de7ce774809f66845e94277bec03e8` | **MATCH** |
| JSON | `output/ai_factory/leaf30_crr_hiliq_count_20261026.json` | `b0e7b1d0` | `b0e7b1d0809c8bf03356175f32347b4a3492b70ce478e5941f9e98dfe77ceee5` | **MATCH** |
| 计数脚本 | `research/leaf30_crr_hiliq_count_gate.py` | `ad524f9e` | `ad524f9e039b40b25d3294b9ca84d56a7c108f16fd2a2d51454ba28c1e4a10d0` | **MATCH** |
| A18 EXEC `.ok` | `output/data/ARCH_RUN_AUTH_DAILY_BASIC_A18_SECTION_5_3_BASELINE_EXEC.ok` | `6de02e74` | `6de02e7421fae731be0ee5ab68443ba514b908b34ec03a6ec049b88e42524eca` | **MATCH 未触** |

`research/leaf30*` **仅** `leaf30_crr_hiliq_count_gate.py`；**无**正式 α 构建脚本。live `output/loop/RESEARCH_QUIET*` **无**；本审**未挂** QUIET。

## 2. 必审清单

| # | 要点 | 结果 | 证据 |
|---|---|---|---|
| 1 | λ=1.0 + IC 对次期特质收益期望为正；禁事后翻；冻结前未读收益 | **PASS** | FROZEN §0/§4/§11：`λ^{FROZEN}=1.0`；IC「期望为正」；「禁事后翻」；「冻结前未读任何本叶收益选 λ/方向」 |
| 2 | 正交硬闸：Jaccard≥0.7 硬拒；ρ_excess>0.5 强度过滤；对照叶19/25/accrual_quality | **PASS** | FROZEN §0/§6；计数回执/JSON：J20_max l19≈0.026 / l25≈0.053≪0.7；ρ_mean≈0.365/0.371；strength_filter false |
| 3 | 行业硬掩码 银/地/非银；综金按非银；801230 不掩 | **PASS** | FROZEN §5 + JSON `industry_exclude`：`801780.SI`/`801180.SI`/`801790.SI`；明文 `综合=801230.SI` 不在掩码 |
| 4 | APPROX/GAP 醒目钉；正式须 financials_pit OP + cashflow 16 季 CRR+vol_pen；禁 ocf 冒充 X2 | **PASS** | FROZEN §⚠ A1–A4 + §8；回执 APPROX/GAP；JSON `approx:true` + gaps 含 operate_profit 列缺失 |
| 5 | 机制分家：多季 CRR+CFOOE vol_pen ≠叶19/25/单点 OCF | **PASS** | FROZEN §1–§2；mechanism_tag `g1g5_ashare_crr_cfooe_volpen_v1` |
| 6 | 宇宙/窗：HI_LIQ；X2 2024-06-03→2026-10-09；20td；30bp；日度 base-α 非 Top-N | **PASS** | FROZEN §7；JSON window/rebalance_every_td=20 |
| 7 | 构建脚本 ABSENT | **PASS_WITH_CONDITIONS** | 仅 count_gate；无正式 α 构建 → C1（预期；本拍只审 who_pays） |
| 8 | 计数闸入口：gate_pass=true APPROX；masked median≈2298.5；ρ/J 如上；≠晋级/≠X2 | **PASS** | 回执+JSON 一致；FROZEN A4「计数过闸≠晋级」 |
| 9 | 残差最低集 SW L1 demean + log 流通市值；不强制 mom/vol/ADV | **PASS_WITH_CONDITIONS** | FROZEN §3.5；若 X2 前加正交须补丁 → C4 |
| 10 | 隔离：未签 `.ok`；未挂 QUIET；未触 A18；叶26 不交审；28/29 FROZEN；live=false | **PASS** | 本回合动作 + 盘证；FROZEN §9–§10 |

## 3. 条件（另窗构建/X2 前必须满足）

1. **C1 正式构建脚本尚未写**：另窗 AI 写脚本 → Arch 审脚本 → 再排独立 X2 `.ok`；**本拍禁签**任何 `.ok`。
2. **C2 计数 APPROX 不得升格为 X2 主交付**：正式 α **必须** `financials_pit_tushare`（`operate_profit`）+ `cashflow_pit_tushare`（`n_cashflow_act`）做 L≈16 季 OP CRR + CFOOE 残差 `vol_pen`；禁 ocf_to_profit 冒充。
3. **C3 X2 前重算重叠**：须用完整 α 重算 vs 叶19/叶25/`accrual_quality` 的 Jaccard/ρ；计数抽样（6 日 / proxy rank）仅入口。
4. **C4 残差 mom/vol/ADV 未强制**：若主/Arch 后加，须补丁文件，不得静默改 FROZEN。
5. **C5 错开 A18**：Eng 用 `.ok` `6de02e74`（≥17:45）；本审**不挂** QUIET、不抢 mem 重活；未触 A18 字节。

## 4. 禁项（本回合）

- 不签 / 不改任何 `.ok`；不挂 QUIET；不代跑 python 重活
- 不改 FROZEN / DRAFT / 计数脚本 / JSON
- 不触 A18 `6de02e74`；不解阻 X2；不当 X2 ACCEPT
- 叶26 不交审；叶28/29 仍 FROZEN；不推 Leo；live=false

## 5. 硬钉下一跳

```
who_pays FROZEN 93cad965（本审 PASS_WITH_CONDITIONS）
  → 另窗 AI 写正式构建脚本（16Q OP CRR + vol_pen）
      → Arch 审脚本
          → 独立新窗 .ok（禁复用叶25；避 A18）
              → X2（完整 α；≠APPROX；≠本拍）
```

## 6. 本回合非动作声明

- **未签**任何 `.ok`
- **未挂** QUIET
- **未代跑**构建/X2/selfcheck
- **未改** FROZEN/DRAFT/脚本/JSON
- **未触** A18 `.ok` `6de02e74`
- **不推 Leo**；live=false；promotion=false；x2_accept=false

## 7. 结论

**PASS_WITH_CONDITIONS** — who_pays FROZEN 预注册可收；钉全 MATCH；λ/IC/硬闸/掩码/APPROX·GAP/分家/宇宙窗齐。开放项见 §3（C1–C5）。**可请主排另窗：AI 写构建脚本 → Arch 审脚本 → X2 `.ok`**；本回合不签。

审阅文 sha8：落盘后由执行器钉（见文末）。

live=false.
