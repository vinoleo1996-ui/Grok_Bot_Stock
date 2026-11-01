# Arch fund MDD-cut Book-Smoke 独立窗 `.ok` 签发回执

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-27T23:29:48-04:00`（America/New_York） |
| 主令 | 主 ~23:25 ET · Arch FROZEN 只审 **PASS_WC `2f039c3d` MATCH** → **GO 新独立 fund MDD-cut Book-Smoke `.ok` 签窗（C3）**；钉 FROZEN **`d489c937`** / RECEIPT **`058ec68e`** / 本审 **`2f039c3d`** / DRAFT **`eeccb25e`** / ArchDRAFT **`41d4fc76`**；主臂 **V_BALLAST_MIX** 0.50/0.50·510300 + 对照 stock∈{0.40,0.60} 共 3 臂；mask **`6ab6a305`**；基线 Eng旁线 `b013a7a8` / Arch `694b9a80`+`3e2a9b9c`；ALLA + dark_horse_add；禁 mid_large；rss≤1500；**禁 RESTORED `f08ce32c`**；**禁 QUIET**；**禁代跑**；X2 另令；不混叶38 `c01c2034`；CLI_GAP 另票；≠ACCEPT；leo_notify=false；live=false |
| FROZEN / RECEIPT / ArchFROZEN | `d489c937…` / `058ec68e…` / `2f039c3d…` |
| 掩码 / 事件 / 池 / 组合主臂 | `6ab6a305…` / **dark_horse_add** / **ALLA** / **V_BALLAST_MIX** |
| live / promotion_approved / leo_notify | **false** / **false** / **false** |

## 结论

**SIGNED** — fund who_pays **组合层降 MDD** · **Book-Smoke** 独立窗 `ARCH_RUN_AUTH`（ok_id=`ARCH_RUN_AUTH_FUND_PORTFOLIO_MDD_CUT_BOOK_SMOKE_V_BALLAST_MIX`；mechanism=`g1g5_ashare_fund_portfolio_v1` / ALLA `…_v1_allA`；事件 **`dark_horse_add`**；组合主臂 **`V_BALLAST_MIX`** stock=0.50/core·510300=0.50；ablation stock∈{0.40,0.50,0.60} 共 **3** 臂；PRIMARY 池 **ALLA_tradable**；**禁 mid_large 主口径**；rss=1500 禁抬；**禁 QUIET**；**禁 RESTORED `f08ce32c`**；**禁混叶38** `c01c2034`）已**新建**落盘（**未**从 `_consumed` 拷回旧票；**未**复用旧 ok_id）。钉 FROZEN **`d489c937`** / RECEIPT **`058ec68e`** / ArchFROZEN **`2f039c3d`** / DRAFT `eeccb25e` / ArchDRAFT `41d4fc76` / mask **`6ab6a305`** / 基线 Eng `b013a7a8` / Arch `694b9a80`+`3e2a9b9c` / C2 events `81afda13` / WHO `547b246e` / ALLA `724e1df5` / book_smoke.py `1a5fa1aa` / 叶38旁线 `c01c2034` / 原 who_pays FROZEN `303e0185`旁线 **全 MATCH**。

- **book_smoke=true**；**x2=false**；**x2_accept=false**；**selfcheck=false**；**allow_eng_book_smoke=true**
- **≠ Book-Smoke ACCEPT**；**≠ X2 ACCEPT**；**≠ selfcheck**
- **Arch 不代跑**（EXECUTED@签=false；executed=false）
- **本拍未挂 QUIET**（`quiet_status_at_sign=ABSENT`；`forbid_quiet=true`）
- **禁 RESTORED** `f08ce32c` 及旧 ok_id `ARCH_RUN_AUTH_FUND_PORTFOLIO_WHO_PAYS_BOOK_SMOKE_DARK_HORSE_ADD`
- 叶38 旁线 CONSUMED **`c01c2034` UNTOUCHED**
- CLI_GAP=`book_smoke_no_arch_ok_path` 另票；本窗 Eng 可用 wrapper 预核；**禁改** `book_smoke.py` `1a5fa1aa`
- **请主 MATCH 本 `.ok` + 本 SIGNED 后再令 Eng GO** 真跑 Book-Smoke（须带 `--arch-ok-path` 本路径；先 3 臂；X2 另令）

## 钉点 MATCH 表

| 件 | 期望 sha8 | 实测全长 | 结果 |
|---|---|---|---|
| MDD FROZEN | `d489c937` | `d489c937499f6ea7b6813e4a492c81f499b45b39bfd31f4d1eb7b6cc480df896` | **MATCH** |
| FROZEN RECEIPT | `058ec68e` | `058ec68e90080c478d361c648eef23da05e5bcea3ea2b8c324da35169a0bfce3` | **MATCH** |
| ArchFROZEN 审 | `2f039c3d` | `2f039c3dee1656714e99019d645a168fcecf3ea4a18c58a3116fcfdfd81f8e07` | **MATCH** |
| MDD DRAFT | `eeccb25e` | `eeccb25e0c1fd9d8ef410bda5714aece827fef05b2b16ec1d26e3846c329df11` | **MATCH** |
| Arch DRAFT 审 | `41d4fc76` | `41d4fc7664974c782f6439407d290a467eb42365ee87ecf511cfe3d2930d836f` | **MATCH** |
| mask | `6ab6a305` | `6ab6a305cb91db9a89c17a8db005d967679cfe4585a7fecad361e902a3daa114` | **MATCH** |
| 基线 Eng BS | `b013a7a8` | `b013a7a846119aff7a542bd4a2d87791c0cad324c4cd128609343fa348f46a4c` | **MATCH**（旁线陈述） |
| 基线 Arch PASS_WC | `694b9a80` | `694b9a80645f00334ecd46b97f865d1f06a9e484921effba5d5db380df14dc60` | **MATCH** |
| 基线 Arch CONSUMED | `3e2a9b9c` | `3e2a9b9cd7d843f6fdeb3fd30efe0d919ddf80ac54b42cce7401ea2a35d633de` | **MATCH** |
| C2 events | `81afda13` | `81afda134adcf63af0b36d540c73a0aa71f0859682c45cda1a9647d32451be62` | **MATCH** |
| WHO | `547b246e` | `547b246e64de4a3c358e78bd4a95a187849da22e3cb8947e238633b498716f36` | **MATCH** |
| ALLA | `724e1df5` | `724e1df52c1e69a21dc6e9ae725000266845e77b44aff9604662fab663d35e06` | **MATCH** |
| book_smoke.py | `1a5fa1aa` | `1a5fa1aa6ab847bd1ecda4d01bd4bda88b23535edceb91021520261be3e8251b` | **RECORDED·禁改** |
| 原 who_pays FROZEN | `303e0185` | `303e01850ab2ed3966a823deb1b8ce07e43da2dbff901593134763e89b95f9e0` | **MATCH**（旁线不覆盖） |
| 叶38 CONSUMED | `c01c2034` | `c01c2034063a5cffc71122d356281a5844a6fa47307a130c4389122f51c3aa4b` | **MATCH**（未混） |
| 拟 .ok 签前 | ABSENT | ABSENT→新建 | **MATCH** |
| QUIET 签前/签后 | ABSENT | ABSENT / ABSENT | **MATCH** |
| `f08ce32c` | 仅 `_consumed` | 仅归档；未 RESTORED | **MATCH** |
| 窗期 | ~至 01:00 ET + expires+5min | `2026-10-27T23:29:00-04:00` → `2026-10-28T01:00:00-04:00` / expires `2026-10-28T01:05:00-04:00`；签时 `2026-10-27T23:29:48-04:00` | **IN_WINDOW** |

## 钉

| 项 | 值 |
|---|---|
| `.ok` 路径 | `output/ai_factory/ARCH_RUN_AUTH_FUND_PORTFOLIO_MDD_CUT_BOOK_SMOKE_V_BALLAST_MIX.ok` |
| `.ok` sha8 / 全长 | `335635dd` / `335635dd982591db87dc6e6dddeb03d5385bde231eb67634248e6614e60a5de3`（**盘上为准**） |
| ok_id | `ARCH_RUN_AUTH_FUND_PORTFOLIO_MDD_CUT_BOOK_SMOKE_V_BALLAST_MIX` |
| QUIET 路径 | `output/loop/RESEARCH_QUIET.lock` |
| QUIET 状态 | **ABSENT**（本拍**未挂**） |
| holder | `fund_portfolio_mdd_cut_book_smoke_v_ballast_mix` |
| 事件 / 池 / 组合主臂 | **dark_horse_add** / **ALLA_tradable** / **V_BALLAST_MIX**（0.50/0.50·510300） |
| ablation | stock∈{0.40,0.50,0.60}（共 3 臂；主臂 0.50） |
| 掩码 | `research/all_a_universe_mask.py` = `6ab6a305cb91db9a89c17a8db005d967679cfe4585a7fecad361e902a3daa114` |
| book_smoke.py | `quantlab/portfolio/book_smoke.py` = `1a5fa1aa6ab847bd1ecda4d01bd4bda88b23535edceb91021520261be3e8251b`（禁改） |
| 评窗 / 权重窗 | 评窗 **2024-06-03→2026-10-09**；权重覆盖 **2024-01-02→2026-10-09**（沿 FROZEN） |
| 授权窗期 | `2026-10-27T23:29:00-04:00` → `2026-10-28T01:00:00-04:00`；expires `2026-10-28T01:05:00-04:00` |
| out_dir（占位） | `output/ai_factory/_fund_portfolio_mdd_cut_book_smoke_v_ballast_mix/<ET_TS>/` |
| rss 软/硬帽 | **1500** MB；禁抬 |
| Book-Smoke / X2 ACCEPT / selfcheck / 叶38混 / RESTORED f08 | **true(本窗授权)** / **false** / **false** / **禁** / **禁** |
| EXECUTED@签 | **false** |

## QUIET / 旁线 / 禁 RESTORED

| 项 | 值 |
|---|---|
| QUIET 本拍 | **未挂 = ABSENT** |
| forbid_quiet / ban_hang_quiet_this_sign | **true** |
| Arch 代跑 Book-Smoke | **未执行** |
| 叶38 `c01c2034` | **未打开改写 / 未混** |
| RESTORED `f08ce32c` | **否**（仍仅 `_consumed`；本 `.ok` 为新建） |
| 旧 who_pays BS ok_id | **禁复用 / 禁拷回** |
| mid_large 主口径 | **false** |
| CLI_GAP | `book_smoke_no_arch_ok_path` 另票；禁改 `1a5fa1aa` |

## 下一跳

1. **主** MATCH 本 `.ok`（+ 本 SIGNED 回执）后令 **Eng GO** 真跑 Book-Smoke（须在 expires 前；须带本 `--arch-ok-path`；先 **V_BALLAST_MIX** + 对照 3 臂；Arch **不代跑**）
2. X2 **另令**（本 `.ok`：`x2=false`）
3. ≠Book-Smoke ACCEPT；≠X2 ACCEPT；禁混叶38；禁挂 QUIET；禁 RESTORED `f08ce32c`；禁抬 rss；live=false；leo_notify=false

live=false.

---
本回执路径：`docs/v2/audit/ARCH_FUND_PORTFOLIO_MDD_CUT_BOOK_SMOKE_OK_SIGNED_20261027_ZH.md`
本回执 sha8：**以盘上为准**（落盘后由脚本打印；文内自算若不一致勿采）
盘上打印钉（写入时正文哈希）：sha256=`d9771793890265f550bb13af357664cf3bba76a9623f579a3f7f249ecf427fe2` · sha8=`d9771793`（若与 `sha256sum` 全文件不一致，**以 sha256sum 盘上全文件为准**）
