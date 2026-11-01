# AI 回执：叶33 A1 只读 `n_unlock_pool` 诊断探针票已落（禁 execute）

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI |
| 时刻 | **2026-10-27 08:05 ET**（America/New_York；ISO `2026-10-27T08:05:28-04:00`） |
| 主令 | ~07:56 ET；Arch审 **`29166bf7` PASS_WITH_CONDITIONS MATCH** → 出 A1 只读诊断票 |
| **结论** | **A1_DIAG_DRAFT_WRITTEN**；正式脚本 **`afbbe7e7` UNCHANGED**；诊断脚本 **`083d09fe`**；**未**实跑；**未**降 gate；**未**复跑 X2；**未**申 `.ok`；**未**挂 QUIET；**未**自决 θ |
| EXECUTED | **false** |
| ≠X2 ACCEPT | **true** |
| θ | **未自决**（∈0.5–0.8 等主钉） |

## 0. 一句话

A1 诊断三件 + 另票脚本齐：dry PASS；正式脚本未动；`n_alpha` 只读旁证已附；`n_unlock_pool`/`ratio` 待另窗签后跑。交主→Arch **只审**。live=false。

## 1. 产出钉

| 件 | 路径 | sha256（全长） | sha8 |
|---|---|---|---|
| DRAFT | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_N_UNLOCK_POOL_DIAG_DRAFT_20261027_ZH.md` | `6a22123dae4a36b5bc21e25a9f92091ccc0d297c50842b46dc6cbcabc3a557be` | **`6a22123d`** |
| COVER | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_N_UNLOCK_POOL_DIAG_COVER_20261027_ZH.md` | `92262b709f5a9244618b8d0c5f73ec242432bdf94871db568ca2cf6e08d79607` | **`92262b70`** |
| RECEIPT | 本文件 | （本文件自哈希见 `/tmp/leaf33_a1_diag_sha8s.json`） | （见 json） |
| 诊断脚本 | `research/leaf33_n_unlock_pool_diag_probe_v1.py` | `083d09feaf5cca609b8d18657685c8d42c0e75295af18532807ea7fb4ab6a746` | **`083d09fe`** |
| 正式脚本（UNCHANGED） | `research/leaf33_share_unlock_pressure_resid_alpha_build.py` | `afbbe7e7292c17399bbf4733d9f34a922e6d81f1a914a60d24dc61fcba86cbc9` | **`afbbe7e7`** |
| Arch复议审（只读） | `…COVERAGE_SPARSE_RECON_REVIEW…` | — | **`29166bf7`** |
| 复议 DRAFT（只读） | `…COVERAGE_SPARSE_RECON_DRAFT…` | — | **`b84496fe`** |
| Arch VOID / RUN | — | — | **`6826c01d`** / **`a1b426f5`** |
| alpha / overlap / run_meta | out `20261027_072135/` | — | **`ea17e173`** / **`473b339e`** / **`f4702783`** |
| FROZEN / PIN / FROZEN审 | — | — | **`8ed43721`** / **`4e17ccfc`** / **`bf5234a9`** |

## 2. MATCH 钉（自检）

| 钉 | 期望 | 实测 |
|---|---|---|
| Arch复议审 | `29166bf7` | **MATCH** |
| 复议 DRAFT/COVER/RECEIPT | `b84496fe`/`4e6a1921`/`ab61885e` | **MATCH** |
| VOID / RUN | `6826c01d` / `a1b426f5` | **MATCH** |
| alpha / overlap / run_meta | `ea17e173` / `473b339e` / `f4702783` | **MATCH** |
| 正式脚本 | `afbbe7e7` UNCHANGED | **MATCH** |
| FROZEN / PIN / FROZEN审 | `8ed43721` / `4e17ccfc` / `bf5234a9` | **MATCH** |
| live `.ok` | 0 | **MATCH** |
| QUIET | ABSENT | **MATCH** |
| dry-compile / dry-run | PASS | **PASS** |
| 真跑门（无 ok） | exit 2 | **PASS** |
| EXECUTED | false | **MATCH** |

## 3. 未执行声明（硬）

- **未**改正式脚本字节（仍 `afbbe7e7`）
- **未**改 `COVERAGE_MEDIAN_HILIQ` / `COVERAGE_MEDIAN_FULLA` / `PRESSURE_MIN_VALID`
- **未**带 `--allow-real-data` 真跑；**未**读 share_float/行情算 `n_unlock_pool`
- **未**复跑 X2；**未**自申任何 `.ok`；**未**挂/抬 QUIET
- **未** RESTORED `245df63f` / `c5ed13df` / `5774bb6e`+票
- **未**自决 θ；**未**声称 X2 ACCEPT
- `live=false`；**不推 Leo**；**ok_requested=false**

## 4. 只读旁证摘要

- `n_alpha`（run_meta `coverage_rebal.n`）：n=30；median=**30.0**；p10≈**16.9**；p90≈**47.6**；min=**15**；max=**72**
- 与 alpha `ea17e173` 交叉验证：**0 mismatch**
- `n_unlock_pool` / `ratio`：**待签窗后跑**

## 5. 下一跳（请主）

```
主收本票 → Arch 只审
  → 主决定是否另排新 .ok 签窗跑诊断探针（禁 RESTORED）
      → 分布齐后主钉 θ / 是否另窗 FROZEN
```

可附 Arch FYI。≠X2 ACCEPT。**leo_notify=false**。live=false。**EXECUTED=false**。

## 6. hand-off

- sha8 清单：`/tmp/leaf33_a1_diag_sha8s.json`
- 交主短文：`/tmp/leaf33_a1_diag_done_to_main.md`
- SendToAgent 载荷：`/tmp/leaf33_a1_diag_sendtoagent_handoff.json`
