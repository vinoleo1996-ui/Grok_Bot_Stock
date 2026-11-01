# 叶25 全叶因子 · X2 轨 cmd 草案（未授权）

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI（执行器） |
| 起草 | 2026-10-25T11:48:03-0400（America/New_York；墙钟 `2026-10-25 11:48:03 EDT`） |
| 状态 | **DRAFT**（**未授权实跑** · **不是 `.ok`** · **不替代 Arch 签发**） |
| live | **false** · promotion_approved **false** |
| 拟窗（主排） | **今日 14:30–16:00 ET**（America/New_York）；**须** Arch 新 X2 `.ok` 且入窗；**叶27 12:30–13:30 优先，勿抢** |
| 本回合非动作 | **不申 `.ok`** · **不实跑** · **不读真实行情大表** · **不 git commit** |

---

## 1. 钉表（全长）

| 件 | 路径 / 值 | sha256 |
|---|---|---|
| r6 FROZEN 戳记 | `docs/v2/AI_LEAF25_FULL_FACTOR_PREREG_r6_FROZEN_20261025_ZH.md` | `4bb1ff2b805f441499607ada5f871044e72e6176a66052c73b64816130d199e2` |
| r6 冻结正文（基盘 DRAFT） | `docs/v2/AI_LEAF25_FULL_FACTOR_PREREG_r6_DRAFT_20261025_ZH.md` | `e8ca2bcc1136b473bdc77f3f655e77f35404990068e9e30ac0c1cd9ed721292c` |
| 主令 | `docs/v2/audit/MAIN_LEAF25_R6_FROZEN_ORDER_20261025_ZH.md` | （主令 11:44 ET；以盘为准） |
| MEM/分块 | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_FULL_FACTOR_MEM_ESTIMATE_CHUNK_20261025_ZH.md` | `103717df1f9e5d63f8c681f16da091f44801e1b69b219ae1a18b2159446145d1`（**待 Arch 审**；未审不得签 `.ok`） |
| P2 Arch PASS | `docs/v2/…` / 审阅文 | `964cf57be56e8723fcff79ba620c5034e18b6e0fe083f59bef939e5db4705f78` |
| P2 DIFF | sampler→`/tmp` | `9584723f8dcce3907c797fd3b50d15576491a1f3898690b75c97fd707337fa38` |
| **wrapper v5** | `docs/v2/audit/cmc_v1_1_leaf24/cmc_wrapper_v5_4240ce82.sh` | **`4240ce82f0929085ab4bcb37e2400a3414e70e162c9e697cf02d97103342f882`** |
| 对照 R5c_v5（step_m1 草案形） | `docs/v2/audit/leaf25_step_m1/LEAF25_STEP_M1_R5c_v5.cmd` | `0b43d5bd59d4e6c6be2917410ebd87f7801474d70f2be8a1b3b68437e7743a49`（**仅形参对照；禁复用其 `.ok` 占位**） |
| 禁复用 step_m1 `.ok` | CONSUMED | **`1c32ab1e5ffb9eb3ddf466f15b0cd778a1579eaca678f2f5fbe1dd1ae00e66f0`** |
| Data X2 结束日 PIN | `docs/v2/audit/DATA_LEAF25_X2_END_DATE_DISK_PIN_20261025_ZH.md` | `adb219a0094da06441793d0b90c59424ba3d23b511e46762deb16d30cff7eb2a` |
| X2 窗 | **2024-06-03 → 2026-10-09** | `X2_END_TRADE_DATE=20261009` |
| 密封窗（本草案**不含**） | 2018-01-02 → 2024-05-31 | **另签另 `.ok` 另进程** |

- 全叶 build / eval 脚本：基盘 §8 #12/#13 **待写待钉** → 下表 CLI 中 `<BUILD_SCRIPT>` / `<EVAL_OR_FACTORY>` 为占位；**Arch 签 `.ok` 前必须换成现盘全长 sha**。
- 密封轨：**不在本草案**；须 X2 全硬闸后再排密封窗。

---

## 2. 帽与分块（禁抬帽）

| 项 | 值 | 说明 |
|---|---|---|
| C4 | **1331200** kB | 对齐 step_m1；`.ok` 须同钉 |
| wrapper STOPKB | **1484800** kB | wrapper v5 默认 |
| hard | **1536000** kB | 单进程硬线 |
| 期望峰报告线（example） | ~900000 kB（MEM 文） | 超过 → **再拆块**，**不是**抬帽理由 |
| MEM 强制分块 | 按再平衡日/年/SW L1 行业/宇宙轨（MEM §3） | **硬前置**；禁整窗 densify |
| 采样 | **仅** `/tmp/quantlab_*` | wrapper v5 默认 `/tmp/quantlab_wrapper_sampler/`；并行 30s 采样亦须 `/tmp`；**禁** `output*`/`data*` |
| 破帽 | **ABORT** | 不自重试；不抬帽 |

`.ok` / `.cmd` 若写成更高帽 → **Arch 应拒签**。

---

## 3. 拟 cmd（仅 X2 轨 · wrapper v5）

占位：
- `<ET_TS>=$(date +%Y%m%d_%H%M%S)`（开跑瞬间）
- `<ARCH_X2_OK>` = Arch **新**签发路径（名拟 `output/ai_factory/ARCH_RUN_AUTH_LEAF25_FULL_FACTOR_X2_R1.ok`）——**不得**填 `1c32ab1e…` / 任何 CONSUMED/VOID
- `<BUILD_SCRIPT>` = 全叶 build 现盘路径（待写后钉 sha）
- 断言 stem 以 Arch `.ok` 为准（下例 `leaf25_full_factor_x2` 为拟）

```bash
# DRAFT — 未授权；有新 X2 .ok 且 14:30–16:00 ET 窗内、且叶27 12:30–13:30 已让出后才可执行
# 本文件不是 .ok；禁复用 1c32ab1e；禁与密封同张；禁抬帽；采样仅 /tmp
cd /workspace/QuantLab && \
ET_TS=$(date +%Y%m%d_%H%M%S) && \
OUT=output/ai_factory/_leaf25_full_factor/${ET_TS} && \
LOGDIR=${OUT}_logs && \
SAMPDIR=/tmp/quantlab_leaf25_full_x2_${ET_TS} && \
mkdir -p "$OUT" "$LOGDIR" "$SAMPDIR" && \
# 预检：pgrep 空 + 新 .ok 钉 wrapper v5/C4/分块/X2 窗 + 时刻∈14:30–16:00 ET + MEM 已 Arch 审 后，再：
bash docs/v2/audit/cmc_v1_1_leaf24/cmc_wrapper_v5_4240ce82.sh \
  --arch-ok <ARCH_X2_OK> \
  --assert leaf25_full_factor_x2 \
  --tag leaf25_full_factor_x2 \
  --logdir "$LOGDIR" \
  --outdir "$OUT" \
  --meta "$OUT/run_meta.json" \
  --cwd /workspace/QuantLab -- \
  timeout 3600 env PYTHONDONTWRITEBYTECODE=1 \
  /workspace/qlvenv/bin/python <BUILD_SCRIPT> \
    --window x2 \
    --x2-end 20261009 \
    --out "$OUT/"
```

**一行摘要（开跑核；脚本名待钉）**：

```text
bash docs/v2/audit/cmc_v1_1_leaf24/cmc_wrapper_v5_4240ce82.sh … -- /workspace/qlvenv/bin/python <BUILD_SCRIPT> --window x2 --x2-end 20261009
```

| 路径类 | 约定 |
|---|---|
| out_dir | `output/ai_factory/_leaf25_full_factor/<ET_TS>/`（α 分区见 MEM §3.3；禁写纸面/FROZEN） |
| log | `…/<ET_TS>_logs/` |
| **sampler** | wrapper 默认 `/tmp/quantlab_wrapper_sampler/<TAG>_sampler.txt`；并行监控 **必须** `/tmp/quantlab_leaf25_full_x2_<ET_TS>/` |
| X2 日历 | **2024-06-03 … 2026-10-09**（`X2_END_TRADE_DATE=20261009`） |
| 密封 | **本草案不含**；另窗另签 |

**明确禁止**：
- `--window both` / 密封+X2 同进程同 `.ok`
- 复用 step_m1 `.ok` `1c32ab1e5ffb9eb3ddf466f15b0cd778a1579eaca678f2f5fbe1dd1ae00e66f0`
- 抬 C4/stop/hard 超 1331200/1484800/1536000
- 采样写入 `output*` / `data*`
- 在叶27 **12:30–13:30 ET** 窗内抢跑
- 申签本草案本身当作授权

---

## 4. `.ok` 结构要求（供 Arch；AI 不申）

| 键意图 | 要求 |
|---|---|
| 轨 | **仅 X2**（密封另张） |
| wrapper | v5 `4240ce82f0929085ab4bcb37e2400a3414e70e162c9e697cf02d97103342f882` |
| c4_limit_kb / stopkb / rss_limit_kb | **1331200 / 1484800 / 1536000** |
| X2 窗 | start `2024-06-03` end `2026-10-09`；字面 `X2_END_TRADE_DATE=20261009` |
| prereg | FROZEN 戳记 `4bb1ff2b805f441499607ada5f871044e72e6176a66052c73b64816130d199e2` + 正文 `e8ca2bcc1136b473bdc77f3f655e77f35404990068e9e30ac0c1cd9ed721292c` |
| MEM | `103717df1f9e5d63f8c681f16da091f44801e1b69b219ae1a18b2159446145d1` 且 Arch 审结 **PASS**（或等价）后才签 |
| 脚本 | 现盘 build/eval 全长 sha（待写后填） |
| 采样 | `/tmp` only；`allow_c5_ignore=false` |
| 禁复用 | 显式禁 `1c32ab1e5ffb9eb3ddf466f15b0cd778a1579eaca678f2f5fbe1dd1ae00e66f0` |
| 窗 | not_before≈14:30 / expires 以主+Arch 为准（拟工作至 16:00 ET） |
| ai_no_retry | true |

---

## 5. 开跑前检查清单（全部 PASS 才启进程；本回合不跑）

1. 叶27 12:30–13:30 已结束或主书面让出；现盘无叶27 研究进程
2. `pgrep` 研究/web 写链空（对齐团队预检惯例）
3. **新** X2 `.ok` 现盘且 sha ≠ `1c32ab1e5ffb9eb3ddf466f15b0cd778a1579eaca678f2f5fbe1dd1ae00e66f0`；内容钉 wrapper v5 / C4 三帽 / X2 窗 / FROZEN+DRAFT sha / MEM 已审
4. 时刻 ∈ **14:30–16:00 ET**；未过 expires
5. §8 财务 + leaf19 **重验回执已落**（见 FROZEN 戳记 §5；本草案不替代）
6. QUIET 若要求则设后核 healthz；结束/ABORT 须 lift
7. 分块实现已按 MEM；静态 `py_compile`→`/tmp` PASS；未写 research `__pycache__`

---

## 6. 本文件边界

| 本文件是 | 本文件不是 |
|---|---|
| X2 轨 cmd **草案** + 钉表/帽/分块/窗约束 | **不是** `.ok` / 不是授权 |
| 对齐主令 FROZEN + P2 PASS + wrapper v5 | **不**替代 Arch 签发 |
| 引用 FROZEN `4bb1ff2b805f441499607ada5f871044e72e6176a66052c73b64816130d199e2` | **不**含密封轨；**不**申 `.ok`；**不**自开跑 |

对照：FROZEN 戳记；MEM `103717df1f9e5d63f8c681f16da091f44801e1b69b219ae1a18b2159446145d1`；R5c_v5 形参 `0b43d5bd59d4e6c6be2917410ebd87f7801474d70f2be8a1b3b68437e7743a49`；叶27 cmd 草案形 `docs/v2/audit/AI_LEAF27_LOWMEM_HILIQ_X2_CMD_DRAFT_20261025_ZH.md`。

live=false.
