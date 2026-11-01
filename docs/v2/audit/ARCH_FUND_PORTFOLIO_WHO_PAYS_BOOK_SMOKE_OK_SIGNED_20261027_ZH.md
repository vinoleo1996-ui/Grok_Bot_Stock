# Arch fund who_pays Book-Smoke 独立窗 `.ok` 签发回执

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-27T22:31:37-04:00`（America/New_York） |
| 主令 | 主 22:26 ET · Eng BLOCKED_MISSING_AUTH 回执 **`9c4a8ad5` MATCH**（live fund `.ok`=0）→ **令 Arch 另签本窗独立 BS `.ok`**（钉 FROZEN **`303e0185`** / Arch **`bcbe4b72`** / 掩码 **`6ab6a305`**；禁 mid_large；禁混叶38；rss≤1500；**禁 QUIET**）；Eng 纸面待机；主 MATCH 后再令 Eng GO；叶38 旁线 `.ok` `794f6578` 不混；≠ACCEPT；leo_notify=false；live=false |
| FROZEN / RECEIPT / ArchFROZEN | `303e0185…` / `df153eb9…` / `bcbe4b72…` |
| 掩码 / 主变体 / 池 | `6ab6a305…` / **dark_horse_add** / **ALLA** |
| Eng BLOCKED | `9c4a8ad5…` |
| live / promotion_approved / leo_notify | **false** / **false** / **false** |

## 结论

**SIGNED** — fund who_pays **Book-Smoke** 独立窗 `ARCH_RUN_AUTH`（mechanism=`g1g5_ashare_fund_portfolio_v1` / ALLA `…_v1_allA`；主变体 **`dark_horse_add`**；PRIMARY 池 **ALLA_tradable**；**禁 mid_large 主口径**；rss=1500 禁抬；**禁 QUIET**；**禁混叶38** `794f6578`）已落盘。钉 FROZEN **`303e0185`** / RECEIPT **`df153eb9`** / ArchFROZEN **`bcbe4b72`** / DRAFT `7cfbb3e5` / ArchDRAFT `985564ee` / C1C2 `5f7ff5a6` / C2 链 `cb48e5d9`·`d6024472`·`81afda13` / WHO `547b246e` / ALLA `724e1df5` / 掩码 **`6ab6a305`** / Eng BLOCKED **`9c4a8ad5`** / AE `d96b83e1` / book_smoke.py `1a5fa1aa` **全 MATCH**。

- **book_smoke=true**；**x2=false**；**x2_accept=false**；**selfcheck=false**
- **≠ Book-Smoke ACCEPT**；**≠ X2 ACCEPT**；**≠ selfcheck**；**≠ 叶 alpha_build**
- **Arch 不代跑**（EXECUTED@签=false；book_smoke_executed_at_sign=false）
- **本拍未挂 QUIET**（`quiet_status_at_sign=ABSENT`；`ban_hang_quiet_this_sign=true`）
- 叶38 旁线 `.ok` **`794f6578` UNTOUCHED**（禁打开/消费/混）
- **请主 MATCH 本 `.ok` + 本 SIGNED 后再令 Eng GO** 真跑 Book-Smoke（须带 `--arch-ok-path` 本路径；X2 另令）

## 钉点 MATCH 表

| 件 | 期望 sha8 | 实测 | 结果 |
|---|---|---|---|
| FROZEN | `303e0185` | `303e01850ab2ed3966a823deb1b8ce07e43da2dbff901593134763e89b95f9e0` | **MATCH** |
| FROZEN_RECEIPT | `df153eb9` | `df153eb9964109bffe59fc5798d4e2c1bac9ee1205902b4e86ee46980d85c3b9` | **MATCH** |
| ArchFROZEN | `bcbe4b72` | `bcbe4b72c487c67cab7a69665e7df98a02d5c39fcb855590a94f3613684cfb92` | **MATCH** |
| DRAFT | `7cfbb3e5` | `7cfbb3e5c53446f403dd56341e5c680a41d7cc529a4bfec66b8ccc7661d2f8ec` | **MATCH** |
| ArchDRAFT | `985564ee` | `985564ee2a1c23a284cc1303bc9705ff68a9fe8a761216f0bfc82bdf5c63ba2d` | **MATCH** |
| C1C2 | `5f7ff5a6` | `5f7ff5a64287fd6d6cadde2a639eb75a6443d060a646e5827fc1bd8df5c79ce1` | **MATCH** |
| C2_RECEIPT | `cb48e5d9` | `cb48e5d957923be24ff5023e13f4d5203457261aecc6e6303023847f654f37d2` | **MATCH** |
| C2_JSON | `d6024472` | `d60244728d9c87630373dc0ede7e6548acb579bf0506c6493e49d7ecbcfad292` | **MATCH** |
| C2_events | `81afda13` | `81afda134adcf63af0b36d540c73a0aa71f0859682c45cda1a9647d32451be62` | **MATCH** |
| WHO | `547b246e` | `547b246e64de4a3c358e78bd4a95a187849da22e3cb8947e238633b498716f36` | **MATCH** |
| ALLA | `724e1df5` | `724e1df52c1e69a21dc6e9ae725000266845e77b44aff9604662fab663d35e06` | **MATCH** |
| mask | `6ab6a305` | `6ab6a305cb91db9a89c17a8db005d967679cfe4585a7fecad361e902a3daa114` | **MATCH** |
| Eng BLOCKED | `9c4a8ad5` | `9c4a8ad5cbf979d2b419e01eb18544eaf6a32e0629caaabf4d87b62f3ae55ac6` | **MATCH** |
| AE parquet | `d96b83e1` | `d96b83e12951bf53b76016927bd7417dae1a0e41f6c748a69860c710e52390f8` | **MATCH** |
| book_smoke.py | （记录） | `1a5fa1aa6ab847bd1ecda4d01bd4bda88b23535edceb91021520261be3e8251b` | **RECORDED** |
| 拟 .ok 签前 | ABSENT | ABSENT | **MATCH** |
| QUIET 签前/签后 | ABSENT | ABSENT / ABSENT | **MATCH** |
| 叶38 live `.ok` | `794f6578` 旁线未混 | `794f6578c26e2e8bf77fbc5528d1d11f1fe4388a575629108d8fee07c1233974` UNTOUCHED | **MATCH** |
| 窗期 | 约 90min + expires≈+4min | `2026-10-27T22:31:00-04:00` → `2026-10-28T00:01:00-04:00` / expires `2026-10-28T00:05:00-04:00`；签时 `2026-10-27T22:31:37-04:00` | **IN_WINDOW** |

## 钉

| 项 | 值 |
|---|---|
| `.ok` 路径 | `output/ai_factory/ARCH_RUN_AUTH_FUND_PORTFOLIO_WHO_PAYS_BOOK_SMOKE_DARK_HORSE_ADD.ok` |
| `.ok` sha8 / 全长 | `f08ce32c` / `f08ce32c5566030e48e941039f09ead5c4a7a4e8828f457ae2f15309cfe63817` |
| QUIET 路径 | `output/loop/RESEARCH_QUIET.lock` |
| QUIET 状态 | **ABSENT**（本拍**未挂**；`quiet_set_at_sign=false`；`ban_hang_quiet_this_sign=true`） |
| holder | `fund_portfolio_who_pays_book_smoke_dark_horse_add` |
| 主变体 / 池 | **dark_horse_add** / **ALLA_tradable**（禁 mid_large 主口径） |
| 掩码 | `research/all_a_universe_mask.py` = `6ab6a305cb91db9a89c17a8db005d967679cfe4585a7fecad361e902a3daa114` |
| book_smoke.py | `quantlab/portfolio/book_smoke.py` = `1a5fa1aa6ab847bd1ecda4d01bd4bda88b23535edceb91021520261be3e8251b` |
| 窗期 | `2026-10-27T22:31:00-04:00` → `2026-10-28T00:01:00-04:00`；expires `2026-10-28T00:05:00-04:00` |
| CLI 提示（占位·不执行） | `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python -m quantlab.portfolio.book_smoke --windows X2 --capitals 600000,1000000 --out output/ai_factory/_fund_portfolio_who_pays_book_smoke_dark_horse_add/<ET_TS>/ --arch-ok-path output/ai_factory/ARCH_RUN_AUTH_FUND_PORTFOLIO_WHO_PAYS_BOOK_SMOKE_DARK_HORSE_ADD.ok` |
| rss 软/硬帽 | **1500** MB；禁抬 |
| Book-Smoke / X2 ACCEPT / selfcheck / 叶38混 | **true(本窗)** / **false** / **false** / **禁** |
| EXECUTED@签 | **false** |

## QUIET / 旁线

| 项 | 值 |
|---|---|
| QUIET 本拍 | **未挂 = ABSENT** |
| ban_hang_quiet_this_sign | **true** |
| Arch 代跑 Book-Smoke | **未执行** |
| 叶38 `.ok` `794f6578` | **未打开 / 未消费 / 未混** |
| mid_large 主口径 | **false** |

## 下一跳

1. **主** MATCH 本 `.ok`（+ 本 SIGNED 回执）后令 **Eng GO** 真跑 Book-Smoke（须在 expires 前；须带本 `--arch-ok-path`；Arch **不代跑**）
2. X2 **另令**（本 `.ok`：`x2=false` / `neq_x2=true`）
3. ≠Book-Smoke ACCEPT；≠X2 ACCEPT；禁混叶38；禁挂 QUIET；禁抬 rss；live=false；leo_notify=false

live=false.


---
本回执路径：`docs/v2/audit/ARCH_FUND_PORTFOLIO_WHO_PAYS_BOOK_SMOKE_OK_SIGNED_20261027_ZH.md`
本回执（不含本行）sha256=`fe0a93838499e8c108cbdbf402baac0db5ef5ad5ce5a4aab72733371f900afdf` · sha8=`fe0a9383`
