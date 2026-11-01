"""Old (pre-fix full_d1_turn arm A) vs fixed arm A — 中文表. Research-only."""
import json, pathlib
R = pathlib.Path(__file__).resolve().parents[1] / "output/strategy_paper_costs"
old = json.load(open(R/"full_d1_turn/summary.json"))["arm_a_baseline_m01_ep"]
new_s = json.load(open(R/"full_d1_fixed_armA/summary.json")); new = new_s["arm_a_baseline_m01_ep"]
rows = [("累计收益","total_return",True),("CAGR","cagr",True),("夏普(rf=0)","sharpe_rf0",False),("最大回撤","max_drawdown",True),("年化波动","ann_vol",True)]
f = lambda v,p: f"{v*100:.2f}%" if p else f"{v:.3f}"
L = ["# Full D1 臂A 基线：修复前 vs 修复后（研究级，promotion_approved=false）","",
     "修复：持仓始终按收盘估值；涨跌停/停牌只限制成交，未成交单顺延到下一可交易日；收益序列用 close_to_close_returns。","",
     "| 指标 | 修复前 | 修复后 |","|---|---|---|"]
for n,k,p in rows: L.append(f"| {n} | {f(old['metrics_research_only'][k],p)} | {f(new['metrics_research_only'][k],p)} |")
L.append(f"| 交易成本(元) | {old['total_cost_cny']:.0f} | {new['total_cost_cny']:.0f} |")
L.append(f"| 成本/初始资金 | {old['total_cost_as_frac_of_capital']*100:.2f}% | {new['total_cost_as_frac_of_capital']*100:.2f}% |")
L += ["", f"顺延成交次数：{new_s.get('carry_over_fills',{}).get('arm_a')}；修复前所有 paper 输出已标 SUPERSEDED。"]
out = R/"full_d1_fixed_armA/COMPARE_OLD_VS_FIXED_ZH.md"; out.write_text("\n".join(L)+"\n", encoding="utf-8"); print("\n".join(L))
