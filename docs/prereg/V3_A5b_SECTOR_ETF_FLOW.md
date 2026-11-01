# V3-A5b 预注册（草案）：行业 ETF 份额资金流截面（V3_A5b_SECTOR_ETF_FLOW）
状态：**draft — exploration only; sealed requires Leo approval**。研究级，`promotion_approved=false`。不碰小盘个股，不改 MAINBOOK，不涉及 H3。与 A5（宽基择时）正交：本假设是**行业截面**资金流。
登记：2026-10-11 22:25 ET，先于任何该信号的计算。

## 1. 机制
行业/主题 ETF 的净申购反映机构与主题资金对该板块的直接配置。申购冲击 sticky（AP 创建、指数成分买入有摩擦），预测该行业 ETF 随后 5–20 日相对收益为正；赎回反向。付钱方：在资金流已兑现后才跟进的主题追逐者。
与 A7（价格相对动量）正交：A5b 用份额变化，不用收益。

## 2. 数据与 available_at
- data/v2/etf/share_pit/etf_share_flow_pit_industry_theme.parquet：479 只（439 行业+40 主题），2018-01-02→2026-10-09；flow_est = Δshare×NAV 估计（非真实申赎）。
- available_at：份额 T+1 09:00，净值 max(ann,trade)+23:59，合并取较晚 → **T+1 日终可得，T+2 开盘成交**。
- 映射：data/v2/etf/sw_l1_etf_map_pit_daily.parquet（每日每申万一级一条主 ETF）。缺 ETF 覆盖的行业：商贸零售、纺织服饰、综合、美容护理 —— 这些行业不进池。
- 无 IOPV。

## 3. 信号
对映射到的主 ETF：flow5 = Σ_{t−4..t} flow_est / AUM_{t−5}；zF = 截面 z-score（当日合格行业）。
合格：当日有份额与净值、AUM 可得、amt20 达中位数一半。
主仓位（T1）：多 zF 最高 3、空最低 3，各等权，美元中性。每周调仓，信号日 t → 持仓从 t+2 开盘起。

## 4. 试验（≤4 臂）
- A5b_T1_LS_FLOW：上述多空。
- A5b_T2_LONGONLY：只做多 top-3，相对合格行业等权超额。
- A5b_T3_DOSE：截面 IC(zF, fwd5/10/20) + 五分位（检验统计量）。
- A5b_T4_PLACEBO：(a) 收益平移 250 日；(b) 随机打乱行业标签 500 次。

## 5. 预测与失效
P1：IC(zF, fwd10) > 0。P2：T1 扣 5bp 年化 > 0 且 NW t≥2。P3：五分位 Q5−Q1 > 0。
失效：P1 反号；T1 净超额≤0；随机百分位 <80%。

## 6. 成本
ETF 单边 5bp（主）与 10bp。毛多/空各 ≤1.0。

## 7. 探索窗强信号门槛（全满足才建议密封）
探索窗 2024-06-03→最新。
1) 周频 IC 均值>0 且 t≥2；2) T1 扣5bp 年化≥+5pp 且 NW t≥2，MaxDD > −40% 则 fail；3) Q5−Q1>0；4) 随机百分位≥95。

## 8. 密封规则
密封窗 2018-01→2024-05 每臂只跑一次，须 Leo 批准。
