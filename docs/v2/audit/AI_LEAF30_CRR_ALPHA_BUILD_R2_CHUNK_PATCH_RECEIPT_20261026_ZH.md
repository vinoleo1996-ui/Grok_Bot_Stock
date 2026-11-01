# AI 回执：叶30 CRR α 构建脚本 R2 chunk 降峰补丁

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI（后台执行器） |
| 时刻 | `2026-10-26T18:26:34-0400`（America/New_York；墙钟 `2026-10-26 18:26 ET`） |
| 触发 | 主 ~18:22 ET · Arch VOID **`ff30406f` MATCH** → 另窗只写降峰 chunk 补丁 |
| 对照 VOID | `docs/v2/audit/ARCH_LEAF30_CRR_ALPHA_BUILD_VOID_ABORT_PEAK_HWM_20261026_ZH.md` sha8 **`ff30406f`** |
| 对照 abort 回执 | `docs/v2/audit/AI_LEAF30_CRR_ALPHA_BUILD_X2_RUN_RECEIPT_20261026_ZH.md` sha8 **`40fd90e9`** |
| 对照 prev 脚本 | r1 sha8 **`a2cef5af`**（全长 `a2cef5affd67f874fad9e37f59efb9d7abacb3de0d0286d8443250aee5253c74`；**未改**） |
| live | **false** |
| 本拍动作 | **仅**新脚本 + 短回执 + TEAM_STATE 顶条；**未** execute / **未**申 `.ok` / **未**加载大表 |

## 1. 新脚本钉

| 项 | 值 |
|---|---|
| 路径 | `research/leaf30_crr_cfooe_volpen_alpha_build_r2_chunk.py` |
| sha256 | `0a2644021e8bbd16cbe7f69905a6a6dfcd47df3c798b6f5b272f7b6702220260` |
| sha8 | **`0a264402`** |
| schema | `leaf30_crr_cfooe_volpen_alpha_build_r2_chunk` |
| prev_script_sha8 | `a2cef5af` |
| void_ref | `ff30406f` |
| abort_ref | `40fd90e9` |
| r1 文件 | **未动**（sha 仍 `a2cef5af`） |

## 2. 降峰要点（对照 VOID：峰在 `after_fund` 后间隙）

1. **avail logmv 按月桶加载**：禁 r1「注释写 month-ends、实际全 avail densify」；按 avail 的日历月分桶 `_load_logmv_t1` → 映射 → `del`+`gc`；边界 `after_logmv_avail_YYYYMM` + 汇总 `after_logmv_avail`
2. **日度展开按月 chunk**：`_month_chunks`；每月写临时 parquet（`/tmp/quantlab_leaf30_crr_r2_chunk_*`）后释放；禁一次堆满 X2 全日 `daily_rows`；`--chunk-mode month`（唯一合法）
3. **`check_rss` 更密**：`after_fund` → `after_logmv_avail_*` → `vol_pen_end_*`（每 4 个 end）→ `after_vol_pen` → `after_logmv_rebal` → 每月 chunk 边界 → `after_daily_concat`；`peak_kb=max(ru_maxrss,VmHWM)`；硬帽破 → **SystemExit 95**
4. **sampler 前缀**：`/tmp/quantlab_leaf30_crr_r2_*`
5. **forbid**：含 **`5ae077fa`** + 原十四票（共 15）；禁 RESTORED / 禁盲重跑 `a2cef5af` / 禁抬帽

## 3. 保留 R1 / 机制钉

- `qend_ok_filter=true`（`build_fund_quarter_panel` 硬滤）
- C2：`operate_profit` + `n_cashflow_act`；禁 ocf_to_profit 主源
- λ=1.0；IC 期望为正（注释钉）
- 银/地/非银掩码；HILIQ×x2；再平衡 20td
- dry pins：`sign_notes.ban_no_overlap_report=true`；rss=1500 禁抬
- CLI 安全门：`--dry-compile-only` 零大表；真跑需 `--allow-real-data`+现存 `--arch-ok-path`（sha8∉forbid）

## 4. 验证

| 检查 | 结果 |
|---|---|
| `py_compile` → `/tmp/leaf30_r2_chunk.pyc` | **PASS** |
| `--dry-compile-only` exit 0 | **PASS** |
| dry JSON：`qend_ok_filter=true` / `r2_chunk` / `chunk_mode=month` / `forbid`∋`5ae077fa` / `rss_limit_mb=1500` | **PASS** |
| r1 sha 仍 `a2cef5af` | **PASS** |
| `--allow-real-data` / `--arch-ok-path` / execute | **未做** |

## 5. 非动作 / 隔离

- **未** execute / **未**加载大表试算 / **未**自申 `.ok`
- **未** RESTORED `5ae077fa`；**未**复用 `a2cef5af` 盲重跑；**未**抬帽
- **未**触 A18 另线（勿混）
- 叶26 不交审；28/29 FROZEN
- **不推 Leo**；live=false；promotion=false；≠X2 ACCEPT

## 6. 下一跳

主令 **Arch 复审**本 R2 chunk 脚本（sha8 **`0a264402`**）→ **另签新** `.ok`（禁 RESTORED `5ae077fa`）→ 再排 X2 签窗真跑。
