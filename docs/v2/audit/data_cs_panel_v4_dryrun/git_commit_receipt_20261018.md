# git 提交回执 · SD1 r6c fix_sd1 + 两份方案（ARCH v4a pin）

- 时间：2026-10-18 05:12:13 EDT（America/New_York）；执行人：QuantLab Data；没有运行任何项目代码；live=false，promotion=false
- commit：`b9674c8b88bd44702067094bbda68243983284ac`（main）
- parent（提交前 HEAD）：`f8e64decd068252cb8d3d17d9eaec2070f811cc1`，即「alpha: CMC/s8 v1.1 r3 + runguard + selftest (Arch r3 bbfcb7ef)」，2026-10-18 03:39:40 EDT
- 提交信息：`SD1 r6c: fix_sd1 scripts + plans pinned by ARCH v4a (dry-run passed, D3D4 review 9ee8e9d9)`
- 方式：先 `git add -- <7 个路径>`，再用 `git commit -m ... -- <7 个路径>` 限定提交范围。没有用 --no-verify、--amend 或 push。

## 提交前状态
- 暂存区为空，没有预先暂存的改动。
- 工作区另有大量 ` M`（docs/、logs/、output/ 等），都是其他 agent 的未提交改动。本次没有暂存，提交后保持原样。
- 7 个路径提交前都是未跟踪状态（`??`），之前没有提交过，git log 中也没有它们的记录。两份方案文档因此是首次提交，满足"之前未以相同内容提交"的条件。
- scripts/fix_sd1/ 目录里只有这 5 个 .py 文件，没有其他文件，也没有 __pycache__ 或 *.pyc。它们正好是 v4a.ok pin 的 5 个脚本：common_sha256、script_stock_delisted_sha256、script_cs_panel_sha256、script_suspend_flags_sha256、test_sd1_common_sha256。
- 没有 git remote（`git remote -v` 为空），所以没有推送，也无从推送。.git/hooks 中只有 sample 文件，没有自定义 hook。

## 三处 sha 核对
- 归档的 v4a.ok：`output/data/_consumed/ARCH_RUN_AUTH_CS_PANEL_RESUMEFIX_v4a.d5c326df_CONSUMED_20261018_0510ET.ok`，sha256=d5c326dfd6b69393b5555747ba63e85271b14930bc0a1870061291c3b0b1ede5 ✓
- 下表中三处分别是：工作区 sha256、`git show b9674c8:<path> | sha256sum`、v4a.ok 中的 pin。

| 文件 | .ok 键 | 工作区 sha256 | git blob（git show） sha256 | v4a.ok pin | 一致 |
|---|---|---|---|---|---|
| scripts/fix_sd1/sd1_common.py | common_sha256 | 542dd13650979983f926778d5c7ea39a6f6e7655c2ac40ed1823601eb45ba4b9 | 542dd13650979983f926778d5c7ea39a6f6e7655c2ac40ed1823601eb45ba4b9 | 542dd13650979983f926778d5c7ea39a6f6e7655c2ac40ed1823601eb45ba4b9 | ✓ |
| scripts/fix_sd1/build_stock_delisted_v2.py | script_stock_delisted_sha256 | 34e4689929bc02a42fabdb1642b46e511c61717986179a46c8029d18b2730ba5 | 34e4689929bc02a42fabdb1642b46e511c61717986179a46c8029d18b2730ba5 | 34e4689929bc02a42fabdb1642b46e511c61717986179a46c8029d18b2730ba5 | ✓ |
| scripts/fix_sd1/build_cs_panel_v2_resumefix.py | script_cs_panel_sha256 | 6e2e127393fed6f089c69041d18e0e4181794de11e63c6174c31a0719e47de27 | 6e2e127393fed6f089c69041d18e0e4181794de11e63c6174c31a0719e47de27 | 6e2e127393fed6f089c69041d18e0e4181794de11e63c6174c31a0719e47de27 | ✓ |
| scripts/fix_sd1/build_suspend_flags_v2.py | script_suspend_flags_sha256 | 6b8fd0330b7aa00eccb91a41d6d9da29eaf1eb096abfe12c314f759ac5baaa30 | 6b8fd0330b7aa00eccb91a41d6d9da29eaf1eb096abfe12c314f759ac5baaa30 | 6b8fd0330b7aa00eccb91a41d6d9da29eaf1eb096abfe12c314f759ac5baaa30 | ✓ |
| scripts/fix_sd1/test_sd1_common.py | test_sd1_common_sha256 | 7dbcf5d38e2874c1ccf53614cdae94826b51560056c904e77f4d418d2fcec325 | 7dbcf5d38e2874c1ccf53614cdae94826b51560056c904e77f4d418d2fcec325 | 7dbcf5d38e2874c1ccf53614cdae94826b51560056c904e77f4d418d2fcec325 | ✓ |
| docs/v2/DATA_SUSPEND_DELIST_FIX_PLAN_ZH.md | plan_sd_fix_sha256 | 903e64ef439415c4e7b158e8151985fc309ef288a2f39ec322fc1a66707b89e3 | 903e64ef439415c4e7b158e8151985fc309ef288a2f39ec322fc1a66707b89e3 | 903e64ef439415c4e7b158e8151985fc309ef288a2f39ec322fc1a66707b89e3 | ✓ |
| docs/v2/DATA_CS_PANEL_RESUME_REBUILD_PLAN_ZH.md | plan_cs_panel_sha256 | 362e323994d3e40181ee2f26da3864c5fdf4720c0b1f1a5e35b095652eec3bbe | 362e323994d3e40181ee2f26da3864c5fdf4720c0b1f1a5e35b095652eec3bbe | 362e323994d3e40181ee2f26da3864c5fdf4720c0b1f1a5e35b095652eec3bbe | ✓ |

结果：7/7 三处一致 ✓

## git show --stat
```
commit b9674c8b88bd44702067094bbda68243983284ac
parent f8e64decd068252cb8d3d17d9eaec2070f811cc1
Author: QuantLab <leo@quantlab.local>
Date: 2026-10-18 05:12:13 -0400

    SD1 r6c: fix_sd1 scripts + plans pinned by ARCH v4a (dry-run passed, D3D4 review 9ee8e9d9)

 docs/v2/DATA_CS_PANEL_RESUME_REBUILD_PLAN_ZH.md | 158 ++++++++++
 docs/v2/DATA_SUSPEND_DELIST_FIX_PLAN_ZH.md      | 153 ++++++++++
 scripts/fix_sd1/build_cs_panel_v2_resumefix.py  | 193 ++++++++++++
 scripts/fix_sd1/build_stock_delisted_v2.py      | 149 +++++++++
 scripts/fix_sd1/build_suspend_flags_v2.py       | 128 ++++++++
 scripts/fix_sd1/sd1_common.py                   | 385 ++++++++++++++++++++++++
 scripts/fix_sd1/test_sd1_common.py              | 117 +++++++
 7 files changed, 1283 insertions(+)
```

## 提交后核对
- 提交只包含上面 7 个文件（1283 行新增），没有其他文件。
- 提交中 __pycache__ 或 *.pyc 的数量为 0；git ls-files 中 fix_sd1 下的 __pycache__ 或 *.pyc 数量为 0 ✓
- 提交后暂存区为空，7 个路径在工作区干净，没有未提交差异。
- 未做：没有运行任何项目代码；没有 execute；没有动 94322 和补数队列；没有 push；没有发消息。
