# 叶25 step_m1 R5 — 新窗 .ok 签发回执（v4）

- 时刻（America/New_York）：2026-10-25T10:11:47-04:00
- 依据：主 P0 最终确认——VOID `7b279d47`（rc96 C5 FALSE_POSITIVE SELF_SAMPLER）后随即重签；采样只钉 `/tmp`
- live=false；promotion=false

## .ok

| 项 | 值 |
|---|---|
| 新路径 | `output/ai_factory/ARCH_RUN_AUTH_LEAF25_TTM_RECON_STEP_M1_R5_v4.ok` |
| sha256 | `1c32ab1e5ffb9eb3ddf466f15b0cd778a1579eaca678f2f5fbe1dd1ae00e66f0` |
| sha8 | `1c32ab1e` |
| cmd | `docs/v2/audit/leaf25_step_m1/LEAF25_STEP_M1_R5c_v4.cmd` sha `8231cf2df598716cce30343bc335c8bf645614058eeab9d691a6ef768c011052` |
| DIFF | `DIFF_cmd_R5c_v3_to_R5c_v4.diff` sha `66e1edfa693c5b23a69f2b241883eeee764ac181d4c8314fed5a0da83fca8e6c` |
| 窗 | **2026-10-25 11:15–12:00 ET**（expires 12:15 ET） |
| 旧 R5_v3 | VOID → `output/ai_factory/_consumed/ARCH_RUN_AUTH_LEAF25_TTM_RECON_STEP_M1_R5_v3.7b279d47.VOID.20261025T1011ET.ok`（sha `7b279d4731760de3c6b194b1d5d93e47acfc5607fa5d05f1defbd5dce07e31a7`） |
| 归档 | `docs/v2/audit/leaf25_step_m1/ARCH_LEAF25_STEP_M1_R5_RC96_C5_ARCHIVE_20261025_ZH.md` sha `3c12d335eb538b42467b758cfe31253e91015491c50f8a6fc8aae88590d665fe` |

## 硬钉

- 采样：**仅** `/tmp/leaf25_step_m1_r5_<ET_TS>_sampler_30s.txt`；禁 output*/log_dir
- `allow_c5_ignore=false`（不放宽整树 C5）
- AI：`ai_no_retry` / `ai_no_self_rerun`；禁复用 `7b279d47`
- 叶27 `27-ok-10-50` 不变；禁复用本叶25钉

## 给 AI

窗内用本 v4 `.ok` + `R5c_v4.cmd` 开跑；采样写 `/tmp`；**勿自重跑**；勿消费已 VOID 的 v3。
