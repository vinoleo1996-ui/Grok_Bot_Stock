# 叶18 候选扫描（修订 · 2026-10-14 08:25:32 ET）
研究级；live=false；promotion=false；禁 GP/高杠杆；**未读任何价格/收益用于选方向或调参**。
**HARD PIVOT（主 Agent 08:24 ET）**：禁止卖方/研报/调研/金股/目标价/重大合同方向。原 tech_qual_cert / 合同类草稿已 **ABORTED**（见 AI_LEAF18_TECH_QUAL_CERT_ABORT_ZH.md）。

宇宙：**HI_LIQ 主口径**；FULLA 研究对照。须 Leo 工艺：分域标定、慢α/快gate 分离、行业+市值残差、正交、α向量非 Top-N；密封+X2；60万/100万；跑不赢主干即砍。

## 三候选（①②③ 仅此范围）

### ① earnings quality / cash-flow accruals / RNOA
- **PIT**：BS/IS/CF 满窗可得；可算 WC 应计、CF 应计、RNOA。
- **硬伤**：`accrual_quality` 已 Book-Smoke **WATCH/DONE_FAIL**；`indcap_momneut_ocf` 已入穷尽表；再开应计/OCF 同族易被判换皮。RNOA 虽公式不同，仍属「质量/盈利能力」教科书邻域，与 Leo「禁教科书主线」张力大。
- **ρ vs capacity_adv 预期**：低（历史 Jaccard max≈0.22），但**已验证烟灭**。
- **结论**：不选。

### ② intraday vs overnight 分解 / idiosyncratic volatility ★选定
- **PIT 就绪度：最高**。真分钟线历史不足（bars 仅近窗样本）；但标准 **隔夜= open/pre_close−1、日内= close/open−1** 可由 `tushare_raw/daily` 全日 OHLC 满窗重建（抽检 2018–2025 覆盖率≈100%）。HI_LIQ 掩码覆盖 2018-01→今。
- **谁付钱（机制）**：偏好「隔夜彩票」的高特质隔夜波动交易者支付溢价；低特质隔夜波动名称被注意力资金忽视 → 后续补偿。慢因子=20 日特质隔夜波动（截面残差后）；快门=近 1–3 日隔夜极端左尾过滤（不作 α 加权）。
- **ρ vs capacity_adv 预期：低**（机制=隔夜微观结构/波动，非 ADV 流动性分位；与合同/卖方/财报事件亦正交）。
- **与已有叶**：非 earnings_event / report_rc / broker / contract / equity_incentive；非已灭量价动量主线（不用涨跌幅排序作主 α）。
- **结论**：选定。

### ③ desensitized SUE residual
- **PIT**：有 `ep_pit_daily`（e_ttm），**无分析师一致预期** → 只能做时间序列季节 RW 代理 SUE，不是标准 SUE。
- **重合**：与 `earnings_event` 同属盈余披露扩散族，ρ/Jaccard 风险高于 ②。
- **结论**：不选（数据定义弱 + 同族风险）。

## 选定：② → 机制名 `overnight_idio_ivol`（g1g5_ashare_overnight_idio_ivol_v1）
下一步：FULLA+HI_LIQ 双口径 who_pays 预注册（读收益前冻结）→ 覆盖/可交易名计数闸 → α 向量与自检。不自跑 Book-Smoke。

## 披露
- 「intraday」本叶 = **日线开-收分解**，不是分钟线；分钟线可行性见 INTRADAY_DATA_FEASIBILITY_ZH.md（监控用途，不作本叶历史回测主源）。
