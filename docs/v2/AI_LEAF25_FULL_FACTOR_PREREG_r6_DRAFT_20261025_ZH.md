# 【DRAFT r6 — 未 FROZEN】叶25 全叶因子预注册草案（CF 应计 / earnings quality）

| 项 | 值 |
|---|---|
| 起草 | QuantLab AI · 2026-10-25 11:37:28 ET（初稿）；**修订** 2026-10-25 11:41:30 ET（America/New_York；墙钟 `2026-10-25T11:41:30-0400`） |
| 状态 | **DRAFT r6 / 未 FROZEN**；**X2 结束日已写入；待主令 FROZEN**；勿开跑 / 勿申 `.ok` / 勿实跑读盘 |
| live | **false** |
| promotion_approved | **false** |
| research_only | true |
| 本文件角色 | 主裁 2026-10-25 ~11:28 ET：**先 r6 再 FROZEN**（勿直接冻 r5）；供 Arch/主审钉表 |
| 前驱 r5 | `docs/v2/AI_LEAF25_ACCRUALS_PREREG_DRAFT_r5.md` sha256 `81123646382f7bb188a135e0d9142372b373c079e289d47066f5587a1fde40e1`（**仍未 FROZEN；本 r6 继任冻结底座**） |
| 全叶窗草案 | `docs/v2/AI_LEAF25_FULL_FACTOR_WINDOW_DRAFT_20261025_ZH.md` sha256 `994324c9ad0c4cc10d2f24426ed9375ca6ec79bf3ca191aa9d53409d00eab002` |
| 步骤−1 | **STEP_M1_RECON_PASS**（Alpha 披露 `63868a18a759de179a195e33eca7943674371e16492387e15d8c0f8f68c93278`）；AI 回执 `2bf4745d9f01a192738362aa8ccaa30957ea2d3a83b1348d612894f7df7457a4`；Arch CONSUMED `9c96bf351ef6e6e69b127ef9e308569e01f574dd5840588866239a842473c838`；`.ok` `1c32ab1e…` **已消费，禁复用** |
| MEM/分块 | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_FULL_FACTOR_MEM_ESTIMATE_CHUNK_20261025_ZH.md` sha256 `103717df1f9e5d63f8c681f16da091f44801e1b69b219ae1a18b2159446145d1`（同批交付；强制分块、禁抬帽；本修订无 PENDING） |
| Data X2 结束日 PIN | `docs/v2/audit/DATA_LEAF25_X2_END_DATE_DISK_PIN_20261025_ZH.md` sha256 `adb219a0094da06441793d0b90c59424ba3d23b511e46762deb16d30cff7eb2a`；主钉候选 **FROZEN 候选**（主→AI ~11:37 ET） |
| mechanism_tag | `g1g5_ashare_cfacc_desens_cs_v1`（与 r5 一致） |

---

## 0. r6 相对 r5 的变更（主裁钉死 + Arch 新核）

| # | 项 | r5 | r6（本草案） |
|---|---|---|---|
| 1 | 冻结路径 | r5 待 DIFF C / sw 落地后冻 | **先出 r6 再 FROZEN**；勿直接冻 r5 |
| 2 | `sw_members_asof` | 阻塞表述 / 待落地 | Arch **PIN_OK_WITH_CONDITIONS** 文 sha `4e4ca0b80d8f0280addb3cfccb967505839f426826b83c84c12bfe2a5d619374`；脚本现盘 **MATCH** `dec73305f8cd49d2c4ad695f72158e10bceb20de83fa19b2a1580be08579a9a7`；入口 `sw_l1_asof_with_gap_carry` |
| 3 | 测试 | 未共钉 | 建议同钉 `research/tests_sw_pit/test_sw_members_asof.py` = `e80f98ed778dbb82d096716fc87c76306fe14d887c177015e623e534514794cc`（Arch） |
| 4 | cal + SW 共钉 | r5 已写路径 | **须共钉**现盘 MATCH：日历 `fa4260b808755b9a1c91e3ade210edec84bbdb91e0dfff4c6a955c4d35fd8a41`；SW L1 CLEAN `89d4afa337435a2302b5c13fd4cf049b71eda2f20e1d9094f15d62cdb587f66c`；`gap_carry` **显式传 TradeCal**；经 **r6 冻结**写入；日历续期致 sha 变 → 改 `TRADE_CAL_SHA_PIN`（脚本 sha 变）并 **重签** 一切钉旧 `dec73305` 的 `.ok` |
| 5 | X2 结束日 | 「冻结时写死」 | **已钉字面值** `X2_END_TRADE_DATE=20261009`；窗 **2024-06-03 → 2026-10-09**；Data 回执 sha `adb219a0094da06441793d0b90c59424ba3d23b511e46762deb16d30cff7eb2a`；瓶颈 `float_mktcap_daily_from2015_tushare` sha `346d0dda8a95e8d209fd388cfb1aad5425745fc0b5eb0a16dd4de3ab3d72a1ef`；**勿**改钉 daily_basic/adv20 上移结束日（须另 PIN） |
| 6 | 家族 t* | leaf21 待主裁 | 主裁：**leaf21 不同族** → n=**4**，t*=**2.50** |
| 7 | P2 sampler→`/tmp` | 未钉 | Arch 审阅 **PASS** sha `964cf57be56e8723fcff79ba620c5034e18b6e0fe083f59bef939e5db4705f78`；DIFF `9584723f8dcce3907c797fd3b50d15576491a1f3898690b75c97fd707337fa38`；wrapper v5 `4240ce82f0929085ab4bcb37e2400a3414e70e162c9e697cf02d97103342f882` **可钉全叶**；采样强制 `/tmp`；**C5 不放宽**；P3 mkdir 非挡可后续。**P2 前置门 = 已满足** |
| 8 | `.ok` 结构 | 一窗一签倾向 | 密封与 X2 **分两张独立 `.ok`**（主裁钉死） |
| 9 | 内存 | step_m1 帽 | 全叶 **强制分块**；C4/stop/hard **对齐 step_m1**；**禁抬帽**（见 MEM 文） |
| 10 | 禁复用 | — | **禁复用** step_m1 `.ok` `1c32ab1e5ffb9eb3ddf466f15b0cd778a1579eaca678f2f5fbe1dd1ae00e66f0` 及任何已 CONSUMED/VOID 钉 |

**仍不签全叶 `.ok`，直至同时满足**：r6 **FROZEN**（主令）+ 钉表齐（§8）+ MEM/分块方案经 Arch 审 + 密封/X2 分签准备齐 + 主填窗。P2 PASS 与 X2 结束日字面钉入 **不替代**上述其余闸；**本文件不得自行宣布 FROZEN**。

---

## 1. 机制一页（who_pays；对齐 r5 §1 / 全叶草案 §1）

**谁付钱**：过度依赖报表利润、低估「利润现金含量」的交易者——高应计（NI_ttm ≫ CFO_ttm）公司后续易失望；本叶 long-only 买**低** CF 应计（脱敏截面）。与 leaf19（CFACC×ΔRNOA）/ accrual_quality（BS WC 应计）公式可区分。

**主信号（冻结前不改口径）**：

```
CFACC = (n_income_ttm − n_cashflow_act_ttm) / avg(TA_E, TA_{E−1y})
α_raw = desensitize(winsor 1/99 → rank → normal score)(−CFACC)   # 低应计优先
```

截面残差（再平衡拟 20 交易日，FROZEN 时钉）：SW L1 dummy + logmv + β120 + mom + logADV20 + vol20 + **leaf19 α（缺→0）** → base-α。快 gate（1–3 日）**不入 α**。

**明确不是**：卖方/调研/金股/一致预期；BS Sloan WC 换皮；OCF/利润兑现主轴；ADV 分位选股；Top-N 当主交付。

---

## 2. 家族与 t*（主裁钉死）

| 成员 | 备注 |
|---|---|
| leaf19 cfacc_rnoa | 同族 |
| accrual_quality | 同族 |
| indcap_momneut_ocf | 同族 |
| **leaf25（本叶）** | 同族 |
| leaf21 biz_climate | **不同族**（主裁）；仅 ρ 披露，**不计入 n** |

- 家族 **n=4**；HAC t*（NW lag 19）两档日净超额 vs HI_LIQ wb：**≥ +2.50**（Φ⁻¹(1−0.05/8)≈2.4977→2.50）
- 重复硬闸仍对 leaf19 / accrual_quality / indcap_momneut_ocf / leaf23 / leaf24（ρ_excess>0.5 或 median top-10 Jaccard≥0.5 → FAIL）

---

## 3. Universe 双轨

| 轨 | 角色 | 掩码意图（路径 FROZEN 时重钉 sha） |
|---|---|---|
| **FULLA_V1** | 研究披露 / 覆盖闸 | `output/strategy_fulla/universe_mask_fulla_v1.parquet` |
| **HI_LIQ_V1.1** | **纸面主闸 / 判决轨** | `output/strategy_hiliq/universe_mask_hiliq_v1.parquet` |

覆盖硬闸：HI_LIQ 每再平衡日可算 α median **≥300**；FULLA median **≥800**。硬排除 `600519.SH`、`002371.SZ`；适用性排除 SW L1 银行+非银（房地产保留；S-exRE 仅披露）。

---

## 4. 密封窗与 X2（结束日已钉）

| 窗 | 日期 | 角色 | `.ok` |
|---|---|---|---|
| **密封** | **2018-01-02 → 2024-05-31** | X2 全硬闸通过后**另签**只读一次；两档净超额相对 HI_LIQ wb **同号且 >0**，否则 WATCH 封顶 | **独立** `ARCH_RUN_AUTH_LEAF25_FULL_FACTOR_SEALED_*.ok`（名待 Arch） |
| **X2** | **2024-06-03 → 2026-10-09** | 主判决窗；`X2_END_TRADE_DATE=20261009`（**20261009**） | **独立** `ARCH_RUN_AUTH_LEAF25_FULL_FACTOR_X2_*.ok`（名待 Arch） |

### 4.1 `X2_END_TRADE_DATE=20261009`（主钉 · Data PIN）

| 项 | 值 |
|---|---|
| 字面结束日 | **`20261009`**（SSE `is_open=1`；展示 `2026-10-09`） |
| X2 窗 | **2024-06-03 → 2026-10-09** |
| 密封窗（不变） | **2018-01-02 → 2024-05-31** |
| Data 回执 | `docs/v2/audit/DATA_LEAF25_X2_END_DATE_DISK_PIN_20261025_ZH.md` sha256 `adb219a0094da06441793d0b90c59424ba3d23b511e46762deb16d30cff7eb2a` |
| 瓶颈板 | `data/v2/float_mktcap/float_mktcap_daily_from2015_tushare.parquet` sha256 `346d0dda8a95e8d209fd388cfb1aad5425745fc0b5eb0a16dd4de3ab3d72a1ef`（`trade_date` max=20261009） |
| 主裁语义 | **FROZEN 候选**字面值已写入本 r6 DRAFT；**仍待主令宣布 FROZEN**（本文件不自宣 FROZEN） |

**硬约束（主钉）**：

- **勿**改钉 `daily_basic` raw / HI_LIQ `adv20_yuan` 以把结束日上移到 20261014/20261016——**须另出 PIN / 改契约后再写**。
- **不得**写「发 `.ok` 时最新」或墙钟日。
- 旧「结束日待 Data」占位 **已清除**；字面值变更 → 新文件名 r6.x / 冻结补丁，不得静默改本文件冒充未变。

档位（对齐 GATE_V3 / r5）：60万 Top-6 / 100万 Top-10；单名帽 6%（余 510300）；行业帽 HI_LIQ 25% / FULLA 28%；判决成本 **30bp/边**（对照表并报 17.5bp）；年化 244 主 / 252 对照；信号收盘 t → **T+1 开盘**；主交付日度 base-α parquet（非 Top-N 权重）。

---

## 5. 门 A / 门 B / 其它硬闸（对齐全叶草案 §5）

| 闸 | 意图 |
|---|---|
| **Gate A** | vs capacity_adv：ρ_excess **<0.5** 且残差 α **>0**；活跃集 Jaccard **≪0.7** 且 frac(J≥0.7)=0 |
| **Gate B** | CMC v1.2：`cap80 + 叶20`；两档净 CAGR **> capacity_adv** |
| **GATE_V3** | 两档 MDD **≤25%**（另报 ≤15%）；衰减 KEEP；可交易 |
| **重复硬闸** | §2 |
| **衰减** | `alpha_decay_gate` v1.1 → **KEEP** |
| **可交易** | 双边日换手 **≤20%**；成本拖累合格 |
| **硬地板** | 两档净 30bp CAGR > HI_LIQ wb |
| **HAC t*** | 两档 ≥ **+2.50**（n=4） |

selfcheck：`research/leaf_selfcheck_v3.py` sha256 `ecaa30d8760f7ae5f53c330c128e6702476d01d8d69112b1dbf2fe769b7eaebe`（FROZEN 重验）。  
CMC：`research/alpha_combo_marginal_v1_2.py` sha256 `bba212afadefce68dcd1bf76919f91de39402658e4398e925e3d80c6f01592c4`（FROZEN 重验）。

---

## 6. 步骤−1 契约（只读；本窗不重跑 recon）

| 物 | 路径 / 值 |
|---|---|
| out_dir | `output/ai_factory/_leaf25_ttm_recon/20261025_111646/` |
| raw_rows.csv | sha256 `5a0ba8fb3939389b085efb522783f3293e3cd3e1916164dba9845c20e0ae80ed` |
| ttm_script.csv | sha256 `ba6d57d613ac87789a824dd9231e03eb8ad9cd3f01e30150d95f4aa5670490c6` |
| run_meta.json | sha256 `b3dc83437c4bb679b088d52efd09462c61f522e4a0a0174330acbdf5487d8238` |
| rule_exercised | i/ii/iii **全 True**；ET_TS `20261025_111646`；peak_kb=675792 |
| `.ok` | `1c32ab1e…` **CONSUMED** → **禁复用** |

全叶 build **必须**遵守 step_m1 已 exercised 的版本/TTM 规则；改规则 → **新文件名 + 新 step_m1（新 `.ok`）**。

---

## 7. P2 前置（已满足；仍不签 `.ok`）

| 项 | sha256 全长 | 状态 |
|---|---|---|
| AI DIFF | `9584723f8dcce3907c797fd3b50d15576491a1f3898690b75c97fd707337fa38` | 已交 |
| Arch 审阅 | `964cf57be56e8723fcff79ba620c5034e18b6e0fe083f59bef939e5db4705f78` | **PASS** |
| wrapper v5 | `4240ce82f0929085ab4bcb37e2400a3414e70e162c9e697cf02d97103342f882`（`docs/v2/audit/cmc_v1_1_leaf24/cmc_wrapper_v5_4240ce82.sh`） | **可钉全叶** |
| unified DIFF | `c903234b5afcadec73f911e7c05f27b06a7e3d431801183bc85dfc9a21cca903` | MATCH |
| 采样 | 强制默认 `/tmp/quantlab_wrapper_sampler/`；硬禁 output*/data* | 钉入全叶 `.cmd` |
| C5 | **不放宽** | 钉 |
| P3 mkdir 顺序 | 非挡；可后续 | 不挡签 |

**语义**：P2 门从「挡全叶签」→「前置已满足」。**仍禁止**在 r6 未 FROZEN（主令）/ 钉表未齐 / MEM 未审 / 分签未备时申发全叶 `.ok`。X2 结束日字面值已钉入 §4（Data 缺口门已解除）。

---

## 8. 钉表（空/PENDING = 不得发 `.ok`）

| # | 钉项 | 值 | 状态 |
|---|---|---|---|
| 1 | 本预注册 | 本文件（r6 DRAFT） | **DRAFT；X2 结束日已写入；待主令 FROZEN** |
| 2 | `sw_members_asof.py` | `dec73305f8cd49d2c4ad695f72158e10bceb20de83fa19b2a1580be08579a9a7` | Arch **PIN_OK_WITH_CONDITIONS**（文 `4e4ca0b8…`）；**可钉** |
| 3 | 测试 | `e80f98ed778dbb82d096716fc87c76306fe14d887c177015e623e534514794cc` | Arch 建议同钉 |
| 4 | Arch 钉核文 | `docs/v2/audit/leaf25_step_m1/ARCH_LEAF25_SW_MEMBERS_ASOF_PIN_CHECK_20261025_ZH.md` sha `4e4ca0b80d8f0280addb3cfccb967505839f426826b83c84c12bfe2a5d619374` | 已落 |
| 5 | 日历 | `data/v2/calendar/trade_cal_sse_pit.parquet` = `fa4260b808755b9a1c91e3ade210edec84bbdb91e0dfff4c6a955c4d35fd8a41` | 现盘 MATCH；**须与 #2 共钉**；FROZEN 瞬间再 `sha256sum` |
| 6 | SW L1 CLEAN | `data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet` = `89d4afa337435a2302b5c13fd4cf049b71eda2f20e1d9094f15d62cdb587f66c` | 现盘 MATCH；**须与 #2 共钉** |
| 7 | gap_carry 约定 | 调用 `sw_l1_asof_with_gap_carry` **显式传 TradeCal**；禁 `sha_pin=None` 生产路径 | **写入 FROZEN 正文** |
| 8 | 日历续期耦合 | cal sha 变 → 改脚本 `TRADE_CAL_SHA_PIN` + 重签一切钉旧 `dec73305` 的 `.ok` | 运维约束 |
| 9 | income / cf / bs | r5 §2.0 起点 sha（bc0f4c3d… / 71d5c3d3… / 9ca05496…） | **FROZEN 前重钉**（Data 重跑可能变更；脚本换新文件名） |
| 10 | leaf19 α | HI_LIQ `16202b2e…` / FULLA `c761dc36…`（r5） | FROZEN 重验 |
| 11 | P2 / wrapper v5 | PASS `964cf57b…` / v5 `4240ce82…` | **前置已满足** |
| 12 | 全叶 build 脚本 | `research/leaf25_cfacc_desens_build_*.py`（**新文件名；待写**） | **待钉 sha** |
| 13 | 全叶 eval / X2 脚本 | `research/leaf25_*_x2_*.py` 或工厂入口（待选） | **待钉 sha** |
| 14 | MEM/分块 | 同批 MEM 文 sha `103717df1f9e5d63f8c681f16da091f44801e1b69b219ae1a18b2159446145d1` | **待 Arch 审** |
| 15 | C4 / STOPKB / hard | **对齐 step_m1**：C4=`1331200` / stop=`1484800` / hard=`1536000`（kB）；不够就拆，**禁抬帽** | 钉意图 |
| 16 | 采样 | 只 `/tmp/quantlab_*`（wrapper v5 默认） | 钉 |
| 17 | X2 结束日 | **`X2_END_TRADE_DATE=20261009`**；窗 2024-06-03→2026-10-09；Data 回执 `adb219a0094da06441793d0b90c59424ba3d23b511e46762deb16d30cff7eb2a`；瓶颈 float_mktcap `346d0dda8a95e8d209fd388cfb1aad5425745fc0b5eb0a16dd4de3ab3d72a1ef` | **已钉字面值**（主 FROZEN 候选）；**勿**经 daily_basic/adv20 上移（须另 PIN） |
| 18 | X2 `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF25_FULL_FACTOR_X2_R1.ok`（名拟） | **未申请** |
| 19 | 密封 `.ok` | 另签；X2 全硬闸后；密封窗 2018-01-02→2024-05-31 | **未申请**；**禁与 X2 同张** |
| 20 | 窗 | not_before / window / expires_et | **待主**（建议 45–60min 工作日 ET；避叶27 重跑） |
| 21 | out_dir 前缀 | `output/ai_factory/_leaf25_full_factor/<ET_TS>/` | 拟；禁写纸面/FROZEN |
| 22 | 禁复用 | `1c32ab1e…` 及任何 CONSUMED/VOID | **硬禁** |
| 23 | float_mktcap D1（X2 瓶颈） | `data/v2/float_mktcap/float_mktcap_daily_from2015_tushare.parquet` = `346d0dda8a95e8d209fd388cfb1aad5425745fc0b5eb0a16dd4de3ab3d72a1ef` | 现盘 MATCH；尾日 20261009 |

---

## 9. 与全叶窗草案 `994324c9…` 对照表

| 草案 § / 项 | 草案状态 | r6 处置 |
|---|---|---|
| §9.1 先 r6 再冻？ | 待主裁 | **主裁已裁：先 r6**（本文） |
| §9.2 X2 结束日 | 待 Data | **已钉** `20261009`（2024-06-03→2026-10-09）；回执 `adb219a0094da06441793d0b90c59424ba3d23b511e46762deb16d30cff7eb2a`；**勿**改钉 daily_basic/adv20 上移 |
| §9.3 脚本产权 / 分块 | 待裁 | AI 写 build/eval + MEM；**强制分块**；禁抬帽 |
| §9.4 P2 是否挡签 | 建议挡 | Arch P2 **PASS** → 前置**已满足**；仍不签直至 §0 余闸齐 |
| §9.5 家族 t* | leaf21？ | **不同族；n=4；t*=2.50** |
| §9.6 密封/X2 分签 | 默认是 | **主裁钉死：分两张 `.ok`** |
| §9.7 排窗 | 待主 | 等 r6 FROZEN + §8 钉齐 + 叶27 降内存包交审后由主填（P2✅；X2 结束日✅） |
| §2.2 sw `dec73305`「待 Arch」 | 待确认 | Arch **PIN_OK_WITH_CONDITIONS** `4e4ca0b8…`；共钉 cal+SW |
| §8 #5 wrapper | 待 P2 | **v5 `4240ce82` 可钉** |
| 禁复用 `1c32ab1e` | 已写 | **维持** |

---

## 10. 执行阶段（拟序；均须独立 `.ok`）

| 阶段 | 内容 | `.ok` |
|---|---|---|
| 已完成 | 步骤−1 TTM recon | `…STEP_M1_R5_v4.ok` **已 CONSUMED**（禁复用） |
| **本 r6 目标（X2）** | 全叶 build α（FULLA+HI_LIQ）+ X2 评价 + 自检/CMC；窗至 **20261009** | **新** X2 `.ok` |
| 后续（条件） | 密封窗只读复核（2018-01-02→2024-05-31） | **又一**独立密封 `.ok` |
| 后续（主派） | Eng Book-Smoke | Eng 侧；AI 不自跑 |

每阶段：一叶一档一 `.ok`；`ai_no_retry=true`；窗外禁跑；`live=false`。

---

## 11. 禁项（红线）

- **禁自开跑** / **禁申 `.ok`** / **禁实跑读盘** / **禁 git commit**（本 DRAFT 阶段）
- 禁复用 `1c32ab1e` 或任何已 CONSUMED/VOID 钉
- 禁直接冻 r5；须经本 r6（或主裁等价）FROZEN；**禁本文件自行宣布 FROZEN**
- 禁静默改 `X2_END_TRADE_DATE`；变更须新文件名 / 冻结补丁
- **禁**经 `daily_basic` / `adv20` 上移 X2 结束日而不另出 PIN
- 禁抬 RSS 帽；禁 GP；禁空头腿；禁改 FROZEN_CONFIG / 纸面
- 禁把 STEP_M1_RECON_PASS 写成叶级 ACCEPT / 纸面票
- 禁改并行中的叶27 降内存文件（他人线）
- 禁放宽 C5；禁 ADV 分位选股；禁卖方/金股路径

---

## 12. 状态机

```
STEP_M1_RECON_PASS
  → FULL_FACTOR_WINDOW_DRAFT_READY (994324c9)
    → [本文件] PREREG_r6_DRAFT_READY
        → X2_END 字面钉入 (20261009；Data PIN adb219a0…)
        → Arch/主审钉表 + MEM 审
            → r6 FROZEN（**仅主令**）
                → 主排窗 + 签独立 X2 .ok（P2 前置已满足）
                    → 窗内开跑 X2（→2026-10-09）
                        →（条件）独立密封 .ok
                            → Alpha 叶级闸审
```

当前指针：**PREREG_r6_DRAFT_READY**（文档级；**X2 结束日已写入**）；**未 FROZEN / 勿开跑 / 勿申 `.ok`**。

live=false；promotion_approved=false。
