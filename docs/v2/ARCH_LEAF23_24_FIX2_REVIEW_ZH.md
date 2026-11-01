# Arch 复审：叶23 r2.3 / 叶24 r2（AI 第二轮修复，对 129d67c5 附录 + 主 Agent 02:23 裁定）
- 时间：2026-10-18 02:30 ET，QuantLab Arch。**静态审**：只读文件、sha256sum、用 pandas 只读 mask/leg/delisted_master/v1 panel 的元数据与少量列核对口径；没有运行、import 或 py_compile 叶脚本，没有改 AI 代码或任何 FROZEN 产物，没有建任何 .ok。live=false；promotion=false。
- 自查披露：本审第一次读 mask 全表时单进程峰值 RSS 3176MB，超过 1.5GB 上限（只读，无写入），之后改为按年和按代码过滤读取（≤448MB）。此为 Arch 违规，记录在案。

## 0. 结论：**CONDITIONAL（不放行，.ok 不签）**
- P0=0 / P1=1 / P2=2 / P3=6。
- 129d67c5 的 P1-1～P1-3、P2-1～P2-6、P3-1～P3-6 **按原文全部落实**，02:23 风格集改动实现正确、无前瞻。
- **新 P1-A 来自 Arch 自己 §3 第 1、5 条的错误假设**：「mask 无行 = 未上市/退市」。实测 mask 是**矩形网格**，2017-12-01～2026-10-14 每天 5467 名全有行，退市后整段 `suspended=True`。所以「mask 无行记 False」永远不触发：凡是退市前最后一个交易日是成员、且退市前不经 ST 的名（吸收合并/私有化），会被当成停牌一直沿用到窗口末尾，收益记 0，权重按退市前流通市值。
- 即使没有 P1-A，现在也不能签：Data cs_panel 重建 execute 未完成（r6b 在审），D1b 回执、manifest/mask sha 都还没有。

## 1. 核验事实（全部实测）
| 对象 | 期望 | 实测 |
|---|---|---|
| 叶23 r2.3 `research/g1g5_sue_desens_cs_alpha.py` | f011b277… | f011b27714cd153f3e1a1ef6e6466ad855ca798942a9899ffb497b884fdfa14f ✓ |
| 叶24 r2 `research/g1g5_imax_intraday_alpha.py` | 6f57c82d… | 6f57c82d6e37e76308270dae4add51f0919912cdf296e6f7ea130d6366b7311c ✓ |
| 旧版 `_recovery/ai/pre_arch_fix2_0217/` | 81c2b4e6… / de87c839… | 一致 ✓ |
| diff `docs/v2/AI_LEAF23_24_ARCH_FIX2_DIFF.patch` | 416e237a… | 416e237a7fd4e5e4c233b6dc061fd2ae1150ea56554222616d7731491c0254bd ✓ |
| diff 复现 | — | 在临时目录对旧版 `git apply --check` 后应用，产物 sha 与 f011b277 / 6f57c82d **逐位一致** ✓ |
| 预注册 | 8f5d8ac4 / c289e770 | 未改 ✓ |
| prereg_sha_leaf23/24.txt | 更新、旧行标 superseded | ✓（另记了两份从未送审的草稿 35ab7938 / 52bdd159，已标 superseded） |
| capacity_adv 腿 `output/strategy_hiliq/legs/g1g5_capacity_adv_hiliq_v1_1_daily_weights_20261014_195620.parquet` | 3b288c83… | 3b288c832b956820af9802f02861af459e215e7d4097a6420724b26cf2d31c4d ✓ |
| mask `universe_mask_hiliq_v1.parquet` | c5433e80…（以 D1b 回执为准） | c5433e80…；日期 2017-12-01～2026-10-14，每日 5467 名，**无 .BJ** |
| `ARCH_TOOL_CMDS_LEAF23/24_X2.cmd` | 签发时由 Arch 写 | 尚不存在（正常） |
| `output/ai_factory/panel_cache_v2_resumefix` | D1b execute 产物 | 尚不存在 |

## 2. 逐项复审
| 项 | 结论 | 依据 |
|---|---|---|
| P1-1 B3 递推 | **代码忠实实现了 §3，但 §3 有错 → 见 P1-A** | 2018 起逐年读 col/logmv/ind + mask suspended，跨年只带状态向量；锚点：有行取 col、无行且 mask 停牌 NaN→ffill、其余 0（断链）；MV 同法，-inf 断链；Mp=S.shift(1)，wv=MV.where(S).shift(1)·Mp；Mp≠carry 停跑保留；verify_panel 核 receipt pins.mask_sha256，TOOLS 再核 sha(MASK)，三方一致；旧写法与 r2.2 写法的 EW/wb 只披露 ✓ |
| P1-1 原因计数 | 正确但**同义反复**（P3-A） | 沿用名·日按构造必然 sus==1，`not_suspended` 恒为 0，只是自洽检查，不是独立校验 |
| P1-2 | ✓ | 非主口径要求 allow_sensitivity=true，且 variant_tag 正好等于 sensitivity_specs 中一项；组合变体（如 `sig-sue_nofc`）会被拒；两叶 tag 字符串与草案一致 |
| P1-3 / P2-4 | ✓ | 拦：python+research/、scripts/fix_sd1/、scripts_eng/、scripts/nightly_update.py；scripts/acquire/ 只记录；排除整条祖先链（/proc stat 字段 ppid、nice、rss 下标核对正确）；nice<10、MemAvailable<2GB 拒跑；ps 快照写进 meta |
| P2-1 | ✓（另见 P2-A） | 白名单 = OK_FIXED ∪ OK_REQUIRED ∪ TOOLS ∪ TOOL_CLOSURE，未知键拒，全部必填；issued_at 带时区；tool_cmds sha 核对 |
| P2-2 | ✓ | 叶23 敏感性首阶段 fund 核主口径 eval_meta（同 script/.ok/manifest）；叶24 首阶段核叶23 主口径 + 4 敏感性 eval_meta 全在、链完整、同一 manifest、同一 script/.ok；叶24 敏感性另核叶24 主口径 |
| P2-3 | ✓ | meta/summary/B3_carry_mismatch/全部 parquet 及 ai_factory 根目录 daily_weights/run_meta 均 open('x'/'xb') |
| P2-5 | ✓ | 深市 30 开头（含 302）与沪市 688/689 用 20%，其余 10%。**.BJ**：mask 0 行，HI_LIQ/FULLA 不可能含北交所，当前无影响（见 P3-D） |
| P2-6 | ✓ | PANEL_YEARS=2018–2026，verify_panel 逐年 sha + build_version |
| P3-1～P3-6 | ✓ | assert→raise；held_resume_rows_carry 按 carry_col；叶24 再平衡日涨停占比（原口径保留）；行业帽出处注明；每阶段读前 panel_recheck（含 mask repin）；B4 注记已写 |

## 3. 主 Agent 02:23 裁定的实现
**3.1 风格集（两叶）**：SW L1 dummy + lmv1=logmv.shift(1)、beta120=rolling(120,≥60) cov/var 对 510300 后 shift(1)、mom=log1p(ret).shift(21).rolling(100,≥80) 求和（即 t−1 时点的 t−120→t−20 收益：收益日 t−120…t−21）、ladv1=log(adv20).shift(1)。**全部 ≤t−1 信息，无前瞻** ✓。预热 2023-06-01（2024 年 X2 前约 240 个交易日）、之后各年从上一年 05-01 起，≥121 日满足 ✓。gate 和第二步残差仍只用行业+lmv1，与预注册一致 ✓。
- 与 Alpha 冻结实现 `research/alpha_hiliq_s8_paradigm.py` 的差别（P3-B，披露）：Alpha 代码 beta、ADV 取 t 日（未 shift），mom=C.shift(20)/C.shift(120)−1 也以 t 为锚；AI 按裁定原文「全部 t−1」各后移一日。以裁定为准，AI 写法正确；Alpha §8 自己的实现与「t−1」不一致，交 Alpha 自查。
- 面板只有 fulla|hiliq 行和补回行，ST/成交额不足日无行。rolling 用有效日计数，mom 对缺失日等于记 0 收益（≥80/100 有效）。Alpha 用连续复权价，缺口自然跨过（P3-C，披露缺口名·日规模）。

**3.2 叶23 capacity_adv 回归项**：腿文件 3,595,176 行、2024-01-02～2026-10-09 共 668 日，每日 5382 行（全名单，未持有 0），无重复 (date,instrument)，代码格式 `000001.SZ` 与面板一致，510300 平衡行已剔除；权重只在月末 34 个调仓日变。按 date 当日合并：腿权重是 capacity_adv 用 D1 asof ADV 在 t 或更早定的目标持仓，信号 t 收盘出、T+1 成交，**t 日权重属 t 收盘已知信息，无前瞻** ✓。与「风格全取 t−1」的口径不同，但这一项是持仓状态而非风格暴露，可接受；若要统一可 shift(1)，选做（P3-E）。
- 设计提醒：该列是稀疏变量（约 10 名非零），回归只吃掉持仓名的平均 raw 值，残差化力度弱于「对 capacity_adv α 回归」。这符合预注册 §1「对 capacity_adv 回归」的字面意思，判重仍以 Alpha CMC `--base capadv` 为准。

**3.3 叶24 e_id：维持只用 SW L1 + logmv_{t−1}（Arch 明确答复）**
- e_id 是**因子定义的一部分**（预注册 c289e770 §3：先剥离行业和规模，得到特质日内收益，再取 IMAX）。它不是「去敏残差化」。
- 02:23 裁定针对的是 α 的去敏残差化，两叶都已改为冻结风格集。
- 若把 beta/mom/ADV 放进 e_id 回归，就是另一个因子：需要重新冻结预注册，家族试验次数也要 +1。
- 风格对信号的影响由最终 α 的冻结集残差化，以及 Alpha §8 A′（冻结集特质 IC）覆盖。
- 结论：e_id 不改；回执写明「e_id 是信号构造，不属于 02:23 残差化范围」。

## 4. P 清单
**P1（必须改，改后报新 sha；不改不签 .ok）**
- **P1-A（两叶，Arch §3 第 1、5 条更正）退市名被永久沿用。**
  - 实测：mask 每天 5467 名全有行，退市后 suspended=True。例：600837.SH 海通证券最后成交 2025-02-05，v1 面板当天 hiliq=True、fulla=True，此后 mask 恒停牌；601989.SH 中国重工最后成交 2025-08-12，同样情况。
  - 按 r2.3 写法，两者会以约 1005 亿元、1163 亿元流通市值，作为收益为 0 的成员，分别沿用到 2026-10-09。
  - `data/v2/delisted/delisted_master_tushare.parquet` 中，last_trade_date 落在 2024-05-20～2026-10-09 的退市名共 87 个。其中退市前一年内非 ST 的 8 个：002505.SZ、600297.SH、000861.SZ、600837.SH、601028.SH、600705.SH、601989.SH、603056.SH。ST 退市名在 ST 期已断链，不受影响。
  - 修法：
    - 读 delisted_master（ts_code、last_trade_date），对 d > last_trade_date 记 S=False、MV 断链，与「mask 无行」同等处理。
    - 新增 .ok 键 `data_delisted_sha256`，放进 TOOLS，authorize 时核对，读前 repin。本审实测 63590f23171dbaaaf29ff51edce564130d2e8296630e1f448396fe9b8191d6fd；该文件 mtime 10-18 01:10，签发时以届时实测为准。
    - b3 诊断加一项 `delisted_cut_name_days_x2`，按名列出被截断的名·日数。
    - 「mask 无行记 False」分支保留，作防御。
  - 预注册文字「停牌记 0、不剔分母」不变：退市不是停牌，所以不需要重新冻结。

**P2（与 P1-A 同一补丁改）**
- **P2-A（两叶）.ok 缺 expires_et。** 团队 .ok 格式要求必须有 expires_et，但现在的白名单会把它当未知键拒掉。修法：把 `expires_et` 加进 OK_REQUIRED，要求带时区 ISO8601，到期即拒（authorize 时，以及每个阶段开始时各核一次）。
- **P2-B（两叶）B3 回退的完整性。** P1-A 修好后，加一条硬断言：X2 窗口内被沿用的名，沿用段要么以面板有行结束（复牌），要么持续到窗口末尾，且该名不在 delisted_master 里。任何「沿用到窗口末、但在 delisted_master 里」的名，都要停跑并报 Arch。

**P3（披露或顺手修）**
- P3-A：`not_suspended` 计数按构造恒为 0，回执写明这是自洽检查；独立校验靠 Mp≠carry 和 P2-B。
- P3-B：风格集取 t−1，而 Alpha 冻结代码取 t，两者差一日，回执披露（Alpha 另行自查）。
- P3-C：mom/beta 在面板缺口日（ST、成交额不足）上的处理与连续价格口径不同，回执报「120 日窗口内有效日 <100 的名·日占比」。
- P3-D：limit_up 加防御：col 成员里出现 .BJ 就停跑（北交所涨跌幅 30%）。另外，FULLA 与 mask 均不含北交所，与「研究宇宙全 A」有差距，属已知设计边界，由 Data/主 Agent 另行跟踪，与本叶无关。
- P3-E：capacity_adv 腿权重取当日（t 收盘已知，无前瞻），回执写明；若要与风格 t−1 统一可 shift(1)，选做，但要事先声明，不能看结果再选。
- P3-F：WARM="2024-01-01" 常量已不用于 build 预热，建议删除或注明，免得误读。

## 5. 设计假设复审
1. **「mask 无行 = 退市」错误（Arch 自己的假设）**：mask 是矩形网格。教训：凡是把「缺行」当状态的规则，都要先实测数据形状。之前的 B3 C1「无行 = 停牌」错过一次，这是第二次。今后同类规则在 Arch 审稿时必须附实测。
2. **基准成员应以「最后成交 T−1 状态」为准**：Data classify_restore 的 carry 定义与本叶一致，但只覆盖复牌行；退市不在其覆盖范围内，所以 Mp≠carry 断言抓不到 P1-A。独立断言（P2-B）是必要的。
3. **稀疏持仓权重作回归项**：去敏力度弱，判重仍靠 CMC；预注册字面满足即可，不扩大解释。
4. **e_id 与残差化分层**：信号构造由预注册冻结，去敏残差化由主 Agent 裁定统一。两层不混用，避免「裁定」变成事后改因子。

## 6. .ok 草案更新（**仍未签发**；取代 129d67c5 §6）
- 签发前提：P1-A、P2-A、P2-B 修完，新 sha 复审通过；Data D1b 重建 execute 回执经 Arch 审过；`.cmd` 由 Arch 写好。
- 空值键（manifest、mask、tool_cmds、delisted 以 D1b 回执/签发时实测为准；issued_at、expires_et）签发时填写；script_sha256 修完后替换。
- 格式：key=value，无 BOM、无注释、无空格、键唯一；键集合必须与脚本白名单完全相同。

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
script_sha256=<r2.4 新 sha；当前 f011b27714cd153f3e1a1ef6e6466ad855ca798942a9899ffb497b884fdfa14f 不可签>
prereg_sha256=8f5d8ac43ba49f11b4461a287addae8c0cf247fbe9d8e81d0b339764e843922e
cs_panel_dir=/workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix
cs_panel_manifest_sha256=
cs_panel_build_version=cs_panel_v2_resumefix
data_mask_sha256=
data_delisted_sha256=
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
script_sha256=<r3 新 sha；当前 6f57c82d6e37e76308270dae4add51f0919912cdf296e6f7ea130d6366b7311c 不可签>
prereg_sha256=c289e77068be607c108359a87e1d17d6b2e8edac9e4cbcca865a9a49430133a8
cs_panel_dir=/workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix
cs_panel_manifest_sha256=
cs_panel_build_version=cs_panel_v2_resumefix
data_mask_sha256=
data_delisted_sha256=
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
- 相对 129d67c5 §6 的变化：叶23 新增 `dep_capadv_leg_sha256`（3b288c83，实测一致）；两叶新增 `data_delisted_sha256`（P1-A）、`expires_et`（P2-A）。叶24 不读 capacity_adv 腿，不加该键；叶24 白名单不含 forecast/financials 键，草案与之一致。
- 签发次序不变：本 diff 复审 → Data D1b 重建并审过回执 → 写 .cmd 和 .ok → 叶23（主口径 + 4 个敏感性）→ 叶24，串行。

live=false；promotion=false。本审未建任何 .ok，未运行任何叶脚本或测试。
