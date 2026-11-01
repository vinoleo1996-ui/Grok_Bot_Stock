# MAIN · 叶27 baseline_evac_r1 交审 · 2026-10-25 22:11 ET

## MATCH
Leo 开 A / 令文 `46dc8cb3` / Arch R2 `c8dc89b6` / 笔记 `0b483746`。

| 件 | sha8 |
|---|---|
| 脚本 | `585ba746`（prev `27aae6db`；≠旧 Gate A） |
| COVER | `0ff59ed4` |
| CMD | `bf6ffe4a` |
| DIFF | `dc802879` |
| HAND | `b0e01ea4` |
| VERIFY | `7ddd47e3` |
| H2A | `416df9b9` → 本令后视作 **SUBMITTED** |

路径：`docs/v2/audit/AI_LEAF27_CHUNKED_BASELINE_EVAC_*_20261025_*`；脚本 `research/leaf27_chunked_members_mktcap_r1.py`。

## 令 Arch（只审不签）
审 COVER/CMD/DIFF/脚本硬钉：
- 机制 A：lim_cache 因子窗驱逐 + α part flush；保留 mktcap_cache_r1/hist_prune_r1
- PRIMARY HILIQ×x2×ndays40；rss=1500 **禁抬**
- forbid 七票：`e107383f`/`2be59acd`/`a7d98ac9`/`8e51de63`/`3a6caa4f`/`8bcd79dc`/`725be3e0`
- peak_proof REQUIRED；估峰 1400–1490 须实峰
- 旧 Gate A CLOSED_INSUFFICIENT 禁重批；B/C 不开
- **本回合不签.ok / 不挂 QUIET / 不代跑 / 不抬帽 / 不解阻 X2**
- 审结 priority 回主 → 主再排签窗

## 令 AI
停等 Arch 审结；禁自开跑/禁申.ok。

live=false；≠X2。
