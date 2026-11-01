# 叶27 limit_hit 日对齐闭合回执（研究级）

- **角色**：QuantLab AI
- **时刻**：2026-10-25 06:51:30 ET（America/New_York）
- **触发**：Arch 终审 PASS_WITH_CONDITIONS（审阅 sha `666fed209731dab958cddf498f16ca879f03ff22d844e8d52aee0f315871bd79`）条件5 阻断
- **锁**：不申 `.ok` · 不跑 sealed/X2 · 不挡叶25 · 不 git commit · `live=false`

## 闭合内容

1. **`limit_hit` 日对齐已接线**（相对旧脚本 `1da6922c…`）：`LimitPanelCache` 按 `(ts_code, 1c85|ext)` 缓存；1c85 用 index `event_time`→`%Y-%m-%d`；extend 用 `trade_date`；路径切分 `ymd<=20260630`→1c85 else extend。
2. **返回语义**：`True`=触板；`False`=板价有效且未触；`None`=缺 panel/行或 lu&ld 均无效（含 BJ 空）。**禁**恒返 None 桩；**禁**静默当未触板。
3. **日循环**：`limit_policy=exclude_hit_or_unknown` — 触板或未知剔除，不进截面残差 / `eps_hist` / ivol；meta 披露 `limit_hit_n` / `limit_unknown_n` / `bj_limit_empty_n`。
4. **`available_at`**：表无列 → **不伪造**；主裁研究级豁免 **GRANTED** sha256 `b39954c3ff6ee4c03f904ec9f58660871b1b574bfab6498c57b825878f28ab7f`；日历 T−1 仍 SCRIPT_LANDED。豁免 ≠ `.ok`。

## 新包 sha（全长）

| 项 | sha256 |
|---|---|
| 脚本 `research/g1g5_on_minus_id_idio_ivol_alpha.py` | `7a5f756c0a1ab09fb55aa2bc3c17f389bde44d222d7066237e503566c908f8c6` |
| DIFF `docs/v2/AI_LEAF27_ON_MINUS_ID_IDIO_IVOL_DIFF.patch` | `e2ed0fc88bfe38c07892a3a87d03f9b2372cb8cfd568fd7de9548f3113978b71` |
| impl pin `docs/v2/AI_LEAF27_IMPL_CONTRACT_PIN_20261025_ZH.md` | `a532e6db956600ab3e4048edeaabdc653b2e83ed4ef52f2839eeb78e12f87416` |
| Arch 预告（MATCH） | `31462908aa15c131fd74b6c378870907713235b975e08d7f026c79cc1707e196` |
| 主豁免（MATCH） | `b39954c3ff6ee4c03f904ec9f58660871b1b574bfab6498c57b825878f28ab7f` |

旧包 `3d3a901f…` / `1da6922c…` / `2fc801aa…` **SUPERSEDED**。

## 非动作

未签 `.ok`；未跑实数；路径 sha 另窗再核；不挡叶25@10:00 ET。
