"""ALPHA_LEAF_ACCEPT_V2 pipeline (AI side): HC -> single-leaf -> CMC -> decay gate -> GATE_V3 -> (Eng X2).
Writes output/ai_factory/leaf_reports/<leaf>/selfcheck_v2.json with blocks hc, single_leaf, cmc, decay, gate_v3, factor,
lookahead. AI fills data only; verdicts (cmc_verdict/hc_verdict) are Alpha's. Thresholds are NOT applied here, except
reporting threshold comparisons as 'flags_vs_prereg' for convenience (no verdict).
Usage: python3 research/leaf_accept_v2_pipeline.py <leaf> [...]"""
from __future__ import annotations
import sys, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
RPT = ROOT / "output/ai_factory/leaf_reports"
HC = {
 "report_rc_allup": dict(
   H1="定期报告披露后 5 日内 ≥3 家卖方一致上调当年 np → 卖方信息扩散完成而买方按旧一致预期定价 → 60 日内价格补涨；收益来自买方对卖方修正的反应不足（行为）。",
   H2="付钱方：按旧一致预期定价、反应迟缓的资金；持续性来自卖方修正到买方仓位调整的时滞；容量：中大盘、日均 7.8 名×4%，压舱 69%。",
   H3="report_rc available_at=report_date 次一交易日 09:00；触发=disclosure_date actual_date（当日收盘后）；窗口结束后 T1 次日 T2 入场；复权价 adj_price；池 mid_large PIT top300（锚 2024-06-28，2024H1 有幸存偏差）+ 入场日 PIT 成员检查。截断前视检查见 lookahead 块。",
   H4="见 single_leaf.rho 与 cmc：ρ_resid vs capacity_adv 0.038、earnings_event 0.105、insider 0.116；Jaccard max vs capacity_adv 0.111、earnings_event 0.167。",
   H5="尝试 1 次（单一冻结规则，阈值沿用国信 3 家/5 日/全部上调）；草稿阶段看过 2018–2021 封存窗口计数（未看收益）；未在冻结前看 X2 收益。GATE_V3 事后发现声明见 GATE_V3 预注册。",
   H6="mid_large PIT top300；双边换手 2.09%/日。",
   H7="①卖方上调多发生在股价已涨后，事件收益可能只是动量延续，2024 残差 α 为负即为迹象；可证伪：若剔除事件前 20 日超额前 30% 后 α≤0 则机制不成立。②业绩预告/快报触发缺失、机构名未归一，事件集可能偏向大券商覆盖的大票；可证伪：机构名归一后事件数变化 >20% 且 α 方向翻转。"),
 "analyst_recoverage": dict(
   H1="同一券商断档 ≥6 个月后重新覆盖 → 冷门票基本面拐点 → 后续关注与重估；收益来自注意力回归（行为）。",
   H2="付钱方：忽视冷门票、只跟热门覆盖名单的资金；持续性弱（事件极密，几乎全池）；容量充足但换手 63%/日。",
   H3="report_rc available_at=report_date 次一交易日 09:00；T1 次日 T2 入场；复权价；池同叶11。截断前视检查见 lookahead 块。",
   H4="ρ_resid vs capacity_adv 0.043、earnings_event 0.268、report_rc_allup 0.095、equity_incentive 0.466；Jaccard max 0.216。",
   H5="尝试 1 次；计数前写草稿，计数后冻结（规则未改）；未看 X2 收益。",
   H6="mid_large；**双边换手 63.3%/日 > 20%**（不满足）。",
   H7="①事件定义过宽（券商换分析师即触发），信号接近随机轮换；可证伪：把门槛提到 ≥2 家同时重新覆盖后事件数应降 >80% 且 α 不升即机制无效。②高换手吞噬全部毛超额；可证伪：成本 17.5bp 下净 CAGR 已为负。"),
 "stk_surv": dict(
   H1="断档 ≥1 年后重新被机构调研 → 机构研究重新进入 → 后续关注与建仓；收益来自建仓前的价格压力（行为/流动性）。",
   H2="付钱方：机构建仓前卖出筹码的对手盘；持续性受调研披露滞后（L=25）侵蚀；容量：日均 5.7 名，压舱 77%。",
   H3="stk_surv available_at=surv_date+25 交易日 09:00（Data p95；约 5% 事件实际披露晚于 L，存在残余前视风险）；反转过滤用复权价截至 T2 前一日；池同上。截断检查见 lookahead 块。",
   H4="ρ_resid vs capacity_adv 0.396、earnings_event −0.028、report_rc_allup 0.117、insider 0.354；Jaccard max 0.30（block_trade）。",
   H5="尝试：3 个变体计数、1 个跑收益；主变体选取规则写于看过计数之后、读收益之前（已披露）；阈值上浮条款不触发（≤3 次）。",
   H6="mid_large；双边换手 1.52%/日。",
   H7="①披露滞后 25 日后，机构建仓多已完成，可交易窗口内无价格压力；可证伪：L 改为 p50 时 α 应显著更高，否则机制不在滞后内。②调研本身追涨（反面证据），反转过滤剔除 30.6% 仍残留；可证伪：被剔除事件的后续超额若高于保留事件，则过滤方向错误。"),
 "insurer_surv": dict(
   H1="同日 ≥3 家保险机构集中调研 → 长久期配置资金慢速建仓 → 建仓期价格压力；收益来自配置型资金流（流动性）。",
   H2="付钱方：建仓窗口内的短线卖方与反应迟缓资金；持续性依赖保险资金配置节奏（2025 单年贡献全部 α，持续性存疑）；容量：日均 10.2 名，压舱 59%。",
   H3="stk_surv available_at=surv_date+25 交易日 09:00（同 stk_surv，p95 残余风险）；机构类型按 org_type 白名单；复权价；池同上。截断检查见 lookahead 块。",
   H4="ρ_resid vs capacity_adv −0.342、stk_surv 0.072、earnings_event 0.426、report_rc_allup 0.089、insider −0.010；Jaccard max 0.25。",
   H5="尝试 1 次；候选筛选时已看过粗计数（156/66，已披露）；未看收益；分类口径冻结时放宽（另含综合/再保险/集团）。",
   H6="mid_large；双边换手 2.27%/日。",
   H7="①α 全部来自 2025（保险权益配置政策年），2024/2026 为负，属政策驱动而非可持续行为；可证伪：2027 前向残差 α ≤0。②与 earnings_event ρ 0.426，保险调研多在财报后，可能是财报事件的换皮；可证伪：剔除 earnings_event 窗内事件后 α 应保持 >0。"),
 "tp_rerate": dict(
   H1="10 个交易日内 ≥3 家卖方把目标价较各自上一次上调 ≥20% → 卖方集体重定估值锚 → 持有者按旧锚定价、反应慢 → 60 日内补涨；收益来自估值锚调整时滞（行为），不看 np。",
   H2="付钱方：按旧估值锚定价、对卖方重定估值反应慢的持有者；冷却 60 日；容量：中大盘、日均 6.6 名×4%，压舱 73%。",
   H3="report_rc available_at=report_date 次一交易日 09:00；目标价=max_price/min_price 均值（report_rc 的 tp 字段实为利润总额，已在预注册更正）；T1 写权重、次日开盘成交；反转过滤用截至 d 的复权收盘；池 mid_large PIT top300 + 入场日 PIT 成员检查。截断检查见 lookahead 块。",
   H4="ρ_resid vs capacity_adv 0.016、report_rc_allup 0.323、earnings_event 0.167、analyst_recoverage 0.187；逐日 Jaccard max 0.25（report_rc_allup）。",
   H5="尝试 1 次；预注册写于计数前（含反转过滤 80 分位与目标价字段更正），计数后冻结未改；冻结前未读收益。",
   H6="mid_large；单边换手均值 0.86%/日（双边约 1.7%）。",
   H7="①目标价上调多跟随股价上涨，反转过滤剔除 52% 事件后剩余事件 α≈0，说明信号主要是动量尾部；可证伪：被剔除事件的后续超额若显著高于保留事件则过滤方向错误。②机构名未归一，同一券商多名称可能虚增“家数”；可证伪：归一后事件数变化 >20% 且 α 方向翻转。"),
}


HC["broker_gold_new_alla"] = dict(
   H1="同月 ≥2 家券商新进金股 → 卖方新增共识推荐经销售渠道传导 → 月初集中买盘；收益来自推荐带来的资金流（行为/流动性）。",
   H2="付钱方：不跟踪卖方月度推荐、月初被动卖出的资金；月度全换仓；容量：全A池，日均约 7.8 名×4%。",
   H3="broker_recommend 按月给出，无精确发布时刻；保守 available_at=当月第1个交易日收盘后，第2个交易日写权重、T2(第3个交易日)开盘成交；复权价；池为 T2 的全A可交易 mask。截断检查见 lookahead 块。",
   H4="见 run_meta rho_resid_vs 与逐日 Jaccard（全部 <0.5 / <0.7）。",
   H5="尝试 1 次；预注册 06:51:36 ET 冻结、全A补充 07:25:11 ET 冻结，计数后未改；冻结前未读收益；同名事件多于 20 时按券商家数降序、代码升序取前 20（预注册未写明的实现细节，已披露）。",
   H6="全A（主口径，含小盘，小盘仅披露）。",
   H7="①金股多为券商已看好且已上涨的票，月初买盘可能已在发布前被抢跑；可证伪：T2 入场后 5 日超额 ≤0。②事件集中于 7/12 月，α 可能由少数月份驱动；可证伪：剔除最大两个月后 α 方向翻转。")
HC["broker_gold_new"] = dict(HC["broker_gold_new_alla"], H2="同上；池为 mid_large PIT top300（对照口径）。", H3=HC["broker_gold_new_alla"]["H3"].replace("全A可交易 mask", "mid_large top300 PIT 名单"), H6="mid_large（对照口径）。")


def run(leaf: str) -> dict:
    import research.leaf_selfcheck_v3 as V3
    import research.alpha_combo_marginal as C
    o = RPT / leaf; o.mkdir(parents=True, exist_ok=True)
    meta = json.load(open(V3.mfile(leaf))); v3 = json.load(open(o / "selfcheck_v3.json"))
    la = json.load(open(o / "lookahead_check.json")) if (o / "lookahead_check.json").exists() else {"status": "PENDING"}
    s = meta["selfcheck"]
    single = dict(weights=v3["weights"], gross_cagr=s["leaf_cagr_gross"], mdd=s["mdd_leaf"], resid_alpha=s["alpha_ann_leaf"],
                  by_year={y: v["alpha_ann"] for y, v in s["by_year"].items()},
                  rho={k: (v if isinstance(v, float) else v["rho"]) for k, v in s.get("rho_resid_vs", {}).items()},
                  mean_ballast=meta.get("mean_ballast"), mean_names=meta.get("mean_names"))
    cm = C.cmc(leaf); cm.pop("definition_notes", None)
    fl = dict(d_ic_ge_0_003=cm["d_ic"] >= 0.003, d_icir_full_ge_0_05=cm["d_icir_full"] >= 0.05,
              d_icir_roll_ge_0_05=(cm["d_icir_roll252_median"] or -9) >= 0.05,
              d_cagr_ge_0_5pp={t: v["d_cagr_net"] >= 0.005 for t, v in cm["tiers"].items()},
              mdd_worsen_le_1pp={t: v["mdd_worsening_pp"] <= 1.0 for t, v in cm["tiers"].items()},
              b1_mdd_le_25={t: v["B1_mdd"] >= -0.25 for t, v in cm["tiers"].items()},
              rho_le_0_5=cm["rho_leaf_resid_vs_B0"] <= 0.5, neg_years_le_1={t: v["n_neg_years"] <= 1 for t, v in cm["tiers"].items()})
    cm["flags_vs_prereg"] = fl; cm["note"] = "flags 仅为阈值对照，非判定；cmc_verdict 由 Alpha 写入 output/loop/alpha_labels.json"
    res = dict(leaf=leaf, prereg="docs/v2/ALPHA_LEAF_ACCEPT_V2_PREREG_ZH.md", order=["hc", "single_leaf", "cmc", "decay", "gate_v3", "eng_x2"],
               hc=HC[leaf], hc_note="AI 填写原文，不判定；hc_verdict 由 Alpha 裁定", single_leaf=single, cmc=cm,
               decay=v3["decay"], cost=v3["cost"], gate_v3=v3["gate_v3"], factor=v3["factor"], marginal_v3=v3["marginal"], lookahead=la,
               promotion_approved=False, live=False)
    (o / "selfcheck_v2.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float))
    return res


if __name__ == "__main__":
    for lf in sys.argv[1:]:
        r = run(lf); c = r["cmc"]
        print(lf, round(c["d_ic"], 4), round(c["d_icir_full"], 3), c["d_icir_roll252_median"], round(c["rho_leaf_resid_vs_B0"], 3),
              {t: (round(v["d_cagr_net"] * 100, 2), round(v["mdd_worsening_pp"], 2), round(v["B1_mdd"], 4), v["n_neg_years"], {y: round(x * 100, 2) for y, x in v["yearly_d_return_net"].items()}) for t, v in c["tiers"].items()})
