# 叶33 HI_LIQ 限售解禁压力残差慢 α · who_pays 封面 · **DRAFT ONLY**

- **角色**：QuantLab AI
- **时刻**：2026-10-27T05:43:00-04:00（America/New_York；墙钟 2026-10-27 05:43 ET）
- **状态**：**DRAFT ONLY** · **ok_requested=false** · **EXECUTED=false** · **不是 `.ok`** · **不申 `.ok`** · **禁自开跑** · **禁实跑** · **未挂 QUIET** · Arch **只审不签** · live=false · promotion_approved=false
- **票种**：**新叶 who_pays 提案**（**≠** selfcheck · **≠** Book-Smoke · **≠** X2 ACCEPT · **≠** 叶30/31/32 RESTORED）
- **主令**：2026-10-27 ~05:40 ET 叶32 HOLD `45dd87dc` → 续挖下一正交叶（盯 decay KEEP **且** 组合闸有过关路径；避 25/27/30/31/32 同构）

## 一句话

叶32 MARGIN_NET_FLOW_RESID selfcheck **HOLD**（decay=**KEEP** 但仍门 A/B/current 总 false；untradable=true；KEEP 不解阻 X2 ACCEPT；不派烟）。本票提案 **叶33 PRIMARY = HI_LIQ 限售解禁压力残差慢 α**（`g1g5_ashare_share_unlock_pressure_resid_v1`）：解禁事件 PIT → `unlock_raw=sum(float_share)/float_mktcap_T-1` → 短窗 pressure → SW+style 残差 → `α=−rank(pressure_resid)`；**不**读两融/Amihud/应计/CRR/hk_hold；α 向量给优化器；**decay KEEP** 硬写 `latest_resid_α>0 ∧ 非连降5季 ∧ H2_net_cagr>510300`；慢供给冲击**意图**改善可交易性（勿宣称已过闸）。请主**排号→Arch 只审不签**。

## 对照钉

| 项 | 值 |
|---|---|
| 叶号意向 | **33**（28/29 FROZEN；26 GAP 不交审；23/24 另轨不复开） |
| mechanism_tag | `g1g5_ashare_share_unlock_pressure_resid_v1` |
| who_pays | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_WHO_PAYS_DRAFT_20261027_ZH.md` |
| 叶32 HOLD | Alpha `45dd87dc` · selfcheck `99675387` · CONSUME Arch `efa033e0` · 构建闸 `1aa432a5`（不回撤） |
| 叶31 / 叶30 HOLD | `7ef5aa11` / `f00536b9`（不回撤） |
| 正交硬拒 | vs 叶19/25/27/30/31/32 Jaccard≥0.7 |
| W / rebal | DRAFT 20 / 20 交易日（慢） |
| 残差清单 | SW L1 + log 市值 + style（mom20/vol20/logADV20） |
| overlap 对象 | 叶19/25/27/30/31/32 |
| rss 意向 | **1500** 禁抬；peak_proof REQUIRED（脚本阶段） |
| forbid | 二十票齐 + `5774bb6e`（点名 `5774bb6e`/`02426b73`/`4bb141c9`/`fdbaa512`/`aa25e989`/`7e239487`/`5af20222`/`5ae077fa` + Arch 十三票） |
| `0087c928` | 另队不夹带 |
| PIN_GAP | `float_ratio` 单位不确定 → 主路径 `float_share/float_mktcap` |
| EXECUTED | **false** |

## 提案摘要（mechanism / 数据 / 公式）

| 项 | 内容 |
|---|---|
| mechanism | HI_LIQ 限售解禁压力残差慢 α：低估供给冲击抛压错配 |
| 数据路径 | `data/v2/share_float/share_float_pit.parquet`（6,449,659 行；含 `available_at`）；float=`float_mktcap_daily_from2015_tushare.parquet`；HI_LIQ mask 同叶31/32 |
| 公式 | 事件窗 H=20 / H_back=5；`unlock_raw=Σ float_share / float_mktcap_T-1`；`pressure_raw=mean_W`；`α=−rank(pressure_resid)` |
| W / 再平衡 | DRAFT 20 / 20 交易日（慢） |
| 残差 | SW L1 + log 市值 + style（mom20/vol20/logADV20）；缺列→PIN_GAP |
| 宇宙 | HI_LIQ 主判决；FULLA 研究双钉意向 |
| X2 窗意向 | 2024-06-03 → 2026-10-09 |
| 交付 | 日度 α 向量；非 Top-N |
| decay KEEP | latest_resid_α>0 ∧ 非连降5季 ∧ H2_net_cagr>510300；否则 DOWNGRADE 截断 |
| 组合闸意图 | 慢供给冲击、避高换手微观追逐 → 意图改善可交易性；**未宣称已过闸** |

## 禁止清单（forbid）

- 申 `.ok` / 实跑 / 抬 rss / 申 X2 ACCEPT / Book-Smoke / 升纸面 / 挂 QUIET
- 重跑叶30/31/32 selfcheck；碰 RESTORED 二十票 + `5774bb6e`
- 禁改 `4e0f3c00` / `dcf6b559` / `3ee9fed2` / `08f37fd2`
- 卖方/金股/survey/TP/LLM 权重；GP/杠杆；moneyflow 80/20 叠仓；hk_hold / margin / Amihud 换皮
- 叶27 idio / 叶25·30 会计 / 叶31 Amihud / 叶32 两融净流入复刻
- git commit；报 Leo；夹带 `0087c928`；叶28/29 升 PRIMARY

## 请主 / Arch

1. **主**：确认叶号（默认 **33**）→ 收 who_pays+COVER → hand Arch **只审不签**；通过后再谈预注册冻结/脚本窗。
2. **Arch**：只审文档契约与正交/禁项/PIT/`float_ratio` PIN_GAP；**不签** `.ok`；不代跑。
3. `0087c928` / 叶32 组合闸修复 **另队**，不挡本叶。

## 盘证

| 件 | 路径 |
|---|---|
| WHO_PAYS | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_WHO_PAYS_DRAFT_20261027_ZH.md` |
| COVER | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_COVER_DRAFT_20261027_ZH.md` |
| 叶32 HOLD 上下文 | Alpha `45dd87dc` · selfcheck `99675387` · CONSUME `efa033e0` · 构建闸 `1aa432a5` |
| share_float schema | `data/v2/share_float/share_float_pit.parquet`（只读核对） |

live=false · ≠X2 · ok_requested=false · EXECUTED=false · QUIET 未挂 · leo_notify=false
