# 外部 Beta 机制消化（ortho 外延）— 公式级

更新：2026-10-12 07:47 ET（America/New_York）  
用途：吸收外源结构性收益来源，再设计 **我们自己的** 正交臂；禁止抄双低 / 教科书动量 / 已禁近亲。  
`promotion_approved=false`。主表 AUM 仅 60万/100万。压舱 **GOLD only**（禁 DD×GOLD）。

---

## 0. 硬禁与已有 WATCH（勿再扩近亲）

| 状态 | 臂/族 |
|---|---|
| WATCH explore-pass | MATPREM 族、IND-RATE-DIFF、PREMRESID-COV、GOLD-BETA |
| research_observe（ortho6 Strategy 定案） | PUTFLOOR-NEAR、BOND-NAV-MR（vs GOLD ρ≈0.57）、SEASON-NEW |
| FORBID 近亲 | MATPREM；IND-RATE/LPR/heat→510300；MATWALL；PARITY；PREMRESID-COV；PUTFLOOR；BOND-NAV-MR；SEASON-NEW；EQBOND-CORR；CALL-HEAT；P90；双低；教科书动量；小盘主线；IC/股指期货 |

---

## 1. 外源机制表（公式 + 样本/失败 + 正交性 + data/v2）

### 1.1 华泰中性化平价溢价率（PR residual）

**机制一句话：** 裸转股溢价率嵌平价/信用/规模/期限；截面回归残差才是「相对估值」。

**公式（殷超/张继强 2023《因子提纯在转债投资中的应用》推敲）：**

定义平价 \(\mathrm{Parity}_{i,t}=\) 转股价值 \(=\) `cb_value`，转股溢价率
\[
\mathrm{PR}_{i,t}=\frac{P_{i,t}-\mathrm{Parity}_{i,t}}{\mathrm{Parity}_{i,t}}= \texttt{cb\_over\_rate}/100.
\]
截面（日或调仓日）OLS：
\[
\mathrm{PR}_{i,t}
=\alpha_t+\beta_t\,\mathrm{Parity}_{i,t}
+\sum_k\gamma_{k,t}R_{i,t}^{(k)}
+\delta_t\log\mathrm{Size}_{i,t}
+\eta_t\,\mathrm{TTM}_{i,t}
+\underbrace{\theta_t\mathrm{Parity}_{i,t}^{2}+\phi_t\mathrm{TTM}_{i,t}^{2}+\cdots}_{\text{高阶}}
+\underbrace{\psi_t(\mathrm{Parity}\times\mathrm{TTM})+\cdots}_{\text{交叉}}
+\varepsilon_{i,t}.
\]
中性化因子 \(\widehat{\mathrm{PR}}^{\perp}_{i,t}=\hat\varepsilon_{i,t}\)（低残差=相对便宜）。评级 \(R\) 实务三分组：AA+以上 / AA及AA− / A+及以下。华泰结论：正股市值改进有限；评级+余额+TTM+高阶/交叉改进明显；**分组非绝对单调，常第 8–9 组优于第 10 组**；因子 IC 仍偏低。

**样本/失败条件：**
- 样本：华泰回测约 2018–2023；个券少、银行余额占比高 → 不做中性化易风格堆叠。
- 失败：机构化后「极低残差=正股恶化充分定价」（他思笔记同构）；极端信用事件；IC 不稳 → 不宜单独当主收益。
- 我们盒上：**无独立债项评级序列**（`cb_rate_raw` 是票息档而非评级）→ 完整华泰式 \(R\) 项不可落地；仅能做 Parity + log(remain_size) + TTM [+二次]。

**与已有臂正交性：**
- vs **MATPREM**：MATPREM≈裸低溢价排序；本式显式 \(\perp\) Parity → 理论上更纯，但仍是估值残差族。
- vs **PREMRESID-COV**：**近亲**（同属 PR~Parity 残差）。**禁止再实现为新臂。**
- vs IND-RATE/GOLD/PUTFLOOR：机制轴不同（截面估值 vs 利率体制/压舱/债底带），但若落地易与 PREMRESID-COV 高相关。

**data/v2：** `cb_daily.cb_over_rate/cb_value`、`cb_share_raw.remain_size`、`cb_basic.maturity_date` ✅；评级 ❌ → **消化采纳、实现禁（近亲 PREMRESID）**。

**谁付钱：** 支付给「在相同平价/期限/规模下仍愿买贵期权」的追涨资金；残差多头赚的是其过度支付的期权费均值回归（若仍存在）。

---

### 1.2 港中深 arXiv:2409.06496 — LSMC 定价 + 下修概率 \(p\)

**机制一句话：** 用路径依赖条款（强赎/回售/下修）的 LSMC 模型价相对市价的低估错价，而非双低分数。

**公式要点（Liu 2024/修订 2026）：**
- 正股 \(dS_t=(r-q)S_t dt+\sigma S_t dW_t\)；日度路径模拟 \(M\) 条。
- 续存价值回归基函数：
\[
\mathbf{e}_t=\{S_t,S_t^2,F_t,F_t^2,Y_t,Y_t^2,S_t F_t,S_t Y_t,F_t Y_t\},
\]
其中 \(F_t=\) 近 \(m_c\) 日触及强赎触发占比，\(Y_t=\) 近 \(m_p\) 日触及回售触发占比。
- 续存：\(y_t^{(i)}=e^{-r}V_{t+1}^{(i)}\)，\(\hat y_t=\mathbf{e}_t\hat\theta_t\)，
  \(\hat\theta_t=(\mathbf{E}_t^\top\mathbf{E}_t)^{-1}\mathbf{E}_t^\top\mathbf{y}_t\)（\(M\gg N\Rightarrow\) 唯一解）。
- **Multi-regression**：按 \(S_t\) 落入 \((k_t,\infty]/(C_t,k_t]/(p_t,C_t]/(-\infty,p_t]\) 分段回归。
- **下修：** 当 \(Y_t=1\)（回售触发）以概率 \(p\) 发生下修；数据不足时取 **\(p\approx 0.8\)**；下修至
  \(\hat C_t=\max(\overline{S}_{20},S_t)\) 底线。
- 策略：每日做多模型价相对市价最低估的 Top-10；文中显著跑赢双低基准。

**样本/失败条件：**
- 实证：2023H1 约 10 只 AAA 高成交券定价 RMSE≈3%；全市场 Top-10 低估日频再平衡。
- 失败：\(\sigma/r\) 误设；\(p\) 行业异质；交易成本与日频换手；无对冲时仍吃正股 Beta。

**正交性：** vs MATPREM/双低=条款路径定价错价 ≠ 低价+低溢价；vs PUTFLOOR=连续债底带持有 ≠ 回售触发态下的期权博弈；vs PREMRESID=模型价−市价 ≠ 截面 PR 残差。  
**与我们禁令：** 文中「优于双低」可吸收；**不可**把双低当主线复制。

**data/v2：** 日线/条款事件 `cb_events_*`、正股需另链；完整 LSMC **重**（路径+逐日回归）→ 短跑可做 **代理**：回售提示窗口 × 未下修 × ADV（事件概率 \(p\) 思想），但 ortho4 RESET-COOL 已 MDD 失败 → **勿近亲重开**；完整 LSMC 留给后续 infra。

**谁付钱：** 支付给忽略下修/回售路径依赖、用粗糙 BS/双低定价的对手盘；模型多头赚条款错价收敛。

---

### 1.3 Moreira & Muir (JoF 2017) 波动管理

**机制一句话：** 条件波动高时降仓，因波动变化未被预期收益等比补偿 → 夏普可升（权益因子显著）。

**公式：**
\[
f_{t+1}^{\mathrm{VM}}
=\frac{c}{\hat\sigma_t^{2}(f)}\,f_{t+1},
\quad
\hat\sigma_t^{2}(f)=\mathrm{RV}_{t}^{\mathrm{month}}
\]
（上月已实现方差；\(c\) 使无条件波动与 buy-and-hold 对齐）。均值方差动机：
\[
w_t^{\star}\propto\frac{\mathbb{E}_t[f_{t+1}]}{\hat\sigma_t^{2}(f)}
\underset{\mathbb{E}\text{近似常}}{\approx}\frac{c'}{\hat\sigma_t^{2}}.
\]
实务波动目标常写 \(w\propto\sigma_{\mathrm{target}}/\hat\sigma_t\)（与 \(1/\sigma^{2}\) 差一次幂，定性同向）。

**关键推敲（权益 vs 债/商品）：**
- **权益**：杠杆效应 + 波动−收益弱联动 → VM 常增夏普。
- **债券/商品**：文献与后续扩展普遍显示 **夏普增益弱或无**；对 GOLD/国债做 VM 多为降波动而非抬夏普。
- ECB 等：风险平价/vol-target 在危机相关升时被迫去杠杆，**放大卖压**（危机反身性）。

**样本/失败：** 美股因子 1926+；失败于预期收益与波动同向上升的体制、交易成本、杠杆约束。

**正交性：** vs GOLD-BETA（β(金,股) 调仓）不同；vs IND-RATE（利率差→权益）不同。  
**落地：** 对 **510300** 做 VM ≈ 又一条「体制→削宽基」，易坍缩 IND-RATE/CALL-HEAT 族 → **禁作主臂**。对 **511010↔GOLD** 做 VM：按文献 **不指望夏普增益**，至多作波动整形，非独立 Beta 源。

**谁付钱：** 在高波动时仍保持高仓的杠杆/vol-target 被动流；VM 多头赚的是其被迫卖出时的流动性溢价（若存在）。

---

### 1.4 他思笔记：双低失效 + 估值过滤 +（禁抄）对冲闭环

**机制主张：** 2022H2 后双低/隐波差在偏股转债上系统性衰退；「便宜」常是正股恶化充分定价。估值（债底溢价、转股溢价）应作 **安全边际过滤**，主线改为正股 Alpha + CCB Delta + **股指期货**对冲。

**公式片段（情绪 Delta）：**
\[
\Delta_{\mathrm{total}}
=\Delta_{\mathrm{adj}}
+\mathrm{Vega}\cdot\frac{\partial\sigma_{\mathrm{imp}}}{\partial S},
\quad
\min_h(w_{\mathrm{cb}}+h)^\top\Sigma(w_{\mathrm{cb}}+h)
\]
约束 \(\sum w\Delta_{\mathrm{total}}+\sum h\Delta_{\mathrm{fut}}\approx 0\)。

**对我们的硬约束：** **禁 IC/股指期货** → **不能抄其对冲闭环**；可吸收的是：
1) **双低不作主线**；2) 估值作过滤；3) 条款感知 Delta 思想（无期货时只能降净暴露/用 GOLD 压舱，不能声明市场中性）。

**谁付钱（其对冲版）：** 支付给承担未对冲 Beta 的多头；我们无 IC 则拿不到这笔「中性 Alpha」，只能拿结构性多头溢价。

---

### 1.5 可转债凸性 / 债底防守（Mirabaud、Advent、BNP）

**机制：** 非对称参与：上行捕获期权 Delta，下行债底截断。2025–26 利率抬升使债底「重新有意义」；**回避 80–100 Delta**（近似正股+到期日）。BNP：低 Delta、短久期、优质信用 → **Carry**；或 Delta 中性套利吃实现波动>隐含（需融券，A 股难）。

**公式（示意）：**  
参与率 \(\approx\Delta\)；债底 \(B=\mathrm{PV}(\mathrm{coupons}+\mathrm{principal};\ y_{\mathrm{credit}})\)；价格 \(P\approx B+\mathrm{Option}\)。  
低 Delta 筛：\(\Delta\lesssim 0.2\) 或价格近 \(B\) 且 YTM 有吸引力。

**失败：** 信用冲击击穿债底；高估值时期期权贵；流动性枯竭。

**正交性：** vs PUTFLOOR（我们已用 close/bond_value 带）— **近亲，禁扩**；vs MATPREM（低溢价股性）相反端。  
**落地：** 中 Delta 凸性带（溢价×价格联合带）仍可试，**须避开 PUTFLOOR/PARITY 阈值**。

**谁付钱：** 在恐慌中按近股性抛售转债的人，把非对称期权便宜卖给防守买方。

---

### 1.6 Carry + Roll-down（现金债 / 曲线）

**公式（曲线不变）：**
\[
R_{\mathrm{carry+roll}}
\approx\underbrace{(y-r_{\mathrm{repo}})h}_{\mathrm{carry}}
+\underbrace{\big(-D_{\mathrm{mod}}(y_{N-h}-y_N)\big)}_{\mathrm{roll}}.
\]
正斜率 → 滚下为正；倒挂 → roll 为负。等价叙事：赌现货曲线比远期更「粘」。

**中国代理：** 无完整国债曲线仓位时，用 **Shibor 期限利差** 或 **TF−T 期货结算价差** 代理「曲线陡峭 → 加久期（511010）」。

**失败：** 曲线熊市陡峭化（利率上行快于 roll）；TERM-3M30 曾配权益导致 X2 失败 — **本消化要求无权益袖套**。

**正交性：** ≠ LPR-LEVEL（水平）、≠ IND-RATE（行业−利率差→510300）、≠ BOND-NAV-MR（折溢价）。

**data/v2：** `rates/shibor.parquet`、`futures/bond_fut_*`、`511010/511880/518880` ✅。

**谁付钱：** 支付远期曲线定价（或必须对冲久期的机构）；陡峭时 roll 多头赚「曲线粘性未达远期」的差额。

---

### 1.7 ETF 折溢价 / AP 资产负债表

**机制：** 市价相对 NAV 的偏离反映 AP 资金与成分流动性约束（Pan–Zeng）；危机中债 ETF 折价可持续数周。QDII 额度可使套利失效。

**公式：** \(\mathrm{Prem}_t=P_t/\mathrm{NAV}_{t-}^{\mathrm{asof}}-1\)；扩展 z 分档调仓。

**正交性：** BOND-NAV-MR 已做 511010↔GOLD → **禁近亲**（勿再对 511010 换皮；511380 无 X1 覆盖）。

**谁付钱：** 在折价时恐慌卖 ETF、或在溢价时 FOMO 买 ETF 的二级账户。

---

### 1.8 融资/流动性体制（两融、北向）

**机制：** 融资余额刻画杠杆拥挤；快速去杠杆压迫风险资产。北向 2018+ → **X1 无覆盖**，ortho 批跳过。

**正交性：** MARGIN-DELTA（Δ→削 510300）已 fail_precheck 且近 IND-RATE 热度族。  
可试：**融资压力 → 缩放 CB 风险预算（不碰 510300）**。

**谁付钱：** 高杠杆融资客在去杠杆时的被迫卖出；CB/债券买方赚流动性溢价。

---

### 1.9 风险平价 / 危机 Alpha 压舱

**RP：** \(w_i\propto 1/\sigma_i\) 或风险贡献相等。危机中相关↑ → 去杠杆。  
**Crisis alpha：** 趋势/管理期货双向；黄金为压舱非万能（2020 亦曾因保证金抛售下跌）。

**我们：** GOLD-BETA 已 WATCH；禁 DD×GOLD 叠满；债期货趋势可作卫星但本批优先覆盖稳定的 ETF/CB 袖套。

---

## 2. 明确跳过（克隆/近亲/不可落地）

| 想法 | 跳过理由 |
|---|---|
| 双低 / 低价+低溢价主线 | 他思+华泰：失效/非单调；硬禁教科书估值主线 |
| 完整华泰 PR 残差臂 | **= PREMRESID-COV 近亲**；且缺评级 |
| 完整 LSMC Top-10 | 算力/正股链未就绪；RESET 事件代理已失败 |
| 权益 vol-target → 510300 | 坍缩 IND-RATE/heat 族 |
| 债/金 vol-target 当 Alpha | Moreira 逻辑下夏普增益弱 |
| 股指期货对冲闭环 | **禁 IC** |
| 511010 NAV 再分档 | ortho6 BOND-NAV-MR research_observe |
| PUTFLOOR/PARITY/SEASON/MATWALL/LPR 换皮 | FORBID |
| 北向 z | X1 无覆盖 |
| 511380 CB-ETF NAV | X1 days=0 |

---

## 3. 我们的候选臂（DISTINCT；含「谁付钱」）

按相对 MATPREM / IND-RATE / GOLD 的期望正交性排序（高→低）：

| # | 臂 | 唯一收益来源（1句） | 谁付钱 | 期望正交 | data/v2 | 覆盖预期 |
|---|---|---|---|---|---|---|
| 1 | **SHIBOR-ROLL-BOND** | Shibor **1y−1m** 扩展 z 陡→加 511010、平/倒→加 511880；余仓 GOLD | 支付远期/必须对冲久期的机构 | 高（纯曲线，无权益） | shibor+ETF | 高 |
| 2 | **TF-T-CURVE** | 主力 **TF−T** 结算价差扩展 z 陡→加久期 ETF，否则 GOLD | 期货曲线套保/展期流量 | 高（期货曲线≠LPR/NAV） | bond_fut+ETF | 高 |
| 3 | **CB-MIDCONVEX** | `cb_over_rate∈[15,55]` ∧ `close∈[100,130]` ADV 等权（中凸性，回避高Δ） | 追高Δ/抛售中性凸性的交易者 | 中高（≠PARITY/PUTFLOOR/MATPREM） | full CB | 中（X1 avg≈4） |
| 4 | **MARGIN-CB-BUDGET** | 两融余额 z 高→压缩 CB 袖套权重抬 GOLD（**不碰 510300**） | 去杠杆融资客 | 中 | margin+CB | 中 |
| 5 | **CB-NOCALL-ADV** | 剔强赎提示/实施后 ADV 等权（回避强赎 Gamma 击穿） | 强赎临近仍当股炒的持仓 | 中 | events+CB | 中高 |
| 6 | **CB-DEBTFILTER** | 估值仅作过滤：`bond_over_rate` 不过高 ∧ ADV，主仓仍流动性 | （过滤）信用低估陷阱的对手 | 低（易沾 CREDIT-RANK） | CB | 中 |
| 7 | **GOLD-VM-SHAPE** | 仅整形 GOLD 波动，不作 Alpha 宣称 | — | — | ETF | 跳过作主臂 |

**本批 ortho_ext1 落地前三（覆盖优先）：** 1 SHIBOR-ROLL-BOND，2 TF-T-CURVE，3 CB-MIDCONVEX。

---

## 4. 闸门（沿用）

- 预检 @60万 X1：Sharpe≤0 或 avg_names=0 → `fail_precheck`
- 正式：X1&X2 Sharpe>0、MDD>−25%、X2 CAGR≥12%；双 AUM 60万/100万
- 仅 pass → `handoff_strategy/`；`promotion_approved=false`
- 压舱 GOLD only

---

## 5. 来源 URL

- 华泰《因子提纯在转债投资中的应用》(2023-07-11)：https://file.iyanbao.com/pdf/a0e79-9c4b7acc-90ca-46d6-8cc5-45e276bad1ea.pdf
- Liu, arXiv:2409.06496：https://arxiv.org/abs/2409.06496 ；HTML：https://arxiv.org/html/2409.06496v6
- Moreira & Muir (2017) NBER w22208：https://www.nber.org/papers/w22208
- 他思笔记：https://heth.ink/ConvertibleBonds/
- Mirabaud CB convexity H1 2026：https://www.mirabaud-am.com/en/insights/news-detail/article/convexitys-proof-of-concept-what-h1-2026-showed-convertible-bond-investors
- BNP absolute-return CB：https://www.bnpparibas-am.com/portfolio-perspectives/taking-an-absolute-return-approach-to-convertible-bond-investing/
- Carry/roll-down：https://riskhub.org/blogs/carry-roll-down-explained ；中文骑乘：https://help.mathema.com.cn/zh/latest/docs/fixedincome/curveridding
- ETF arb / AP：Pan–Zeng SSRN https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2895478
- ECB vol-target focus：https://www.ecb.europa.eu/press/financial-stability-publications/fsr/focus/2020/html/ecb.fsrbox202005_02~f6616db9be.en.html

## Strategy 台账（2026-10-12T05:14:31-04:00）TF-T-CURVE
fail_explore X2 MDD≈−25.2%；无交接；台账 `descriptive_TF_T_CURVE_fail_explore`。promotion_approved=false。

---

## 6. ortho_evt_ind2（2026-10-12 06:50 ET）— 事件/资金·行业机制冒烟

New Bot 搜索循环：停 CB/利率/GOLD 压舱近亲；停磨 MARGIN-PX-DIV；禁 DT/NB/ANN（X1 仍 2018+）。  
压舱 **GOLD 518880 only**。AUM 60/100万。`promotion_approved=false`。  
数据：`etf_share_flow_pit_all` 自 2014-01-02（X1 行业 ETF≈32/日）；`data/sw/level1_bars.parquet` 自 1999。

| 臂 | 机制 / 谁付钱 | X1（60万） | X2（60万） | ρ vs IND-RATE | 处置 |
|---|---|---|---|---|---|
| **SW-DISP-CUT** | SW L1 日收益截面 σ 扩展 z 高→削 510300；低估离散度/相关破裂的宽基持有者 | 3.8% / −18.1% / 0.37 | 20.3% / −19.9% / 1.13 | X1≈0.96 / X2≈0.98 | **research_observe_near_relative**（无交接） |
| **IND-CREATE-HHI** | 正 Δshare HHI 高→削 510300；主题 FOMO 申购散户/渠道与 AP | 1.5% / −18.8% / 0.18 | 17.7% / −21.6% / 1.03 | X1≈0.96 / X2≈0.99 | **research_observe_near_relative**（无交接） |
| **IND-NAV-STRESS** | CS mean \|close/unit_nav−1\| 高→削 510300；AP/流动性应力对手方 | 4.5% / −15.3% / 0.43 | 21.6% / −19.3% / 1.23 | X1≈0.95 / X2≈0.99 | **research_observe_near_relative**（无交接） |

说明：三臂持仓空间均为 **510300↔GOLD 月调仓削仓**，收益流与 IND-RATE-DIFF 同构 → \|ρ\|>0.85 软标近亲；**不作独立 explore-pass / 不交接**。  
预注册：`docs/v2/V3_SW_DISP_CUT_PREREG.md` / `V3_IND_CREATE_HHI_PREREG.md` / `V3_IND_NAV_STRESS_PREREG.md`。  
Runner：`output/v3/run_ortho_evt_ind2.py`；batch：`output/v3/pretest_batch_20261012_ortho_evt_ind2.json`。

---

## 7. ortho_evt_ind3_book（2026-10-12 06:50 ET）— 改持仓：行业 ETF 多头书

**新规则**：禁止再发明「只削 510300」的扳机；本批持仓必须是 **行业 ETF 篮**（map-pit 每行业 1 只），GOLD 518880 仅残差。  
停 CB/利率/IND-RATE 近亲；停磨 MARGIN；禁 DT/NB。`promotion_approved=false`。AUM 60/100万。

预注册（运行前）：`V3_IND_CREATE_REV_BOOK` / `V3_IND_NAV_CHEAP_BOOK` / `V3_SW_DISP_TILT_BOOK` / `V3_IND_FLOW_DIFFUSION`（替换）。  
Runner：`output/v3/run_ortho_evt_ind3_book.py` + `run_ortho_evt_ind3_diffusion_only.py`；batch：`pretest_batch_20261012_ortho_evt_ind3_book.json`。

| 臂 | 机制 / 谁付钱 | X1（60万） | avg_names | 处置 |
|---|---|---|---|---|
| **IND-CREATE-REV-BOOK** | map-pit 底 tercile 20d ΣΔshare 创设反转；高位催促 AP 创设的散户/渠道 | −15.8% / −57.4% / **−0.36** | 1.16 | **fail_precheck** |
| **IND-NAV-CHEAP-BOOK** | 最负 prem tercile 折价书；急售/延迟 AP | −18.9% / −50.6% / **−0.41** | 1.16 | **fail_precheck** |
| **SW-DISP-TILT-BOOK** | 离散度高→行业篮 inv-vol，否则 EQW；追高波主题配置盘 | −16.6% / −48.3% / **−0.42** | 3.66 | **fail_precheck**（已替换） |
| **IND-FLOW-DIFFUSION** | 创设广度 z 高→份额滞后半仓 EQW，否则全合格 EQW | −15.3% / −48.3% / **−0.35** | 2.94 | **fail_precheck**（替换臂） |

说明：持仓空间已与 IND-RATE 削仓族脱钩（无 510300）；X1 行业池薄（液态 map≈3.7 行业/日）下行业 Beta 主导，Sharpe 全≤0 → **无一正式/无交接**。ρ vs IND-RATE 未开正式故未计。  
与前期 IND-SHARE-REV（份额 pct 底 3，avg≈2.7，Sharpe≈−0.34）同属「行业篮在 X1 熊段失效」族，非近亲削仓假过关。

---

## 8. ortho_evt_ind3_full（2026-10-12 06:53 ET）— 全宇宙行业篮（修 map-pit 过窄）

**修复**：弃 `sw_l1_etf_map_pit` 每行业 1 只；池=`etf_basic.category==行业` ∩ share_pit ∩ adj；`amt20≥1000`、上市≥60 日。  
持仓仍=**行业 ETF 篮**（非 510300 削仓）；GOLD 518880 残差；`promotion_approved=false`。AUM 60/100万。

预注册（运行前）：`V3_IND_CREATE_REV_FULL_PREREG.md` / `V3_IND_NAV_CHEAP_FULL_PREREG.md`。  
Runner：`output/v3/run_ortho_evt_ind3_full.py`；batch：`pretest_batch_20261012_ortho_evt_ind3_full.json`。  
X1 液态 names/day≈**11.3**（map-pit 曾≈3.7）。

| 臂 | 机制 / 谁付钱 | X1（60万） | avg_names | 处置 |
|---|---|---|---|---|
| **IND-CREATE-REV-FULL** | 全宇宙底 tercile 20d ΣΔshare；FOMO 创设对手方 | −13.2% / −46.5% / **−0.36** | **3.53** | **fail_precheck** |
| **IND-NAV-CHEAP-FULL** | 全宇宙最负 prem tercile；急售/延迟 AP | −20.8% / −51.4% / **−0.67** | **3.53** | **fail_precheck** |

说明：宇宙修复达标（avg_names>3），但 X1 行业 Beta 熊段仍 Sharpe≤0 → **无一正式/无交接**；ρ vs IND-RATE 未开正式故未计。不停磨 MARGIN；不停 CB/利率近亲。

## 9. stock_etf_smoke（2026-10-12 07:27 ET）— 个股+ETF 袖套
主线切换：个股事件/资金结构 × 宽基 ETF 残差；禁 CB/利率/黄金近亲。  
EVT-DT-INST-STOCK → **fail_precheck**（X1 Sharpe≈−0.55）。  
EVT-ANN-POLARITY-STOCK → **coverage_blocked_X1**（公告自 2018；S/X2 descriptive 未过闸）。  
**handoff: NO**。详见 hub `BETA_NEXT_AUM_ARMS_ZH.md` §stock_etf_smoke。

---

## 10. AI v20 Track B `etf_timing`（2026-10-12 07:47 ET）— Beta 复核+冒烟

包：`output/ai_factor/gp_reopen_hardgate_v20_track_b_etf_timing/`（evals=80 pass=23；叶子 ind/all/major；theme 跳过）。  
标签=次日行业 ETF **流延续**（非收益）。复核文档：`docs/v2/AI_V20_ETF_TIMING_BETA_REVIEW_ZH.md`。

| 检验 | 结果 |
|---|---|
| 流自相关 ICIR（PIT） | **+10.7**（lag1 ρ≈0.41） |
| vs 次日/5日行业 ETF 收益 ICIR | **−0.64 / −1.43** |
| 冒烟 T1–T10（顶 tercile 行业篮，残差 511880） | **全 fail_precheck**（X1 Sharpe≈−0.52～−0.57；T4/6/7 avg_names=0） |
| handoff | **NO**；promotion=false |

根因：包优化「猜明天的流」；流≠价。非 IND-RATE 削仓皮。LIMITUP/UNLOCK 本批不磨。

---

## 11. AI v21 `etf_timing_ret`（2026-10-12 07:51 ET）— Beta 复核+冒烟

包：`output/ai_factor/gp_reopen_hardgate_v21_etf_timing_ret/`（evals=120 pass=18）。  
标签=**fwd 1d/5d excess vs 510300**（非流延续）。复核：`docs/v2/AI_V21_ETF_TIMING_RET_BETA_REVIEW_ZH.md`。

| 检验 | 结果 |
|---|---|
| 标签形态 | ✅ 超额收益（非 v20 流延续） |
| 包窗 PIT `neg(flow)` vs excess ICIR | **≈ −0.10** |
| 包窗 trade_date 泄漏同检验 | **≈ +1.36 ≈ 包内 1.608** |
| 流自相关（叶子） | 仍 +10.7 |
| 冒烟 R1–R10（顶 tercile 行业篮，残差 511880） | **全 fail_precheck**（X1 Sharpe≈−0.12～−0.64；R5 avg_names=0） |
| handoff | **NO**；promotion=false |

根因：换了 y 仍用 trade_date 特征 → ICIR 虚高；PIT+真持仓不过闸。不磨 LIMITUP/UNLOCK/v20。

