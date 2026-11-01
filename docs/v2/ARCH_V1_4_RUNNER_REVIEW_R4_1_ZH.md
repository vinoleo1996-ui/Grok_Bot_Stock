# Arch 复审补记 R4.1：P1-1 修复核对与 selftest .ok 签发

- 时间：2026-10-18 03:04 ET；接续 docs/v2/ARCH_V1_4_RUNNER_REVIEW_R3_R4_ZH.md（f2edc099）
- 本次操作：只读、sha256sum、git diff，读 ok_runner_pin 源码和 T 的门控源码。未执行任何项目代码。

## 1. 核对

- **commit a123a52f（父提交 336acd0f）改动 3 个文件：** T、research/_runner_archive/MANIFEST.md（+2 行）、快照 test_v14_synthetic.d281916d….py。
  - 065cf63e..a123a52f 区间里多出的 STRATEGY_V1_4_r4_vs_ce45f3da.diff 来自 336acd0f，不是这次的改动。
- **T 的 diff 只有一行，** 在 DEPS 中新增 `"d21": ROOT / "research/optimizer_core_v1_3_basisC_recalc_d21.py",`。新 T 的 sha 为 f1c1a89f…a7b，与申报一致。
- **快照 sha 为 d281916d…d9d9，** 与旧 T 一致。
- **以下文件均未改动：** R c844dbb4、D21 497f9a2b、E 09dc431d、V b500c21b、C 875daca9、ok_runner_pin c7805d9a。
- **P1-1 已关闭。**
- **新增 P3-7：** V（research/optimizer_core_v1_1.py）在 git 中仍是未跟踪文件。它的字节已由 sha 钉住，所以不影响本次签发；建议由文件归属方提交入库。

## 2. 签发

- 旧 .ok 33ef1df9 已归档为 output/strategy_optimizer/core_x2/_superseded/ARCH_RUN_AUTH_SELFTEST_v1_4.33ef1df9.ok。
- 新 .ok 写在 output/strategy_optimizer/core_x2/ARCH_RUN_AUTH_SELFTEST_v1_4.ok，共 27 个键。键集与旧版相同，另加 dep_sha256_d21。
- 格式按 ok_runner_pin.parse_ok/enforce 和 T 的 _selftest_selfcheck 核对：
  - 无 BOM，LF 行尾，不含行内注释，无重复键；
  - 6 个 dep 与 runner 的 pin 均按实测 sha 填写；
  - 除 allow_selftest=true 外，所有 allow_* 显式为 false；
  - live=false，promotion=false，out_dir=mkdtemp；
  - expires_et=2026-10-19T03:00:00-04:00。
- 本 .ok 只授权运行一次 T，串行，nice 10，RSS ≤1.5GB。
- v1.4 和 D21 的运行 .ok 不签，等 Leo 决定 Core 去留。
