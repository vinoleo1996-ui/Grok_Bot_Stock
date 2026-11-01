# 叶25 R5_v3 — cmd 重钉回执（R5c_v3）

- 时刻（America/New_York）：2026-10-25T04:42:31-04:00
- 依据：AI 钉冲突；主 P0 04:40；裁示 **(1) 重钉 cmd→R5c_v3**
- live=false

## 结论

同路径重签 `ARCH_RUN_AUTH_LEAF25_TTM_RECON_STEP_M1_R5_v3.ok`（保持 AI `R5c_v3.cmd` 的 `--arch-ok` 指向）：

| 项 | 值 |
|---|---|
| .ok 路径 | `output/ai_factory/ARCH_RUN_AUTH_LEAF25_TTM_RECON_STEP_M1_R5_v3.ok` |
| .ok sha256 | `7b279d4731760de3c6b194b1d5d93e47acfc5607fa5d05f1defbd5dce07e31a7` |
| .ok sha8 | `7b279d47` |
| cmd_path | `docs/v2/audit/leaf25_step_m1/LEAF25_STEP_M1_R5c_v3.cmd` |
| cmd_sha256 | `be7f5e5a48af13f0dfe30e1363709a697331521c5fae3abd6b28e31a8819b268` |
| DIFF | `22be3d068448488671d6cf7236d5dcd1782d16087e820f88434f05c4c80a7684` |
| 窗 | 2026-10-25 10:00–10:45 ET（expires 11:00） |
| 前版 v3 | SUPERSEDED_CMDPIN → `output/ai_factory/_consumed/ARCH_RUN_AUTH_LEAF25_TTM_RECON_STEP_M1_R5_v3.8c77420a.SUPERSEDED_CMDPIN.20261025T044231ET.ok`（sha `8c77420ab965cdceb95e563863fb23baa946cbbe5db342e2a9b2f4b4f4318b05`） |

## 给 AI

用本 .ok + `LEAF25_STEP_M1_R5c_v3.cmd` 开跑；勿用 R5c_v2.cmd / 旧 8c77420a 内容。例程可解暂停。
