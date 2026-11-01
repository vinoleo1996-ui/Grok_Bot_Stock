# 叶32 HI_LIQ 净融资流入强度残差慢 α · who_pays 封面 · **DRAFT ONLY**

- **角色**：QuantLab AI
- **时刻**：2026-10-27T03:39:49-04:00（America/New_York；墙钟 2026-10-27 03:39 ET）
- **状态**：**DRAFT ONLY** · **ok_requested=false** · **EXECUTED=false** · **不是 `.ok`** · **不申 `.ok`** · **禁自开跑** · **禁实跑** · **未挂 QUIET** · Arch **只审不签** · live=false · promotion_approved=false
- **票种**：**新叶 who_pays 提案**（**≠** selfcheck · **≠** Book-Smoke · **≠** X2 ACCEPT · **≠** 叶30/31 RESTORED）
- **主令**：2026-10-27 ~03:35 ET 叶31 HOLD `7ef5aa11` → 续挖新叶（盯 decay KEEP；避 25/27/30/31 同构）

## 一句话

叶31 Amihud selfcheck **HOLD**（decay=**DECAY_DOWNGRADE**；A/B/current 全 false；不派烟）。本票提案 **叶32 PRIMARY = HI_LIQ 个股净融资流入强度残差慢 α**（`g1g5_ashare_margin_net_flow_resid_v1`）：`net_rz=rzmre−rzche` → 短窗 / 流通市值 → SW+style 残差 → `α=−rank(flow_resid)`；**不**读 hk_hold（≠northbound 换皮）；**不**复刻 Δrzye `margin_delta` / 叶31 Amihud / 叶27 idio / 叶25·30 会计轴；α 向量给优化器；**decay KEEP** 硬写 `latest_resid_α>0 ∧ 非连降5季 ∧ H2_net_cagr>510300`。请主**排号→Arch 只审不签**。

## 对照钉

| 项 | 值 |
|---|---|
| 叶号意向 | **32**（28/29 FROZEN；26 GAP 不交审；23/24 另轨不复开） |
| mechanism_tag | `g1g5_ashare_margin_net_flow_resid_v1` |
| who_pays | `docs/v2/audit/AI_LEAF32_MARGIN_NET_FLOW_RESID_WHO_PAYS_DRAFT_20261027_ZH.md` |
| 叶31 HOLD | Alpha `7ef5aa11` · selfcheck `d4553423` · CONSUME `fc7e712a` · 构建闸 `a476567d`（不回撤） |
| 叶30 HOLD | `f00536b9`（不回撤） |
| 正交硬拒 | vs 叶19/25/27/30/31 Jaccard≥0.7 |
| rss 意向 | **1500** 禁抬；peak_proof REQUIRED（脚本阶段） |
| forbid 六票 | `4bb141c9` / `fdbaa512` / `aa25e989` / `7e239487` / `5af20222` / `5ae077fa` |
| `0087c928` | 另队不夹带 |

## 提案摘要

| 项 | 内容 |
|---|---|
| 公式 | \(\mathrm{net\_rz}=\mathrm{rzmre}-\mathrm{rzche}\)；\(\mathrm{flow\_raw}=\mathrm{mean}_W(\mathrm{net\_rz}/\mathrm{float\_mktcap}_{T-1})\)；\(\alpha=-\mathrm{rank}(\mathrm{flow\_resid})\) |
| W / 再平衡 | DRAFT 20 / 20 交易日（慢） |
| 残差 | SW L1 + log 市值 + style（mom20/vol20/logADV20） |
| 数据 | `margin_detail_daily_2018plus.parquet`（5,786,686 行；含 `available_at`）；float=`float_mktcap_daily_from2015_tushare.parquet`；HI_LIQ mask 同叶31 |
| 宇宙 | HI_LIQ 主判决；FULLA 研究双钉意向 |
| X2 窗意向 | 2024-06-03 → 2026-10-09 |
| 交付 | 日度 α 向量；非 Top-N |
| decay KEEP | latest_resid_α>0 ∧ 非连降5季 ∧ H2_net_cagr>510300；否则 DOWNGRADE 截断 |

## 禁止清单

- 申 `.ok` / 实跑 / 抬 rss / 申 X2 ACCEPT / Book-Smoke / 升纸面 / 挂 QUIET
- 重跑叶30/31 selfcheck；碰旧 `.ok` 六票
- 卖方/金股/survey/TP/LLM 权重；GP/杠杆；moneyflow 80/20 叠仓；hk_hold 换皮
- 叶27 idio / 叶25·30 会计 / 叶31 Amihud / Δrzye margin_delta 复刻
- git commit；报 Leo；夹带 `0087c928`

## 请主 / Arch

1. **主**：确认叶号（默认 **32**）→ 收 who_pays+COVER → hand Arch **只审不签**；通过后再谈预注册冻结/脚本窗。
2. **Arch**：只审文档契约与正交/禁项/PIT；**不签** `.ok`；不代跑。
3. 叶30 KEEP 修复 `0087c928` / 叶30·31 衰减修复 **另队**，不挡本叶。

## 盘证

| 件 | 路径 |
|---|---|
| WHO_PAYS | `docs/v2/audit/AI_LEAF32_MARGIN_NET_FLOW_RESID_WHO_PAYS_DRAFT_20261027_ZH.md` |
| COVER | `docs/v2/audit/AI_LEAF32_MARGIN_NET_FLOW_RESID_COVER_DRAFT_20261027_ZH.md` |
| 叶31 HOLD 上下文 | Alpha `7ef5aa11` · selfcheck `d4553423` · CONSUME `fc7e712a` |
| margin schema | `data/v2/margin/margin_detail_daily_2018plus.parquet`（只读核对） |

live=false · ≠X2 · ok_requested=false · EXECUTED=false · QUIET 未挂 · leo_notify=false
