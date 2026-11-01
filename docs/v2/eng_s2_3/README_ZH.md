# S2-3 exec_layer 00:48:19 ET 改动 —— 交 Arch 补审（P1-1；主 Agent 判 VOID_PENDING_DIFF）

编写：QuantLab Eng，2026-10-18 01:2x ET。只读整理，没有运行任何 runner。

| 文件 | sha256 | 性质 |
|---|---|---|
| `s2_3_exec_layer.a_pre0048_RECONSTRUCTED.py.txt` | 059cf43e4322fda69cab5a2ebddca91bcb7ed636b50005ee698075be2b7a93e5 | 改前版本（放行 .ok 00:47:18 ET 时的状态），**重建件**：把 00:48:19 的三处字符串替换逐一反做得到；没有备份、git 或哈希能独立核对 |
| `s2_3_exec_layer.b_ran_004852.py.txt` | **3d4b08e31973ad58254714fdfdf699290d7995da4c9461bd48ea13df9d5b2bf4** | 00:48:52–00:49:04 ET 正式运行所用的代码，**逐位核实**：与 v1_3_RUN_MANIFEST.json（00:51:04 ET）记的 code sha 一致；由现行文件去掉 runner-pin 3 处改动得到，sha 完全一致 |
| `s2_3_exec_layer_diff_0048.patch` | 653dc8e01828…（见 SHA256SUMS） | a→b 的 diff。已验证：把 patch 打到 a 上得到的文件 sha 恰为 3d4b08e3… |
| `s2_3_exec_layer_pin_delta_post0048.diff` | 见 SHA256SUMS | b→现行文件（847806e9…）的差异：只加了 ok_runner_pin（P1-1 之后的改动，非运行时代码） |

改动范围（a→b）：只动了输入守卫和 meta（新增 `--weights-ok` 权重 sha 校验、release .ok 文档哈希校验、meta 里 2 个字段）。整手程序、带、HARD 复核、换手、成本、汇总代码都没有改。

状态：四个正式运行目录的 S2-3 数字一律 **VOID_PENDING_DIFF**（每个目录里都有 VOID_PENDING_DIFF.md，sha 5a5577d6…），Arch 补审之前不进入任何结论。live=false，promotion=false。
