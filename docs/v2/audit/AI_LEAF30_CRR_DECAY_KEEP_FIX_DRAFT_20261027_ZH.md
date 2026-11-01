# 【DRAFT ONLY · 研究队列 KEEP】叶30 CRR 衰减修复提案（另窗）

- 角色：QuantLab AI
- 时点：2026-10-27 02:01 ET（America/New_York）
- 状态：**DRAFT ONLY** · **不自动开跑** · **不申 `.ok`** · **禁**改已 CONSUMED 脚本字节当复跑 · **禁** RESTORED `aa25e989`/`7e239487`/`5af20222`/`5ae077fa` · **禁**重跑 selfcheck
- 上下文：Alpha HOLD `f00536b9`；report `3eeffb02`；decay=**DECAY_DOWNGRADE**（`latest_alpha<0` + `H2_net_cagr<=510300`）；门A=true 不解阻；门B/current=false；**不派 Eng Book-Smoke**；构建闸 `1c992d62` 不回撤
- live=false；promotion_approved=false；≠X2 ACCEPT；leo_notify=false

---

## 1. 根因对齐（selfcheck，不重跑）

| 触发 | 实数（自 HOLD 审 / report） | 含义 |
|---|---|---|
| `latest_alpha<0` | latest_resid_alpha≈**−0.021** | 近端残差 α 转负 → v1.1 硬触发 DOWNGRADE |
| `H2_net_cagr<=510300` | H2 net≈**−6.56%** vs bench≈**−3.37%** | 后半窗净 CAGR 未优于 510300 |
| 非触发 | 换手≈3.5%/日；连降=1 | H1/连降 3 未触发 |

**解释（研究假设，非已验证因果）**：慢 α（CRR+vol_pen）在近端可能被 (a) λ=1.0 对 vol_pen 过罚、(b) 行业掩码外仍含高波动转化噪声、(c) 快评价闸与慢信号同一套权重放大近端回撤 共同拖累 H2/latest α。

---

## 2. 低成本提案（1–2 条；KEEP 另窗）

### 提案 A（优先）：近端 λ 下调 + 快闸/慢 α 分离（文档级规格变更）

| 项 | 内容 |
|---|---|
| 改什么 | 预注册**新修订草稿**（非改 CONSUMED `3ee9fed2`/`797724d4` 字节复跑）：(1) λ：全局 1.0 → **分段** λ_base=1.0、近端窗（与 decay H2 对齐）λ_near=**0.5**（冻结时写死，**另窗**才可测）；(2) 评价：**慢 α 向量**与 **快闸/权重帽** 分层披露，禁用快闸结果回写主 α |
| 为何低成本 | 不改会计 PIT 主路径；不重拉财报；仅合成权重与评价分层 |
| KEEP 验收 | 另窗 selfcheck：latest_resid_α>0 **且** H2_net_cagr>510300；Gate B/GATE_V3 再读；仍 FAIL → 废案 |
| 禁 | 本窗实跑；读密封窗；RESTORED 旧 `.ok`；事后因数字再改 λ |

### 提案 B（备选）：vol_pen 分段 + 行业掩码微调

| 项 | 内容 |
|---|---|
| 改什么 | (1) `vol_pen` 用 **分段秩**：高波段（上四分位）才满罚，中低波段罚半（系数冻结时写死）；(2) 掩码：在银/地/非银之外，**研究披露**「综合」敏感性（**默认仍不硬排除**，除非计数闸证明噪声源）；不得无计数依据扩掩码 |
| 为何低成本 | 仍用既有 CRR/ε 序列；不新开数据源 |
| KEEP 验收 | 同提案 A；另须 Jaccard vs 叶19/25 仍 <0.7 |
| 禁 | 把掩码扩成数据挖掘；改 CONSUMED alpha 字节原地「修复」 |

**推荐顺序**：先 A（λ 分段 + 评价分层）→ 主裁是否排 Arch 审修订 who_pays；B 仅当 A 被拒或计数显示行业噪声。

---

## 3. 明确非目标

- **不是** X2 ACCEPT / Book-Smoke 授权
- **不是** 对 `aa25e989` 签窗 RESTORED
- **不是** 重跑 `leaf30_crr_x2_selfcheck_v1.py`（`797724d4`）
- **不是** 改已 CONSUMED R3 alpha（`c8c7a5a5`）当「修复版」冒充同叶验收
- 若主裁开修：须 **新** who_pays 修订号 + **新** 脚本路径/sha + **新** `.ok` 窗

---

## 4. 请主裁决

1. 是否把提案 A 排入 **Arch 只审**（文档）队列；  
2. 是否与叶31 新叶并行（推荐：**叶31 PRIMARY 推进**，叶30 KEEP 修复降优先级）；  
3. 未明示前：**不**写脚本、**不**申 `.ok`、**不**实跑。

---

## 5. 草稿钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/audit/AI_LEAF30_CRR_DECAY_KEEP_FIX_DRAFT_20261027_ZH.md` |
| 状态 | DRAFT ONLY · 研究队列 |
| 交主 | 是（裁决是否排 Arch） |
| 自动开跑 | **否** |

**sha256 / sha8**：落盘后打印。
