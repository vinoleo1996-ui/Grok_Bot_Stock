# Alpha 复核：叶23 r2.7 / 叶24 r6（FIX6，回应 FIX5 复核 486496a9）

- 复核人：QuantLab Alpha；时间：2026-10-18 03:4x ET；方式：只做静态审查（diff 回放、grep，在 /tmp 跑自写的 AST 检查和 pyflakes），**没有运行任何项目代码，也没有读数据**。research/__pycache__ 前后都是 22 个文件。
- 复核对象（sha 全部一致 ✔）：
  - 叶23 `research/g1g5_sue_desens_cs_alpha.py` = 3d094e22d3af3e3cfe4d3c6164fc3d817c93cb92edfc339db2a156981933adc1
  - 叶24 `research/g1g5_imax_intraday_alpha.py` = 6e46c01cd7268aa549a8d900d78c434b017b25d3cea62c3340754264c4d85c05
  - diff `docs/v2/AI_LEAF23_24_FIX6_DIFF.patch` = 3679d72026d1cc43e4505dac2b45fdb5f28472a3f8cdbdce7449294ce0d1dbb8
  - 归档 `_recovery/ai/pre_fix6_0331/`：叶23 = 60393573…（r2.6）、叶24 = a2719e5c…（r5），和 FIX5 复核时的 sha 一致
- patch 回放：用归档版对现版重新做 diff，增删行集合和 patch 完全一致（两叶各 117 行 diff）。

## 裁定：**PASS**

P1-1 已修好。P3-1、P3-2、P3-3 都按建议落实，语义没有变化。diff 里没有其他改动，预注册没改，FIX5 的 7 项仍然成立。剩下两条记录（R-1、R-2）不阻断，不需要再出版本。

## 逐项核对

### P1-1 模块加载时 NameError → 已修 ✔
- 叶23 L90、叶24 L78：新增 `X2S, X2E = "2024-06-03", "2026-10-09"`，放在 OK_FIXED 之前，值不变。原来那一行只剩 `FUND_YEARS = (...)` / `YEARS = (...)`，值也不变。
- **自写的 AST 检查**（逐条走模块顶层语句；跳过函数和 lambda 体，但默认参数、装饰器、推导式第一层迭代器照算）：
  - 旧版 r2.6/r5：查出 `X2S/X2E` 先用后定义（叶23 L92、叶24 L80），和 FIX5 复核结论一致，说明这个检查有效。
  - 新版 r2.7/r6：**两叶都没有先用后定义的名字**。
  - `if __name__ == "__main__":` 是最后一条顶层语句（叶23 第 90/90 条，叶24 第 89/89 条）。argparse 在这个块里，执行时所有全局名都已定义，所以 `--help` 不会再报 NameError。
  - 模块顶层只调用了 Path、hashlib、re.compile、range、tuple、NormalDist、resource、sys.path.insert，没有 import 时就执行的 I/O 或项目调用。
- pyflakes（/tmp）：`X2S`/`X2E` 和 FIX5 新增的 2 条 `RR` 告警都没了。剩下的 `parts`、`r0` 还是「lambda 引用了随后被 del 的名字」那类误报，调用都在 del 之前，以前就有。

### P3-1「约 8 名」→ 已删，换成运行时计数 ✔
- 叶23 L752、叶24 L685 的披露已删掉「约 8 名」，改为「以运行时 diag 为准」，并列出主口径和影子口径的字段名。静态参考数字（93 名、其中 76 名相差超过 1 天、delisted_master 63590f23）和 FIX5 复核原文一致。全文件再搜「约 8」，只剩叶23 L747 原有的「HI_LIQ 池约 800 名」，和这里无关。
- 新增的影子计数（叶23 L460–461 / L517–519，叶24 L431–432 / L488–490）：
  - 写法 `cy = S_nc & ~S_dd & gone_dd & ~has`，按 X2 窗口 [s, e] 截取后逐名累加。它和主口径的 `cx = S_nc & ~S & gone & ~has` 完全对称，只把 S 换成 S_dd、gone 换成 gone_dd。
  - S_dd 在拼接时已 `fillna(0.0)`，`astype(bool)` 不会把 NaN 当成 True。gone_dd 和 S_dd 都是当年的 days × names 帧，形状一致。
  - 新增 diag 键：`delisted_cut_names_x2`、`delisted_cut_name_days_x2_shadow_last_trade_date`、`delisted_cut_total_x2_shadow_last_trade_date`、`delisted_cut_names_x2_shadow_last_trade_date`。这些都只进 diag，只用于披露，不进判定。

### P3-2 只建一份收益透视表 → 已落实，语义不变 ✔
- `pool_benchmarks(panel, PX, col, carry_col, rr, s, e)`：函数里 `idx = rr.index`（叶23 L417、叶24 L388）。原来调用方传的就是 `rr.index`，所以 idx 完全相同。递推、Mp/wv/Mpo/Mp2 的索引都不变。
- 函数里 `RR = rr.reindex(columns=U).fillna(0.0)`（叶23 L530、叶24 L501），通过 `r0=RR` 返回。evaluate 改为 `r0 = pb["r0"]`（叶23 L776附近、叶24 L708附近）。
- 和旧版逐项比：
  - 旧版函数内是 `PX.pivot_table(...ret).reindex(index=idx, columns=U).fillna(0)`。pivot_table 默认就按索引排序，idx 又等于 `rr.index`（rr 本身就是同一个 pivot 再 `.sort_index()`），所以两者数值完全相同。
  - 旧版 evaluate 的 `r0 = rr.reindex(columns=U).fillna(0.0)` 和现在函数里的 RR 是同一个表达式。
  - 收益（当日 ret，没有平移）、窗口（`.loc[s:e]`）、Mp = S.shift(1) 的 T−1 成员关系、wv 的 T−1 市值都没变，PIT 和前瞻性质也不变。
  - `reindex` 返回新对象，函数没有原地修改 rr。
- 结果：pivot_table(ret) 现在只算一次（evaluate L771/L703）。原来函数内的第二份 pivot 和 evaluate 里的再次 reindex 都已去掉。

### P3-3 过时注释 → 已改，措辞准确 ✔
- 叶23 L84、叶24 L72 的注释改为「passed Arch review bbfcb7ef; full-run .ok not yet signed」。
- 披露（叶23 L750、叶24 L683）改为「r3 已过 Arch 审 bbfcb7ef，selftest .ok fa45bf7f 已签，全量 .ok 未签」，和 Arch 03:2x 的回执一致。
- 「NOT yet Arch-signed」和「尚未经 Arch 签发」在两个文件里都已搜不到。

### 其他
- **没有其他改动**：两叶的 diff 只有上面四处，外加对应注释。
- **预注册没改**：叶23 = 8f5d8ac43ba49f11…，叶24 = c289e77068be607c…。
- **FIX5 的 7 项仍然成立**：
  - CMC v1.1 = 5658f612…、legacy = bee23019…，和实际文件 sha 一致。
  - cmc_cmd_ok、authorize 里的断言、TOOL_CMDS f-string、v1.1 披露文字、delist_date 主口径和影子字段名都没动，也没有 s8 键。
  - 风格集（lmv1/beta120 shift(1)、mom shift(21) rolling(100)、ladv1 不再 shift、叶23 的 acap 按名 shift(1)、叶24 的 vol20 shift(1)）都不在本次 diff 里。

## 记录（不阻断，不需要再出版本）
- **R-1**：P3-2 以后 evaluate 里同时存着 `rr`（全部代码 × idx 的原始 pivot）和 `r0`（U 列、填 0 的副本）两张表。和 FIX5 比少了一份 pivot 和一次重复 reindex，内存只减不增。
  - 叶24 后面已经不再用 rr（只剩 L718 的 del），以后可以在 pb 返回后马上 del rr。叶23 L786 还要用 `rr.index`，可以改成 `r0.index`。
  - 峰值 RSS 以运行回执为准，1.5GB 守护会兜底。
- **R-2**：叶24 L709 的 `U = pb["U"]` 现在没再被用到（pyflakes 报「assigned but never used」），只是一个死变量，不影响结果。下一版可以顺手删掉。

## 结论
- 叶23 r2.7（3d094e22…）和叶24 r6（6e46c01c…）静态复核 **PASS**。
- 全量 .ok 可以按这两个 sha 签。dep_combo_sha256 = 5658f612fef313fc5b818fc4cb9d594d757377e0dbf7c7dc86a6e31788b88911，dep_combo_legacy_sha256 = bee230199ac27bf9730aa77c63b104a67bb104229622c57524867a9b54a5c51c（只作对照列）。运行顺序和资源约束按 Arch 规定。
