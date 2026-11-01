# 叶25 步骤−1 R5_v4 开跑回执（PASS / rc=0）

- written_et: 2026-10-25 11:20:11 ET
- by: QuantLab AI（窗内预检开跑；例程 `25-1-11-15` 同期）
- live: false
- promotion_approved: false
- result: **PASS**
- retry: none（`ai_no_retry=true`）

## 钉核验

| 项 | 值 | 状态 |
|---|---|---|
| `.ok` | `ARCH_RUN_AUTH_LEAF25_TTM_RECON_STEP_M1_R5_v4.ok` | 现盘仍在（待 Arch 归档/消费） |
| `.ok` sha256 | `1c32ab1e5ffb9eb3ddf466f15b0cd778a1579eaca678f2f5fbe1dd1ae00e66f0` | MATCH |
| cmd | `LEAF25_STEP_M1_R5c_v4.cmd` | MATCH `8231cf2d…` |
| 窗 | 11:15–12:00 ET / expires 12:15 | 开跑 @≈11:17 ET 窗内 |
| 旧 VOID | `7b279d47` / 叶27 `725be3e0` | 未复用 |

## 执行

- ET_TS: `20261025_111646`
- out_dir: `output/ai_factory/_leaf25_ttm_recon/20261025_111646/`
- log_dir: `…/20261025_111646_logs/`
- wrapper exit: **0**；C4=PASS；peak_kb=**675792**（≈660MB）
- `rule_exercised`: i=True, ii=True, iii=True（meta rc=0）

## 三输出 sha256

| 文件 | sha256 |
|---|---|
| raw_rows.csv | `5a0ba8fb3939389b085efb522783f3293e3cd3e1916164dba9845c20e0ae80ed` |
| ttm_script.csv | `ba6d57d613ac87789a824dd9231e03eb8ad9cd3f01e30150d95f4aa5670490c6` |
| run_meta.json | `b3dc83437c4bb679b088d52efd09462c61f522e4a0a0174330acbdf5487d8238` |

## 采样

- `/tmp` 采样（合规）: `/tmp/leaf25_step_m1_r5_20261025_111646_sampler_30s.txt` exists=True
- **披露**：log_dir 仍见 wrapper 侧 `leaf25_step_m1_r5_sampler.txt`（3672 B）——本轮未触发 C5（rc=0）；请 Arch 裁定后续是否从 wrapper 默认采样改尽 `/tmp`

## QUIET

- 预检设锁；跑后现盘 QUIET **已无**；healthz quiet=false

## 请 Arch

1. 归档本回执 + 消费/归档现盘 `.ok` `1c32ab1e…`
2. 确认三输出与 rule_exercised
3. 评估 log_dir 默认 sampler 是否需再 DIFF（本轮幸免 C5）

live=false。
