# Arch 叶25 mem_probe r3 实峰 probe `.ok` 签发回执

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-25T12:47:07-04:00`（America/New_York） |
| 主令 | PASS 后另签独立实峰 probe；对齐 VOID 裁定 `6ef34f99…`；撞 14:00–14:45 则叶27优先 |
| 审阅 | `63500a9f…` **PASS_WITH_CONDITIONS** |
| live / promotion_approved | **false** / **false** |

## 结论

**SIGNED** — 独立实峰 probe `.ok` 已落盘；**≠ X2.ok**；**Arch 不代跑**；X2 / NEED_MEM_PROBE **仍不解阻**，直至入窗实峰跑 PASS。禁复用 VOID `cd230f9c` / `1c32ab1e`。

## 钉

| 项 | 值 |
|---|---|
| `.ok` 路径 | `output/ai_factory/ARCH_RUN_AUTH_LEAF25_MEM_PROBE_R3.ok` |
| `.ok` sha8 / 全长 | `c5e54085` / `c5e540855bc836b97b7395a53dd63a6d3c295860fdd11e72e77abd6cf3152011` |
| 脚本 | `research/leaf25_full_factor_mem_probe_r3.py` = `8da4f2e663d83956b4b9910fc958f9decba68f40327f2089610ffa1a069600ea` |
| wrapper v5 | `4240ce82f0929085ab4bcb37e2400a3414e70e162c9e697cf02d97103342f882` |
| 审阅 | `63500a9f34015264eff43eec41e1f9af5ed8b2a86d7a1a1a74e2bc2d8c47018d` PASS_WITH_CONDITIONS |
| COVER/CMD/DIFF | `33117114975338a5c2f3b41ea9fc7e2ecb3f12cf356663c413d2746622c937a4` / `440930e8ac2cc3ef61e2891cad1683271c8b6ceab10ebd92d4c0035b197b84f7` / `caec5bde93b17144fdf0faabec4fcb927d9c7681cd1bae4e16803738bbdd2f4f` |
| 拟短窗 | `2026-10-25T12:50:00-04:00` → `2026-10-25T13:45:00-04:00`；expires `2026-10-25T13:47:00-04:00`（**错开叶27 14:00–14:45**；请主确认/改排） |
| CLI 核 | HI_LIQ · `--mode month` · `--start 2024-06-03 --end 2024-06-28 --chunk-id 0` · `--allow-real-data` |
| 帽 | C4/stop/hard **1331200/1484800/1536000**；阈 **1131520**；**禁抬帽** |
| 采样 | 仅 `/tmp/quantlab_*` |
| 滤子 | end_date **Timestamp/schema-aware**（禁 string vs timestamp[us]） |
| 禁复用 | `cd230f9c2aa9fc8de7fc538fb1f04ded8d9c20463f24b88b6c0f76950ec34279`；`1c32ab1e5ffb9eb3ddf466f15b0cd778a1579eaca678f2f5fbe1dd1ae00e66f0`；禁 r1 dry；禁 X2/密封同张 |
| 披露 | dry_run=false；float32；densify=false；claims_full_cfacc=false；alpha_kind=crude_accrual_cs_zscore_probe_only；peak_kb；end_date_filter=Timestamp |
| QUIET | 已挂锁留给 AI prelaunch（未 lift） |

## 预检旁证

`ARCH_LEAF25_MEM_PROBE_R3_PREOK_EVIDENCE_20261025_ZH.md` sha `38bf4474231dc0cd4ce395b8e818be710d8cc5c2fdbd2f2f6cf7a0043cdbbbbb`

## 下一跳

1. **主**确认/改排短窗后令 AI prelaunch 开跑（须在 expires 前；勿撞叶27 14:00）
2. AI 交实峰回执（peak_kb 等）→ Arch 核 → 才解阻 X2 内存键
3. Arch 不代跑；live=false
