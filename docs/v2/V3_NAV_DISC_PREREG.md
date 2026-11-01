# V3_NAV_DISC_PREREG — 510300 折溢价反拥挤调 β + 压舱

研究级，**promotion_approved=false**。  
**写于 2026-10-12 01:18 ET，在任何运行之前。**  
依据：`docs/v2/BETA_NEXT_AUM_ARMS_ZH.md` ①；CB-MATPREM 已通过并对账。

## 0. 差异
- **≠ SHARE-AC**：信号是 **价/净值折溢价**，不是基金份额 Δ。  
- **≠ 静态 60/40**：权重随折溢价 z 变化。  
- **≠ CB-*** / MATPREM：无转债。

## 1. 机制
二级市场相对 NAV 的短暂错价与拥挤；溢价时降 β。付钱方：溢价买入 / 折价恐慌卖出者。

## 2. 规则
- 净值：`data/v2/etf/raw/fund_nav/510300.SH.parquet`；PIT：`available_at = ann_date 23:59`（Asia/Shanghai 日历日）；信号日 T 只用 available 日历日 < T（即 ann 当日收盘后可知，T+1 开盘调仓前用到 T−1 及更早净值）。更稳妥：只用 `ann_date.normalize() < T`。  
- 交易价：510300 当日 `close`（原始价，与 NAV 同口径）。  
- \(prem_t = close_t / NAV^{asof}_t - 1\)；\(S_t = z_{250}(prem)\)。  
- 每 5 个交易日：  
  - \(S≥+1\) → \(w_{eq}=0.35\)  
  - \(S≤−1\) → \(w_{eq}=0.85\)  
  - 否则 → \(w_{eq}=0.60\)  
  - \(|Δw_{eq}|<0.10\) 则保持上期。  
- \(w_{eq}\)→510300；\(1−w_{eq}\)→511010/518880 逆波。gross≤1；L=1；无期货。  
- T+1 开盘；现金 511880；**AUM ∈ {600000, 1000000} only**。  
- 对照：静态 60/40（同压舱规则）。

## 3. 判定
探索 X1+X2 一次；S 描述。通过 = 每 AUM：两窗 MDD≤25%、夏普>0，X2 CAGR≥12%。通过才交接 Strategy。

## 4. 结果（2026-10-12 01:20 ET；`output/v3/nav_disc/results.json`）

| AUM | X1 | X2 | S（描述） | 判定 |
|---|---|---|---|---|
| 60万 | −1.3%/−28.2%/0.00 | 5.8%/−9.4%/0.56 | 0.1%/−24.8%/0.06 | **不通过** |
| 100万 | −1.4%/−28.2%/−0.00 | 5.8%/−9.4%/0.56 | 0.0%/−24.8%/0.06 | **不通过** |

短报：`output/v3/nav_disc/SHORT_ZH.md`。**无 Strategy 交接。** promotion_approved=false。
