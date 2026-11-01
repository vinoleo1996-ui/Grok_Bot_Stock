# 压舱二选一 + Leave-one-out / 边际贡献门槛草案（Strategy · 研究级）

- **写入：** 2026-10-12T02:40:06-04:00（ET / America/New_York）
- **性质：** 研究草案，**非晋升证据**；`promotion_approved=false`
- **主表 AUM：** 仅 **60万 / 100万** CNY
- **禁小盘**；不改 Mandate；不重跑密封窗；不改 promotion 开关
- **来源审计：** `output/d1/EXTERNAL_AI_BETA_ALPHA_GAP_AUDIT_ZH.md` §P0-4 / V5 / V10 / P0-9
- **相关诊断：** `output/strategy_recon/dd_matprem_overlay/SHORT_ZH.md`
- **单臂对账：** `output/strategy_recon/gold_beta/SHORT_ZH.md` · `output/strategy_recon/dd_ballast/SHORT_ZH.md` · `output/strategy_recon/cb_matprem/SHORT_ZH.md` · `output/strategy_recon/mp_near/SHORT_ZH.md`

---

## §1 决策：主表试配压舱 = GOLD-BETA；DD-BALLAST → watch_only / 对照

| 项 | 结论 |
|---|---|
| **主表试配压舱** | **GOLD-BETA** |
| **对照 / watch_only** | **DD-BALLAST**（对账记录保留，不删除；不作第二压舱叠满） |
| **依据（已验证单臂 X2 @60万）** | GOLD **15.35% / −6.31% / 1.40** vs DD **12.36% / −7.66% / 1.08**；GOLD 在 X2 Sharpe 与 CAGR 均更高，且 MDD≤25% |
| **双档一致** | @100万：GOLD 15.36%/−6.32%/1.40；DD 12.37%/−7.66%/1.09 → 同序 |
| **相关闸** | DD×GOLD 日相关 ≈ **0.974**（周 ≈0.96）；持仓 Jaccard≈1.0（同持 510300+511010+518880）→ 叠满 = 买两次同一保险 |
| **X1 软风险（须披露）** | GOLD X1 ≈ −0.5% / −21.6% / 0.03；DD X1 ≈ 0.36% / −24.1% / 0.10。GOLD X1 更深；**失败路径 = 降权益腿 / 缩 CB 仓，禁止叠第二压舱** |

**一句话：** 压舱二选一选 GOLD；DD 留作 LOO 交替对照与压力情景，不进主表试配双压舱。

---

## §2 硬闸：禁止双压舱叠满进主表试配

```
IF |ρ_daily(DD, GOLD)| > 0.70:
    主表试配至多保留 ONE ballast
    另一条 → watch_only / 对照
    50/50 DD+GOLD 叠加 → 仅历史诊断，不作候选书、不作晋升臂
```

- 实测 `|ρ| ≈ 0.974 > 0.70` → **本闸已触发**。
- Overlay 中 DD+GOLD static @60万 ≈ 13.87% / −6.92% / 1.25，弱于 GOLD 单臂 X2 夏普 1.40，且相对 GOLD+MATPREM（≈14.1% / −5.7% / 1.50）无分散优势叙事。
- **禁止**在营销/值班话术中把「DD+GOLD 双压舱」写成主表候选。

---

## §3 选择公式（研究级）

```
ballast* = argmax_{s ∈ {DD, GOLD}} Sharpe_X2_net(s)
           s.t.  MDD_X1(s) ≤ 25%  AND  MDD_X2(s) ≤ 25%
                 AND  通过 AUM 容量备注（主表 60万/100万 均有对账）
```

- **双档：** 须在 **60万与100万** 上同一 sleeve 胜出（或并列后走 tie-break）。
- **Tie-break：** 更高的 X2 CAGR；再并列则披露 X1 软风险后由 Leo 裁定。
- **本次应用：** GOLD 在两档 Sharpe 与 CAGR 均胜；MDD_X2 远低于 25%；X1 MDD≈−21.6% ≤25%（仍软）。→ **ballast* = GOLD-BETA**。
- **失败条件（审计原文）：** 单压舱后组合 X1 软风险恶化超过预注册上限 → **降权益 / 缩 CB**，**不**叠加第二压舱。

---

## §4 Leave-one-out / 边际贡献门槛草案（研究级）

### 4.1 主表 primary 集合提案

| 角色 | Sleeve | 备注 |
|---|---|---|
| **Primary（提案）** | **MATPREM**（或族内经 LOO 胜出的唯一 primary）+ **GOLD-BETA** | 转债低溢价主机制 × 单压舱 |
| **Secondary（默认）** | MP-NEAR / MP-MERGE / MP-RELAX | MATPREM 族近亲；须 LOO 证明 Δ 才可升 primary |
| **Watch_only / 对照** | **DD-BALLAST** | 压舱交替应力；禁与 GOLD 同进 primary |
| **禁** | DD+GOLD 双 primary | §2 硬闸 |

### 4.2 定义（草案方法须写清）

对 primary 集合 \(B\)，在主表 AUM（60万与100万）的 **X2** 上定义：

\[
\Delta\mathrm{Sharpe}_k = \mathrm{Sharpe}(B) - \mathrm{Sharpe}(B\setminus\{k\})
\]
\[
\Delta\mathrm{CAGR}_k = \mathrm{CAGR}(B) - \mathrm{CAGR}(B\setminus\{k\})
\]

**合成方法（草案二选一，执行前锁一种）：**

1. **静态等权 primary 书**：各 primary sleeve 的 recon **engineA NAV** 日收益等权（本次附录插图用此法）；或
2. **多袖套账本等权 NAV**：`v2_multisleeve_book` / NOIC 骨架输出的书级 NAV（正式闸门证据优先此法，待 Leo 批准权重 JSON 后再算）。

本文件阈值阈值阈值为 **研究草案**；附录插图 **不是** 闸门证据。

### 4.3 提议阈值（可调）

- **保留 primary：** 若在 **60万与100万两档** 均满足  
  \(\Delta\mathrm{Sharpe}_k \ge 0.05\) **或** \(\Delta\mathrm{CAGR}_k \ge 0.5\,\mathrm{pp}\)  
  → 保留；否则降为 secondary / watch_only。
- **族内闸：** 若与已有 primary 的 \(|\rho_{\mathrm{daily}}| \ge 0.70\)（MATPREM 近亲建议 **≥0.85** 直接否决第二 primary），则不得并列第二 primary；LOO 须击败「族内折叠为单臂」的替代方案。
- **压舱特例：** `{DD, GOLD}` 至多 **一条** 进 primary；另一条仅作 LOO 交替应力（swap 对照），不得同时计 Δ 后「双过闸」。
- **失败条件（审计）：**
  - 单压舱后 X1 恶化超预注册 → 降权益/CB，不叠第二压舱；
  - LOO 后整簇对书无边际 → 整簇降级；
  - 用 L>1.5 或密封窗重调参「做」出假 CAGR → 否决。

### 4.4 附录：60万 X2 等权 NAV 插图（**illustrative diagnostic only**）

方法：`output/strategy_recon/{cb_matprem,mp_near,gold_beta,dd_ballast}/AUM_600000/nav_X2.csv` 的 **engineA** 对齐日收益（2024-06-03→2026-10-09，N=570），静态等权；**非**正式闸门、**未**跑 100万 LOO、**未**改权重 JSON。

| 书 | CAGR / MDD / Sharpe | 解读 |
|---|---|---|
| **MATPREM+GOLD**（提案 primary） | ≈14.7% / −5.6% / **1.54** | 基准插图 |
| LOO 去掉 MATPREM | ΔSharpe≈**+0.12**；ΔCAGR≈**−1.2pp** | Sharpe 贡献过阈；CAGR 因 GOLD 单臂更高而「负」——须与单臂叙事一并读 |
| LOO 去掉 GOLD | ΔSharpe≈**+0.20**；ΔCAGR≈**+1.4pp** | GOLD 边际大 |
| MATPREM+DD（交替压舱） | ≈13.1% / −6.3% / **1.34** | 弱于 MATPREM+GOLD |
| MATPREM+GOLD+DD（**禁主表**） | ≈14.1% / −6.3% / **1.41** | 去掉 DD 后 Sharpe **上升**（ΔSharpe≈−0.14）→ 双压舱伤害书 |
| 全四臂 MATPREM+NEAR+GOLD+DD | ≈14.4% / −6.1% / **1.48** | 去掉 DD：ΔSharpe≈−0.08（DD 负边际）；NEAR ΔSharpe≈+0.07 / ΔCAGR≈+0.3pp（未双过草案阈） |

**插图结论（仅诊断）：** 支持「选 GOLD、DD 不进 primary」；NEAR 升 primary 需正式双档 LOO 再证。

---

## §5 明确不做

- **不做** DD×GOLD 双压舱叠满营销 / 主表候选话术  
- **不翻转** `promotion_approved`（保持 false）  
- **不碰小盘**  
- **不用** L>1.5 虚增 CAGR  
- **不**密封窗重调参当新证据  
- **不**把本草案阈值或附录插图当作晋升证据  
- **不**在未获 Leo 批准前写入正式 book weight JSON

---

## §6 下一步

1. **Beta：** 在后续 handoff / 预检模板中确认「压舱二选一 = GOLD；DD=watch_only」。  
2. **Strategy：** 60/100万双引擎对账协议不变；新包照旧对账；WATCH / 多袖套账本已标 P0-4。  
3. **更新 WATCH：** 见 `output/v3/handoff_strategy/WATCH_ZH.md`。  
4. **等 Leo：** 批准后再锁 LOO 合成方法、阈值数值、以及任何 book weight JSON。  
5. **正式 LOO：** 待权重锁定后，用书级 NAV 在 60万+100万重算；附录插图作废为闸门证据。

---

## 引用路径速查

| 文件 | 用途 |
|---|---|
| `output/d1/EXTERNAL_AI_BETA_ALPHA_GAP_AUDIT_ZH.md` | P0-4 / V5 / V10 规则原文 |
| `output/strategy_recon/dd_matprem_overlay/SHORT_ZH.md` | DD×GOLD≈0.97；叠加诊断 |
| `output/strategy_recon/gold_beta/SHORT_ZH.md` | GOLD 对账短报 |
| `output/strategy_recon/dd_ballast/SHORT_ZH.md` | DD 对账短报 |
| `output/v3/handoff_strategy/WATCH_ZH.md` | 值班备忘 |
| `docs/v2/STRATEGY_MULTISLEEVE_BOOK.md` | 多袖套账本状态表 |
