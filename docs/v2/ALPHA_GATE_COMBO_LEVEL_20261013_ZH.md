# Alpha 烟测派发门改为组合层面（2026-10-13）

依据：Leo 2026-10-13 22:45 ET 在 Alpha 聊天亲口确认「派发门改为组合层面优于 capacity_adv」（New Bot 22:44 ET 同步转达）。

## 新规则（即日起替代单叶 12% 门）
- 主干：capacity_adv（PAPER_ACTIVE_CONFIRMED）。
- 卫星叶派发 Book-Smoke 条件：硬闸全过 + 与主干残差相关低 + 本地组合诊断显示有增益；单叶 CAGR<12% 也可派。
- 通过标准：叠加后组合在 60万 与 100万 两档，CAGR 与 MDD 均优于 capacity_adv 单跑，且 MDD 不深于 −25%。
- 一次烟测，不重烟。

## 不变红线
禁 GP / 小盘 / 高杠杆；promotion_approved=false；live=false；handoff=NO。

## 追溯
叶7/8/9 组合诊断均未胜过主干 → 维持 WATCH，不派烟。
