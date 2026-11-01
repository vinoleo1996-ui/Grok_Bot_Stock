# QuantLab 因子工厂上下文（给 QuantMind 深读对照用）

- Alpha 只做：残差/正交定义、硬闸规格、短清单裁决。GP/搜索主循环归 QuantLab AI。
- promotion_approved=false；无 Leo Alpha 聊天原话不开密封。
- 主线：个股残差 + ETF 相关短清单；MATPREM/金/CB 仅对照。
- 硬闸：θ_cov=0.08 / θ_primary=0.15；impact+flat25@60万∧100万≥10%；ICIR(ε)>0；双读 icir_eps_gate vs icir_eps_posthoc；族 ρ soft0.35/hard0.50；λ_fam=0.30；Z=[log float mcap CS-z, SW_L1, shortlist_PRIMARY]。
- 硬禁：overnight* / ind_rel_overnight 精神；勿擅自扩 ACTIVE primary；ACTIVE 现 v2f_v24（24 primary + 8 secondary）。
- 资本档：60万∧100万 CNY；禁小盘主仓；数据 PIT（Data 专责）。
- 已有皮毛文档勿复述：QUANTMIND_ADAPT_PLAN_ZH.md / QUANTMIND_ADAPT_RECEIPT；本次要源码级深读 + 真实问题思路。
- 交付：docs/v2/QUANTMIND_DEEP_READ_ZH.md（中文）；禁粘贴大段上游源码；禁教材 Alpha158 主攻；AGPL 不 vendor。
