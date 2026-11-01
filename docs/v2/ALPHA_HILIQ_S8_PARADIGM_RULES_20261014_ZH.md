# HI_LIQ 五事件腿 §8 范式判定读法（Alpha）— 看数前冻结

- 冻结：2026-10-14 09:13:34 ET（算任何 §8 数字之前）
- 依据：Leo 09:12 ET（经主 Agent）；`docs/v2/ALPHA_ACCEPT_PARADIGM_RESID_NEUT_ZH.md`；叶验收 v2 阈值（ΔIC≥+0.003、ΔICIR≥+0.05 双读、ρ≤0.5）**不改**
- 宇宙 HI_LIQ_V1.1 掩码；窗口 X2 2024-06-03→2026-10-09（样本内）；h=20；年化 244；成本 17.5bp/单位换手；信号=腿权重
- 风格：SW L1 哑变量 + log 流通市值 + 滚动 120 日 β + 动量（t-120→t-20）+ 流动性 log ADV20
- t 统计：naive / neff(n/h) / HAC(Newey-West, lag=h-1) **仅披露**，不作阈值

| 项 | 计算 | PASS 条件 |
|---|---|---|
| A 残差 α | 腿信号对行业+风格残差化 → RankIC、ICIR 全样本 + 滚动 252 中位 | RankIC>0 且两种 ICIR 读法均 >0 |
| A′ 特质 α | 再对 capacity_adv HI_LIQ 信号正交 → RankIC/ICIR；CMC ΔIC/ΔICIR（0.8·z_cap+0.2·z_leaf vs z_cap） | 特质 RankIC>0 且 ΔIC≥+0.003、ΔICIR 双读≥+0.05 |
| B 中性化净超额 | 每日截面回归收益对行业+风格取残差（=相对 HI_LIQ 池基准）；腿股票袖 top-N（60万 N=6、100万 N=10）按权重归一，T+1（权重滞后 2 日作用于收盘收益），扣 COST·换手 | 两档年化净超额均 >0 |
| C 快慢错配 | ρ(腿残差 z, cap 残差 z)；换手/持有期比；叠加 ΔIC vs 加权和；腿中性收益对 cap 回归截距（正交增量） | ρ≤0.5，且不得同时满足〔ρ>0.3、持有期同档(比值 0.5–2)、正交截距≤0〕 |

- 研究级 ACCEPT：A+A′+B+C 全过，且 §2.1 行业硬闸过；**研报类（report_rc_allup）/调研类（insurer_surv）最高 WATCH**。
- 进 GATE_V3/派 Eng/纸面：另需 GATE_V3 四条 + Eng X2；本轮 Alpha 不派 Eng。
- Top-N 等权不作证据；B 用中性化残差收益，非原始 Top-N 收益。

## 附：风格暴露时点锚点澄清（2026-10-18 ET 追加；事后澄清，阈值不变）
- 依据：主 Agent 2026-10-18 02:44 ET 裁定；Arch bd3abe5c P3-B；Alpha 自查 `docs/v2/ALPHA_S8_LAG_SELFCHECK_ZH.md`（238b2978）。
- **信号残差化（A、A′、叠加 IC/CMC、C 中的 ρ）：t−1 相对信号日 d。**
  - log 流通市值取 d−1 收盘；
  - β120 用 d−120..d−1 的收益；
  - 动量取 C(d−21)/C(d−121)−1；
  - log ADV20 取 mask 的 adv20_yuan[d]，它本身就是 d−20..d−1 的均值（写入方 `research/strategy_hiliq_universe_v1.py` L130–141：`prior = sess[sess < S][-ADV_WIN:]`），**已经是 t−1**；
  - 申万一级取不晚于 d 的最近月末成员；
  - 前瞻收益从 d+1 起，截到窗口末 END。
- **B（中性化净超额）：t−1 相对收益日 r**，即用 r−1 的暴露（`resid_ret` → `xmat(c, d0=r−1)`），与 af48bc05 相同。
- **适用范围：** v1.1（`research/alpha_hiliq_s8_paradigm_v1_1.py`、`research/alpha_combo_marginal_v1_1.py`）从叶23/24 起生效，叶25 及以后默认使用 v1.1。
- **旧版本：** af48bc05 / bee23019 冻结，只用于 v4/v4.1 复现以及作为对照披露列。v4/v4.1 的判定不变，阈值不变。
- **说明：** 「事后、只适用于后续叶子」。冻结风格集不含 vol20。
