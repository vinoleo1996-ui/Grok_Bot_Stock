# 主令 · 叶27 X2 selfcheck_v2 签窗

- **角色**：主 Agent
- **时刻**：2026-10-26T00:42:17.304514-04:00（America/New_York；墙钟 2026-10-26 00:42 ET）
- **状态**：OK_WINDOW_SCHEDULED · **现不签** · **现不挂 QUIET** · live=false · ≠X2 ACCEPT

## 签窗

| 项 | 值 |
|---|---|
| 开窗 | **2026-10-26 00:55 ET** |
| 闭窗 | **2026-10-26 01:40 ET** |
| expires | **2026-10-26 01:42 ET**（过期禁签） |
| 拟 `.ok` 路径 | `output/ai_factory/ARCH_RUN_AUTH_LEAF27_X2_SELFCHECK_V2_HILIQ_X2.ok` |
| 审阅 | `docs/v2/audit/ARCH_LEAF27_X2_SELFCHECK_REVIEW_20261026_ZH.md` sha8 **`46526394`** |
| 交审令 | **`9e0317ba`** |
| 脚本 | **`a40d7069`**（`research/leaf27_x2_selfcheck_v2.py`） |
| 钉三件 | alpha `652b8a68` / meta `85c2dc78` / summary `80596bff` |
| 构建脚本 | UNCHANGED **`585ba746`** |
| PRIMARY | HILIQ × x2；钉既有 alpha → 评价权重 → selfcheck_v2 |
| rss 软帽 | **1500** 禁抬；峰＞1500 → 停+上报；**peak_proof REQUIRED** |
| forbid RESTORED | 八票 `e107383f`/`2be59acd`/`a7d98ac9`/`8e51de63`/`3a6caa4f`/`8bcd79dc`/`725be3e0`/`0f50daf7` |
| sampler（若启用） | `/tmp/quantlab_leaf27_x2_selfcheck_*` only |
| QUIET | 签时挂短窗；AI 勿擅 lift |
| Book-Smoke / X2 ACCEPT | **false**；baseline_evac CONSUMED **不解阻** |

## PRIMARY CLI（签文必须逐字）

```bash
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf27_x2_selfcheck_v2.py --universe HILIQ --window x2 --alpha-path output/ai_factory/leaf27_on_minus_id_idio_ivol/alpha_HILIQ_x2_20261025_224033.parquet --execute
```

## 令 Arch（入窗 00:55 ET 起）

1. **现不签 / 现不挂 QUIET / 不代跑**
2. 入窗后签发拟 `.ok`（禁 RESTORED 八票；钉 CONDITIONS 全项）+ 挂 `output/loop/RESEARCH_QUIET.lock`
3. 签发后 **priority 回主**（SIGNED 回执 + `.ok` sha8 + QUIET sha）
4. 过 expires **禁签**；窗外不签

## 令 AI

- **停等**主 MATCH `.ok`+QUIET 后 prelaunch 单次
- 禁自开跑 / 禁自申 `.ok` / 禁改 `585ba746` / 禁抬帽 / 禁 Book-Smoke / 禁开叶28/29
- SELFCHECK_EXECUTED 保持 false 直至授权 `--execute`

## 包钉（对照）

COVER `1e28d0e5` · CMD `61c3ef3b` · DIFF `1c4fb74a` · HAND `3dd71dc3` · VERIFY `c47be63a` · H2A `48aa5db7` · PIN `4e0473bd` · Arch CONSUMED `78557480` · AI RUN_RECEIPT `1671eec4`

live=false；promotion=false；本拍不推 Leo。
