# 下一批正交叶候选（2026-10-14 ET；只用盘上数据、只计数、未读收益、未开叶）
池：mid_large PIT top300（锚 2024-06-28），排除 600519/002371。计数口径：全窗｜X2 相关期（≥2023-10）。已灭/已用：见 AI_LEAF_LEDGER_ZH.md 与 AI_LEAF_CANDIDATES_EXHAUSTED_ZH.md（龙虎榜、share_float、分红、disclosure_date、pledge、北向、两融、量价族、财报事件、调样、大宗、report_rc_allup、analyst_recoverage、stk_surv gap1y 等均排除）。

| # | 候选 | 谁付钱 | 数据源 | 粗计数 | 同构风险 |
|---|---|---|---|---|---|
| 1 | **tp_rerate**：10 日内 ≥3 家机构把目标价较各自上一条上调 ≥20%（不看 np），事件后 60 日冷却 | 按旧估值锚定价、对卖方估值重定反应慢的资金；与盈利上调不同，是估值/叙事重估 | data/v2/events/report_rc_2018plus.parquet（tp） | 969 条/271 只｜X2 477 条/220 只（2024:165/2025:158/2026:154） | **中高**：与 report_rc_allup 同源（卖方）；tp 上调常伴随股价已涨（追涨风险），需反转过滤与 ρ vs report_rc_allup、earnings_event 检验；事件较密 |
| 2 | **insurer_surv**：同日 ≥3 家保险资管/寿险机构调研 | 长线保险资金调研预示配置型建仓；付钱的是建仓前的短线卖方 | data/v2/events/stk_surv_2018plus.parquet（org_type） | 280 条/85 只｜X2 156 条/66 只（2024:46/2025:56/2026:45） | **中**：stk_surv 已有 gap1y（ρ vs capacity_adv 0.396），需核对与 stk_surv、capacity_adv（大市值偏好）的 Jaccard/ρ；保险偏好高股息大盘，可能与红利暴露同构 |
| 3 | **foreign_surv**：同日 ≥5 家境外机构（外资银行/英文名机构）调研 | 外资研究先行，内资跟随；付钱的是信息跟随慢的内资 | stk_surv（rece_org 名称 + org_type 识别，规则粗） | 178 条/55 只｜X2 100 条/41 只（2024:36/2025:24/2026:29） | **中**：北向族已灭（外资偏好重合）；机构名识别规则粗，计数闸边缘（X2 41 只 <50），大概率计数不过 |
| 4 | **post_report_surv**（stk_surv V2）：定期报告披露后 5 日内被调研 | 财报后路演解读加速信息扩散 | stk_surv + disclosure_date | 291 条/99 只｜X2 176 条/74 只 | **高**：与 earnings_event、report_rc_allup 同一时点；已在叶 13 预注册中列为非主变体 |
| 5 | coverage_expansion：30 日内 ≥3 家机构首次覆盖、此前覆盖 ≤3 家 | 冷门票被卖方集体发现 | report_rc | 51 条/50 只｜X2 2 条 | 计数闸必败（中大盘几乎都已被覆盖），不建议 |

## 建议
- 优先：**#2 insurer_surv**（谁付钱清晰、计数够、与已有卖方信号来源不同），其次 #1 tp_rerate（计数充足，但必须先写死对 report_rc_allup 的同构判据与反转过滤）。
- #3、#5 计数不足；#4 同构风险高。
- 外部待数：fund_portfolio（dark_horse_add 草稿已写）、broker_recommend（金股，盘上无，需 Data 拉）。
- 本文件不开任何叶；开叶需按流程先写 who_pays 草稿 → 计数闸 → 冻结。
