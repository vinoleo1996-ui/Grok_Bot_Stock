# Alpha 裁定：叶16 `broker_gold_new`（券商金股同月 ≥2 家新进）— WATCH/DONE_FAIL

| 项 | 值 |
|---|---|
| 裁决 | **WATCH/DONE_FAIL**（不可交易 / CMC·衰减·GATE_V3 均不过）；**Book-Smoke=SKIP**（主 Agent 因闸门失败取消 X2，不派 Eng） |
| 日期 | 2026-10-14 ≈07:41 ET · QuantLab Alpha |
| 宇宙 | **FULLA_V1 时代**：全 A 为主口径（Leo 07:24 取消禁小盘）；mid_large 仅对照 |
| promotion / live / handoff / GP | false / false / NO / 禁 |
| 权重（主） | `output/ai_factory/g1g5_broker_gold_new_alla_daily_weights_20261014_192744.parquet`（sha256 `7f033b4b10fc…d5d5`） |
| 权重（对照） | `output/ai_factory/g1g5_broker_gold_new_daily_weights_20261014_192827.parquet`（sha256 `4da6631255ee…0395`） |
| 回执 / 预注册 | `docs/v2/AI_G1G5_BROKER_GOLD_NEW_WEIGHT_RECEIPT_ZH.md`；who_pays `AI_G1G5_BROKER_GOLD_NEW_WHO_PAYS_PREREG_ZH.md` + 全A补充 |
| 自检 | `output/ai_factory/leaf_reports/broker_gold_new_alla/`（主）与 `broker_gold_new/`（对照） |
| JSON | `output/alpha/AI_G1G5_BROKER_GOLD_NEW_WEIGHT_ACCEPT_20261014.json` |

## 1. 独立核验（parquet，全A主）
- 122,912 行 / 668 日 / 184 标的（含 510300）；2024-01-02 → 2026-10-09
- 列含 `date,instrument,target_weight,weight,mechanism_tag,who_pays_zh,universe_id,session,instrument_id`；`target_weight≡weight`；无 NaN；无 stub
- 日 Σw min=max=1.0；个股单名 max 4.0%；日持股 ≤20（max=20）；申万一级 max 16%（≤28% ✅）
- 600519 / 002371：**不在持仓表**（hard_exclude 恒 0）✅
- 压舱 510300：均值 69.0%；全压舱 102/668 日；股票袖均值 31.0%
- who_pays 列非空；mechanism_tag=`g1g5_ashare_broker_gold_new_v1_allA`；universe_id=`g1g5_all_a_tradable_broker_gold_new`
- 平局规则（读收益前披露）：同日事件 >20 名 → 券商家数降序、代码升序取 Top20 ✅
- mid_large 对照：72,812 行 / 109 标的；Σw≡1；单名≤4%；压舱均 75.3% — 仅对照，不入主裁

## 2. 叶验收 v2（HC → 单叶 → CMC → 衰减门 v1.1 → GATE_V3 本地）

### 2.1 HC（假设批判）→ **HC_PASS**
| # | 结果 |
|---|---|
| H1 机制 | 同月≥2 家券商新进金股 → 卖方新增共识 → 月初买盘（行为/流动性）✅ |
| H2 who_pays | 付钱方：不跟踪卖方月度推荐、月初被动卖出的资金；容量：全A、日均~7.8 名×4% ✅ |
| H3 前视/PIT | available_at=当月第1交易日收盘后；第2日写权、T2 开盘；截断检查 3 切点 max_abs_diff=0 → **PASS** ✅ |
| H4 重叠 | ρ_excess vs capacity_adv −0.326；其余 <0.5；逐日 Jaccard max 0.25（vs earnings_event）<0.7 ✅ |
| H5 事后挑选 | 尝试 1 次；冻结前未读收益；平局规则已披露 ✅ |
| H6 宇宙/换手 | FULLA_V1（Leo 07:24 取消禁小盘，覆盖预注册「只中大盘」）；双边换手 6.64%/日 ≤20% ✅ |
| H7 反方 | 抢跑 / α 由少数月份驱动 — 已写可证伪条件 ✅ |

### 2.2 单叶（全A主，引用自检；年化主报 244）
| 项 | 值 |
|---|---|
| 毛 CAGR / MDD | 6.71% / −18.81% |
| 残差 α（去β） | −5.36%（2024 −8.10 / 2025 +3.70 / 2026 −10.91） |
| 净 CAGR（T+1，17.5bp） | 4.44%；毛超额 −5.44%；成本拖累 2.84%/年 → **不可交易** |
| Gate A（残差 α>0） | **不过** |

### 2.3 CMC → **CMC_FAIL**
| 项 | 全A（主） | 阈值 |
|---|---|---|
| ΔIC | −0.00006 | ≥ +0.003 |
| ΔICIR 全样本 / 滚252 | −0.021 / −0.005 | ≥ +0.05 |
| ΔCAGR 净 60万 / 100万 | **−1.28pp / −1.78pp** | ≥ +0.50pp |
| ρ vs B0 | 0.037 | ≤ 0.5 ✅ |
| MDD 恶化 | 两档 ≤1pp ✅；B1 MDD≤25% ✅ | |

### 2.4 衰减门 v1.1 → **DECAY_DOWNGRADE**
- 理由：`latest_alpha<0`（−11.3%）、`H2_net_cagr<=510300`
- 见 `output/ai_factory/leaf_reports/broker_gold_new_alla/decay_v1_1.json`

### 2.5 GATE_V3 本地（cap80+叶20 vs capacity_adv；T+1/净/244）→ **FAIL**
| 档 | 组合 CAGR / MDD | capacity_adv 单跑 | MDD≤25% | CAGR>cap |
|---|---|---|---|---|
| 60万 | 13.29% / −13.94% | 13.93% / −14.24% | ✅ | **否（−0.64pp）** |
| 100万 | 16.79% / −12.59% | 17.77% / −12.47% | ✅ | **否（−0.98pp）** |

另：decay≠KEEP；tradable=false → 四条件全过失败。mid_large 对照同向：13.31%/17.03% 均低于 cap。

## 3. 缺口 / 软注
1. **券商名归一**：脚本对 `broker` 做 NFKC+strip 去重，**未做别名合并**（如「中信证券」vs「中信证券股份有限公司」）→ ≥2 家计数可能虚高；记软缺口，不单独否决（本叶已因其他闸失败）。
2. 压舱均值 69%（全压舱 102 日），个股袖薄；小盘仅披露，全A 残差 α 劣于 mid_large（−5.4% vs −2.8%）。
3. broker_recommend 无逐条 available_at；按「月份第1交易日≤T」截断，已通过 lookahead。
4. 单叶 gross/残差 α 脚本内置用 252 系数；成本/净/CMC/GATE_V3 自检为 244 — 主报 244，结论一致。
5. 叶验收 v2 预注册正文仍写「只中大盘」；以 Leo 07:24 全A 为准（FULLA_V1）。

## 4. 裁定与下一步
- **研究级：WATCH / 终态 DONE_FAIL**（硬闸同构/ρ 过；可交易、衰减、Gate A/B、CMC、GATE_V3 均不过）。
- **Book-Smoke：SKIP** — 主 Agent 原 07:27 ET 曾批准进 X2，后因 CMC_FAIL / 衰减门 DOWNGRADE / GATE_V3 本地 FAIL **取消烟测、不派 Eng**；`re_smoke=false`。
- 不晋级；不纸面；不实盘；禁 GP；不重开同叶改参。
