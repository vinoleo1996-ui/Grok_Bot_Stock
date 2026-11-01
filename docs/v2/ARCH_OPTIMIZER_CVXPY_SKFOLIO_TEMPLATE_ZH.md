# 优化器可落地模板（cvxpy / skfolio / Riskfolio）— Arch → Strategy

- 起草：2026-10-14 ≈08:02 ET（Arch）
- 读者：Strategy（实现）；Eng（冲击标定与 book-smoke）；Beta（\(\Sigma\)/硬约束共签）；AI/Alpha（α 向量）
- 对齐：`STRATEGY_OPTIMIZER_PREREG_DRAFT_ZH.md`、`ARCH_INDUSTRIAL_PILLARS_SPEC_ZH.md`、Leo **07:56 / 07:58**、`BETA_BUDGET_MDD25_FOR_COMBO_ZH.md`
- **明确不改**：`FROZEN_CONFIG`、capacity_adv / B4 / S6 **纸面轨**、HI_LIQ 冻掩码（无 dated V2 不得动）
- **约束**：`live=false`；禁 GP；不虚构数据；确认 FROZEN 前**禁止**把本模板产出当晋级 NAV

开源证据（实现选型）：

| 库 | URL | 用途 |
|---|---|---|
| cvxpy | https://github.com/cvxpy/cvxpy · https://www.cvxpy.org/ | 主求解器：二次风险 + L1 换手 + 凸代理冲击 |
| skfolio | https://github.com/skfolio/skfolio | CPCV / walk-forward 组合层防过拟合验收 |
| Riskfolio-Lib | https://github.com/dcajasn/Riskfolio-Lib | CDaR/MaxDD 风险度量与风险预算（对照/压力，非必须进日频主循环） |
| sklearn LedoitWolf | https://scikit-learn.org/stable/modules/generated/sklearn.covariance.LedoitWolf.html | \(\Sigma\) V1 收缩协方差 |
| PyPortfolioOpt | https://github.com/PyPortfolio/PyPortfolioOpt | 可选：HRP/协方差工具对照 |
| pysystemtrade | https://github.com/pst-group/pysystemtrade | buffer / 无交易区概念对照 |

仓库内已有：`quantlab.config` 的 `lw_shrinkage`；引擎 `sqrt_impact_cost`（**终判**仍用 strategy_v1；优化内用 \(3/2\) **代理**）。

---

## 1. 目标函数（写死）

\[
\max_{w}\; \alpha^\top w - \lambda_{\mathrm{risk}}\, (w-w_b)^\top \Sigma (w-w_b) - \lambda_{\mathrm{tc}}\,\mathrm{TC}(w-w_0) - \lambda_{\mathrm{crowd}}\,\mathrm{Crowd}(w)
\]

等价 cvxpy 最小化形式：

\[
\min_w\; -\alpha^\top w + \lambda_{\mathrm{risk}}\, \mathrm{quad\_form}(w-w_b,\Sigma) + \lambda_{\mathrm{tc}}\,\mathrm{TC} + \lambda_{\mathrm{crowd}}\,\mathrm{Crowd}
\]

| 符号 | V1 提案（与 Strategy DRAFT 对齐；共签前可微调但须写死单点） |
|---|---|
| \(\alpha\) | 慢因子残差 α（全 investable 池向量）；**禁止** \(\alpha\propto 1/\mathrm{rank}\) |
| \(w_b\) | 中证全指在池内 renormalize；缺失则流通市值加权代理并打标 |
| \(\Sigma\) | Ledoit–Wolf（\(L=120\)）+ 行业哑元结构（见 §3） |
| \(\lambda_{\mathrm{risk}}\) | **1.0**（α 与风险项先同量纲标定后） |
| \(\mathrm{TC}\) | \(\lambda_1\|w-w_0\|_1\) 死区逻辑 + \(3/2\) 冲击代理（§5） |
| \(\mathrm{Crowd}\) | \(\sum_i w_i c_i\) 或 \(w^\top \mathrm{diag}(c) w\) 接口（§4） |
| 仓位 | \(w_i\ge 0\)，\(\sum w_i + w_{\mathrm{cash}}=1\)，L≤1，**禁空禁杠杆** |

---

## 2. 硬约束 / 软惩罚

### 2.1 硬约束（不可违反；不可行则缩域/降仓，不得松约束交差）

| 约束 | V1 取值 | 备注 |
|---|---|---|
| β vs \(w_b\) | \(|\beta_{w,w_b}-1|\le 0.10\) | Beta 共签实现（收益回归或因子暴露） |
| 线性 Size | \(|e_{\mathrm{size}}|\le 0.30\) | 对数市值 z |
| **非线性 Size / MidCap** | \(|e_{\mathrm{mid}}|\le 0.30\) | **防杠铃**；可用 \(z_{\mathrm{size}}^2\) 截面化或 Barra MidCap 代理 |
| 申万一级相对 \(w_b\) | ±2.0% | absolute 兜底任一行业 ≤35% |
| 单票上限 | 100万 **1.0%**；60万 **1.5%** | |
| 单票下限 | 目标 <0.15% → 0 | 求解后投影 |
| 持仓宽度 | 100万 200–400；60万 100–200 | 可用基数惩罚或迭代剔微权 |
| 参与率 | 单日单票 \(|\Delta V|\le 0.6\%\times\mathrm{ADV20}\) | 超出 → 分步建仓（§5） |
| 可选：成份内权重 | ≥60%（相对某指数成分） | **默认关**；指数增强试验才开；开则 dated 修订 |
| 单边换手硬帽 | ≤30% NAV / 再平衡 | |

### 2.2 软惩罚（进目标，不挡可行域）

| 软项 | 形式 | V1 |
|---|---|---|
| 有把握风格 | \(\sum_s \mu_s (e_s - e_s^{\star})^2\) | \(e^\star=0\)（近中性）；\(\mu_s\) 与 Beta 共签单点 |
| 拥挤度 | \(\lambda_{\mathrm{crowd}}\sum_i w_i c_i\) | 见 §4；无可靠 \(c\) 时 \(\lambda_{\mathrm{crowd}}=0\) 并打标 |

---

## 3. \(\Sigma\)：Ledoit–Wolf + 行业哑元 → Barra 类演进

### 3.1 V1（必须与 Strategy/Beta **共签**后写进 FROZEN）

1. 取 investable 池内过去 120 个开市日收益矩阵 \(R\)（PIT；停牌/缺失按 0，**禁止**用未来填）。
2. `sklearn.covariance.LedoitWolf().fit(R).covariance_` → \(\hat\Sigma_{\mathrm{LW}}\)。
3. 行业：申万一级哑元 \(X\)（日度 PIT 成员）。两种等价实现任选其一面共签：
   - **加性**：在二次型中增加 \(\lambda_{\mathrm{ind}}\|X^\top(w-w_b)\|_2^2\)（已有相对行业硬约束时 \(\lambda_{\mathrm{ind}}\) 可小）；或
   - **因子结构**：\(\Sigma \approx B F B^\top + \Delta\)（\(B\)=行业暴露，\(F\)=行业因子协方差，\(\Delta\)=对角特异风险取 LW 对角或 60 日 \(\sigma^2\)）。
4. 数值：对 \(\Sigma\) 做对称化 + 最小特征值地板，保证 PSD。

### 3.2 演进（非本模板范围，仅路线）

+ Size / Non-linear Size / Momentum / Residual Volatility 等风格因子 → 「Barra 类」。**未建成不得在报告写「Barra 模型」**。每次加因子：Arch+Beta dated 共签 + 试验计数 +1。

### 3.3 伪代码（研究脚本级，非生产补丁）

```python
# 仅示意；落地放 research/strategy_optimizer_* ，勿写入纸面 FROZEN 路径
from sklearn.covariance import LedoitWolf
import numpy as np
import cvxpy as cp

def sigma_v1(returns_TxN: np.ndarray) -> np.ndarray:
    lw = LedoitWolf().fit(returns_TxN)
    S = lw.covariance_
    S = 0.5 * (S + S.T)
    eps = 1e-8
    w, V = np.linalg.eigh(S)
    w = np.clip(w, eps, None)
    return (V * w) @ V.T

def solve_day(alpha, Sigma, w0, wb, c_crowd, cfg):
    n = len(alpha)
    w = cp.Variable(n, nonneg=True)
    cash = cp.Variable(nonneg=True)
    dw = w - w0
    risk = cp.quad_form(w - wb, Sigma)
    # 换手 L1（死区用前置投影 / 迭代：|dw|<tau_lo → 固定 0）
    tc_l1 = cfg.lambda1 * cp.norm1(dw)
    # 3/2 冲击：对每个 i 用 cp.power(cp.abs(dw[i]), 1.5) * scale_i（需 DCP 友好写法见 §5）
    impact = cfg.kappa * cfg.impact_expr(dw)  # 见 §5.2
    crowd = cfg.lambda_crowd * c_crowd @ w
    obj = -(alpha @ w) + cfg.lambda_risk * risk + tc_l1 + impact + crowd
    cons = [cp.sum(w) + cash == 1]
    cons += hard_constraints(w, wb, cfg)  # β/Size/MidCap/行业/单票/参与率
    prob = cp.Problem(cp.Minimize(obj), cons)
    prob.solve(solver=cp.OSQP, warm_start=True)  # 或 CLARABEL/ECOS
    return np.array(w.value), float(cash.value), prob.status
```

---

## 4. 拥挤度代理 → 接到惩罚 / \(\Sigma\)

**原则**：V1 只用**可复现、无未来函数**的代理；不声称「看到了同行实盘持仓」。

| 代理 | 构造（PIT） | 接入 |
|---|---|---|
| A. 开源量价多头交集 | 用 3–5 个**已文档化**的公开量价分数（例：反转、高换手、小波动）在 investable 池截面取 Top 分位多头；\(c_i =\) 近 20 日被点名为多头的次数 / 20 | \(\lambda_{\mathrm{crowd}}\sum w_i c_i\) |
| B. 高 α 侧自重叠 | 近 20 个再平衡日，优化器（或慢 α Top 分位）持仓的加权重合度 → 个股 \(c_i\) | 同上；防自己放大拥挤 |
| C. 盘口/高频代理 | **占位**：接口 `crowd_from_l2(state)->c`；无 L2 时返回全 0 并打标 `crowd_l2=disabled` | 不得静默当作有信号 |
| D. 进 \(\Sigma\)（可选） | \(\Sigma \leftarrow \Sigma + \nu\, \mathrm{diag}(c)\) 或低秩 \(c c^\top\) 缩放 | 与加性惩罚二选一为主，避免双计；V1 **推荐只做加性惩罚** |

V1 DRAFT：\(\lambda_{\mathrm{crowd}}=0.25\)（与 α 同量纲标定后）；网格禁止。审计：每日落盘 `c_i` 分位数与 Top20 拥挤票名单。

---

## 5. 双阈值死区 + \(3/2\) 冲击 + 分步建仓

### 5.1 死区（无交易区）

对 \(\delta_i=w_i-w_{0,i}\)：

1. \(|\delta_i|<\tau_{\mathrm{lo}}\) → 强制 0（不交易）
2. \(\tau_{\mathrm{lo}}\le|\delta_i|<\tau_{\mathrm{hi}}\) → 允许，但 \(\lambda_1^{\mathrm{mid}}=1.5\lambda_1\)
3. \(|\delta_i|\ge\tau_{\mathrm{hi}}\) → 正常 \(\lambda_1\)

| AUM | \(\tau_{\mathrm{lo}}\) | \(\tau_{\mathrm{hi}}\) |
|---|---|---|
| 60万 | 15 bp | 40 bp |
| 100万 | 10 bp | 25 bp |

实现建议：先解无死区 → 投影微权 → 再解；或用分段 \(\lambda_1\) 迭代 2–3 次。**两档分别标定，禁止串用。**

### 5.2 \(3/2\) 冲击代理

工业形式（与 Leo 表述一致）：

\[
\mathrm{Impact}_i \propto \left(\frac{|\Delta V_i|}{\mathrm{ADV}_i}\right)^{3/2} \cdot \mathrm{ADV}_i
= \kappa\, |\delta_i|^{3/2}\, \mathrm{NAV}^{3/2} / \sqrt{\mathrm{ADV}_i}
\]

（具体 \(\kappa\) 与 strategy_v1 的 sqrt 冲击同量级标定；Eng 给初值。）

**DCP 注意**：`cp.power(cp.abs(dw[i]), 1.5)` 在 dw 为变量时对 Minimize 通常可用（power≥1 的范数型）；若求解器不稳，用 **分段线性上限** 或 **\(\|\delta\|_2^2 / \sqrt{\mathrm{ADV}}\)** 作保守代理，并在 receipt 注明「非纯 3/2」。

**与引擎关系**：优化内 = 引导；**终判 NAV** = `ExecConfig.strategy_v1`（现网为 **sqrt** 冲击）。报告须并列「优化内 TC」与「引擎成本」。日后若 Eng 增加 3/2 fill 模型，另开预注册，**不改**当前纸面默认。

### 5.3 分步建仓

若 \(|\delta_i| > 0.6\%\times\mathrm{ADV20}/\mathrm{NAV}\) 或 \(>3\tau_{\mathrm{hi}}\)：拆成至多 **3** 个再平衡日均匀执行；快因子门卫可提前终止增持。

---

## 6. skfolio / Riskfolio 验收层（不做选股主循环）

日频权重主循环用 **cvxpy**（约束细、拥挤度/死区好接）。

验收与压力：

| 工具 | 用法 |
|---|---|
| **skfolio** | 对优化器输出的权重路径做 **walk-forward / CPCV**，报告样本外分布；防止「单次 X2 好看」过拟合。文档：https://github.com/skfolio/skfolio |
| **Riskfolio** | 在**同一权重路径**上算 CDaR/MaxDD、风险预算分解，对照 Beta MDD≤25% / 另报≤15%；**不**在 V1 用 Riskfolio 重做日频求解（除非共签改为 CDaR 目标）。 |

验收窗（确认 FROZEN 后才跑）：

| 窗 | 区间 | 标注 |
|---|---|---|
| 密封窗 | 2018-01-02→2024-05-31 | 开发；非晋级；HI_LIQ 密封段偏薄须披露 |
| X2 | 2024-06-03→2026-10-09 | **样本内** |
| 资金档 | 60万 / 100万 | 均报 CAGR、MDD、Calmar、换手、成本、填单率 |
| MDD | ≤25% 硬关注；**另报 ≤15%** | 与 Leo / Beta 预算一致 |

对照基线（不替换）：纸面 capacity_adv、B4（top300 / 现行 FROZEN）。

---

## 7. 双轨接线

| 轨 | 本模板 |
|---|---|
| FULLA 研究 | α / 拥挤度 / 分域诊断可在 FULLA 算；**求解宇宙**优先 HI_LIQ_V1.1（流动性与 Leo 3000–4500 目标更近） |
| HI_LIQ | investable 掩码复用，**不重建**；输出权重进研究目录 `output/strategy_optimizer/` |
| 纸面 FROZEN | **只读对照**；禁止覆盖 capacity_adv/B4/S6 权重与 FROZEN_CONFIG |

幸存者：Eng S1 退市清算落地前，宽池优化器报告页眉必须印 `delist_terminal=false`（见幸存者审计）。

---

## 8. 交付清单（Strategy 勾选）

1. [ ] `research/strategy_optimizer_v1_solve.py`（或等价）：按日/月再平衡调用 §3 求解  
2. [ ] `output/strategy_optimizer/calib_tc_60w.json` / `calib_tc_100w.json`（FROZEN 后、首跑结果前）  
3. [ ] 每日/每月：`weights.parquet`、`exposures.json`（β/Size/MidCap/行业）、`crowd_c.parquet`  
4. [ ] skfolio CPCV 摘要 + Riskfolio CDaR 对照表  
5. [ ] 与 B4/capadv 并列的 60万/100万 指标表（样本内标注）  
6. [ ] Arch/Beta \(\Sigma\)+硬约束共签记录  
7. [ ] **确认未写入**任何纸面 FROZEN 路径  

试验计数：仅在预注册改 FROZEN 且首跑后 +1（接 Strategy DRAFT §5）；本模板文档本身不计。

---

## 9. 明确不做

- 不改纸面 FROZEN_CONFIG / 日终权重  
- 不做 Top-N 主路径回归  
- 不做 GP；不用 alphagen 生成器  
- 不把 Riskfolio/skfolio 的研究数字写成「已晋级」  
- 不虚构 L2 拥挤度  
- `live=false`

---

## 10. 修订

| 时间 | 内容 |
|---|---|
| 2026-10-14 ≈08:02 ET | Arch 初稿：目标函数、硬软约束、LW+行业 \(\Sigma\)、拥挤度代理、死区+3/2、skfolio/Riskfolio 验收、双轨与纸面隔离。 |
