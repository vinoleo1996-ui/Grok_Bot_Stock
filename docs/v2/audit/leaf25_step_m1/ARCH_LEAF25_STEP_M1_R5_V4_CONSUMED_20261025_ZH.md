# Arch 叶25 步骤−1 R5_v4 消费归档（PASS）2026-10-25

- 角色：QuantLab Arch
- 时刻（America/New_York）：2026-10-25T11:22:41-04:00
- live=false；promotion_approved=false

## 结论

**CONSUMED_PASS** — AI 回执 MATCH；三输出 sha MATCH；rule_exercised i/ii/iii 全 True；`.ok` `1c32ab1e` 已迁 `_consumed`。

## 核验

| 项 | 值 | 判定 |
|---|---|---|
| AI 回执 | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_STEP_M1_R5_V4_RUN_RECEIPT_20261025_ZH.md` | sha `2bf4745d…` **MATCH** |
| `.ok` 内容 sha | `1c32ab1e5ffb9eb3ddf466f15b0cd778a1579eaca678f2f5fbe1dd1ae00e66f0` | MATCH |
| cmd | `LEAF25_STEP_M1_R5c_v4.cmd` | sha `8231cf2d…` MATCH |
| out_dir | `output/ai_factory/_leaf25_ttm_recon/20261025_111646/` | |
| raw_rows.csv | `5a0ba8fb…` | MATCH |
| ttm_script.csv | `ba6d57d6…` | MATCH |
| run_meta.json | `b3dc8343…` | MATCH；rc=0；peak_rss_kb=675792；rule_exercised 三 True |
| `/tmp` 采样 | `/tmp/leaf25_step_m1_r5_20261025_111646_sampler_30s.txt` | 有 |
| 进程/QUIET | 空 / 无锁 | 消费时 CLEAR |

## 归档路径

`output/ai_factory/_consumed/ARCH_RUN_AUTH_LEAF25_TTM_RECON_STEP_M1_R5_v4.1c32ab1e.CONSUMED.20261025T1122ET.ok`

## 开放（不挡本消费）

**P2-sampler-wrapper**：log_dir 仍有 wrapper 默认 `leaf25_step_m1_r5_sampler.txt`（3672 B）；本轮未 C5。后续须 DIFF 把默认采样改尽 `/tmp`（与 v4 钉一致），再送 Arch 审。

## 非动作

- 禁 AI 自重试本窗
- 不晋级；live=false
- 叶27 另窗仍等降内存包

live=false。
