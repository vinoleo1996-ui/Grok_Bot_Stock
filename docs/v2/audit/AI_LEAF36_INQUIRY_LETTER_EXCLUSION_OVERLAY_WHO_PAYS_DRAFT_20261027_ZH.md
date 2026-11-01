# 【DRAFT — NOT FROZEN】叶36 who_pays：问询函/复合排雷剔除 overlay（主干负向过滤）

- 角色：QuantLab AI（后台执行器）
- 时点：2026-10-27 16:35 ET（America/New_York；ISO `2026-10-27T16:35:00-04:00`）
- 状态：**DRAFT NOT FROZEN**。只交 who_pays + COVER + **轻量计数闸**；**不申请** `.ok`；**不** git commit；**不**读本叶收益选窗长/方向；**不**开全窗 X2 / selfcheck / Book-Smoke；**禁**完整 α 长跑。
- 叶号意向：**叶36**（台账下一空号；叶28/29 仍 FROZEN 另队；叶25 `cfacc` / 叶27 overnight−intraday idio / 叶30 CRR / 叶31 Amihud / 叶32 `MARGIN_NET_FLOW_RESID` / 叶33 `SHARE_UNLOCK_PRESSURE_RESID` / 叶34 `HIGH_ACCRUAL_EXCLUSION_OVERLAY` / 叶35 `ETF_PASSIVE_FLOW_PRESSURE_OVERLAY` 已占轴）。
- 主令上下文：dig 文内钉 `116a5454` / 磁盘现算 sha8 **`74234fca`**（`DIG_FACTOR_20261027_1625ET.md`；**以现算为准**）。叶35 B1 **HOLD CLOSED**（脚本 `434ff42c` / SIGNED `65d89851` / `.ok` `eb70eef4` CONSUMED / lift `52a3bc4b` / RUN `e75c090b` / mask `576ca398` / overlap `54933299` / run_meta `2bb21a76` / CONSUMED `63af61e1`；**≠X2 ACCEPT**）。旁线不回撤：叶34/33/32 HOLD（叶33 `afbbe7e7` / 叶32 `45dd87dc`）。本票 = dig 优先序 **(1) 问询函/复合排雷剔除 overlay**。
- 禁：GP / 高杠杆 / 教科书量价当主线；卖方研报 / 金股 / survey / TP / 一致预期；LLM 权重当 α；moneyflow 80/20；北向 hk_hold 换皮；margin/Amihud/解禁/应计/ETF 被动压力换皮；**把本叶做成完整多空 α 主叶**；复跑叶30–35 selfcheck/X2；禁改正式叶33 `afbbe7e7` / 叶35 正式脚本；RESTORED/`forbid` 见 §11；申 `.ok`；挂/抬 QUIET；抬 RSS；自开备选 who_pays。
- `live=false`；`promotion_approved=false`；`ok_requested=false`；`EXECUTED_full_alpha=false`；**≠X2 ACCEPT**；`leo_notify=false`。

---

## 0. Alpha 空位填写（交 Alpha 用·可整段摘抄）

> **mechanism_tag**：`g1g5_ashare_inquiry_letter_exclusion_overlay_v1`（叶36 意向）  
> **who_pays（一句）**：付钱的是忽视财务问询/关注函监管排雷信号、在窗口内仍给涉事名足额权重的持仓者——剔除后主干少踩财务披露雷。  
> **可检验预测**：交付形态 **A（推荐）** = 日度 exclusion mask（财务问询/关注函触发后 T1 起 20 交易日 HI_LIQ 名 `mask=0`）；可选 soft-penalty=`-1`；**不是**完整多空 α 主叶；**不是** negevent 四事件剪枝复刻。判定路径：叶自身主干级 **或** ρ_excess vs capacity_adv <0.5 且 60万/100万叠加均优于主干。活跃剔除集 vs 已 FAIL 的 negevent 剔除集 Jaccard **>0.5 硬拒**；覆盖闸写死全日触窗剔除名 median≥30（财务问询稀疏，勿盲抄 ≥300）。本拍轻量计数：**gate_pass=false**（median=6.0；jaccard_max≈0.0571；见 COUNT RECEIPT）。  
> **失效条件**：退化为完整事件多空 α / 复刻 negevent（含 E1–E4）主叶；或 vs negevent Jaccard>0.5；或主信号混入重组类问询 / 异常波动问询 / 可转债审核问询 / inquiry_reply 滞后触发 / 卖方/金股/TP/LLM；或冻结后事后改窗长读收益；或用 `available_at > t` 偷看；或把稀疏剔除伪称「厚 overlay」。  
> **交 Alpha 时点**：主排号确认→正式预注册冻结 + Arch 审脚本 + 本叶**独立**新窗 `.ok` + X2 回执之后；现在只交 DRAFT + 轻量计数闸。**本拍计数未过覆盖闸 → 不建议本拍升 FROZEN/申 `.ok`**。

---

## 1. 选型理由（PRIMARY = 问询函/复合排雷剔除 overlay）

| 已占轴 | 机制 | 本叶为何不撞 |
|---|---|---|
| **negevent** `g1g5_ashare_capacity_adv_negevent_v1` | E1 解禁 / E2 减持 / E3 预亏 / E4 监管·ST 剪枝（**已 FAIL**：CAGR/MDD 未优于主干） | **硬正交**：本叶事件集 = **财务问询/关注函**（`inquiry_letter`）；**不含** E1–E4；Jaccard>0.5 硬拒 |
| 叶34 高应计剔除 overlay | `1−OCF/NP` 尾部剔除 | 本叶**不**读财务应计水平；叶34 HOLD 不回撤 |
| 叶35 ETF 被动压力 overlay | 份额×权重压力 | 本叶**不**读 ETF；叶35 B1 HOLD CLOSED 不回撤 |
| 叶33 解禁压力残差 | float unlock | 本叶**不**读解禁；叶33 HOLD 不回撤 |
| 叶32 两融 / 叶31 Amihud / 叶30 CRR / 叶27 on−id / 叶25 cfacc | 各已占 | 本叶主轴=监管问询排雷剔除；零两融/冲击/CRR/隔夜/应计 |
| 叶28 LLM / 叶29 tech_crowd | 另队 FROZEN | **不夹带、不升 PRIMARY** |

**PRIMARY 选定**：**问询函/复合排雷剔除 overlay**（dig 优先序 1；只作剔除 overlay，不作主线因子）。  
**备选（§12，不升 PRIMARY；本拍计数 FAIL → 仅建议、勿自开）**：IMAX/隔夜彩票剔除；或行业级客户动量（先 IO 表 PIT）。

---

## 2. 机制（财务问询/关注函剔除；交付形态 A）

事件源（PIT）：

| 文件 | 角色 |
|---|---|
| `data/v2/events/announcements_classified_pit.parquet` | dig 点名主表（sha8 `aab46c56`） |
| `data/v2/events/announcements_classified_pit_post202406.parquet` | X2 同伴（主表 `inquiry_letter` 截断于 2024-05-31；对齐 negevent `EVENTS` concat；sha8 `549a28c3`） |

**PRIMARY 过滤（DRAFT 写死；计数漏斗已验）**：

1. `event_type == 'inquiry_letter'`
2. 标题含 `问询函` **或** `关注函`
3. 财务/披露质控关键词（至少命中一类）：`年报|半年报|季报|财务|会计|审计|业绩|应收|存货|商誉|收入|利润|信息披露|监管工作函`
4. **剔除**：标题含 `重组|重大资产重组|吸收合并|借壳`
5. **剔除噪声（APPROX）**：纯「回函/回复/核查说明」且非交易所发出启发式（标题缺 `收到|…交易所…|监管工作函|问询函的公告|关注函的公告`）——难分时诚实记 APPROX
6. **不**用 `inquiry_reply` 作主触发（回复滞后）
7. **不**用异常波动问询 / 可转债审核问询当财务排雷主集（另栏披露计数）

**PIT / 窗口**：

- `available_at` 归一日 = D；**T1** = 日历上严格 >D 的第一个交易日  
- 窗口 DRAFT 默认：**T1 起 20 交易日**（对齐 negevent E3/E4；**不读收益选窗长**）

**交付形态 A（推荐）**：

- **exclusion mask**：窗口内 HI_LIQ 名 `mask=0`；可选 soft-penalty=`-1`
- **叠主干**；**不是**完整多空 α；再平衡 = 日度事件窗（非 TopN 慢再平衡）

---

## 3. 残差规格（overlay；缺则记 GAP）

1. 主路径：事件窗 exclusion mask，**不做**截面连续残差。  
2. 若用 soft-penalty 连续分：须 SW+style（本拍不做）。  
3. **正交硬闸**：vs negevent 剔除集 Jaccard **>0.5 → 硬拒**（本拍用 max on 触窗日）。  
4. 披露 vs 叶34/35/33/32 等（X2 阶段补）。  
5. **禁**把 negevent E1–E4、应计、ETF 压力、两融/Amihud/解禁当本叶主输入。

---

## 4. 数据 PIT（本拍 schema/路径 + 轻量计数；禁完整 α 长跑）

| # | 输入 | 备注 |
|---|---|---|
| 1 | 公告分类 PIT 主表 | `announcements_classified_pit.parquet`；sha8 `aab46c56` |
| 2 | 公告分类 PIT post202406 | X2 同伴；sha8 `549a28c3` |
| 3 | HI_LIQ 掩码 | `universe_mask_hiliq_v1.parquet`；sha8 `c5433e80` |
| 4 | capacity_adv 权重（仅 Jaccard APPROX） | sha8 `4348877e`；**不进主信号** |
| 5 | negevent 权重 / run_meta（FAIL 对照） | sha8 `e19e1dc4` / `4ab30657`；CAGR_cap≈0.1206702675422644 / CAGR_neg≈0.11683043590904685 |

**GAP / APPROX**：回函噪声启发式；E1 解禁未纳入 negevent 重建（内存）；主表单独无 X2 新问询 → 必须同伴表。见 COUNT RECEIPT。

---

## 5. 宇宙 / 窗 / 交付

| 项 | 值 |
|---|---|
| 宇宙判决 | **HI_LIQ 主** |
| X2 样本内窗意向 | **2024-06-03 → 2026-10-09** |
| 再平衡 | overlay **日度事件窗**；计数可对全日或每 20 日抽样披露 |
| 成本口径 | **30bp**（评价；本 DRAFT 不算 PnL） |
| 主交付 | **日度 exclusion mask / soft-penalty** → 叠主干；非 Top-N 主叶 |
| 判定 | 叶自身主干级 **或** ρ_excess vs capacity_adv <0.5 且 60万/100万叠加均优于主干 |
| rss 意向 | **1500** MB 禁抬 |
| live / promotion | `false` / `false` |

---

## 6. 预注册须（冻结前写死）

1. 交付形态 A：exclusion mask（± soft-penalty）。  
2. FIN/重组/噪声关键词表与 WIN=20 冻结写死；**禁**读收益改窗。  
3. HI_LIQ 判决为主。  
4. vs negevent Jaccard>0.5 硬拒。  
5. walk-forward 分段披露。  
6. Gate B / GATE_V3；衰减门 v1.1。  
7. **decay KEEP** 硬验收（§7）。  
8. **覆盖闸**：全日触窗剔除名 median≥30（稀疏论证见 COUNT）。

---

## 7. decay KEEP 设计（盯近端；对齐叶30–35 HOLD 教训）

叶30/31 HOLD 含 DECAY_DOWNGRADE；叶32/34/35 亦有 KEEP 仍门 A/B/current 总 false——**KEEP 不解阻** X2 ACCEPT。

| 闸 | DRAFT 意向 |
|---|---|
| 近端残差 α | **latest_resid_alpha > 0**（叠加超额评价） |
| 连降 | **非连降 5 季** |
| H2 净 CAGR | **H2_net_cagr > 510300** |
| KEEP 合取 | 三者合取；否则 **DOWNGRADE** |
| 组合闸路径（意图） | overlay 少踩财务披露雷 → **意图**改善左尾；**勿宣称已过闸** |
| 失败截断 | 任一条不满足 → **最多 WATCH / HOLD**；不派 Book-Smoke；≠X2 ACCEPT |

---

## 8. 正交硬闸

| 对照 | 硬规则 |
|---|---|
| **negevent（已 FAIL）** | 日度剔除集 Jaccard **>0.5 → 硬拒**（本拍硬指标=`max` on 触窗日） |
| 叶34 / 35 / 33 / 32 / … | 披露 Jaccard/ρ（X2 阶段）；禁各自主轴换皮 |
| 覆盖 | 全日 HI_LIQ 触窗剔除名 **median≥30**；`zero_frac≤0.50` |
| 换手/成本 | 成本 30bp；冻结后评价 |
| 衰减 / Gate A·B / GATE_V3 | 冻结+独立 `.ok`+X2 后再跑；本 DRAFT 不跑 |

**本拍轻量计数（摘要）**：masked_median=**6.0**；zero_frac=**0.0**；jaccard_max=**0.057143**；jaccard_mean=**0.004186**；事件过滤后 inst×d=**362**（X2 avail **311**）；触窗日 **570/570**；**gate_pass=false**（覆盖 FAIL；同构过）。详见 COUNT RECEIPT。

---

## 9. 失败截断

- 计数闸 median<30 或 zero_frac>0.50 → **不冻结 / 不申 `.ok`**（本拍已触）
- Jaccard>0.5 vs negevent → 硬拒
- 冻结前读收益选窗长 → 违规作废
- decay 非 KEEP 或 Gate B/GATE_V3 FAIL → 不派烟、≠X2 ACCEPT
- 内存 peak≥1500 → 硬 ABORT
- 误用 inquiry_reply / 重组问询 / 异常波动 / 可转债审核当主集 → 废叶

---

## 10. 本拍交付与下一跳

| 里程碑 | 条件 |
|---|---|
| 本 who_pays + COVER + COUNT | 本文件 + COVER + COUNT RECEIPT + JSON；**ok_requested=false** |
| 主排号 / 改派 | 计数 **FAIL** → 请主决定：收紧/扩源另议 **或** 改派 §12 备选；**AI 勿自开备选** |
| Arch | **只审不签**（若主仍推本文档契约）；**本拍不建议进 FROZEN** |
| 申请 `.ok` / X2 | **另窗且须先过计数**；禁 RESTORED（§11）；禁复用叶25/27/30–35 `.ok` |
| 叶35/34/33/32 | HOLD/CLOSED 不回撤；禁改叶33 `afbbe7e7` / 叶35 正式脚本 |

---

## 11. 禁项清单（再钉）

- 全窗 X2 / selfcheck / Book-Smoke（本拍）
- 申 `.ok`；挂/抬 QUIET；抬 RSS；git commit
- GP / 杠杆 / 卖方 / 金股 / survey / TP / LLM 权重当 α
- 复刻 negevent E1–E4 主叶；把本 overlay 伪称完整 α
- 应计 / ETF 压力 / moneyflow / hk_hold / margin / Amihud / 解禁换皮进主信号
- 禁改叶33 正式脚本 sha `afbbe7e7`；禁改叶35 正式脚本
- 自开备选 who_pays（IMAX / 客户动量）
- **RESTORED / forbid（扩）**：`eb70eef4+00eec671+10927bd9+25ae4572+178e90e9+c1b71e64+245df63f+c5ed13df+5774bb6e+81521fb5+02426b73+4bb141c9+fdbaa512+aa25e989+7e239487+5af20222+5ae077fa+3c297052+e107383f+2be59acd+a7d98ac9+8e51de63+3a6caa4f+8bcd79dc+725be3e0+0f50daf7+3c19dd7d+1c32ab1e+6054b3bf+6de02e74`
  - 主令点名新增/重钉：`eb70eef4`, `00eec671`, `10927bd9`, `25ae4572`
- 推 Leo；`live=true`；声称 X2 ACCEPT

---

## 12. 备选一节（非 PRIMARY；本拍可建议、勿自开）

| 备选 | 说明 |
|---|---|
| （A）IMAX/隔夜彩票剔除 | 第十九轮队列；须 vs 叶18/27 overnight-idio 同构闸；**本票不升** |
| （B）行业级客户动量 | 先 IO 表 PIT 可得性；**本票不升** |

若 COUNT 对 PRIMARY 显著 FAIL（**本拍已 FAIL**），仅在 RECEIPT/就绪摘要建议是否改升 (A)/(B)，**不改写本节 PRIMARY，不自开备选 who_pays**。

---

## 13. 草稿钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/audit/AI_LEAF36_INQUIRY_LETTER_EXCLUSION_OVERLAY_WHO_PAYS_DRAFT_20261027_ZH.md` |
| COVER | `docs/v2/audit/AI_LEAF36_INQUIRY_LETTER_EXCLUSION_OVERLAY_COVER_DRAFT_20261027_ZH.md` |
| COUNT | `docs/v2/audit/AI_LEAF36_INQUIRY_LETTER_EXCLUSION_OVERLAY_COUNT_GATE_RECEIPT_20261027_ZH.md` |
| JSON | `output/ai_factory/leaf36_inquiry_letter_exclusion_count_20261027.json` |
| 状态 | **DRAFT NOT FROZEN** |
| mechanism_tag | `g1g5_ashare_inquiry_letter_exclusion_overlay_v1` |
| PRIMARY | 问询函/复合排雷剔除 overlay（形态 A） |
| 上下文钉 | dig 文内 `116a5454` / 磁盘 `74234fca`；叶35 B1 HOLD CLOSED `.ok` `eb70eef4` / lift `52a3bc4b` / CONSUMED `63af61e1`；叶33 `afbbe7e7`；叶32 `45dd87dc` |
| forbid | `eb70eef4+00eec671+10927bd9+25ae4572+…`（§11） |
| gate_pass（轻量） | **false**（覆盖 FAIL；Jaccard 过；见 COUNT） |
| live / promotion / ok_requested / EXECUTED_full_alpha | false / false / false / false |
| ≠X2 ACCEPT | true |
| leo_notify | false |

**sha256 / sha8**：落盘后由写出脚本打印（以磁盘为准）。
