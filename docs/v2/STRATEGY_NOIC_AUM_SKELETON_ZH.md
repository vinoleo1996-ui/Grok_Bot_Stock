# 无 IC 多袖套账本骨架（AUM 60万 / 100万）— 研究诊断级

**状态**：diagnostic · `promotion_approved=false` · **禁小盘**  
**日期**：2026-10-12 00:15 ET（书签刷新 2026-10-12T01:28:16-04:00）  
**Owner**：Strategy  

## 口径（Leo）

| 项 | 规则 |
|---|---|
| 主结论 AUM | **60万** 与 **100万**（`--capital 600000` / `1000000`） |
| 大资金 500万 | **仅附录**，不得作主结论标题数字 |
| IC 期货 | **禁止**（一手约 147 万，小资金手数归零） |
| 510500 贴水代理 | **禁止** |
| 小盘 | **禁止** |
| Full D1 / 密封窗 | **禁止**（本骨架不跑） |
| 晋升 | `promotion_approved=false`；不作晋升证据 |

## 袖套构成（骨架）

| 袖套 | 默认权重 | 规则 |
|---|---|---|
| CB | 50% | 全规则 **CB1** 或 **CB2**（`--cb-mode`；默认 CB2，对齐 CIB2-NOIC） |
| 压舱 | 50% | **511010 / 518880** 60 日逆波（月度），MA-RP 风格但**去掉股票腿** |

可选：后续若 Beta 交接 MA-RP（含 510300）无 IC 变体，再以 `--sleeves` 扩展；当前骨架保持债金压舱。

## 代码

```bash
cd /workspace/QuantLab
# 主结论两档
PYTHONPATH=. python3 -m quantlab.portfolio.v2_multisleeve_book_noic \
  --capitals 600000,1000000 --cb-mode CB2 --windows X1,X2 \
  --out output/strategy_mbook_noic_diag

# 便宜结构性冒烟（最近 2–3 个信号日）
PYTHONPATH=. python3 -m quantlab.portfolio.v2_multisleeve_book_noic --smoke

# 5M 仅附录（显式开关；结果带 appendix_only=true）
PYTHONPATH=. python3 -m quantlab.portfolio.v2_multisleeve_book_noic \
  --capital 5000000 --allow-appendix-5m --windows X2 \
  --out output/strategy_mbook_noic_diag_appendix5m
```

模块：`quantlab/portfolio/v2_multisleeve_book_noic.py`  
既有含 IC 账本：`quantlab/portfolio/v2_multisleeve_book.py`（L≤1.5；与本骨架分离）。

## Beta 交接值班（历史短表已并入上方「与 fail_explore / pass 臂的关系」）

一旦 `output/v3/handoff_strategy/` 出现**无 IC**、适配 60万/100万 的新交接包，Strategy **立刻**两引擎对账；本骨架只作诊断容器，不顶替正式交接。

**2026-10-12T01:28:16-04:00 值班快照**：**唯一 explore-pass 候选（研究级）= CB-MATPREM**（对账+NOIC smoke OK；**非晋级**）；有效无 IC 交接 = **cb_matprem/**；其余近期臂均为 fail_explore；`cb3ic/` 空目录勿当交接；`cib2/` 为含 IC 的 CIB2-EW（**不进 NOIC**）；`fut_rp*` / `sc_vt` 含期货或 IC，**不进 NOIC**。详见 `output/v3/handoff_strategy/WATCH_ZH.md`。


## 更新 2026-10-12 01:19 ET — CB-MATPREM 接线评估（研究级）

| 项 | 内容 |
|---|---|
| 推荐 | **wire diagnostic now**（研究诊断接线）；**wait** 才升为默认 CB 袖套；**未 blocked** |
| 可插路径 | 交接包 `output/v3/handoff_strategy/cb_matprem/AUM_600000/` 与 `.../AUM_1000000/`（targets：`date,instrument,target_weight`，已含 CB50%+压舱50% 合成权重） |
| 相对骨架角色 | **替换 CB 选券规则**（日历池低溢价），**压舱仍为 511010/518880 逆波 50%**；**禁止 IC** |
| 与 CB1/CB2 差异 | 池先经转股期∩剩余期限[1,3]年；**不要求**价≤130；空池→100%压舱 |
| 阻断 / 风险 | X1 池极浅（空仓≈81.7%）；`v2_multisleeve_book_noic.py` 目前仅 `--cb-mode CB1/CB2`，尚无 MATPREM 模式或外部 schedule 开关；密封窗禁重跑；不作晋升证据 |
| 下一步 | (1) 增 `--cb-mode MATPREM` 或 `--external-targets` 读交接 targets（诊断）；(2) 便宜 smoke 校验权重形状；(3) **不**跑 Full D1 / 密封窗；(4) 前向纸面盯池深后再谈默认主臂 |
| 短报 | `output/strategy_mbook_noic_diag/MATPREM_NOIC_EVAL_ZH.md` |

## 与 fail_explore / pass 臂的关系（同步 2026-10-12T01:28:16-04:00）

> **当前唯一 explore-pass 候选（研究级，非晋级）**：**CB-MATPREM**（对账+NOIC smoke OK）。下表其余臂均为 **fail_explore / 无交接**。

| 臂 | 状态 | 交接 | 对本骨架含义 |
|---|---|---|---|
| **CB-MATPREM** | **唯一 explore-pass 候选**（研究级；对账+NOIC smoke OK；**非晋级**） | **有** `handoff_strategy/cb_matprem/` | **唯一可接诊断 CB 袖套**；X1 空仓≈81.7% 靠压舱，须盯池深；`promotion_approved=false` |
| **CIB2-NOIC** | fail_explore（X2≈8%&lt;12%） | **无交接** | 同构参考；骨架复用其「CB+债金、无 IC、AUM 60/100万」口径 |
| **TCarry-G** | fail_explore（X2 8.5%&lt;12%） | **无交接** | 可作压舱零件候选，不进主臂 |
| **CB3-IC** | fail_explore | **无交接**（空目录） | 含 IC，不进本骨架 |
| **CB3-BALLAST** | fail_explore（X2≈0.5%） | **无交接** | 不进 |
| **SHARE-AC** | fail_explore（X2≈6.6%） | **无交接** | 不进（且含宽基股腿，非本债金骨架） |
| **CB-DUAL** | fail_explore（X2≈10.5%） | **无交接** | 不进 |
| **CB2-DYN** | fail_explore（X2≈6.8–7.0%） | **无交接** | 不进 |
| **NAV-DISC** | fail_explore（X2≈5.8%） | **无交接** | 含宽基股腿，不进 |
| **CB1-FLOOR** | fail_explore（X2≈2.5%） | **无交接** | 不进 |
| **LIQ-TV** | fail_explore（X2≈7.7%） | **无交接** | 不进 |
| **MIX-FROZEN** | fail_explore（X2≈10.8–10.9%） | **无交接** | 含股腿，不进 |

台账：`docs/trial_ledger.csv` Strategy note 行 + `output/promotion_ledger.json` descriptive_*；预注册描述见 `docs/v2/PREREGISTRATION_V2_ZH.md`。

## 不做

- 不跑 Full D1 / 密封窗  
- 不把 5M 数字写进主结论  
- 不晋级、不改 Mandate JSON  
- 不碰小盘

## 更新 2026-10-12 01:23 ET — MATPREM 诊断接线已落地（研究级）

| 项 | 内容 |
|---|---|
| CLI | `--cb-mode MATPREM` 或 `--external-targets output/v3/handoff_strategy/cb_matprem`（直灌 targets，不叠 combine_noic） |
| smoke | 60万/100万 × X1/X2 已跑；结果 `output/strategy_mbook_noic_diag/matprem/` |
| 主表 | X2 年化≈12.8%/13.2%；X1≈3.3%/3.2%；MDD≈−5.0~−5.4% |
| 软风险 | **X1 空仓≈81.7%**，主要靠压舱 |
| 晋升 | `promotion_approved=false` 未改 |
| 短报 | `output/strategy_mbook_noic_diag/matprem/SHORT_ZH.md` |

## 更新 2026-10-12T01:28:16-04:00 — 书签：唯一 explore-pass 候选

- **CB-MATPREM** = 当前 **唯一** explore-pass 候选（研究级）：对账 OK + NOIC smoke OK。
- **仍非晋级**：`promotion_approved=false`；不作晋升证据；禁小盘。
- 其余近期臂（BALLAST / SHARE-AC / DUAL / DYN / TCarry-G / CIB2-NOIC / CB3-IC / NAV-DISC / CB1-FLOOR / LIQ-TV / MIX-FROZEN）均 **fail_explore**。
- 继续盯 `output/v3/handoff_strategy/`：新 Beta 无 IC 袖套 → 立刻 Strategy 双引擎对账。

