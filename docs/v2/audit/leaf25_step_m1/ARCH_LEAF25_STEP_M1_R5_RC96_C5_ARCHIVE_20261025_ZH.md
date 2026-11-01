# 叶25 步骤−1 R5 rc=96（C5）归档 + 重签新窗（Arch）

- written_et: 2026-10-25T10:11:47-04:00（America/New_York）
- by: QuantLab Arch
- live: false
- promotion_approved: false

## 1. 结论（裁定）

1. **根因**：C5 **FALSE_POSITIVE / SELF_SAMPLER**——AI 例程并行 30s 采样器写 `output/ai_factory/_leaf25_ttm_recon/20261025_100250_logs/sampler_30s.txt`，被 wrapper C5 判为他进程持有 `output*` fd，误杀研究组 → **rc=96**。非 web readers / 非 94322 / 非第二研究进程。C4=PASS（peak_kb=379092）。
2. **旧窗闭合**：FAIL + VOID；**禁止**把旧 `.ok` 记为 SUCCESS。
3. **本窗不授权重试**（旧 10:00–10:45 已尽；例程 no retry）。
4. **主 P0 覆盖后随即重签新窗**：**2026-10-25 11:15–12:00 ET**（expires 12:15 ET）；采样**只钉 `/tmp`**；`allow_c5_ignore=false`（不放宽整树 C5）。
5. **AI 禁自重跑**（须等本新 `.ok`；禁复用 `7b279d47`）。

## 2. 回执与证据钉

| 项 | 路径 / 值 | sha256 |
|---|---|---|
| AI 回执 | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_STEP_M1_R5_RUN_RECEIPT_20261025_ZH.md` | `af961f32d75c33e42f798aea9f3215326cb341feafb28498fb9fc2a701bdaf2b` |
| C5 摘要 | `output/ai_factory/_leaf25_ttm_recon/20261025_100250_logs/leaf25_step_m1_r5_c5.txt` | `1cc01a013518b291467a22954bf56ac1d378eaac10947e6eb8f2d9ea2b958ce5` |
| exit 摘要 | `output/ai_factory/_leaf25_ttm_recon/20261025_100250_logs/leaf25_step_m1_r5_exit.txt` | `583ba19ee142438bfdd0650787d1e9c9d8e09398c60390d38a47e03f7591a929` |
| sampler_30s | `output/ai_factory/_leaf25_ttm_recon/20261025_100250_logs/sampler_30s.txt` | `25cb1ff07a4e1637ddc707c9a223113cc2d8dd127279672496111c82367c1354` |
| wrapper sampler | `…/leaf25_step_m1_r5_sampler.txt` | `3452d7c8f5aaaf3c4130cf0048586b1329982be18c4337659066d0e5f43e0294` |
| void 目录 | `output/ai_factory/_void/leaf25_step_m1_r5_rc96_20261025_100256/` | 存在（目录标记；产物在 log_dir） |
| log_dir | `output/ai_factory/_leaf25_ttm_recon/20261025_100250_logs/` | ET_TS=`20261025_100250` |
| out_dir | `output/ai_factory/_leaf25_ttm_recon/20261025_100250/` | **空**（无三输出；无 rule_exercised） |
| preflight | `output/ai_factory/_leaf25_ttm_recon/preflight_20261025_100108/` | 静默门禁 PASS |
| C5_HIT | pid=530984 fd=`…/sampler_30s.txt`；SAMPLER_PID=530984（launch.txt） | — |
| 旧 cmd | `LEAF25_STEP_M1_R5c_v3.cmd` | `be7f5e5a48af13f0dfe30e1363709a697331521c5fae3abd6b28e31a8819b268` |

## 3. `.ok` 处置（VOID，非 SUCCESS）

| 项 | 值 |
|---|---|
| 移前路径 | `output/ai_factory/ARCH_RUN_AUTH_LEAF25_TTM_RECON_STEP_M1_R5_v3.ok` |
| 移前 sha256 | `7b279d4731760de3c6b194b1d5d93e47acfc5607fa5d05f1defbd5dce07e31a7`（MATCH） |
| VOID 后路径 | `output/ai_factory/_consumed/ARCH_RUN_AUTH_LEAF25_TTM_RECON_STEP_M1_R5_v3.7b279d47.VOID.20261025T1011ET.ok` |
| VOID 后 sha256 | `7b279d4731760de3c6b194b1d5d93e47acfc5607fa5d05f1defbd5dce07e31a7`（同内容） |
| 消费语义 | **VOID / FAIL**；**非** CONSUMED-SUCCESS |

## 4. 重签（主 P0 最终确认）

| 项 | 值 |
|---|---|
| 新 `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF25_TTM_RECON_STEP_M1_R5_v4.ok` |
| 新 `.ok` sha256 | `1c32ab1e5ffb9eb3ddf466f15b0cd778a1579eaca678f2f5fbe1dd1ae00e66f0` |
| 新 cmd | `docs/v2/audit/leaf25_step_m1/LEAF25_STEP_M1_R5c_v4.cmd` |
| 新 cmd sha256 | `8231cf2df598716cce30343bc335c8bf645614058eeab9d691a6ef768c011052` |
| DIFF | `docs/v2/audit/leaf25_step_m1/DIFF_cmd_R5c_v3_to_R5c_v4.diff` sha `66e1edfa693c5b23a69f2b241883eeee764ac181d4c8314fed5a0da83fca8e6c` |
| 窗 | **2026-10-25 11:15–12:00 ET**（not_before=11:15；expires=12:15 ET） |
| 采样钉 | **仅** `/tmp/leaf25_step_m1_r5_<ET_TS>_sampler_30s.txt`；禁写 output*/log_dir/out_dir |
| C5 | `allow_c5_ignore=false`（不接受放宽整树 output*） |
| AI | `ai_no_retry=true`；`ai_no_self_rerun=true`；须等本新 `.ok`；禁复用 `7b279d47` 文件/sha |
| signed_et | `2026-10-25T10:11:47-04:00`（系统钟） |

## 5. 对叶27 / 叶26 影响

- 叶25 本次尝试已闭合（FAIL+VOID）后，**例程 `27-ok-10-50` 仍按 ≥10:50 ET 执行**；签前复测 Data `acb8d3e0` + AI `63185c9f` + 盘面；**禁复用叶25钉**（含本 v4）。
- 叶26 FROZEN 仍等主裁：**叶25 FAIL 已归档，FROZEN 时机仍听主**（叶25 未成功完成）。
- 补跑仍 SUSPEND；live=false。

## 6. 给 AI（开跑前必读）

1. 只用本归档第 4 节的 **R5_v4.ok + R5c_v4.cmd**；勿碰 VOID `7b279d47`。
2. 并行采样**必须**写 `/tmp/…`；写回 log_dir 将再次触发 C5。
3. **禁止自重跑**；窗外 / 无新 Arch `.ok` 不得再启。
4. 静默门禁与旧窗相同；rc=96/124 = fail、no retry。

live=false。
