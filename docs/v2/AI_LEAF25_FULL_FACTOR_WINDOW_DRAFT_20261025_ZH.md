# 【DRAFT — 未冻结 / 勿开跑】叶25 全叶因子窗草案（独立 `.ok` + X2）

| 项 | 值 |
|---|---|
| 起草 | QuantLab AI · 2026-10-25 11:27:31 ET（America/New_York） |
| 状态 | **DRAFT / 未冻结 / 勿开跑 / 勿申 `.ok` / 勿实跑读盘** |
| live | **false** |
| promotion_approved | **false** |
| research_only | true |
| 本文件角色 | 主令③：全叶因子窗（非仅 recon）排窗前草案；**就绪报主排窗**，AI **禁自开跑** |
| 预注册底座 | `docs/v2/AI_LEAF25_ACCRUALS_PREREG_DRAFT_r5.md` sha256 `81123646382f7bb188a135e0d9142372b373c079e289d47066f5587a1fde40e1`（**仍未 FROZEN**） |
| 步骤−1 状态 | **STEP_M1_RECON_PASS**（Alpha 披露 sha256 `63868a18a759de179a195e33eca7943674371e16492387e15d8c0f8f68c93278`）；非叶级 ACCEPT |
| Arch 消费 | `docs/v2/audit/leaf25_step_m1/ARCH_LEAF25_STEP_M1_R5_V4_CONSUMED_20261025_ZH.md` sha256 `9c96bf351ef6e6e69b127ef9e308569e01f574dd5840588866239a842473c838`；`.ok` `1c32ab1e…` 已 CONSUMED |
| AI 回执 | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_STEP_M1_R5_V4_RUN_RECEIPT_20261025_ZH.md` sha256 `2bf4745d9f01a192738362aa8ccaa30957ea2d3a83b1348d612894f7df7457a4` |
| 方向锁 | 主 Agent 08:24 枢轴批：**earnings quality / CF accruals / RNOA**；**禁**卖方研报/调研/金股/一致预期 |
| mechanism_tag（拟） | `g1g5_ashare_cfacc_desens_cs_v1`（与 r5 一致；冻结时再钉） |
| 并行他人 | P2 sampler→`/tmp`、叶27 降内存——**本草案不改那些文件** |

---

## 0. 结论先行（给主 / Arch）

1. 步骤−1 TTM recon **已过**；全叶仍是**另一扇独立研究窗**，须**新** `ARCH_RUN_AUTH_LEAF25_*` `.ok`（**禁止**复用 `1c32ab1e` / 任何 step_m1 钉）。
2. 本文件只钉**排窗意图与自检清单**；脚本 / `.cmd` / 输入 sha **待钉**（见 §8）；**未冻结 = 不得开跑**。
3. 主交付仍是**日度 α 向量 → Optimizer**，**非 Top-N 卫星主交付**（评价簿 Top6/Top10 仅作闸门对照）。
4. 请主排窗前先裁 §9「待主裁项」；Arch 审签前须补齐 §8 钉表。

---

## 1. 机制一页（who_pays）

**谁付钱（一句）**：付钱的是过度依赖报表利润、低估「利润现金含量」的交易者——高应计（NI_ttm ≫ CFO_ttm）公司后续易失望；本叶 long-only 买**低** CF 应计（脱敏截面），与 leaf19（CFACC×ΔRNOA）/ accrual_quality（BS 营运资本应计）公式可区分。

**主信号（拟，对齐 r5 §3；冻结前不改口径）**：

```
CFACC = (n_income_ttm − n_cashflow_act_ttm) / avg(TA_E, TA_{E−1y})
α_raw = desensitize(winsor 1/99 → rank → normal score)(−CFACC)   # 低应计优先
```

再按 r5 §4 做截面残差：SW L1 dummy + logmv + β120 + mom + logADV20 + vol20 + **leaf19 α（缺→0）** → base-α。慢 α（财报更新驱动；再平衡拟 20 交易日，冻结时钉）。快 gate（1–3 日）**不入 α**。

**明确不是**：卖方/调研/金股；BS Sloan WC 换皮；OCF/利润兑现主轴（indcap_momneut_ocf）；ADV 分位选股（capacity_adv）；Top-N 本身当主交付。

---

## 2. 数据契约 / 依赖（步骤−1 产物如何用）

### 2.1 步骤−1 已验收产物（只读契约；本窗**不重跑** recon）

| 物 | 路径 | sha256 |
|---|---|---|
| out_dir | `output/ai_factory/_leaf25_ttm_recon/20261025_111646/` | — |
| raw_rows.csv | 同上 | `5a0ba8fb3939389b085efb522783f3293e3cd3e1916164dba9845c20e0ae80ed` |
| ttm_script.csv | 同上 | `ba6d57d613ac87789a824dd9231e03eb8ad9cd3f01e30150d95f4aa5670490c6` |
| run_meta.json | 同上 | `b3dc83437c4bb679b088d52efd09462c61f522e4a0a0174330acbdf5487d8238` |
| rule_exercised | meta：i/ii/iii | **全 True**（ET_TS `20261025_111646`） |

**用法（契约意图）**：

- 全叶 build **必须**遵守 step_m1 已 exercised 的版本/TTM 规则（latest as-of、report_type=="1"、fallback/NaN/IPO 规则与 r5 §2）；不得另写一套差分。
- step_m1 三输出是 **recon 金标样本**，不是全市场 α 面板；全叶 α 由独立 build 脚本（§8 待钉）在密封/X2 窗上生成。
- 若 build 脚本改动 TTM 规则 → **新文件名 + 新 step_m1（新 `.ok`）**，不得静默漂移。
- 输入表 sha 以 r5 §2.0 为起点；Data 若有 10-14→10-16 重跑后变更，**冻结前重钉**（脚本换新文件名）。

### 2.2 拟读输入（冻结时重钉 sha；本草案不读盘核验）

| 表 | 路径（拟） | 备注 |
|---|---|---|
| 利润表 PIT | `data/v2/financials_pit/financials_pit_tushare.parquet` | 禁 fina_indicator 非 PIT 列 |
| 现金流 PIT | `data/v2/financials_pit/cashflow_pit_tushare.parquet` | |
| 资产负债 PIT | `data/v2/financials_pit/balancesheet_pit_tushare.parquet` | 取 total_assets |
| 日历 | `data/v2/calendar/trade_cal_sse_pit.parquet` | r5 钉 fa4260b8…（冻结重验） |
| SW L1 | `data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet` | r5 钉 89d4afa3… |
| 共享 as-of | `research/sw_members_asof.py::sw_l1_asof_with_gap_carry` | 现盘 sha256 `dec73305f8cd49d2c4ad695f72158e10bceb20de83fa19b2a1580be08579a9a7`（**待 Arch 确认可钉入全叶 `.ok`**；r5 曾阻塞于 DIFF C） |
| leaf19 α | `output/ai_factory/leaf19_cfacc_rnoa/alpha_*_20261014_213132.parquet` | 残差协变量；缺→0 |

辅：D1 `float_mktcap` / ADV 代理（仅残差与容量硬约束，**不作选股主轴**）。

---

## 3. Universe 双轨（FULLA 研究 / HI_LIQ 纸面）

| 轨 | 角色 | 掩码意图（路径待冻结钉） |
|---|---|---|
| **FULLA_V1** | 研究披露 / 覆盖闸 | `output/strategy_fulla/universe_mask_fulla_v1.parquet` |
| **HI_LIQ_V1.1** | **纸面主闸 / 判决轨** | `output/strategy_hiliq/universe_mask_hiliq_v1.parquet` |

掩码意图（Leo 规）：非 ST / 非停牌 / 上市≥60 日 / ADV20≥300 万（与既有 HI_LIQ 掩码列重建一致；冻结时与 Data/Strategy 对齐）。

覆盖硬闸（对齐 r5 / leaf19）：

- HI_LIQ：每再平衡日可算 α 名数 median **≥300**
- FULLA：median **≥800**

硬排除：`600519.SH`、`002371.SZ`；适用性排除：SW L1 银行+非银（房地产保留，S-exRE 仅披露）。

---

## 4. 密封窗与 X2 档

| 窗 | 日期（拟） | 角色 |
|---|---|---|
| **密封** | 2018-01-02 → 2024-05-31 | X2 全硬闸通过后**另 `.ok`** 只读一次；两档净超额相对 HI_LIQ wb **同号且 >0**，否则 WATCH 封顶 |
| **X2** | 2024-06-03 → **结束日冻结时写死字面日期**（不得写「发 `.ok` 时最新」） | 主判决窗 |

档位（对齐 GATE_V3 / r5）：

| 档 | AUM | 评价簿 | 单名帽（拟） |
|---|---|---|---|
| 60万 | 600_000 | Top-6 | 6%（余 510300） |
| 100万 | 1_000_000 | Top-10 | 6%（余 510300） |

- 行业帽：HI_LIQ **25%** / FULLA **28%**
- 成本：判决用 **30bp/边**；与 leaf19/23/24 对照表并报 17.5bp
- 年化：**244** 主 / 252 对照
- 交易：信号收盘 t → **T+1 开盘**；复权
- 主交付：日度 base-α 向量 parquet（非 Top-N 权重主交付）

---

## 5. 与 capacity_adv 对照（硬闸意图）

| 闸 | 意图 |
|---|---|
| **Gate A** | 相对 capacity_adv：ρ_excess **<0.5** 且残差 α **>0**；活跃集 Jaccard **≪0.7** 且 frac(J≥0.7)=0（≥0.7∧近等权→换皮硬拒） |
| **Gate B** | CMC v1.2：`cap80 + 叶20`；两档净 CAGR **> capacity_adv** |
| **GATE_V3** | 叠加后两档 MDD **≤25%**（另报 ≤15%）；衰减 KEEP；可交易（换手/成本） |
| **重复硬闸** | vs leaf19 / accrual_quality / indcap_momneut_ocf / leaf23 / leaf24：ρ_excess>0.5 **或** median top-10 Jaccard≥0.5 → FAIL |
| **衰减** | `alpha_decay_gate` v1.1 → **KEEP**（非 KEEP 不过） |
| **可交易** | 双边日换手 **≤20%**；成本拖累 ≤ 毛超额一半（无毛超额时 ≤1%/年）；单位换手成本 0.00175（GATE_V3）或判决 30bp（r5）——回执两口径并报 |

capacity_adv 自身是流动性分位主轴；本叶 **logADV20 仅残差协变量 + 容量硬约束**，**禁止** ADV 分位选股。

---

## 6. 自检清单（开跑前 / 回执必勾）

研究级自检（拟走 `research/leaf_selfcheck_v3.py` sha256 `ecaa30d8760f7ae5f53c330c128e6702476d01d8d69112b1dbf2fe769b7eaebe`，`--universe HI_LIQ_V1.1`）：

- [ ] **alpha_decay_gate** → KEEP（常数按 `ALPHA_DECAY_GATE_PREREG_ZH.md`，禁改）
- [ ] **换手 / 扣成本**：日换手≤20%；成本拖累合格（§5）
- [ ] **门 A**：vs capacity_adv ρ/残差/Jaccard
- [ ] **门 B**：CMC v1.2 `research/alpha_combo_marginal_v1_2.py` sha256 `bba212afadefce68dcd1bf76919f91de39402658e4398e925e3d80c6f01592c4`；cap80+叶20
- [ ] 覆盖 HI_LIQ≥300 / FULLA≥800
- [ ] 硬地板：两档净 30bp CAGR > HI_LIQ wb
- [ ] HAC t（NW lag 19）两档日净超额 vs HI_LIQ wb **≥ +2.50**（家族 n=4；若主裁 leaf21 同族则 t*=2.58）
- [ ] 非重复（§5）；非卖方/金股路径
- [ ] peak RSS 目标 ≤1.5GB（wrapper C4/STOPKB 钉法对齐 step_m1 经验；全叶可能更高——**禁抬帽**，只许分块/分窗 DIFF）
- [ ] 采样只写 `/tmp`（P2 落地后；本草案不改 wrapper）
- [ ] `live=false` / `promotion_approved=false` / 不交 Strategy / 不自跑 Book-Smoke

PASS 语义：研究级入场票；**晋级仅经 FWD**（r5：2026-11-02 起议）；Alpha 叶级闸审另开。

---

## 7. 执行阶段（拟序；均须独立 `.ok`）

| 阶段 | 内容 | `.ok` |
|---|---|---|
| 已完成 | 步骤−1 TTM recon | `…STEP_M1_R5_v4.ok` **已 CONSUMED**（禁复用） |
| **本草案目标** | 全叶 build α（FULLA+HI_LIQ）+ X2 评价 + 自检/CMC | **新** `ARCH_RUN_AUTH_LEAF25_FULL_FACTOR_X2_*.ok`（名待 Arch） |
| 后续（条件） | 密封窗只读复核 | **又一**独立 `.ok`（X2 全硬闸后） |
| 后续（主派） | Eng Book-Smoke | Eng 侧 `.ok`；AI 不自跑 |

每阶段：**一叶一档一 `.ok`**；禁自重试；窗外禁跑；`ai_no_retry=true`。

---

## 8. 独立 `.ok` 申请清单（路径 / 脚本 sha **待钉**）

> 本表供主排窗 + Arch 审签；**空单元格 = 未钉 = 不得发 `.ok`**。

| # | 钉项 | 拟路径 / 值 | 状态 |
|---|---|---|---|
| 1 | 预注册 | `docs/v2/AI_LEAF25_ACCRUALS_PREREG_DRAFT_r5.md`（或 r6 若再改） | DRAFT；**待 FROZEN** |
| 2 | 全叶 build 脚本 | `research/leaf25_cfacc_desens_build_*.py`（**新文件名；待写**） | **待钉 sha** |
| 3 | 全叶 eval / X2 脚本 | `research/leaf25_*_x2_*.py` 或复用工厂入口（待选） | **待钉 sha** |
| 4 | `.cmd` | `docs/v2/audit/leaf25_full_factor/LEAF25_FULL_FACTOR_X2_R1.cmd`（目录待建） | **待写** |
| 5 | wrapper | 拟 `cmc_wrapper_v4_6174eacb.sh` 或 P2 后 v5（采样尽 `/tmp`） | 待 Arch 裁 P2 后钉 |
| 6 | 内存估计 | `…/LEAF25_FULL_FACTOR_X2_R1_MEM_ESTIMATE.md` | **待写**（对照 step_m1 peak≈676MB；全叶预期更高→分块） |
| 7 | 输入表 sha 表 | income/cf/bs/cal/SW/D1 | 冻结前 `sha256sum` 重钉 |
| 8 | `sw_l1_asof_with_gap_carry` | `research/sw_members_asof.py` 现盘 `dec73305…` | **待 Arch 确认可钉** |
| 9 | leaf19 α sha | HI_LIQ `16202b2e…` / FULLA `c761dc36…`（r5 披露） | 冻结重验 |
| 10 | selfcheck / CMC | `leaf_selfcheck_v3` `ecaa30d8…` / CMC `bba212af…` | 现盘存在；冻结重验 |
| 11 | `.ok` 路径 | `output/ai_factory/ARCH_RUN_AUTH_LEAF25_FULL_FACTOR_X2_R1.ok`（名拟） | **未申请** |
| 12 | 窗 | 由**主排窗**填写 not_before / window / expires_et | **待主** |
| 13 | C4 / STOPKB / hard | 拟对齐 step_m1：C4=1331200 / stop=1484800 / hard=1536000（全叶若不够→**DIFF 降内存**，禁抬帽） | 待估 |
| 14 | out_dir 前缀 | `output/ai_factory/_leaf25_full_factor/<ET_TS>/` | 拟；禁写纸面/FROZEN |
| 15 | 采样 | 只 `/tmp/quantlab_leaf25_full_*/` | 依赖 P2 |
| 16 | X2 结束日 | 字面日期 | **待 Data/主裁** |
| 17 | 密封窗 `.ok` | 另签；本窗不含 | 后置 |

**申请前检查**：pgrep 读盘链空；Mem 充足；无 QUIET 冲突；不与叶27 窗重叠；`live=false`。

---

## 9. 缺口 / 待主裁项

1. **预注册冻结**：r5 仍 DRAFT；是否以 r5 直接 FROZEN，或先出 r6（钉 `sw_members_asof` `dec73305…`、X2 结束日、输入重钉）？
2. **X2 结束日**字面值（Data 重跑验证后）。
3. **全叶脚本产权**：谁写 build/eval（AI 本窗只交草案，未写脚本）；峰值内存预算与是否强制分块。
4. **P2 sampler→/tmp**：是否必须先 CONSUMED 再签全叶 `.ok`（Arch 曾标不挡 step_m1 消费；全叶建议挡住）。
5. **家族 t\***：leaf21 biz_climate 是否计入同族（n=4→t*=2.50 vs n=5→2.58）。
6. **排窗时刻**：避开叶27 降内存重跑窗；建议工作日 ET 明确 45–60min 密封执行窗。
7. **密封窗**：是否与 X2 分两张 `.ok`（本草案默认是）。

---

## 10. 禁项（红线）

- **禁自开跑** / **禁申 `.ok`** / **禁实跑读盘**（本文件阶段）
- 禁复用 step_m1 `.ok` `1c32ab1e` 或任何已 CONSUMED/VOID 钉
- 禁回到卖方研报/调研/金股/一致预期
- 禁抬 RSS 帽；禁 GP；禁空头腿；禁改 FROZEN_CONFIG / 纸面
- 禁把 STEP_M1_RECON_PASS 写成叶级 ACCEPT / 纸面票
- 禁改并行中的 P2 DIFF / 叶27 降内存文件

---

## 11. 状态机（本草案）

```
STEP_M1_RECON_PASS
    → [本文件] FULL_FACTOR_WINDOW_DRAFT_READY
        → 主排窗 + Arch 审钉 §8
            → 预注册 FROZEN + 新 .ok
                →（仅那时）窗内开跑 X2
                    → Alpha 叶级闸审
```

当前指针：**FULL_FACTOR_WINDOW_DRAFT_READY**（文档级）；**未冻结 / 勿开跑**。

live=false；promotion_approved=false。
