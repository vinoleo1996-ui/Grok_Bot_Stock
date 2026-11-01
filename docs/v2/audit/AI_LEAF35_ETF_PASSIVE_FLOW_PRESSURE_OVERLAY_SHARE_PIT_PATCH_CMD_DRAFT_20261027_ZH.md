# 叶35 Option B · 份额 PIT 补丁 CMD DRAFT（占位；本拍不执行）

- **时刻**：2026-10-27 14:59:25 ET（America/New_York）
- **状态**：CMD **DRAFT ONLY** · EXECUTED=**false** · 无 `.ok` · 无 QUIET · 正式仍 **`25ae4572`**

## 本拍（只审，不跑）

无真跑命令。仅交付 DRAFT/DIFF/COVER/RECEIPT 供 Arch 只审。

## 落地后（未来；须主令 + 新脚本 sha8 ≠ 25ae4572 + Arch 审脚本 + 新 X2 `.ok`）

### A) dry-compile（占位）

```bash
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python -m py_compile \
  research/leaf35_etf_passive_flow_pressure_overlay_alpha_build.py
# 期望：新脚本 sha8 ≠ 25ae4572；再 pyflakes（若环境有）
```

### B) 未来 X2（占位；`.ok` 路径 TBD；禁 RESTORED）

```bash
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python \
  research/leaf35_etf_passive_flow_pressure_overlay_alpha_build.py \
  --universe HILIQ --window x2 --x2-end 20261009 \
  --allow-real-data \
  --arch-ok-path output/ai_factory/ARCH_RUN_AUTH_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_X2_HILIQ.ok \
  --out output/ai_factory/_leaf35_etf_passive_flow_pressure/<STAMP>
```

约束回放：C3 方案 A；C4 mask-only top_q=0.20；须 overlap JSON；peak_proof；rss=1500 禁抬；C11≠叶26；禁 Book-Smoke；≠X2 ACCEPT。

## 钉

- DRAFT `bdfd3c56` · DIFF `2d3abebd` · 推荐 B1  
- CONSUMED 现算 `0471f4f8`（主钉 `bc8f53d7`）· VTRUE `446b60d1`  
- 本拍不执行上述 A/B
