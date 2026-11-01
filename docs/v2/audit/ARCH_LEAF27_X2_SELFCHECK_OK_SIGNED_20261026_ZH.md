# Arch 叶27 X2 selfcheck_v2 · 独立 `.ok` 签发回执

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-26T01:01:52-04:00`（America/New_York） |
| 主令窗 | `MAIN_LEAF27_X2_SELFCHECK_OK_WINDOW` sha `f268d120…`；窗 **00:55–01:40 ET** expires **01:42** |
| 审阅 | `46526394…` **PASS_WITH_CONDITIONS** |
| 催签核盘 | `6b35ee22`（主 URGENT；例程未落盘→Arch 入窗补签） |
| live / promotion_approved | **false** / **false** |

## 结论

**SIGNED** — 独立叶27 X2 selfcheck_v2（PRIMARY：钉既有 HILIQ×x2 alpha → 评价权重 → selfcheck_v2）`.ok` 已落盘；**≠ X2 ACCEPT**；**≠ Book-Smoke**；**≠ RESTORED** 八票（`e107383f`/`2be59acd`/`a7d98ac9`/`8e51de63`/`3a6caa4f`/`8bcd79dc`/`725be3e0`/`0f50daf7`）；构建脚本 **UNCHANGED** `585ba746`；脚本 `a40d7069`；HAND 钉盘上 **`3dd71dc3…`**；H2A 钉盘上 **`48aa5db7…`**（status 盘 READY vs 主令视作 SUBMITTED）；**Arch 不代跑**。峰证明 **REQUIRED**（未实跑不算内存键 PASS）。QUIET **已挂且保留**供 AI prelaunch（本回合不 lift）。PRIMARY only；**无同票 FALLBACK**；峰＞1500→停+上报（禁抬帽）。baseline_evac CONSUMED **不解阻**本票以外的 X2。SELFCHECK_EXECUTED@签=**false**。

## 钉

| 项 | 值 |
|---|---|
| `.ok` 路径 | `output/ai_factory/ARCH_RUN_AUTH_LEAF27_X2_SELFCHECK_V2_HILIQ_X2.ok` |
| `.ok` sha8 / 全长 | `3c19dd7d` / `3c19dd7df94ac5684e97d86f1db59e24bda179ce89675964d346152601169874` |
| 脚本 | `research/leaf27_x2_selfcheck_v2.py` = `a40d7069374bb940863b8af6e3e103a07aa6c82f10c9cf389f53c76c57edddc0` |
| 构建脚本 UNCHANGED | `research/leaf27_chunked_members_mktcap_r1.py` = `585ba7467a5896354c937d14fe0590fa80535afd6b6263015d3c12e3dfccd4ec` |
| 审阅 | `4652639481b0fda754d349b815bd754733e3ff1ff41ad1b856c736d8a3b90a58` PASS_WITH_CONDITIONS |
| 主令窗 | `f268d1207446491defece6680c14b5399ad85a6fd20b44fa45cb611c3b4341fe` |
| 交审令 | `9e0317ba7feb8ed434ca7069ee099072f5d2a87c225d5d35bca1886b1e4e1fa3` |
| COVER / CMD / DIFF / VERIFY | `1e28d0e5232df70a601870ae9b145074ba9608638c485dee31c4a9b0d39f77f4` / `61c3ef3bdf493ba7d40428a72fbb1a2798946398605f1110e116be7de058ef0a` / `1c4fb74a2b3c70f86544905d95fc2a0babadd9add7ec56f984754ef9d46bad4b` / `c47be63a49ba1f8c848cc76aae92a306e6d82e6db9a45c68504dd75fe0affa32` |
| HAND 盘上 / H2A | `3dd71dc3e3d0b7f3636e80834bec5dd58f519c2b8f8ca141fcb453c4f5391dc0` / `48aa5db7f737efbb38933b83554f8807e2d4f559a1ba396b846eed7e1de2b72a` |
| PIN | `4e0473bdd312761a12b3be0defd5d33194a3f8ea3dca1ec5b7ad264f6ce3fb82` |
| CONSUMED / RUN_RECEIPT | `7855748076e926ff2c3ac036fd0f2fbb17648f60de0187af72f4d565ff44440d` / `1671eec4485ccf959f2dce754c4e6a00e5121f40c01d83b344d8327066668fb4` |
| alpha / meta / summary | `652b8a68b28871ddc1cbf623834650c23c79c8a81235fabc578ede71f17cf1b1` / `85c2dc7897c2796e36357042d8521e8b4b91beec8f2cd43bf18c31bdf48d4068` / `80596bffb7de1296f6859f3e7bf1afa5c73ef2ec79a579bb365061cba8579cd6` |
| 窗期 | `2026-10-26T00:55:00-04:00` → `2026-10-26T01:40:00-04:00`；expires `2026-10-26T01:42:00-04:00` |
| CLI PRIMARY | `--universe HILIQ --window x2 --alpha-path output/ai_factory/leaf27_on_minus_id_idio_ivol/alpha_HILIQ_x2_20261025_224033.parquet --execute` |
| FALLBACK | **无**；峰＞1500 / 失败 → 停+上报（禁抬帽） |
| rss 软帽 | **1500** MB；禁抬帽；脚本无硬 ABORT→流程门执守 |
| 采样（若启用） | 仅 `/tmp/quantlab_leaf27_x2_selfcheck_*` |
| 产物 | `_selfcheck/` + `leaf_reports/…/selfcheck_v2.json`（禁覆写钉盘 alpha/meta/summary） |
| 禁 RESTORED | 八票含 `0f50daf7` |
| Book-Smoke / X2 ACCEPT | **false** / **false** |
| peak_proof | **REQUIRED** |
| QUIET | 已挂 `output/loop/RESEARCH_QUIET.lock` sha `69cd9d8e` / `69cd9d8e5f20a5d36a99370a789525de925408e9b8e2b4d32d00f4052ef752e2`（保留不 lift） |
| MemAvailable@签 | 6629060 kB |

## QUIET / pgrep

| 项 | 值 |
|---|---|
| QUIET 挂时 | `2026-10-26T01:01:52-04:00` reason=leaf27_x2_selfcheck_v2 |
| pgrep kline/export_static/snapshot/gen | 空 |

## 下一跳

1. **主**确认后令 AI prelaunch 单次 PRIMARY selfcheck_v2（须在 expires 前；Arch 不代跑）
2. AI 交实峰回执（权重 sha + selfcheck_v2.json sha + peak rss；峰＞1500→停）→ Arch 核 CONSUME
3. ≠X2 ACCEPT；不解阻叶25/全量 X2；live=false
