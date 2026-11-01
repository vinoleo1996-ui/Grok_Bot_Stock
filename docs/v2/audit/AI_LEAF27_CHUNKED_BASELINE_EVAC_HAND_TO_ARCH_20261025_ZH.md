# 叶27 Post-GateA baseline_evac · HAND_TO_ARCH（**等主交审**）

- **角色**：QuantLab AI
- **时刻**：`2026-10-25T22:06:00-04:00`（America/New_York；墙钟 2026-10-25 22:06 ET）
- **status**：**READY_FOR_MAIN_SUBMIT** · **未** SUBMITTED_TO_ARCH · 等主交审后 Arch **只审不签**
- **ok_requested**：false · **live**：false · **实跑**：未做 · **`.ok`**：未申

## 包钉（盘证 MATCH）

| 件 | sha8 | 全长 / 路径 |
|---|---|---|
| 脚本 | `585ba746` | `585ba7467a5896354c937d14fe0590fa80535afd6b6263015d3c12e3dfccd4ec` · `research/leaf27_chunked_members_mktcap_r1.py` |
| COVER | `0ff59ed4` | `0ff59ed4576302224267453821a2a13f07a010ab06f3d14c624b4c73b02f5992` · `docs/v2/audit/AI_LEAF27_CHUNKED_BASELINE_EVAC_COVER_DRAFT_20261025_ZH.md` |
| CMD | `bf6ffe4a` | `bf6ffe4a05a2a90fac45e3e4cb8f101a8f5fa619fa48d145a333ecc16f126b25` · `docs/v2/audit/AI_LEAF27_CHUNKED_BASELINE_EVAC_CMD_DRAFT_20261025_ZH.md` |
| DIFF | `dc802879` | `dc8028799033600dbd0ed653b2d7868096e514c6d85f5b41bde335e850fd4980` · `docs/v2/audit/AI_LEAF27_CHUNKED_BASELINE_EVAC_DIFF_DRAFT_20261025.diff` |
| HAND | `b0e01ea4` | `b0e01ea42f589a7cc6f42570cf997ecfe7b5bd93c6e63806b47af6cc6f1a394c` · `docs/v2/audit/AI_LEAF27_CHUNKED_BASELINE_EVAC_DRAFT_HAND_20261025_ZH.md` |
| VERIFY | `7ddd47e3` | `7ddd47e3c1172f9a3c2de49d1491ad66879f57fe085f872a4a61143dfaed72e0` · `docs/v2/audit/AI_LEAF27_CHUNKED_BASELINE_EVAC_DRAFT_VERIFY_20261025_ZH.md` |

## 硬钉

- PRIMARY：HILIQ×x2×ndays40；tag `baseline_evac_r1` + 保留 `mktcap_cache_r1` / `hist_prune_r1`
- rss=1500 **禁抬**；sampler `/tmp/quantlab_leaf27_chunked_baseline_evac_*`
- out_dir 建议：`…hiliq_x2_baseline_evac`
- forbid 七票：`e107383f`/`2be59acd`/`a7d98ac9`/`8e51de63`/`3a6caa4f`/`8bcd79dc`/`725be3e0`
- 对照：主令 `46dc8cb3` / 主闸 `e8d7346c` / Arch R2 `c8dc89b6` / 笔记 `0b483746` / VOID `ff0394d0` / 回执 `f0f94c9e`
- prev 脚本 `27aae6db`（禁同语义重批）；lowmem **未改** `05bd81ea`
- peak_proof REQUIRED；估峰 1400–1490 须实峰；旧 Gate A 禁重批；B/C 本拍不开

## 动作边界

- 本文件 **READY_FOR_MAIN_SUBMIT**（**不要**写 SUBMITTED_TO_ARCH）
- 等主交审 → Arch 只审不签
- 禁自开跑 / 禁自申.ok / 禁抬帽 / 禁 silent / ≠X2 / live=false / ok_requested=false
