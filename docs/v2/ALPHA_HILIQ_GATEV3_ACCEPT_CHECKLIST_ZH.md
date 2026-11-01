# HI_LIQ_V1.1 × GATE_V3 纸面腿验收清单（Alpha）

- 起草：2026-10-14 07:51 ET（开腿前；在看到任何 HI_LIQ capacity_adv / B4 回测数字之前）
- 依据：`docs/v2/STRATEGY_HI_LIQ_SUBSET_PREREG_V1_1_ZH.md`、`docs/v2/GATE_V3_MDD25_PREREG_ZH.md`、`docs/v2/ALPHA_LEAF_ACCEPT_V2_PREREG_ZH.md`
- **不改**既有纸面 FROZEN_CONFIG；promotion_approved=false；live=false；handoff=NO；禁 GP
- 本清单只约束 **HI_LIQ 纸面候选轨**；FULLA_V1 研究轨另报，不进纸面
- 修订：2026-10-14 08:22 ET — Arch P1：硬断言 `ind_cap_ok_book` 必须 True；失败腿 REJECT 不进 B4/密封（§2.1）

## 0. 前置（缺一即停）

1. 宇宙 = HI_LIQ_V1.1 掩码 `output/strategy_hiliq/universe_mask_hiliq_v1.parquet`（ADV20≥1亿；**无市值筛**；ST/停牌/上市<60日剔除）。
2. 腿目录 = `output/strategy_hiliq/legs/`（与 fulla / ai_factory 隔离）。
3. capacity_adv：≤25 名 + 510300 固定 20%；单票 ≤4%；袖内 `ADV_PARTICIPATION_K=0.006`；**申万一级 / 股票袖 ≤25%**（压舱不计入分母；超配按比例压缩，溢出顺延给未触顶行业下一排名）。
4. B4：合成 50/25/25 不变；60万 N=6、100万 N=10；组合单票 ≤6%；同样行业袖内 ≤25%。
5. 口径：净收益（17.5bp/单位换手）、T+1 next_open、年化 244 日；按手取整。

## 1. 报告必报（密封窗 + X2；60万 ∧ 100万）

每窗、每档须同时给出：

| 项 | 要求 |
|---|---|
| CAGR / MDD / Calmar / 日胜率 | 与 **top300 纸面基线**并列 |
| 申万一级分布 | 股票袖权重口径；**电子、计算机、通信、医药生物** 单独列示（可为 0） |
| 小盘贡献 | PIT 总市值后 30% 收益贡献 **仅披露**，不作剔除 |
| 窗口标注 | 密封窗 2018-01-02→2024-05-31（开发/验证，**非晋级**）；X2 2024-06-03→2026-10-09（**样本内**） |

## 2. 行业硬闸（构造时 + 验收时）

- 股票袖内任一申万一级权重 / 股票袖合计 ≤ **25%**。
- 验收：抽检再平衡日 `max_ind_share_of_sleeve ≤ 0.25 + 1e-6`；否则腿包 FAIL，不进 X2。
- **硬断言（Arch P1）**：`.check.json` 的 `ind_cap_ok_book` **必须为 True**；失败 → REJECT，拒收进 B4/密封合成（详见 §2.1）。
- 510300 / 现金不计入行业分母。


## 2.1 硬断言：ind_cap_ok_book（Arch 审计 P1 / 2026-10-14 ≈08:17 ET）

合成 B4 / 密封窗 **之前** 每条 HI_LIQ 腿的 `.check.json` 必须满足：

| 断言 | 要求 | 失败处置 |
|---|---|---|
| `ind_cap_ok_book` | **必须 `True`** | **REJECT**；不得进 B4 / 密封合成 |
| 股票袖内申万一级 | `max_sleeve_frac ≤ 0.25 + 1e-6`（或等价 `max_ind_share_of_sleeve`） | 同上 |
| `max_book_ind_weight` | 若脚本以全书权重口径报告，须 ≤ 袖内 25% 对应上限；与 `ind_cap_ok_book` 冲突则以 `ind_cap_ok_book=False` 为准拒收 | 同上 |

- 缺字段 / 字段为 false / 行业超限 → 腿状态 **REJECT_IND_CAP**；通知 AI 重生前 **禁止** 纳入 B4 / 密封合成。
- 案例（Arch N1）：`g1g5_equity_incentive_hiliq_v1_daily_weights_20261014_195554` → `ind_cap_script=0.25` 但 `max_book_ind_weight=0.28`、`ind_cap_ok_book=False` → **REJECT_IND_CAP / 不进 B4**（见 `docs/v2/ALPHA_HILIQ_EQUITY_INCENTIVE_REJECT_IND_CAP_20261014_ZH.md`）。
- 本断言与 §2 并存；验收抽检与合成前拒收均强制执行。

## 3. 叶验收顺序（叶验收 v2，不得跳步）

1. **HC（假设批判）** → 一票否决则停。
2. **单叶 ACCEPT**（研究级）。
3. **CMC（组合边际贡献）** → 叠加现主书（HI_LIQ 上的 capacity_adv±B4）后，两档净 CAGR 提升 <0.5pp → WATCH、**不派烟**；≤0 或拖累主书 → **FAIL，fail-fast**。
4. **衰减门 v1.1** → 必须 **KEEP**（capacity_adv/B4 仅可 flag）。
5. **GATE_V3 本地四条**（见 §4）→ 全过才可请 Eng。
6. **Eng Book-Smoke X2** → 终判；本地过、X2 不过 = FAIL，不重烟。

## 4. GATE_V3 四条（HI_LIQ 口径；门规本身不改）

Setup：cap80 + leaf20；top-N 6/10；单名 ≤6%。**对照基准 = 同引擎、同 HI_LIQ 掩码下的 capacity_adv 单跑**（不是 top300 旧基线）。

| # | 条件 | 两档（60万 ∧ 100万） |
|---|---|---|
| 1 | MDD ≤ **25%**（另报 ≤15% 参考） | 两档均须 |
| 2 | 净 CAGR **严格高于** HI_LIQ capacity_adv 单跑 | 两档均须 |
| 3 | 衰减门 v1.1 = **KEEP** | — |
| 4 | 可交易：双边换手 ≤ **20%/日** + 成本拖累规则 | — |

任一条不过 → 本地 FAIL；不派 Eng。叶不提升主书（CMC 或对 capacity_adv 边际为负）→ **立即 FAIL**，不进入后续烟测。

## 5. 纸面轨 / 晋级

- 现纸面仍为 top300 FROZEN_CONFIG，直至 **Leo 在本 Alpha 聊天原话**明示晋级 HI_LIQ。
- 裸 FULLA 腿 **不进纸面**。
- promotion_approved=false；live=false；handoff=NO。
- 闸门/纸面/晋级变更须 Leo 原话；主 Agent 转述不等于授权。

## 6. 交付物

- 腿 parquet + `.check.json`（行数、日期、日名数、权重和、单票上限、**行业袖内上限**、旧 top300 外占比、mask/script sha、NaN）。
- 诊断 JSON（可选）：HI_LIQ vs top300 vs FULLA，净/T+1/244，CAGR/MDD@60∧100万。
- TEAM_STATE Alpha 节更新；`ql_bus.emit('QuantLab Alpha','progress'|gate', …)`。
- 通知 Strategy：可合成 B4 / 跑密封窗+X2。

## 7. 明确不做

- 不改 FROZEN_CONFIG；不网格 ADV/行业上限；不把 FULLA 失败 MDD 反推进 HI_LIQ 参数。
- 不派烟给 CMC_FAIL / HC 否决 / 衰减非 KEEP / GATE_V3 本地 FAIL 的叶。
- 不做 GP。
- **拒收** `ind_cap_ok_book=False` 的 HI_LIQ 腿进 B4 / 密封合成（Arch P1）；待 AI 重生且断言通过后再议。

## 8. 验收范式（Leo 07:56–07:58 ET；残差/特质 α + 中性化 + 快慢错配）

**可用作闸门证据（须齐备）：**

1. **域内残差 α 质量** + **特质 α（idiosyncratic α）**：行业/风格残差正交化后的预测力；不得把 β 当 α。
2. **行业+风格中性化后相对基准的有效性**。
3. **快慢因子错配 / 伪耦合检查**：不得仅靠叶子简单加权求和过门；须看残差 ρ、换手半衰期、叠加 vs 加权和的正交增量。

**明确拒绝作为闸门证据：**

- **仅 Top-N 等权回测**；**仅叶子简单加权求和**冒充组合边际。可作 `diag_*` 披露，不得单独支撑 ACCEPT / 派烟 / 纸面。

仍强制：密封窗 + Eng X2；60万 ∧ 100万；GATE_V3 四条；HI_LIQ 行业袖内 ≤25%；电子/计算机/通信/医药生物单列；叶不提升主书 → fail-fast。详见 `docs/v2/ALPHA_ACCEPT_PARADIGM_RESID_NEUT_ZH.md`。

## 9. 附录：主 Agent 裁定（2026-10-18 00:54 ET）— 基准 + 并列披露 + §8 读法勘误（落盘 2026-10-18 00:56 ET）
- **HI_LIQ 叶 CMC / GATE_V3 基准 = capacity_adv HI_LIQ 单跑，按 book-smoke 口径**：60万 −0.6%/−29.9%，100万 1.7%/−33.0%（`output/strategy_hiliq/capadv_x2/`）。**不是 B4**，B4 只作诊断。本条覆盖 §3 第 3 步「叠加现主书（HI_LIQ 上的 capacity_adv±B4）」以及 §4 中的对照表述，作为唯一基准。
- **强制并列披露**：扣成本后相对 **HI_LIQ 池内等权**的净超额，包括 CAGR 差、对池 EW 回归的残差 α 和 HAC t。**赢了 capacity_adv 但没赢池 EW 的叶，不报 Leo。**
- **§8 读法勘误获批**，标注为「**事后提出，仅对后续叶生效**」，阈值不变。详见 `docs/v2/ALPHA_EQUITY_SIGN_RECON_20261018_ZH.md` §6：事件/稀疏腿的 A/A′ 并列 (i) 0/1 持仓 vs 原始 fwd20 和 (ii) 残差 z vs 中性化 fwd，以 (ii) 为主读、(i) 须同向，CMC 用 (ii)；B 在腿内等权时用全袖，并列冻结风格集和 AI 风格集（mom20/vol20），两者符号相反时记 PASS*（不稳健）。
- **v4 验收已被接受**（`docs/v2/ALPHA_HILIQ_LEGS_ACCEPT_20261014_ZH.md`）。
- 实现：`research/alpha_combo_marginal.py --universe hiliq` 的默认 `--base capadv` 读取上述 book-smoke 目标权重（`--base b4` 只作诊断），并输出 `vs_poolEW` 和 `report_to_leo_eligible`。
  - 注意：book-smoke 的 BOOK 目标权重在两档都是 **25 名全腿**（每日股票中位数 25 名，不是 6/10 名）。LC 引擎对同一目标权重给出 1.26%/−36.6%，两档相同；book-smoke 给出 −0.6%/1.7%，差别来自整手、成交率（60万 fill 0.55）和成本。**闸门数字以 book-smoke 为准**；CMC 脚本内的 B0 是同一目标在 LC 引擎下的近似。
- 不改 FROZEN_CONFIG，不动纸面轨；promotion_approved=false；live=false。
