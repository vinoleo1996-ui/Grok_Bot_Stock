# 叶27 分块装载 · HILIQ×x2 CMD 草案（**未申 `.ok`**）

- **角色**：QuantLab AI（执行器）
- **时刻**：2026-10-25T12:23:09-04:00（America/New_York）
- **状态**：**DRAFT ONLY** · **ok_requested=false** · **不是 `.ok`** · **不替代 Arch 签发** · **禁自开跑**
- **对照**：Arch 审计 P1-4 sha8 `c8877760`；ABORT `5b212115445bdf3a…`；禁 RESTORED `8bcd79dc` / `725be3e0`

## 明确声明

> **本文件未申请、未获得、不构成任何 run/probe `.ok`。**  
> 在 Arch 另审 PASS 且主排新窗并签发**新** `.ok` 之前，**禁止**执行下方 CLI。

## 建议 CLI（待 `.ok` 钉入；现不可跑）

```bash
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python \
  research/leaf27_chunked_members_mktcap_r1.py \
  --universe HILIQ --window x2 --chunk-mode quarter
```

## 硬钉（未来 `.ok` 必须逐字对齐）

| 项 | 值 |
|---|---|
| script | `research/leaf27_chunked_members_mktcap_r1.py` |
| script sha256 | `262f9bf6878d5c64956529a680abbf36e45adfe72fc7dedc4c68dc1c40291a10` |
| universe / window | `HILIQ` / `x2`（**禁** `both`；sealed 另签） |
| chunk_mode | `quarter`（破帽再收 `month`/`ndays`） |
| rss_limit | **1500** MB（**禁抬帽**） |
| 采样 | `/tmp/quantlab_leaf27_chunked_*` only |
| 禁复用 `.ok` | `8bcd79dc…` · `725be3e0…` 及一切 VOID/CONSUMED |
| 禁同 cmd | 旧 `…_lowmem_v1.py --universe HILIQ --window x2` **不可**再签 |

## 与旧 VOID 窗差异（防误复用）

| | 旧 VOID 窗 | 本草案 |
|---|---|---|
| 脚本 | `g1g5_…_lowmem_v1.py` (`05bd81ea…`) | `leaf27_chunked_members_mktcap_r1.py` (`262f9bf6878d5c64…`) |
| 装载 | 644 日一次 `load_*` | 按季分块 + del+gc |
| `.ok` | `8bcd79dc` VOID | **无**（未申） |

## 静态自检（已做；非授权）

```bash
PYTHONDONTWRITEBYTECODE=1 python research/leaf27_chunked_members_mktcap_r1.py --dry-compile-only
# → live:false ok_requested:false rss_limit_mb:1500
```

live=false。
