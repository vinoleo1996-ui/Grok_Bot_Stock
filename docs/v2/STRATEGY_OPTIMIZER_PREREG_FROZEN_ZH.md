# 组合优化器路径预注册草稿（OPTIMIZER_V1，Strategy）— **DRAFT 非冻结**

> **FROZEN_STAMP 2026-10-14 ≈08:29 ET**：Eng 合格 λ 落盘（λ_risk=117.213；λ_turn 60/100万=0.6/0.6；prepared=24；turn_target_src=monthly_two_way_50pct_fallback；x2_returns_used_for_selection=false）。Arch FINAL + Beta PASS_PENDING_ENG_LAMBDA + Leo G0 齐。**授权立刻只跑 Core**（双口径①② + 三列 A/B/C）。X2 漂亮数不得晋级；FWD 2026-11-02 试金石。纸面 FROZEN_CONFIG 不动；live=false。


> **横幅（Leo Core-concentrate ≈08:09 ET）**：本 **FROZEN** 规格按 **主 Agent 转发的 Leo 最终口径** 改写——目标持仓 **20–30 只**（对齐 capacity_adv Top-25 + 整手）。**旧 Leo D 宽度/单票/行业/Size 数字作废**（2.5%/3%、Neff40–70、行业±5%、Size±0.25σ）。**Arch/Beta 旧 CONDITIONAL（含 Leo D 共签）一律 SUPERSEDED，须按本 Core-concentrate 重签**。**Eng λ 标定须用本表 NEW HARD**；旧 HARD 下任何标定产物作废、须重标。状态 **FROZEN**（2026-10-14 ≈08:29 ET）（**正文已对齐 CORE_CONC**，含 Slack 上限与两步整手算法）；**已 FROZEN**；授权只跑 Core（双口径+三列）；禁 Full；live=false。

- **状态**：**DRAFT**（非 FROZEN）。确认前**禁止**跑优化器回测 / book-smoke / 改纸面轨。
- **起草**：2026-10-14 ≈07:57 ET；07:58 四闸；08:08 Leo D；**≈08:13 ET 按 Leo Core-concentrate 最终改写**（看结果前；未跑优化器）。
- **牵头**：Strategy。共签：Beta / Arch（Core-concentrate + **双口径/主指标补丁 ≈08:21** → **请 Beta 重签**）。
  - 旧 Arch Leo D 有条件终签、Beta CONDITIONAL_COSIGN_LEO_D：**SUPERSEDED**（宽度/单票/行业/Size 已变）。
  - 升 FROZEN 阻塞：① Beta/Arch **Core-concentrate 重签** ② Eng 密封窗 λ 标定（**NEW HARD**）③ Leo 过关。α：AI / Alpha。
- **约束**：`live=false`；`strategy_promotion=false`。**不改** FROZEN_CONFIG / capacity_adv / B4 / S6 纸面轨。
- **双轨（显式）**：**求解宇宙 = HI_LIQ_V1.1**；**FULLA 仅 α/分域诊断与对照**；**裸 FULLA 权重不进纸面**。
- **范式**：停止「按总分排前 N」作为纸面/研究**主路径**；改为 **可交易池 → 组合优化器**（先冻+先跑 **Core**；Full 稍后）。

---

## 0. Leo 强制口径总表（≈08:09 Core-concentrate 覆盖 Leo D 宽度数字）

| # | 要求 | 本 DRAFT 写死 |
|---|---|---|
| 1 | 池=HI_LIQ；**不用**中证全指作 \(w_b\) | \(w_b\)=可交易池内**流通市值加权**（默认）；等权为 labeled 备选；纸面仍报 vs 510300 [0.70,1.00] |
| 1b | Size/MidCap vs \(w_b\) | HARD **±0.35σ** + **Slack**（见 §3.4；防无解）；Path A 防杠铃 |
| 2 | 单票 / 有效持仓 / 行业 | 单票：**100万 5.0% / 60万 6.0%**；Neff **20–30**；行业相对 \(w_b\) **±8%**；单行业绝对 **≤20%** |
| 2b | 两步截断重解 | 全池初解 → \(|w^{(0)}|\) 前 20–30 且单票 ≥**暂定 2.0%** → 二次重解 → **整手**（普 100 / 科创 200） |
| 3 | **取消** 3/2 冲击与外部双阈；仅优化器 L1 | \(\mathrm{TC}=\lambda_{\mathrm{turn}}\|w-w_0\|_1\)；引擎 strategy_v1 仍作终判成本 |
| 4 | λ 必须样本内密封窗标定后再进 X2；禁盲冻 λ | 标定闸见 §4；**禁用 X2 收益挑参** |
| 5 | 对标 | **Core 主对标 capacity_adv**（**双口径必报**，见 §5.1）；事件腿 vs B4 **留给 Full**；冻后**先只跑 Core**；Stage1 纸面底仓不动 |

**保留自 Leo D（未被 08:09 覆盖）**：\(w_b\) 定义、仅 L1、密封窗标定、双轨 HI_LIQ/FULLA、β HARD |β−1|≤0.10（后备 ±0.15）、Σ=行业+特异、INFEASIBLE 不松 HARD（Size/MidCap Slack 为 Leo 明示例外）、V1=单慢残差α+域壳仅 Full、库正交=V1.1。

原 Arch/Beta 条件共签中的「中证全指 \(w_b\)、行业 ±2%/±5%、单票 1–3%、宽度 40–400、双阈+3/2、Size±0.25」**全部作废**，以本表为准。

---

## 1. 可交易池（Investable Universe）

### 1.1 基础过滤（PIT，与 FULLA_V1 同族）

| 规则 | 口径 |
|---|---|
| 范围 | 沪深 A（不含北交所）；S 前 20 开市日至少 1 根 K |
| 剔除 | ST/*ST；停牌；上市不满 60 开市日 |
| ADV | HI_LIQ_V1.1：**ADV20 ≥ 1.0 亿**；**不做市值剔除**（Leo 07:24） |
| 幸存者 | 掩码含后来退市股；Eng 退市 terminal 未落地前报告打标 |

目标日均在池：X2 ≈3007（密封窗偏薄须披露）。

### 1.2 掩码（方案 A，不改冻）

- 路径：`output/strategy_hiliq/universe_mask_hiliq_v1.parquet`
- sha256：`c5433e80a74ac3acc0cd5a52d57fdd0bda5ed578fb86fb98cbd652ccb9f1b9af`
- **不**因想更宽而在本草稿内改 ADV；降 ADV 须 dated HI_LIQ_V2。

### 1.3 基准 \(w_b\)（**非**中证全指）

| 项 | DRAFT |
|---|---|
| **默认** | 可交易池内 **流通市值加权**，日度 renormalize；标签 `wb_proxy=float_mktcap_hiliq` |
| 备选 | 可交易池 **等权**；标签 `wb_proxy=equal_hiliq`；启用须 dated |
| **明确不用** | 中证全指官方成分权、CSI300 成分权冒充 \(w_b\)（纸面对照仍可报 vs 510300，见 §3.2） |
| 缺失 | 当日无流通市值 → 该票出 \(w_b\) 支持集；日志打标 |

### 1.4 分域（V1 = 域预算壳；真分域 α = V1.1）

**V1 写死**：

- **全池单一慢残差 α** + 域预算壳：D1/D2/D3 仅作预算与披露。
- 域定义：D1=CSI300∩池；D2=(CSI500∪CSI1000)∩池\D1；D3=其余。
- 域预算 \(b_d\)：初始化为 \(w_b\) 落在该域的权重和；相对偏离 **±3pp**（组合层）。
- **真分域独立慢 α = V1.1**（dated，Alpha 交付后）。

**Core vs Full**：域预算壳属 **Full**；**Core** 不做域预算（全池一次优化 + 两步截断）。

---

## 2. 因子闸 — 慢底仓 / 快门卫

**输入优化器的是残差 α，不是 Top-N 名次。**

### 2.1 慢 vs 快

| 类 | 角色 |
|---|---|
| **慢因子** | capacity_adv 类质量/容量/基本面 → 中性化后 \(\alpha_{\mathrm{res}}^{\mathrm{slow}}\) 进主目标 |
| **快因子** | 事件腿等 → **仅门卫/通道**；V1 默认只开门卫（\(q=0.30\)），通道加量关 |

### 2.2 残差与正交（V1 / V1.1）

1. **V1**：原始慢分在可交易池内对 **行业哑元 + 线性 Size + MidCap** 回归取残差 → \(\alpha_{\mathrm{res}}^{\mathrm{slow}}\)。
2. **对已有因子库施密特正交 = V1.1**；V1 **不**宣称库级正交。
3. **禁止**名次/秩当 α；禁止 \(\alpha\propto 1/\mathrm{rank}\)。

### 2.3 来源

| 来源 | V1 角色 |
|---|---|
| capacity_adv 截面分 | **慢 α 主源**（全池向量，非 Top-25 权重） |
| 事件腿 | 快门卫（**Full**）；Core 关 |
| 合成 | \(\alpha_{\mathrm{res}}=\alpha_{\mathrm{res}}^{\mathrm{slow}}\) |

---

## 3. 优化器规格（Leo Core-concentrate）

### 3.1 目标函数

\[
\max_w\; w^{\top}\alpha_{\mathrm{res}} - \lambda_{\mathrm{risk}}(w-w_b)^{\top}\Sigma(w-w_b) - \mathrm{Pen}_{\mathrm{soft}}(w) - \lambda_{\mathrm{turn}}\|w-w_0\|_1
\]

- \(w_i\ge 0\)；\(\sum w_i\le 1\)；现金≥0；L≤1.0；禁空。
- **唯一**优化内交易成本项：\(\lambda_{\mathrm{turn}}\|w-w_0\|_1\)。
- **已删除**：3/2 次冲击代理、外部双阈死区 \(\tau_{\mathrm{lo}}/\tau_{\mathrm{hi}}\)、分步建仓（staged builds）作为优化器规格。按手/涨跌停/participation 仍由 **引擎** strategy_v1 终判。

### 3.2 双口径 β（兼容保留）

| 用途 | 基准 | 约束/报告 |
|---|---|---|
| **优化器 HARD** | \(w_b\)=池内流通市值加权 | β：60 日滚动对 \(r_b=\sum_i w_{b,i}r_i\)；**HARD** \(\lvert\beta(w,w_b)-1\rvert\le \mathbf{0.10}\)（密封窗可行域系统性 INFEASIBLE 时 dated 改 ±0.15 + Beta 一行重签） |
| **纸面/Mandate 报告** | **510300** | 仍报 β∈报告带 **[0.70, 1.00]**、跟踪误差；**不**充当优化器硬约束 |
| **禁止** | 两套口径混用或互相替代 | — |

### 3.3 风险模型 \(\Sigma\)（重申）

**V1**：**申万一级行业因子 + 对角特异风险**（特异 = LW 对角或 60 日波动）。  
**禁止**「全池个股稠密 LW 无行业结构」作正式 Σ。L=120 PIT；停牌填 0 须披露偏差。

### 3.4 约束闸（HARD / SOFT / Slack）

**HARD（Leo Core-concentrate ≈08:09）**

| 硬约束 | DRAFT |
|---|---|
| 线性 Size | \(e_{\mathrm{size}}=(w-w_b)'z_{\ln\mathrm{mcap}}\)；**\(\lvert e_{\mathrm{size}}\rvert\le 0.35\)** |
| MidCap / 非线性 Size | \(z_{\mathrm{mid}}\)=截面标准化的 \((\ln\mathrm{mcap}-\mu)^2\)；**\(\lvert e_{\mathrm{mid}}\rvert\le 0.35\)** |
| **防杠铃 Path A** | ① MidCap 连续暴露硬盒 ② 分位桶 \(\min(w_{\mathrm{P20}},w_{\mathrm{P80}})\le 0.05\) |
| 申万一级相对 \(w_b\) | **±8.0%**（主动）；**单行业绝对 ≤20%** |
| 单票上限 | **100万：5.0%**；**60万：6.0%** |
| 单票下限（支撑集） | 终解 ≥ **暂定 2.0%**（1.5–2.0% 敏感性；密封窗后钉单点）；初解可更低探测；不达标归零 |
| **有效持仓宽度** | 目标 **Neff 20–30**（\(N_{\mathrm{eff}}=1/\sum w_i^2\) 与权重大于下限的个数双监控；公平对标 capacity_adv Top-25） |
| 权重和 / 杠杆 | \(\sum w_i\le 1\)；L≤1.0；禁空 |
| 参与率（引擎侧） | 单日单票调仓名义 ≤ ADV20 × **0.6%**（Eng 终判） |
| 域预算 | 仅 **Full**：相对 \(w_b\) 域份额 ±3pp |
| β vs \(w_b\) | \(\lvert\beta-1\rvert\le 0.10\)（后备 ±0.15，dated+Beta） |

**SOFT**

| 软罚 | DRAFT |
|---|---|
| 自信风格（残差价值/质量等） | \(\sum_s\mu_s(e_s-0)^2\)；把握不足则 \(\mu=0\) |
| 拥挤度接口 | 见 §3.6；缺失 → \(\nu=0\) 打标 |

**Slack 上限（Beta CORE_CONC 共签前提 · 写死）**

| 通道 | 上限 | 说明 |
|---|---|---|
| Size/MidCap | 相对 HARD 盒额外 **≤ 0.05σ**（即有效至多 ±0.40） | 打标 `slack=size_midcap`；披露用量 |
| 行业相对 \(w_b\) | 相对 ±8% 额外 **≤ 1pp**（即至多 ±9%） | 打标 `slack=industry`；**绝对 ≤20% 不享受 Slack** |
| 单票 / Neff / β / 绝对行业 | **0** | 禁止任何 Slack |

Slack = step2 / 数值误差在 HARD 外的**有限**软溢出，**不是**第二套更宽 HARD。正式臂须披露是否动用及用量；超出 Slack → 仍 `INFEASIBLE`。

**降级序（INFEASIBLE 永不松上述硬上限之外）**

1. 先置软罚 μ/ν → 0（`degrade=soft_zero`）。
2. 若仍 INFEASIBLE：在 **Slack 上限内**尝试 Size/MidCap（≤0.05σ）与行业相对（≤1pp）；打标并披露。
3. Full 域预算 → 压回 0（贴 \(w_b\) 域份额）。
4. 权益总仓比例降仓 → 现金。
5. 仍不可行 → 该再平衡日沿用上期权重或全现金，`optimize_status=INFEASIBLE`。
6. 月内 INFEASIBLE ≥2 → 停跑升级主 Agent；阈值修订须 dated + 双签，另计试验。

**禁止**把「临时把行业改为 ±15% / Size 改为 ±0.50 / 单票改为 10% / 丢掉绝对 20%」的解记入正式臂。

### 3.5 两步截断重解 + 整手算法（Core 写死）

| 步 | 动作 |
|---|---|
| (a) | **全池初解**：在 HI_LIQ 上求 \(w^{(0)}\)（HARD+SOFT+L1） |
| (b) | **支撑集**：主准则写死按 \(|w^{(0)}|\) 降序取前 **20–30** 名（α 贡献仅诊断对照，**不**作主排序）；且单票目标权重 ≥ **暂定 2.0%**（1.5–2.0% 敏感性；**密封窗后钉单点**）；其余强制 0 |
| (c) | **二次重解**：仅在支撑集上重解（同一目标+HARD）得 \(w^*\) |
| (d) | **整手取整**（书面算法，见下）→ \(w^{\mathrm{lot}}\)；现金吸收残差 |
| 失败 | 支撑集过窄，或 step2/整手后违反 HARD 且 **超出 Slack** → `optimize_status=INFEASIBLE` 或 `LOT_HARD_FAIL`；**不得**静默接受；不得偷偷扩到 Neff>30 而不打标 |

**整手算法（须实现一致）**

1. 对每只票 \(i\)：\(\mathrm{lot}_i=200\) 若代码为科创板（`688***`），否则 \(\mathrm{lot}_i=100\)。
2. \(q_i=\left\lfloor\dfrac{w^*_i\cdot\mathrm{AUM}}{P_i\cdot\mathrm{lot}_i}\right\rfloor\cdot\mathrm{lot}_i\)（\(P_i\)=可交易价，PIT）。
3. \(w^{\mathrm{lot}}_i=q_i P_i/\mathrm{AUM}\)；未分配权重进现金。
4. 校验 HARD（含 Neff、单票、行业、Size/MidCap、β）；仅允许 §3.4 **Slack 上限内**溢出；否则失败码如上。
5. 引擎 `strategy_v1` 仍作最终成交/成本终判；优化器输出不得假定无整手摩擦。

### 3.6 拥挤度代理（可审计）

| 字段 | V1 |
|---|---|
| `c_i` | 近 \(L_c=20\) 日成交额分位 × 与高 α 侧重叠代理（或换手 z） |
| 覆盖率阈值 | 可交易池内有效 `c_i` 覆盖 ≥ **70%** 当日权重支持集 |
| `missing_policy` | 覆盖不足或 state 缺失 → **ν=0**，打标 `crowd=off` |
| ν | **CONDITIONAL**：仅 α–风险同量纲标定后可写死；未标定前 ν=0 |

### 3.7 成交闸 — **仅 L1**

| 项 | DRAFT |
|---|---|
| 优化内 TC | \(\lambda_{\mathrm{turn}}\|w-w_0\|_1\) **唯一** |
| **删除** | 3/2 冲击、双阈死区、staged builds（优化器规格层） |
| 引擎终判 | `ExecConfig.strategy_v1`：next_open、sqrt 冲击、participation、按手、涨跌停 |
| 单边换手硬帽 | ≤ **40%** NAV / 再平衡（与 B4 换手量级标定对齐，见 §4） |

### 3.8 再平衡 / AUM

- **再平衡写死（Leo ≈08:20 ET 终签拍板 · 唯一）**：与现行 **capacity_adv** 完全一致 —— cadence=`month_end_plus_first_last`（月末主再平衡 + 窗首/末日）。**禁止**在密封窗内试周频/月末两种频率；日后若改频须重标 \(\lambda_{\mathrm{turn}}\) + Beta/Arch 双签。
- **控制变量**：Stage1 验证「优化器构造 vs Top-25 排序」时，调仓时点须与 capacity_adv **100% 同步**，排除调仓频率带来的收益/回撤差。
- **\(\lambda_{\mathrm{turn}}\) 密封窗标定中心目标（非硬保）**：月**双边**换手 \(\approx 50\%\)（或折合年化单边换手 **4–6 倍**）；首选对齐同窗同 AUM **capacity_adv** 引擎换手中位数 **±20%** 带（B4 仅作参考对照）。
- **成本 / 实际换手**：作为 X2 样本外自然观测如实报告（含是否 ≤1.3%/AUM）；**不做事前硬性承诺**。≤1.3% 仅为 stretch 观察（现 capadv BOOK ~1.72%）。
- Core **禁止**塞入 LLM 权重或防守垫 ETF（属 Full / 第三臂）。
- 快因子门卫可禁增持（Full）；Core 关。
- 60万 / 100万；普通 lot=100；科创板 lot=200；`order_rounding=target`。

---

## 4. 标定闸（FROZEN 前置 · BLOCKING）

**禁止**盲写 λ 进 FROZEN。须在**样本内（密封窗）**标定后再碰 X2：

| 参数 | 状态 | 口径 |
|---|---|---|
| \(\lambda_{\mathrm{risk}}\) | **BLOCKING** | 密封窗内使典型 \(\lvert w-w_b\rvert\) 下风险项与 \(w'\alpha\) 同量级；产物 `calib_lambda_risk.json` |
| \(\lambda_{\mathrm{turn}}\) | **BLOCKING** | 密封窗标定中心目标=月双边 \(\approx 50\%\)（或年化单边 4–6×）；**优先**对齐同窗同 AUM **capacity_adv** 引擎换手中位数 ±20%（B4 对照）；实际换手/成本=X2 观测非硬保；产物 `calib_lambda_turn_60w.json` / `_100w.json` |
| ν | **BLOCKING**（未标定=0） | 同量纲后单点；否则 crowd=off |
| β 带宽 | **±0.10 vs \(w_b\)**（±0.15 仅 INFEASIBLE 后备） | — |

标定**只看**约束可行性、换手、暴露；**不看**密封窗 CAGR 选参。X2 为样本内报告窗，标定不得用 X2 收益挑 λ。

**HARD 变更通知 Eng**：任何在旧 HARD（2.5%/3%、Neff40–70、行业±5%、Size±0.25）下已跑或在跑的标定 **一律作废**；须按本 §3.4 NEW HARD + 两步截断重标。交接单：`STRATEGY_OPTIMIZER_LAMBDA_CALIB_HANDOFF_ZH.md`；产物目录：`output/strategy_optimizer/calib/`。

---

## 5. Core vs Full 消融（写死）

| 臂 | 包含 | 对标 / 角色 |
|---|---|---|
| **Core** | 优化器 + 行业±8%/绝对≤20% + Size/MidCap±0.35σ（Path A）+ Slack + L1 + **两步截断（Neff20–30）**；慢残差 α；**无**域预算、**无**快门卫、**无**拥挤度；**禁** LLM 权重 / 防守垫 ETF | **主对标 capacity_adv**（§5.1 双口径）；冻后**先只跑 Core** |
| **Full** | Core + 域预算壳 ±3pp + 快/慢门卫（事件腿）+ 拥挤度接口 | **事件腿对标 B4 延后到 Full**；分开报告，禁把 Full 增益回贴 Core 选参 |

两臂均报 60万/100万 × 密封窗+X2；与纸面 capacity_adv / B4 **并列对照，不替换**。

### 5.1 Core vs capacity_adv：**双口径对标（强制）**

采纳 Arch（挑战方）：Core 对决 capacity_adv 时**必须同时输出**两套净值，缺一不可；**禁止**用「满仓 HI_LIQ / 取消 510300」的单稿冒充公平对标。

| 口径 | 组合构造 | 用途 |
|---|---|---|
| **① 纯股票腿 100%** | 优化器输出股票权重 renormalize 至 100%（无 510300 袖） | 看浓缩选股/约束本身 |
| **② 同挂 20% 510300 总口径** | 股票袖 **80%** + **510300 固定 20%**（与现行 capacity_adv 书结构同形） | **主对标** capacity_adv 纸面总账 |

规则：
1. 两口径均报 60万∧100万 ×（密封窗披露 + X2 样本内）；必报 CAGR/MDD/Calmar/成本/换手/填单/Neff。
2. **主结论表以口径②为准**与 capacity_adv 并排；口径①仅作分解，不得单独宣称「跑赢 capadv」。
3. **Stage1 纸面底仓不动**：FROZEN_CONFIG / capacity_adv / B4 / S6 日终轨不因本对标改权重。
4. 优化器求解仍在 HI_LIQ、\(w_b\)=池内市值加权；510300 **只出现在报告层套袖**，不进优化器 HARD（与 §3.2 双口径 β 一致）。

### 5.1.1 Core 包装三列对标（主 Agent ≈08:24 评审 · 强制）

Core 正式报告表**必须含三列**（缺一不可；均在口径② 80/20 上主比，口径①可附分解）：

| 列 | 臂 | 宇宙 / 锚 | 角色 |
|---|---|---|---|
| **A** | **Core（优化器）** | HI_LIQ_V1.1 | 待验构造 |
| **B** | **现行 capacity_adv** | mid_large 锚（纸面轨） | 现行书锚；**不改纸面** |
| **C** | **capacity_adv Top-25 @ HI_LIQ 同池** | 同 HI_LIQ_V1.1；Top-N 排序（非优化器） | 同池控制变量；隔离「池切换」vs「优化器构造」 |

纪律（写死）：
1. **X2 漂亮数不得晋级**：X2（2024-06→）仅为样本内报告；**禁止**因 X2 CAGR/MDD/Sharpe 漂亮而改纸面 / 升 promotion / 宣称 Stage1 过关。
2. **FWD 2026-11-02 起前向纸面窗**才是试金石（与 B4 前向轨同纪律）；密封窗+X2 只作披露与对照。
3. **B4 / S6 事后挑选纪律不变**：预注册外 walk-forward 挑出的组合（含 S6）**不得**因漂亮数自动进纸面；须另写预注册 + Leo/主 Agent 过关。
4. 列 C 可复用已落盘 HI_LIQ X2（`STRATEGY_HILIQ_CAPADV_X2_ZH.md`）；Core 开跑后三列同窗同 AUM 并表。

### 5.2 主指标与 α 表述（主 Agent ≈08:19 采纳）

| 项 | 写死 |
|---|---|
| **对标对象** | Core **只对标** capacity_adv（不做与 B4 的主对决；B4→Full） |
| **主指标** | **Sharpe、MDD、IR**（信息比率 vs 同口径基准）；CAGR/Calmar/胜率仍必报但**非**主排序 |
| **公平性** | **禁止**用口径①（纯股票 100%）的绝对 MDD/Sharpe **直接**对比含 20% 510300 的 capacity_adv 总账；主对比必须在口径②（80/20）上 |
| **α 目标** | 用 **目标区间**：「抬 Sharpe / 压 MDD（相对同口径 capadv）」；**不作**「α≥8%+」之类设计输入或硬门槛 |
| **记分卡** | 若引擎/记分卡暂无 Sharpe/IR 字段，Eng 须在 Core 报告中 **补算**（日收益、244 年化）并标注公式 |

### 5.3 三阶段（Stage1–3）

| 阶段 | 内容 | 状态 |
|---|---|---|
| **Stage1** | 纸面 **底仓规则不动**；浓缩 **Core** 冻结并只跑；双口径 + **三列**对标；禁 LLM、禁换垫仓；X2 禁晋级 | **本 DRAFT 范围** |
| **Stage2** | LLM/事件须 **PIT+脱敏** 进 **Full**，对标 B4；不回贴 Core 选参 | 后置 |
| **Stage3** | 才考虑替换 20% 510300 垫仓（国债/红利/动态闸门等） | 后置；须独立预注册 |
  
首次 FROZEN 后跑通计 **+1** 臂（**仅 Core**）；Full 另计、稍后。

---

## 6. 窗口与报告

| 窗口 | 区间 | 标注 |
|---|---|---|
| 密封窗 | 2018-01-02→2024-05-31 | **标定 + 开发**；非晋级；池偏薄须披露 |
| X2 | 2024-06-03→2026-10-09 | **样本内报告**；**禁止**用 X2 收益标定 λ；**漂亮数不得晋级** |
| FWD | **2026-11-02 起** | **前向纸面试金石**；Stage1/晋级只认此窗（与 B4 前向轨同纪律） |

必报（**主指标** Sharpe、MDD、IR；其余次之）：Sharpe、MDD、IR、CAGR、Calmar、日胜率、单边换手、成本、填单率、\(N_{\mathrm{eff}}\)（目标 20–30）；申万一分布；单列电子/计算机/通信/医药；D1/D2/D3（Full）；小盘后 30% **仅披露**；Size/MidCap；vs **510300** 纸面 β；两步截断前后持仓数；**§5.1 双口径①②全套** + **§5.1.1 三列**（A Core / B 现行 capadv mid_large / C capadv Top-25@HI_LIQ）；主对比在②。年化 **244**。MDD 门：≤25% 硬关注；另报 ≤15%。

---

## 7. 明确不做

- **不跑**优化器回测直至 FROZEN + Leo/主 Agent 确认。
- **不**用中证全指 / CSI300 官方权作 \(w_b\)。
- **不**恢复 3/2 冲击或外部双阈作优化器 TC。
- **不**盲冻 λ / ν；**不**用旧 HARD 标定产物。
- **不**把 Top-N / 50/25/25 作主路径（纸面对照除外）。
- **不**改 HI_LIQ 冻掩码；**不**动 FROZEN 纸面轨；**不**翻转 live/promotion。
- **不**在 Eng 退市清算落地前宣称无幸存者问题。
- **不**在 Core 臂开启事件门卫或固定 50/25/25。

---

## 8. 待共签 / BLOCKING 总表

| # | 项 | 状态 | 谁 |
|---|---|---|---|
| B1 | 接受 Leo Core-concentrate 覆盖 Leo D 宽度数字 | **CLOSED**：Arch CONDITIONAL_PASS + Beta CONDITIONAL_COSIGN_CORE_CONC | Beta, Arch |
| B2 | \(w_b\)=float_mktcap_hiliq；行业±8%/绝对≤20%；单票 5%/6%；Neff 20–30；Size±0.35σ+**Slack≤0.05σ**；行业 Slack≤1pp；两步+整手算法 | **CLOSED（正文已写）** | Strategy+Beta |
| B3 | 优化器 β 带宽 vs \(w_b\) | **±0.10 HARD**（±0.15 后备） | Strategy+Beta |
| B4 | \(\lambda_{\mathrm{risk}},\lambda_{\mathrm{turn}}\) 密封窗标定（**NEW HARD**） | **BLOCKING for FROZEN**；旧 HARD 标定作废 | Eng + Strategy |
| B5 | ν 标定或保持 0 | **BLOCKING** | Beta + Strategy |
| B6 | V1=单 α+域壳；库正交=V1.1；双轨一句 | **已写** | Arch 终签 |
| B7 | Core 主对标 capadv；Full↔B4 延后；先跑 Core | **已写** | Arch 审计 |

纸面 vs 510300 报告带保留。live=false。

---

## 9. 依赖

| 角色 | 需要 |
|---|---|
| Beta | **按 Core-concentrate 重签**：新单票/Neff/行业/Size+Slack、两步截断、L1-only、降级序、拥挤度 missing_policy |
| Arch | **按 Core-concentrate 终签**：四闸完整性；确认两步截断+集中度不违工业支柱 |
| Alpha | 全池慢残差 α 向量（非 Top-25） |
| AI | 快门卫残差分（Full，稍后） |
| Eng | **按 NEW HARD** 密封窗 λ 标定；L1 与 strategy_v1 换手对齐；book-smoke；退市 terminal |
| Data | 流通市值 PIT；成分仅用于分域标签 |

---

## 10. 修订记录

| 时间 | 内容 |
|---|---|
| 2026-10-14 ≈07:57 ET | DRAFT 初稿。 |
| 2026-10-14 ≈07:58 ET | 加深四闸。 |
| 2026-10-14 ≈08:03–08:05 ET | Arch/Beta 旧数值共签（已作废）。 |
| 2026-10-14 ≈08:08 ET | Leo 选项 D：\(w_b\)/±0.25σ/单票2.5·3%/N_eff40–70/行业±5%/仅 L1。 |
| 2026-10-14 ≈08:11 ET | 采纳 β±0.10；Arch/Beta Leo D 有条件共签曾齐（现 SUPERSEDED）。 |
| **2026-10-14 ≈08:13 ET** | **Leo Core-concentrate（≈08:09 via 主 Agent）**：单票 **5%/6%**；Neff **20–30**；行业 **±8%/绝对≤20%**；Size/MidCap **±0.35σ+Slack**；**两步截断重解+科创200整手**；Core 主对标 capacity_adv Top-25；B4 事件对标延后 Full；冻后先只跑 Core。旧 Leo D 宽度共签 **SUPERSEDED**。仍 **DRAFT**；禁跑；live=false。 |
| **2026-10-14 ≈08:14 ET** | Arch 微缺口：支撑集主准则写死 \(|w^{(0)}|\)；单票下限暂定 **2.0%**（密封窗后钉点）。Arch **CONDITIONAL_PASS** 已收；Beta **CONDITIONAL_COSIGN_CORE_CONC** 已出；DRAFT 正文已对齐浓缩。仍 **DRAFT**；等 Eng λ + Leo 过关。 |
| **2026-10-14 ≈08:15 ET** | 按 Beta CORE_CONC：写入 **Slack 上限**（Size/MidCap ≤0.05σ；行业相对 ≤1pp；绝对行业/单票/Neff/β=0）+ **两步整手书面算法**（科创200）。正文已非 Leo D。仍 **DRAFT**；FROZEN 卡 Eng λ + Leo 过关。 |
| **2026-10-14 ≈08:20 ET** | Arch 拍板补丁：Core vs capadv **双口径**（①纯股票100% + ②80/20+510300）；主结论用②；禁满仓 HI_LIQ 单稿对标；Stage1 底仓不动；再平衡写死月末；成本≤1.3% = stretch；Core 禁 LLM/防守垫。请 Arch **终签冻 Core**。仍 **DRAFT**（待 Eng λ + Leo）。 |
| **2026-10-14 ≈08:21 ET** | 主 Agent 采纳 Arch 补丁强化：主指标 **Sharpe/MDD/IR**；禁①直接比 capadv 绝对回撤；α=抬夏普/压回撤目标区间（非 8%+ 输入）；Stage1–3 写死。请 **Beta 重签**；Eng λ 按双口径密封窗。仍 DRAFT。 |
| **2026-10-14 ≈08:22 ET** | **Leo 终签拍板（频率+换手）**：调仓写死=`month_end_plus_first_last`（与 capacity_adv 完全一致；禁密封窗双试周/月末）；\(\lambda_{\mathrm{turn}}\) 标定中心=月双边≈50% 或年化单边4–6×（优先对齐 capadv）；成本/实际换手=X2 观测非硬保；双口径保留。**请 Beta/Arch 终签**；Eng λ 齐后立即 FROZEN 开跑 Core。仍 DRAFT 至 λ 落盘。 |
| **2026-10-14 ≈08:24 ET** | **主 Agent 评审**：Core 包装强制三列 A=Core(HI_LIQ) / B=现行 capadv(mid_large) / C=capadv Top-25@HI_LIQ 同池；**X2 漂亮数不得晋级**；**FWD 2026-11-02** 才是试金石；B4/S6 事后挑选纪律不变。写入 §5.1.1。仍 DRAFT 至 Eng λ。 |
| **2026-10-14 ≈08:29 ET** | **FROZEN**：Eng λ 合格（risk=117.213；turn 0.6/0.6；24日；fallback 月双边50%；INFEASIBLE=0）。盖戳开跑 Core 双口径+三列。纸面不动；live=false。 |

---

## 附录 A：与 Arch/Beta 共签关系

- `ARCH_OPTIMIZER_V1_COSIGN_ZH.md`、`BETA_OPTIMIZER_COSIGN_V1_ZH.md`：旧数值，作废。
- `ARCH_OPTIMIZER_V1_COSIGN_LEO_D_ZH.md`、`BETA_OPTIMIZER_COSIGN_LEO_D_ZH.md`：Leo D 宽度数字，**SUPERSEDED**，须按本 Core-concentrate **重签**。
- 结构仍可复用：Σ=行业+特异、Path A、降级序（Slack 通道收窄为仅 Size/MidCap）、双口径纸面 β、crowd missing→0、双轨、V1 域壳、仅 L1。
- **FROZEN ✅ ≈08:29 ET**：Eng λ + Arch FINAL + Beta PASS_PENDING + Leo G0 全齐；已授权 Core 开跑。

| **2026-10-14 ≈08:45 ET** | **修订 v1.1（实现修正，主 Agent 选项 B）**：满仓 Σw=1 + 整手后现金 ≤2%；step2 失败 → INFEASIBLE 并沿用上期持仓（禁回退 step1）；硬 20–30 只（迭代 top-k）。λ 不变。见 `STRATEGY_OPTIMIZER_PREREG_AMEND_v1_1_ZH.md`（FROZEN_v1.1，待 Arch 程序性共签）。 |
