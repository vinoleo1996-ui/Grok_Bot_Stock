# D1 掩码完备 — 实现计划与脚手架

> 2026-10-10 · 云端 `/workspace/QuantLab` · `promotion_approved=false`
> 对齐 Eng 冻结名：`float_mktcap`、`median_amount_20d`、`industry_members_sw_l1`

## 模块路径

| 路径 | 角色 |
|---|---|
| `quantlab/universe/mask.py` | Phase-0 接口 / StubUniverseMaskProvider |
| `quantlab/universe/d1_masks.py` | **可执行 D1 管道**（本阶段落地） |
| `quantlab/v2_schemas.py` | 冻结列名 / schema_handshake_payload |
| `quantlab/data/v2_d0_meta.py` | D0 meta/calendar 探针 |
| `scripts/d1_mask_prototype.py` | 1c85 只读冒烟 |
| `data/local_market/1c85fd9aceaa03c3c4863bec/` | D0 底座（只读） |
| `data/v2/sw_l1_pit/industry_members_sw_l1.parquet` | SW_L1 PIT（研究级） |
| `data/v2/etf_510300/panels/sh.510300.parquet` | Beta 袖套 Eng 面板 |
| `data/v2/d1_masks/` | 原型输出 |

## 可交易掩码顺序（决策日 t）

```
1. instruments 历史宇宙（含退市前）
2. listing_trading_days >= 120
3. 可交易且非 ST
     - suspended: tradestatus==0 或 open_status==halted
     - st_flag: is_st_at_open
     - research: open_status in {trading, derived} 可过
     - strict:   仅 open_status==trading（derived/unknown 拒绝买入）
4. U30: median_amount_20d >= Mandate 阈值（默认 3e7 CNY）
5. limit_up_buy_block / limit_down_sell_block
6. 剔最小 exclude_bottom_mktcap_pct≈30% 的 float_mktcap（PIT）
7. 贴 SW_L1 as-of（industry_members_sw_l1；禁止 D0 industry_records 替代）
```

## float_mktcap 派生

D0 panels **无** `float_mktcap` 列。研究代理公式（写入 manifest）：

```
float_mktcap = close * volume / (turnover / 100)   # turnover 为 percent
```

`turnover<=0` 或缺失 → NaN → 不参与分位剔除（或进 data_gaps）。
质量：`derived_from_turnover_percent`；不可当晋升级流通市值真相。

## 伪代码

见 `quantlab.universe.d1_masks.PSEUDOCODE` 与 `output/d1/PSEUDOCODE.txt`。

## 验收（D1 研究级）

- [ ] 单日 `build_d1_masks_for_session` 可在 1c85 上跑通
- [ ] 输出含 `float_mktcap`、`median_amount_20d`、SW_L1 列
- [ ] `promotion_approved` 恒 false
- [ ] strict 模式对 derived open_status 拒绝买入路径有单测（待补）

## 已知洞

- open_status 多为 derived
- turnover 空洞约 572 只（coverage）
- SW_L1 leaf→L1 投票映射覆盖约 60% 历史行（见 D2）
