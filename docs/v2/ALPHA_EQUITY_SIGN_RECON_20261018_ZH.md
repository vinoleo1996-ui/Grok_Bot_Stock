# equity_incentive（HI_LIQ 202436）§8 符号分歧对账 + §8 读法勘误（Alpha）

- 落盘：2026-10-18 00:52 ET（实际落盘时间）。只读；FROZEN/纸面未动；live/promotion=false；不派 Eng；禁 GP。
- 对照：AI `docs/v2/AI_EQINC_SEC8_RECONCILE_ZH.md`、`output/ai_factory/hiliq_sec8/eqinc_reconcile.json`；Arch `docs/v2/audit/AUDIT_20261018_0016_ET_ZH.md` N4。
- Alpha 独立脚本（nice，与 AI 串行；未改 AI 和 S8 原脚本）：
  - `research/alpha_eqinc_recon_ai_repro.py`：照抄 AI 代码复现 AI 数。
  - `research/alpha_eqinc_recon_leaf1920.py`：因子拆解。
  - `research/alpha_s8_errata_sparse_ic.py`：五腿按两种新读法重报 A/A′。
  - `research/alpha_s8_errata_fullsleeve_b.py`：B 改按 20 名全袖计算。
- 产出：`output/alpha/recon_eqinc/step_{a,b,c,d}*.json`。

## 1. 两边数字都已复现
- AI 口径（step A）：IC20 = **+0.009297**，neutral_net 全书 −6.71%，60万 −4.13%，100万 −8.93%，stock_share 0.7988。和 AI 10-14 补充包逐位一致。
- Alpha 口径（step B）：A RankIC **−0.0049**（HAC t −0.31），B 60万 +17.30%、100万 +17.18%。和 §8 v3 一致。
- 两套残差收益 ε 的逐日截面相关为 0.976。

## 2. 逐项排查（结论：不是数据错，也不是方向错）
| 维度 | Alpha | AI | 影响 |
|---|---|---|---|
| 信号方向 | 腿权重，多头为正 | 0/1 持仓，多头为正 | 无反号 |
| 信号形态 | 权重对 SW L1+风格残差化后，在**全池**做 z-score | 0/1 对 SW L1+logmv+cap 0/1 残差化 | 见第 3 节 |
| 相关 | **Spearman** | Pearson | **IC 符号的主因** |
| 标签 | 原始收益 t→t+20（含 t 收盘到 t+1 开盘的不可得段） | 中性化 ε 累计 t+2→t+21 | 次要 |
| 风格集（ε） | SW L1 + log 流通市值 + β120 + mom(120→20) + log ADV20（**冻结 §8 读法**） | SW L1 + logmv + mom20 + vol20，收益截尾 | **B 符号的唯一主因** |
| 池 | HI_LIQ 掩码 in_universe 当日 | cs_panel 的 hiliq 字段（ind≥0） | 可忽略（AI 定义搬到 Alpha 池上仍是 +0.0092） |
| B 权重 | top-N 归一到 100% 股票袖 | 账簿口径，含 20% 510300 | 只差幅度 ×1/0.8 |
| top-N | `rank(method="first")` | `leaf_topn` sort_values | 腿内 20 名**全部 0.04 等权**（每日不同权重数 = 1），两边的 top-N 都是任意子集 |

## 3. IC 符号：确切原因
- 同一个残差化信号，只把 Spearman 换成 Pearson，IC 就从 −0.0049 变成 **+0.0085**（HAC t 3.78）。只把标签换成中性化 ε（仍用 Spearman），IC 为 +0.0092（HAC 2.55）。
- 只在非持仓名之间算 Spearman：**−0.0064**。持仓名减非持仓名的原始 fwd20 差：**+1.63%**（HAC t 2.85）。
- 机制：腿每天 20 名，池约 1500 名，98% 是非持仓名。这些名字残差化后的值等于 −风格拟合值。Spearman 按秩赋权，于是 IC 被这 98% 名字的「反向风格溢价」主导，量的是风格，不是事件。Pearson 和 0/1 读法则由持仓名主导。
- AI 的 +0.0093 同样能在 Alpha 池上复现：AI 的 X + AI 的 ε + Pearson = +0.0092（HAC 3.83）。
- 结论：**事件本身对前瞻收益是正向的（约 +0.009~0.010，HAC t 2.5~3.9）**。§8 v3 的 A 为负，是稀疏信号 × 全池 RankIC 的测量缺陷。

## 4. B 符号：确切原因
| ε 风格集 | 20 名全袖（归一 100%） | 账簿口径（含 ETF） |
|---|---|---|
| 冻结 §8（Alpha） | **+8.9%**（HAC5 t 1.66） | — |
| AI | **−8.9%**（t −1.61） | −7.2% |
- 在同一风格集内部，换权重口径只改变幅度。换风格集，符号就翻。
- top-N 是任意子集：「字母序前 6/10」给出 +17.3%/+17.2%。随机挑选但持仓粘滞（20 次）：60万 +6.5% ± 8.5%（区间 −12%~+26%），100万 +9.2% ± 5.3%。每日重抽则因换手爆炸到 −50%，没有意义。§8 v3 的 B 数字被字母序放大了。
- 附带发现：capacity_adv 自己的 25 名全袖，在冻结风格下 +8.2%，在 AI 风格（去掉 mom20/vol20）下 **−48.7%/年**。说明 capacity_adv 的收益高度依赖 20 日动量和波动这两个风格。这个幅度异常大，建议 AI/Data 核一下 cs_panel `ret` 的时点和截尾（只披露，不下结论）。

## 5. 哪边「对」，WATCH 变不变
- **按冻结 §8 读法字面**，Alpha 的实现是忠实的：风格集是冻结集合，A 写的是「残差化 → RankIC」。AI 的风格集不是冻结口径，只能作稳健性披露。
- 但字面读法对稀疏事件腿有**测量缺陷**：A 的 RankIC 被非持仓名主导；B 的「top-N 按权重」在全等权时没有定义。这两点都需要勘误（第 6 节）。
- equity_incentive 维持 **WATCH，不变**。勘误后 A 为正，A′ 的特质 IC 为正；但 CMC ΔIC 只有 +0.0026，低于 +0.003（ΔICIR +0.092/+0.106 已过）。B 的符号随风格集翻转，没有稳健的特质收益。不派烟。

## 6. §8 读法勘误 / 附录（阈值不动；对后续叶生效；本轮五腿同时重报）
冻结规则 `ALPHA_HILIQ_S8_PARADIGM_RULES_20261014_ZH.md` 不改原文，sha 不变。勘误内容如下：
1. **事件 / 稀疏腿的 A 和 A′**并列两种读法：（i）0/1 持仓 vs 原始 fwd20（t→t+20）；（ii）冻结定义的残差化 z vs 中性化前瞻收益（冻结风格集 ε 累计 t+2→t+21）。CMC ΔIC 用（ii）。PASS 以（ii）为主读，（i）方向须一致；只看原始收益的全池 RankIC 仅作披露。三种 t 值都披露，不作判定键。
2. **B**：腿内等权、名单不超过 N 时，用全部持仓名归一的全袖；有真实排序时才取 top-N，并列报随机挑选的分布。
3. **B 稳健性**：并列报 AI 风格集（mom20/vol20）。两套风格集符号相反时，B 记 PASS*（不稳健），不能单独支撑升级。
4. 数值阈值（ΔIC ≥ +0.003、ΔICIR ≥ +0.05 双读、ρ ≤ 0.5、RankIC>0）**全部不变**。本勘误属于读法变更，事后提出，原因是 AI 和 Arch 发现了测量缺陷，**不是**为了让某条腿过闸：勘误后没有任何腿升级为 ACCEPT。
5. 闸门级变更仍须 Leo 原话。本勘误不改阈值，按 errata 记档并报主 Agent。

## 7. HI_LIQ capacity_adv 腿（195620）X2 口径对账（`output/alpha/recon_eqinc/capadv_hiliq_basis.json`）
| 口径 | 60万 | 100万 | 说明 |
|---|---|---|---|
| LC 引擎，**全腿** 25 名 + 20% 510300，X2 06-03 起 | 1.44% / −36.6%（不分档） | 同左 | 与 AI 的 1.26%/−36.6% 一致（AI 从 06-05 起，差在起点）。年度：2024 −6.5%、2025 +35.3%、2026 −18.2% |
| LC 引擎，`leaf_topn` 前 6/10 | 30.9% / −38.1% | 8.3% / −41.0% | 腿内多名并列 4% 上限，前 N 名有任意性（另见 Strategy tie 审计） |
| Strategy book-smoke（整手、6%、行业 25%、fill 0.55；**勘误 00:56**：BOOK 目标权重两档都是 25 名全腿，不是 6/10 名） | −0.58% / −29.9% | 1.71% / −33.0% | `output/strategy_hiliq/capadv_x2_summary.json`，**以此为准** |
| 旧 Alpha 诊断 18.17%/−24.92%、4.52%/−34.82% | — | — | 用现有产物**无法复现**（来源窗口/引擎未留档，可能是改行业前的腿或不同窗口）；**作废**，不再引用 |
- 结论：AI 的「约 1.3% / −37%」是**全腿口径**，属实。三种可复现口径的 MDD 都超过 25%。
- 对 B4/Core 参照的影响（只是提议）：Core 记分卡 B 列 13.8%/−10.1% 是 **top300 旧 capacity_adv**，不是 HI_LIQ 腿。HI_LIQ 上 GATE_V3「净 CAGR 严格高于同池 capacity_adv 单跑」这道门槛很低，单腿本身 MDD 就破门。B4@HI_LIQ（22.4%/−16.5%、14.9%/−20.2%）的收益不能归功于 capacity_adv 腿，Arch N6 也指出压舱漂移混入了收益。建议 Strategy 和主 Agent 明确：HI_LIQ 叶的 CMC 和 GATE_V3 基准，到底用 HI_LIQ B4 还是 HI_LIQ capacity_adv 单跑。

- 补记（00:56 ET）：主 Agent 00:54 已裁定 HI_LIQ 叶的 CMC/GATE_V3 基准 = 本表 book-smoke 行，并强制并列披露相对池等权的净超额（见清单 §9）。book-smoke 与 LC 全腿（1.26%）之差来自执行层面（整手、成交率、成本），不是选股不同。

## 8. 叶19 / 叶20 / 18v 状态记档（不评审）
- AI 回执 `AI_G1G5_CFACC_RNOA_WEIGHT_RECEIPT_ZH.md`（叶19，23:58）和 `AI_G1G5_SUE_RESID_WEIGHT_RECEIPT_ZH.md`（叶20，00:03）均自判 **WATCH，且不交 Alpha 验收**。叶19 在 HI_LIQ 上衰减 DOWNGRADE，不可交易，GATE_V3 不过；FULLA 的 X2 强势主要来自小微盘 β，对池等权超额 +5.3%，t 0.89。叶20 在 HI_LIQ 上衰减 DOWNGRADE，密封窗为负，对池等权超额 t<1。
- 预注册 sha 与 `prereg_sha_leaf19_20_18v.txt` 一致（0528549e… / 53cbdc9e…）。两份回执自报建 α 时峰值 RSS 超过 1.5GB 红线。
- Alpha 按主 Agent 00:17 的指示**不跑**完整评审，记 WATCH（AI 自判，未送审），不派烟。


## §6 补注（2026-10-18 00:59 ET）capacity_adv 勘误读数出处
capacity_adv HI_LIQ：(ii) 残差 z vs 中性化 fwd rank_ic=0.008994，HAC t=1.723；(i) 0/1 持仓 vs 原始 fwd rank_ic=−0.010383，HAC t=−1.711。来源：research/alpha_s8_errata_sparse_ic.py → output/alpha/recon_eqinc/step_c_s8_errata_sparse_ic.json 键 "cap"。v3 读数 0.050（HAC 3.06）来源：output/alpha/hiliq_s8/ALPHA_HILIQ_S8_run20261017.json。应 Arch 10-18 要求补出处。

**更正（2026-10-18 01:01 ET，应 Arch）**：上文「0.050 勘误成 0.009」的说法撤回。旧口径（v3 §8 A，全池残差 z vs 原始 fwd20）RankIC 0.0497、HAC t 3.06，出处 output/alpha/hiliq_s8/ALPHA_HILIQ_S8_run20261017.json 键 cap.ic（第 4、11 行），与 C.cap_ic_same_days 数值相同；新口径 (ii) 残差 z vs 中性化 fwd 为 0.0090（HAC 1.72）。两者口径不同，不能直接比较，不构成「勘误后下降」。


---
> **v4.1r（2026-10-18 01:21 ET 写入）**：01:05 ET 重启丢失原 §9，按主 Agent 01:21 指示由 _recovery/alpha 重写版以新版本号 v4.1r 写入；数字照对话记录，未重算，待 step_e 重算逐项核对与 Arch 审查。

> RECONSTRUCTED from Alpha chat record 2026-10-18; numbers as recorded, not recomputed

# ALPHA_EQUITY_SIGN_RECON §6 更正 + §9（恢复副本）

## §6 更正（2026-10-18 01:01 ET，应 Arch）
撤回「0.050 勘误成 0.009」。旧口径（v3 §8 A，全池残差 z vs 原始 fwd20）RankIC 0.0497、HAC t 3.06，出处 output/alpha/hiliq_s8/ALPHA_HILIQ_S8_run20261017.json 键 cap.ic（第 4、11 行），与 C.cap_ic_same_days 数值相同；新口径 (ii) 0.0090（HAC 1.72）。口径不同，不可比较。

## §9 v4.1 勘误（AI ε 同日 logmv bug）
- AI 风格集列作废并以前一日 logmv 重算；数字见 ALPHA_HILIQ_LEGS_v4_1_SECTION_ZH.md。equity_incentive 两套风格集同号（+8.9% / +8.7%），弱，CMC +0.0026 < 0.003，维持 WATCH；整包 NO_ACCEPT；各腿裁定不变。
- 撤回「B 符号只由风格集决定」——翻号原因是 bug。
- IC 稀疏缺陷、读法勘误、基准对账结论不受影响。

> **已核对（2026-10-18 01:46 ET，重启后重建）**：step_e 复现（旧 cs_panel，非新证据，阈值不变）逐项与本节记录数字一致；step_e_fullsleeve_b_v41.json sha256=367556b4180c6afb78a10b19817f07be2ef27e6d62cf60ddf186dc5d5b0c087e；step_c sha256=fdd911ff…（未重跑，cap (ii)/(i) 一致）；依据 Arch .ok d0816a37…。

> **披露（Arch 裁定 VALID_WITH_DISCLOSURE，10-18 01:48 ET）**：① 01:37 首跑峰值 RSS 1,573,940KB 超 1.5GB 被看门狗杀、无产物；② 01:44 重跑仅加 MALLOC_ARENA_MAX=2 / MALLOC_TRIM_THRESHOLD_=0，峰值 RSS 未记录；③ nice 19 串行；④ .ok d0816a37 已用尽，不得再用。后续：e88b88e7 须改按年分块读取并自记峰值 RSS 后方可新跑。step_e=367556b4…，step_c=fdd911ff…

> **补录（10-18 01:53 ET）**：重跑峰值 RSS 未记录。唯一记录为首跑（01:37）peak_VmHWM 1,573,940KB，见 output/alpha/recon_eqinc/step_e_v41_regen.log 第 11–12 行；未为测内存重跑。
