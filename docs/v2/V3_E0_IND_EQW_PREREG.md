# V3_E0_IND_EQW_PREREG — 行业 ETF 等权对照（E0）
研究级，**promotion_approved=false**。写于 **2026-10-12 05:55 ET，运行前**。
批次：`smoke_evtflow_indetf`。压舱 **511880**。对照臂，非主线。

## 机制
仅承担行业 β 与分散；**无动量、无份额信号**。用于对照 IND-SHARE-REV 是否真有申赎反转溢价。

## 规则
- 同 IND-SHARE-REV 可交易池；每月末对所有合格行业 ETF **等权**；无合格则 511880。
- 引擎与 fund_div 说明同 ETF_ROTATION_PREREG / IND-SHARE-REV。
- 历史 E0 在旧映射 X2 曾跑输 510300（见 ETF_ROTATION_PREREG §14）；本轮按 60/100万 + 511880 压舱重跑冒烟。

## 闸门
同 hub；对照臂即使过闸也标注 **control_only**，不单独作为主线晋升候选。
