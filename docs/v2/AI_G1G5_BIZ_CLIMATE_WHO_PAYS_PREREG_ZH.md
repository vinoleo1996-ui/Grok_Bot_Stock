# 【FROZEN 2026-10-18 00:18:58 ET】
# G1G5 预注册：经营景气（合同负债变化 + 存货周转变化），g1g5_ashare_biz_climate_v1，叶21
状态：**FROZEN**（冻结时间见文末，冻结前未读任何本叶收益）。研究级；promotion_approved=false；live=false；禁 GP、禁高杠杆；不自跑 Book-Smoke；不碰卖方/调研/金股/一致预期。依据：主 Agent 10-18 00:17 ET 指令（叶21 只开这一个；研发资本化、日内反转不启动）。

## 机制与谁付钱
合同负债（含预收）同比扩张 = 已收款、未确认收入的订单储备在增加，领先于利润表；存货周转同比加快 = 去库、需求强于供给。两者都是资产负债表里的「经营景气」信号，市场主要按已报告利润定价，对它们反应不足。付钱的是只看利润表增速、忽略订单与库存周期的交易者。
与库内因子的区分：叶19 是现金流应计 + RNOA，叶20 是盈余意外；本叶只用资产负债表的订单和存货动量，并在中性化后检查 ρ。

## 规则（冻结后不调）
1. **数据**
   - balancesheet_pit_tushare：contract_liab、adv_receipts、inventories。
   - bs_cf_pit_tushare：total_assets。
   - financials_pit_tushare：revenue、grossprofit_margin（均为 YTD）。
   - 只取 report_type=1。同一 (ts_code, end_date) 取**最早** available_at 版本。available_at 的次日起可用（PIT）。
2. **订单储备**：CL* = contract_liab + adv_receipts，缺失按 0，但两者至少有一个非空。用合并口径消除 2020 年新收入准则的科目迁移。
   - ΔCL = (CL*_t − CL*_{t−4q}) / 平均总资产(t, t−4q)。
   - 两期必须正好相隔 4 个季度。
3. **存货周转**：COGS_q 由 YTD 的 revenue × (1 − grossprofit_margin/100) 拆成单季，TTM 需要连续 4 季齐全。
   - TURN = COGS_ttm / 平均存货(t, t−4q)。
   - ΔTURN = log(TURN_t / TURN_{t−4q})。
   - 存货 ≤0 或 TURN ≤0 记缺失。
4. **剔除金融**：SW L1 为银行、非银金融的股票不进池。另外硬排除 600519、002371。
5. **行业内标准化**：每日在池内、按 SW L1 分组，对 ΔCL 和 ΔTURN 各自 winsorize 到 1%/99% 后取 z-score。行业池内少于 5 名的分组记 0。
   - α_raw = z(ΔCL) + z(ΔTURN)，等权；单项缺失时用另一项。
6. **残差化与正交**：池内截面 OLS，回归项为 SW L1 dummy + log 流通市值 + mom20 + mom60 + vol20 + log ADV20（capacity_adv 机制代理），取残差。
   - 然后分域 rank 到 [−1, 1]，分域阈值为 logmv 的 P70/P90（小微 / 中小 / 大盘）。
   - 再对行业 + 市值做一次残差、分域 rank，得到 base-α。
   - 事后报告 ρ 和 Jaccard：对 capacity_adv（旧 / HI_LIQ）、五条 HI_LIQ 事件腿、earnings_event、叶19、叶20。ρ >0.5 的只能作过滤。
7. **慢 α 与快门**：慢 α 每 20 交易日再平衡（每日 α 向量照常输出）。
   - 快门（1–3 日，不进 α）：近 3 日里，任一日的行业 + 市值残差收益落在池内最低 5%，则 gate=0。
   - 快门与 α 不加权合成。
8. **评价权重**：≤20 名，每名 4%；行业帽 HI_LIQ 25%、FULLA 28%；余额配 510300。只在 gate=1 的名单里按 α 降序选。
9. **宇宙**：HI_LIQ_V1.1 为主（纸面路径）；FULLA_V1 为研究对照（取 cs_panel 的 fulla 列，覆盖密封窗）。
10. **窗口与成本**
    - 密封 2018-01-02→2024-05-31；X2 2024-06-03→2026-10-09。
    - 60万 = α 序前 6，100万 = 前 10。
    - 年化 244 为主、252 对照；复权；T+1 开盘；成本 17.5bp × 单位换手。
11. **主交付**：日度 base-α 向量。
12. **工程**：按年分块构建，每年的 α / gate 单独落盘；全程挂 1.5GB RSS 守护，超限即杀，不放宽。

## 硬闸（同叶19，外加池等权超额）
- 覆盖：每个再平衡日可算 α 的名数中位数，HI_LIQ ≥300，FULLA ≥800。
- 重合：Jaccard ≥0.7 硬拒；ρ_excess >0.5 只作过滤。
- 可交易：换手 >20%/日，或成本 > 毛超额的一半 → 不可交易。
- 衰减门 v1.1 不是 KEEP → 不过。
- Gate A：ρ vs cap <0.5 且残差 α >0。
- Gate B：cap80 + 叶20 两档净 CAGR 都 > cap。
- GATE_V3：MDD ≤25%（另报 ≤15%）。
- 对池等权基准的超额，必须报 t 值和分年。
- 自检用 leaf_selfcheck_v3 新池（含 HAC t，仅披露）。
- 跑不赢主干 → WATCH。

冻结：**FROZEN 2026-10-18 00:18:58 ET**（冻结时尚未计算任何本叶收益或覆盖统计）
