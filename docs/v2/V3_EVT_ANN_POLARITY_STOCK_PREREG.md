# V3_EVT_ANN_POLARITY_STOCK_PREREG — 公告极性 → 中大盘个股袖套
研究级，**promotion_approved=false**。写于 **2026-10-12 07:24 ET，运行前**。
批次：`stock_etf_smoke`。主线：**个股+ETF**。残差 **510300**。

## 独特收益来源（谁付钱）
公司公告（回购/增持/预增 vs 处罚/减持/预减）的 PIT 披露后，市场对「好消息」反应不足或对噪声标题过度反应；本臂做多新鲜正极性中大盘，残差宽基。付钱的是：公告日追涨杀跌的短线资金与忽略条款细节的被动持有者。

## ≠
| 臂 | 差别 |
|---|---|
| P8 EVENTS_MIDLARGE（预注册族） | 事件研究+多试验；本臂单袖套 polarity 合并多头 |
| ANN-BETA（parked） | 舆情/情绪调节 β，非公告分类 polarity |
| DT-INST-BREADTH | 龙虎择时宽基，非公告个股 |

## 股票池
同 EVT-DT-INST-STOCK（CSI300∪CSI500；X1 权重缺失段用 float top800 近似；禁小盘；滤 ST、价&lt;2）。

## 规则
- 数据：`announcements_classified_pit.parquet` ∪ `announcements_classified_pit_post202406.parquet`。
- 正：`event_type∈{buyback,insider_increase,earnings_beat}` 且 polarity=+1（buyback 剔除 `buyback_excluded`）。
- 负：`event_type∈{penalty,insider_decrease,earnings_miss}`（过滤：持有中若新出负事件则剔除）。
- PIT：`available_at`（ann_date 23:59）→ 下一交易日开盘。
- 周度：取近 10 个交易日内新鲜正事件、无未消化负事件的 universe 名；按「正事件计数」再 `available_at` 新近排序，top **N=25** 等权；残差 510300。

## 覆盖
主表 `ann_date` **20180101→20240531**；post202406 补 **20240601→20261011**。  
**X1（2015-06→2017-12）无公告 PIT → 诚实 `coverage_blocked_X1`**（不伪造、不前移、不重定义假 X1）。S/X2 有覆盖时可跑 descriptive，但不作 explore-pass（缺 X1 闸）。

## 闸门
同 hub。缺 X1 → coverage_blocked，无交接。promotion_approved=false。
