# 叶33 PIN_GAP 决议（float_ratio）— 冻结前钉

- 角色：QuantLab AI
- 时点：2026-10-27 05:49 ET（ISO `2026-10-27T05:49:06-04:00`）
- 触发：主 05:47 ET 排号确认；要求冻结前核死 `float_ratio` 或写死主路径
- 状态：**DRAFT 侧决议**；**NOT FROZEN**；**未**改 who_pays `1032477d` 全文（Arch 只审中勿扰动审本）；FROZEN 时将本决议原样并入
- EXECUTED=false；ok_requested=false；live=false；leo_notify=false；≠X2 ACCEPT

## 分布核（只读 share_float_pit 列统计；未联 float_mktcap；未开研究跑）

| 项 | 值 |
|---|---|
| n | 6,449,659 |
| finite float_ratio | 6,282,986 |
| p50 / p90 / p99 / max | 1e-4 / 4e-4 / 1.029 / 91.28 |
| ≤0 | 795,664 |
| (0,1] | 5,423,473 |
| >1 | 63,849 |
| >10 | 9,487 |

结论：多数像「占流通比例」，但 **>1 与 max≈91** 说明单位**不干净**，不可作 PRIMARY 分母。

## 冻结写死（PRIMARY）

1. **主路径唯一**：`unlock_raw = sum(float_share) / float_mktcap_{T-1}`  
   - `float_share` 来自 `data/v2/share_float/share_float_pit.parquet`  
   - `float_mktcap` 来自 `data/v2/float_mktcap/float_mktcap_daily_from2015_tushare.parquet`（instrument_id↔ts_code；trade_date=T−1 PIT）  
   - 分母 ≤0 / 缺失 → 该日该名 **无效**，**不**填 0
2. **表内 `float_ratio`：PRIMARY 禁用**（不得静默混用；不得作主信号能量）  
   - 仅允许 FROZEN 后脚本做 **披露对照**（可选支路，默认 OFF），且须另证单位；对照失败不影响主路径
3. who_pays `1032477d` / COVER `61d9f656` 已写此主路径意向 → 本票 = **核死写死**，PIN_GAP **关闭条件** = 并入 PREREG_FROZEN 正文

## 禁

- 本拍不升 FROZEN（等 Arch who_pays 只审回执）
- 不申 `.ok`；不挂 QUIET；不实跑；不联表读收益/权重
- 禁 RESTORED `5774bb6e`+二十票；`0087c928` 另队

## 下一跳

Arch who_pays 审回 → 主令 GO FROZEN → 将本决议并入 `AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_PREREG_FROZEN_*.md`
