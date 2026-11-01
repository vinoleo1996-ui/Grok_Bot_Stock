# Arch 裁定采纳：叶25 mem_probe — 拒签实峰（主 (A)）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-25T12:05:24-04:00`（America/New_York；墙钟 `2026-10-25 12:05 ET`） |
| **结论** | **FAIL_FOR_REAL_PEAK** · 静态包可记 **PASS_STATIC_ONLY** |
| 主裁定 | r1 `real_peak_path_gated`=NotImplemented → **不得签「实峰」probe `.ok`**；偏好 **(A)** |
| 本回合动作 | **不签任何 probe `.ok`**（含 DRY_STRUCTURAL）；**推迟 12:10 窗**；不解阻 NEED_MEM_PROBE / 不解锁 X2 内存键 |
| live / promotion | false / false |

## 0. 一句话

执行器审阅 `ARCH_LEAF25_MEM_PROBE_IMPL_REVIEW_20261025_ZH.md` sha `0c7709299abae048968b82c06cf4a1ecb26a7a1c1c7228428398caf96dea013a` 静态 MATCH、dry 烟测 PASS，但其「可签 dry 短窗」建议**不采纳**。对齐主偏好 **(A)**：拒签实峰；**(B) DRY_STRUCTURAL 不签**（静态 py_compile + dry 烟测已在审阅内完成，无需再入窗 dry）。AI 须补最小真实峰路径后再另审另签。

## 1. 证据钉（与执行器审一致）

| 件 | sha256（全长或前缀） |
|---|---|
| 执行器审阅 | `0c7709299abae048968b82c06cf4a1ecb26a7a1c1c7228428398caf96dea013a` |
| probe r1 | `a0071e627d37f7e2498ea73984abb5b7ee4b1d2d0d27afdb85f8fc30986aed23` |
| chunk_plan | `e858b32d314b9161a366ffef6661605943061162d707f7b86d01439d35dcdb12` |
| cfacc stub | `45537fb9294202f10293b8c0c7b57d9ebf95b835f8af23e3ef63a6dc25c47ee3` |
| COVER / CMD / DIFF | `24901024ded0a0d2c077e7d766ed63df9848e2dfe7318e7d7da68d2f1529a19d` / `c8a853c5e3d76227e0fb34ead0ba99c956c0d9938b620fcea6738f425590ca03` / `25bc47bd5ae2040642e5a50ad1ca7715387cdd2a7ad4cf54dcf456856df51f1a` |
| Arch MEM NEED_MEM_PROBE | `f389c394041cf517b8b8449507bfc157a354e51d2a3f41484adc57d021596d49` |
| wrapper v5 | `4240ce82f0929085ab4bcb37e2400a3414e70e162c9e697cf02d97103342f882` |

`real_peak_path_gated` 现体：即便 `--allow-real-data` + 假 `.ok` 亦硬 `SystemExit`（NotImplemented）——**不可解阻 X2**。

## 2. 裁定

| 选项 | 决定 |
|---|---|
| (A) 拒签实峰 + AI 补真实峰路径 | **采纳** |
| (B) 另签 DRY_STRUCTURAL 短窗 `.ok` | **不采纳**（明文：不解阻 X2 / 不算 mem_probe PASS；且静态审已覆盖结构烟测） |
| 12:10–12:40 ET 窗 | **推迟**；勿硬签实峰 |

## 3. 令 AI（最小真实峰路径 r2）

在仍钉下列约束下实现 `real_peak_path_gated`（填实，去 NotImplemented）：

1. 读 PIT（列投影）→ 截面 α → 落盘 part（float32 parquet 可）→ `gc`
2. **HI_LIQ 单块**（`--mode month` 或 `rebal_days≤20`）；禁 `--window both`；FULLA 非本轮优先
3. C4/stop/hard = **1331200 / 1484800 / 1536000** kB；拆块阈 **1131520**；**禁抬帽**
4. 采样 / 中间产物仅 `/tmp/quantlab_*`；`allow_c5_ignore=false`
5. wrapper v5 `4240ce82f0929085ab4bcb37e2400a3414e70e162c9e697cf02d97103342f882`；禁复用 step_m1 `.ok` `1c32ab1e…`
6. 交：DIFF + COVER + CMD 草案 + 三脚本新 sha；**禁自开跑 / 禁申 X2.ok**
7. Arch 另审；**仅实峰路径审 PASS 后**才可申独立实峰 probe `.ok`

## 4. 不解阻清单

- NEED_MEM_PROBE（`f389c394041cf517b8b8449507bfc157a354e51d2a3f41484adc57d021596d49`）**仍挡** X2 `.ok`
- dry 峰 / 静态 PASS **不算** mem_probe PASS
- 禁复用 `1c32ab1e`；禁与密封同张
- Web v2.1.2 已装（`695db08e` / server `4a04f0e2`）与 probe **互斥排程 OK**（本回合无 probe 窗）

## 5. 下一步

1. AI：r2 真实峰路径包 → Arch 另审  
2. Arch：实峰审 PASS 后另窗签 probe `.ok`（非本回合）  
3. probe 实跑 PASS → 才开 X2 `.ok` 闸（原排 14:30 顺延）  
