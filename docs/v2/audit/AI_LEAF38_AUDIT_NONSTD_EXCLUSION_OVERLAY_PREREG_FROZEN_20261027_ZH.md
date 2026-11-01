# 【FROZEN 预注册 2026-10-27 20:50 ET】叶38：非标审计意见剔除 overlay（PREREG_FROZEN）

- 角色：QuantLab AI（执行器）
- 冻结时点：**2026-10-27 20:50 ET**（America/New_York；ISO `2026-10-27T20:50:00-04:00`）
- 状态：**FROZEN**（相对 who_pays/COVER/COUNT **DRAFT** 升格为预注册冻结）。冻结前**未**读任何本叶收益选定义/方向。
- 主令：2026-10-27 ~20:46 ET — 主裁 **叶38 出 FROZEN GO**；Arch who_pays 只审 **PASS_WITH_CONDITIONS** 回执 **`acba0865`** → 令 AI 出 FROZEN（C1–C13 入钉；**首要 C9 压峰**）。
- 上游钉（本机 MATCH）：
  - Arch 审：`docs/v2/audit/ARCH_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_WHO_PAYS_DRAFT_REVIEW_20261027_ZH.md` sha8 **`acba0865`**（全长 `acba08650a034b7f40773a5a19923d529dcee0c0cabc6997ddee63501fe0caf2`）
  - WHO_PAYS DRAFT：`docs/v2/audit/AI_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_WHO_PAYS_DRAFT_20261027_ZH.md` sha8 **`16c1f70b`**（全长 `16c1f70bc96b0c7c3d83cfb8493c42dc9ea554e1a2a45f978e78fbf0e573729c`）
  - COVER DRAFT：`…COVER_DRAFT_20261027_ZH.md` sha8 **`7c3b8691`**（全长 `7c3b86915440d3a440be5bde10313cfe7f49360199ed7f70617b572d19f71fea`）
  - COUNT RECEIPT（盘上）：`…COUNT_GATE_RECEIPT_20261027_ZH.md` sha8 **`e82aefa2`**（全长 `e82aefa24a158719e46acafa3933a33e2b78ca6ea674284f138d2b407087a20b`；文内自称 `7cc317d9` **勿采**）
  - COUNT SCRIPT：`…COUNT_GATE_SCRIPT_20261027.py` sha8 **`ba34da2a`**（全长 `ba34da2a6da73fc3736894d99548fee85a3ee74b2ea1722b51d8da3f164be296`）
  - COUNT JSON：`output/ai_factory/leaf38_audit_nonstd_exclusion_count_20261027.json` sha8 **`2b3babb5`**（全长 `2b3babb5d83947d27b61306b9702a43f6093b0b0565ccea3d5e19d6431462750`）
  - dig：`output/d1/DIG_FACTOR_20261027_2026ET.md` sha8 **`fa973826`**（全长 `fa973826c86be2d7e555d5abd30da4c32a3f5c6540b15e33e08f876eeb529101`；文内自称 `a6ddc4ef` **勿采**）
- 对照形态：叶37 PREREG_FROZEN（结构对齐；**内容换叶38 审计非标**；**勿抄** IMAX/彩票机制）；叶34/35 PREREG_FROZEN（exclusion overlay 族）。
- 叶号：**叶38**；mechanism=`g1g5_ashare_audit_nonstd_exclusion_overlay_v1`。
- **上游叶37**：IMAX/隔夜彩票剔除 overlay **HOLD CLOSED**（Alpha `384fb9db` / Arch `4afd5ae1`；`.ok` `57ab9096` 已归档）→ **禁复开** 叶37 主轴；**禁复跑** `015e6f06`/`32605aca`/`108aba8f`（C10）。
- 旁线不混：fund_portfolio 计数附录（Data fund_basic 另线；主令可另排 recount）**不夹带**本 FROZEN。
- **本冻结 ≠ `.ok` / ≠ 正式构建脚本 / ≠ X2 / ≠ selfcheck / ≠ Book-Smoke**；**禁**自申 `.ok`；**本拍无** `research/leaf38*`（ABSENT 预期；C2）；**EXECUTED=false**。
- `live=false`；`promotion_approved=false`；`ok_requested=false`；**≠X2 ACCEPT**；`leo_notify=false`。

---

## 0. Alpha 空位填写（交 Alpha 用·可整段摘抄）

> **mechanism_tag**：`g1g5_ashare_audit_nonstd_exclusion_overlay_v1`（叶38）  
> **who_pays（一句）**：付钱的是忽视非标审计意见（保留/无法表示/否定/带强调事项段等）仍给涉事名足额权重的持仓者——剔除后主干少踩财务鉴证雷。  
> **可检验预测（已冻结）**：PRIMARY 交付 = **mask-only** 日度 exclusion mask（HI_LIQ 内最新可用审计意见 `is_non_standard=True` → `mask=0`；其余可算名 `mask=1`；不可算名不进有效集、不填假 0）；**叠主干 / capacity_adv**；**不是**完整多空审计事件 α 主叶；**不是**叶36 问询函 / 叶37 IMAX / negevent 换皮。PIT：`available_at→T1` + 最新意见判定；键=`ts_code`。判定路径：ρ_excess vs capacity_adv <0.5 且 60万/100万叠加均优于主干。活跃剔除集 vs negevent **与** 叶36 Jaccard **任一 >0.5 硬拒**；完整重叠 + vs 叶34/35/37（及必要时 18/24/27）须 X2 前重算（COUNT 轻量不能替）。厚度闸写死：触窗日剔除名全日 **median≥30** ∧ **frac(日剔除名≥10)≥0.60** ∧ **zero_frac≤0.50**（**勿盲抄** median≥300；叶36 median=6 FAIL 教训）。rss=**1500** 禁抬；正式 X2/申 `.ok` 前须 **peak_proof≤1500**。  
> **失效条件**：退化为完整事件多空 α 主叶；或 vs negevent/叶36 Jaccard>0.5；或用标准无保留意见当剔除；或偷看 `available_at>t`；或把 ETF/应计/问询函/IMAX/negevent 换皮当本叶主输入；或冻结后事后改定义/读收益改阈；或无 peak_proof≤1500 仍申 `.ok`；或把 COUNT gate_pass 当 X2 ACCEPT；或 KEEP 被误读为解阻 ACCEPT。  
> **交 Alpha 时点**：Arch 审本 FROZEN → 另窗正式构建脚本（含压峰）→ Arch 审脚本 → 本叶**独立**新窗 `.ok` + X2 回执（完整重叠 + peak_proof≤1500 + decay KEEP）之后。

---

## 1. 机制（非标审计意见剔除 overlay；慢）— **FROZEN**

### 1.1 PIT / 非标定义（C3 — 写死）

| 项 | **FROZEN** |
|---|---|
| 源 | `data/v2/audit/audit_opinion_pit_tushare.parquet`（字段含 `ts_code` / `available_at` / `is_non_standard` / `audit_result` …） |
| 盘上规模（计数拍披露） | 非标约 **2621** 行 / **895** 只（参考；非正式 α） |
| `available_at→T1` | 将 `available_at` 归一日 D；**T1** = 日历上严格 >D 的第一个交易日（与叶36 同构 T1） |
| 最新意见规则 | 对每个 HI_LIQ 名、每个交易日 t：取全部 `T1 ≤ t` 的审计意见中**最新**一条；若该条 `is_non_standard=True` → **剔除**（mask=0） |
| 改判 | 下一份意见（无论标准/非标）的 T1 起改判 |
| 映射键 | **`ts_code`**（如 `600829.SH`）对齐 HI_LIQ `instrument`；**禁**用 `instrument_id`（`sh.600829`）硬拼 |
| 禁偷看 | **禁**使用 `available_at > t` 的未来意见 |
| 禁误剔 | **禁**用标准无保留意见当剔除 |

`is_non_standard=True` 覆盖族（源字段已标）：带强调事项段的无保留意见、保留意见、无法表示意见、否定意见等（以源列为准；本冻结不事后扩/缩定义读收益）。

### 1.2 剔除规则 / 交付（C4 / C11 — **mask-only PRIMARY**）

```
对交易日 t、名 i ∈ HI_LIQ_t：
  取最新审计意见 op(i,t)（T1≤t）
  若 op.is_non_standard = True → mask(i,t) = 0
  否则可算名 → mask(i,t) = 1
  不可算名 → 不进有效集、不填假 0
交付 = 日度 exclusion mask 叠主干 / capacity_adv
```

| 项 | **FROZEN** |
|---|---|
| **PRIMARY 交付** | **mask-only** 负向 exclusion overlay；**≠主叶**；**禁**完整多空审计事件 α |
| 明示（C4） | **mask-only PRIMARY**；soft-penalty **非 PRIMARY** |
| soft-penalty 另窗 | 若启用连续 soft-penalty=`-1`，须 **SW L1 + log 流通市值 + style（mom20/vol20/logADV20）**；缺列→**PIN_GAP**；须重审 |
| 符号 | 「非标审计意见=剔除」；**禁**读收益改定义/翻方向 |
| C11 | 交付=形态 A **mask-only overlay 叠主干**；**禁**输出完整多空审计 α 主叶；**禁** ETF/应计/问询函/IMAX/negevent 当本叶主输入 |
| 边界 | ≠叶36 inquiry；≠叶37 IMAX/彩票；≠negevent E1–E4 主轴；≠叶34/35 各自主轴换皮 |

---

## 2. 方向 / 符号（已冻结；禁事后切换）— **C1 / C5 厚度纪律**

| 项 | **FROZEN** |
|---|---|
| 主规格 | 最新非标审计意见 → mask=0（负向剔除） |
| 符号 | 「非标=剔除」；冻结前**未**读本叶收益 |
| 厚度阈（C5） | **median≥30** ∧ **frac(日剔除名≥10)≥0.60** ∧ **zero_frac≤0.50** |
| 禁事后改阈 | **禁止**事后改成 median≥300 或放宽到 median≥6；**禁止**读收益改阈 |
| 禁读收益选号 | 冻结前/本拍**未**打开本叶任何收益序列选定义/方向 |

---

## 3. soft-penalty / 残差（C4 — 非 PRIMARY；启用另窗）

1. **PRIMARY = mask-only**（§1.2）：不做 SW+style 全残差。
2. **若另窗启用连续 soft-penalty**：同日 PRIMARY 掩码后须 **SW L1 demean + vs log 流通市值 OLS + style（mom20/vol20/logADV20）**；缺列 → PIN_GAP；后加正交项须**补丁文件**并重审。
3. 披露 vs negevent / 叶36（硬拒口径）及叶34/35/37（及必要时 18/24/27）的 **Jaccard** 与 **ρ**（C7）。
4. **禁**把 ETF/应计/问询函/IMAX/negevent α 当本叶主输入（C11）。

---

## 4. 正交硬闸（C7 — 口径本 FROZEN 写死）

| 对照 | 硬规则 |
|---|---|
| negevent / 叶36 inquiry | 剔除集 Jaccard **>0.5 → 硬拒**（任一对照超限即拒） |
| 叶34 / 35 / 37 | **披露** Jaccard/ρ；完整重叠 **X2 前重算** |
| 叶18 / 24 / 27（必要时） | X2 前按需披露；**禁**复跑其主轴当本叶授权 |
| 厚度 | 触窗剔除名 median≥**30**；frac(≥10)≥**0.60**；zero_frac≤**0.50** |
| 换手/成本 | 评价口径 **30bp** |
| 正式重叠 | **X2 前须用完整 overlay 重算** vs negevent（含 E1 若可行）与叶36（硬拒）及 **34/35/37**（披露）；COUNT 轻量 **不能替**正式重叠证明 |

COUNT 轻量摘要（附录参考，≠X2；**不解阻** ACCEPT）：median=**48.0**；frac_ge10=**1.0**；zero_frac=**0.0**；Jmax_neg≈**0.0562** / Jmax_l36≈**0.0649** ≪0.5；peak≈**1584**MB **WATCH**（仅参考）。

---

## 5. 宇宙（C6 — HI_LIQ 主判决）

| 池 | 角色 | 掩码路径（FROZEN） | 覆盖硬闸 |
|---|---|---|---|
| **HI_LIQ_V1.1** | **PRIMARY 判决** | `output/strategy_hiliq/universe_mask_hiliq_v1.parquet`（sha8 `c5433e80`） | 厚度 §2 / §4（median≥30 等；**非** median≥300） |

- **PRIMARY 不得静默改 FULLA**；若另窗加 FULLA 研究对照须补钉，不得替换 PRIMARY。
- C6：HI_LIQ 主（本叶 COUNT/who_pays 口径；**明示 HI_LIQ-only PRIMARY**）。

---

## 6. 窗 / 交付 / rss / 压峰（C9 — **首要硬条件**）

| 项 | **FROZEN** |
|---|---|
| X2 样本内窗意向 | **2024-06-03 → 2026-10-09** |
| 成本口径 | **30bp**（评价；本冻结不跑 PnL） |
| 主交付 | **日度 exclusion mask**（HI_LIQ）；形态 A overlay 叠主干 / capacity_adv；soft-penalty 非 PRIMARY |
| 判定路径 | ρ_excess vs capacity_adv <0.5 且 60万/100万叠加均优于主干 |
| **rss 意向** | **1500** MB **禁抬**；未来执行窗超限 → **硬 ABORT** |
| **peak_proof** | **REQUIRED**：正式 X2 / 申 `.ok` 前须 **peak_proof≤1500**；**无则不得申 `.ok` / 开 X2** |
| 本拍计数 peak | ≈**1584** MB 仅 **WATCH 参考**（COUNT 脚本非正式构建；不解阻） |
| live / promotion / ok_requested / EXECUTED | `false` / `false` / `false` / `false` |

### 6.1 压峰路径（写死；正式 `research/leaf38*` 必须落地）

1. **分进程**：overlay mask 构建与 negevent/叶36 Jaccard 重建 **分进程**（或预落 pair 集再只读加载）；禁止同一进程同时持有 CAP_ADV+NEGEVENT_W 全帧 + ANN_MAIN/POST + HI_LIQ mask_by + excl 大 dict。
2. **流式/分块**：HI_LIQ / 权重 / 公告 parquet 按日期块或 row-group 过滤读入；`mask_all` 建成 `mask_by` 后立即 `del`+`gc`；审计表建完 excl 后立即释放。
3. **降表示**：instrument 用 categorical / 内部 int id，避免海量 `str`×`set` 双份；Jaccard 对照用磁盘上的 `(date,inst)` 紧凑格式，勿长期驻留巨型 Python set。
4. **单线程**：禁并行 worker 叠 RSS；单进程墙内 ≤1.5GB。
5. **超限硬 ABORT**：peak>1500 → **硬 ABORT**；**禁止**把意向改成 1600/1800「先跑通」。
6. **peak_proof**：正式窗必须回传 `peak_rss_mb≤1500` 证明；否则回执不完整、**不得**申 `.ok`。

---

## 7. decay KEEP 硬验收（C13 — 对齐 `alpha_decay_gate` v1.1 + 叶32/37 教训）

| 闸 | **FROZEN** |
|---|---|
| 近端窗定义 | 与 `alpha_decay_gate` v1.1 **H2 同口径**：评估日 t 起**最近 252 个交易日**净收益窗（不足则按闸门 SHORT_HISTORY/INSUFFICIENT；**≥126** 日才出 α） |
| 近端残差 α | **`latest_resid_alpha > 0`**（年化；v1.1：对 510300 去 β 后截距×252；若以叠加超额评价则同口径披露） |
| 连降 | **非连降 5 季** |
| H2 净 CAGR | **`H2_net_cagr > 510300`** |
| KEEP 合取 | `latest_resid_alpha>0 ∧ 非连降5季 ∧ H2_net_cagr>510300` **三闸同时**；任一条不满足 → **最多 WATCH / HOLD** |
| KEEP 不解阻 | **KEEP 不解阻 X2 ACCEPT**（叶32 **`45dd87dc`** / 叶37 HOLD 教训） |
| 失败截断 | **不派** Book-Smoke；**≠X2 ACCEPT**；不得事后改定义/厚度阈救闸 |

本冻结**不跑**衰减门；验收在独立 `.ok`+X2/selfcheck 另窗。

---

## 8. PIT 输入（正式构建契约）

| # | 输入 | 路径 / 角色（FROZEN） |
|---|---|---|
| 1 | 审计意见 PIT | PRIMARY：`data/v2/audit/audit_opinion_pit_tushare.parquet`；`ts_code`/`available_at`/`is_non_standard` |
| 2 | HI_LIQ 掩码 | PRIMARY（§5；`c5433e80`） |
| 3 | capacity_adv / 主干叠层 | 叠加评价；非本叶主信号源 |
| 4 | SW L1 / style / 市值 | **仅** soft-penalty 另窗强制；mask-only PRIMARY 可后钉 |
| 5 | negevent / 叶36/34/35/37 剔除集或 α | **仅** Jaccard/ρ；不进主信号 |

**GAP 纪律**：缺列/缺窗 → 记 **PIN_GAP**，**勿静默编造**。COUNT APPROX（无 E1；叶36 同漏斗重建；ts_code 映射）持续披露。本拍**未**实算完整 α。

---

## 9. 相对已占轴分家

| 已占轴 | 机制 | 本叶必须多出来的正交 |
|---|---|---|
| **negevent** | E1–E4 剪枝（已 FAIL） | 本叶事件=审计意见非标 PIT 状态；Jaccard>0.5 硬拒 |
| **叶36** inquiry | 财务问询/关注函短窗 | 源不同（audit_opinion vs inquiry_letter）；Jaccard>0.5 硬拒；叶36 覆盖 FAIL 不回撤 |
| **叶37** IMAX/彩票 | 隔夜 idio 波动剔除 | **HOLD CLOSED**；不读收益/波动；不复开 |
| 叶35 ETF 压力 / 叶34 高应计 | 各 overlay | 不读 ETF/应计；HOLD/正式不回撤 |
| 叶33/32/31/30/27/25/24/18 | 各已占 | 零解禁/两融/冲击/CRR/隔夜/量价主输入 |
| fund_portfolio | 主动权益持仓边际 | **旁线**；不夹带本 FROZEN |
| 叶28/29 / `0087c928` | 另队 | **不夹带** |

**一句话分家**：negevent=负面事件剪枝；叶36=问询函短窗剔除；叶37=高 IMAX 彩票剔除（HOLD CLOSED）；叶38=**HI_LIQ 非标审计意见 PIT mask-only 鉴证剔除 overlay（非主 α）**。

---

## 10. 禁 RESTORED / 禁复用旧窗（C8）

forbid∋ 主令点名 **`57ab9096`+`b5be1164`+`4096d401`+**（叶37 `.ok` 及旧 RESTORED 串；**禁触**）：

| sha8 | 备注 |
|---|---|
| **`57ab9096`** | 叶37 selfcheck `.ok` 已归档；禁 RESTORED |
| **`b5be1164`** | 主令点名 RESTORED |
| **`4096d401`** | 主令点名 RESTORED |
| （及主/Arch 既有 forbid 全集） | 禁复用为叶38 授权 |

另禁：
- 复跑叶37 脚本 **`015e6f06`** / B1 **`32605aca`** / 基盘 **`108aba8f`**
- 复用叶18 / 24 / 25 / 27 / 30–37 任一 live/CONSUMED `.ok` 当本叶授权
- 脚本 CLI `--arch-ok-path` 自开
- 本拍申任何 `.ok`；挂/抬 QUIET；抬 RSS；RESTORED 上列任一票
- GP / 高杠杆 / 卖方金股 / TP / LLM / survey

---

## 11. 叶37 HOLD CLOSED / 旁线 / 另队（C10）

- **叶37 IMAX/彩票 HOLD CLOSED**（Alpha `384fb9db` / Arch `4afd5ae1`；`.ok` `57ab9096` 归档）：**禁复开** IMAX/彩票主轴；**禁改**叶37 产物；禁复跑 `015e6f06`/`32605aca`/`108aba8f`。
- **fund_portfolio**：旁线（Data fund_basic / 计数附录另排）；**不混**本 FROZEN。
- 叶36 inquiry 覆盖 FAIL / HOLD 教训：**不回撤**；不放宽其覆盖阈借窗口改写。
- 叶32 HOLD **`45dd87dc`**（KEEP≠ACCEPT）不回撤。
- 叶35 正式 / 叶33 正式 **UNCHANGED** 不回撤。
- 叶30 衰减 KEEP 修复 **`0087c928`**：**另队**；**不并入**本 FROZEN。
- 叶28/29 仍 **FROZEN**；**不夹带**。

---

## 12. C1–C13 对照表（Arch `acba0865` §3 全文入钉；首要 C9）

| # | 条件（Arch §3） | 本 FROZEN |
|---|---|---|
| C1 | 另窗冻结完整预注册 | **本文件**全文（mechanism/PIT/窗/交付/判定/压峰） |
| C2 | 正式脚本另窗；计数非正式构建 | `research/leaf38*` **ABSENT**；计数脚本 audit **`ba34da2a`**（非正式 α 构建） |
| C3 | PIT / 非标定义冻结 | `available_at→T1` + 最新 `is_non_standard=True`→mask=0；键=`ts_code`；禁偷看；禁用标准无保留当剔除 |
| C4 | soft-penalty / mask-only | **明示 mask-only PRIMARY**；连续 soft-penalty 非 PRIMARY，启用须 SW+style |
| C5 | 厚度阈冻结纪律 | median≥30 ∧ frac(≥10)≥0.60 ∧ zero_frac≤0.50；禁改≥300/≥6；禁读收益改阈 |
| C6 | HI_LIQ 主判决 + 窗 | HI_LIQ PRIMARY；窗意向 2024-06-03→2026-10-09；不得静默改 FULLA |
| C7 | X2 前完整重叠；COUNT 不替 | vs negevent/叶36 硬拒>0.5；vs 34/35/37（及必要时 18/24/27）披露；COUNT 轻量不替 |
| C8 | forbid 全集；禁复用旧 `.ok`；禁 `--arch-ok-path` | §10；含 `57ab9096`+`b5be1164`+`4096d401`+；禁复跑叶37 |
| C9 | **rss=1500 + 压峰硬条件（首要）** | rss=1500 禁抬；peak_proof≤1500 REQUIRED；§6.1 分进程/流式/降表示/单线程/硬 ABORT；无 peak_proof≤1500 不得申 `.ok` |
| C10 | 叶37 HOLD CLOSED + 旁线不混 | 禁复开叶37；fund_portfolio 不夹带；§11 |
| C11 | overlay ≠ 主叶硬钉 | 交付=负向 exclusion mask overlay；禁完整多空审计 α；禁换皮主输入 |
| C12 | 轻量计数 ≠ X2 ACCEPT | gate_pass 仅放行 FROZEN/脚本讨论；**不解阻** ACCEPT / Book-Smoke / 升纸面 / 签 `.ok` |
| C13 | decay KEEP；KEEP 不解阻 ACCEPT | 近端=252d（≥126 才出 α）；KEEP 三闸合取；KEEP 不解阻（`45dd87dc` / 叶37 教训） |

---

## 13. 失败截断

- 厚度闸 median<30 或 frac(≥10)<0.60 或 zero_frac>0.50 → 不申 `.ok`
- Jaccard>0.5 vs negevent 或叶36 → 硬拒，改机制或废叶
- 退化为完整多空审计 α 主叶 → 废叶
- 冻结后读收益改定义/厚度阈/方向 → 违规，作废本轮 FROZEN（须新修订文件）
- 偷看 `available_at>t` 或用标准无保留当剔除 → 废叶
- decay 非 KEEP 或 Gate B/GATE_V3 FAIL → 最多 WATCH/HOLD；不派烟、≠X2 ACCEPT；**KEEP 亦不解阻** X2 ACCEPT
- 内存 peak>1500 MB → 硬 ABORT；无 peak_proof≤1500 → **不得**申 `.ok`；回执不完整
- 误读 ETF/应计/问询函/IMAX/negevent 当主输入 / 复开叶37 / 夹带 fund_portfolio → 废叶
- 把 COUNT gate_pass 当 X2 ACCEPT → 违规（C12）

---

## 14. 状态机 / 下一跳（C1 / C2）

```
who_pays DRAFT 16c1f70b + COVER 7c3b8691 + JSON 2b3babb5
  + COUNT 盘上 e82aefa2（文内 7cc317d9 勿采）/ 脚本 ba34da2a
  → Arch PASS_WITH_CONDITIONS acba0865
      → 【本文件】PREREG_FROZEN（C1；mask-only；PIT 非标；厚度；**C9 压峰**；≠主叶）
          → 主排 Arch 只审 FROZEN（本拍目标）
              → 另窗 AI 写正式构建脚本 research/leaf38_*（C2：本拍禁；ABSENT；须含 §6.1 压峰）
                  → Arch 审脚本
                      → 独立新窗 .ok（禁 RESTORED 57ab9096+b5be1164+4096d401+；禁复跑叶37；须 peak_proof≤1500）
                          → X2（完整重叠含 negevent/36/34/35/37；rss+peak_proof；decay KEEP；KEEP 不解阻 ACCEPT）
```

| 项 | 状态 |
|---|---|
| 本 PREREG_FROZEN | **本文件**（C1） |
| 计数脚本 | **`ba34da2a`**（audit/；非正式构建） |
| `research/leaf38*` | **ABSENT**（C2：本拍禁落） |
| 申 `.ok` / X2 / selfcheck / Book-Smoke | **禁**（等主/Arch） |
| COUNT gate_pass | true（附录参考）；**≠X2 ACCEPT**（C12） |
| peak≈1584 | **WATCH**；须压峰 + peak_proof≤1500 后方可申 `.ok`（C9） |
| 叶37 IMAX/彩票 | **HOLD CLOSED** 不复开（C10） |
| fund_portfolio | **旁线不混** |
| 叶33 / 叶35 / 叶32 `45dd87dc` | **不回撤** |

---

## 15. 禁项清单（再钉）

- 本拍实跑完整 α / 申 `.ok` / 落 `research/leaf38*` 构建脚本 / 挂 QUIET / 抬 RSS / git commit
- RESTORED forbid（见 §10）含 `57ab9096`+`b5be1164`+`4096d401`+
- 复跑叶37 `015e6f06`/`32605aca`/`108aba8f`；复开叶36 inquiry 主轴借改
- 禁改叶33 / 叶35 正式产物
- GP / 高杠杆 / 卖方金股 / TP / LLM
- 自开 Book-Smoke；推 Leo；`live=true`；声称 X2 ACCEPT
- 夹带 fund_portfolio 进本票；无 peak_proof≤1500 仍申 `.ok`

---

## 16. 冻结钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/audit/AI_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_PREREG_FROZEN_20261027_ZH.md` |
| RECEIPT | `docs/v2/audit/AI_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_PREREG_FROZEN_RECEIPT_20261027_ZH.md` |
| 状态 | **PREREG_FROZEN**（≠ `.ok`；≠ X2 ACCEPT） |
| mechanism_tag | `g1g5_ashare_audit_nonstd_exclusion_overlay_v1` |
| C3 | PIT `available_at→T1` + 最新非标 → mask=0；键=`ts_code` |
| C4 | **mask-only PRIMARY** |
| C5 | 厚度 median≥**30** ∧ frac(≥10)≥**0.60** ∧ zero_frac≤**0.50** |
| C9 | rss=**1500** 禁抬；peak_proof≤**1500** REQUIRED；§6.1 压峰路径 |
| C11 | **≠** 完整多空审计 α 主叶 |
| Arch | `acba0865` PASS_WITH_CONDITIONS |
| dig | `fa973826`（自称 `a6ddc4ef` 勿采） |
| COUNT | 盘上 `e82aefa2`（自称 `7cc317d9` 勿采） |
| live / promotion / ok_requested / EXECUTED | false / false / false / false |
| leo_notify | false |

**sha256 / sha8**：落盘后由写出脚本打印（以磁盘为准）。
