# 说明：本目录为未授权运行的产物（只作证据保留）
- 作者：QuantLab Strategy，2026-10-18 ET。按 Arch 裁定：本目录原地保留作证据，不删、不挪，已有文件不改；本文件和 READ_LOG_20261018.md 是后来新增的。
1. 本次运行没有 Arch .ok：统计脚本 sw_lookahead_count.py 在 2026-10-18 07:03:37–07:04:11 和 07:04:39–07:05:13 ET 跑了两次；同期还有其他直接读真实数据的命令，见 READ_LOG_20261018.md。这些都没有 Arch 签的只读 .ok。
2. 时间可能和已作废的叶 23 第一次运行（07:04–07:06 ET）重叠：上面第二次运行（07:04:39–07:05:13）落在这个区间内，第一次运行（到 07:04:11）与其起点相邻。
3. RESULT.md、result.json、synth_mismatch_rows.csv 里的数字不作为任何结论或输入使用。重跑要等叶 24 之后 Arch 签只读 .ok，在新目录里进行。

## 本目录文件 sha256（不含本文件；都是文档或产物，不是真实数据）
| 文件 | sha256 |
|---|---|
| READ_LOG_20261018.md | 2571956ef3015544a54a2e5da0252d2d5ff41c613104c685f2e9e4de11516d2a |
| RESULT.md | d63525aad852494b9d6dca4a5dcca3f1f4cf8c0fe2438cc2e79a71a45f7291df |
| SHA256SUMS | f1d06711120ead2a1296a31e9a79fd00fd465eb48b7e82a1e590867541da5fd3 |
| result.json | 1ae8cee97d4a632b51f841835395f6e87dce602832ae9eb5d43257ad7ed56a97 |
| run.log | b466a7c3678b2d66df5ab0ef98908cec22425a13f90b485b6f71fba5f4dba1e7 |
| sw_lookahead_count.py | f6ed68edeff8c4b6773ded2659e6513ec88c4d55651a52de35c67fb4aa68ea9e |
| synth_mismatch_rows.csv | de981e078a215de1ee1148aa15544da19a8800bfb33eb5c03b9cc8813efcc1a5 |

本文件自身的 sha256 无法写在文件里，见 Strategy 的报回。
