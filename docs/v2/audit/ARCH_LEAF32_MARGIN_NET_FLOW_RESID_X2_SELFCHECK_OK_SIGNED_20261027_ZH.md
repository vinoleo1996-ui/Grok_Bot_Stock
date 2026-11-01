# Arch 叶32 Margin Net Flow Resid X2 selfcheck_v1 · 独立 `.ok` 签发回执

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-27T05:18:42-04:00`（America/New_York） |
| 主令 | 主 05:13 ET priority · 叶32 X2 selfcheck 独立签窗 OPEN · 立即 SIGN |
| 审阅 | `3d7a5848…` **PASS_WITH_CONDITIONS** |
| CMD | `754bf251…`（禁 `--arch-ok-path`；流程门=新 `.ok`+主窗） |
| live / promotion_approved | **false** / **false** |

## 结论

**SIGNED** — 独立叶32 Margin Net Flow Resid X2 selfcheck_v1（PRIMARY：钉既有 HILIQ×x2 alpha `13eee6fd` → eval_weights → `leaf_selfcheck_common.evaluate` → `selfcheck_v1.json`）`.ok` 已落盘；**≠ X2 ACCEPT**；**≠ Book-Smoke**；**≠ 重跑 alpha**；**≠ RESTORED** 二十票（首项叶32 X2 构建 CONSUMED `02426b73`；次项叶31 selfcheck `4bb141c9`；三项叶31 build `fdbaa512`；四项叶30 selfcheck `aa25e989`；五项 R3 `7e239487`；六/七项 R2/R1 VOID `5af20222`/`5ae077fa`；及审文全集）；脚本全长 **`dcf6b559…` MATCH**；构建 **`4e0f3c00` UNCHANGED**；模板 **`e1fe578c` UNCHANGED**；审 **`3d7a5848`**；COVER **`e901405b`**；CMD **`754bf251`**；DIFF **`3f98d664`**；SCRIPT_RECEIPT **`30af740d`**；Arch CONSUME **`a1a5e35a`**；Alpha 闸 **`1aa432a5`**（ACCEPT 仅构建）；FROZEN **`6b8de5e9`**；rss 软/硬帽 **1500** 禁抬 + 硬 ABORT + peak_proof **REQUIRED**；流程门=本 `.ok`+主窗（`--execute` alone 不算授权）；**禁** CLI `--arch-ok-path`；sampler 外挂 `/tmp/quantlab_leaf32_x2_selfcheck_*`；盯 decay KEEP 三闸+gates A/B/current；**Arch 不代跑**。QUIET **已挂且保留**供 AI prelaunch（本回合不 lift；≠A18）。PRIMARY only；**无同票 FALLBACK**；峰＞1500→硬 ABORT 停+上报（禁抬帽）。SELFCHECK_EXECUTED@签=**false**。PIN_GAP IC/ICIR/WF **ABSENT_UNTIL_SELFCHECK**。**≠A18**。`0087c928` **另队不夹带**。**不报 Leo**。

## 钉点 MATCH 表

| 项 | 期望 | 实测 | 结果 |
|---|---|---|---|
| 脚本 | `dcf6b559…` | `dcf6b559165e43dcaa56df8adc3cb5d9574b6b55cc5ba20cf39d97b0285cda4f` | **MATCH** |
| CMD | `754bf251` | `754bf25123c680faaac38e185363d08a0a9e78fd50dde642b02272d8d41c62c9` | **MATCH** |
| COVER | `e901405b` | `e901405bb1015c7f1ade9704211e1e1a2a55214f7381827c12f22966aac626c8` | **MATCH** |
| SCRIPT_RECEIPT | `30af740d` | `30af740dd89275b6eae2fdd0d8214394179fa44c668e20dac056281927d9ee50` | **MATCH** |
| 审回执 | `3d7a5848` PASS_WITH_CONDITIONS | `3d7a584880e13898ce34bf528630e8386e251e7aed671079199f816a2ae5933d` | **MATCH** |
| DIFF | `3f98d664` | `3f98d66413a05f05cc5d2692fd91d043334b0c4c2c226118bd1a6392f218a0f9` | **MATCH** |
| alpha | `13eee6fd` | `13eee6fdf0922b14756cf22985964dcd177810772a2ee4ec3bdb7c1668646ed2` | **MATCH** |
| overlap / meta | `a643d71a` / `e510f346` | `a643d71ad77e3ae06eab2dc1fb20a0b99bf3d572db9310821b00ba8627bfe5fe` / `e510f346bed46e6ca64f802de3aaed5f28f469f0a2fbf68ee2d5f2fffc4f6610` | **MATCH** |
| 构建脚本 | `4e0f3c00` UNCHANGED | `4e0f3c002057393c031598e0379c6622afe8ca4a18579c9ab3b9f3d7ba4ae187` | **MATCH** |
| 模板叶31 selfcheck | `e1fe578c` UNCHANGED | `e1fe578ca70bd61f6c98bd849357beecb918f9e88f0732ac6bbc98dcfb0d4b38` | **MATCH** |
| Arch CONSUME | `a1a5e35a` | `a1a5e35af07e297577aef47311e2f79c6c2f04ecdef3a5dd60fb7518a0b3f31e` | **MATCH** |
| Alpha 闸 | `1aa432a5` | `1aa432a5c0529122c13f8ef05a42ac37921bf3a3c738e7ffe6778eb896c0d885` | **MATCH** |
| FROZEN | `6b8de5e9` | `6b8de5e9d4a4cc6caecbe344bfc4b6ce4da0f9e983f87c7c7b73759e0f893f42` | **MATCH** |
| 拟 .ok 签前 | ABSENT | ABSENT | **MATCH** |
| QUIET 签前 | ABSENT | ABSENT | **MATCH** |
| live leaf32 selfcheck `.ok` | 0 | 0→1（本签） | **MATCH** |
| `_selfcheck/` / `selfcheck_v1.json` | ABSENT | ABSENT → EXECUTED=false | **MATCH** |
| CMD 拟 CLI | 无 `--arch-ok-path`；`… --universe HILIQ --window x2 --execute` | 同左 | **MATCH** |
| forbid 碰撞 | 新 `.ok` sha8 ∉ 二十票 | `5774bb6e` ∉ forbid | **PASS** |
| pgrep leaf32 selfcheck | 空 | 空 | **MATCH** |
| 窗期 | ≥90min | `2026-10-27T05:18:00-04:00` → `2026-10-27T06:48:00-04:00` / expires `2026-10-27T06:50:00-04:00`；签时 `2026-10-27T05:18:42-04:00` | **IN_WINDOW** |

## 钉

| 项 | 值 |
|---|---|
| `.ok` 路径 | `output/ai_factory/ARCH_RUN_AUTH_LEAF32_MARGIN_NET_FLOW_RESID_X2_SELFCHECK_V1_HILIQ_X2.ok` |
| `.ok` sha8 / 全长 | `5774bb6e` / `5774bb6e8a1ad3e5dc879561b4cb3f08b9a6ad67e2bbdf34168f9c2117d26909` |
| QUIET 路径 | `output/loop/RESEARCH_QUIET.lock` |
| QUIET sha8 / 全长 | `3301eb86` / `3301eb8635e224ef38200ff413872f2780f5bee060f204e0b91db6b844a2c2ad` |
| QUIET holder | `leaf32_MARGIN_NET_FLOW_RESID_X2_SELFCHECK_V1`（含 leaf32_selfcheck；≠A18） |
| 脚本 | `research/leaf32_margin_net_flow_resid_x2_selfcheck_v1.py` = `dcf6b559165e43dcaa56df8adc3cb5d9574b6b55cc5ba20cf39d97b0285cda4f` |
| 构建脚本 UNCHANGED | `research/leaf32_margin_net_flow_resid_alpha_build.py` = `4e0f3c002057393c031598e0379c6622afe8ca4a18579c9ab3b9f3d7ba4ae187` |
| 模板 UNCHANGED | `research/leaf31_amihud_impact_slow_x2_selfcheck_v1.py` = `e1fe578ca70bd61f6c98bd849357beecb918f9e88f0732ac6bbc98dcfb0d4b38` |
| 审阅 | `3d7a584880e13898ce34bf528630e8386e251e7aed671079199f816a2ae5933d` PASS_WITH_CONDITIONS |
| CMD / COVER / DIFF / RECEIPT | `754bf25123c680faaac38e185363d08a0a9e78fd50dde642b02272d8d41c62c9` / `e901405bb1015c7f1ade9704211e1e1a2a55214f7381827c12f22966aac626c8` / `3f98d66413a05f05cc5d2692fd91d043334b0c4c2c226118bd1a6392f218a0f9` / `30af740dd89275b6eae2fdd0d8214394179fa44c668e20dac056281927d9ee50` |
| CONSUME / Alpha 闸 / FROZEN | `a1a5e35af07e297577aef47311e2f79c6c2f04ecdef3a5dd60fb7518a0b3f31e` / `1aa432a5c0529122c13f8ef05a42ac37921bf3a3c738e7ffe6778eb896c0d885` / `6b8de5e9d4a4cc6caecbe344bfc4b6ce4da0f9e983f87c7c7b73759e0f893f42` |
| alpha / overlap / meta | `13eee6fdf0922b14756cf22985964dcd177810772a2ee4ec3bdb7c1668646ed2` / `a643d71ad77e3ae06eab2dc1fb20a0b99bf3d572db9310821b00ba8627bfe5fe` / `e510f346bed46e6ca64f802de3aaed5f28f469f0a2fbf68ee2d5f2fffc4f6610` |
| 窗期 | `2026-10-27T05:18:00-04:00` → `2026-10-27T06:48:00-04:00`；expires `2026-10-27T06:50:00-04:00` |
| CLI PRIMARY | `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf32_margin_net_flow_resid_x2_selfcheck_v1.py --universe HILIQ --window x2 --execute` |
| CLI 可选显式钉盘 | `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf32_margin_net_flow_resid_x2_selfcheck_v1.py --universe HILIQ --window x2 --alpha-path output/ai_factory/_leaf32_margin_flow/20261027_042805/alpha_HILIQ_x2_20261027_044214.parquet --meta-path output/ai_factory/_leaf32_margin_flow/20261027_042805/run_meta.json --execute` |
| FALLBACK | **无**；峰＞1500 / 失败 → 硬 ABORT 停+上报（禁抬帽） |
| rss 软/硬 | **1500** / **1500** MB；forbid_raise_rss；hard_abort_on_rss=true |
| PIN_GAP | IC/ICIR/WF **ABSENT_UNTIL_SELFCHECK** |
| decay KEEP | 盯 KEEP 三闸 + portfolio gates A/B/current |
| 采样 | 仅 `/tmp/quantlab_leaf32_x2_selfcheck_*` |
| 产物 | `_selfcheck/` + `leaf_reports/leaf32_margin_flow/selfcheck_v1.json`（禁覆写钉盘 alpha/meta/overlap） |
| 禁 RESTORED | 二十票：`02426b73,4bb141c9,fdbaa512,aa25e989,7e239487,5af20222,5ae077fa,3c297052,e107383f,2be59acd,a7d98ac9,8e51de63,3a6caa4f,8bcd79dc,725be3e0,0f50daf7,3c19dd7d,1c32ab1e,6054b3bf,6de02e74` |
| Book-Smoke / X2 ACCEPT / 重跑 alpha | **false** / **false** / **false** |
| peak_proof | **REQUIRED** |
| MemAvailable@签 | 12857100 kB |
| ≠A18 | ban_touch_a18_ok_a62881b9=true；未触 |
| `0087c928` | 另队；**不在**本 `.ok` |

## CONDITIONS（签文硬钉）

1. approved_cmd 仅 `… --universe HILIQ --window x2 --execute`（可选显式 alpha/meta path）；**禁** `--arch-ok-path`
2. 流程门=本 `.ok`+主窗；`--execute` alone 不算授权
3. forbid∋`02426b73`+`4bb141c9`+`fdbaa512`+`aa25e989`+`7e239487`+`5af20222`+`5ae077fa`（二十票齐）
4. rss=1500 禁抬 + 硬 ABORT + peak_proof REQUIRED
5. 钉 alpha `13eee6fd`；≠重跑 alpha；≠Book-Smoke；≠X2 ACCEPT
6. sampler 外挂 `/tmp/quantlab_leaf32_x2_selfcheck_*`；Arch 不代跑
7. 盯 decay KEEP 三闸 + gates A/B/current
8. `0087c928` 另队不夹带；≠A18

## QUIET / pgrep

| 项 | 值 |
|---|---|
| QUIET 挂时 | `2026-10-27T05:18:42-04:00` reason=leaf32_margin_net_flow_resid_x2_selfcheck holder=`leaf32_MARGIN_NET_FLOW_RESID_X2_SELFCHECK_V1` |
| do_not_lift_until_arch_or_consumed | **true**（本拍不 lift） |
| neq_a18 | **true**（未触 `_lifted` 旧 A18 QUIET） |
| pgrep leaf32 selfcheck / kline/… | 空 |
| SELFCHECK_EXECUTED@签 | **false**（无 `_selfcheck/`、无 `selfcheck_v1.json`） |

## 下一跳

1. **主** MATCH `.ok`+`QUIET`+本回执后令 AI prelaunch→execute（须在 expires 前；Arch **不代跑**）
2. AI 交实峰回执（权重 sha + selfcheck_v1.json sha + peak rss + **PIN_GAP IC/ICIR/WF ABSENT_UNTIL_SELFCHECK 复述** + decay KEEP outcome + gates A/B/current；峰＞1500→硬 ABORT 停）→ Arch 核 CONSUME
3. ≠X2 ACCEPT；≠Book-Smoke；不解阻全量 X2；≠A18；不 RESTORED `02426b73`/`4bb141c9`/`fdbaa512`/`aa25e989`/`7e239487`/`5af20222`/`5ae077fa`；`0087c928` 另队；live=false；**不报 Leo**

live=false.
