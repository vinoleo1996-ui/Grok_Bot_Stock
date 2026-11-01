"""ALERTS 周末刷新后处理（契约 v1.1）：加 events[]（显式 severity）、人工复核说明、周报链接；写 EVENT_CALENDAR + history。研究级，live=false。"""
import json, sys
from datetime import datetime; from zoneinfo import ZoneInfo
sys.path.insert(0, "/workspace/QuantLab/research/intel"); import intel_run as IR
R = "/workspace/QuantLab/output/intel/"; H = R + "history/"
now = datetime.now(ZoneInfo("America/New_York")); TS = now.strftime("%Y%m%d_%H%M")
weekly = sys.argv[1] if len(sys.argv) > 1 else "WEEKLY_latest.md"
p = json.load(open(R + "ALERTS_latest.json"))
E = lambda event, t, sev, src, note, url: dict(event=event, time_et=t, severity=sev, source=src, note=note, url=url)
events = [
 # ---- 本周已发生（10-12~10-17）----
 E("台积电Q3已公布（超指引，Q4指引强）", "2026-10-15 02:00", "high", "TSMC 6-K / IR",
   "营收 US$46.72B（指引 44.6–45.8，超中值 +3.36%，前9季中位 +2.47%）；毛利率 66.4%（指引 65–67%）、营业利率 58.7%；Q4 指引 US$52.3–54.3B（中值环比 +14%）、毛利率 65–67%；2026 全年营收增速上调至约 44%（7月为“略高于40%”）；资本开支 2026 维持 US$60–64B；HPC 占 68%（环比 +22%）；AI 加速器 2024–29 CAGR 中至高 50%，CEO称“可能更高”；对2027消费端审慎。TSM ADR 周 -9.0%（行业去杠杆压过基本面）。", "https://www.sec.gov/Archives/edgar/data/1046179/000104617926000726/a3q26e_withguidancexfinal.htm"),
 E("美国9月PPI已公布（大幅超预期）", "2026-10-15 08:30", "high", "BLS",
   "终端需求 +1.3% m/m（预期 +0.6%，Dow Jones），同比 6.3%（预期5.5%）；核心（除食品能源）+0.7%（预期 +0.3%）、同比 5.0%；除食品能源贸易 +0.5%；能源 +10.8%、汽油 +20.3%。", "https://www.bls.gov/news.release/archives/ppi_10152026.htm"),
 E("美国9月零售销售已公布", "2026-10-15 08:30", "watch", "U.S. Census Bureau",
   "+0.8% m/m（预期 +0.4%，WSJ），8月上修至 +1.3%；除汽车与加油站 +0.25%（8月约 +1.1%）→ 名义强、实际在油价挤压下放缓。", "https://www.census.gov/retail/sales.html"),
 E("褐皮书（10-14）已发布", "2026-10-14 14:00", "watch", "Federal Reserve",
   "3个区价格“强劲”、8个“温和”，4个区价格上涨加快；油价渗透所有区；就业基本持平，5个区称因AI提效放缓招聘。Bespoke：通胀相关词频创纪录（CNBC 转述）。", "https://www.federalreserve.gov/monetarypolicy/beigebook202610-summary.htm"),
 E("Warsh IMF 对谈（无前瞻指引）", "2026-10-15 23:30", "watch", "CNBC/Bloomberg",
   "“不预判会议”“不再做前瞻指引”；称全球“同步紧缩、没有搭便车者”。市场解读为10月按兵不动：CME FedWatch 10-28 加息概率 ≈34%（10-15）→ ≈15–16%（10-16）；12月加息约 89%。高盛预期12月最后一次加息。", "https://www.cnbc.com/2026/10/16/feds-warsh-says-ai-development-path-will-be-very-bumpy-.html"),
 E("费城半导体8连跌（2008年来最长）", "2026-10-16 16:00", "high", "Yahoo/Investing.com",
   "SOX 10-16 -3.83% 至 11137.29，周 -11.4%；AMD -13%、MU -14.6%、LRCX -17.2%、INTC -14.2%（周）；驱动：AI 融资成本（Broadcom/Intel CEO 10-12 警示）、利率、长鑫存储技术突破引发的存储供给担忧。A股周五收盘早于此，周一开盘承接。", "https://www.investing.com/news/stock-market-news/chip-index-sox-posts-longest-losing-streak-since-2008-as-ai-worries-deepen-4955401"),
 E("霍尔木兹海峡袭船升级，Brent 触及 $110", "2026-10-17", "high", "Al Jazeera/CNBC",
   "UKMTO：截至10-16一周至少12艘船遇袭；10-17 又有油轮遭RPG袭击、IRGC称超级油轮触雷起火（CENTCOM 称已清雷）。WTI 10-16 收 $101.41（周 +10.4%），Brent $109.86。美方报道称大选（11-03）后可能升级。", "https://www.aljazeera.com/news/2026/10/17/us-and-iran-both-claim-control-of-strait-of-hormuz-amid-attacks-on-vessels"),
 E("中国拟修订禁止/限制出口技术目录（AI/生物医药/光伏 40项）", "2026-10-16", "watch", "商务部 科技部公告2026年第48号",
   "新增 23 项 AI、5 项生物医药、12 项光伏技术（14禁止/26限制），征求意见至 11-15，即日起对相关技术出口实施临时登记。属中国自身技术出口管制，非对华制裁；对A股主要影响为光伏/AI 企业海外技术授权与出海项目合规成本。", "https://www.mofcom.gov.cn/zcfb/blgg/art/2026/art_1666fcaa24424766afe0683498ff0908.html"),
 # ---- 下周及以后 ----
 E("中国Q3 GDP + 9月经济数据", "2026-10-18 22:00", "high", "国家统计局（北京时间10-19 10:00）",
   "周一A股盘中公布；Reuters 调查预期Q3增速回升（具体数值未获取）。", "http://caifang.china.com.cn/2026-10/15/content_43498091.htm"),
 E("10月LPR报价", "2026-10-19 21:15", "watch", "中国人民银行（北京时间10-20 09:15）", "9-30 央行已下调 PSL 利率至 1.5%、扩大再贷款额度；LPR 是否跟进未知。", "https://english.www.gov.cn/news/202609/30/content_WS6abcbd63c6d00ca5f9a0d8a5.html"),
 E("美国9月新屋开工/营建许可", "2026-10-20 08:30", "info", "U.S. Census Bureau", "", "https://www.census.gov/construction/nrc/index.html"),
 E("Netflix Q3财报", "2026-10-20 16:01", "watch", "Netflix IR", "公司自家指引 EPS $0.82、营收 $12.86B（与共识一致）。映射：传媒。", "https://www.stocktitan.net/articles/earnings-calendar-week-of-october-19-2026"),
 E("Meta Q3财报（资本开支指引）", "2026-10-21 16:30", "high", "Meta IR",
   "2026 capex 指引 $130–145B；若上调/维持 → 光模块/服务器链情绪修复；若下调 → AI 算力链再承压。共识 EPS $6.35。", "https://www.stocktitan.net/articles/earnings-calendar-week-of-october-19-2026"),
 E("Lam Research Q3财报", "2026-10-21 17:00", "high", "Lam IR", "周 -17.2%，WFE 景气与中国区收入占比是A股半导体设备映射关键。共识 EPS $2.17。", "https://www.stocktitan.net/articles/earnings-calendar-week-of-october-19-2026"),
 E("德州仪器 / Tesla / IBM / SAP Q3财报", "2026-10-21 16:30", "watch", "公司IR",
   "TXN（模拟/工业库存周期，共识 $2.39）、TSLA（交付 48.65 万辆已知，共识 $0.21）、IBM、SAP。", "https://www.stocktitan.net/articles/earnings-calendar-week-of-october-19-2026"),
 E("美国初请失业金", "2026-10-22 08:30", "info", "U.S. DOL", "", "https://www.dol.gov/ui/data.pdf"),
 E("西部数据 Q3财报", "2026-10-22 16:30", "watch", "WDC IR", "存储景气（共识 EPS $3.97）。", "https://www.stocktitan.net/articles/earnings-calendar-week-of-october-19-2026"),
 E("密歇根大学消费者信心（终值）", "2026-10-23 10:00", "watch", "University of Michigan", "关注通胀预期分项。", "https://www.sca.isr.umich.edu/"),
 E("FOMC决议", "2026-10-28 14:00", "high", "Federal Reserve",
   "10-27~28，无SEP。CME FedWatch（10-16）：维持 ≈84–85%，加息25bp ≈15–16%；12月加息 ≈89%。联储静默期按惯例自会前第二个周六（10-17）开始。", "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"),
 E("SK hynix Q3财报", "2026-10-28", "high", "SK hynix（日期据 Nasdaq/媒体日历）", "本周跌 >11%（10-15 单日 -11.06%），存储周期与HBM指引。", "https://www.stocktitan.net/articles/earnings-calendar-week-of-october-19-2026"),
 E("美国9月PCE", "2026-10-29 08:30", "high", "BEA", "CPI/PPI 双热后的核心 PCE 映射。", "https://www.bea.gov/news/schedule"),
 E("Intel Q3财报", "2026-10-29 16:00", "watch", "Intel IR", "", "https://www.stocktitan.net/articles/earnings-calendar-week-of-october-19-2026"),
 E("美国中期选举", "2026-11-03", "watch", "—", "伊朗战事可能在选后升级（媒体报道）。", "https://www.aljazeera.com/news/2026/10/17/us-and-iran-both-claim-control-of-strait-of-hormuz-amid-attacks-on-vessels"),
]
p["events"] = events
p["generated_et"] = now.strftime("%Y-%m-%d %H:%M")
p["trigger"] = ["周末恢复刷新：全队10-15起停摆，ALERTS 自 10-14 09:35 后首次更新"]
# 人工复核：日韩 10-16 收盘早于美股周五大跌，其上涨不构成对冲 → 电子按纳指/费半重算
review = []
for a in p["alerts"]:
    if a["industry"] == "电子":
        a.update(call="偏空", strength="强", score=-6, note="（人工复核：剔除日经/KOSPI 10-16 上涨——其收盘早于美股周五大跌，不构成对冲；按纳指-2.15%/费半-3.83%重算）",
                 manual_override=True)
        review.append("电子：机器得分 -2（中）→ 人工 -6（强）")
    a.setdefault("invalidation", []).append("历史研究：纳指≤-2%次日A股科技弱势几乎全在开盘跳空，开盘后不再跑输——开盘跳空后不追空（INTEL C1 成本检验）")
IR.C.apply_alert_severity(p["alerts"])
for a in p["alerts"]:
    if a.get("manual_override"): a["severity_note"] = "explicit, manual review"
p["manual_review"] = review + [
    "新闻分类器误判提示：①“China proposes export controls on 23 AI technologies”为中国自身技术出口管制（商务部 科技部 2026 第48号），并非对华出口管制，不应按“实体清单/对华管制”利空计；②“Trump waives 100% tariffs on Russian oil buyers India and China”为解除关税威胁（偏利好），被关税规则误计为利空；③“Taiwan reportedly plans export controls on AI servers and chips”仅单一来源，未核实。",
    "计算机/通信 high 由纳指、费半两项“强”冲击单独即可触发（得分 -4 以上），不依赖上述新闻。"]
p["weekly_report"] = "output/intel/" + weekly
p["live"] = False; p["promotion_approved"] = False
md = IR.render_md(p)
md += "\n## 人工复核\n\n" + "\n".join("- " + x for x in p["manual_review"]) + "\n"
md += "\n## 事件（events[]，契约 v1.1 显式 severity；market 级仅展示）\n\n| 时间 ET | 事件 | 等级 | 来源 | 说明 |\n|---|---|---|---|---|\n"
md += "\n".join(f"| {e['time_et']} | {e['event']} | {e['severity']} | {e['source']} | {e['note'][:140]} |" for e in events) + "\n"
md += f"\n周报：{p['weekly_report']}；研究级，live=false，不下单、不改权重。\n"
json.dump(p, open(R + "ALERTS_latest.json", "w"), ensure_ascii=False, indent=1); open(R + "ALERTS_latest.md", "w").write(md)
json.dump(p, open(H + f"ALERTS_{TS}.json", "w"), ensure_ascii=False, indent=1); open(H + f"ALERTS_{TS}.md", "w").write(md)
cal = {"schema": "quantlab.intel.event_calendar.v1", "updated_et": p["generated_et"], "live": False, "events": events}
json.dump(cal, open(R + "EVENT_CALENDAR_latest.json", "w"), ensure_ascii=False, indent=1); json.dump(cal, open(H + f"EVENT_CALENDAR_{TS}.json", "w"), ensure_ascii=False, indent=1)
st = json.load(open(R + "intraday_state.json")); st["written_et"] = p["generated_et"]; json.dump(st, open(R + "intraday_state.json", "w"), ensure_ascii=False)
from collections import Counter
print(TS, "alerts", Counter(a["severity"] for a in p["alerts"]), "events", Counter(e["severity"] for e in events))
