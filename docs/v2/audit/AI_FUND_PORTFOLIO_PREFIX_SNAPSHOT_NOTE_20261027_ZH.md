# fund_portfolio 冻结前缀字节快照说明（C1 · 2026-10-27）

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI（执行器） |
| 时刻 | 2026-10-27 ~21:30 ET（America/New_York） |
| 触发 | 主裁 HOLD who_pays→X2；Arch 附录审 `b410680b` PASS_WC → C1/C2 |
| 范围 | **仅**前缀快照与说明；**未**改 WHO/ALLA「## 计数附录」以上任何条款字节 |
| 叶38 | **未混** |

## 1. 历史冻结全文钉（sidecar / 文内）

| 钉 | 来源 | 全长前缀 | 盘上可复算字节？ |
|---|---|---|---|
| WHO 冻结全文 `a7add1185270bad77cbe6157d211e9c6faad67ec06c7780d2aca5e5b96fb6f36` | `docs/v2/AI_G1G5_FUND_PORTFOLIO_WHO_PAYS_PREREG_ZH.md.sha256` 文面钉 | `a7add118…` | **ABSENT**（git 无该路径历史 blob；docs/output/tmp/stores 全盘检索无 sha8=`a7add118` 文件；现盘全文=`604d777d`；附录前缀≠该钉） |
| ALLA 条款前 `ee7bfc79…` | Arch 审 `b410680b` / RERUN RECEIPT 文内钉 | `ee7bfc79…` | **ABSENT**（盘上 ALLA `.sha256` 现文面为 `09eff235…`，**既非**现全文 `0cbfacd9` **亦非**现前缀 `9a90c4eb`，亦无 `ee7bfc79` 字节快照；**禁止伪造** `…_HIST_ee7bfc79.bin`） |

结论：历史全文钉仅存于 sidecar/文内引用；**找不到**等于 `a7add118` / `ee7bfc79` 的历史全文 → 记 **ABSENT**，不造假。

## 2. 现盘「## 计数附录」前缀（本拍可复算快照）

因历次**仅追加/替换附录**，现全文 ≠ 历史冻结全文钉；**条款前缀字节以本快照为准**。

| 件 | 快照路径 | nbytes | sha8 | 全长 sha256 |
|---|---|---:|---|---|
| WHO | `docs/v2/audit/AI_FUND_PORTFOLIO_WHO_CLAUSE_PREFIX_SNAPSHOT_20261027.bin` | 5618 | **`05346562`** | `053465623702bc176cfc6e192c03cc9bb81a20435d732715b1bc3d734732858c` |
| ALLA | `docs/v2/audit/AI_FUND_PORTFOLIO_ALLA_CLAUSE_PREFIX_SNAPSHOT_20261027.bin` | 2700 | **`9a90c4eb`** | `9a90c4eb6c3448af3b9ceaa9ba1e83f88f5c641ce70d679bfd5c04626165f337` |

旁路：`*.bin.sha256`（写全长）。复算：`sha256sum` 切点 = 文件内首次 `## 计数附录` UTF-8 字节之前。

## 3. 对照 Arch

- Arch：`docs/v2/audit/ARCH_FUND_PORTFOLIO_COUNT_APPENDIX_RERUN_REVIEW_20261027_ZH.md` **`b410680b`** PASS_WC；COND **C1** 即本闭环。
- C1 **不动**条款；C2 只换附录。

## 4. 禁项

- 未空改冻结条款；未伪造 HIST 快照；未自签 `.ok`；未挂 QUIET；未混叶38；leo_notify=false；live=false
