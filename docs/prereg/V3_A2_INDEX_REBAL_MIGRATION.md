# V3-A2 预注册：沪深300 ↔ 中证500 调样迁移（V3_A2_INDEX_REBAL_MIGRATION）
登记：2026-10-11（ET），先于任何密封窗计算。研究级，`promotion_approved=false`。不碰小盘，不改 MAINBOOK。
依据：/workspace/QuantLab-V3_FIRST_PRINCIPLES_ZH.md §4 A2、§8 Alpha 第 2 条。

## 1. 预设试验（若数据可行）
- A2_T1 MIGRATE_IN_300：500→300 迁入股，公告日次日开盘买入、生效日收盘卖出，超额相对 300+500 等权。
- A2_T2 MIGRATE_OUT_300：300→500 迁出股，同窗口超额（预测为负；只做多约束下仅作回避，不做空）。
另报：调样预测准确率；超额对「净被动需求/ADV」的单调性；生效日后 5/20 日回吐。成本口径同 V3_A1。

## 2. 数据核查与可运行性判定（预先写定）
- 成分：index_weight_csi300_500_1000.parquet 为月末快照（2018-01→2026-09），index_member_events.parquet 的 ann_date 字段若全空，则**没有真实公告日**；生效日只有区间 (prev_snapshot, snapshot_date]。
- 被动跟踪规模（ETF 份额）：§1 标为缺口 → 「需求/成交额」单调性无法计算。
- 判定：若 ann_date 缺失，不得用快照日或生效日倒推入场（快照在生效之后，用它确定名单即前视）。代用方案「按中证规则用日均市值自行预测调样名单」需单独预注册并实现排名规则，本轮不做。故 **A2 在 ann_date 缺失时标记 blocked_data，不跑密封窗、不计入 BY 实际检验数**。
- 解锁条件：Data 提供中证指数调样公告日（或 cninfo/中证官网公告原文）与 ETF 份额。

## 3. 修订 A（2026-10-11 12:25 ET 登记，先于任何密封窗计算；原哈希 f9504974…）
数据核查（本修订前）：
- Data 交付 data/v2/index_members/csi_review_calendar.parquet：17 个定期调样（2018-06→2026-06），ann_date 与 effective_date 全非空；其中部分为 rule_inferred（公告=前月最后周五，生效=第 2 个周五收盘后首个交易日），已在报告逐期标注来源。
- index_member_events.parquet 的 ann_date 已回填：5734/5840 非空；106 行为非定期临时调整，保持空 → 剔除，不倒推。
- ETF 每日份额仍缺（仅有 510300 价格/成交额，无 fund_share）→ 解锁条件部分满足。
修订内容（仅以下几点，其余不变）：
1. 只跑不依赖 ETF 份额的两个已注册臂 A2_T1、A2_T2；每臂密封窗只跑一次。
2. 「净被动需求/ADV」单调性降级为**仅报告**的代理：demand_proxy = 公告日前一交易日流通市值 / 公告前 20 日日均成交额（ETF AUM 不可得，权重×AUM 无法计算）；分三分位报超额，不作检验、不选型。
3. 时间口径写死：available_at = ann_date 当日 20:00（北京时间）；入场 = ann_date 之后**第一个交易日开盘**（复权开盘价）；出场 = effective_date 当日收盘（按原文 §1）；effective_date 前一交易日收盘出场只作敏感性报告。
4. 迁移定义：同一 review 内 000905→000300（T1）与 000300→000905（T2）；对照 = 入场日前最新月末快照的 300∪500 等权，同窗口开→收。只做多：T2 只作回避证据，增量 = −超额。
5. 成本：flat 25/50/100bp 单边×2；sqrt 冲击（quantlab.platform.execution.sqrt_impact_cost，k=1，sigma=前 20 日日收益 std，ADV=前 20 日成交额）在资金 5e7/2e8 按篮子等权分配，含佣金 2.5bp、卖出印花税。
6. 检验：以 review 为聚类单位（每期篮子均值）单侧 t（T1 H1>0；T2 H1 超额<0），flat25；BY 族 = A1 四臂 + A2 两臂（共 6）。通过：BY q<0.05 且 flat25、imp5e7 净超额同向为正（T2 为负）、分年方向一致；报 0.6 折。2024-06 起为确认窗，只报告。

## 4. 修订 B（2026-10-12 02:25 ET 登记，先于任何份额需求计算；原修订 A 哈希 9703a178…）
数据核查（本修订前）：
- QuantLab Data 交付 data/v2/etf/share_pit/etf_share_flow_pit_all.parquet：1829 只 ETF，1,474,906 行，2018-01-02→2026-10-09；available_at = max(份额 T+1 09:00, 净值 available_at)，naive=Asia/Shanghai；研究级。
- IOPV 仍缺口（Data 注明：无日频历史；实时仅深市）。本修订不使用 IOPV。
- A2_T1 / A2_T2 密封窗已跑过一次且 FAIL；本修订**不重跑**密封假设检验、不新开密封 pass/fail、不重开 BY 族。

修订内容（仅解锁报告臂，其余不变）：
1. 将修订 A §2 降级的「净被动需求/ADV」代理，升级为**份额×权重需求**报告臂（仍仅报告、不作检验、不选型、不参数搜索）。
2. 跟踪 ETF 宇宙（写死，计算前）：
   - CSI300：etf_basic 中 category=宽基，且 name/benchmark 匹配纯「沪深300」指数跟踪（benchmark 含「沪深300指数」，排除 增强/联接/质量/价值/成长/红利/ESG/自由现金流/等权重/行业/主题 变体）；至少含 510300.SH、159919.SZ 等。
   - CSI500：同上，纯「中证500」/「中证小盘500」；至少含 510500.SH、159922.SZ 等。
   - 名单与每期可用 AUM 写入 output/alpha/V3_A2_ETF_SHARE_DEMAND/，不事后增删代码调结果。
3. AUM 口径：AUM_万元 = share_wan × unit_nav（与 flow_est_wan_yuan 一致）；取 available_at ≤ 该期公告 available_at（ann_date 当日 20:00 北京）的最新一行，**不前视**。
4. 需求定义（报告唯一公式，不调参）：
   - 权重：旧指数权重 = 入场日前最近月末快照；新指数权重 = 生效日及之后首个月末快照（实现权重；报告标注重量时点，非交易信号输入）。
   - T1（500→300）：Δpassive_万元 = (w300_new/100)·AUM300 − (w500_old/100)·AUM500；demand = Δpassive_万元·1e4 / ADV_20（元）。
   - T2（300→500）：Δpassive_万元 = (w500_new/100)·AUM500 − (w300_old/100)·AUM300；demand 同除 ADV_20。
   - ADV_20 复用密封 events.csv 的 adv_in（入场日口径，已 shift，不重算面板）。
5. 输出：按臂在密封窗（exit_rule=eff）对 demand 三分位，报各档 xs 均值与计数；并与 demand_proxy_terciles.csv（流通市值代理）对照。确认窗若成本低则同样只报告。
6. 明确边界：T1/T2 密封 FAIL 结论不变；不重开 BY；promotion_approved=false；不开密封；不启动 GP。
