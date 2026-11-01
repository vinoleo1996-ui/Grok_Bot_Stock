# 叶27 · capacity_adv 残差步契约钉（暴露/活跃指示）

- **日期**：2026-10-25 ≈06:28 ET · America/New_York  
- **作者**：QuantLab Alpha（残差定义所有权）  
- **闭合**：Arch 契约预告 `docs/v2/ARCH_AI_LEAF27_CONTRACT_PREVIEW_20261025_ZH.md` sha `ac853d7f…` §1.5 **UNKNOWN**  
- **对齐**：预注册 r1 `docs/v2/AI_LEAF27_OVERNIGHT_IDIO_IVOL_PREREG_r1.md` sha `f12965da…` 残差清单第 5 步；填审 `01ab6bf3…`  
- **锁**：`live=false` · `promotion_approved=false` · **不申 .ok** · 不挡叶25 · 不改预注册 r1 正文（本文件为契约钉；脚本 DIFF 必须引用本钉）  
- **协作者**：AI 须在脚本 DIFF / 回执中按本钉实现并披露 sha；Data/Arch 签脚本前核对路径字节

## 结论先行

| 项 | 写死值 |
|---|---|
| **主规格「暴露」** | 同日截面 **连续组合权重** `target_weight`（≠ ADV 分位；≠ 活跃 0-1） |
| **序列路径** | `output/strategy_hiliq/legs/g1g5_capacity_adv_hiliq_v1_1_daily_weights_20261014_195620.parquet` |
| **权重文件 sha256** | `3b288c832b956820af9802f02861af459e215e7d4097a6420724b26cf2d31c4d`（sha8 `3b288c83`） |
| **universe_id** | `HI_LIQ_V1_1` |
| **mechanism_tag** | `g1g5_ashare_capacity_adv_v1` |
| **列** | 主键 `(date, instrument)`；暴露列 **`target_weight`**（与 `weight` 字节级相同，实现读 `target_weight`） |
| **活跃指示** | `active_capadv := 1{target_weight > 0}` —— **仅**用于 Jaccard / 活跃集硬闸披露，**不得**替代主规格残差回归量 |
| **ADV 分位** | **禁止**作第 5 步回归量（`adv20_yuan` / `adv_fail` 仅宇宙掩码上游，不是 paper 书暴露） |

## 1. 语义（主规格）

残差清单第 5 步 = 在第 4 步残差 `ε₄`（已完成 SW L1 demean → log 流通市值 → 滚动β(510300)）上，再对 **capacity_adv 当日组合暴露** 做同日截面 OLS，取残差得 `ε₅`：

\[
\varepsilon_{5,i,t} = \varepsilon_{4,i,t} - \hat a_t - \hat b_t\, x^{\mathrm{cap}}_{i,t}
\]

其中

\[
x^{\mathrm{cap}}_{i,t} =
\begin{cases}
\texttt{target\_weight}_{i,t} & \text{若 }(t,i)\text{ 出现在钉死权重表} \\
0 & \text{否则（当日不在 paper 书 → 暴露为 0）}
\end{cases}
\]

- 回归宇宙 = 当日已通过预注册 §2.4（停牌无效；涨跌停不进截面）且完成前四步的**个股**集合。  
- **`510300.SH`（压舱）**：不进入个股截面残差宇宙（本叶 α 是个股向量）；若权重行存在该码，实现须剔除，不得把 ETF 压舱当股票暴露回归。  
- 名过少（与 SW L1 同档披露阈值）：仅对 `x^{cap}` demean 或跳过本步并 **记 GAP + 回执披露**，不得静默用 ADV 分位顶替。  
- 缺权重文件 / sha 不 MATCH → **硬 GAP**，不得用宇宙掩码或自造 0-1 冒充。

## 2. 活跃指示（闸门用，非残差主轴）

| 用途 | 定义 |
|---|---|
| Jaccard / 活跃集硬闸 | `active_capadv = 1{target_weight > 0}`（个股；剔 510300） |
| 残差 ρ 披露 | 对 `ε₅` 与 capacity_adv 组合日收益（或权重加权收益）报 ρ_excess；实现路径回执写死 |
| **禁止** | 主规格第 5 步用 `active_capadv` 0-1 代替 `target_weight`；用 `adv_fail`/`adv20_yuan` 分位代替 |

敏感性（可选、不得升格主规格）：0-1 活跃哑元作回归量可另报一列，**不能**写入主 α。

## 3. 明确否决的歧义项（Arch 列举）

| 候选 | 裁定 |
|---|---|
| 权重 `target_weight` | **主规格 = 是** |
| ADV 分位 / `adv20_yuan` | **否**（选股上游，非书暴露） |
| 活跃集 0-1 | **仅 Jaccard**；非残差主轴 |
| 自造 `capacity_adv_exposure` 列且无 sha | **否**；必须读钉死 parquet |
| moneyflow / 叶26 权重 | **否**（正交他腿，禁混） |

## 4. 实现检查清单（AI 脚本 DIFF / Arch 审）

1. 打开路径上表；`sha256` **必须** = `3b288c83…`（若日后换钉，须 Arch 新契约 + 本文件修订，不得私换）。  
2. 按 `(date, instrument)` left-join 到残差面板；缺失 → 0。  
3. 剔 `510300.SH` 出个股 CS。  
4. OLS → `ε₅` → 其后 `ivol=std(ε₅,W)` → `α_raw=−ivol`（预注册已冻）。  
5. 回执披露：所用路径、sha8、正权名数均值、`active_capadv` 日均覆盖、本步跳过/GAP 日数。  
6. **不**改预注册 r1 已冻方向/β/W；本钉只闭合暴露语义。

## 5. Beta 旁注（知会，非本钉范围）

Beta 页 `BETA_LEAF27_ON_MINUS_ID_IDIO_BETA_STYLE_CHECK_ZH.md` sha `3e65fcba…`：主规格 `−ivol` 与 vol16% **软兼容**；`+ivol` 或与叶26/moneyflow 混轴 = 硬冲突。与本钉一致：方向保持 `−ivol`；禁混 moneyflow/叶26 进第 5 步。

## 6. 非动作

不申叶27 `.ok`；不挡叶25（钉 `7b279d47`）；不读收益选参；不碰纸面；live=false。

## 7. 请 AI 确认

请 AI 在脚本 DIFF 首页引用本文件 sha，并回复「暴露=target_weight / 路径+sha MATCH / 活跃仅 Jaccard」。若不同意连续权重主规格，须在 4 小时内提出替代并经 Alpha+Arch 重钉——默认按本钉执行。
