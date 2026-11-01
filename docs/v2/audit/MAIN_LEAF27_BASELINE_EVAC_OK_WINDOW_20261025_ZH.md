# MAIN · 叶27 baseline_evac_r1 签窗 · 2026-10-25 22:19 ET

## 审结 MATCH
- Arch 审 `ARCH_LEAF27_CHUNKED_BASELINE_EVAC_REVIEW_20261025_ZH.md` sha8 **`84fb87cf`** = **PASS_WITH_CONDITIONS**
- 包钉：脚本 `585ba746` / COVER `0ff59ed4` / CMD `bf6ffe4a` / DIFF `dc802879` / HAND `b0e01ea4` / VERIFY `7ddd47e3` / H2A `416df9b9` / 交审 `00672672`

## 签窗
- **2026-10-25 22:30–23:15 ET**；expires **23:17 ET**
- 拟 `.ok` 路径：`output/ai_factory/ARCH_RUN_AUTH_LEAF27_CHUNKED_MEMBERS_MKTCAP_HILIQ_X2_BASELINE_EVAC.ok`
- **现不签 / 不挂 QUIET**（入窗再签）

## 签时须钉（CONDITIONS）
1. 脚本全长 sha256 对应 sha8 `585ba746`；PRIMARY HILIQ×x2×ndays40；三 tag：`baseline_evac_r1`+`mktcap_cache_r1`+`hist_prune_r1`
2. rss=1500 禁抬；peak_proof REQUIRED；ABORT→停+另票
3. forbid 七票：`e107383f`/`2be59acd`/`a7d98ac9`/`8e51de63`/`3a6caa4f`/`8bcd79dc`/`725be3e0`
4. sampler `/tmp/quantlab_leaf27_chunked_baseline_evac_*`；OUT_DIR 显式钉 `…hiliq_x2_baseline_evac`（勿继承 lowmem 歧义）
5. H2A 签钉盘上全长（盘上 READY_FOR_MAIN_SUBMIT vs 主令 SUBMITTED 漂移已记）
6. 旧 Gate A 禁重批：禁脚本 `27aae6db` / 禁复用 VOID `.ok` `e107383f`

## 令 Arch
- 入窗 **签发** 上述 `.ok` + **挂 QUIET**；签后 priority 回主
- 窗外不签；本令不代跑

## 令 AI
- 继续停等；主 MATCH `.ok`+QUIET 后再令 prelaunch
- 禁自开跑/禁申.ok/禁抬帽

live=false；≠X2。
