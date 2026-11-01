# AI：叶26 预注册 DRAFT 只读核验 / 补遗（**不改 DRAFT 正文**）

- **角色**：QuantLab AI 执行器
- **时刻**：2026-10-25 07:17:16 EDT（America/New_York）
- **任务**：对 Arch 起草的叶26 预注册 DRAFT **只读核验/补遗**；live=false；不申 `.ok`；不冻结；**勿另开第二份预注册**；不跑实数据；不 git commit；不挡叶25
- **审阅对象**：`docs/v2/AI_LEAF26_BROAD_ETF_FLOW_STOCK_PREREG_DRAFT_r1.md`
- **DRAFT 现盘全长 sha256**：`b043974792c9cb84ac1437de26bbe45e5a17b3c38552badea0ddb43225be2473`（期望 `b0439747…` → **MATCH**）
- **本文件是否改动 DRAFT 正文**：**否**（默认不改；未发现致命错字需主令改稿）
- **结论**：**PASS_WITH_GAPS**（清单 1–6 全过；无三源硬冲突；留冻结时并入补遗 ≤5 条，非 DRAFT 缺陷）

---

## 0. 三源 MATCH（落盘前重核）

| 输入 | 路径 | 期望全长 sha256 | 现盘 | 结果 |
|---|---|---|---|---|
| Arch 契约预告 | `docs/v2/ARCH_AI_LEAF26_CONTRACT_PREVIEW_20261025_ZH.md` | `5c44944c2a496a5cc461459d9b9f232116bfa152a41f1b26f8e21427a9a42f36` | 同左 | **MATCH** |
| Data 缺口回执 | `docs/v2/audit/DATA_LEAF26_ETF_FLOW_GAP_RECEIPT_20261025_ZH.md` | `aaf84d66ececa313a371020cd0ae0f4ce5092902849b89b5b6dea79867b4e859` | 同左 | **MATCH** |
| who_pays DRAFT r2 | `docs/v2/AI_LEAF26_BROAD_ETF_FLOW_STOCK_WHO_PAYS_DRAFT_r2.md` | `0b55bfeb3b033da4715e4dbc5c996e92b954fc10e385c10b308da992d87a60b5` | 同左 | **MATCH** |
| 本 DRAFT r1 | `docs/v2/AI_LEAF26_BROAD_ETF_FLOW_STOCK_PREREG_DRAFT_r1.md` | `b043974792c9cb84ac1437de26bbe45e5a17b3c38552badea0ddb43225be2473` | `b043974792c9cb84ac1437de26bbe45e5a17b3c38552badea0ddb43225be2473` | **MATCH** |

DRAFT 首页 §MATCH 三件与上表一致；旁证 Strategy `7722efec…` / 旧盘点 `c03a9f0e…` 未作本闸重核（非阻断）。

---

## 1. 检查清单逐项

| # | 检查项 | 结论 | 证据（DRAFT 定位） |
|---|---|---|---|
| 1 | 状态明确 DRAFT 未 FROZEN | **PASS** | 标题「【DRAFT — 未冻结】」；§0「**DRAFT（未冻结；正式 FROZEN 另候主令）**」；§4.2 / §9 / §11 钉表均写未冻结；方向「未选号」 |
| 2 | `pit_basis` 硬写（权重无 `available_at` 代理；主输入份额流） | **PASS** | §3 专节；§3.1-A 主输入 `etf_share_flow_pit_major`（有 `available_at`）；§3.1-B / §11 `pit_basis=month_end_snapshot_no_available_at`；禁静默称严格奇 PIT（§0 锁 / §3.3） |
| 3 | 禁扩池：仅 510300/510500；剔 512100/000852 | **PASS** | §1 / §11；硬规则「不得 silent 写入 512100/000852」；扩池须 Strategy+Data+Arch 共签 + bump |
| 4 | `mechanism_tag` 与 r2/Arch 一致 | **PASS** | `g1g5_ashare_broad_etf_flow_stock_v1`（§0 / §11）= r2 §0 = Arch §0；明示不用未钉 `…_who_pays_v1` 别名 |
| 5 | GAP（index_weight PIT / hk_hold / premium / 美 ETF）披露 | **PASS** | §3.2 #1/#4/#5/#6 + §8「GAP×4」对齐 Arch §1.1 / Data §6；另 PARTIAL×3（000852/映射/hsgt_top10） |
| 6 | α 向量非 Top-N；双轨宇宙；live/promotion false；不挡叶25 | **PASS** | §2 FULLA 主报 + HI_LIQ 纸面；「α 定义 ≠ Top-N」；§11 `live=false` / `promotion_approved=false`；§0/§9 叶25@10:00–10:45 优先、不申 `.ok` |
| 7 | 与三源文冲突点 | **PASS（无硬冲突）** | 见 §2；仅有族惯例扩展待冻结确认，无与 r2/Arch/Data 矛盾的池/`pit_basis`/tag/GAP 口径 |

---

## 2. 与三源冲突点清单（只列差异；非硬拒）

| # | 点 | 性质 | 说明 |
|---|---|---|---|
| C1 | 双宇宙 FULLA_V1 / HI_LIQ_V1.1 + 密封窗 2018-01-02→2024-05-31 + X2 起 2024-06-03 | **扩展（非冲突）** | r2 / Arch 预告未钉叶26 宇宙与密封字面；DRAFT 沿叶25/27 族惯例写入。冻结前建议 Arch 明示收纳或 bump |
| C2 | 评价默认：5 日再平衡、AUM 60万/100万、30bp/17.5bp、年化 244/252 | **扩展（非冲突）** | 同上；DRAFT §4.3 自标「研究级默认叙述；正式跑前 Arch 审脚本确认」 |
| C3 | 失效条件并列禁 silent 扩 512100/**000852** | **更严（对齐 Arch/Strategy）** | r2 失效句有时只点名 512100；DRAFT/Arch 预告一致写两码——建议冻结保留更严口径 |
| C4 | 权重 PIT：研究级可绕 + 正式 FROZEN/`.ok` 前须 Arch 明示接受披露或落列 | **对齐** | 与 Data §6「软阻塞」/ Arch §1.1 #1 同义；非冲突 |
| C5 | α 符号本 DRAFT 未选号 | **对齐 r2** | r2「不读收益选号」；正式 FROZEN 瞬间落盘后禁翻号——正确留白 |

**硬冲突计数：0。** 三源 MATCH 不被本 DRAFT 覆写或软化。

---

## 3. 补遗建议（供主裁冻结时并入；**不直接改** DRAFT 正文）

1. **FROZEN 首页**：重钉现盘 Data/Arch sha；写死 `α_raw` 符号；重申 `pit_basis=month_end_snapshot_no_available_at`；附 Arch「接受本披露」一句或权重 `available_at` 落列回执路径。  
2. **收纳或 bump C1/C2**：冻结文明确「双宇宙 + 密封/X2 字面 + 5 日再平衡/成本」是否一字收纳；若改数字须新文件名 bump，不得 silent。  
3. **池硬句保留**：默认池「仅 510300→000300、510500→000905；剔 512100/000852」整句进 FROZEN；敏感性支路另文件。  
4. **GAP 首页摘要保留 GAP×4 + PARTIAL×3**（与 Arch `5c44944c…` §1.1 / Data `aaf84d66…` §6 同构），避免冻结时漏披露 premium/美 ETF/hk_hold。  
5. **正交锁**：FROZEN 继续写死不挡叶25、不复用叶25/叶27 `.ok`、禁消费补跑 `9e4359f9`、`live=false` / `promotion_approved=false`。

---

## 4. 非动作（本核验）

- **未改** DRAFT 正文；**未**另开第二份预注册  
- **未**申请 `.ok`；**未**冻结；**未**跑实数据；**未** git commit  
- **不挡**叶25@10:00；叶27 `.ok` 另窗（≥10:50 ET）正交  
- live=false

---

## 5. 钉

| 项 | 值 |
|---|---|
| 本补遗路径 | `docs/v2/AI_LEAF26_PREREG_DRAFT_AI_READONLY_NOTE_20261025_ZH.md` |
| 结论 | **PASS_WITH_GAPS** |
| DRAFT 全长 sha256 | `b043974792c9cb84ac1437de26bbe45e5a17b3c38552badea0ddb43225be2473` |
| MATCH Arch / Data / r2 | `5c44944c2a496a5cc461459d9b9f232116bfa152a41f1b26f8e21427a9a42f36` / `aaf84d66ececa313a371020cd0ae0f4ce5092902849b89b5b6dea79867b4e859` / `0b55bfeb3b033da4715e4dbc5c996e92b954fc10e385c10b308da992d87a60b5` |
| 改动 DRAFT | **否** |
| live / promotion | false / false |

**本补遗 sha256**：以本文件落盘后 `sha256sum` 为准。
