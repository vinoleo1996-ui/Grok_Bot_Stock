# Beta · 宽基 ETF 资金流/折溢价 → β 与波动预算信号（研究级一页）

- 时间：2026-10-25 ≈04:38 ET（America/New_York；盒机 `date` 显示 CST=UTC+8，换算 ET=UTC−4）
- 角色：QuantLab Beta（β / 风险预算 / 风格；**不**猎数、**不**挖 Alpha）
- 触发：主 Agent 转发 Leo 04:35 ET「冲年化」— 评估宽基 ETF（510300 等）资金流/折溢价对 β 目标与波动预算的可用信号
- 性质：**机制 + 文献 + 草稿规则**。全程只读（Read / rg / sha256sum / ls / 公开 WebSearch）。**未**跑任何 python / pytest / 读行情或 parquet 的脚本。未申请 Arch .ok。
- **live=false；promotion_approved=false。** 不改线上、不改 Mandate JSON、不碰冻结纸面轨（capacity_adv / B4 / S6）。研究开关**默认关**。

---

## §0 结论三句

1. **能用，但只作风险预算侧的研究开关，不能当冲年化主引擎。** 盘上份额流 PIT（`share_pit`，通常 T+1 09:00）可用；真折溢价 \((P-\mathrm{IOPV})/\mathrm{IOPV}\) **不可用**（D4 历史 IOPV 硬缺口，禁伪造）。弱代理可用 \((P-\mathrm{NAV}_{t-})/\mathrm{NAV}_{t-}\)，须显式标注「非 IOPV」。
2. **与 Mandate vol16% / β0.70：抬 β 冲年化 = 硬冲突倾向；降 β 反拥挤 = 软兼容。** 报告带 `target_beta_band=[0.5,0.85]`、`target_annual_vol_range=[0.14,0.18]`。Core v1.3 组合层已见 vol≈19.6–19.9%、β≈0.86–0.87（对 510300），**已压在/越过带上沿与 vol 目标**；再抬 β/vol 须 Leo 书面放宽 Mandate，本页不做。
3. **下一步**：本开关默认关；盒机恢复后若要 smoke，先向 Arch 申 selftest/研究 .ok；优先用份额流 z（不依赖 IOPV）；与已 FAIL 的 NAV-DISC / SHARE-AC / ETF-timing v20–v23 / 行业申赎反转同构叶**正交隔离**；X2 只入场券；无实证数字（本页未回测）。

---

## §1 信号定义（公式 · PIT · 滞后）

### 1.1 宇宙与对象

| 项 | 口径 |
|---|---|
| 主对象 | 宽基：`sh.510300`（沪深300ETF）；对照可扩 `510050` / `510500` / `159919` / `512100`（与 `etf_share_flow_pit_major` 一致） |
| 用途 | **调 Mandate 风险预算旋钮**（`target_beta` / 有效 `target_vol` / DD 缩放触发），**不是**个股残差 α、不是行业轮动 |
| 决策滞后 | 信号日 \(t\) 只用 \(available\_at ≤ t\) 15:00 的信息；下单按既有再平衡（`month_end_plus_first_last` 或 Mandate 双周），**禁止**同日盘中偷看 |

### 1.2 折溢价（理想定义 vs 盘上可得）

**理想（一级套利口径）：**

\[
\mathrm{Prem}^{\mathrm{IOPV}}_{i,t}=\frac{P_{i,t}-\mathrm{IOPV}_{i,t}}{\mathrm{IOPV}_{i,t}}
\]

- \(P\)：场内成交价（收盘或决策可用最后价）。
- \(\mathrm{IOPV}\)：基金份额参考净值（盘中）。
- **盘上状态**：`ALPHA_DATA_D4_IOPV_GAP_ZH.md` — **无历史 IOPV**；Tushare/datahub 无 `etf_iopv`/`fund_iopv` 史；仅实时深市 `rt_etf_sz_iopv`。**禁止用 NAV/收盘价伪造 IOPV。**

**弱代理（须标注 `proxy=nav_premium`，研究级）：**

\[
\mathrm{Prem}^{\mathrm{NAV}}_{i,t}=\frac{P_{i,t}}{\mathrm{NAV}_{i,t-}^{\mathrm{asof}}}-1,\quad
S^{\mathrm{prem}}_{i,t}=z_{\mathrm{expanding}}\big(\mathrm{Prem}^{\mathrm{NAV}}_{i,t};\;\min=60\big)
\]

- NAV PIT：`ann_date.normalize() < T`（与 BOND-NAV-MR 一致，`allow_exact_matches=False`）。
- 注意：NAV 折溢价 ≠ IOPV 折溢价；宽基现金拖累/分红日可造伪信号。**NAV-DISC（对 510300 调权益 β）已 fail**（见 `V3_BOND_NAV_MR_PREREG` ≠ 禁族）。本页若启用 prem，只作与份额流的**联合确认**，不得单独复刻 NAV-DISC。

### 1.3 申购/赎回（份额流，主信号）

\[
\Delta_{20} fd\_share_{i,t}=fd\_share_{i,t}-fd\_share_{i,t-20},\quad
S^{\mathrm{flow}}_{i,t}=z_{250}\big(\Delta_{20} fd\_share_{i,t}\big)
\]

| 字段/约定 | 说明 |
|---|---|
| 源 | `data/v2/etf/share_pit/etf_share_flow_pit_major.parquet`（宽基）/ `etf_share_flow_pit_all.parquet`；列含 `fd_share`、`share_wan`、`d_share_wan`、`share_available_at`、`available_at` |
| PIT | 2018+：`share_available_at`（通常 **下一交易日 09:00**）；2014–17：`raw/fund_share`，research_grade 假定 available=下一交易日 09:00（与 `V3_SHARE_AC_PREREG` / `V3_B1_PREREG` 同） |
| 决策 | 信号日 \(T\) 只用 \(available\_at ≤ T\) 15:00 → **至少滞后约 1 个交易日**；不得用当日未公布份额 |
| 净申赎金额代理 | \(flow\_est ≈ \Delta share \times NAV\)（若表内已有 `flow_est_wan_yuan` 则用之）；宽基主用份额 z，金额作稳健性 |

**可选二级代理（非主门）：** 场内成交额 20 日 z（二级拥挤，**不是**一级申赎）；禁止把它叫作「申赎」。

### 1.4 合成状态（研究默认）

\[
\mathrm{State}_t=\mathrm{sign}\big(S^{\mathrm{flow}}_{510300,t}\big)\;\mathbf{1}\{|S^{\mathrm{flow}}|≥1\}
\;\oplus\;
\mathrm{confirm}\big(S^{\mathrm{prem}}_{510300,t}\big)
\]

- 主触发：\(|S^{\mathrm{flow}}|≥1\)（拥挤/抽离）。
- `confirm`：若有 NAV prem 且同号（溢价∧净申购，或折价∧净赎回）→ 置信 +1；异号 → 置信 0（不动作）。无 IOPV 时 prem 分支可整体关掉。
- **文献方向提示（非本页实证）**：国盛 2025 等指出份额流入整体偏**反转**（流入后收益偏弱），宽基分组弱于行业主题；溢价越高越易吸引申购、加重短期超买。华安综述（美股文献）区分需求流 / 套利流 / 意外流：套利流对次日收益偏负，意外流偏正。→ 对 **β 预算**，拥挤（高流入+溢价）更宜**降**风险预算，而非抬 β 追年化。

---

## §2 调 β 规则草稿（研究开关，`etf_flow_beta_overlay=false` 默认）

只动 Beta 袖套旋钮与有效目标；**不**改 `max_etf_sleeve_weight=0.40`；**不**改 Strategy 残差 α；**不**写实盘权重。

记 Mandate 点目标 \(\beta^\star=0.70\)、\(vol^\star=0.16\)；带 \([\beta_L,\beta_U]=[0.5,0.85]\)、\([vol_L,vol_U]=[0.14,0.18]\)。
有效目标：

\[
\beta^{\mathrm{eff}}_t=\mathrm{clip}\big(\beta^\star+\Delta\beta_t;\;\beta_L,\beta_U\big),\quad
vol^{\mathrm{eff}}_t=\mathrm{clip}\big(vol^\star+\Delta vol_t;\;vol_L,vol_U\big)
\]

再进入既有公式（`BETA_VOL_TARGET_HANDOFF`）：

\[
w_{vol}=vol^{\mathrm{eff}}/\hat\sigma,\quad
w_{\beta}=\beta^{\mathrm{eff}}/\hat\beta_{\mathrm{unit}},\quad
etf=\min(w_{vol},w_{\beta},max\_etf)
\]

（仍叠 L1–L4 DD 缩放；DD 只降不升。）

### 2.1 离散档位（建议）

| 状态（T 日 PIT） | \(\Delta\beta\) | \(\Delta vol\) | 备注 |
|---|---|---|---|
| 拥挤：\(S^{\mathrm{flow}}≥+1\)（及同号溢价确认） | **−0.10** → \(\beta^{\mathrm{eff}}=0.60\) | **−0.02** → \(vol^{\mathrm{eff}}=0.14\) | 反拥挤；落在带内 |
| 中性：\(\|S^{\mathrm{flow}}\|<1\) | 0 | 0 | 维持 Mandate 点目标 |
| 抽离：\(S^{\mathrm{flow}}≤−1\)（及同号折价确认） | **+0.05** → \(\beta^{\mathrm{eff}}=0.75\) | 0 | **仅**在组合 realized vol 已 ≤16% 时允许；否则 \(\Delta\beta=0\)（见 §3） |
| 换手死区 | 若 \(\|\beta^{\mathrm{eff}}-\beta^{\mathrm{eff}}_{prev}\|<0.05\) 则保持上期 | 同 | 降无效换手 |

### 2.2 明确禁止的「冲年化」反向档（需 Leo 放宽 Mandate 才可议）

| 想法 | 本页态度 |
|---|---|
| 高溢价/强净申购 → 抬 \(\beta^\star\) 到 0.85–1.0 或抬 \(vol^\star\) 到 >0.18 | **拒绝默认**；属硬冲突（§3）；文献亦偏反转 |
| 抬 `max_etf` 或绕过 DD L1–L4 | **拒绝**；与 handoff 契约冲突 |
| 把份额流当残差 α 主因子 | **拒绝**；归 Alpha/AI 叶，且行业申赎反转叶已判同构 FAIL |

### 2.3 与既有失败臂的隔离

| 已有 | 关系 |
|---|---|
| NAV-DISC（510300 折溢价调权益 β） | **已 fail**；本页 prem 仅确认位，不得单独复刻 |
| SHARE-AC（份额 z 反拥挤调 \(w_{eq}\)） | X1/X2 **不通过**；本页改的是 Mandate \(\beta^{\mathrm{eff}}/vol^{\mathrm{eff}}\) 旋钮而非固定 0.35/0.85 仓位表，机制近亲 → 若开 smoke 须报 vs SHARE-AC 的差分与近亲闸 |
| AI ETF-timing v20–v23 | Beta 已拒（价/收益叶）；本页**不用价格动量** |
| G1G5 行业 ETF 申赎反转 | 同构 FAIL；本页**不**做行业轮动、不下沉个股 |

---

## §3 与 Mandate 16% / 0.70 冲突表

Mandate 锚点（`QuantLab-MANDATE_V2.json` / DEFAULTS）：`target_annual_vol=0.16`（范围 0.14–0.18）；`target_beta_vs_benchmark=0.70`；`target_beta_band=[0.5,0.85]`；`max_etf_sleeve_weight=0.40`。

| 动作 | 冲突级 | 理由 |
|---|---|---|
| §2.1 拥挤档：\(\beta^{\mathrm{eff}}=0.60\)、\(vol^{\mathrm{eff}}=0.14\) | **无冲突** | 落在报告带内；与 DD 缩放同向（降风险） |
| §2.1 抽离档：\(\beta^{\mathrm{eff}}=0.75\) 且 vol 已 ≤16% | **软冲突** | 仍 ≤0.85；但抬 β 会推高组合 vol/MDD，须双门槛（vol 已达标才抬） |
| 抬 \(\beta^\star>0.85\) 或 \(vol^\star>0.18\)，或「冲年化」无条件加 β | **硬冲突** | 越 Mandate 带；须 Leo 书面改 Mandate **且**改门在看收益前 |
| 在 Core v1.3 现状上再抬 β | **硬冲突（现状叠加）** | Core 门控审查（只读）：组合 vol **19.6–19.9%**（高于 16% 目标 3.6–3.9pp，亦高于范围上沿 0.18）；β≈**0.86–0.87**（对 510300），已在/越过 `target_beta_band` 上沿 0.85。再抬 β = 更冲年化预期的同时**加剧**已超标的 vol/MDD 风险；与 Leo 风险预算意图相反 |

**含义（给 Leo / 主 Agent）：**  
「用宽基 ETF 资金流抬年化」若实现为**顺流加 β**，与 Mandate **硬冲突**且与公开文献的反转方向相悖；若实现为**拥挤降 β / 抽离小幅回补**，与 Mandate **无硬冲突**，但**不承诺**抬年化——它是风险预算工具，年化靠 Alpha/结构，不靠把 β 拧过 0.85。

---

## §4 失败条件与不做

1. **不替代残差 α**；不申购赎回下沉成分股选股（那是 AI/Alpha 叶，且缺 PCF 时不可稳做）。
2. **不碰冻结纸面轨** capacity_adv / B4 / S6；不改线上权重；`live=false`。
3. **X2 只入场券**；即使未来 smoke 过 X2，晋级仍看 FWD 与 Leo 密封。
4. **无 Arch .ok 不回测**；本页零实证数字；任何「年化 +x%」陈述在本页出现即视为违规。
5. **失败即关开关**：若未来 smoke 显示 (a) 近亲 SHARE-AC / NAV-DISC（ρ 或仓位路径过高），(b) 组合 vol 中位仍 >18%，(c) 相对静态 Mandate 点目标无风险改善（同 MDD 带下 Calmar/vol 不改善），则 `etf_flow_beta_overlay` 保持 false 并归档。
6. **不伪造 IOPV**；无历史 IOPV 则 prem 分支关闭或仅 NAV 弱代理+标注。

---

## §5 待数据 / 待 Arch

| 项 | 状态 | 谁 |
|---|---|---|
| 盒机刷新事故 | 事故文仍在；TEAM_STATE 记恢复核验 PASS / BACKUP_PIN CLOSED / Leo 04:30 解冻 enable+叶25 **分签中**。Beta **仍不**自跑实数据；本页已遵守禁跑 | Arch / 主 |
| 本开关 smoke | 须 Arch 新签研究/selftest .ok（`scope`/`allow_*`/`out_dir`/`expires_et` 按 `ARCH_RUN_AUTH_SELFTEST_SPEC`）；RSS≤1.5GB；`PYTHONDONTWRITEBYTECODE=1 nice -n 10 … -p no:cacheprovider` | Arch → Beta |
| IOPV 史 | D4 GAP；无源则不做真折溢价门 | Data（另开单） |
| 份额增量 | `share_pit` 窗至约 2026-10-09；事故后增量是否齐全由 Data 核 | Data |
| `sw_l1_pit` / 行业中性 | `sw_pit` 0b1d3432 缺 349 只行业；等 `sw_l1_pit_v2`；本页宽基信号**不依赖**行业表 | Data |
| Core v1.3 | 门控 **FAIL** 两档不变；去留等 Leo；若保留则 v1.4 口径 C 重走全部门——**与本开关正交，本页不复活 Core** | Leo / 主 |

---

## §6 引用（盘内 sha / 公开 URL）

### 6.1 盘内（写时 sha256）

| 文件 | sha256 |
|---|---|
| docs/v2/ARCH_BOX_REFRESH_INCIDENT_20261025_0111ET_ZH.md | 486bb27396961c4f2a511f56067f22a2edc9f8da7bc0f8bfe1a49a62eac03d49 |
| docs/v2/BETA_VOL_TARGET_HANDOFF.md | 3872d1a449b8704ae398f79881194aa7ab6b49cfe7e9fc2689893b62f0ddedfa |
| docs/v2/QuantLab-MANDATE_V2.json | 04afacc45778bfcdcfbcc7b8ff73098f2ec843cd49fea6ef406d297e05e68f0f |
| docs/v2/QuantLab-MANDATE_V2-DEFAULTS.md | 902fcebbfe6578d258301c4ed6b4b1ffb5b862e9a5db72381111e3778602f76d |
| docs/v2/MANDATE_UNIFIED_STOCK_ETF_20261012_ZH.md | e53fa57153713cca926648976098f3b5dbaef760602f1ed8c9d6f8b1a0761064 |
| docs/v2/BETA_CORE_V1_3_GATE_REVIEW_ZH.md | 8bff82f1b30c92898fb5cc8c681dd8c3440925a71eef1bdd72918db72990a4fa |
| docs/v2/V3_SHARE_AC_PREREG.md | 7b2de1badaecc1a88d6cb2628012835f2d1c2fe2241734cb83b2fb6350513899 |
| docs/v2/V3_BOND_NAV_MR_PREREG.md | 7d47dff97597a4542d09219834e4a054d71bea210f5dca724e935d594446c29b |
| docs/v2/ALPHA_DATA_D4_IOPV_GAP_ZH.md | 52c5c827416c7e4e2a7d31f753caf6495ad1eb5fd738e9ca6ea84ded4d87d061 |
| docs/v2/BETA_X1_EVT_FLOW_COVERAGE.md | c154341c25c93c5355a421d64677a8a30399a4c876d56c609ee3b074e8d0f994 |
| docs/v2/V3_B1_PREREG.md | 336dbaa6ae6d25206649a8d33f7f7fd402383515e2ec930714e37f3e509f0bd9 |
| docs/v2/AI_V23_ETF_TIMING_PRICE_BETA_REVIEW_ZH.md | 927df0f839cff783229e00ad8b3b2a63311bca5c1b93da70d89aba7f03fa0619 |
| docs/v2/EXTERNAL_BETA_DIGEST_ORTHO_ZH.md | 09381a46e8837d3fedf230753dd2305b227595e34f447ce1844864b32597563b |
| docs/v2/AI_G1G5_IND_ETF_FLOW_REV_WHO_PAYS_PREREG_DRAFT_ZH.md | 79a53527fb470b27843069450c7a802b78f8834e4f99b4a7d926d090d127873b |

### 6.2 公开文献 / 研报（机制引用；**不**采信其回测数字为本页结论）

| 出处 | URL | 取用机制 |
|---|---|---|
| 薛英杰（西南财经大学）ETF 折溢价与收益可预测性 | https://www.ppdoc.com/degree/eb89db24a73847d763cb83e639c9946a.html | 折溢价对未来 ETF 收益偏负向可预测；套利限制/情绪放大 |
| 国盛证券 2025-01《解构 ETF 资金流的反转现象》 | http://fxbaogao.com/detail/4681372 | 份额流整体反转；行业主题强、宽基弱；溢价促申购 |
| 华安证券「学海拾珠」ETF 资金流信息分解 | https://www.nxny.com/report/view_5130297.html | 意外流正向 / 套利流负向预测次日（美股文献转述） |
| 中信建投 2025-03 ETF 资金流行业轮动 | http://wt.microbell.com/data/6d628d7f4fd182a760f46f55e1038d25.html | 折溢价与份额变动相关；增强稳定性（行业层，非本页 β 预算） |

---

## §7 落盘与门锁

- 路径：`docs/v2/BETA_ETF_FLOW_PREMIUM_BETA_SIGNAL_DRAFT_ZH.md`（写前确认不存在；未覆盖任何旧文）
- 最终 sha256：见文末 shell 实测行（R3）
- `etf_flow_beta_overlay=false`；`live=false`；`promotion_approved=false`



- 落盘备注：完整文件 sha256 以 TEAM_STATE / 回执中 R3 实测为准（避免自指改哈希）。正文至此结束。
