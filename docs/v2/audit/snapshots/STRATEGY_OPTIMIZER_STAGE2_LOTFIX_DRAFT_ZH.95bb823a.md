# OPTIMIZER Core v1.4 / Stage2 整手修复草案（LOTFIX，DRAFT）

- **状态：DRAFT（r3）**。待主 Agent 冻结。live=false，promotion=false。
- **修订记录**：
  - r2 = a1a2552c…83e7，已由 Arch 和 Beta 会签。快照：`docs/v2/audit/snapshots/STRATEGY_OPTIMIZER_STAGE2_LOTFIX_DRAFT_ZH.a1a2552c.md`（Strategy 存），以及 Arch 存的全 sha 文件名副本。两份字节相同。
  - r3（2026-10-18 ≈00:57 ET）只做纯文字修订：
    - Arch 会签 `ARCH_LOTFIX_v1_4_COSIGN_ZH.md`（CONDITIONAL：P0 0、P1 1、P2 6、P3 3）：P1-1、P2-1…P2-6、P3-1、P3-3，以及 Arch 关于 β 和 MILP 的附注；
    - Beta 会签 `BETA_LOTFIX_V1_4_COSIGN_ZH.md`（PASS_WITH_AMENDMENTS）：L1–L6，以及两袖耦合与 M4 的措辞更正。
    - 机制、常量和已批准的 80% 都没有改。
- **流程（Arch P2-6）**：今后本草案每次修订之前，先把当前版本按 sha 命名存入 `docs/v2/audit/snapshots/`，并核对 sha，然后才改。r2→r3 已按此执行。
- **性质：看过 v1.3 非收益失败序列后提出、只前瞻生效。**
  - 起草时没有计算、也没有看过任何 v1.3 收益。
  - 本草案不追溯 v1.3，不改 v1.3 的任何产物或结论。
- 起草：QuantLab Strategy，2026-10-18 ET。
- 依据：
  - 主 Agent 2026-10-18 00:46 ET 对诊断的裁定：采纳 S1/S3/S5 和落盘；不采纳 S2/S6/现金 3%；S10 属 Leo mandate；S4 留作后手。
  - 主 Agent 00:46 ET 经 Arch 转达的裁定：整手后口径和 40% 硬帽，见 §6。
- 诊断依据：`docs/v2/STRATEGY_CORE_100W_LOT_FEASIBILITY_DIAG_ZH.md`（sha256 `fcc2931262751525bb90aca46737648a84568be4249aa76bf8ae4a5bc7baf576`）。
- 本文是 **v1.4 草案**。按既定规则，v1.3 是最后一次实现修复。v1.4 是否实施，以 v1.3 记分卡出来后主 Agent 的书面决定为准。若 v1.3 记分卡显示 Core 输给 B，诚实结论照常成立，本草案不得用来推翻或稀释那个结论。
- **证据地位（Arch P2-1）**：
  - v1.4 在 X2 上的结果**只算「在口径 C 下复现、修复有效性的诊断」**，不算新证据，也不得用来比较 Core 与 B 的优劣，从而推翻 v1.3 记分卡的结论。
  - 晋级只看 2026-11-02 起的 FWD。
  - v1.4 之后，**不再在同一个 X2 上做任何整手层修订**。

## 0. 引用而不修改的冻结 / 已定文件

| 文件 | sha256 | 本草案与它的关系 |
|---|---|---|
| `STRATEGY_OPTIMIZER_STAGE2_PREREG_DRAFT_ZH.md` | 3ab622b3bccf07969a21d1f226f5c210a7d3a6703f30d56af81508f53753c4ce | Stage2 执行层（S2-3 不交易带）。本草案只改整手层，不动它 |
| `STRATEGY_OPTIMIZER_STAGE2_S2_3_DRAFT_ZH.md` | 7ee72195cdc092d69ab40239bef43c057f151d9df1e452a5c990c21ae54e89dc | S2-3 冻结规格。v1.4 整手结果作为 S2-3 的 w_target 输入，S2-3 规则不变 |
| `STRATEGY_OPTIMIZER_STOPRULE_CONSEC_DRAFT_ZH.md` | 41f29825c85a66c889474460605b45a19f5fa475ae46570f299416535cb3559b | 连续失败停跑规则（k=3，M1–M6）。v1.4 适用它，失败日定义以它为准 |
| `STRATEGY_OPTIMIZER_PREREG_DRAFT_ZH.md`（FROZEN 正文） | 020a64f58e91cddb2a6c2d79b6dafd84c669981f6aa286f0bffcee0627220488 | §3.4 降级序、§3.5 整手算法、§3.7 换手硬帽。本草案在 v1.4 中对它们做修订（见 §2–§6） |
| `STRATEGY_OPTIMIZER_PREREG_AMEND_v1_3_ZH.md` | 278bc4019041fc5d52e5060667500a14b46063ed977e126a5c78a8dd1a4f3502 | v1.3 规则①–④。除本文明确修订的部分外，全部沿用 |
| `ARCH_OPTIMIZER_CORE_v1_3_RESIGN_ZH.md` | bd8b23f66ec9e65eed89c4a48d9529ecdb1fc687a6cf1ce4f4348ab5f7e83dff | Arch P1-R1（口径 A/B/C）、P1-R2（40% 硬帽）、P2-4（失败原因细分） |

## 1. 常量（全部不变，写死）

- λ_risk = 117.213（117.21317483995702），λ_turn = 0.6 / 0.6（60万 / 100万）。不重标。
- 单票上限：60万 6%，100万 5%。
- 行业：相对全池 wb ±8%（+slack ≤1pp），绝对 ≤20%（不享受 slack）。
- Size/MidCap：±0.35σ（+slack ≤0.05σ）。β：±0.10（无 slack）。
- 名数 20–30，求解阶段单票下限 2%。现金 ≤2%（K2：硬约束优先于现金，现金 >2% 记 LOT_CASH_GT2，只披露）。
- 调仓：`month_end_plus_first_last`。
- 池子：HI_LIQ_V1.1（掩码 sha c5433e80…9af）。行业基准：全池 wb（IND_POOL）。
- **基准不随预筛变化（Beta L2）**：以下各项一律在**完整 HI_LIQ 池**上计算，包含 S5 剔除的名字和 cap_lot=0 的名字：
  - wb（全池流通市值基准）；
  - bb（wb 加权的 β 基准）；
  - Size/MidCap 的标准化（均值和标准差）及其 wb 加权的基准值 zb、mb；
  - 行业 wb。
  S1/S5 只改变求解候选集和逐票上限，不改变池子和基准。
- 口径：①（equity_100，预算 B=1.0）、②（equity80_etf20_510300，股票预算 B=0.8，510300 固定 0.20、不取整）。
- 窗口：sealed 2018-01-02→2024-05-31，X2 2024-06-03→2026-10-09，FWD 自 2026-11-02 起。X2 不得用于晋级。
- 两袖共用同一个求解解，任一袖整手失败则该档两袖同时沿用（v1.3 第 355 行逻辑保留，因为 S6 不采纳）。

## 2. 记号

| 记号 | 含义 |
|---|---|
| A | 档位 AUM（600,000 或 1,000,000） |
| c_A | 单票上限（0.06 或 0.05） |
| s ∈ {①,②}，B_s | 口径及其股票预算（1.0 / 0.8） |
| L_i | 每手股数：688/689 开头为 200，其余 100 |
| P_i | 调仓日 PIT 收盘价（向前回看 ≤10 个自然日，取最后一笔，与 v1.3 相同） |
| u_i = L_i·P_i / A | 一手占 NAV 的比例 |
| w_i | 求解器股票簿权重（Σw=1） |
| x_i^s = B_s·w_i | 口径 s 下该票的 NAV 目标权重 |
| ε = 1e-6 | 取整容差，单位是手 |

## 3. S1：整手感知单票上限（lot-aware cap）

### 3.1 公式
对每只票 i、每个口径 s：

- 最大可持手数：m_i^s = floor( c_A·B_s·A / (L_i·P_i) + ε )
- 口径 s 的整手上限（NAV 层）：cap_i^{s,lot} = m_i^s·u_i。在容差内有 cap_i^{s,lot} ≤ c_A·B_s + ε·u_i（Arch P3-1）：只有当 c_A·B_s·A/(L_i·P_i) 落在 [m−ε, m) 时才会多取一手，超出量 ≤ ε·u_i ≈ 1e-6 手，可以忽略。实现时若要严格不超，可对该票改用不带 ε 的 m，二者择一须在代码审查时写死。
- 求解器（股票簿）的单票上限：**w_i ≤ cap_i^{lot} := min_s ( cap_i^{s,lot} / B_s )**。两袖共用一个解，所以取两袖中较紧的一个。
- 这仍是逐票线性上界，不改变问题的凸性。HARD 单票 c_A 不变：除 ε 容差外，cap_i^{lot} ≤ c_A，只会更紧，不会更松。
- **下限不会高于上限（Arch P2-5）**：记 T = c_A·B_s·A，u' = L_i·P_i。
  - 对候选集内的票（S5 已保证 u' ≤ T，即 m ≥ 1），由 floor 的定义，m·u' > T − u'，所以 (m+1)·u' > T。
  - 又因为 m ≥ 1，所以 2m ≥ m+1，于是 2m·u' ≥ (m+1)·u' > T，即 m·u' > T/2。
  - 两边除以 A·B_s，得 cap_i^{lot} > c_A/2。60万 为 3%，100万 为 2.5%，都大于 2% 的求解下限。
  - 所以 S1 不会造成「下限 2% > 单票上限」导致的单票不可行。
- **S1 削减上限的风格倾斜（Beta L3，事前参考）**：
  - Beta 用 v1.3 X2 求解支撑集复算：上限被削比例 h_i 与 ln(价格) 相关 0.71，与 Size z 相关 0.16，与 β_i 相关 0.20（逐日中位数）。也就是说，S1 系统性压低高价、偏大盘、偏高 β 名字的权重上限。
  - 100万 支撑集的 Σcap_lot 均值 0.943（区间 0.821–1.043），每日顶格名 17.1 只，被削比例均值 8.0%（最大 13.6%）。所以 S1 下 100万 的 K=20 几乎必然不可行。60万 Σcap_lot 均值 1.13（最小 1.04）。
  - Size 和 β 的 HARD 仍由求解器保证，不会违约。但这是 α 取样上的倾斜，须逐期披露（§7.7）。
- 对 m_i^s = 0 的票，cap 为 0，等价于 §5 的预筛剔除。由 S5 先剔掉，不进求解。

### 3.2 与整手取整、补手的关系
- **取整**：q_i^s = floor( x_i^s·A / (L_i·P_i) + ε )·L_i。
  - 加 ε，是为了防止求解器把顶格解返回成 cap−1e-12 时被 floor 少取一手。
  - 加 ε 后不会超过上限：x_i^s ≤ B_s·cap_i^{lot} ≤ cap_i^{s,lot} = m_i^s·u_i。
- **结果**：顶在 cap_i^{lot} 的名字取整无损（残差 0）。诊断 §1 所说的「顶格名一手都补不回」被消除。
- **修复与补手**：风格修复和现金补手的加仓条件写成「q_i^s + L_i ≤ m_i^s·L_i」。这与 v1.3 的「c_i + u_i ≤ c_A·B_s」在整数手意义上等价，不放宽，只写成手数形式以避免浮点歧义。
- **K=20、100万 的角点**：Σ_i cap_i^{lot} < 1 时（除非 20 只的价格恰好整除，几乎不会发生），K=20 求解不可行，按现有 K 循环自动升 K（§4 的 S3 也覆盖）。这不是新增参数，完全由价格和上限推出。
- **预期影响（不承诺数值）**：
  - 100万 的 K 会系统性上升。
  - 60万 在 K=20 时 Σcap 约为 120%，基本不受影响。
  - 换手与分散度可能上升，逐期披露。

## 4. S3：整手阶段失败时升 K

### 4.1 什么算「整手阶段失败」
在某个 K 下求解成功后，按 §3/§5/§6（口径 C）对两袖做整手、修复、补手。以下任一袖出现即为整手阶段未达标：
- **LOT_HARD_FAIL**：名数 <20、行业（上界/下界/绝对）、Size、MidCap、β 任一超界（按口径 C，含所用 slack）；
- **LOT_CASH_GT2**：硬约束都满足但现金 >2%。

两者都触发 S3 重试。理由：诊断显示 100万 的现金超 2% 和风格失败同源，都来自顶格角点。

**现金触发的性质（Arch P1-1，写死）**：
1. **这是 v1.4 对 K2 执行方式的修订。**
   - K2 规定的是优先级：硬约束优先于现金 ≤2%。v1.1–v1.3 的执行方式是「现金超限即放弃，只披露」。
   - v1.4 改为：在硬约束都满足的前提下，在 K ≤30 范围内尝试满足 CASH_MAX=2%。
   - 因此，原本只披露的现金超限事项，在 v1.4 中**会改变持仓**（选中更大的 K）。
   - K2 的优先级本身不变：任何 K 下都不以违反硬约束为代价换取现金 ≤2%。
2. **现金触发不影响失败日判定。** 失败日仍只由求解阶段 INFEASIBLE 或整手阶段 LOT_HARD_FAIL 决定（停跑规则 §2/M3）。现金 >2% 的日子，无论是否升 K，都不算失败日。
3. **单列披露「只因现金升 K」的日子**：即在 K_sel 上两袖硬约束都满足、只有现金 >2%、因而触发 S3 的日子（s3_trigger=cash）。逐日报告：
   - 天数；
   - K 增量 ΔK = k_final − K_sel；
   - 这些天的换手：求解单边换手，以及整手后目标到目标的换手 0.5·Σ|w_post−w_cur|；
   - 并列给出不升 K 时（K_sel 那次尝试）的同口径换手，作为对照。

   不升 K 时的换手直接取自 attempt 落盘，不另做求解。

### 4.2 K 的步长、顺序与上限（写死）
- **步长 +1，只向上**。降 K 会加重 Σcap 角点，所以不向下。
- **硬上限 K_max = 30**（= NEFF_HI，不得超过）。
- **重试集合**：{K_sel+1, …, 30}，去掉当日求解阶段已证实不可行的 K。K_sel 是现有循环选中的 K。
- **每个 K 内**仍然走现有的 slack 阶梯：(0,0) → (0.05σ, 0.5pp) → (0.05σ, 1pp)，每个 K 最多 3 次求解。
- **重试次数上限**：每档每日最多 (30 − K_sel) 个 K，即 ≤10 个 K、≤30 次额外求解。超过即停。
- 每个 K 的支撑集都按 v1.3 规则取 step-1 解 |w| 降序的前 K 名（并列按代码排序）。不重新做 step-1，不改选股主准则。

### 4.3 与现有降级序的先后（v1.4 写死）
1. 现有求解循环：K 从 k0 起，求解不可行时先在该 K 内走 slack 阶梯，再升 K（到 30 为止），再从 k0−1 降到 20。规则不变，只是单票上限换成 cap_i^{lot}。
2. 在选中的 K_sel 上做整手（S1/S5，口径 C）。两袖都严格 OK（硬约束满足且现金 ≤2%）→ 采用。
3. 否则进入 **S3**：按 §4.2 依次试 K_sel+1…30，**采用第一个两袖都严格 OK 的 K**。
4. 若没有严格 OK 的 K：在所有试过的 K（含 K_sel）里，**采用最小的、两袖硬约束都满足的 K**。这时现金 >2%，记 LOT_CASH_GT2，按 K2 只披露。
5. 若连硬约束满足的 K 都没有 → LOT_HARD_FAIL，沿用上期持仓（首日无上期则全现金），计为失败日（停跑规则 §2/M1）。
6. **β ±0.15 后备在 v1.4 不启用为可行判定**，只做影子披露（§7.5）。所以 v1.4 不产生 SOFT_BETA15 日。若主 Agent 日后要启用，须另行预注册，并按停跑规则 M1 记为失败日。
7. 冻结正文 §3.4 降级序中的「Full 域预算」不适用于 Core；「权益降仓到现金」在 v0–v1.3 没有实现，v1.4 也不实现。如实写明，不另造步骤。

所有尝试都写入 §7 的落盘字段（每个 K 一条 attempt 记录）。

### 4.4 S3 救回日、失败阶段与 K 路径的披露
- **S3 救回日（Arch P2-2，参照停跑规则 M1）**：
  - S3 救回的日子在硬约束下是可行的，没有放宽任何约束，所以**不算失败日**。这与 β 0.15 救回不同，后者按 M1 算失败日。
  - 但须单独计数，并分两类：
    - `s3_rescued_from_hard`：K_sel 上任一袖 LOT_HARD_FAIL，升 K 后两袖硬约束都满足；
    - `s3_rescued_from_cash`：K_sel 上只有现金 >2%，升 K 后严格 OK。
  - 对每个救回日，标出它在「假如不救回就会形成的失败连续段」中的位置：段首、段中、段尾或孤立。并报告：若不救回，停跑规则 k=3 是否会触发。
  - `s3_rescued_from_cash` 本来就不算失败日，所以只标它在「失败或现金 >2%」连续段（M3）中的位置。
- **K 分布与有效名数**：逐期披露 K_sel、k_final 的分布，Neff = 1/Σw²（求解权重和整手后权重各一份），以及 S3 带来的 Neff 变化。
- **S3 路径（Beta L5）**：逐期披露 k_trace（试过的 K 及各自结果）、k_final、s3_used、s3_trigger ∈ {hard, cash}，以及 S3 带来的换手和 Neff 变化（与 K_sel 尝试对照）。
- **失败按阶段拆分（Arch P2-4）**：
  - 失败日分两类：**求解阶段**（INFEASIBLE：K 循环内所有 K 和 slack 都不可行）和**整手阶段**（LOT_HARD_FAIL）。两类分别披露，**都计入停跑规则**。
  - 注意：S1 收紧了逐票上限，会把 v1.3 中的部分整手阶段失败**转移到求解阶段**（例如 100万 K=20 角点在 S1 下直接求解不可行）。所以 v1.3 与 v1.4 的失败数要按阶段合计比较，不能只比较整手阶段。
- **关于 β（Arch 附注）**：
  - Arch 指出，v1.3 中 100万 整手前求解权重的 β 越界为 0，而 25 个失败日中有 18 天 β 是在整手和修复之后被打破的（按口径计：① 15、② 9）。
  - 根因仍是整手角点（顶格名补不回、修复没有可加仓名）。S1 拆掉角点，S3 增加修复余地，机制上对症。
  - 但 **S1 不直接约束整手后的 β，S3 升 K 也不保证 β 回到界内**。效果须实测，事前不作承诺。§7.2 的 post_floor 和 post_repair 两个阶段的 beta_act 落盘，用于事后拆分 β 失败原因。
- **MILP 抛光原型（Arch P3-2）**：是 Arch 的单独提议，用于界定 round-and-repair 相对整数最优损失了多少可行率。它须单独预注册，并经 Arch 授权才能运行，只作对照，**不替换 v1.4**，也不得在 v1.4 冻结后据此改规则。S4 仍是留作后手的选项，是否列入后续版本由主 Agent 决定。

## 5. S5：分袖一手预筛

- **口径 s 的门槛**：T_{A,s} = c_A·B_s·A。
  - 60万：① ¥36,000，② ¥28,800。
  - 100万：① ¥50,000，② ¥40,000。
- **单袖剔除条件**：L_i·P_i > T_{A,s}（P_i 为 §2 的 PIT 收盘价；无价格的票照 v1.3 处理，不剔除，记 no_price）。
- **共用求解的候选集**：由于两袖共用一个求解解（S6 不采纳），候选集 = 两袖预筛都通过的票，即按 ② 的门槛 L_i·P_i > c_A·0.8·A 剔除。
- **与 S1 一致**：S5 剔除的票恰好就是某一袖 m_i^s = 0 的票，所以 S1 的 cap_i^{lot} 在候选集内恒 >0。
- **只因 ② 被剔的票**（L_i·P_i 落在 (0.8·c_A·A, c_A·A] 区间）单列披露。诊断给出的 X2 池内每日中位数是 60万 11 只、100万 6 只，作为事前参考。
- **代价（如实写明）**：① 的候选池也随之缩小。不采纳「两袖分别求解」（那等于 S6 的一部分），也不为 ① 单独放宽。
- **① 缩池的系统性偏向（Arch P2-3 / Beta L3）**：
  - 按 ② 的门槛剔除，对 ① 是**系统性缩池**，而且偏向剔除高价股。
  - Beta 的 v1.3 复算（逐日中位数）：被 S5 剔除的名字 Size z 均值 +1.2 / +1.3，β 均值约 1.65（1.67 / 1.64），占全池 wb 的 5.1%（60万）/ 1.6%（100万）。
  - 以下各项列为**披露项**，**只在获得运行授权后计算**，现在不算：
    1. 只因 ② 被剔、而在 v1.3 中被 ① 实际持有的票：票数、它们在 v1.3 ① 中的持仓权重合计（逐日和均值）；
    2. 被剔名字的行业分布（申万一级）和 wb 加权的 β、Size、MidCap 倾斜；
    3. 被剔名字占全池 wb 的比例（逐期）。

## 6. 整手后硬约束口径与换手硬帽（主 Agent 00:46 ET 经 Arch 转达的裁定；替换原占位）

### 6.1 整手后硬约束口径（Arch P1-R1）
- **v1.3（本轮）**：放行判定用 **口径 A（代码口径）**，记分卡并列披露口径 B 和 C 的越界和翻转天数。v1.3 本轮通过**只是入场券**，不代表整手后口径问题已经解决。
- **自 v1.4 起**：放行判定改用 **口径 C**（股票袖按预算归一）。求解器、整手修复、补手和最终判定四处统一用 C。
  - 口径 s 下，风格和 β 的主动暴露为 E_s(x) = (Σ_i x_i^{s,lot}·x_i)/B_s − x_b（x 为 Size z、MidCap m 或 β；x_b 为全池 wb 加权基准值；现金留在分母里、暴露为 0；510300 不进 HARD）。界为 ±0.35σ（+slack）、β ±0.10。
  - 行业：G_g^s = Σ_{i∈g} x_i^{s,lot}，要求 G_g^s/B_s − wb_g ≤ 8%+slack，wb_g − G_g^s/B_s ≤ 8%+slack，G_g^s/B_s ≤ 20%（与 v1.3 代码口径一致）。
  - ① 的 B=1，C 与 A 相同。差别只在 ②：A 把 510300 当作基准暴露，相当于把股票袖的风格/β 界放宽到 0.4375σ / 0.125。C 取消这个放宽。
  - 与求解器口径一致：求解器在股票簿（Σw=1）上约束暴露，取整前 E_s 恰好等于求解器暴露。C 只是把这一口径延续到整手之后。
- **口径 B（股票部分归一，现金不进分母）**：v1.4 继续只披露，不作判定。
  - Arch 在 `ARCH_OPTIMIZER_CORE_v1_3_RESIGN_ZH.md` §3 指出，B 下除了行业越界，**β 和 MidCap 也越界**：β 21–28 行，最大超出 0.046；MidCap 7–12 行，最大超出 0.164σ。
  - Strategy 此前「按披露口径只有行业越界」的说法不完整，这里更正。
- **事前提示（不作承诺）**：Arch 在 v1.3 上的复算显示，改用 C 会让可行行翻成不可行：60万 全样本 27 / X2 10，100万 全样本 18 / X2 5，全部在 ②。所以 v1.4 在 C 下对 ② 更严，S1/S3/S5 的改善有一部分会被它抵消。这一点在 §8 的升级门槛里一并考虑，不另设宽限。

### 6.2 单边换手 40% 硬帽（Arch P1-R2）
- 冻结正文 §3.7 写着「单边换手硬帽 ≤40% NAV/再平衡」，但 v0–v1.3 从未执行（代码 `TURN_HARD_CAP=0.40` 只是监控项）。
- **裁定：监控项，只披露。自 v1.4 起从规格中删除硬帽表述**，改为监控。
- 每期披露两种换手超过 40% 的天数：求解权重的单边换手，以及整手后目标到目标的换手 0.5·Σ|w_post−w_cur|。
- S3 升 K 可能抬高换手。按升 K 与否分组披露，但不因此设上限，也不调 λ_turn。

## 7. 落盘字段（诊断 §6 列出的 5 项缺失；只落盘，不改算法）

所有文件放在 v1.4 输出目录，键为 (date, aum, sleeve, K, attempt)。attempt 从 0 起，按 §4.3 的尝试顺序编号；sleeve=SOLVER 表示求解层。失败日和成功日**都要落盘**，每个尝试过的 K 都要落盘。

### 7.1 `core_v1_4_attempt_weights.parquet`：失败日与各次尝试的求解权重
| 字段 | 类型 | 说明 |
|---|---|---|
| date, aum, K, attempt | date/int | 键 |
| solver_status | str | optimal / optimal_inaccurate / infeasible |
| size_slack, ind_slack | float | 该次所用 slack |
| instrument | str | 支撑集内的票 |
| w_solver | float | 股票簿求解权重 |
| cap_lot | float | §3.1 的 cap_i^{lot} |
| lot, price, u | int/float | L_i、P_i、u_i |
| sleeve | str | ① / ② |
| q_floor, q_final | int | 取整后手数、修复补手后手数 |
| x_lot | float | 整手后 NAV 权重 |
| at_cap_lot | bool | w_solver ≥ cap_lot − 1e-9 |
| selected | bool | 是否为最终采用的 attempt |
| beta_i | float | 逐票 β（与求解所用相同） |
| size_z_i, midcap_m_i | float | 逐票 Size z、MidCap m（全池标准化，Beta L2/L4） |
| sw_l1 | str | 逐票申万一级行业 |
| s3_trigger | str | none / hard / cash（Arch ⑥） |

### 7.2 `core_v1_4_style_components.csv`：风格三分量
| 字段 | 说明 |
|---|---|
| date, aum, sleeve, K, attempt, stage | stage ∈ {solver, post_floor, post_repair, final} |
| basis | A / B / C（三种都写；判定用 C） |
| size_act, size_bound, size_excess | 主动暴露、界（0.35+slack）、超出量（≥0） |
| midcap_act, midcap_bound, midcap_excess | 同上 |
| beta_act, beta_bound, beta_excess | 界 0.10 |
| cash | 该口径下的现金 |

### 7.3 `core_v1_4_industry_detail.csv`：行业越界明细
| 字段 | 说明 |
|---|---|
| date, aum, sleeve, K, attempt, stage, basis | 键 |
| sw_l1 | 申万一级代码（含无入选票的行业） |
| G, wb_g, active | 行业权重（按口径归一）、全池基准、主动偏离 |
| bound_rel, bound_abs | 8%+slack、20% |
| breach_type | none / upper_rel / lower_rel / abs |
| excess | 超出量（≥0） |

### 7.4 `core_v1_4_repair_trace.jsonl`：修复轨迹
每一步一行：date, aum, sleeve, K, attempt, step, phase（floor / style_repair / cash_topup）, action（add / sell / swap / none）, add_inst, rem_inst, lots, excess_before, excess_after, cash_before, cash_after, n_names。每个 phase 结束再写一行 stop_reason（excess_zero / no_candidate / cash_le_2pct / iter_cap_300 / cap_lot_block）。

### 7.5 `core_v1_4_beta15_shadow.csv`：β 0.15 影子披露（不参与判定）
| 字段 | 说明 |
|---|---|
| date, aum, sleeve, K, attempt | 键 |
| beta_act_C | 口径 C 的 β 主动暴露 |
| pass_beta010, pass_beta015 | 是否满足 ±0.10 / ±0.15 |
| other_hard_pass | 除 β 外其它硬约束是否都满足 |
| beta15_would_rescue | other_hard_pass ∧ ¬pass_beta010 ∧ pass_beta015 |

影子披露不另做 β=0.15 的求解，只对已有尝试的整手结果做判定。

### 7.7 逐日基准值与沿用日暴露（Beta L4）
- `core_v1_4_daily_bench.csv`（每个调仓日、每档一行）：date, aum, bb, zb（wb 加权 Size 均值）, mb（wb 加权 MidCap 均值）, size_mu, size_sd, mid_mu, mid_sd（全池标准化参数）, beta_window_start, beta_window_end, beta_window_n（β 估计窗）, pool_n, n_prefilter, n_prefilter_sleeve2_only, wb_share_prefiltered, wb_beta_prefiltered, wb_size_prefiltered, caplot_cut_sum, corr_cut_lnprice, corr_cut_size, corr_cut_beta（S1/S5 倾斜，Beta L3）。
- `core_v1_4_carry_exposure.csv`（沿用日）：date, aum, sleeve, basis（A/B/C），以及**实际持有的那本书**的 size_act, midcap_act, beta_act, ind_active_max, ind_abs_max, cash, carry_n_out_of_pool, carry_out_of_pool_names。延续 v1.3 的 carry_drift，扩展到三种口径。

### 7.8 失败原因细分（Arch P2-4）
disclosure 的 `lot_fail_reason` 改为多值枚举：names / industry_upper_rel / industry_lower_rel / industry_abs / size / midcap / beta；另列 cash_gt2。新增列：`fail_stage` ∈ {solve, lot}、`k_trace`（试过的 K 和各自结果）、`s3_used`（bool）、`s3_trigger`、`k_final`、`s3_rescued_from_hard`、`s3_rescued_from_cash`、`neff_solver`、`neff_lot`、`n_prefilter_sleeve2_only`（只因 ② 被剔的票数）。

## 8. 升级门槛：「S1+S3+S5 之后 100万 仍不可行」的事前定义（✅ 主 Agent 2026-10-18 00:51 ET 批准 80%，此后不得再改）

- **提议门槛（需主 Agent 批准后才生效）**：在 v1.4 的 X2 正式运行中（29 个调仓日，排除无数据日），按**口径 C** 的**严格可行**（硬约束满足且现金 ≤2%，按记录状态，含两袖耦合），满足以下任一条即判定「100万 仍不可行」：
  1. 100万 ① 或 ② 任一口径的严格可行率 **< 80%**（即 <24/29；24/29 = 82.8%）；
  2. 按停跑规则（k=3，M1–M6）在 X2 上 100万 会触发停跑。
- **触发后**：主 Agent 向 Leo 报告，由 Leo 决定是否考虑 S10（100万 单票上限改为 6%，属 mandate 变更）或其它 mandate 选项。Strategy 不提出 S10，不预先实施。S4（MILP 抛光）留作后手，是否启用由主 Agent 决定。
- **80% 的来历（如实披露）**：取自 v1.3 60万 X2 的严格可行水平（① 82.8%、② 86.2%，口径 A），意思是「100万 至少达到 60万 现有水平」。它是在看过 v1.3 非收益失败序列后提出的，不是独立先验。备选值：70%（较宽）或 90%（较严）。**主 Agent 2026-10-18 00:51 ET 书面批准 80%**：X2 口径 C 严格可行（含两袖耦合），100万 任一口径 <24/29 天，或 k=3 停跑触发，即判「100万 仍不可行」，由主 Agent 报 Leo 谈 6% 上限。理由：与 60万 ① 已观测水平对齐、两档同标；选择风险已披露。**此数写入后不得再改。**
- 不以收益作门槛。门槛只看 X2，sealed 只披露。60万 在 v1.4 下若变差（例如 S5 缩池、口径 C 更严），单独披露，不纳入这一门槛。
- **口径错配披露（Beta L1；80% 不改）**：
  - 80% 的参照是 v1.3 60万 X2 在**口径 A** 下的严格可行水平（① 24/29 = 82.8%，② 25/29 = 86.2%），而 §8 的判定用**口径 C**。
  - Beta 拿 v1.3 按口径 C、含两袖耦合复算，严格可行天数为：60万 ①/② 都只有 **15/29（51.7%）**；100万 ① 5/29、② 7/29。也就是说，在口径 C 下，连 60万 也达不到 80%。
  - 因此：
    1. v1.4 运行时**同时报告 60万 的口径 C 严格可行率**（①、②，含耦合）；
    2. 若 60万 在 v1.4 下也 <80%，主 Agent 报 Leo 时须写明：**不可行不能只归因于 100万 的 5% 上限**。口径 C 下 ② 的 β/MidCap 收紧是共同原因，S10（6%）不是唯一选项，也未必能解决。
  - 80% 由主 Agent 00:51 ET 批准，已冻结，本条不改数值，只补披露。
- **同口径比较（Beta L6）**：v1.3 按口径 C 重算的可行性，只用于和 v1.4 做同口径（C 对 C）的并列比较，不改变 v1.3 按口径 A 的放行判定和记分卡结论。v1.3↔v1.4 只在同一口径下比较（C 对 C、A 对 A）。

## 9. 明确不采纳（主 Agent 00:46 ET）
- **S2**（Σcap ≥1+h 的名数下限）：h 是自由参数，容易被调。
- **S6**（两袖解耦判定）：会机械地抬高可行率。runner 的两袖耦合保留，即当日任一袖整手失败则两袖同时沿用（v1.3 runner 第 355 行）。注意：这与停跑规则 M4 是两回事。M4 管停跑范围（按档同停），不影响逐日状态；M4 也不变。
- **现金上限放宽到 3%**：直接贴合观测值，改变「严格」的定义。
- **S10**（100万 上限 6%）：属 Leo mandate，现在不提，只作 §8 触发后的上报选项。
- **S4**（MILP 抛光）：留作后手，不在 v1.4。
- 不调 λ，不改任何约束数值，不改调仓频率，不改选股主准则。

## 10. 运行前提（全部满足前不得运行，包括 smoke 和单日测试）
1. v1.3 记分卡出来：按 RUN_AUTH → 重跑 → Arch 复签 → `ARCH_RESIGN_A_v1_3.ok` → RESIGN → Eng 的顺序走完。
2. 主 Agent 书面决定启动 v1.4（见文首关于「Core 输给 B」的约束）。
3. 本草案完成 Arch 与 Beta 会签，主 Agent 冻结，并批准 §8 的门槛。
4. v1.4 runner 和求解代码经 Arch 审过，sha 写入授权。现行 v1.3 runner b6238254 已经 Arch 复审 PASS（smoke 隔离修复 r2，仅限 v1.3）；v1.4 的改动会产生新 sha，须重新审。
5. Arch 写好的运行授权文件（例如 `ARCH_RUN_AUTH_v1_4.ok`）存在。**Strategy 永远不创建 Arch 的 .ok 文件。** 任何测试或 smoke 也都要先问 Arch。
6. 新的 ckpt 目录必须是空的。不得复用或覆盖 `_ckpt_v1_3_poolind/`。v1.3 产物一律不动。

## 11. Arch / Beta 会签栏

**Arch 和 Beta 的行只由 Arch 和 Beta 本人填写，Strategy 不得代填**（Arch P3-3）。以下事实记录写在表外：
- Arch：`docs/v2/ARCH_LOTFIX_v1_4_COSIGN_ZH.md`，对 r2 a1a2552c 给出 PASS_WITH_AMENDMENTS（P0 0、P1 1、P2 6、P3 3）。r3 已按其文字补上。
- Beta：`docs/v2/BETA_LOTFIX_V1_4_COSIGN_ZH.md`，对 r2 a1a2552c 给出 PASS_WITH_AMENDMENTS（L1–L6，Beta 写明「随文字补充生效，无需再审」）。r3 已按其文字补上。
- 主 Agent：§8 的 80% 已于 2026-10-18 00:51 ET 书面批准（已报告的事实）。冻结待定。

| 会签方 | 结论 | 时间（ET） | 所签版本 sha | 备注 |
|---|---|---|---|---|
| Arch | | | | |
| Beta | | | | |
| 主 Agent | | | | |

## 12. 声明
本草案只是文字：没有运行任何优化器、回测或求解器，没有计算收益，没有修改任何 v1.3 产物、预注册、runner、冻结文档或停跑规则文件。
