# LOTFIX v1.4 冻结记录附录 · CLARIFY-1（运行前澄清，仅追加）

- 写入时间：2026-10-18 01:59 ET（America/New_York, UTC-4）；裁定来源：主 Agent 01:59 ET 书面裁定；记录人：QuantLab Arch
- 性质：仅追加的附录文件。冻结文件字节未改动：
  - 冻结文档 STRATEGY_OPTIMIZER_STAGE2_LOTFIX_DRAFT_ZH.md：sha256=d921dd3f0f698deb822a59e40aa643f1efc7f43f6c36eaed30c7a672dbdf9425
  - 冻结记录 LOTFIX_V1_4_FREEZE_RECORD_ZH.md：sha256=0d47c52f8be402d02e369d0a92c4ba05d868038f4b3c41870b2bdb8234c52641
- live=false，promotion=false

## 1. 时间先后声明：早于任何 v1.4 结果
写入本附录时不存在任何 v1.4 产出。核查（2026-10-18 01:59 ET 前后，Arch 只读 ls）：
- `ls -d output/strategy_optimizer/core_x2/v1_4*` → `No such file or directory`
- `output/strategy_optimizer/` 与 `output/strategy_optimizer/core_x2/` 下按 `v1_4|v14|1.4` 过滤无任何条目
- 现存 core_x2 内容仅 v1.1–v1.3 相关产物与归档（_archive_v1_*、book_smoke_v1_3_*、ARCH_RUN_AUTH_v1_3.ok 等）
- v1.4 尚无 .ok，未运行过（含 dry-run）。

## 2. 裁定原文（E-1）
v1.4 规格 §8「严格可行」两种都报：(a) 分袖计数（每袖各自严格可行的天数）；(b) 两袖同日都严格可行的天数。判定取更严的 (b)「两袖同日都严格」。本条以运行前澄清修订 CLARIFY-1 写入 LOTFIX v1.4 冻结记录附录，时间早于任何 v1.4 结果；24/29 升级门槛按此口径计。Strategy runner 代码须同时输出两种计数。

## 3. 对 24/29 门槛的影响
- 原文（冻结记录第 5 行）：「100万 任一配置严格可行 <24/29 天或 k=3 触发 → 主 Agent 向 Leo 提 6% 上限」。门槛数值 24/29、80%、k=3 均不变。
- 计数口径明确为：某日计为「严格可行」当且仅当该配置两袖在同一天都严格可行。100万 任一配置的两袖同日严格可行天数 <24（共 29 天）即触发升级。
- (b) ≤ 每袖各自计数，故此口径只会更早触发、不会放宽。分袖计数仅披露，不得用于豁免触发。
- runner 输出须含每配置每档的：sleeve_A_strict_days、sleeve_B_strict_days、both_strict_same_day_days、分母 29，及逐日布尔明细；缺任一项即视为输出不完整，不得判定。

## 4. E-3 运行顺序（有条件批）
- 仅当 Leo 决定 Core 继续：先跑 D21（v1.3 口径 C 重算），再跑 v1.4；两者各需独立 Arch .ok，串行，D21 回执经 Arch 审过后再签 v1.4 .ok。
- Leo 决定停 Core：D21 与 v1.4 均不跑。
- 在 Leo 决定前两者均不签 .ok。

## 5. 相关
- E-2（合成数据单测算运行，轻量 .ok）见 docs/v2/ARCH_RUN_AUTH_SELFTEST_SPEC_ZH.md。
