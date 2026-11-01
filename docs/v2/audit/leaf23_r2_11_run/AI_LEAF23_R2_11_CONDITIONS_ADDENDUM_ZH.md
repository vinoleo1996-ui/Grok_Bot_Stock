# 叶23 r2.11 运行条件增补（AI 起草，供 Arch 审定签发；未签发前无效）

- 起草：AI（executor），2026-10-18 ET。live=false；promotion=false。不提交、未运行项目代码、未读真实数据。
- 取代对象：r2.11 起不再继承 r2.7 条件文档 docs/v2/audit/leaf23_r2_7_run/ARCH_LEAF23_RUN_CONDITIONS_ZH.md（cc16c599）§4 的命令；该文档其余条款（红线、单任务、停跑即报、不重试、10-19 04:30 ET 后不起新步）继续适用，除非 Arch 另行改写。依据：Arch B3 诊断 561219c7 §7（授权链文书缺口 P3）。
- 单次有效：本增补 + 对应 .ok 只授权下表 A01–A27 各执行一次；任何一步失败即整体作废，重跑须新增补、新 .ok。

## 1. 钉住的文件
| 项 | 路径 | sha256 |
|---|---|---|
| 脚本 r2.11 | research/g1g5_sue_desens_cs_alpha.py | 4aa19627cd65e62cad1544e4cab75d9f9d1db593c5066f13bbb7c2780871b0a1 |
| 对 r2.10 的 diff | docs/v2/AI_LEAF23_R2_11_DIFF.patch | 9cd94387c4223a243e614da7559301f7d7cea0737d251aac440c9f46b8f6a7da |
| **步骤表** | docs/v2/AI_LEAF23_R2_11_PROPOSED_CMD.txt | **14899dc8011e008a3b23ac96bda45f8a7f10e7357b499fb8b4774e57cb1d1793** |
| r2.10 基线 | 已提交 821a910 | f13443240e204a54611e9c9123d9367f1365d99b07c09534fceebfbfe50fda10（归档 _recovery/ai/pre_r2_11_0643/） |
| 诊断依据 | docs/v2/audit/leaf23_r2_10_run/ARCH_B3_FULLA_MISMATCH_DIAG_ZH.md | 561219c7f0d3cef0f0a6707acf22a8e46cd10802693f38274f24183483aa1659 |
| 叶24 r9 审核（含 P1-1 修法要求） | docs/v2/ARCH_AI_LEAF24_R9_REVIEW_ZH.md | b771b4be4334f452d9a57c6b27209782b548ff3b70cbd0b5e4f21f95d8bc3751 |
| .ok（占位） | output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_11_X2.ok | 由 Arch 签发后填写 |

## 2. 顺序
主口径 A01–A03 → 敏感性 A04–A27 → 叶24 内存复测 → 叶24 正式运行 → CMC。**主 Agent 已于 2026-10-18 06:55 ET 书面确认此顺序**；敏感性在叶24 之前跑，无延后，不需要延后披露。

## 3. 每步成功判定（五条全满足，任一不满足即停报 Arch）
1. 退出码 0。
2. 写出该阶段 meta（eval 为 eval_<uni>_meta.json，merge 为 eval_meta.json），stage / script_sha256 / arch_ok_sha256 / variant 正确，outputs 齐全且 sha 一致。
3. 日志：eval 步 9 行 pool_benchmarks peak_check（2018–2026）+ peak_check eval <uni> + STAMP；merge 步 peak_check merge + STAMP；fund/build 脚本不打这两种行（只查第 3b 条）。3b：无 RSS_GUARD_KILL / RSS_WATCHDOG_ERROR / STOP / refused / Traceback。
4. 包装器 VmHWM 最大值 ≤ 1536000 kB，meta peak_rss_mb < 1500。
5. 该步运行期间无其他读真实数据的进程（前后 ps 快照）。

## 4. 开跑前提
- r2.10 A01 产物及外部 _063101 文件由 Arch 移 _void；r2.9 fund/build 产物与 3 份 meta 保留原位。
- 94322 重新 STOP（状态 T），其余前置检查同 r2.10 回执（forecast f1e59284 / manifest 0bdabc47 / sw_l1_pit 89d4afa3 / data/v2/events 无写打开 / MemAvailable ≥ 2GB / 无其他重进程）。
- .ok 的 59 键与 r2.10 相同；r2.11 主口径起步时会在 output/ai_factory 与 _consumed 下按 sha 找到 r2.9 .ok，逐键比对 15 个输入 pin（prereg、cs_panel_*、data_*、dep_fe、dep_l19_*、dep_l20_hiliq/fulla、dep_capadv_leg），不一致即拒。现场核对：r2.9 .ok（b21e9952，_consumed）与 r2.10 .ok（97964bb1）的这些键逐值相同。

## 5. 命令原文（逐字取自步骤表 14899dc8；命令行与 b44ad8b6 逐字节相同）
```
A01 [primary eval_HILIQ] env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python /workspace/QuantLab/research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_11_X2.ok --stage eval --uni HILIQ
A02 [primary eval_FULLA] env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python /workspace/QuantLab/research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_11_X2.ok --stage eval --uni FULLA
A03 [primary merge] env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python /workspace/QuantLab/research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_11_X2.ok --stage merge
A04 [sig-sue fund] env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python /workspace/QuantLab/research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_11_X2.ok --stage fund --signal sue
A05 [sig-sue build_HILIQ] env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python /workspace/QuantLab/research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_11_X2.ok --stage build --uni HILIQ --signal sue
A06 [sig-sue build_FULLA] env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python /workspace/QuantLab/research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_11_X2.ok --stage build --uni FULLA --signal sue
A07 [sig-sue eval_HILIQ] env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python /workspace/QuantLab/research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_11_X2.ok --stage eval --uni HILIQ --signal sue
A08 [sig-sue eval_FULLA] env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python /workspace/QuantLab/research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_11_X2.ok --stage eval --uni FULLA --signal sue
A09 [sig-sue merge] env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python /workspace/QuantLab/research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_11_X2.ok --stage merge --signal sue
A10 [denom-daily fund] env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python /workspace/QuantLab/research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_11_X2.ok --stage fund --denom daily
A11 [denom-daily build_HILIQ] env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python /workspace/QuantLab/research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_11_X2.ok --stage build --uni HILIQ --denom daily
A12 [denom-daily build_FULLA] env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python /workspace/QuantLab/research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_11_X2.ok --stage build --uni FULLA --denom daily
A13 [denom-daily eval_HILIQ] env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python /workspace/QuantLab/research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_11_X2.ok --stage eval --uni HILIQ --denom daily
A14 [denom-daily eval_FULLA] env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python /workspace/QuantLab/research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_11_X2.ok --stage eval --uni FULLA --denom daily
A15 [denom-daily merge] env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python /workspace/QuantLab/research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_11_X2.ok --stage merge --denom daily
A16 [nofc fund] env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python /workspace/QuantLab/research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_11_X2.ok --stage fund --no-forecast
A17 [nofc build_HILIQ] env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python /workspace/QuantLab/research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_11_X2.ok --stage build --uni HILIQ --no-forecast
A18 [nofc build_FULLA] env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python /workspace/QuantLab/research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_11_X2.ok --stage build --uni FULLA --no-forecast
A19 [nofc eval_HILIQ] env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python /workspace/QuantLab/research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_11_X2.ok --stage eval --uni HILIQ --no-forecast
A20 [nofc eval_FULLA] env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python /workspace/QuantLab/research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_11_X2.ok --stage eval --uni FULLA --no-forecast
A21 [nofc merge] env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python /workspace/QuantLab/research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_11_X2.ok --stage merge --no-forecast
A22 [bo40 fund] env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python /workspace/QuantLab/research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_11_X2.ok --stage fund --blackout 40
A23 [bo40 build_HILIQ] env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python /workspace/QuantLab/research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_11_X2.ok --stage build --uni HILIQ --blackout 40
A24 [bo40 build_FULLA] env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python /workspace/QuantLab/research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_11_X2.ok --stage build --uni FULLA --blackout 40
A25 [bo40 eval_HILIQ] env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python /workspace/QuantLab/research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_11_X2.ok --stage eval --uni HILIQ --blackout 40
A26 [bo40 eval_FULLA] env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python /workspace/QuantLab/research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_11_X2.ok --stage eval --uni FULLA --blackout 40
A27 [bo40 merge] env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python /workspace/QuantLab/research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_11_X2.ok --stage merge --blackout 40
```

## 6. r2.11 改了什么（只改 pool_benchmarks 的 B3 递推 + 3 个 P3）
- carry_nc = (sus == 1) & (~has | restored)，restored = 面板 row_origin == "restored"（pool_benchmarks 每年多读 row_origin 一列，转成 0/1 后立即丢掉字符串列）。
- 市值锚 B / B_dd 都用新 carry 遮罩：restored 行沿用停牌前市值，不取当行 logmv；A_nc、carry_dd 从新 carry_nc 派生。
- 硬断言（逐年、面板有行处）：mask suspended=True ⟺ row_origin=restored；面板有行而 mask 无行（sus 为 NaN）同样停跑。
- 沿用名·日的原因计数改为按 (S & sus==1)。
- 不变：退市截断 gone、P2-B、cut_fail、B3 两侧校验（Mp vs carry_col、not_suspended、.BJ）、旧写法 / r2.2 披露口径；不改 Data 面板，不加白名单，不放宽任何检查。
- P3（已做）：看门狗异常不再吞掉，打印 RSS_WATCHDOG_ERROR 后 exit 137；resume 比对 r2.9 .ok 的数据 pin；步骤表写入五条判定。共享函数 docstring 去掉版本标签（rss_watchdog / peak_check / trim / merge），以便与叶24 r10 逐字一致（仅注释变化，代码不变）。
- 列出未做（非本次范围）：诊断 §4-3 的可选披露计数「复牌后 d+1 的 Mp == 复牌行 carry」；end_carry（carried_to_window_end）仍按 VAL 为空判定，窗口末若是 restored 沿用行不会列入该披露清单（只影响披露清单，不影响任何判定或校验）。

## 7. 会不会改变 HILIQ 侧数字（如实说明）
- **会改**：所有依赖池成员 Mp / 市值权重 wv 的读数——poolEW、HI_LIQ wb 基准年化，books 的 vs_wb / vs_poolEW（超额、HAC t、beta、残差 α），decisive 的 wb_floor_pass / t_hac_ge_2_50 / beats_poolEW，分位数相对 poolEW 的超额与单调性，叶20 重合段的残差相关 rho，N4 排除名数与权重占比，b3_pool_carry 的各披露差。原因：每段停牌中夹 restored 行时，旧递推在 restored 行断链，复牌后 d+1 天还会掉池一天；新规则沿用。HILIQ 窗口内校验口径下同类为 0，但「复牌后掉池一天」在 HILIQ 也存在，所以基准会动。
- **不改**：书本身（pick_book 只用 α/gate，FE.book_ret 只用权重和收益）——books 的 cagr244 / cagr252 / mdd / turnover / 30bp CAGR / 持仓统计、capadv 重算、各分位组合自身收益、Jaccard。fund/build 产物完全不变（r2.9 meta 续用）。
- 量级：未实测，不编数。Arch 诊断 §4 推断 bp 级；HILIQ 两档 CAGR（3.18% / 4.39%）低于 wb（11.60%）约 7 个百分点，判定方向几乎不可能改变，但正式数值以 r2.11 重跑为准。r2.10 A01 的 HILIQ 数字作废、不得引用。
- FULLA：同理；另外修后预期 B3 校验 0 不一致（两条 2025-04-30 002868.SZ、2026-01-14 603056.SH 按新规则 Mp=True=fulla_carry）。若新硬断言在任何年份触发，按规则停跑报 Arch，不得放宽。

## 8. 内存（静态估算，没有任何进程读真实数据）
- 基准：r2.10 实跑日志（docs/v2/audit/leaf23_r2_10_run/logs）。HILIQ（A01）VmHWM 1,109,996 kB ≈ 1084 MiB，峰值出现在 pool_benchmarks 2026 年段（2025 段末 1,069,492 → 2026 段末 1,109,996）。FULLA（A02）1,158,664 kB ≈ 1131.5 MiB 出现在 pb 之前（PX + rr pivot），pb 2025 段升到 1,161,840 kB ≈ 1134.6 MiB；B3 之后各段在实跑中没有走到，r2.10 复刻（AI_LEAF23_R2_10_MEMORY_ESTIMATE_ZH.md v4）显示其后各段低于 pb 峰。
- r2.11 每个 pb 年段新增（按已记录的形状推算，不是实测）：
  - row_origin 列读入：large_string（Arch 叶24 r9 审核 §7 P1-1 所记类型；值为 v1 / restored），每年面板约 1.2M 行（由已记录的读数推算：2024-05-01..2025 年末 2,015,162 行，2025-05-01..2026-10 1,741,082 行），偏移 8 B + 值约 2–8 B，约 12–19 MiB，读入后转 float64 标志（约 9.6 MiB）即丢弃字符串列。
  - 新 pivot：rst（pivot_table 中间 + days × names float64 ≈ 243 × 5,467 × 8 B ≈ 10.6 MiB，转 bool 后约 1.3 MiB）、bad_rs（bool，约 1.3 MiB 与临时帧）。
  - sus 保留到年末：+10.6 MiB（原先在 S/MV 递推后释放）。
  - 合计：每个 pb 年段峰值增加约 20–60 MiB（上限按各项同时存在且 pivot_table 临时开销约为结果 3 倍计）。
- 推算峰值：HILIQ ≤ 1084 + 60 ≈ 1144 MiB；FULLA：pb 段 ≤ 1135 + 60 ≈ 1195 MiB，pb 之前的 1131.5 MiB 不变，故 ≤ 约 1195 MiB。都低于红线 1500 MiB（1536000 kB），也低于 1300 MiB 目标。这是**静态推算**，正式以 r2.11 实跑 VmHWM 为准；FULLA pb 之后各段仍无实跑记录。
- 本次没有为此跑任何复刻或 schema 检查（主 Agent 06:45 裁定：读真实数据的脚本都算运行）。

## 9. 静态检查（均不读数据）
- py_compile：qlvenv 3.12 与系统 python3 3.13 都通过，cfile 写到 /tmp/ai0643/（不写 research/__pycache__）。
- pyflakes（/tmp/pyfl）：0 条。
- 过滤读取 dtype（按代码与已记录 schema 静态核对）：新增读取只在 pool_benchmarks 的 columns 里加了 row_origin，没有新的过滤条件；row_origin 与已存在的 rs 读取过滤 ("row_origin", "==", "restored") 同列同类型（字符串），.eq("restored") 在 pandas 字符串列上返回 bool；mask suspended 为 bool，转 float64 与 r2.10 相同；日期过滤未改。
- diff 可在 r2.10 原件上干净打上，结果 sha = {S}。
