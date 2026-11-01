# 叶27 Post-GateA baseline_evac 独立侧稿 HAND 回执 · **DRAFT_READY_FOR_ARCH_HOLD**

- **角色**：QuantLab AI（执行器）
- **时刻**：2026-10-25T22:06:00-04:00（America/New_York；墙钟 2026-10-25 22:06 ET）
- **status**：**DRAFT_READY_FOR_ARCH_HOLD** — **未**声称已 SUBMITTED 给 Arch；本回合只回主；等主交审
- **ok_requested**：false · **live**：false · **实跑**：未做 · **`.ok`**：未申 · **QUIET**：本回合 **未擅 lift**
- **三件+脚本盘证**：COVER `0ff59ed4` / CMD `bf6ffe4a` / DIFF `dc802879`；脚本 **CHANGED** `585ba746`（prev `27aae6db`）
- **触发**：Gate A ABORT 回执 `f0f94c9e`（1507@chunk6_mktcap）；Arch R2 `c8dc89b6` RECOMMENDED=A；Leo 开 A；主令 `46dc8cb3` 立刻出 COVER/CMD/DIFF/HAND

## 三件 + 脚本盘证

| 件 | 路径 | sha256 |
|---|---|---|
| COVER | `docs/v2/audit/AI_LEAF27_CHUNKED_BASELINE_EVAC_COVER_DRAFT_20261025_ZH.md` | `0ff59ed4576302224267453821a2a13f07a010ab06f3d14c624b4c73b02f5992` |
| CMD | `docs/v2/audit/AI_LEAF27_CHUNKED_BASELINE_EVAC_CMD_DRAFT_20261025_ZH.md` | `bf6ffe4a05a2a90fac45e3e4cb8f101a8f5fa619fa48d145a333ecc16f126b25` |
| DIFF | `docs/v2/audit/AI_LEAF27_CHUNKED_BASELINE_EVAC_DIFF_DRAFT_20261025.diff` | `dc8028799033600dbd0ed653b2d7868096e514c6d85f5b41bde335e850fd4980` |
| 脚本（CHANGED） | `research/leaf27_chunked_members_mktcap_r1.py` | `585ba7467a5896354c937d14fe0590fa80535afd6b6263015d3c12e3dfccd4ec` |

sha8 速查：COVER **`0ff59ed4`** · CMD **`bf6ffe4a`** · DIFF **`dc802879`** · 脚本 **`585ba746`**

## 对照钉

| 钉 | 值 |
|---|---|
| 主令 | `46dc8cb3`（Leo 开 A） |
| 主闸 R2 | `e8d7346c` |
| Arch R2 | `c8dc89b6`（RECOMMENDED=A） |
| 尖峰笔记 | `0b483746` |
| ABORT 回执 | `f0f94c9e`（1507MB @chunk6_mktcap） |
| VOID 权威 | `ff0394d0` |
| VOID `.ok` | `e107383f`（禁 RESTORED） |
| forbid 七票 | `e107383f` / `2be59acd` / `a7d98ac9` / `8e51de63` / `3a6caa4f` / `8bcd79dc` / `725be3e0` |
| Gate A 旧包 | `AI_LEAF27_CHUNKED_MKTCAP_CACHE_*`（**不覆盖**；CLOSED_INSUFFICIENT） |
| PRIMARY CLI | `--chunk-mode ndays --chunk-ndays 40`（**同** Gate A；代码 A 疏散） |
| baseline_evac | lim_cache session 驱逐 + α 中段落盘；tag `baseline_evac_r1` |
| mktcap_cache / hist_prune | **保留** `mktcap_cache_r1` / `hist_prune_r1` |
| rss_limit | 1500 禁抬 |
| sampler | `/tmp/quantlab_leaf27_chunked_baseline_evac_*` only |
| 交审门 | **等主交审**；本 HAND **未** SUBMITTED_TO_ARCH |

## 动作边界

- **未**交 Arch；**未**申 `.ok`；**未**实跑；**未** git commit
- **未**擅 lift QUIET；**未**抬帽；**未**启动任何实数进程
- 工作树已打 baseline_evac_r1 补丁（脚本 `585ba746`）；备份 `27aae6db` → `/tmp/…27aae6db.bak` 与 `docs/v2/audit/_bak/`
- 静态 py_compile/pyflakes/dry-compile OK
- **未**改 `research/g1g5_on_minus_id_idio_ivol_alpha_lowmem_v1.py`（仍 `05bd81ea`）
- 禁自开跑 / 禁申 X2.ok / 禁复用 VOID/CONSUMED / 禁静默切 mode / 禁重批旧 Gate A
- ≠X2 · live=false · **DRAFT_READY_FOR_ARCH_HOLD**（等主交审）
