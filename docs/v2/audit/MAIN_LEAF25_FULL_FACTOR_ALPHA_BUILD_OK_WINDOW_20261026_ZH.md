# 主 · 叶25 全叶 HILIQ×x2 alpha 构建 · 签窗令

| 项 | 值 |
|---|---|
| 角色 | 主 Agent |
| 时刻 | `2026-10-26T01:31:44-04:00`（America/New_York） |
| Arch 审 | `dd68765e` **PASS_WITH_CONDITIONS** |
| 交审令 | `504b6a9d` |
| 脚本 | `de7b3647`（全长 `de7b36477908ee522c73e71db64ac904356d7a65c420ea897332925c36427856`） |
| 签窗 | **2026-10-26 01:45–02:30 ET**；expires **02:32 ET** |
| 拟 `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF25_FULL_FACTOR_ALPHA_BUILD_HILIQ_X2.ok`（**现不创建**） |
| 票种 | 全叶 alpha 构建（≠ selfcheck；≠ Book-Smoke；≠ X2 ACCEPT） |

## PRIMARY CLI（签文必须逐字；开跑另加 auth 旗）

文档钉（dry 形态）：
```
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf25_full_factor_alpha_build_r1.py --universe HILIQ --window x2 --x2-end 20261009 --chunk-mode month --out output/ai_factory/_leaf25_full_factor/<ET_TS>/
```
实跑另加：`--allow-real-data --arch-ok-path output/ai_factory/ARCH_RUN_AUTH_LEAF25_FULL_FACTOR_ALPHA_BUILD_HILIQ_X2.ok`

## 包钉（签时复核）

COVER `07b0a1b8` · CMD `8ab8831c` · DIFF `03d50f3f` · HAND `21bf0d41` · VERIFY `d6750c94` · H2A `2ac86676`  
继承：旧 CMD `035e5818` · r6令 `53331667` · FROZEN `4bb1ff2b` · 基盘 `e8ca2bcc` · MEM `103717df`

## `.ok` 硬钉（CONDITIONS）

1. script 全长 `de7b3647…`；PRIMARY HILIQ×x2×end `20261009`×month；须 `--allow-real-data --arch-ok-path`
2. rss 软帽 **1500** 禁抬；peak_proof **REQUIRED**；ABORT→停+上报
3. **PIN_GAP** 写入签文：β120/mom/logADV20/vol20 未齐；勿称全残差；CFACC TTM+desens 已实装；overall=PARTIAL
4. sampler 前缀硬钉 `/tmp/quantlab_leaf25_full_alpha_*`
5. forbid 十一票：`1c32ab1e` + 八票 + `3c19dd7d` + `6054b3bf`（禁 RESTORED）
6. HAND/H2A 签时钉盘上全长；≠X2/≠selfcheck/≠Book-Smoke
7. 签时挂 QUIET；入窗后签发；过 expires **禁签**

## 角色

- **现不签 / 现不挂 QUIET / 不代跑**
- Arch：入窗签发拟 `.ok` + 挂 QUIET → priority 回主
- 主：MATCH `.ok`+QUIET 后令 AI prelaunch 单次
- AI：停等；禁自开跑/禁自申.ok/禁抬帽
- live=false
