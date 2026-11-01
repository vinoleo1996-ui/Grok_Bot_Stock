# Arch 复核附录：叶23 r2.5 / 叶24 r4（FIX4，对 b09901f5）
- 时间：2026-10-18 02:48 ET，QuantLab Arch。静态复核：只读 diff 和文件、sha256sum、在临时目录 git apply；没有运行、import 叶脚本，也没有读数据，没有建 .ok。live=false；promotion=false。

## 0. 结论：**PASS（代码层面）**——P0=0 / P1=0 / P2=0 / P3=0
- 两叶代码可以进入签发流程。**.ok 仍不签**：前提是 Data D1b execute 回执审过（r6b 还在审，panel_cache_v2_resumefix 尚不存在），并且 Arch 写好 .cmd。

## 1. 核验
- 叶23 r2.5 07c998737647263ab17e851ddaa6f3fea7b857776e22354d614bedf42742bfaa ✓；叶24 r4 1e8de734080f7cfa47f582ad6ccaaedf85402365bc710da36aa2923d4af7e5dc ✓。
- diff a2c07a1c22c185f802c006cfc4e2a40f453ad0fa2c584ecf6f78453eb7a411f8（281 行）。在临时目录对 `_recovery/ai/pre_arch_fix4_0241/`（ccde59eb / 101600f6，与上轮 sha 一致）应用后，**逐位复现**两份新文件 ✓。

## 2. 改动范围（逐 hunk 核对；两叶改动对称）
| hunk | 内容 | 归属 |
|---|---|---|
| pool_benchmarks 开头 | 新增 cut_dd（delist_date，NaT 时用 last_trade_date）和 sp_dd/mp_dd | P3-2 |
| 年循环 | 新增 gone_dd/carry_dd/A_dd/B_dd/S_dd/MV_dd，变量独立，只追加到 parts["S_dd"/"MV_dd"] | P3-2 |
| 循环后 | 删除窗口末停跑规则；在 X2 帧上用 idx 和 cut 独立重建 gone_full，只要 `(S & gone_full).any()` 就 raise；新增 end_after 字典（cut > e 的名及其 cut 日期） | P2-1 |
| 循环后 | Mp_dd/wv_dd 只放进返回 dict | P3-2 |
| diag | 新增 cut_failure_check、carried_to_window_end_delisted_after_window、delisted_master_sha256（取 AUTH_TOOLS）、delisted_master_max_last_trade_date；删除 carried_to_window_end_in_delisted | P2-1 / P3-3 |
| style_feats docstring / 注释 / eval 注记 | ladv 出处改引 strategy_hiliq_universe_v1.py 第 130–141 行；B3 注记改写 | P3-1 / 文字 |
| evaluate 停跑条件 | 删除 `carried_to_window_end_in_delisted` 一项，其余三项（carry_mismatch / not_suspended / .BJ）不变 | P2-1 |
| evaluate b3.update | 新增 ew_d/wb_d 及 *_cut_delist_date、*_diff_vs_cut_delist_date 四个字段，note 文字更新 | P3-2 |
- **范围外改动：无。** 风格集、acap、vol20、e_id、.ok 白名单、阶段链、选股、记账、判定 t 一处都没动。

## 3. P3-2 影子递推的隔离性
- **不影响主口径。** 影子状态 sp_dd/mp_dd/S_dd/MV_dd 全部是新变量名，不写回 sp/mp_/S/MV。主口径的 Mp/wv 仍只由 carry（last_trade_date 截断）推出。ew_d/wb_d 只写进 b3 字典。
- **不进判定。** books、vs_wb、vs_poolEW、判定 t、wb 地板用的都是 ew/wb，不用 ew_d/wb_d。影子也不触发任何停跑，所以不会改变主 pass/fail。
- **不是新试验。** 它和已有的 old/r2.2 两种构造一样，只是**基准构造**的披露：不产生信号、不选股，也不作判定。不计入家族试验次数，不需要多重检验校正。回执要写明「只披露，不作判定」。
- **RSS 估算。** 每年多出约 6 个与 has 同形的临时帧（约 245×5500，float64 每帧约 11MB），用完即 del。跨年多存 S_dd、MV_dd 两个 X2 帧（约 600×5500，bool 约 3MB，float64 约 26MB）。末尾 Mp_dd、wv_dd 约 30MB，随 pb 一起释放。合计增量 ≤约 100MB，在 1500MB 上限和 RSS 看门狗之内。实测要等授权运行，峰值写进 meta。

## 4. P2-1 复核
- gone_full 直接由 idx 和 cut 重建，不复用递推里的 gone，所以是独立断言。它覆盖 X2 全部日（不止窗口末），失败时报出名和名·日数。
- 窗口后退市、窗口末合法停牌的名只列入披露，不停跑，与 b09901f5 裁定一致。
- 按构造，这个断言正常情况下恒为 False，作用是防止将来改代码破坏截断。

## 6. 最终 .ok 草案（**仍未签发**；取代 b09901f5 §6）
- script_sha256 已填为本轮 sha。空值键签发时填写：manifest/mask 以 D1b 回执为准；tool_cmds 等 Arch 写好 .cmd 后填；data_delisted 取签发时实测；issued_at、expires_et 带时区，且 expires_et > issued_at。

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
script_sha256=07c998737647263ab17e851ddaa6f3fea7b857776e22354d614bedf42742bfaa
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
script_sha256=1e8de734080f7cfa47f582ad6ccaaedf85402365bc710da36aa2923d4af7e5dc
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
- 签发次序：Data D1b execute 回执审过 → Arch 写 .cmd 和 .ok → 叶23（主口径 + 4 个敏感性）→ 叶24，串行。

live=false；promotion=false。本复核未建任何 .ok，未运行任何叶脚本或测试。
