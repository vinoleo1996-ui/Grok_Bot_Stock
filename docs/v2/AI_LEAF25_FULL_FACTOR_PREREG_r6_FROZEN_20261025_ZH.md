# 【FROZEN 戳记】叶25 全叶因子预注册 r6

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI（执行器） |
| 戳记落盘 | 2026-10-25T11:47:10-0400（America/New_York；墙钟 `2026-10-25 11:47:10 EDT`） |
| **主令 FROZEN 时刻** | **2026-10-25 11:44 ET**（America/New_York）；令文 `docs/v2/audit/MAIN_LEAF25_R6_FROZEN_ORDER_20261025_ZH.md` |
| 状态 | **FROZEN（戳记）** — 冻结正文 = 下方基盘 DRAFT 全长 sha；**本戳记不改机制/窗/钉表数值** |
| live | **false** |
| promotion_approved | **false** |
| research_only | true |

---

## 1. 冻结正文指针（权威）

| 项 | 值 |
|---|---|
| 基盘路径 | `docs/v2/AI_LEAF25_FULL_FACTOR_PREREG_r6_DRAFT_20261025_ZH.md` |
| 基盘状态行（落盘时） | **DRAFT r6 / 未 FROZEN**（文件头不改；以本戳记宣布主令 FROZEN） |
| **基盘 DRAFT 全长 sha256** | `e8ca2bcc1136b473bdc77f3f655e77f35404990068e9e30ac0c1cd9ed721292c` |
| 校验 | 落戳记前 `sha256sum` **MATCH**；**基盘文件本回合未改写** |

> **语义**：主令宣布 r6 **FROZEN**；机制 / 窗 / 钉表以基盘 DRAFT 正文为准（sha 上表）。本文件是 **状态戳记 + 闸口清单**，不是第二份可改钉的预注册正文。

---

## 2. 主令已钉摘要（只复述；数值以基盘为准）

| 钉 | 值 |
|---|---|
| `X2_END_TRADE_DATE` | **20261009**；X2 窗 **2024-06-03 → 2026-10-09** |
| 密封窗 | **2018-01-02 → 2024-05-31**（**另签**；禁与 X2 同张 `.ok`） |
| t* | **2.50**（家族 n=4；leaf21 不同族） |
| P2 / wrapper v5 | Arch PASS `964cf57be56e8723fcff79ba620c5034e18b6e0fe083f59bef939e5db4705f78`；DIFF `9584723f8dcce3907c797fd3b50d15576491a1f3898690b75c97fd707337fa38`；wrapper **`4240ce82f0929085ab4bcb37e2400a3414e70e162c9e697cf02d97103342f882`**（`docs/v2/audit/cmc_v1_1_leaf24/cmc_wrapper_v5_4240ce82.sh`）**可钉全叶** |
| C4 / stop / hard | **1331200 / 1484800 / 1536000** kB（对齐 step_m1；**禁抬帽**） |
| 采样 | 仅 `/tmp/quantlab_*`（wrapper v5 默认） |
| 禁复用 | step_m1 `.ok` `1c32ab1e5ffb9eb3ddf466f15b0cd778a1579eaca678f2f5fbe1dd1ae00e66f0`（CONSUMED）及任何 VOID |
| Data X2 PIN | `docs/v2/audit/DATA_LEAF25_X2_END_DATE_DISK_PIN_20261025_ZH.md` sha `adb219a0094da06441793d0b90c59424ba3d23b511e46762deb16d30cff7eb2a`；瓶颈 float_mktcap `346d0dda8a95e8d209fd388cfb1aad5425745fc0b5eb0a16dd4de3ab3d72a1ef` |

---

## 3. 硬闸（戳记瞬间仍成立）

- **仍禁申 `.ok`** / **禁自开跑** / **禁实跑读盘** / **禁 git commit**
- 密封与 X2 **分两张独立 `.ok`**；本戳记 **不**构成任一张 `.ok`
- 叶27 另窗 **12:30–13:30 ET** 优先；全叶 X2 拟窗 **14:30–16:00 ET**（主排；须 X2 硬闸齐后再签）
- live=false

---

## 4. 前置未齐（不得假装已过）

| # | 前置 | 状态 |
|---|---|---|
| A | Arch 审 MEM/分块 | **未齐** — `docs/v2/audit/leaf25_step_m1/AI_LEAF25_FULL_FACTOR_MEM_ESTIMATE_CHUNK_20261025_ZH.md` sha256 `103717df1f9e5d63f8c681f16da091f44801e1b69b219ae1a18b2159446145d1` **待 Arch 审**；审过后方可签 X2 `.ok` |
| B | 全叶 build / eval 脚本 sha | **待写待钉**（基盘 §8 #12/#13） |
| C | 主填 X2 窗 + Arch 新 X2 `.ok` | **未申请**；拟 14:30–16:00 ET；叶27@12:30 优先勿抢 |

---

## 5. FROZEN 瞬间待重验清单（§8 财务 + leaf19；**本戳记未做重验**）

> 下列为基盘 §8 / r5 起点钉的 **待重验清单**。本回合 **未**对财务大表 / leaf19 α 做 `sha256sum` 重验（禁实跑读盘）；**不得**把本戳记解读为「已重验通过」。签发 X2 `.ok` 前须由 AI/Arch 现盘重验并写入回执。

| # | 项 | 基盘/r5 起点钉（待重验） | 本戳记 |
|---|---|---|---|
| 5.1 | income PIT | `data/v2/financials_pit/financials_pit_tushare.parquet` 起点 sha `bc0f4c3d3cd70a11d17f44496861e21268806509656247400c64be2d3ae7fab3` | **PENDING_REVERIFY** |
| 5.2 | cashflow PIT | `data/v2/financials_pit/cashflow_pit_tushare.parquet` 起点 sha `71d5c3d39fbf2de05064ce7f21334e15c9b1d977c64494ffe699f7eeb0b95d79` | **PENDING_REVERIFY** |
| 5.3 | balancesheet PIT | `data/v2/financials_pit/balancesheet_pit_tushare.parquet` 起点 sha `9ca054962e850cad7305262e978758c9e9f36613c4cca025efdd99276de8dbb5` | **PENDING_REVERIFY** |
| 5.4 | leaf19 α HI_LIQ | `output/ai_factory/leaf19_cfacc_rnoa/alpha_HILIQ_20261014_213132.parquet` 起点 sha `16202b2e…`（r5；全长待重验时补齐） | **PENDING_REVERIFY** |
| 5.5 | leaf19 α FULLA | `output/ai_factory/leaf19_cfacc_rnoa/alpha_FULLA_20261014_213132.parquet` 起点 sha `c761dc36…`（r5；全长待重验时补齐） | **PENDING_REVERIFY** |
| 5.6 | 日历 + SW L1（与 sw_members 共钉） | cal `fa4260b808755b9a1c91e3ade210edec84bbdb91e0dfff4c6a955c4d35fd8a41`；SW `89d4afa337435a2302b5c13fd4cf049b71eda2f20e1d9094f15d62cdb587f66c`；脚本 `dec73305f8cd49d2c4ad695f72158e10bceb20de83fa19b2a1580be08579a9a7` | **PENDING_REVERIFY**（FROZEN 瞬间再核；本戳记未跑） |
| 5.7 | selfcheck / CMC | `ecaa30d8760f7ae5f53c330c128e6702476d01d8d69112b1dbf2fe769b7eaebe` / `bba212afadefce68dcd1bf76919f91de39402658e4398e925e3d80c6f01592c4` | **PENDING_REVERIFY** |

任一重验 FAIL → **停**；改钉须新文件名 / 冻结补丁，不得静默改基盘冒充未变。

---

## 6. 状态机指针

```
PREREG_r6_DRAFT_READY (e8ca2bcc…)
  → 【本戳记】r6 FROZEN（主令 11:44 ET；正文仍指向 e8ca2bcc…）
      → Arch 审 MEM (103717df…) + §8 重验
          → 主排 X2 窗（拟 14:30–16:00；叶27 12:30–13:30 优先）
              → 独立 X2 .ok（禁复用 1c32ab1e；禁与密封同张）
                  → 窗内开跑 X2
                      →（条件）独立密封 .ok
```

**当前**：**r6 FROZEN（戳记）**；**仍禁申 `.ok` / 禁自开跑**；等 Arch 审 MEM + §8 重验 + 主/Arch 签窗。

live=false.
