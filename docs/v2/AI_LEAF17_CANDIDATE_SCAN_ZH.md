# 叶17 候选扫描（2026-10-14 2026-10-14 07:56:09 ET）
研究级；live=false；promotion=false；禁 GP/高杠杆；**未读任何价格/收益**。
派单：主 Agent 转发 Leo 07:50 ET 核心指令（挖全A超额；新叶同时冻 FULLA+HI_LIQ；密封窗+X2、60万/100万）。

## 已避开（台账 1–16 / 穷尽表）
capacity_adv、earnings_event、insider_increase、equity_incentive、report_rc_allup、analyst_recoverage、stk_surv、insurer_surv、tp_rerate、broker_gold_new；以及已灭/WATCH 的 buyback/block/unlock/interim_div/北向/两融/量价/龙虎榜/解禁/质押等。

## 盘上 PIT 数据速览
| 源 | 窗 | 备注 |
|---|---|---|
| announcements_classified_pit + _post202406 | 2018-01→2026-10 | 密封段与 X2 分段文件，需合并 |
| report_rc_2018plus | 满窗 | 卖方；叶11/12/15/16 已用 |
| stk_surv_2018plus | 满窗 | 叶13/14 已用 |
| financials_pit_tushare（含 grossprofit_margin） | 满窗 | 与 accrual/OCF 同族风险 |
| forecast_1y / express_1y / holder_trade_1y | 近1年 | 不满窗 |
| fund_portfolio | 未满窗 | Data 在拉 |
| Intel event_study | 行业级宏观溢出 | 非个股选股主线 |

## 三候选（只计数、未读收益）

### 1) major_contract_growth（成长行业重大合同/中标）
- **谁付钱**：订单/中标公告后，对「订单→未来营收」反应慢、按旧营收预期定价的资金。
- **数据**：合并两份公告分类表；标题匹配「重大合同/中标/签订…合同」等，剔除框架/担保/借款等；**仅成长 SW L1**（电子/计算机/通信/医药生物/电力设备/机械设备/汽车/国防军工/传媒/家用电器）；同票冷却 40 日、每年最多 4 次（压掉建筑央企常驻中标）。
- **计数**（PIT 入池）：FULLA 成长 395/137（密封∩掩码 72/52；X2 323/123）；HI_LIQ 成长 948/296（密封 661/242；X2 287/114）。行业以电力设备/计算机/机械/医药/通信为主，**不含建筑装饰**。
- **预期重合**：相对已有叶**低**（无合同/中标主叶；叶8 草稿因中大盘建筑央企扎堆未开）。与 earnings_event 时点可能偶发邻近，须报 Jaccard/ρ。
- **数据质量**：高（PIT available_at）；需合并密封/X2 两文件。

### 2) rating_upgrade_cluster（评级上调至买入档）
- **谁付钱**：对卖方评级上调反应慢的资金。
- **数据**：report_rc rating 分值上调至 ≥4（买入/推荐等），10 日内 ≥2 家，冷却 60 日。
- **计数**：FULLA 1347/682（密封 481/380；X2 866/533）；HI_LIQ 4041/1063。
- **预期重合**：**高**（与 report_rc_allup / tp_rerate / analyst_recoverage / broker_gold_new 同属卖方）。
- **数据质量**：高，但同构风险大。

### 3) pharma_tech_milestone（医药/科技里程碑公告）
- **谁付钱**：对临床/获批/器械注册/发明专利等硬里程碑反应慢的资金。
- **数据**：公告标题关键词；冷却 60 日。
- **计数**：HI_LIQ 成长 1695/219（密封 993/158；X2 702/154）；FULLA 1010/172。但 **医药生物约占 90%+**，易退化成单行业押注；关键词噪声。
- **预期重合**：机制层低；行业层极高集中。

## 选定：#1 major_contract_growth
**理由（数据质量 + 低预期重合）**：
1. 与台账 1–16 机制正交性最好（合同/中标未曾作为主叶跑通）。
2. 成长行业过滤 + 年 capped 冷却，直接修复叶8「建筑央企常驻中标」失败模式，覆盖电新/计算机/机械/医药/通信。
3. 两宇宙 X2 计数均过闸；HI_LIQ 密封满窗；FULLA 密封仅掩码重叠段（掩码自 2023-09），须在预注册披露。
4. #2 卖方同构过高；#3 单行业过浓。

下一步：写 who_pays 预注册（FULLA+HI_LIQ 双口径）→ 冻结阈值/硬闸 → 正式计数闸 →（过则）X2+密封权重与自检。不自跑 Book-Smoke。

## Leo 07:56 ET 范式（扫描后、读收益前）
已写入预注册修订附录：池内算因子；大盘/中小盘/小微分域子模型汇总 α；主交付 α 向量（非 Top-N）。写入时刻 2026-10-14 07:57:19 ET。

## Leo 07:58 ET 因子工艺（读收益前）
已写入预注册修订附录二：分域标定、慢α/快gate分离、行业+市值残差、白名单+池内轮动。短名单复判仍选 major_contract_growth。写入 2026-10-14 07:58:58 ET。
