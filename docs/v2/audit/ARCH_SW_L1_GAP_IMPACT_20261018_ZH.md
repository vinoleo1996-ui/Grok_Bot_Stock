# Arch 书面结论：申万一级 PIT 缺口影响（2026-10-18）

- 作者：QuantLab Arch（审计执行）；写成时间 2026-10-18T06:54:23-04:00（ET）
- 性质：只读审计。没有读价格、收益、权重、因子；没有 import 项目代码；没有写 data/、output/、git；没碰 94322（约 06:53 ps 查看状态 Rsl，在跑）。
- 证据目录：/tmp/arch_sw_gap/（脚本 s0–s4、输出 *_out.txt、SHA256SUMS.txt）。只读元数据计数在 06:49:28 到约 06:53 ET 之间，峰值 VmHWM 251MB（s1b），均 <500MB。
- live=false，promotion=false。

## 0. 结论一句话
- 坏的是 **sw_pit 候选表 0b1d3432**（data/v2/sw_pit/industry_members_sw_l1_pit.parquet）。主 Agent 说的 **89d4afa3 是另一张表**（data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet，钉住表），按同一口径在 09-24..10-16 **缺口为 0**。
- (a) 叶23、叶24 只经 cs_panel 的 ind 列间接用 89d4afa3，**不受影响**，r2.11 照常。
- (b) 10-19 纸面（capacity_adv、B4、S6）的行业帽走 89d4afa3，风险旗标走 87d769aa，**都不读 0b1d3432**；对持仓的影响量级 = 0，不需要读持仓或权重，**不需要额外 .ok**。
- (c) 受影响的是 Strategy 的 X2 研究脚本和 Intel（读 0b1d3432），349 只会落进 _UNK_ 组或被漏掉。修复按主 Agent 06:48 裁定推迟；影子对比范围见 §5。

## 1. 五张表：sha、元数据计数、谁在读
口径与 Data 相同：沪深 6 位代码，当日已上市且未退市（stock_basic D/L/P + stock_delisted_v2 9d757b96），as-of 规则 in_date<=D 且 (out_date 为空 或 out_date>D)。窗口 2026-09-24..10-16 共 11 个交易日（trade_cal_sse_pit fa4260b8）。代码格式已统一（sz.000001 → 000001.SZ；第一次跑 s1 未归一导致假阳性，已作废，以 s1b 为准）。

| 表 | sha | 行 / 代码 | 每代码 open 行 | 窗口每日缺 | 235 只是否在表 |
|---|---|---|---|---|---|
| sw_l1_pit/industry_members_sw_l1_tushare.parquet | 89d4afa3（mtime 01:08:43） | 7920 / 5914 | 5914 个代码各恰好 1 条，>1 的 0 个 | **0**（11 天全 0） | 235/235，全部有 open 行 |
| sw_l1_pit/industry_members_sw_l1.parquet | 87d769aa | 7115 / 5847 | 5838 个代码各 1 条 | **0** | 235/235 |
| sw_l1_pit/industry_members_sw_l1_prefix.parquet | 610b0956 | 12925 / 5930 | 各 1 条 | **0** | 235/235 |
| sw_pit/industry_members_sw_l1_pit.parquet | 0b1d3432（mtime 01:13:13；= sw_pit/manifest.json 7c73e70b 所记） | 7573 / 5600 | 12 个代码各 2 条 | **349**（每天都是 349，共 3839 code-day，与 Data 一致） | 0/235，**整段历史都被删** |
| sw_pit/industry_members_sw_l1_pit.bak_pre_fix_20261014.parquet | 59734014 | 7743 / 5759 | 12 个代码各 2 条 | 192 | **235/235**，每只 1 条 open 行，最早 in_date 1990-12-19 |

- Data 的说法「89d4afa3 有 5914 个代码，每个恰好一条 open」**核实属实**。
- 59734014 **确认含全部 235 只**。但它不是干净基线：本身每天也缺 192 只（68 只截断 + 46 只里的 13 只 + 其余 111 只），而且 bak 与当前表逐行比只有 6646 行相同，bak 独有 1097 行、当前表独有 927 行。也就是说 10-14 那次修复不只是删了 254 个代码，还改写了大量行。46 只「原判源缺」里有 33 只在 bak 里有 open 行，是修复时被关掉或删掉的（例：000526.SZ 801210 自 2017-06-29 的 open 行，当前表里没有）。这支持 Data 方案 c692f819 §2 把 46 只改判为我方问题。
- 0b1d3432 的 235 只**不是从 09-24 才开始缺**：它们在表里一条记录都没有。按每 20 个交易日抽样，X2 窗口（2024-06-03..2026-10-09）内这 235 只里已上市的 223–235 只每天都缺。所以凡是读 0b1d3432 的 X2 回测，整段窗口都受影响，不止最后三周。

### 1.1 消费方（按代码路径）
- **89d4afa3**：scripts/fix_sd1/sd1_common.py L29 PIN_DATA → scripts/fix_sd1/build_cs_panel_v2_resumefix.py（6e2e1273）L44/L139–143 生成 cs_panel 的 ind 列（缺成员记 −1）；research/g1g5_nontextbook_weights.py（8a56d136）L5 SW_MEMBERS → _load_sw_members / sw_code_on，被 g1g5_capacity_adv_weights.py、g1g5_earnings_event_weights.py、g1g5_insider_increase_weights.py、g1g5_equity_incentive_weights.py、CMC/combo、optimizer_core_x2_run_v1_4.py（L98 钉 sw_members_sha256）使用；research/ai_cs_panel_build.py L9（v1 面板）。
- **87d769aa**：quantlab/portfolio/research_loop.py L246（Intel 告警行业名映射）、L331（risk_flags，纸面持仓打旗，只标记不改权重）；research/intel/weekly/paper_exposure.py L4。
- **610b0956**：sw_l1_pit/manifest.json 的 prefix_table，promotion_approved=false；本次 grep 未发现纸面或叶路径读它。
- **0b1d3432**：research/strategy_hiliq_capadv_b4_x2.py（1c51531a）L72–76 load_industry_map、L316；research/strategy_fulla_b4_x2.py（7bd657ed）L255；research/intel/intel_common.py（25f23dff）L169–172、sw_members_asof L309，以及 intel_event_study.py、intel_c1_gap_split.py；scripts/nightly_update.py BUNDLE_MAP（复制进 bundle）；scripts/acquire/queue_chain_20261014.py（读 manifest）。
- **59734014**：无代码消费方，只作修复前备份。

## 2. 89d4afa3 的来历（主 Agent 要求的 provenance）
- **01:08 不是写入时间。** data/ 被 .gitignore 第 1 行整体忽略，git 无记录。01:08:00–01:10:00 之间 repo 内共有 61,742 个文件出生（data/v2/tushare_raw 31,225 个、.venv_opt 和 .venv-data-api 的库文件 510 个等），2 分钟写这么多、包括虚拟环境的库，只能是整体恢复。sw_l1_pit/ 6 个文件和 tushare_raw/index_member_all 的 62 个文件都在 01:08:19–01:08:43 出生。这一波早于 RECOVERY_MANIFEST 记录的 01:13:24–01:14:51 那一波（后者主要是 docs/output/sw_pit），恢复都没保留 mtime。
- **写入程序可以从代码上确定。** scripts/acquire/tushare_relay_pull.py（0a1d1ce7，最后提交 94a7a11，2026-10-12）L200–230：读 tushare_raw/index_member_all/*.parquet，按 (instrument_id, sw_code, in_date, out_date) 去重，写到这个路径，quality_status=research_tushare_candidate。s4 只读复核：把 62 个 raw 按同一键去重得 7920 行，和 89d4afa3 比 **7919 行完全相同**，唯一差别是一个非 A 股代码 T00018.SH 的 ID 拼法（sh.T00018 对 Tsh.00018），不涉及任何在市 A 股。
- **内容早于 10-18。** sw_l1_pit/manifest.json 的 tushare_candidate 段由 promotion_acceptance 在 **2026-10-10 14:43:21 ET** 写下：rows 7920、n_instruments 5914、current_members 5914、n_l1 31、in_date 1984-05-09..2026-09-24，和现在的文件逐项一致。
- **结论：** 内容是 tushare_relay_pull.py 由 62 个分拉 raw 生成，10-10 前后写成，10-10 14:43 验收；01:08 的 mtime 来自 10-18 整体恢复。**缺口：** 10-10 验收时没记 sha，所以只能证明计数一致和由 raw 可复现，不能证明逐字节就是 10-10 那份。建议接受（可复现性证据强），并在下次 promotion 或 manifest 更新时补记 sha。它可以作为 Data v2 方案的主来源血统。

## 3. (a) 叶23 / 叶24
- **两者都不直接读任何 SW 文件。** 叶23 HEAD（821a9107，f1344324）和叶24 r9 草稿（research/g1g5_imax_intraday_alpha.py，b83cb8e6，未提交；HEAD 里是 c5b79efa）都只从 cs_panel_v2_resumefix 读 ind 列（叶23 L495、L731–737、L843–848；叶24 L450、L641–667），并用 P.ind>=0 丢掉没有行业的行。grep 两个脚本，没有 sw_l1、sw_pit、industry_members 字样。
- **钉住链：** .ok ARCH_RUN_AUTH_LEAF23_R2_10_X2.ok（97964bb1）不直接钉 SW，但钉了 cs_panel_manifest_sha256=5c44019d；该 manifest 的 pins.sw_l1_sha256=89d4afa3，各年 cs_panel 的 sha 也被钉住。ind 的值已经固化在面板文件里，运行时不再读 SW。
- **窗口：** X2S/X2E = 2024-06-03 / 2026-10-09（脚本 L107，与 .ok window_start/window_end 一致），终点**晚于** 09-24，和缺口窗口重叠了 09-24..10-09。但面板用的是 89d4afa3，它在 09-24..10-16 缺 0，X2 全窗也不缺这 235 只（抽样每点 0），所以重叠没有影响。
- **结论：不受 0b1d3432 缺口影响，叶23 r2.11 照常跑，叶24 同理。**
- 附带发现（P3，不阻塞）：89d4afa3 在 X2 全窗口内有 225 个代码共 1612 个 code-day（约 2.8 个/天）没有成员。逐只看都是换行业当天：旧记录 out_date=D，新记录 in_date 在 D 之后，而面板构建用的是 date<out_date，于是换行业当天 ind=−1，这一行被叶23/24 丢掉。Intel 的单测把「出表当天仍是成员」作为口径，两边不一致。量级约万分之五的行，不改结论；下一版 cs_panel 和 sw v2 统一 out_date 口径。要精确算影响需读 cs_panel_2024–2026 的 date、instrument、ind、hiliq、fulla 五列，属于读真实面板文件，需要 .ok；**不建议现在做**。

## 4. (b) 10-19 纸面
- **代码路径：** quantlab/cli.py paper-daily → quantlab/portfolio/research_loop.py（d3ded87e）paper_daily L779 起：
  1. 子进程 research/capacity_adv_paper_extend.py（bfb05630）→ import research.g1g5_capacity_adv_weights（c7a05486）→ _load_sw_members（89d4afa3），用于行业中性 ADV 打分和行业帽 IND_CAP，找不到行业的记为 _UNK。
  2. research/b4_paper_extend.py --run-legs（6c927ae6）→ 冻结的 earnings_event、insider_increase 腿脚本 → 同样走 _load_sw_members（89d4afa3）。
  3. research/s6_paper_extend.py --run-legs → 加上 equity_incentive 腿，同样走 89d4afa3。
  4. risk_flags（L326–336）→ 87d769aa，只打旗，不改权重。
  5. 主干 quantlab/platform/execution.py（373fed30）和 __init__.py（bfdfa63c）不含任何 SW 引用。
- **0b1d3432 不在纸面路径上。** 读它的 strategy_hiliq_capadv_b4_x2.py 和 strategy_fulla_b4_x2.py 是 X2 研究脚本，不在 paper_daily 的子进程列表里。
- **349 只在纸面里归哪组：** 89d4afa3 和 87d769aa 在窗口内都给这 349 只分配了行业，所以在纸面里它们**照常归入真实行业**，不进 _UNK，也不被丢掉。**影响量级 = 0**，不需要读持仓或权重，**不需要签额外的 .ok**。
- **静态上界（假如误读了 0b1d3432）：** 只读成员标记列（不读 adv20_yuan），06:50:58 ET：
  - HI_LIQ 掩码 universe_mask_hiliq_v1（c5433e80，最新日 10-14）：349 只中有 229 只窗口内某天 in_universe，最后一天有 208 只（235 类 139、68 类 41、46 类 28）；当天在池 2925 只，约 7%。
  - capacity_adv 的 mid_large 池 mid_large_members_pit（4b82c749，最新日 10-16）：206 只某天在池，最后一天 196 只（235 类 119、68 类 51、46 类 26）；当天在池 2510 只，约 7.8%。
  - 因为 capacity_adv 按 ADV 选股，偏大偏活跃，这 196 只的 ADV 相关性不低。但纸面并不读 0b1d3432，这只是上界。
- **Strategy 和 Intel（真正受影响的地方）：**
  - strategy_hiliq_capadv_b4_x2.py L100/L166：找不到行业的记为 _UNK_，_UNK_ **被当成一个行业参与行业帽**。约 200 只股票挤进同一桶，会被不该有的帽子约束，原本该受帽约束的又躲过了。这类 X2 研究结果（包括 TIE_SENS 等依赖它的）在修复后需重算或披露。strategy_fulla_b4_x2.py 同理。
  - Intel sw_members_asof（intel_common L309）用 as-of 成员拿个股列表，349 只不会出现在行业成员里，Intel 行业告警会漏掉这些股票。纸面的 risk_flags 用 87d769aa 映射行业，所以行业级告警仍能打到持仓上，但 Intel 产出的个股级告警会漏掉这 349 只。只影响披露，不影响权重。
  - optimizer_core_x2_run_v1_4.py 读 89d4afa3（L93/L98 已钉），_UNK 只兜底，不受影响。
- **发现（P2）：** 纸面三个 FROZEN_CONFIG（capacity_adv 81f16190、B4 f0783861、S6 6c7fa341）都**没钉 SW 表的 sha**。SW_MEMBERS 写死在 g1g5_nontextbook_weights.py 里（其脚本 sha 被钉），但数据文件本身没有钉。建议 10-19 跑前和跑后各记一次 89d4afa3 和 87d769aa 的 sha 写进回执，以后加入 FROZEN_CONFIG。ARCH_V1_4_RUNNER_REVIEW 已把它列为未钉输入，CMC gate_deps 的 P3-4 也是同一问题。

## 5. (c) 修复排期、影子对比、纸面读哪版
- 方案文档：docs/v2/plans/DATA_SW_L1_PIT_V2_FIX_PLAN_ZH.md（c692f819，06:49:56 写成），已并入 FALSE_DONE 队列 output/relay_outage_backfill_queue.json（c22322a3）的 nightly_step|sw|20261014/15/16。用 01:08 已落地的 62 个分拉 raw 离线重建，不需要 relay；三项 sw 以 superseded_by v2 关闭。**同意这个合并方式**，队列只能在回执审完后改。
- **审查排期（按主 Agent 06:48 裁定：不提前解冻，实施放在叶23、叶24、10-19 纸面之后，和日历包同批）：**
  1. 现在到叶23 r2.11 开跑前：Arch 只做方案静态审（不占资源），10-18 内给出书面意见，回答方案 §11 六个问题。初步意见：第 1 条同意改判，记 P1，和 235 只并为一条；第 2 条要逐只追溯 95 只（本次另发现当前表比 bak 多 117 个当日 active 代码，需一并解释）；第 3 条用 01:08 的 raw 离线重建；第 4 条可以，provenance 见 §2；第 5 条接受内容证据；第 6 条可以。
  2. 叶23 r2.11、4 个敏感性变体、叶24 补测和正式跑期间：不跑任何 SW 修复的东西，selftest 也不跑。
  3. 10-19 17:40 纸面跑完、回执审完后：签 code-change .ok → selftest .ok → dry-run .ok（输出到 /tmp）→ Arch 审 dry-run（重点：normdiff 对 89d4afa3 应为空、每日缺成分应为 0、12 只双开的处理、out_date 口径）→ execute .ok（只写 sw_l1_pit_v2.parquet 和 manifest）。各步都避开 10-19 16:40–18:40 ET，也不和任何叶步骤并发。
  4. 和 2027 日历包同批审，目标在日历包截止日 12-15 之前，越早越好；下游切换和 .ok 重签放在回执审完之后。
- **影子对比（主 Agent 新要求）的范围建议：**
  - 时间：v2 执行并审完之后；不在 10-19 16:40–18:40 ET；不和叶23、叶24 任一步骤并发；运行前确认前一进程已停（主 Agent ③）。单独的影子 .ok，单次使用。
  - 输入（全部钉 sha）：sw_l1_pit_v2.parquet（新）、89d4afa3（对照）、0b1d3432（对照）；10-19 纸面已产出的 60万/100万 持仓与目标权重（capacity_adv、B4、S6，按回执路径和 sha）；三个 FROZEN_CONFIG；冻结的腿脚本。**不改任何脚本文件**：在独立进程里把 g1g5_nontextbook_weights.SW_MEMBERS 指到 v2（影子包装脚本也要先审），或者只做「给定持仓 → 行业映射 → 检查帽子」的离线复算。
  - 输出：只写 output/shadow/sw_l1_pit_v2_vs_frozen_<date>/（新目录，开跑前必须为空）。内容：60万、100万各自的持仓差异（名单增减、权重差的 L1 范数）、行业帽违规列表（IND_CAP，B4 的 25%/28% 按各自配置）、按行业的权重变化、_UNK 组权重、risk_flags 差异；再加 Strategy X2 研究脚本在 0b1d3432 对 v2 下 _UNK_ 组的权重和行业帽违规次数（只复算，不改结果文件）。
  - 资源：单进程 RSS ≤ 1536000 kB，预期 <600MB；nice 10；PYTHONDONTWRITEBYTECODE=1，py_compile 输出到 /tmp。
  - 预期：纸面持仓差异应为 0 或极小，因为纸面本来就用 89d4afa3，而 v2 的目标就是和它的 open 行一致。真正的差异在 Strategy 研究那一侧。
- **纸面要不要改读新版本：建议不改（与主 Agent 06:48 裁定一致）。** 理由：
  1. 纸面本来就不读坏表，改了没有收益。
  2. 改读意味着修改 g1g5_nontextbook_weights.py 里写死的 SW_MEMBERS，这个脚本 sha 被 B4/S6 的内容门禁钉着，等于在冻结期改代码，不只是换数据。
  3. v2 在 10-19 前不会生成（实施推迟），没有可读的版本。
  4. 披露：10-19 纸面回执写明「行业帽数据 = sw_l1_pit/industry_members_sw_l1_tushare.parquet 89d4afa3（09-24..10-16 在市代码无缺口）；风险旗标 = industry_members_sw_l1.parquet 87d769aa；未读 sw_pit 0b1d3432」，跑前跑后各记一次 sha。

## 6. 需要 .ok 的读取
- (b) 的量级为 0，**不需要读持仓或权重**，本次不申请 .ok。
- 可选（不建议现在做）：§3 那个 P3 的精确量级，需要读 cs_panel_v2_resumefix 2024–2026 的 date、instrument、ind、hiliq、fulla 五列，预计 <500MB，不碰收益列。

## 7. 事件和更正
- 主 Agent 裁定里「修复不覆盖 89d4afa3」把两张表混为一谈：坏的是 0b1d3432；89d4afa3 也不该覆盖（Data 方案 §0 两张都保护），结论不变，但请在记录里把 89d4afa3 改为 0b1d3432。
- 叶23 工作区文件现在的 sha 是 4aa19627（AI 正在改 r2.11，未提交，备份在 _recovery/ai/pre_r2_11_0643/）；HEAD 仍是 f1344324。本结论基于 HEAD。
- 本次第一次计数（s1）没把 sz.xxxxxx 格式归一，得出了「89d4afa3 每天缺 5222」的假结果，已作废，改用 s1b，两份输出都留在证据目录。
