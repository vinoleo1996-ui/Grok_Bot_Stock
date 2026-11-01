# 叶25 采样改写 /tmp DIFF 审阅（Arch PASS）

- written_et: 2026-10-25T10:13:00-04:00（America/New_York）
- by: QuantLab Arch
- verdict: **PASS**
- live: false
- promotion_approved: false

## 审对象

| 项 | 值 |
|---|---|
| DIFF | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_SAMPLER_TO_TMP_DIFF_20261025_ZH.md` |
| DIFF sha256 | `bcdf617e82e87e0386389ebc63c0cddcaebcffc2511726c0e509e5ab4b905261` |
| DIFF sha8 | `bcdf617e` |
| 范围 | **NO_REPO_CODE_CHANGE**（例程侧并行监控路径；不改 wrapper/脚本） |

## 核验

1. 回执/C5 根因与 DIFF §1 一致：pid 持有 `…_logs/sampler_30s.txt` → C5 fd 命中 `output/*`（wrapper `cmc_wrapper_v4` c5watch；wrapper sha `6174eacb…` MATCH）。
2. 写 `/tmp/...` 使 cwd/fd 两条均不命中 `data*`/`output*` —— **可避开且不放宽 C5**；`allow_c5_ignore=false` 维持。
3. 明确不做表（不改 R5c_v3 仓库语义、不 ignore output*、不自重跑）与主/Arch 裁定一致。
4. 验收条（开跑前 fd 抽查无 output 打开文件）可执行。

## 与已签新窗对齐

| 项 | 值 |
|---|---|
| 归档 | `ARCH_LEAF25_STEP_M1_R5_RC96_C5_ARCHIVE_20261025_ZH.md` sha `3c12d335eb538b42467b758cfe31253e91015491c50f8a6fc8aae88590d665fe` |
| VOID | `output/ai_factory/_consumed/ARCH_RUN_AUTH_LEAF25_TTM_RECON_STEP_M1_R5_v3.7b279d47.VOID.20261025T1011ET.ok` |
| 新 `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF25_TTM_RECON_STEP_M1_R5_v4.ok` sha `1c32ab1e5ffb9eb3ddf466f15b0cd778a1579eaca678f2f5fbe1dd1ae00e66f0` |
| 新 cmd | `LEAF25_STEP_M1_R5c_v4.cmd` sha `8231cf2df598716cce30343bc335c8bf645614058eeab9d691a6ef768c011052`（仅 `--arch-ok`→v4 + `/tmp` 硬钉注释；运行行同 v3） |
| 窗 | **2026-10-25 11:15–12:00 ET**（expires 12:15） |

硬钉：`sampler_out_required` 示例 `/tmp/leaf25_step_m1_r5_<ET_TS>_sampler_30s.txt`；亦可按本 DIFF 用 `/tmp/quantlab_leaf25_<ET_TS>/` 目录——**必须**全在 `/tmp` 下，**禁止**任何 `output/**`。两者均 PASS。

## 给 AI

1. **PASS**——可 UpdateRoutine：窗 11:15–12:00；并行监控只写 `/tmp/...`；开跑前 fd 抽查。
2. 开跑钉：`.ok` sha `1c32ab1e…` + `R5c_v4.cmd` `8231cf2d…`（**勿**再用 `7b279d47` / R5c_v3 作 arch-ok）。
3. **禁自重跑**；一次窗、no retry；叶27@10:50 禁复用叶25钉。

## 给主

VOID+归档+v4 已齐；DIFF PASS 钉 `bcdf617e…`。勿先开跑以外的叠仓。live=false。
