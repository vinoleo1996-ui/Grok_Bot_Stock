"""新闻分类器自测（python3 research/intel/test_news_classifier.py）。只测标题分类，不联网、不写 ALERTS。"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import intel_common as C

def themes(t): return [x[0] for x in C.classify_title(t)]

CASES = [
    # —— 2026-10-18 01:20 ET 新增：周末 RSS 原标题 ——
    ("China Export Controls: 40-Tech Hit List Explained [2026] - https://tec", ["中国自身出口管制"]),
    ("U.S. crude oil tops $100 as Iran escalates Hormuz attacks", ["原油/霍尔木兹"]),
    # —— 本周两条误判（10-16/10-17 RSS 原标题）——
    ("China proposes export controls on 23 AI technologies - TNGlobal", ["中国自身出口管制"]),
    ("Trump Waives 100 Tariffs on Russian Oil Buyers India and China Under Graham Act Two Days Before Deadline - LawStreet Journal", ["中美谈判缓和"]),
    # —— 中国作施动方 ——
    ("China Proposes New Export Controls on AI Models and Chip Technologies Amid US Rivalry", ["中国自身出口管制"]),
    ("China's Proposed AI Export Controls and New Temporary Export Registration Requirements: Initial Thoughts", ["中国自身出口管制"]),
    ("Beijing tightens export controls on battery technology", ["中国自身出口管制"]),
    ("China Reportedly Planning AI Export Controls, Citing National Security - PCMag", ["中国自身出口管制"]),
    ("商务部 科技部就修订禁止出口限制出口技术目录征求意见 出口管制", ["中国自身出口管制"]),
    ("China expands export controls on rare earths", ["中国自身出口管制", "稀土/关键矿产"]),
    # —— 美方对华管制（应仍为利空）——
    ("US tightens export controls on China chips", ["出口管制/实体清单"]),
    ("Commerce adds 30 Chinese firms to Entity List", ["出口管制/实体清单"]),
    ("Biden administration weighs new chip curbs on China", ["出口管制/实体清单"]),
    ("New BIS rule expands semiconductor restrictions to China", ["出口管制/实体清单"]),
    # —— 美方管制的暂停/延期 ——
    ("US suspends BIS affiliates rule for another year as truce extended", ["中美谈判缓和"]),
    ("Washington delays export control rule on Chinese subsidiaries", ["中美谈判缓和"]),
    # —— 关税：加征 vs 暂停/豁免/撤回/延期 ——
    ("Trump threatens 100% tariffs on China", ["关税"]),
    ("US raises tariffs on Chinese EVs to 150%", ["关税"]),
    ("US pauses tariffs on Chinese goods for 90 days", ["中美谈判缓和"]),
    ("White House grants tariff exemptions for Chinese electronics", ["中美谈判缓和"]),
    ("Trump withdraws tariff threat against China", ["中美谈判缓和"]),
    ("US extends tariff truce with China to January", ["中美谈判缓和"]),
    ("US postpones China tariff hike", ["中美谈判缓和"]),
    ("Chinese toy and gift makers look to tariff cuts to boost US orders - The Star", ["中美谈判缓和"]),
    ("美国宣布暂停对中国商品加征关税", ["中美谈判缓和"]),
    ("美国对中国电动车加征关税", ["关税"]),
    # —— 混合：美方加关税 + 中方管制 ——
    ("Trump threatens tariffs on China after Beijing expands export controls on rare earths", ["中国自身出口管制", "关税", "稀土/关键矿产"]),
    ("Non-tariff barriers biggest hurdle in India-China trade: Sitharaman", []),
    # —— 无关 ——
    ("Nvidia shares rise on data center demand", []),
]

def main():
    bad = 0
    for title, exp in CASES:
        got = themes(title)
        ok = sorted(got) == sorted(exp)
        bad += not ok
        print(("PASS" if ok else "FAIL"), title[:80], "->", got, "" if ok else f"(期望 {exp})")
    # 计分方向检查：中国自身管制不计分；缓和为偏多
    assert C.classify_title("China proposes export controls on 23 AI technologies")[0][1] == {}
    assert all(v > 0 for v in C.classify_title("US pauses tariffs on Chinese goods")[0][1].values())
    print(f"\n{len(CASES) - bad}/{len(CASES)} passed")
    sys.exit(1 if bad else 0)

if __name__ == "__main__":
    main()
