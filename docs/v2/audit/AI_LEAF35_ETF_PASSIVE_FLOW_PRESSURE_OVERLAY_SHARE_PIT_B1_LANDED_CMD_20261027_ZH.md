# AI CMD：叶35 B1 落地脚本（现不可跑 X2；须新 `.ok` + Arch 只审新脚本后主签窗）

| 项 | 值 |
|---|---|
| 时刻 | **2026-10-27 15:11 ET**（America/New_York） |
| 正式脚本 AFTER | **`434ff42c`** / `434ff42c1ba7998e122e0ded4f984c98d40ecbfc12f124afe7ef99742bd69b0a` |
| 正式 BEFORE | **`25ae4572`**（VOID/对照钉；禁 RESTORED 当新窗脚本） |
| Arch 补丁审 | **`31a08790`** PASS_WC；endorse B1 |
| DRAFT / DIFF DRAFT | **`bdfd3c56`** / **`2d3abebd`** |
| LANDED DIFF | **`06a202c3`** |
| EXECUTED_X2 | **false** |

## approved_cmd_dry（本拍已执行）

```
python3 -c "import py_compile;py_compile.compile('research/leaf35_etf_passive_flow_pressure_overlay_alpha_build.py',cfile='/tmp/leaf35_b1_land.pyc',doraise=True)"
/tmp/ql_pyflakes_venv/bin/pyflakes research/leaf35_etf_passive_flow_pressure_overlay_alpha_build.py
```

- dry-compile **PASS**；pyflakes exit **0**

## 拟 approved_cmd_X2（**现不可跑**；须 Arch 另票只审新脚本 `434ff42c` → 主签**新** `.ok`；禁 RESTORED）

```
# PLACEHOLDER ONLY — DO NOT RUN THIS BEAT
# PYTHONDONTWRITEBYTECODE=1 python research/leaf35_etf_passive_flow_pressure_overlay_alpha_build.py \
#   --universe HILIQ --window x2 --allow-real-data \
#   --arch-ok-path output/ai_factory/ARCH_RUN_AUTH_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_X2_HILIQ.ok \
#   ...
```

- **禁** RESTORED `00eec671`+`10927bd9`+`178e90e9`+`c1b71e64`+`81521fb5`+旧票
- rss=1500 禁抬；peak_proof REQUIRED；C11 overlay≠叶26；≠X2 ACCEPT
- 本拍 **EXECUTED_X2=false**；ok_requested=false；leo_notify=false；live=false
