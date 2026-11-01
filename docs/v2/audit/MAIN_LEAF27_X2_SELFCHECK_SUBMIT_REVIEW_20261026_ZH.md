# 主令 · 叶27 X2 selfcheck_v2 交审（只审不签）

- **角色**：主 Agent
- **时刻**：2026-10-26T00:37:23.357410-04:00（America/New_York；墙钟 2026-10-26 00:37 ET）
- **状态**：SUBMIT_TO_ARCH_REVIEW_ONLY · **不签 `.ok`** · **不排签窗**（审结后再排）· live=false · ≠X2 ACCEPT

## MATCH 盘证

| 件 | sha8 |
|---|---|
| 脚本 `research/leaf27_x2_selfcheck_v2.py` | `a40d7069` |
| COVER | `1e28d0e5` |
| CMD | `61c3ef3b` |
| DIFF | `1c4fb74a` |
| HAND | `3dd71dc3` |
| VERIFY | `c47be63a` |
| H2A | `48aa5db7` |
| PIN | `4e0473bd` |
| alpha | `652b8a68` |
| meta | `85c2dc78` |
| summary | `80596bff` |
| 构建脚本（UNCHANGED） | `585ba746` |
| Arch baseline_evac CONSUMED | `78557480` |
| AI baseline_evac RUN_RECEIPT | `1671eec4` |

## 令 Arch

1. **立刻只审不签** 叶27 X2 selfcheck_v2 另包（PRIMARY HILIQ×x2；钉既有 alpha → 评价权重 → selfcheck_v2）
2. 对照 COVER/CMD/DIFF/HAND/VERIFY/H2A/PIN + 脚本 `a40d7069`
3. **本回合不签 `.ok` / 不挂 QUIET / 不代跑**
4. 硬钉：baseline_evac CONSUMED **不解阻 X2**；forbid 八票 `e107383f`/`2be59acd`/`a7d98ac9`/`8e51de63`/`3a6caa4f`/`8bcd79dc`/`725be3e0`/`0f50daf7` 禁 RESTORED；rss 软帽 1500 禁抬；禁 Book-Smoke；禁当 X2 ACCEPT；SELFCHECK_EXECUTED 现为 false（正确）
5. 审结落盘 `ARCH_LEAF27_X2_SELFCHECK_*_REVIEW_*.md` 后 **priority 回主**；主再排签窗

## 令 AI

- **停等**；禁自开跑 / 禁自申 `.ok` / 禁改脚本 `585ba746` / 禁抬帽 / 禁 Book-Smoke / 禁开叶28/29
- CLI 现不可跑；须新 `.ok` + 新窗

## PRIMARY CLI（仅文档对照；现禁跑）

```bash
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf27_x2_selfcheck_v2.py --universe HILIQ --window x2 --alpha-path output/ai_factory/leaf27_on_minus_id_idio_ivol/alpha_HILIQ_x2_20261025_224033.parquet --execute
```

live=false；promotion=false；本拍不推 Leo。
