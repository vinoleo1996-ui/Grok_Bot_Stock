# 叶27 ndays=40 独立 DRAFT · HAND TO ARCH（**SUBMITTED_TO_ARCH**）

- **时刻**：2026-10-25T16:01:32-04:00（America/New_York）
- **角色**：QuantLab AI
- **主令交审**：`docs/v2/audit/MAIN_LEAF27_CHUNKED_NDAYS40_SUBMIT_TO_ARCH_20261025_ZH.md` sha8 **`b1cbafa1`**
- **status**：**SUBMITTED_TO_ARCH**（由 DRAFT_READY_FOR_ARCH_HOLD `b7c33ca8` 改投）
- **ok_requested**：**false** · **禁自开跑** · **禁申 `.ok`** · **禁抬帽** · live=false · promotion_approved=false

## 前置盘证

| 项 | 值 |
|---|---|
| month `.ok` VOID | Arch 裁定 `docs/v2/audit/ARCH_LEAF27_CHUNKED_MONTH_OK_VOID_ABORT_RSS_20261025_ZH.md` sha8 **`30f7289d`**；consumed `…MONTH.8e51de63.VOID.ABORT_RSS.20261025T1559ET.ok` |
| QUIET | 已 lift（`_lifted/RESEARCH_QUIET_leaf27_month_ABORT_RSS_LIFTED_20261025T1559ET.lock`）；现盘无 QUIET |
| month ABORT 回执 | `03c58db5` MATCH |
| 脚本 | `262f9bf6` UNCHANGED |

## 交审钉（包齐 · 盘证 MATCH）

| 件 | 路径 | sha256 / sha8 |
|---|---|---|
| COVER | `docs/v2/audit/AI_LEAF27_CHUNKED_NDAYS40_COVER_DRAFT_20261025_ZH.md` | `ec5f67e9ba402449421339bd6b8fc47639aa5b19a818732862e2b6a47bb6f23d` / **`ec5f67e9`** |
| CMD | `docs/v2/audit/AI_LEAF27_CHUNKED_NDAYS40_CMD_DRAFT_20261025_ZH.md` | `af6f0d49dc89ae963e0e218b620184ecbf069d9e693b4aeeced62a33e82d8c2b` / **`af6f0d49`** |
| DIFF | `docs/v2/audit/AI_LEAF27_CHUNKED_NDAYS40_DIFF_DRAFT_20261025.diff` | `5449dde5fed4fe73d6669572cdb8381c1764b27381c61a07ca5755d6794a6c66` / **`5449dde5`** |
| HAND | `docs/v2/audit/AI_LEAF27_CHUNKED_NDAYS40_DRAFT_HAND_20261025_ZH.md` | `5547940bec333aa5515af5defccdde241c8812a9fb87f5bcc495427586424a81` / **`5547940b`** |
| VERIFY | `docs/v2/audit/AI_LEAF27_CHUNKED_NDAYS40_DRAFT_VERIFY_20261025_ZH.md` | `305f7a93177d8d7a67204d4e58499374d5155cf79dc262f1515333a1545b4d5e` / **`305f7a93`** |
| 脚本 UNCHANGED | `research/leaf27_chunked_members_mktcap_r1.py` | `262f9bf6878d5c64956529a680abbf36e45adfe72fc7dedc4c68dc1c40291a10` / **`262f9bf6`** |
| month ABORT 回执 | `docs/v2/audit/AI_LEAF27_CHUNKED_MONTH_HILIQ_X2_RUN_RECEIPT_20261025_ZH.md` | `03c58db58e7f3e0e2ff1aa22e8e519a11bf3506d1526bec361f0b5c832039177` / **`03c58db5`** |

## 提案（PRIMARY ONLY）

- PRIMARY（唯一）：`--universe HILIQ --window x2 --chunk-mode ndays --chunk-ndays 40`
- **无**同票 FALLBACK；ABORT → 停 + 另交 hist-prune 包
- rss_limit：**1500** 禁抬帽
- sampler：`/tmp/quantlab_leaf27_chunked_ndays40_*` only
- out_dir 建议：`output/ai_factory/leaf27_chunked_members_mktcap_hiliq_x2_ndays40`
- 脚本：`262f9bf6` UNCHANGED（CLI-only vs month 包；DIFF NO_CODE_CHANGE）
- **forbid_restored**（明文）：**`8e51de63`** / **`3a6caa4f`** / **`8bcd79dc`** / **`725be3e0`**
- 禁自开跑；禁申 X2.ok；≠X2

## 请 Arch

1. 审 COVER+CMD+DIFF（脚本宣称 UNCHANGED `262f9bf6`）
2. **本回合不签** `.ok` / 不代跑 / 不挂 QUIET；签窗另排听主
3. 审毕回执即可；残余风险：hist 累积可能使 ndays40 仍破帽 → 下一刀 hist-prune（禁抬帽）

## 门禁

- AI：**禁自开跑** / **禁申 `.ok`** / **禁抬帽** / 禁 RESTORED 上列 sha8
- live=false · promotion_approved=false · ≠X2

