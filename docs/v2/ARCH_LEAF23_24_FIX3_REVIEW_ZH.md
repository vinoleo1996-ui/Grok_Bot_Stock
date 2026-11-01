# Arch 复审：叶23 r2.4 / 叶24 r3（AI 第三轮修复，对 bd3abe5c + Alpha 77441f16 + 主 Agent ~02:33 vol20 裁定）
- 时间：2026-10-18 02:45 ET，QuantLab Arch。**静态审**：只读文件、sha256sum、AST 扫描字符串常量；数据只按代码或按年过滤读取（leg 只读 000001.SZ，ETF 只读 510300 日期，delisted_master 只读 3 列，v1 panel_cache 2024 只读 date 列），本审峰值 RSS ≤448MB。没有运行、import 或 py_compile 叶脚本，没有建 .ok。live=false；promotion=false。
- 上轮教训：漏了 f-string 和滞后链。本轮对每个回归项从源文件追到回归行，写明信息日期，并 AST 扫描全部字符串常量。

## 0. 结论：**CONDITIONAL（.ok 不签）**——P0=0 / P1=0 / P2=1 / P3=3
- bd3abe5c 的 P1-A、P2-A、P3-A～F，以及 Alpha 77441f16 的 ①～④ 全部正确落实。
- 唯一须改的是 P2-1：P2-B 停跑条件按字面写成「沿用到窗口末且名字在 delisted_master 里」。这需要改成 Arch 裁定的口径（见 §3）。改动很小，但会产生新 sha。
- 签发前提仍是 Data D1b execute 回执审过。r6b 还在审，panel_cache_v2_resumefix 尚不存在。

## 1. 核验
| 对象 | 实测 |
|---|---|
| 叶23 r2.4 | ccde59eb299fe3ae339d8c75ba0b4d761d5aa5c0e320e2a711dc228c86608ae6 ✓ |
| 叶24 r3 | 101600f67b9447f5a13291a10b4e6eefbd2567c950d005e6647ab09d84424f12 ✓ |
| diff | e77262de08202e52ab7f095afba066e71733c76692865866ccbd618c50bafdd3；在临时目录对 `_recovery/ai/pre_arch_fix3_0233/`（f011b277 / 6f57c82d）应用后**逐位复现** ✓ |
| Alpha 复审 | 77441f16 ✓ |
| delisted_master | 63590f23… ✓；339 行，ts_code 无重复；last_trade_date 为 NaT 的只有 T600018.SH（delist 2006-10-20）。代码虽然通用写了 fillna(delist_date)，实际只作用于这一名，且该代码格式不会出现在面板里 → 无影响 |

## 2. 回归项端到端追踪（信号日 t 收盘出 α，T+1 成交）
| 回归项 | 源 → 变换 | 信息日期 | 结论 |
|---|---|---|---|
| SW L1 dummy | 面板 ind（PIT 申万成员） | t | ✓ 与前版相同 |
| lmv1 | 面板 logmv.pivot.shift(1) | t−1 | ✓ |
| beta120 | 面板 ret 与 510300 close_hfq.pct_change，rolling(120,≥60) cov/var，再 shift(1) | 收益日 t−120…t−1 | ✓ |
| mom_120_20 | log1p(ret).shift(21).rolling(100,≥80).sum | 收益日 t−120…t−21 | ✓ |
| ladv1（不再 shift） | 面板 adv20_yuan ← `research/ai_cs_panel_build.py` 第 18/35 行直接拷贝 HI_LIQ mask 的 adv20_yuan ← mask 写入方 **`research/strategy_hiliq_universe_v1.py` 第 130–141 行**：`prior = sess[sess < S][-ADV_WIN:]`，adv = 这 20 个交易日成交额均值 | 成交日 t−20…t−1 | ✓。另核 `all_a_universe_mask.py` 第 79–89 行定义相同。但 universe_mask_hiliq_v1 实际由 strategy_hiliq_universe_v1.py 写出，回执出处应改引此文件（P3-1，措辞问题） |
| vol20（叶24） | RW.shift(1).rolling(20,≥15).std | 收益日 t−20…t−1 | ✓（不是 t−19…t）。与预注册 c289e770 第 50 行「vol20 留在回归里」一致，执行的是主 Agent ~02:33 裁定 |
| acap（叶23） | leg target_weight 按 (instrument, date) 排序，groupby(instrument).shift(1)，再截 ≥X2S | leg 会话 t−1 | ✓ 见下 |
| 叶19/20、叶18/18v α | 原文件按 (date, instrument) 合并 | t（各叶自身 t 收盘 α） | 与前版相同 |
| nv120 | ret.notna().rolling(120).sum.shift(1) | t−1 | 只用于披露，不进回归 ✓ |

**acap 滞后链细查（Alpha ③）**
- leg 是**全网格**：668 个会话，每会话 5382 名，未持有记 0，无重复。逐日核对，leg 日历与 510300 交易日完全相同（668=668，两边差集都为空），与 v1 面板 2024 年日历也无差集。
- 因此按名 shift(1) 等价于「上一个交易日」：不存在稀疏行跳日的问题，也不会跨过停牌日。
- 首日处理：读取从 X2S−20 个自然日开始（[05-14, 06-03) 内有 14 个会话）。X2 首日 2024-06-03 取到 2024-05-31（月末调仓日）的权重，非 NaN。窗口外 gstart 那几天 acap 记 0，但不进评估。
- 这样改与风格集 t−1 统一，事先冻结，不看结果，符合 P3-E 的要求。

**字符串模板（Alpha ①）**
- AST 扫描两份脚本里全部「非 f-string 且含 { 的字符串常量」，只剩 3 处中文/英文注释文字里的 `logmv_{t−1}` 下标写法，不是路径或模板，也没有被 .format 使用。全文没有 `.format(` 或 `%` 格式化。
- TOOL_CMDS 现为 `/workspace/QuantLab/output/ai_factory/ARCH_TOOL_CMDS_LEAF23_X2.cmd`（叶24 为 …LEAF24…），与 OK_FIXED["tool_cmds_path"] 及草案一致 ✓。

## 3. 其余逐项
- **P1-A ✓**：`gone = day > cut`（cut 取 last_trade_date，NaT 时用 delist_date，NaT 比较为 False）；`carry = carry_nc & ~gone`；gone 日无面板行，所以 A=0、B=−inf，S 和 MV 都断链。repin_file 用 authorize 时记下的 AUTH_TOOLS；panel_recheck 和 TOOLS 里也有 data_delisted_sha256。计数 `delisted_cut_name_days_x2` 用的是不截断的影子状态 S_nc 与 S 的差（只在 X2 内统计），逻辑正确。
- **P2-A ✓**：expires_et 必填、带时区，要求晚于 issued_at，且晚于当前时刻。authorize 时检查一次；fund/build/eval 每个阶段开头的 panel_recheck 再检查一次。比较前有短路，非法串不会抛异常。
- **P3 ✓**：
  - .BJ：pool_benchmarks 计数，只要大于 0 就停跑；叶24 limit_up 遇到 .BJ 直接停跑。mask 写入方只保留 .SH/.SZ，实测 0 行。
  - WARM 两叶都已删除，grep 无残留引用。
  - nv120<100 占比写进 build meta。
  - not_suspended 注记已写。
  - e_id 未改，仍为 SW L1 + lmv1。
- **P2-1（须改）P2-B 停跑条件。** 现码是 `end_carry_delisted = 沿用到窗口末的名 ∩ cut.index`。
  - 按构造，cut ≤ 窗口末日的名在 cut 之后不可能被沿用，所以这个条件**只会被 cut > 窗口末日的名触发**。也就是窗口末合法停牌、窗口后才退市（或窗口后才有最后成交）的名，恰好是不该停跑的情形。
  - 当前 63590f23 中 last_trade_date 最大为 2026-07-29，所以现在不会误停。但 delisted_master 以后更新就可能误停。
  - **Arch 裁定：**
    - 只有当 cut ≤ 窗口末日，且该名在 cut 之后仍被沿用（任一日 S=True 且 d > cut）时才停跑，这表示截断失败；
    - cut > 窗口末日、在窗口末停牌被沿用的名不停跑，只列入 `carried_to_window_end_delisted_after_window`（附 cut 日期）作披露。
  - 建议直接用 `(S & gone_full).any()` 做截断失败断言（gone 在 X2 帧上重建），比只看窗口末日一天更强。
  - 与代码路径一致性：截断由 gone 完成，断言独立检查它，不改变任何口径和数字。

## 4. 设计假设复审
1. **截断日取 last_trade_date 还是 delist_date（P3-2，交主 Agent 知悉，不改）**
   - 区间 (last_trade_date, delist_date] 内名字仍是上市停牌，例如 002505.SZ 停了约 2 个月。按预注册「停牌记 0、不剔分母」，严格说应沿用到 delist_date。
   - 用 last_trade_date 截断等于在停牌期就「知道」它会退市，对基准（不是信号）有轻微前瞻。
   - 现行口径是 Arch bd3abe5c 所定，影响限于 8 名、每名几十个会话，方向不定。维持现状，回执披露两种口径的 wb 年化差（P3-2，选做）。
2. 吸收合并退市的持有人实际得到的是换股，两种口径都假设 0 收益。这是已知局限，只披露。
3. adv20 的定义已追到写入方。今后引用口径必须引**实际写入该文件的脚本**，不能只引同名逻辑的另一份脚本（P3-1 即此类问题）。

## 5. P 清单
- **P2-1（两叶）**：P2-B 改成 §3 裁定口径。改完报新 sha 和 diff，Arch 只复核这一处。
- **P3-1**：ladv 出处改引 `research/strategy_hiliq_universe_v1.py` 第 130–141 行（两叶 docstring 和回执都改）。
- **P3-2**：选做，回执披露 delist_date 截断口径的 wb/EW 年化差。
- **P3-3**：b3 诊断写进 delisted_master 的 sha 和 max(last_trade_date)，便于以后对照数据更新。

## 6. .ok 草案（**仍未签发**；取代 bd3abe5c §6）
- 键集合与 r2.4/r3 白名单逐键核对一致：叶23 含 dep_capadv_leg_sha256；两叶都含 data_delisted_sha256 和 expires_et；叶24 含 research_only，不含 forecast/financials/capadv_leg。
- 空值在签发时填写（manifest/mask 以 D1b 回执为准，tool_cmds 等 Arch 写好 .cmd 后填，issued_at、expires_et 带时区且 expires_et > issued_at）。

### 6.1 叶23 `output/ai_factory/ARCH_RUN_AUTH_LEAF23_SUE_DESENS_CS_X2.ok`
```
format=quantlab_run_auth_v1
signed_by=arch
leaf=23
mechanism_tag=g1g5_ashare_sue_desens_cs_v1
scope=X2
window_start=2024-06-03
window_end=2026-10-09
allow_full=true
allow_smoke=false
allow_sensitivity=true
allow_sealed=false
live=false
promotion=false
promotion_approved=false
script_sha256=<r2.5 新 sha（P2-1 修后）；当前 ccde59eb299fe3ae339d8c75ba0b4d761d5aa5c0e320e2a711dc228c86608ae6>
prereg_sha256=8f5d8ac43ba49f11b4461a287addae8c0cf247fbe9d8e81d0b339764e843922e
cs_panel_dir=/workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix
cs_panel_manifest_sha256=
cs_panel_build_version=cs_panel_v2_resumefix
data_mask_sha256=
data_delisted_sha256=<签发时实测；本审 63590f23171dbaaaf29ff51edce564130d2e8296630e1f448396fe9b8191d6fd>
dep_fe_sha256=2b49b10b1e79de49161190fd15aa0d705642aac94e21f5acda5d127b1ade916e
dep_selfcheck_sha256=ecaa30d8760f7ae5f53c330c128e6702476d01d8d69112b1dbf2fe769b7eaebe
dep_combo_sha256=bee230199ac27bf9730aa77c63b104a67bb104229622c57524867a9b54a5c51c
dep_adg_sha256=a877cec51dbb96c75a6d071e222caf35f62fd14f101741a03be117e0e6076a97
dep_lc_sha256=218b61cfbf2bf0b6bb133ef030aa2d7ff20b3eafda9724aa98c9f3b1fa5cb054
dep_l19_hiliq_sha256=16202b2e5b4935fc7613b0e6aeefd0573b1dd81c8174917782f118ae8166f9db
dep_l19_fulla_sha256=c761dc3618b813b23cb4c48489bdfd4d67808831a9639c82906e1c205d6bf7e6
dep_l20_hiliq_sha256=4ad2984e278fddad8bbdc2c0b26af8cdf3fc7078492e79ad2a38761bfff3d8ef
dep_l20_fulla_sha256=c572d56b7b32638118592f15bb2d8f2b8fb8509918b36dd1a2f3b1c6595ec403
dep_l20w_hiliq_sha256=a812b5506fcd9f05971088d856ae60344502586098fccbb3eccb46b594f25169
dep_l20w_fulla_sha256=acf9e9c39baa96c57476985eeae98386d5353706bf93510af7f5e65c83d17cdc
dep_capadv600_tw_sha256=b010839dd1d7a0a218a00957a0cf99289bedc4511b0ed058c60e25351a7fb1a3
dep_capadv600_nav_sha256=c16638ca3cf2c9f14cc9317d2e49dae49c565a9f91ea8c783aea3b42588ab16f
dep_capadv1000_tw_sha256=b010839dd1d7a0a218a00957a0cf99289bedc4511b0ed058c60e25351a7fb1a3
dep_capadv1000_nav_sha256=aba50300f4e7032fd335503911e3239526bb9475def39eec2b1471d91d4ac1f1
dep_capadv_leg_sha256=3b288c832b956820af9802f02861af459e215e7d4097a6420724b26cf2d31c4d
data_forecast_sha256=f1e59284c0a77eeca7eebb3005efce6c90d98639fb907b11dc2278ed9ad4a3e5
data_financials_sha256=bc0f4c3d3cd70a11d17f44496861e21268806509656247400c64be2d3ae7fab3
data_etf_daily_adj_sha256=48b21e84695b120b8621eff11f31f3e47879bfc05c93d3d979ddab9220ffd74c
tool_cmds_path=/workspace/QuantLab/output/ai_factory/ARCH_TOOL_CMDS_LEAF23_X2.cmd
tool_cmds_sha256=
tool_closure_adj_price_sha256=93b54ae774651b3bf9c832f8c23d973893e446270eba92423767306c57d37849
tool_closure_panel_stitch_sha256=043fa68d4e6dd40f003db04fddfd79fb431c4a00f280a0a5db35cbe733d90620
tool_closure_moneyflow_sha256=ca04507616030ccc789128bd1650b573ea934014ae6ed5e69dd90088386e943c
tool_closure_nontextbook_sha256=8a56d13669b2820abc6b8757340a5774155581cdea854594ddffe058ed13c789
out_dir=/workspace/QuantLab/output/ai_factory/leaf23_sue_desens_cs
sensitivity_specs=sig-sue,denom-daily,nofc,bo40
serial_order=fund>build_HILIQ>build_FULLA>eval>sensitivities>leaf24
run_niceness=10
rss_limit_mb=1500
issued_at=
expires_et=
```

### 6.2 叶24 `output/ai_factory/ARCH_RUN_AUTH_LEAF24_IMAX_INTRADAY_X2.ok`
```
format=quantlab_run_auth_v1
signed_by=arch
leaf=24
mechanism_tag=g1g5_ashare_imax_intraday_v1
scope=X2
window_start=2024-06-03
window_end=2026-10-09
allow_full=true
allow_smoke=false
allow_sensitivity=true
allow_sealed=false
live=false
promotion=false
promotion_approved=false
research_only=true
script_sha256=<r4 新 sha（P2-1 修后）；当前 101600f67b9447f5a13291a10b4e6eefbd2567c950d005e6647ab09d84424f12>
prereg_sha256=c289e77068be607c108359a87e1d17d6b2e8edac9e4cbcca865a9a49430133a8
cs_panel_dir=/workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix
cs_panel_manifest_sha256=
cs_panel_build_version=cs_panel_v2_resumefix
data_mask_sha256=
data_delisted_sha256=<签发时实测；本审 63590f23171dbaaaf29ff51edce564130d2e8296630e1f448396fe9b8191d6fd>
dep_fe_sha256=2b49b10b1e79de49161190fd15aa0d705642aac94e21f5acda5d127b1ade916e
dep_selfcheck_sha256=ecaa30d8760f7ae5f53c330c128e6702476d01d8d69112b1dbf2fe769b7eaebe
dep_combo_sha256=bee230199ac27bf9730aa77c63b104a67bb104229622c57524867a9b54a5c51c
dep_adg_sha256=a877cec51dbb96c75a6d071e222caf35f62fd14f101741a03be117e0e6076a97
dep_lc_sha256=218b61cfbf2bf0b6bb133ef030aa2d7ff20b3eafda9724aa98c9f3b1fa5cb054
dep_l18_hiliq_sha256=1a42f9e83d2e1c9accc64c01dccff334725a98d70c44692ec3cae5ec2d49e874
dep_l18_fulla_sha256=838c418779d5ecb69095c246928e5351334e183444f1b3308290850a029973c3
dep_l18v_hiliq_sha256=237e760c78abdeda8451486f554466bbc45c230dd3b1800583f7f8f5490d1939
dep_l18v_fulla_sha256=e942de2988dc8ce3864bbc417b8540f17f4f36da2d3e8741d3b20fbd743663d6
dep_l18w_hiliq_sha256=ed4dbf57953d84c0ef0470937fefded319fdd0bf97e87f3ce8ddc0faa68bea2a
dep_l18w_fulla_sha256=d158e41007d9274096810316141cacca1d90f6d34b49c7f2c6b1551609bc263f
dep_l18vw_hiliq_sha256=6002afab2f1214f183fca7f9064301daa272e1cc442a3d8f00bfe122a2fa6e54
dep_l18vw_fulla_sha256=ee68d5eb2d7ff5392eb5312294da6b0b73e4c5b8dbfc37564cc921a8b2cdfaef
dep_capadv600_tw_sha256=b010839dd1d7a0a218a00957a0cf99289bedc4511b0ed058c60e25351a7fb1a3
dep_capadv600_nav_sha256=c16638ca3cf2c9f14cc9317d2e49dae49c565a9f91ea8c783aea3b42588ab16f
dep_capadv1000_tw_sha256=b010839dd1d7a0a218a00957a0cf99289bedc4511b0ed058c60e25351a7fb1a3
dep_capadv1000_nav_sha256=aba50300f4e7032fd335503911e3239526bb9475def39eec2b1471d91d4ac1f1
data_etf_daily_adj_sha256=48b21e84695b120b8621eff11f31f3e47879bfc05c93d3d979ddab9220ffd74c
tool_cmds_path=/workspace/QuantLab/output/ai_factory/ARCH_TOOL_CMDS_LEAF24_X2.cmd
tool_cmds_sha256=
tool_closure_adj_price_sha256=93b54ae774651b3bf9c832f8c23d973893e446270eba92423767306c57d37849
tool_closure_panel_stitch_sha256=043fa68d4e6dd40f003db04fddfd79fb431c4a00f280a0a5db35cbe733d90620
tool_closure_moneyflow_sha256=ca04507616030ccc789128bd1650b573ea934014ae6ed5e69dd90088386e943c
tool_closure_nontextbook_sha256=8a56d13669b2820abc6b8757340a5774155581cdea854594ddffe058ed13c789
out_dir=/workspace/QuantLab/output/ai_factory/leaf24_imax_intraday
sensitivity_specs=src-total,k1,win60,exfin
serial_order=after_leaf23_complete>build_HILIQ>build_FULLA>eval>sensitivities
run_niceness=10
rss_limit_mb=1500
issued_at=
expires_et=
```
- 签发次序不变：P2-1 修后复核 → Data D1b execute 回执审过 → Arch 写 .cmd 和 .ok → 叶23（主口径 + 4 个敏感性）→ 叶24，串行。

live=false；promotion=false。本审未建任何 .ok，未运行任何叶脚本或测试。
