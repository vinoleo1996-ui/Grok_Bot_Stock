# Beta：Leo D 优化器风险预算（**SUPERSEDED** · 历史）

> **2026-10-14 ≈08:11 ET**：Leo 集中 Core 改口径（Neff 20–30 / 单票 5–6% / 行业±8%·绝对≤20% / Size±0.35σ+Slack / 两步整手）。本表 Leo D 数字 **不再**作优化器冻结路径。现行共签：`BETA_OPTIMIZER_COSIGN_CORE_CONC_ZH.md`。Strategy ≈08:11 接线确认（β0.10）历史有效。**未** FULL；等 Strategy DRAFT 正文对齐 + Eng λ 标定。

- **时间**：2026-10-14 08:06 ET（原文）· 废弃标注 08:11 ET
- **状态**：**SUPERSEDED**（原 PENDING_STRATEGY_V1_1 / CONDITIONAL_COSIGN_LEO_D）
- **不是**：FROZEN HARD；不是单独共签文件（共签见 Cosign Leo D）
- **作者**：QuantLab Beta · live=false · promotion_approved=false
- **依据**：Leo 选项 D（TEAM_STATE ≈08:03 ET）；Strategy DRAFT ≈08:08 ET；本文件供 Strategy 接线与快速升 FULL

---

## 0. 范围

| 轨 | 本文件 |
|---|---|
| **OPTIMIZER（Leo D）** | 下表 PENDING 数字；与 Cosign Leo D 六项一致 |
| **纸面袖套** | 仍以 `BETA_RISK_BUDGET_OPTIMIZER_PREREG_ZH.md` §2 为准（510300 / ±8% / ≤6% / 30–60）；**不动** |
| **禁止** | 跑优化器回测；改 FROZEN 纸面；把 PENDING 写成已 FROZEN |

---

## 1. 提案数字表（OPTIMIZER · PENDING）

| 项 | PENDING 提案 | 备注 |
|---|---|---|
| \(w_b\) | HI_LIQ 池内 **流通市值加权**（`wb_proxy=float_mktcap_hiliq`） | 自基准；不用中证全指/CSI300 官方权 |
| 纸面报告基准 | **510300** | 双口径；Mandate β 带 [0.70, 1.00] 仍报 |
| β HARD vs \(w_b\) | **\(\lvert\beta-1\rvert\le 0.10\)** | Strategy ≈08:11 **ACCEPTED** 0.10（±0.15 仅密封窗后备）；路径改 CORE_CONC |
| 线性 Size | \(\lvert e_{\mathrm{size}}\rvert\le\mathbf{0.25}\)（active z vs \(w_b\)） | HARD |
| MidCap | \(\lvert e_{\mathrm{mid}}\rvert\le\mathbf{0.25}\) | HARD |
| 防杠铃 | **Path A**：MidCap 盒 + \(\min(w_{P20},w_{P80})\le 0.05\) | V1 不用 Path B |
| 单票上限 | **100万 2.5% / 60万 3.0%** | 敏感度：统一 2.75%（仅报告） |
| 有效持仓 | **40–70**（\(N_{\mathrm{eff}}\) 或权重大于下限个数） | — |
| 行业主动 | **±5%** vs \(w_b\)（申万一） | `industry_wb_proxy=float_mktcap_hiliq` |
| 绝对行业帽 | **≤35%** | 纸面袖套仍 ≤25% |
| Σ | 行业因子 + 对角特异 | 禁稠密个股 LW 正式路径 |
| TC | **仅 L1** \(\lambda_{\mathrm{turn}}\|w-w_0\|_1\) | 无 3/2、无双阈 |
| 拥挤度 | schema 保留；缺失/覆盖不足 → **ν=0** | 标定前不写死 ν |
| λ_risk / λ_turn | **未冻**；密封窗同量纲标定后单点 | **禁** X2 收益偷看 |
| Core | β + Size/MidCap HARD + 行业 ±5% + L1；无域/快门卫/拥挤 | 60万∧100万 |
| Full | Core + 域预算 ±3pp + 快门卫 + 拥挤接口 | 分开报告 |
| DD 钩子 | **默认关** | — |

---

## 2. Core vs Full（与 Cosign / Strategy §5 对齐）

| 臂 | HARD | 软/模块 |
|---|---|---|
| **Core** | β vs \(w_b\)；Size/MidCap ±0.25σ；Path A 桶锁；行业 ±5%；单票/宽度；L1 | 无域预算、无快门卫、无拥挤、软风格 μ 默认可 0 |
| **Full** | 同 Core | + 域预算壳 ±3pp + 快/慢门卫 + 拥挤度接口（ν 标定后）+ 有把握风格软罚 |

两臂均报 60万 ∧ 100万 × 密封窗 + X2；对照 B4 / capacity_adv 纸面（非主路径）。

---

## 3. 拥挤度 schema（沿用先验）

```text
field: crowding_z / c_i
sign: 越高 = 多头拥挤越严重
penalty: ν * Σ w_i * max(c_i, 0)
coverage: 权益权重支持集 ≥70% 有效 c_i
missing_policy: 不足或缺失 → ν=0，打标 crowd=off（不填补、不因此失败）
schema_frozen: true（接口）；ν 数值未冻
status: NO_SERIES_OR_UNCALIBRATED
```

---

## 4. 与 Strategy DRAFT / Cosign 指针

| 文档 | 角色 |
|---|---|
| `STRATEGY_OPTIMIZER_PREREG_DRAFT_ZH.md` | Strategy Leo D DRAFT（接线源） |
| `BETA_OPTIMIZER_COSIGN_LEO_D_ZH.md` | **本 PENDING 的共签正文** |
| `BETA_RISK_BUDGET_OPTIMIZER_PREREG_ZH.md` | 纸面 §2 仍 SIGNED_FOR_PAPER；优化器路径 → 见 Cosign Leo D |
| `BETA_OPTIMIZER_CONFLICT_RESOLVE_ZH.md` | 旧六项冲突 PAUSE；被 Leo D 路径取代 |

---

## 5. 明确不做

- **不**将本表标 FROZEN / HARD 生效
- **不**跑优化器 / book-smoke 当正式
- **不**改 FROZEN 纸面轨 / FROZEN_CONFIG
- **不**恢复 3/2、双阈、中证全指 \(w_b\)、±2% 行业、1% 单票、100–400 宽度

live=false；promotion_approved=false。
