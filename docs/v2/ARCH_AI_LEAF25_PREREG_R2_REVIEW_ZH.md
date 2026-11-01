# Arch 审查：AI 叶25 应计预注册 r2（g1g5_ashare_cfacc_desens_cs_v1）

- 审查人：QuantLab Arch。只做静态审查：读文档与 JSON manifest，对文件算 sha256，用标准库/scipy 算正态分位；没有读任何 parquet 内容，没有运行项目代码，没有提交。
- 时间：2026-10-18T10:29:20-04:00（ET，取自 `date`）
- 被审对象：docs/v2/AI_LEAF25_ACCRUALS_PREREG_DRAFT_r2.md，sha256 6dcc919da69dd05a3cbc77dda8d1ec32b8cbc8f2679a51f89e50ea6e9501bd94，92 行，与申报一致。r1 docs/v2/AI_LEAF25_ACCRUALS_PREREG_DRAFT.md 993c4ce5a80b0c48e79335d6b15182bc8fb662b3f28f26ab1a805fff62e3cfe4 未动。
- 依据：增量审计 docs/v2/audit/AUDIT_20261018_1018_ET_ZH.md（88db7a5a957f…）。
- live=false，promotion=false。本审查不签任何 .ok。

## 结论：PASS（有条件）——不可冻结，须出 r3

P0=0，P1=0，P2=6，P3=12。审计 P2-1/P2-2/P2-3 与 P3-1~P3-5 的主体都已落实；但 r2 新引入或暴露了 6 个 P2（版本取舍的前视口子、NI 字段口径、OCF 臂认错、与叶19 公式重合、as-of 口径引错版本、SW 表选错）。r3 须逐条修完再送审；步骤 −1 的只读 .ok 须在 r3 修完 P2-A/P2-B 之后才可申请（对账脚本要实现的正是这两条规则）。

## 一、核实项

| 项 | 结果 |
|---|---|
| r2 sha | 6dcc919d…01bd94 ✔ |
| SW prefix 表 | data/v2/sw_l1_pit/industry_members_sw_l1_prefix.parquet = 610b0956ec9a01cda1ea63951751bb993290fa0370079140ed1e6cc882bb6af1 ✔（r2 L49 全长一致） |
| SW tushare 表 | industry_members_sw_l1_tushare.parquet = 89d4afa337435a2302b5c13fd4cf049b71eda2f20e1d9094f15d62cdb587f66c（冻结件，只读） |
| SSE 日历 | data/v2/calendar/trade_cal_sse_pit.parquet = fa4260b808755b9a1c91e3ade210edec84bbdb91e0dfff4c6a955c4d35fd8a41 |
| 包装器 v4 | docs/v2/audit/cmc_v1_1_leaf24/cmc_wrapper_v4_6174eacb.sh = 6174eacb4ff2d0905634477430b96bf155d3606794cd66f23a5a38a4f85e4169 ✔ |
| CMC v1.2 | research/alpha_combo_marginal_v1_2.py = bba212afadefce68dcd1bf76919f91de39402658e4398e925e3d80c6f01592c4（存在） |
| leaf_selfcheck_v3.py | ecaa30d8760f7ae5f53c330c128e6702476d01d8d69112b1dbf2fe769b7eaebe（r3 须全长钉入） |
| financials_pit 输入（当前） | financials_pit_tushare.parquet bc0f4c3d3cd70a11d17f44496861e21268806509656247400c64be2d3ae7fab3；cashflow_pit_tushare.parquet 71d5c3d39fbf2de05064ce7f21334e15c9b1d977c64494ffe699f7eeb0b95d79；balancesheet_pit_tushare.parquet 9ca054962e850cad7305262e978758c9e9f36613c4cca025efdd99276de8dbb5；bs_cf_pit_tushare.parquet 01a015bfdec842a9e367b323aba57617f8c192c209cc5ce4d792d713cdd5650d（今日 Data 补跑后须重算） |
| 冻结闭包 | docs/v2/eng_sd1/paper_import_closure.json 不含 financials_pit；含 trade_calendar.py。叶25 不写任何冻结件 |

### t* 数值核验（statistics.NormalDist 与 scipy.stats.norm.isf 两路一致）
双侧 5%、Bonferroni（即 Holm 第一步，叶25 在前序成员均未显著时取最严一步，口径正确）：t* = Φ⁻¹(1 − 0.05/(2n))。
- n=3：2.3940 → r1 的 2.39 正确。
- n=4：2.4977 → r2 的 2.50 正确（四舍五入到两位）。
- n=5：2.5758；n=6：2.6383（备用，见 P3-K）。
- 用 t 分布（df≈300~600）复核 n=4：2.505~2.513，HAC t 按渐近正态取 2.50 可接受。

## 二、审计项逐条落实情况

| 审计项 | r2 位置 | 判定 |
|---|---|---|
| P2-1 TTM 差分公式 | L31 | ✔ 公式正确；年报期 TTM=Annual_y 正确 |
| P2-1 三分量同一 as-of | L32 | ✔ 原则正确；但同一 available_at 多版本时未定取舍，见 P2-A |
| P2-1 f_ann_date 可用时点 | L34 | ⚠ 「first announcement date」措辞会被读成“该期首次公告日套用到更正版”，见 P2-A |
| P2-1 更正版只从自身 available_at | L34 | ✔ |
| P2-1 缺季/年报晚于一季报 | L36–L37 | ✔ 规则可用；缺绝对过期上限，见 P3-A |
| P2-1 3 只股票手算对账 | L84 | ✔ 已列为步骤 −1、单独 .ok、未跑；选股方式须改为确定性规则，见 P3-L 与第五节 |
| P2-2 叶19 同族、n=4、t*=2.50 | L11、L20、L78 | ✔ 数值正确；但 OCF 臂认错，见 P2-C |
| P2-2 重复硬闸对叶19 | L57 | ✔ 已加；漏了 indcap_momneut_ocf，见 P2-C |
| P2-3 SW 表钉 sha | L49 | ✔ sha 正确；但表选错，见 P2-F |
| P2-3 金融剔除用同一表 | L44 | ✔ |
| P2-3 as-of 交易日取法 | L50 | ⚠ 引到被取代的版本，见 P2-E |
| P3-1 CMC v1.2 / 包装器 v4 | L69、L85 | ✔ |
| P3-2 地产 | L44、L81 | ✔ 主口径保留 + S-exRE 仅披露，接受 |
| P3-3 244 天 | L66 | ✔ 与叶23/24 一致 |
| P3-4 成本 30bp 判定、17.5bp 披露 | L65 | ✔ 接受；可比性披露见 P3-I |
| P3-5 §12 慢因子进 Optimizer Core | L91 | ✔ |

## 三、问答（a）（b）

### （a）as-of 口径与「r3b 作废」
- 来源核对：c72f0856 = docs/v2/ARCH_STRATEGY_SW_PIT_ASOF_FIX_R2_REVIEW_ZH.md，L74 原文为「主规则：in_date < d 且（out_date 为空或 out_date >= d），d 先 normalize」✔；但紧接着 L75 写的空档沿用是「out_date == d − 1 自然日」，属于 05:45 裁定，已被 06:01 取代。28eabd35 = docs/v2/ARCH_STRATEGY_SW_PIT_ASOF_TRADEDAY_C_REVIEW_ZH.md，L7 原文为 06:01 裁定「严格 in_date<d；只有旧 out_date 等于 d 之前最近的 SSE 交易日时才沿用旧行业，且只沿用 1 个交易日；日历作为参数传入；d 超出日历覆盖就报错」✔。两处引文字面都对。
- 「r3b 已作废」不成立，是两个 r3b 混淆：821dcfaa 是 Strategy sw_pit **freshness** 自查的 r3b，确由 docs/v2/ARCH_STRATEGY_SW_PIT_FRESHNESS_R4_REVIEW_ZH.md（8d5bc796）L4 作废；审计 L18 说的「Strategy r3b as-of 修复」是 **DIFF C 的 r3b**：docs/v2/audit/STRATEGY_SW_PIT_ASOF_TRADEDAY_PROPOSAL_20261018_r3b.diff（913e683082cfd63707f314cc4bd5f5166854cc787d685c1560a3e29cd891f5ae，07:22），未作废，仍待 Arch 审（待办「C r3b」），也未落地（research/sw_members_asof.py 不存在）。
- C r3b 的现行口径（diff L108–L124）比 r2 L50 的字面规则宽一档：d 必须是 SSE 开市日；当 d 无有效行时，旧行须 in_date 可解析且 in_date ≤ out_date，并且 prev_open(d) ≤ out_date < d（prev_open = 传入日历中 d 之前最近的开市日），才沿用 1 天；不要求有后继行；out_date 落在非开市日的也沿用（披露 n_rows_gap_carry_out_on_closed_day）；日历必须作为 TradeCal 传入、钉 TRADE_CAL_SHA_PIN fa4260b8…；d 为 NaT、超出日历、非开市日或之前无开市日 → SwPitIntegrityError，绝不退回自然日。
- 裁定：主规则（in_date<d、out_date 空或 ≥d、日历参数化、超界报错）对；空档沿用条件须改为 C r3b 的 prev_open(d) ≤ out_date < d 窗口版，并加 in_date ≤ out_date 与“d 为开市日”两条。实现上不得私写，须调用 C r3b 落地后的共享函数 sw_l1_asof_with_gap_carry（钉其落地 sha）；C r3b 未审完、未落地前，叶25 不得冻结。

### （b）家族成员与 n
逐一检索 docs/v2/AI_LEAF_LEDGER_ZH.md 与 docs/v2 下 accrual/OCF/cfacc 相关文档：
1. 叶19 cfacc_rnoa（g1g5_ashare_cfacc_rnoa_v1，台账 L46，WATCH）——同族。
2. accrual_quality（2026-10-13，资产负债表 Sloan WC 应计，WATCH/DONE_FAIL）——同族。
3. indcap_momneut_ocf（g1g5_ashare_indcap_momneut_ocf_v1，叶 A，主信号 ocf_to_profit = 经营现金流/净利润，即盈利的现金兑现，WATCH）——同族，r2 所说「OCF arm」应当就是它。
4. 叶25 本身。
- 不计入：northbound_flow、d1_val_resid（r2 L20 把它们与 OCF 并列，机制无关，须删）；STOCK-OCF-QUALITY V32（ocf_to_profit 提案，仅待批、无产物，未消耗试验）；叶21 biz_climate（合同负债+存货周转，属营运资本分量但机制为订单/库存景气，算邻族，只要求 ρ 披露）；叶22 rd_innov（不同族）。
- 结论：n=4、t*=2.50 正确，前提是把第 3 项按 mechanism_tag 写明。若主 Agent 认定 biz_climate 也算同族，则 n=5、t*=2.58。

## 四、发现

### P2-A 版本取舍与可用时点（前视风险）—— L29、L32、L34
- 数据实况（manifest，未读 parquet）：financials_pit_tushare、cashflow_pit_tushare、balancesheet_pit_tushare 均「保留全部 update_flag/report_type 版本」，available_at = coalesce(f_ann_date, ann_date) 18:00 Asia/Shanghai；多版本占比约 37.5%，最多 4~8 版。
- 问题 1：Tushare 更正版常与原版共享同一 f_ann_date/ann_date。L32「取 available_at < d 的最新记录」在并列时会选中更正值，等于把更正提前到原公告日——正是 L32 自己禁止的回填。r3 须写明：同一 (ts_code, end_date, report_type) 有多条 available_at 相同的版本时，取 update_flag=0（原版）；无原版则取文件中最早一条；并披露并列组数。
- 问题 2：L34「available_at = f_ann_date（first announcement date）」须改为「每一行（版本）自己的 available_at 列，即 coalesce(f_ann_date, ann_date) 18:00 上海；available_at 为空的行永不使用，不得用 end_date+滞后推算」。
- 问题 3：report_type 未钉。须写明主口径只用 report_type=1（合并报表，与 accrual_quality 一致）；后续报告附带的调整后比较数（调整合并报表）是否用于 A_{y−1}、YTD_{y−1}，二选一写死并披露。
- 问题 4：L29 利润表来源只写「PIT income」，无路径。须钉 data/v2/financials_pit/financials_pit_tushare.parquet（或另指文件）的全长 sha，并列出所用列名（列名由 AI 从 manifest/文档给出，不读数据）。

### P2-B NI 字段与 CFO 口径不一致 —— L29、L42
n_income_attr_p 是归母净利润，n_cashflow_act 是合并口径经营现金流；两者相减会把少数股东损益当成应计，少数股权大的公司系统性偏高。叶19 预注册（AI_G1G5_CFACC_RNOA_WHO_PAYS_PREREG_ZH.md L8）用的是 n_income（合并净利润）。r3 主口径改用 n_income；n_income_attr_p 只作敏感性披露，或写明理由。

### P2-C OCF 臂认错，重复硬闸漏同族成员 —— L20、L51、L57、L78
L20「OCF-related arm (northbound/OCF/d1_val)」不是一个成员的名字。同族的是 indcap_momneut_ocf（ocf_to_profit = CFO/NI，与 NI−CFO 应计几乎是同一信息的反向表达）。r3 须：§0.1 与 §9 写明 mechanism_tag g1g5_ashare_indcap_momneut_ocf_v1 及其权重包路径；L57 的 ρ_excess>0.5 或 top-10 Jaccard≥0.5 判 FAIL 硬闸同时对它生效；删掉 northbound、d1_val。

### P2-D 主口径与叶19 的 CFACC 分量公式相同 —— L22、L42、L48
叶19 预注册 L10：CFACC = (NI_ttm − OCF_ttm)/平均总资产（本期、去年同期），与 r2 L42 逐字相同；r2 与叶19 的差别只剩去敏、残差化、版本取舍和去掉 RNOA。叶22、叶23 的先例是把叶19 α 放进残差化回归。r3 须在 L48 回归项中加入叶19 cfacc_rnoa base-α（同池同日，缺失按 0），并把「不残差叶19」列为敏感性披露；否则须由主 Agent 裁定接受“纯重复硬闸”路线。

### P2-E as-of 口径引用被取代版本 —— L12、L50
见第三节（a）。r3 须：删除「r3/r3b (cd90f2f3 / 821dcfaa) voided」那句或改为准确表述（821dcfaa 是 freshness r3b）；空档沿用改为 C r3b（913e6830）口径；依赖 C r3b 审完、落地后的共享函数及其 sha；日历钉 fa4260b8。

### P2-F SW 表选择 —— L49
data/v2/sw_l1_pit/manifest.json 的 research_preferred 是 industry_members_sw_l1_tushare.parquet（10-10 14:43 复核），晚于 NOT_PROMOTION_GRADE.md（10-10 11:36）把 prefix 表列为研究默认的说法；prefix 表 12925 行中 1468 行未映射到 801xxx（7 个 L1 前缀），会落进 PREFIX_* 桶，金融/地产判定在这些行上没有定义。Strategy as-of 修复与 C r3b 的空档统计、CLEAN manifest 校验都是针对 tushare 表做的。r3 主口径改钉 tushare 表 89d4afa3…（只读，冻结件可读不可写）；prefix 表 610b0956 只作敏感性。sw_l1_pit_v2 落地后再改钉（预注册修正）。注：Arch 审计 L18 建议 prefix 表，此处由 Arch 自行更正。

### P3
- P3-A L37：只有相对过期上限（比最新一期晚一季）。须加绝对上限：TTM 的期末日早于 d 前 15 个月（或超过法定披露期限仍无新报告）→ NaN，并计数。
- P3-B IPO 不足 4 期：r1 L19 要求「≥4 季」，r2 删了。须写明：上市前期间只有当该行 available_at < d 时才可用；A_{y−1} 或 YTD_{y−1} 或 TA_{t−4q} 缺失 → NaN，按年报告 IPO 引起的 NaN 数。
- P3-C 改财年：A 股基本为日历年；须写明 end_date 只能是 03-31/06-30/09-30/12-31，否则 NaN 并计数；同一年出现两期年报 → NaN。
- P3-D 只改一个分量的更正：规则按“表 × 期 × 版本”独立取，已覆盖；须在 §2.1 明文写一例（上年三季报 CFO 更正 → 只从该更正的 available_at 起影响当期 TTM），并在步骤 −1 中覆盖。
- P3-E 年报与一季报同日披露：常见情形，TTM_Q1 需要当日的 A_y，二者同日可得，按 L36 不触发回退；须写明并计数。一季报早于年报在 A 股属违规罕见情形，按回退规则处理即可。
- P3-F L48：logADV20 未写窗口截止 t−1；r2 也没写信号日与成交日（叶23/24 为 T+1 开盘成交）。须补。
- P3-G L64：单名上限未写（r1 有 17%/10%，叶23 为 6%）。须写死。
- P3-H L72：「same sign」改为「两档都 ≥ +2.50（正向）」。
- P3-I L65：判定用 30bp，与叶19/23/24 的 17.5bp 不可直接比；与前序叶比较的表格须同时列 17.5bp；Gate B 与 wb 硬地板用哪档成本须写明（建议都用 30bp）。
- P3-J L61：X2 终点「.ok 签发时的最新面板日」须改为冻结时写死具体日期；今天有 Data 10-14→10-16 补跑，面板终点可能变化。
- P3-K 叶21 biz_climate 列入 L51 的 ρ 披露清单（已在“叶15–24”内，点名即可）；若主 Agent 判其同族，t* 改 2.58。
- P3-L L84「3 Arch-chosen codes」：选股本身要读数据，须改成冻结在脚本里的确定性选取规则（见第五节），Arch 审规则、不预看数据。另：cashflow 表 manifest 显示 ann_min=2015-01-01，密封窗 2018 起的 TTM 预热够用，但须在 §2 披露。

## 五、步骤 −1（3 只股票 TTM 手算对账）只读 .ok 的前置清单
Arch 只有在以下全部齐备、逐项核对后才签；本审查不签。
1. 时序：r3 已修完 P2-A、P2-B（及 P2-F 若涉及金融判定），且 Arch 对 r3 的 §2 给出书面通过。
2. 脚本：路径固定为 research/leaf25_ttm_recon_step_m1.py（或 AI 另提、Arch 认可的路径），给出全长 sha256；Arch 静态审过源码。脚本只 import 标准库、pandas、pyarrow；不 import research.* 或 quantlab.* 中会读行情的模块。
3. 精确命令（一行，含解释器）：cd /workspace/QuantLab && PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf25_ttm_recon_step_m1.py --out output/ai_factory/_leaf25_ttm_recon/<ET 时间戳>/ ，外套 cmc_wrapper_v4（6174eacb…，STOPKB 1484800，C4 1331200），同时提交 .cmd 文本。
4. 三只股票与日期：由脚本里冻结的确定性规则选出，并在 .ok 前把规则写入 r3 §11：(i) 一例“同一 (ts_code, end_date) 有更正版且只改了三张表中的一张”；(ii) 一例“年报与一季报同日或一季报不晚于年报”；(iii) 一例“上市不足 4 期或少数股东损益占比大”。每类取满足条件的 ts_code 字典序最小者（限 HI_LIQ_V1.1 名单内时，名单文件须钉 sha，且只读代码列表）。每只至少 4 个 as-of 日：更正前一交易日、更正生效首日、年报生效首日、任意一个普通季报生效首日；日期由规则从 available_at 推出并打印。若 AI 能不读数据就预先点名 3 只代码与日期，也可直接列出，Arch 认可后写死。
5. 输入文件与 sha：只读 data/v2/financials_pit/ 下 financials_pit_tushare.parquet、cashflow_pit_tushare.parquet、balancesheet_pit_tushare.parquet（或改用 bs_cf_pit_tushare.parquet，二选一），全长 sha 在签发前重算钉入，脚本启动时重算、不符即退出（rc≠0）。如需 SSE 日历，钉 trade_cal_sse_pit.parquet fa4260b8…。**只读 financials_pit 与日历，不读任何价格、收益、权重、因子、面板文件。**
6. 读法：pyarrow 按列读（只取 ts_code、end_date、ann_date、f_ann_date、available_at、update_flag、report_type 及 n_income/n_income_attr_p、n_cashflow_act、total_assets），用 filters 下推到 3 只代码；不得整表读入。
7. 输出：只写 --out 目录（scratch，不在冻结闭包内）：raw_rows.csv（每只代码所有入选版本的原始 YTD 行）、ttm_script.csv（每个 as-of 日脚本算出的三分量、TTM、分母、CFACC 及所选版本键）、run_meta.json（输入 sha、规则、并列版本数、rc）。不写其他路径。AI 与 Arch 用 raw_rows.csv 逐行手算对账，任何不符 → 停、报。
8. 内存估计：书面给出（按列读 + 过滤后预计峰值 < 600000 kB），Arch 认可；硬线 1536000，目标 1331200，包装器停止线 1484800。
9. 单进程：同一时刻只有这一个真实数据进程；不并行、不重试。
10. 94322：运行全程处于 T 状态或已退出，附 Data 的 ps 证据（运行前、运行后各一次）。
11. 时间窗：不得落在 10-19 16:40–18:40 ET；不得与 Data 今日 10-14→10-16 补跑重叠——须在补跑结束（或 16:00 ET 放弃）且 Arch 核完补跑前后 sha 之后再跑；若补跑改动了上列 financials_pit 文件，按新 sha 重新钉。
12. Web 前置（Web v2.1 安装回执未核验前仍有效）：设 RESEARCH_QUIET.lock 后等 ≥15 秒，再核三项：pgrep -P <server.py PID> 为空；全机无 gen/snapshot/kline/export_static 进程，也无 deploy_loop 的这类子进程；localhost:8795/healthz 显示 gen_running=false。
13. .ok 本身：key=value、LF、显式 allow_*（allow_read_financials_pit=true，allow_read_prices=false，allow_write 仅 --out 目录），signed_et/issued_at/expires_et 取自 date，单次使用，用后归档 _consumed/。rc=0 不等于成功：按输出文件逐项核对。

## 六、对 r3 的要求汇总
修完 P2-A~P2-F；逐条处理 P3-A~P3-L（可写“不采纳+理由”）；§0 变更表补本审查的条目；送审时给出 r3 全长 sha。r1、r2 保留不改。
