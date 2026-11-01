# GATE_V3 新口径重判：叶11–15（2026-10-14，Alpha）

- 门：docs/v2/GATE_V3_MDD25_PREREG_ZH.md，**规则未改**。衰减门用 v1.1。
- 新口径：T+1 次日开盘成交、扣 17.5bp×换手的净收益、244 日年化；cap80+叶20，top-N 6/10，单名 ≤6%（引擎 research/leaf_selfcheck_common.py，AI 审计修复版）。基准是同口径的 capacity_adv 单跑，窗口 2024-01-04～2026-10-09。
- 胜率：月胜率（日胜率在 JSON 里）。capacity_adv 单跑：60万 13.93%/−14.24%/Calmar 0.98/月胜 55.9%；100万 17.77%/−12.47%/1.43/55.9%。
- 与 AI selfcheck_common_after_audit.json 方向一致；AI 版窗口按滚动β有效日截掉前约 60 日，所以绝对数偏低（capacity_adv 60万 13.27%）。

| 叶 | 60万 CAGR/MDD/Calmar/月胜 | 100万 CAGR/MDD/Calmar/月胜 | 胜过 capacity_adv 两档 | 衰减门 v1.1 | 换手/日 | 本地新口径 | 终判 |
|---|---|---|---|---|---|---|---|
| 11 report_rc_allup | 14.08%/-14.73%/0.96/58.8% | 18.96%/-12.64%/1.50/55.9% | 过/过 | KEEP | 2.09% | PASS | FAIL (Eng X2 终判绑定) |
| 12 analyst_recoverage | 6.09%/-17.61%/0.35/52.9% | 11.80%/-14.66%/0.81/44.1% | 不过/不过 | DECAY_DOWNGRADE | 63.29% | FAIL | FAIL |
| 13 stk_surv | 13.91%/-14.50%/0.96/55.9% | 17.88%/-12.73%/1.40/52.9% | 不过/过 | DECAY_DOWNGRADE | 1.52% | FAIL | FAIL |
| 14 insurer_surv | 14.16%/-14.77%/0.96/61.8% | 18.53%/-12.29%/1.51/52.9% | 过/过 | DECAY_DOWNGRADE | 2.27% | FAIL | FAIL |
| 15 tp_rerate | 13.85%/-14.40%/0.96/52.9% | 17.21%/-12.72%/1.35/52.9% | 不过/不过 | DECAY_DOWNGRADE | 1.72% | FAIL | FAIL |

## 翻转
- **无终判翻转**，五叶都是 FAIL。
- 叶11：本地新口径四条都过（60万 14.08% vs 13.93%，余量只有 0.15pp），但 Eng X2 终判 FAIL 有约束力，维持 WATCH/DONE_FAIL，不重烟。事后发现声明仍然有效。
- 叶14：CAGR 两档都过（旧口径也过），只因衰减门 DOWNGRADE 不过，结论不变。
- 叶13：60万 13.91% < 13.93%，衰减门也是 DOWNGRADE。叶12：换手 63%/日，三项都不过。叶15：自检已到（selfcheck_v3 + decay_v1_1），不是 PENDING；两档 CAGR 都低于基准，衰减门 DOWNGRADE。

## 标记
- tp 字段：report_rc 的 tp 是利润总额，不是目标价。查了叶代码和文档，**没有已验收的叶把 tp 当目标价**：叶15 用 max_price/min_price，叶11 用 np。
- 机构名未归一（≥N 家计数可能虚增）：叶11（≥3 org_name）、叶12（同机构重覆盖判断）、叶13（≥20 rece_org）、叶14（≥3 保险 rece_org）都已在记录里标出；叶15 已由 AI 归一复核，未虚增。

## 其他
- 叶14 正式记录：AI_G1G5_INSURER_SURV_WEIGHT_ACCEPT_ZH.md（WATCH，不派烟，CMC_FAIL，HC_REWRITE H3）。
- 叶15 还没有 ACCEPT 记录，标签暂未建；需要的话另行补记。
- 不跑 GP，不派 Book-Smoke；paper/promotion/live=false；未提交。数据：output/alpha/ALPHA_GATEV3_REJUDGE_NEWBASIS_20261014.json
