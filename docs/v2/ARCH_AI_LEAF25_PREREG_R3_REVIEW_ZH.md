# Arch 审查：AI 叶25 应计预注册 r3 + 步骤 −1 包

- 审查人：QuantLab Arch。只做静态审查：读文档；对文件算 sha256；用 pyarrow.parquet.read_schema / ParquetFile.metadata 读 schema 与列统计（不读数据页）；脚本复制到 /tmp（set -euo pipefail，核对 pwd）只做 AST 检查，未执行；没有运行项目代码，没有提交。
- 时间：2026-10-18T10:39:57-04:00（ET，取自 `date`）
- 被审对象：
  - docs/v2/AI_LEAF25_ACCRUALS_PREREG_DRAFT_r3.md，sha256 0fb784f2d5a751dc006ee5624298fdbf08425f13ef223517609d5a8a39423d9f，113 行 ✔
  - research/leaf25_ttm_recon_step_m1.py，7edf577f875512e8d5eab28c9f3590ec5d2bfb85add9bdc99b925adf6524cf83，280 行 ✔（未跟踪文件）
  - docs/v2/audit/leaf25_step_m1/LEAF25_STEP_M1.cmd，6e01e1de285c179c1090feb9b736530ab2a376568533d058daa1942bdf376933 ✔
  - docs/v2/audit/leaf25_step_m1/LEAF25_STEP_M1_MEM_ESTIMATE.md，bf2c29feae23fbabb186a6be4242318a4d63fa7a7a55b4532b4b05d457d8296b ✔
- 上轮：docs/v2/ARCH_AI_LEAF25_PREREG_R2_REVIEW_ZH.md（69d88da7）。live=false，promotion=false。本审查不签任何 .ok。

## 结论
- **§2（TTM/版本）：PASS（有条件）**。r2 的 P2-A/P2-B 已关；新发现 1 个 P2（资产负债表 report_type 标签不统一，见 N-P2-1），若干 P3。没有前视型 P1。
- **r3 整体：PASS（有条件）**。P0=0，P1=0，新 P2=3（N-P2-1 report_type 标签、N-P2-2 单名上限、N-P2-3 步骤 −1 选例与日期不对题），P3=8。仍不可冻结：DIFF C r3b（913e6830）未审、共享函数未落地（r3 L4、L72 已自认）。
- **步骤 −1 .ok：未就绪**。脚本须按 N-P2-1、N-P2-3 改为新文件名新版后再审；运行条件见第六节。

## 一、r2 发现关闭情况
| 项 | r3 位置 | 判定 |
|---|---|---|
| P2-A 版本取舍/可用时点 | L52–L54；脚本 L103–L114 | ✔ 关闭：逐行 available_at、上海日期 < d、空值不用、并列取 update_flag=0 否则最早文件行、并列计数 |
| P2-B NI 字段 | L42、L64、L101 | ✔ 关闭：n_income 主口径，n_income_attr_p 为 S-NIparent |
| P2-C OCF 成员 | L33、L77、L98 | ✔ 关闭；indcap_momneut_ocf 权重包 sha 7d289d54… 实测一致 |
| P2-D 叶19 残差化 | L68、L101 | ✔ 关闭；叶19 α 文件 sha 16202b2e… / c761dc36… 实测一致 |
| P2-E as-of 口径 | L70–L72 | ✔ 关闭（冻结仍待 C r3b 落地） |
| P2-F SW 表 | L69 | ✔ 关闭 |
| P3-A 绝对过期 | L57；脚本 L126 | ✔ |
| P3-B IPO | L58 | ✔ |
| P3-C 财年 | L59 | ⚠ 部分：「同年两份年报 → NaN」在只认季末 end_date 后不可能出现，脚本也未实现（N-P3-4） |
| P3-D 单表更正例 | L50 | ✔ 文字到位；但步骤 −1 实际未必测到（N-P2-3） |
| P3-E 年报+一季报同日 | L60 | ✔ |
| P3-F ADV/成交时点 | L68、L85 | ✔ |
| P3-G 单名上限 | L86 | ✘ 数值错，见 N-P2-2 |
| P3-H 正向 t | L93 | ✔ |
| P3-I 成本可比 | L87 | ✔ |
| P3-J X2 终点 | L81 | ✔ |
| P3-K 叶21 | L73、L98 | ✔ |
| P3-L 选例规则 | L107–L108 | ⚠ 规则已冻结，但与对账目的不对题，见 N-P2-3 |

### AI 自认“未重读”的引用——逐一核实
- 本人 r2 审查行号：L27–32（t*）、L57–61（问答 a）、L74–79（P2-A）、L81–82、L84–85、L87–88、L90–91、L93–94、L97–108（P3-A~L）、L110–124（第五节清单）、L117（读法/列名）、L123（Web 前置）——全部对得上 ✔。
- 821dcfaa 由 docs/v2/ARCH_STRATEGY_SW_PIT_FRESHNESS_R4_REVIEW_ZH.md（8d5bc796b3728d07…）L4 作废 ✔。
- 叶23 r2.1 文件名 AI_G1G5_SUE_DESENS_WHO_PAYS_PREREG_R2_1_ZH.md，sha 8f5d8ac43ba49f11… ✔；L95 残差化含「叶19 cfacc_rnoa base-α」✔。
- 叶22 AI_G1G5_RD_INNOV_WHO_PAYS_PREREG_ZH.md，sha 74aa58b967fb29fc… ✔；L24 含「叶19 cfacc_rnoa 同池同日 base-α（缺失按 0）」✔。
- 叶19 预注册 L8 用 n_income ✔。

## 二、schema 核验（只读 schema 与列统计，不读数据页）
所用列全部存在，AI 所说「列名未核实」风险解除；r3 L42 那句「verified only by the step −1 schema check」可改为“Arch 已于本审查核实”。
| 文件 | 行数 / 行组 | 列与类型 |
|---|---|---|
| financials_pit_tushare（36 列） | 422129 / 1 | ts_code string；end_date、ann_date、f_ann_date timestamp[us]；available_at timestamp[us, Asia/Shanghai]；update_flag、report_type large_string；n_income、n_income_attr_p double |
| cashflow_pit_tushare（15 列） | 315718 / 1 | 同上键列（ts_code 为 large_string）；n_cashflow_act double |
| balancesheet_pit_tushare（166 列） | 451857 / 1 | 同上键列；total_assets double |
| trade_cal_sse_pit | 8035 / 1 | cal_date large_string（20050101–20261231）；is_open int64 |
列统计（元数据）：
- income、cashflow：report_type 最小=最大=「1」，0 空值 → 只有合并报表行，r3 L53「不用调整后比较数」在这两张表上自然成立。available_at 时刻为 10:00 UTC = 18:00 上海 ✔。cashflow available_at 最小 2015-01-01（与 manifest 一致）。
- **balancesheet：report_type 最小「1」、最大「合并期末」，268 个空值；update_flag 475 个空值；f_ann_date 288 个空值（available_at 0 空值，已由 ann_date 补）。** 见 N-P2-1。
- 三表都只有 1 个行组：ts_code 的 filters 无法跳过行组，第二阶段会先物化整列再过滤（不影响结论，见第四节）。

## 三、新发现
### N-P2-1 资产负债表 report_type 标签不统一 —— r3 L53；脚本 L81、L105
balancesheet 的 report_type 除「1」外还有文本标签（至少有「合并期末」），另有 268 个空值。脚本 `report_type == "1"` 会把这些行静默丢掉，TA 缺失 → NaN，且可能集中在某一来源/时期（偏差）。r3 §2.2 须写明：主口径只认「1」；其他标签与空值一律不用并逐值计数；步骤 −1 的 run_meta 须报告三表 report_type、update_flag 的逐值行数（2018 年起与全表各一份）。若「1」以外的合并类标签在 2018 年起占比 >0.5%，冻结前由 Arch 裁定是否映射为「1」，不得由脚本自行映射。update_flag 空值按“非原版”处理（现规则已如此），须计数。

### N-P2-2 单名上限 17%/10% 错误 —— r3 L86
- HI_LIQ 子集预注册 docs/v2/STRATEGY_HI_LIQ_SUBSET_PREREG_ZH.md L14：HI_LIQ 的填单可行下界按「6% × 100万 / 0.6% = 1000 万」推出，即宇宙阈值以单名 6% 为前提。100万×10% = 10 万、60万×17% = 10.2 万，都超过下界票 0.6%×1000 万 = 6 万的参与率约束，判定书在宇宙边缘不可成交。
- 叶23/24 判定书为 60万 top-6 / 100万 top-10、单名 6%、行业 ≤25%、余额 510300（Arch 0d9bd147 L96 P1-3，台账 L51；叶24 预注册 L61、L88）。Optimizer Core 惯例：60万 6%、100万 5%（optimizer_lambda_calib_sealed.py L61、v1.3 修正 L21）。
- 裁定：改为**两档单名 6%，余额 510300**（与叶23/24 同口径，保证可比）；20 名 4% 书仍仅披露。注：本人 r2 审查 P3-G 写「r1 有 17%/10%，叶23 为 6%」措辞未定向，此处明确以 6% 为准。

### N-P2-3 步骤 −1 的选例与日期测不到要测的规则 —— 脚本 L186–L193、L233–L254
- 规则 (i) 在第一阶段按“恰有一张表某期有多个可得日”选代码，但第二阶段取更正日期时另起炉灶：按 income→cashflow→balance 顺序找第一张有多版本的表、取最早一期（L234–L241），可能不是选中它的那一期，也可能是三表同时更正的那一期。
- 更正可能晚于该期很多年，所选 as-of 日的 TTM 根本不用被更正的那一期，更正规则等于没测。
- 规则 (ii) 的代码，日期取的是“最近一次年报”（L242–L246），不一定是触发条件的那一年（一季报不晚于年报的那一年）。
- 要求（新文件名新版脚本）：第一阶段把触发的 (ts_code, end_date, table, 更正可得日) 与 (ts_code, y, 同日) 原样带入第二阶段；规则 (i) 只选“被更正期属于更正可得日当天 TTM 所用的五个分量期（E、A_{y−1}、YTD_{E−1y}、TA_E、TA_{E−1y}）之一”的代码；as-of 日必须含更正生效前后各一个开市日、同日事件生效首日及其前一开市日；run_meta 对每例写 rule_exercised=true/false，任何一例为 false → 退出码非 0（停、报）。
- 同时在 run_meta 加：孤立更正数（某期只有 update_flag=1、没有原版的组数，此类无法排除前视，只能披露）、并列组数（已有）、N-P2-1 的逐值计数。

### P3
- N-P3-1 r3 §2.0 须写明：financials_pit_tushare 中 fina_indicator 来源列（eps、roe、bps、profit_dedt 等，manifest：按 (ts_code,end_date) 的最新快照拼入）一律不用，它们不是 PIT。脚本现未使用 ✔。
- N-P3-2 孤立更正（只有更正版）在数据中无法识别前视，r3 §2.2 披露并计数（见 N-P2-3）。
- N-P3-3 版本口径与叶19 不同（叶19 取每期最早版本、用 bs_cf；叶25 取 as-of 最新版本、用分表）：两者都是 PIT 合法，但须在 §0.1 或 §2 披露，重复硬闸对比时说明。
- N-P3-4 「同年两份年报 → NaN」（r3 L59、脚本文档 L14）在只认季末 end_date 后不可能触发，脚本也未实现：删去或改成可检出的规则。改财年在 end_date 上不可识别（表中无 end_type），如实披露即可。
- N-P3-5 内存估计称第二阶段 <5 MB：单行组下会先物化整列（三表约 45 万行 × ≤12 列），瞬时约数十 MB。结论不变，估计文字更正即可。
- N-P3-6 脚本 L171 的 --out 前缀检查用 startswith 未带路径分隔符（_leaf25_ttm_recon_x/ 也能过）；改为比较 parents。
- N-P3-7 .cmd 可加 `--meta <out>/run_meta.json`，让包装器把 peak_rss_kb 也纳入峰值（现已有 STAGE ru_maxrss 与 hwm_kb=，非必须）。
- N-P3-8 本人 r2 审查第五节第 2 条曾写「或 AI 另提路径」，现路径已定，新版须用新文件名（见第五节）。

## 四、步骤 −1 包静态审查
| 项 | 结果 |
|---|---|
| import | AST：__future__、argparse、datetime、hashlib、json、pathlib、resource、sys、zoneinfo、pandas、pyarrow.parquet ✔。无 research.*/quantlab.* |
| 读取 | 只读 INPUTS 中 3 个 financials_pit 文件 + 日历；第一阶段投影 5 个键列（全表扫描用于选例，必要）；第二阶段投影键列+值列并按 ts_code 过滤 ✔；无整表读入 ✔。读前用 read_schema 检查列，缺列退出 ✔ |
| sha 自检 | L176–L180 全长比对，不符 die → 退出码 3 ✔ |
| 写入 | 只有 --out 下 raw_rows.csv、ttm_script.csv、run_meta.json；--out 须为空、须在 output/ai_factory/_leaf25_ttm_recon/ 下 ✔（前缀检查见 N-P3-6） |
| 选例确定性 | 排序后取字典序最小，文件行序 row_ord 决定并列 ✔；但规则对题性见 N-P2-3 |
| <4 个 as-of 日 | L256–L257 die ✔ |
| 规则实现 | 版本选择、季末过滤、TTM 差分、一季度回退、15 个月上限、平均 TA 与 r3 §2 一致 ✔；available_at 先转 UTC 再转上海取日期，正确 ✔；日历 cal_date 为 YYYYMMDD，解析正确 ✔ |
| balancesheet vs bs_cf | 选 balancesheet 9ca05496。bs_cf（01a015bf）558358 行、14 列，行数不等于两表之和（451857+315718），是合并后的结构，单表更正的版本语义不明。按表独立取版本须用分表：理由成立 ✔。代价只是宽表，列投影后与 RSS 无关 ✔ |
| .cmd | cd /workspace/QuantLab；cmc_wrapper_v4_6174eacb.sh；--arch-ok output/ai_factory/ARCH_RUN_AUTH_LEAF25_TTM_RECON_STEP_M1.ok；--assert leaf25_ttm_recon_step_m1（命中脚本路径）；--logdir <ET_TS>_logs 在 --out 之外 ✔；env PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python ✔；输出 output/ai_factory/_leaf25_ttm_recon/<ET_TS>/ ✔。包装器 guard 默认 94322，需 T 或已退出才启动、运行中离开 T 即停组 ✔；C5 会拦下同机其他 research/scripts 进程（含 Data 补跑），与“不重叠”要求互为保险 |

### 内存裁定
- qlvenv 为 pandas 3.0.6 + pyarrow 25.0.1：to_pandas 的字符串列默认是 Arrow 支撑的 str dtype，不是逐格 Python 对象，AI 担心的“去重失效 +250 MB”基本不会发生；AI 自己的最坏情形约 650 MB，也只占 1331200 的约 49%。
- 裁定：**不需要**字典/categorical 读法，也不需要按代码预筛；第一阶段三表同驻可以保留。
- .ok 内存键：C4 判定线 1331200 kB（M = max(STAGE ru_maxrss, 采样 VmHWM, runguard STOP, JSON peak_rss_kb)，不含 vm_peak_kb）；包装器 STOPKB 1484800（默认，不改）；硬线 1536000；**预期峰值上报线 650000 kB**，超过只记 P3 复核、不作废。

## 五、AI 自报：原地覆盖脚本（6f508001 → 7edf577f）
- 事实：research/leaf25_ttm_recon_step_m1.py 未跟踪、从未提交；6f508001 在 docs/v2 与 output/ai_factory 中无任何引用，未进任何 .ok，未运行。
- 定级：**P3**（违反“改动即换文件名”规则，但无运行、无 .ok 引用、无结果依赖，审计链未断）。
- 补救：(1) 在 r4（或 r3 修订说明）§0 记一行出处：旧 sha 6f508001…、覆盖时间（ET，取自 date）、从未运行、未被任何 .ok 引用；(2) 本次 N-P2-1/N-P2-3 要求的修改必须写成新文件 research/leaf25_ttm_recon_step_m1_r2.py，7edf577f 保留不动；(3) 今后凡已向 Arch 报过 sha 的文件，一律新文件名。

## 六、步骤 −1 .ok 就绪判定：未就绪
签发前须全部满足（不签于本审查）：
1. AI 提交 research/leaf25_ttm_recon_step_m1_r2.py（新 sha），修完 N-P2-1、N-P2-3、N-P3-5、N-P3-6；对应 .cmd 与内存估计改钉新脚本 sha；Arch 静态复审通过。
2. r3 修订（或 r4）把 N-P2-1 的 report_type 规则、N-P3-1/N-P3-2 写入 §2，并改正 N-P2-2 单名上限；Arch 书面通过 §2。
3. Data 今日 10-14→10-16 补跑已结束（或 16:00 ET 已放弃），Arch 已核完补跑前后 sha；三张 financials_pit 输入与日历在签发时重算全长 sha，写入脚本 INPUTS 与 .ok（若有变化，脚本须换新文件名重钉）。
4. 94322 处于 T 或已退出，附 Data 的 ps 证据（运行前、运行后各一次）；包装器 guard 保持默认 94322。
5. 静默锁：设 RESEARCH_QUIET.lock 后等 ≥15 秒，附三项证据：pgrep -P <server.py PID> 为空；全机无 gen/snapshot/kline/export_static 进程及 deploy_loop 此类子进程；localhost:8795/healthz 显示 gen_running=false（Web v2.1 安装回执核验前有效）。
6. 单进程、不并行、不重试；不落在 10-19 16:40–18:40 ET；不与补跑重叠。
7. .ok 格式：key=value、LF、allow_read_financials_pit=true、allow_read_prices=false、allow_write 仅 --out 与其 _logs；内存键按第四节；signed_et/issued_at/expires_et 取自 date；单次使用，用后归档 _consumed/。退出码 0 不等于成功：逐个核对三份输出与每例 rule_exercised。
