# Arch 复审：叶23 r2.1（去敏 SUE / ΔE/P）与叶24（IMAX 剔隔夜）预注册及构建脚本

- 审核人：QuantLab Arch（执行器）｜时间：2026-10-18 01:50 ET｜**只做静态审核**：没有运行任何叶脚本，没有读任何叶结果，没有建 .ok。
- 只读过：两份预注册、两份脚本源码、`research/g1g5_fund_resid_alpha.py`、`leaf_selfcheck_v3.py`/`leaf_selfcheck_common.py`/`alpha_combo_marginal.py` 的导入与路径、Data 重建方案 r3 与 `build_cs_panel_v2_resumefix.py` 的 manifest 写法、台账第 18/18v/23/24 行、TEAM_STATE。读数据只限于：列名/schema、capadv target_weights 的 instrument_id 格式、叶18 eval_weights 的权重取值（全为 0.04，用来判断 Jaccard 排序），均不涉及任何收益。
- 对照：前审 `ARCH_LEAF23_SUE_DESENS_PREREG_REVIEW_ZH.md`（本次追加附记 A2、A3 后 sha 023eb184…；r2/r2.1 引用的是追加前的 0d9bd147…）。

## 0. 结论

| 叶 | 预注册 | 脚本 | 总判定 |
|---|---|---|---|
| 叶23 r2.1 | **通过**（P0/P1 文字全部落实；附 Arch 澄清 C1，不需要重新冻结） | **不通过**：4 项阻断（B1 FIN 未定义会崩；B2 manifest 文件名对不上，必拒跑；B3 池 EW/wb 没有计入复牌行；B4 信号「当前记录」被提前丢行改变了定义）+ 依赖闭包未钉全 | **CONDITIONAL，本轮不发 .ok** |
| 叶24 | **通过**（标准与叶23 一致；附澄清 C1） | **不通过**：B2、B3 同叶23；另有叶18/18v Jaccard 排序失效、依赖闭包未钉全 | **CONDITIONAL，本轮不发 .ok** |

另外，两叶的 .ok 本来就要等：Data `panel_cache_v2_resumefix` 重建完成（盘上目前不存在）、Arch 审过 Data 回执、manifest sha 已知。脚本修好后，AI 报新 sha，Arch 只复审 diff。运行顺序：**叶23 先、叶24 后，串行**，都排在 cs_panel 重建之后。

## 1. 核验事实

| 项 | 实测 |
|---|---|
| 叶23 r1 | `6eca9eb8cae08231861c7094436b7b3e2a0c7606aa709409a28ab38617b4af79`，未改 |
| 叶23 r2 | `f0e39ade330944c19bed474861f477562825983c2a3af063d2b36760093e40ea`，未改（已被 r2.1 取代） |
| 叶23 r2.1 | `8f5d8ac43ba49f11b4461a287addae8c0cf247fbe9d8e81d0b339764e843922e`，FROZEN 01:43:23 ET；与 r2 的 diff 只在文首、§0.1、§6.2（20% 帽披露书）、§8（64 位全长、运行时重算）、§9（C1 唯一、敏感性不进判定、判定 t 口径）和冻结戳，其余逐字相同 |
| 叶23 脚本 | `research/g1g5_sue_desens_cs_alpha.py` = `8bfc8d4ba22b8c09a299e3e92bfb21c6d766caf39a6542fd1ecbccacd44f597c`（mtime 01:43:23）；内置 PREREG 指向 r2.1、PREREG_SHA=8f5d8ac4… 一致 |
| 叶24 预注册 | `c289e77068be607c108359a87e1d17d6b2e8edac9e4cbcca865a9a49430133a8`，FROZEN 01:44:40 ET |
| 叶24 脚本 | `research/g1g5_imax_intraday_alpha.py` = `4be361eee708e752a9f1adeeda2328946df3a7130c1a51ad962fe4ba1368651e`（mtime 01:46:29，晚于预注册冻结，属脚本，不违规）；内置 PREREG_SHA 一致 |
| sha 清单 | `output/ai_factory/prereg_sha_leaf23.txt`、`prereg_sha_leaf24.txt` 所列 sha 与实测全部一致 |
| 台账 | 第 23 行（r2 冻结，待重建+.ok）、第 24 行（冻结，待审+重建+.ok，排在叶23 之后）已登记 |
| 叶产出 | 盘上没有 `leaf23_*` / `leaf24_*` 输出目录，也没有任何叶23/24 的 .ok → 未运行，结论成立 |
| 面板 | `output/ai_factory/panel_cache_v2_resumefix/` **不存在**（Data 未重建） |
| Data 方案 | 现行为 r3 `DATA_CS_PANEL_RESUME_REBUILD_PLAN_ZH.md` = `5d0a0fb2…`；两份预注册 §3.7 引的是旧版 3a7bb0cd / 脚本 8eac523b。只是出处引用，判定以 .ok 钉的 manifest sha 为准，**不要求重新冻结** |
| 主 Agent 01:42 裁定 | TEAM_STATE 里只在 AI 小节和叶24 预注册 §0 中转述，主 Agent 小节没有 01:42 条目。转述内容（主口径不剔金融、第 3 次试验 |t|≥2.50、涨停只披露但必报、长仓、面板/基准/行业帽）与 Arch 标准不冲突，本审照此审；**原文请主 Agent 确认** |

## 2. 叶23：前审 P 项落实情况（r2.1 + 脚本 8bfc8d4b）

| 项 | 预注册 r2.1 | 脚本 | 判定 |
|---|---|---|---|
| P0-1 面板 | §3.7 全部写明：v2_resumefix、信号只读掩码列、停牌留权重记 0、复牌记真实收益、is_resume_day 只作披露和禁新买、拒 v1 与 fixesnone | 信号/选名读取有断言（`read_panel` 拒读 is_resume_day/hiliq_carry）✓；拒 panel_cache / fixesnone（按 resolve 后目录名，软链也拦得住）✓；.ok 必填 cs_panel_dir + manifest sha ✓；核对 version / fixes / 逐年 sha / build_version 列 ✓。**但 manifest 文件名对不上（B2）** | 文字 ✓；脚本 **B2** |
| P0-2 sha | §8 钉全，64 位全长，运行时重算 | 脚本、预注册、3 个工具、叶19/20 α 都重算比对 ✓；无绕过开关 ✓。**依赖闭包漏钉（N1）** | 需补 |
| P1-1 基准 | 三基准并列；wb 硬地板（出处 00:59，待 Leo）；cap = capadv-HI_LIQ 重算值 | ① filed + 重建面板重算，判定用重算 ✓（instrument_id `sh.600383` → `600383.SH` 转换已核对格式）；② wb ✓；③ 510300 ✓；floor/beat_cap/beat_ew/report_to_leo 都有 ✓ | ✓（wb 构造见 B3） |
| P1-2 试验台账 | §9：第 4 次试验、唯一判定规格、C1 唯一、|t|≥2.50 两档都要、其余仅披露 | `T_DECISIVE=2.50`；`hac_t` 调 `ic_tstat_hac(x,20)`，lag = h−1 = **19** ✓；两档都须 ≥2.50 ✓ | ✓ |
| P1-3 档位书 | gate=1 名单内重选 6/10，单名 6%，行业 25%，余额 510300；20% 帽书披露 | `pick_book` 重选、行业帽、逐日断言 ✓；20% 帽书已加 ✓ | ✓（符合附记 A3） |
| P1-4 池 EW/wb | §6.6 写「T−1 成员 × T 收益，含复牌行，停牌记 0 不剔分母」 | `Mp = M.shift(1)` 不能把停牌期成员沿用下去 → **复牌行实际被剔除（B3）** | **B3** |
| P1-5 分母 | 选 (a) MV_fix（生效日前一交易日），日更作敏感性 B；§1 写了文献关系 | `lmv_fix` = 生效日前一交易日 logmv ✓；`--denom daily` ✓ | ✓ |
| P1-6 密封窗 | §6.5a：S_F 并列、只读一次、只读 S_F、规则、叶20 已读、FWD 才是晋级测试 | `--no-forecast` ✓（独立输出目录）；`--sealed` 直接退出 ✓ | ✓ |
| P2-1…P2-8 | 都已改写 | P2-4「剔除名数与 wb 权重占比」**脚本没算**（N4）；P2-8 计数有 ✓；P2-5 叶20 重算+Jaccard top-6/10/20 ✓；P2-6 整手 ✓ | 补 N4 |
| P3-1…P3-8 | 都已改写 | P3-3 HAC+朴素并列 ✓；P3-4 30bp ✓；P3-5 X2 前不落盘 ✓；P3-6 只报名数，预注册写「记录数/名数」（N6） | 小项 |

预注册 r2.1 只有一处笔误：§8 末段仍写「本 r2 sha」，按 r2.1 理解即可，不需要改。

## 3. 叶24：按叶23 同一标准审核

| 标准 | 预注册 | 脚本 | 判定 |
|---|---|---|---|
| 面板 v2_resumefix、信号不读记账列 | §3.7 与叶23 相同；另写「复牌行不进信号」 | e_id、IMAX 窗口只用掩码内行（复牌补回行 hiliq=False，自然不进）✓；断言 ✓；拒 v1/fixesnone ✓；manifest 同 **B2** | B2 |
| 基准与 wb 硬地板 | §6.6/§7 三基准、wb 地板（00:59 出处）、cap = 重算 | 与叶23 相同 ✓；池 EW/wb 同 **B3** | B3 |
| 试验台账 | 低波动/彩票家族第 3 次（叶18、18v 之后），|t|≥2.50，严于 n=3 的 2.39 | `T_DECISIVE=2.50`、两档 ✓ | ✓。注：因子库 p1_factor_lib 里也有低波因子，家族实际次数可能大于 3；但 2.50 已等于 n=4 的门槛，结论不受影响，回执披露即可 |
| 档位书重选 + 帽 | 25% 判定、20% 披露、单名 6%、断言 | 与叶23 同一 `pick_book` ✓ | ✓（符合 A3） |
| 前一日池成员 | 公式同叶23 | 同 **B3** | B3 |
| 全长 sha 门禁 | §8 | TOOLS 加了 64 位长度检查 ✓；闭包同 **N1**；叶18/18v eval_weights 未钉（N2） | 需补 |
| 日内/隔夜 PIT | r_id = (1+ret)/(1+ret_on)−1 = close/open−1；t 日收盘算 α，T+1 开盘成交 | 只用日频 ret/ret_on，不用分钟数据；窗口 [t−19, t] 含 t 日，t 收盘已知 ✓；e_id 回归用 logmv_{t−1} ✓；掩码为 t 日盘前可知 ✓；涨停标记用 t 日 ret ✓ | ✓；`ret_on` 缺失时 `fillna(0)` 会把隔夜分量混进来（N7） |
| 涨停占比必报 | §3.4/§6.8 | 全池、各书持仓 `lu_share` ✓ | ✓ |
| 金融 | 主口径不剔，剔金融为敏感性 D | ✓；持仓金融占比 ✓ | ✓ |
| 与叶18/18v 判重 | §5：重建面板重算 ρ_excess，Jaccard top-6/10/20 | ρ ✓；**Jaccard 按叶18 权重排序取前 N，但叶18/18v 权重全是 0.04（实测 nunique=1）→ top-6/10 实际是任意截取（N3）** | N3 |
| 长仓局限 | §1 事前声明，无空头腿；分位多空只作单调性描述 | 字段名 `long_short_ann244_descriptive_only` ✓ | ✓ |

预注册小项（不需要重新冻结）：文件名叫 `IMAX_OVERNIGHT`，但因子是「剔除隔夜」，回执里写清即可。

## 4. 阻断项（脚本必须改，改后报新 sha）

**B1（仅叶23）FIN 未定义，build 必崩。** 第 251 行把 `FIN = {...}` 写进了注释，第 267 行 `~P.ind.isin(FIN)` 会抛 NameError。py_compile 查不出来。
- 修复：把第 251 行拆成两行，`FIN = {i for i, n in enumerate(IND_NAMES) if n in ("银行", "非银金融")}` 作为代码，并断言 `len(FIN) == 2`。

**B2（两叶）manifest 文件名对不上，必拒跑。** Data 的 `build_cs_panel_v2_resumefix.py` 第 176 行写的是 `<out>/manifest.json`，两份脚本 `verify_panel` 用的是 `panel.glob("manifest_*.json")`，永远找不到。其余字段已核对兼容：`version="cs_panel_v2_resumefix"`、`fixes="resume"`、`years[y]["sha256"]`、补回版逐年文件有 `build_version` 列。
- 修复：只认 `panel/"manifest.json"`，核对它的 sha 等于 .ok 的 `cs_panel_manifest_sha256`。再加两条检查：`man["step"] == "D1b_resume_execute"`、`man["mode"] == "execute"`；同目录 `RECEIPT_D1b_resume_execute.json` 存在、状态为 PASS，且回执里的 `manifest_sha256` 等于 .ok 值。

**B3（两叶）池 EW / wb 没有计入复牌行，停牌第 2 天起也被剔出分母。** 违反 r2.1 §6.6、叶24 §6.6「含复牌行，停牌（无行）记 0、不剔出分母」，而这正是判定用的 wb 地板和判定 t 的基准。
- 原因：`M` 来自面板 pivot，停牌日没有行，`fillna(False)` 后 `M[T−1]` 为假。所以复牌日 T 的收益进不了 EW/wb；停了两天以上的票，从停牌第 2 天起也退出分母。Data 方案里补回行 hiliq=False，前一日又无行，所以 `Mp` 永远为假。
- 书（`FE.book_ret` 读全部行）会计入复牌收益，基准却不计，口径仍然不对称，即前审 P1-4 没有真正修好。
- **Arch 澄清 C1（不需要重新冻结）**：两份预注册公式里的 M_{i,T−1}，解释为「截至 T−1 的最新成员状态」。股票停牌无行的日子，沿用停牌前最后一个有行日的成员状态和流通市值；退市后（该票此后再无任何行）不再沿用。这正是预注册文字「含复牌行、停牌记 0、不剔分母」的意思，也就是 Data 列口径里 hiliq_carry 的含义。
- 修复（eval 内，eval 允许读记账列）：
  ```
  Mraw = pivot(col)                              # 有行处为 True/False，无行处为 NaN
  last = PX.groupby("instrument").date.max()      # 每只票最后有行日
  after = Mraw.index.values[:, None] > last.reindex(Mraw.columns).values[None, :]   # 最后有行日之后（退市）
  Mc = Mraw.ffill().mask(after).fillna(False).astype(bool)
  MVc = MV.ffill().mask(after).where(Mc)           # 停牌期沿用停牌前流通市值
  Mp = Mc.shift(1, fill_value=False); wv = (MVc.shift(1) * Mp).fillna(0)
  ```
  然后断言：在 `row_origin=="restored" & restore_reason=="resume"` 的行上，`Mp` 与 `hiliq_carry` 一致（FULLA 对 `fulla_carry`）。不一致行数写进 summary，必须为 0，否则停跑并报 Arch。
  - 另报一个披露项：按旧写法（不沿用）算的 EW/wb，以及两者的年化差。

**B4（仅叶23）「当前记录」被提前丢行，改变了信号定义。** 第 222 行 `dropna(subset=["niq","eff"])`、第 229 行 `dropna(subset=["d1"])` 都在第 230–233 行选「当前记录」之前执行。结果是：最新季度缺 NI_q 或 NI_{q−4} 时，这条记录被丢掉，脚本退回去用更早季度的 ΔE/P（最多沿用 200 天）。r2.1 §3.4 的规定是：先取最新 end_date 作当前记录，再算 ΔE/P，算不出就记缺失。
- 修复：正式报表记录只要有 eff 就参与选「当前记录」（niq 可为 NaN）。预告记录保持现状，即 niq 算不出的不算一条可用记录，这一点写进回执。选完当前记录后再算 `d1 = niq − n4`，NaN 即无 α。
- 回执披露：按旧写法会有多少名·日退回旧季度。

## 5. 必改项（与阻断项同一个补丁改掉）

- **N1 依赖闭包未钉（两叶）。** 两份脚本都 `from research.leaf_selfcheck_v3 import ic_tstat_hac`，导入时会执行 `research/alpha_decay_gate.py` 和 `research/leaf_selfcheck_common.py` 的模块级代码。这两个文件今晚被 Eng 改过，01:33:21 才还原。
  - 修复：TOOLS 加 `dep_adg_sha256`（a877cec5…）、`dep_lc_sha256`（218b61cf…）。
  - 更稳的做法是把 `ic_tstat_hac` 的 7 行实现拷进脚本本体，不再 import leaf_selfcheck_v3；`dep_selfcheck_sha256` 仍然钉，因为后面要用这个工具跑衰减门和 GATE_V3。
- **N2 未钉的输入（两叶）。** 下列文件都会被读，但不在 TOOLS 里，也要加进去，运行时重算：
  - 叶23：叶20 eval_weights（HILIQ/FULLA）。
  - 叶24：叶18、叶18v eval_weights（HILIQ/FULLA，共 4 个）。
  - 两叶：capadv 两档的 target_weights.parquet、nav.csv；`etf_daily_adj.parquet`。
  - 叶23 另加：`forecast_2024plus.parquet`、`financials_pit_tushare.parquet`。
  - 键名见 §7。
- **N3（叶24）叶18/18v Jaccard 排序失效。** 修复：按叶18/18v 自己的 α 文件排序取前 N（与叶23 处理叶20 的做法一致），α 文件已钉。
- **N4（叶23）P2-4 披露缺失。** 修复：summary 加两项，每日因子适用性剔除名数（金融 + 600519/002371）的中位数，以及它们在 HI_LIQ wb 中的权重占比中位数。
- **N5 .ok 解析器（两叶）。** 现在是逐行 split，后出现的重复键覆盖前面的；`live` 缺省按 false 处理；`promotion`、`scope`、`allow_smoke` 都没校验；`sealed_not_opened` 查的是一个 Arch 格式里不存在的 `allow` 键。BOM 和行内注释目前会导致核对失败而拒跑，属安全失败，但要写成显式检查。修复，照 tie-sens 或 `scripts/fix_sd1/sd1_common.py` 的解析器：
  - 只认 `^[a-z0-9_]+=\S+$` 这种行；
  - 遇到 BOM、重复键、空值一律拒跑；
  - 以下键必须显式存在且取值正确：`live=false`、`promotion=false`、`allow_smoke=false`、`allow_sealed=false`、`scope=X2`、`leaf=23|24`、`cs_panel_build_version=cs_panel_v2_resumefix`；
  - `out_dir` 必须等于脚本实际输出目录（按变体）。
- **N6 输出覆盖与阶段链（两叶）。** fund/build 输出没有时间戳，`mkdir(exist_ok=True)` 会让重跑静默覆盖；eval 读 alpha/gate 时也不核对它们由哪份 .ok 和哪版脚本产出。修复：
  - fund（叶24 为 build）开跑时，若 out_dir 非空就拒跑；
  - 每阶段的 meta.json 写入 `script_sha256`、`arch_ok_sha256`、`variant` 和本阶段产出文件的 sha；
  - 下一阶段核对上一阶段 meta 与本次一致，并逐个核对产出文件 sha。
- **N7（叶24）** `ret_on` 缺失时改为 r_id = NaN，不要 `fillna(0)`。
- **N8（两叶）** `ind_names.csv` 只读面板目录内那份，不要回退到 v1 的 panel_cache（Data 已保证与 v1 同 sha，回退分支多余）。

## 6. 披露项（不阻断，写进回执）

- 两叶的 mom20/mom60/vol20 用的是面板全部行的 ret，所以重建后会包含复牌补回行的收益。这是 PIT 的（shift(1)），也更接近真实价格路径，但和 v1 面板下的叶15–22 不完全可比。
- 补回行 hiliq=False，再平衡日落在复牌日的已持仓股不在 α 名单里，会被调出。所以 `blocked` 入场闸门实际上不会触发。SD0 下这是乐观处理，回执计数。
- 外部工具：`leaf_selfcheck_v3.py` 的 `PANEL` 写死为 v1 `panel_cache`，用来定池成员和 IC 价格指数。`alpha_combo_marginal` 与 `leaf_selfcheck_common` 的书收益来自原始复权价（`g1g5_x2_panel_stitch` / `adj_price`），不是 `FE.book_ret`。
  - 所以 Gate B / GATE_V3 / 衰减 / IC 与脚本内判定读数不是同一引擎、同一面板，这与叶15–22 相同，可以横向比较。
  - 回执须写明这一点。建议 AI 另提 `leaf_selfcheck_v3 --panel-dir`（新 sha、单独审），本轮不阻断。
  - 外部工具的运行也要 Arch 授权。它们不解析 .ok，所以把工具命令行和闭包 sha 写进同一份 .ok（§7 的 `tool_*` 键），由运行者在开跑前用 `sha256sum` 人工比对并留痕。
- `other_research_jobs` 只认命令行里含 `research/` 的 python 进程，Data（`scripts/fix_sd1/`）和 Eng（`scripts_eng/`）的任务识别不到。开跑前人工 `ps` 确认，并建议把匹配范围扩到 `scripts`。
- 叶23 S_F：密封窗已被叶20 读过。叶24：叶18/18v 读过密封窗。两叶的密封窗都不是干净样本外。X2 只是入场券，晋级唯一测试为 2026-11-02 起的 FWD。
- 两叶引擎都是 SD0。SD1 合入后是否重算，由 Arch 另定。

## 7. .ok 草案（**未签发**；等 B1–B4、N1–N8 修完、新 sha 复审通过、Data 重建回执审过之后才写）

格式：`key=value`，无 BOM、无行内注释、无空格，每键一次。标「*」的键现行解析器还不读，AI 须按 N1/N2/N5 加进解析器；其余是现行脚本已经解析的键。`script_sha256` 填的是**现行** sha，脚本修改后必须替换。

### 7.1 叶23：`output/ai_factory/ARCH_RUN_AUTH_LEAF23_SUE_DESENS_CS_X2.ok`
```
format=quantlab_run_auth_v1
signed_by=arch
leaf=23 *
mechanism_tag=g1g5_ashare_sue_desens_cs_v1 *
scope=X2 *
window_start=2024-06-03 *
window_end=2026-10-09 *
allow_full=true
allow_smoke=false *
allow_sensitivity=true
allow_sealed=false *
live=false
promotion=false *
promotion_approved=false *
script_sha256=8bfc8d4ba22b8c09a299e3e92bfb21c6d766caf39a6542fd1ecbccacd44f597c
prereg_sha256=8f5d8ac43ba49f11b4461a287addae8c0cf247fbe9d8e81d0b339764e843922e
cs_panel_dir=/workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix
cs_panel_manifest_sha256=<D1b manifest.json 的 sha256，Data 回执审过后回填>
cs_panel_build_version=cs_panel_v2_resumefix *
dep_fe_sha256=2b49b10b1e79de49161190fd15aa0d705642aac94e21f5acda5d127b1ade916e
dep_selfcheck_sha256=ecaa30d8760f7ae5f53c330c128e6702476d01d8d69112b1dbf2fe769b7eaebe
dep_combo_sha256=bee230199ac27bf9730aa77c63b104a67bb104229622c57524867a9b54a5c51c
dep_adg_sha256=a877cec51dbb96c75a6d071e222caf35f62fd14f101741a03be117e0e6076a97 *
dep_lc_sha256=218b61cfbf2bf0b6bb133ef030aa2d7ff20b3eafda9724aa98c9f3b1fa5cb054 *
dep_l19_hiliq_sha256=16202b2e5b4935fc7613b0e6aeefd0573b1dd81c8174917782f118ae8166f9db
dep_l19_fulla_sha256=c761dc3618b813b23cb4c48489bdfd4d67808831a9639c82906e1c205d6bf7e6
dep_l20_hiliq_sha256=4ad2984e278fddad8bbdc2c0b26af8cdf3fc7078492e79ad2a38761bfff3d8ef
dep_l20_fulla_sha256=c572d56b7b32638118592f15bb2d8f2b8fb8509918b36dd1a2f3b1c6595ec403
dep_l20w_hiliq_sha256=a812b5506fcd9f05971088d856ae60344502586098fccbb3eccb46b594f25169 *
dep_l20w_fulla_sha256=acf9e9c39baa96c57476985eeae98386d5353706bf93510af7f5e65c83d17cdc *
dep_capadv600_tw_sha256=b010839dd1d7a0a218a00957a0cf99289bedc4511b0ed058c60e25351a7fb1a3 *
dep_capadv600_nav_sha256=c16638ca3cf2c9f14cc9317d2e49dae49c565a9f91ea8c783aea3b42588ab16f *
dep_capadv1000_tw_sha256=b010839dd1d7a0a218a00957a0cf99289bedc4511b0ed058c60e25351a7fb1a3 *
dep_capadv1000_nav_sha256=aba50300f4e7032fd335503911e3239526bb9475def39eec2b1471d91d4ac1f1 *
data_forecast_sha256=f1e59284c0a77eeca7eebb3005efce6c90d98639fb907b11dc2278ed9ad4a3e5 *
data_financials_sha256=bc0f4c3d3cd70a11d17f44496861e21268806509656247400c64be2d3ae7fab3 *
data_etf_daily_adj_sha256=48b21e84695b120b8621eff11f31f3e47879bfc05c93d3d979ddab9220ffd74c *
out_dir=/workspace/QuantLab/output/ai_factory/leaf23_sue_desens_cs *
sensitivity_specs=sig-sue,denom-daily,nofc,bo40 *
serial_order=fund>build_HILIQ>build_FULLA>eval>sensitivities>leaf24 *
rss_limit_mb=1500 *
issued_at=<签发时 ET 时间>
```
（两档 capadv 的 target_weights 实测 sha 相同，b010839d…，两份文件内容一样；Strategy 的 nav 不同。是否属实由 Strategy 在回执中说明，不影响本叶。）

### 7.2 叶24：`output/ai_factory/ARCH_RUN_AUTH_LEAF24_IMAX_INTRADAY_X2.ok`
```
format=quantlab_run_auth_v1
signed_by=arch
leaf=24 *
mechanism_tag=g1g5_ashare_imax_intraday_v1 *
scope=X2 *
window_start=2024-06-03 *
window_end=2026-10-09 *
allow_full=true
allow_smoke=false *
allow_sensitivity=true
allow_sealed=false *
live=false
promotion=false *
promotion_approved=false *
research_only=true *
script_sha256=4be361eee708e752a9f1adeeda2328946df3a7130c1a51ad962fe4ba1368651e
prereg_sha256=c289e77068be607c108359a87e1d17d6b2e8edac9e4cbcca865a9a49430133a8
cs_panel_dir=/workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix
cs_panel_manifest_sha256=<同叶23，回填>
cs_panel_build_version=cs_panel_v2_resumefix *
dep_fe_sha256=2b49b10b1e79de49161190fd15aa0d705642aac94e21f5acda5d127b1ade916e
dep_selfcheck_sha256=ecaa30d8760f7ae5f53c330c128e6702476d01d8d69112b1dbf2fe769b7eaebe
dep_combo_sha256=bee230199ac27bf9730aa77c63b104a67bb104229622c57524867a9b54a5c51c
dep_adg_sha256=a877cec51dbb96c75a6d071e222caf35f62fd14f101741a03be117e0e6076a97 *
dep_lc_sha256=218b61cfbf2bf0b6bb133ef030aa2d7ff20b3eafda9724aa98c9f3b1fa5cb054 *
dep_l18_hiliq_sha256=1a42f9e83d2e1c9accc64c01dccff334725a98d70c44692ec3cae5ec2d49e874
dep_l18_fulla_sha256=838c418779d5ecb69095c246928e5351334e183444f1b3308290850a029973c3
dep_l18v_hiliq_sha256=237e760c78abdeda8451486f554466bbc45c230dd3b1800583f7f8f5490d1939
dep_l18v_fulla_sha256=e942de2988dc8ce3864bbc417b8540f17f4f36da2d3e8741d3b20fbd743663d6
dep_l18w_hiliq_sha256=ed4dbf57953d84c0ef0470937fefded319fdd0bf97e87f3ce8ddc0faa68bea2a *
dep_l18w_fulla_sha256=d158e41007d9274096810316141cacca1d90f6d34b49c7f2c6b1551609bc263f *
dep_l18vw_hiliq_sha256=6002afab2f1214f183fca7f9064301daa272e1cc442a3d8f00bfe122a2fa6e54 *
dep_l18vw_fulla_sha256=ee68d5eb2d7ff5392eb5312294da6b0b73e4c5b8dbfc37564cc921a8b2cdfaef *
dep_capadv600_tw_sha256=b010839dd1d7a0a218a00957a0cf99289bedc4511b0ed058c60e25351a7fb1a3 *
dep_capadv600_nav_sha256=c16638ca3cf2c9f14cc9317d2e49dae49c565a9f91ea8c783aea3b42588ab16f *
dep_capadv1000_tw_sha256=b010839dd1d7a0a218a00957a0cf99289bedc4511b0ed058c60e25351a7fb1a3 *
dep_capadv1000_nav_sha256=aba50300f4e7032fd335503911e3239526bb9475def39eec2b1471d91d4ac1f1 *
data_etf_daily_adj_sha256=48b21e84695b120b8621eff11f31f3e47879bfc05c93d3d979ddab9220ffd74c *
out_dir=/workspace/QuantLab/output/ai_factory/leaf24_imax_intraday *
sensitivity_specs=src-total,k1,win60,exfin *
serial_order=after_leaf23_complete>build_HILIQ>build_FULLA>eval>sensitivities *
rss_limit_mb=1500 *
issued_at=<签发时 ET 时间>
```

### 7.3 外部评价工具运行（两份 .ok 各加一段；工具本身不解析，运行者开跑前人工 sha256sum 比对并留痕）
```
tool_selfcheck_cmd=python3 research/leaf_selfcheck_v3.py --universe HI_LIQ_V1.1
tool_combo_cmd=python3 research/alpha_combo_marginal.py --universe hiliq --base capadv
tool_closure_adj_price_sha256=93b54ae774651b3bf9c832f8c23d973893e446270eba92423767306c57d37849
tool_closure_panel_stitch_sha256=043fa68d4e6dd40f003db04fddfd79fb431c4a00f280a0a5db35cbe733d90620
tool_closure_moneyflow_sha256=ca04507616030ccc789128bd1650b573ea934014ae6ed5e69dd90088386e943c
tool_closure_nontextbook_sha256=8a56d13669b2820abc6b8757340a5774155581cdea854594ddffe058ed13c789
```
（命令行含空格，不能放进严格解析的 .ok 行。实际签发时改写为 `tool_selfcheck_args=--universe_HI_LIQ_V1.1` 之类不含空格的值，或另附一份 `.cmd` 文件并钉它的 sha。）

`g1g5_fund_resid_alpha.py` 01:25 曾短暂为 3077bf33（Eng 临时改动），现为 2b49b10b（01:33:21 还原）。签发时以届时实测 sha 为准；如果与草案不同，先查明原因再签。

## 8. 给 AI 的修复清单（按顺序）
1. 叶23 B1：FIN 改为代码行并断言。
2. 两叶 B2：manifest 改为 `manifest.json`，加 step/mode/RECEIPT 核对。
3. 两叶 B3：池 EW/wb 按 C1 沿用停牌期成员和市值；断言复牌补回行上 `Mp == hiliq_carry`（FULLA 用 fulla_carry）；旧写法差异作披露。
4. 叶23 B4：先选当前记录再算 d1；正式报表 niq 为 NaN 也参与选当前记录。
5. N1/N2：TOOLS 补钉闭包和输入，或内联 `ic_tstat_hac`。
6. N3（叶24）：Jaccard 按叶18/18v α 排序。
7. N4（叶23）：剔除名数与 wb 权重占比。
8. N5：严格解析器和必填键。
9. N6：out_dir 非空拒跑，阶段 meta 链式核对。
10. N7（叶24）、N8（两叶）。
11. 改完只做 py_compile，报两份新 sha 和 diff，更新 prereg_sha_leaf23/24.txt。预注册不需要重新冻结。

live=false；promotion_approved=false；本审未建任何 .ok，未运行任何脚本。
