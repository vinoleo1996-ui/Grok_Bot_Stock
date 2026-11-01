# 叶35 Option B · 份额 PIT 口径补丁 RECEIPT

- **角色**：QuantLab AI 后台执行器
- **时刻**：2026-10-27 14:59:25 ET（America/New_York）；ISO `2026-10-27T14:59:25-04:00`
- **结论**：DRAFT 包已落盘 · **EXECUTED=false** · 正式 **`25ae4572` UNCHANGED** · 交主→Arch **只审** · ≠X2 ACCEPT · ≠叶36

## 1. 交付物

| # | 路径 | sha8 | 全长 |
|---|---|---|---|
| 1 | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_SHARE_PIT_PATCH_DRAFT_20261027_ZH.md` | `bdfd3c56` | `bdfd3c56ca38591db842e3167176e683f7ed45d7564fb0672dbde98e5f701043` |
| 2 | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_SHARE_PIT_PATCH_COVER_DRAFT_20261027_ZH.md` | `8ea77257` | `8ea772576fdf6add2a7054ec2cec891b05fd0b9800057c324db1e14183810a84` |
| 3 | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_SHARE_PIT_PATCH_DIFF_DRAFT_20261027.diff` | `2d3abebd` | `2d3abebd4032adacc6905b0db935305e1e9c767391a30540470341f217acf8c7` |
| 4 | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_SHARE_PIT_PATCH_RECEIPT_20261027_ZH.md` | （盘上 `sha256sum`） | （盘上 `sha256sum`） |
| 5 | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_SHARE_PIT_PATCH_CMD_DRAFT_20261027_ZH.md` | `8d35a619` | `8d35a6194dd3cc2a2e64f76dbab9766e3045b468954236fd6d8bc822adbf3813` |

## 2. 正式 / 叶33 / live 状态证明

| 检查 | 结果 |
|---|---|
| 正式脚本 sha8 | **`25ae4572`** MATCH · 全长 `25ae45723454423a31d4b0c6987c5eb0a2e8bb733c2506c2db67d628e91b4ad0` |
| 叶33 正式 sha8 | **`afbbe7e7`** MATCH · 全长 `afbbe7e7292c17399bbf4733d9f34a922e6d81f1a914a60d24dc61fcba86cbc9` |
| live `output/ai_factory/*.ok` | **0**（ABSENT） |
| live `output/loop/RESEARCH_QUIET.lock` | **ABSENT** |
| DIFF header | 含 `DRAFT ONLY — DO NOT APPLY` |
| DIFF 是否含 parquet API 误改 | **否**（保持 `pq.read_table`） |
| DIFF 是否应用到 research/ | **否**（仅 /tmp 拷贝 diff -u） |
| `patch -p` / git commit / TEAM_STATE | **未做** |
| RESTORED 旧票 / 复跑 X2 / Book-Smoke / 写 alpha | **未做** |

## 3. 上游闭环

| 项 | sha8 |
|---|---|
| CONSUMED_PASS **现算** | `0471f4f8`（全长 `0471f4f85c0b62eb69a64a88ef01c2e33a4acc56eb65e2bbc7562ec17f5b42e7`） |
| CONSUMED_PASS **主钉**（双记） | `bc8f53d7`（≠现算勿瞒；以现算为准） |
| consumed `.ok` / QUIET lift | `00eec671` / `9306ceff` |
| VTRUE RECEIPT / JSON / 探针 | `107a72b1` / `446b60d1` / `2c2226e0` |
| PIN / FROZEN / ArchFROZEN | `dd17044a` / `be9fc459` / `5a082d18` |

## 4. 推荐与门禁

- **推荐 Option B1**（对齐 PIN §1.3）
- B2 不推荐；B3 须主裁（本票不推）
- 落地：Arch 只审 → 主令新脚本（≠`25ae4572`）→ Arch 审脚本 → 主签**新** X2 `.ok`
- EXECUTED=false；≠X2 ACCEPT；≠叶36；leo_notify=false；live=false

## 5. DIFF 拟改摘要

- `_load_etf_flows_window`：窗 `[min(rebal)−40d, max(rebal)]`，取消 `isin(rebal_days)`；**保持** `pq.read_table`
- `_pressure_on_day`：`available_at_clock≤t_ts ∧ trade_date≤d`，按 ETF 最新 avail；取消 `trade_date==d`
