# 叶35 mapping recon · 真值只读探针 CMD DRAFT（Option A · **本拍不执行**）

- **角色**：QuantLab AI
- **时刻**：2026-10-27 14:22 ET（America/New_York）；ISO `2026-10-27T14:22:19-04:00`
- **状态**：CMD **DRAFT ONLY** · **本拍不执行**真跑 · EXECUTED_PROBE=false
- **探针**：`docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_MAPPING_RECON_PROBE_VTRUE_DRAFT_20261027.py` sha8 **`2c2226e0`**

## 1. 本拍已执行（验证）

```bash
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python -c \
  'import py_compile; py_compile.compile(
    "docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_MAPPING_RECON_PROBE_VTRUE_DRAFT_20261027.py",
    cfile="/tmp/leaf35_mapping_recon_probe_vtrue_draft_20261027.pyc", doraise=True)'

PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python -m pyflakes \
  docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_MAPPING_RECON_PROBE_VTRUE_DRAFT_20261027.py

PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python \
  docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_MAPPING_RECON_PROBE_VTRUE_DRAFT_20261027.py \
  --dry-compile-only
# expect rc=0；executed_probe=false
```

STOP 验证（本拍已做）：

```bash
# 无 --allow-real-data → rc=3
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python \
  docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_MAPPING_RECON_PROBE_VTRUE_DRAFT_20261027.py

# 缺 .ok → rc=4
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python \
  docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_MAPPING_RECON_PROBE_VTRUE_DRAFT_20261027.py \
  --allow-real-data --arch-ok-path /tmp/does_not_exist_leaf35.ok \
  --out /tmp/quantlab_leaf35_mapping_recon_vtrue_should_not_write
```

## 2. 拟真跑（**须** Arch 只审本版 + 主签**新**只读探针 `.ok` 后；**本拍不执行**）

```bash
# <NEW_OK> = 未来新签只读探针窗；禁 RESTORED 10927bd9+178e90e9+c1b71e64+245df63f+c5ed13df+5774bb6e+81521fb5+二十票
# <ET_TS> 例：20261027_HHMMSS（America/New_York）
STAMP="<ET_TS>"
OUT="output/ai_factory/_leaf35_mapping_recon_vtrue/${STAMP}"
# 或：OUT="/tmp/quantlab_leaf35_mapping_recon_vtrue_${STAMP}"

PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python \
  docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_MAPPING_RECON_PROBE_VTRUE_DRAFT_20261027.py \
  --universe HILIQ --window x2 --x2-end 20261009 \
  --allow-real-data \
  --arch-ok-path <NEW_OK> \
  --out "${OUT}"
```

硬钉：rss=**1500** 禁抬；peak_proof REQUIRED（STAGE/`RSS_CHECK`）；out **仅** `mapping_recon_vtrue_per_rebal.json` + `.tsv`；**禁** alpha/mask/overlap；**禁**改 `25ae4572`；**禁** `--force`；**≠X2 ACCEPT**；≠叶36。

## 3. 流程门

1. Arch **只审**本真值版（本票）
2. 主令 Arch **新签**只读探针 `.ok`（禁 RESTORED `10927bd9`）
3. AI 持新 `.ok` 执行 §2（方可 `EXECUTED_PROBE=true`）
