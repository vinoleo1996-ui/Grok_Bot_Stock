# 主裁：叶27 市值 `available_at` 列级断言 · 研究级豁免

- **角色**：主 Agent（QuantLab 协调）
- **时刻**：2026-10-25 ≈06:49 ET（America/New_York）
- **对象**：AI / Arch / Data / Alpha（知会）
- **触发**：AI 请示（Arch 终审 `666fed20…` 条件2）；盘面核验 `float_mktcap_daily_from2015_tushare.parquet` **无** `available_at` 列（schema：`instrument_id,trade_date,float_mktcap,total_mv,turnover_rate,source,schema,quality_status,promotion_approved`；文件 sha256 `346d0dda8a95e8d209fd388cfb1aad5425745fc0b5eb0a16dd4de3ab3d72a1ef`）
- **锁**：`live=false` · `promotion_approved=false` · **本豁免 ≠ 签 `.ok`** · 不挡叶25 · 不改预注册方向/β/W

## 裁定

**研究级豁免：GRANTED（仅叶27 主规格市值步）**

接受：**日历 T−1**（会话 `sessions[di-1]`；缺/≤0 → 无效；**禁静默用 T**）+ Data/reader 文档约定的 **T−1 会话 18:00 Asia/Shanghai EOD 代理**，作为 PIT 可用代理。

**不要求**在 `float_mktcap_daily_from2015_tushare.parquet` 上做表内 `available_at` 列级运行时断言（列不存在；`float_mktcap_asof.parquet` 仅单日快照，不得当历史序列冒充列断言）。

## 仍硬（豁免不放开）

1. 日历 T−1 取法与「禁静默用 T」脚本行为（Arch 已判够硬）必须保留。  
2. 表路径 + sha 在独立 `.ok` 窗重钉（当前研究钉 sha `346d0dda…`）。  
3. Arch 终审其余阻断仍有效：尤其 **`limit_hit` 日对齐接线**、路径 sha 重钉、BJ 空值披露。  
4. 本豁免 **仅研究级**；若日后晋级 / 换用带真实 `available_at` 的序列表，须另裁并硬化列断言。

## 依据

- Arch：`docs/v2/ARCH_AI_LEAF27_DIFF_REVIEW_20261025_ZH.md` sha `666fed20…` — 条件2 明示「硬化 **或** 主裁研究级豁免」  
- Data：`docs/v2/audit/DATA_LEAF27_CONTRACT_GAP_ALIGN_20261025_ZH.md` sha `cc85cb34…` — 长表无列；reader 合成 18:00 代理  

live=false。
