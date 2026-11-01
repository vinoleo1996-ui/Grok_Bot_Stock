# Beta 会签：LOTFIX v1.4 AMEND-1 候选池快照

- 审查对象：docs/v2/LOTFIX_V1_4_AMEND_POOL_SNAPSHOT_ZH.md，sha256 0fce3cb9233a2463ce7a61fd5ef159c274e8d9e714911a022938acaed8fbaf6b（2026-10-18 复算一致）
- 母本：v1.4 FROZEN d921dd3f0f698deb822a59e40aa643f1efc7f43f6c36eaed30c7a672dbdf9425（复算一致）
- 角度：β / 风格（Beta L2、L4）
- 未运行任何代码；live=false

## 结论：PASS_WITH_AMENDMENTS
不改算法、只落盘、开关逐位一致，这些我都认可。下面 A1–A4 是纯文字补充，写进附录后生效，不用再审。

## 字段覆盖（L4）
beta、size_z、midcap_m、sw_l1、wb_i、q_cont、q_final 都在。结合 selected/stage/K_sel，失败日可以不重跑 prepare_day，逐票拆出 β、Size、MidCap 和行业的贡献。

## 补充
- **A1（池范围，L2）**：「完整候选池」须写明是完整 HI_LIQ 池，包含 S5 预筛剔除和 cap_lot=0 的名字（in_candidate=false），否则 Σwb_i≠1，bb/zb/mb 复算不出来。须加一条校验：每个 date×tier×sleeve 下 Σwb_i=1（容差 1e-9），且 Σwb_i·beta=bb。
- **A2（基准与标准化参数）**：bb、zb、mb 和 size_mu/sd、mid_mu/sd 不在快照里重复存，以 §7.6 的 core_v1_4_daily_bench.csv 为准，按 (date, tier/aum) 关联。须写明 size_z、midcap_m 用的就是该行的全池参数，beta 的估计窗等于 beta_window_start/end。快照与 daily_bench 不一致时视为落盘错误。
- **A3（现金 / 510300 行）**：组合层 β 和权重要闭合，就须每个 date×tier×sleeve 加一行 code=CASH 和 code=510300（若该袖持有）。字段：q_cont、q_final、beta（现金为 0，510300 用同窗估计值），其余可为空。或者明确写明这两项在别处落盘，并给出文件和字段。
- **A4（类型）**：size_z、midcap_m 统一写成标准化后的值，sw_l1 用申万一级代码；β 缺失时不得填 0，填 NaN，并在 stage 中标出。

## 签字
Beta | PASS_WITH_AMENDMENTS（A1–A4 纯文字） | 2026-10-18 ET | 0fce3cb9…af6b
