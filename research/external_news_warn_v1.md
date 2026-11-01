# 外围消息预警 V1 — 轻量采集草案

**状态：** 研究草案；`promotion_approved=false`；不下单；不改 Strategy 权重。  
**更新：** 2026-10-12。  
**原则：** 公开源 / 官方稿优先；**不装重依赖**（不做浏览器农场、不做付费终端必选）；能 curl + 正则/轻解析即可。

---

## 1. 目标

为 `docs/v2/EXTERNAL_NEWS_EARLY_WARNING_V1_ZH.md` 提供可人工或半自动执行的源清单与最小流程，日终产出预警短报（含研究级 `偏多/偏空/观望` + 理由 + 失效条件）。

---

## 2. 源候选（V1）

| 优先级 | 源 | 覆盖 | 取法（轻量） | 备注 |
|---|---|---|---|---|
| P0 | ITC 官网 investigations / 337 | `US337_ITC` | 公开 HTML 列表页；记录 URL+标题+日期 | 官方原文，置信度高 |
| P0 | BIS / Federal Register 实体清单、出口管制规则 | `EXPORT_CTRL` | 官方 RSS/HTML；存 URL 与文号 | 官方 |
| P0 | USTR / 白宫 / 财政部制裁或关税稿 | `TARIFF_SANCTION` | 官方 press 页 | 官方 |
| P1 | 中国商务部 / 海关总署 / 工信部政策稿 | 对等监管、出口管制中方侧 | 官网政策发布 | 境内官方 |
| P1 | 证监会/交易所重大监管（行业级） | `INDUSTRY_REG` | 官网；与 A 股公告管线去重 | 个股处罚仍归公告 PIT |
| P2 | 主流财经对上述官方稿的**首发转述** | 补上下文 | 仅作第二源；须能链回官方 | 禁止单独撑 `high` |
| P3 | 央行 / 重大宏观日历 | `MACRO_MAJOR` | 公开日历 + 官方声明 | 意外项才发卡 |

**不做（V1）：** 付费彭博必选、微信群、无出处自媒体、需重型 JS 渲染且无官方替代的站点。

---

## 3. 最小流水线（人工半自动即可）

1. **扫源（每日）**：P0→P1；有新文号/新案号才进入下一步。  
2. **留证**：保存 `source_url`、标题、`published_at`、首次看到时点；可先落 markdown 附录，V1.1 再 JSONL。  
3. **映射**：按规格「直接列名 > 一级供应 > 同业(indirect)」；只填中大盘。  
4. **填卡**：必填字段含 `research_stance` / `research_stance_reason` / `invalidation`。  
5. **短报**：写入 `output/d1/EXTERNAL_NEWS_WARN_YYYYMMDD_ZH.md`；无事件则一行 `no_material_external_warn`。  
6. **硬停**：不调用下单 API；不改 Strategy 权重文件；不跑 GP。

---

## 4. 标的映射提示（消费电子 337 示例）

| 层级 | 示例 | 用法 |
|---|---|---|
| 直接列名被告/目标 | 以 ITC 诉状为准 | `confidence` 可上 `high`（有官方） |
| 一级代工/组件龙头 | 立讯精密、工业富联等 | 需业务敞口叙述支撑 |
| 同业弱相关 | 宽基消费电子 ETF 成分 | 标 `indirect`；立场常 `观望` |

映射表 V1 可用手维 CSV（如 `research/external_news_map_ems_sample.csv`），不强制代码。

---

## 5. 与公告拉取的接口

- 外围卡发出后，若映射公司发了 A 股风险提示，在短报追加「公告侧确认：是/否」。  
- 数据路径参考：`data/v2/events/announcements_classified_pit.parquet`（见 `docs/v2/EVENT_FLOW_DATA_STATUS.md`）。  
- **禁止**把公告分类器的 `other` 垃圾标题升级成 337 事件。

---

## 6. 工程备忘（可选 V1.1）

- 脚本位置建议：`scripts/external_news_warn_scan.py`（只读抓取 + 打印候选；默认不写网除官方 GET）。  
- 依赖：stdlib + 现有 `requirements-data.txt` 内工具即可；新增包须单独审批。  
- 输出：`output/d1/external_news_warn_YYYYMMDD.jsonl` 一行一卡。

---

## 7. 验收勾选

- [x] 规格含研究级交易建议字段  
- [x] 样例短报含偏空 + 理由 + 失效条件  
- [x] 本采集草案（公开源、轻依赖）  
- [ ] 日更 cron（非 V1 必达）
