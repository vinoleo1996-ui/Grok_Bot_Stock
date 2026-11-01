# fund_portfolio 流式合并设计 v1.1 — Arch 正式复审

live=false；promotion=false。
- 审查对象：docs/v2/DATA_FUND_PORTFOLIO_STREAM_MERGE_DESIGN_v1_1_ZH.md
- 设计 sha256：4a46df7f61a281efd74ec1d0abc126aa681cdd435ee3dfd5a0ab40eed8c1815f（251 行）
- 基线 v1：b78cc9e1…（未改）
- 闭合预备复审：5a79b7e2…
- 审查时刻：2026-10-25T00:20:52-04:00
- 方式：只读静态；未改代码、未读真实 parquet 行、未发信号、未签运行 .ok

## 结论

**PASS**（正式；去掉「预备」）。C1–C8 均已在正文闭合；O1–O6 已按预备裁定落盘。Eng 可按本文实现；**改码提交前**须另签实现审阅 .ok，**开跑前**另签单次运行 .ok。今晚（主 00:14）除已闭合 BACKUP_PIN 外不签运行类 .ok。

## C1–C8 核对

| ID | 结果 | 说明 |
|---|---|---|
| C1 | 闭合 | §2.1：强制批路径；BATCH_MAX_FILES=128 且 BATCH_MAX_ROWS=400000 同时生效；批间 del；单文件超行单独成批；超 1e6 kB abort 21；常量回显 manifest |
| C2 | 闭合 | §4.1：path+sha 双钉；sha 不符 exit 28；自测强制 /tmp 合成日历；禁止隐式活路径 |
| C3 | 闭合 | §3+§9.3：省略无键 drop；路径 A/B 键集合夹具必过，不一致则改回保留无键步 |
| C4 | 闭合 | §1.1：新 CLI；启用后 L96 → RuntimeError("disabled") |
| C5 | 闭合 | §2.2：tmp_root 已存在换新 run_id；不 exist_ok；不扫删他 run |
| C6 | 闭合 | §5：manifest/DONE .tmp+replace；DONE==manifest.sha256==表 sha |
| C7 | 闭合 | §8：mem_available_min_kb 只从运行 .ok 读；缺字段 exit 20；默认 2621440 |
| C8 | 闭合 | §10.1：allow_broker_recommend 必须 false；缺省/true → exit 20；不触 Q8 |

## 残留披露（不挡 PASS，进实现审阅核对清单）

1. **期内 acc 仍持有整期**：批间 del 的是 batch_frame，键去重前 acc 可为整期。须在每批追加到 acc 之后采样 VmRSS（§8 已写「每批/每期」）；实现审阅时核采样点代码。
2. **运行 .ok 须钉** trade_cal 现盘 sha（当前钉住件 141078fa…）或当时有效 pin；不得口头约定。
3. **断点跳过**：§0 R6 提及可跳过已有期级产物，与 §2.2「禁止复用同 run_id」并存——实现须明确：仅当**新 run_id** 且 CLI 显式 `--resume-from-period-dir`（指向只读完成期目录）时才允许跳过；默认关闭。缺省关闭不挡本 PASS；若 Eng 加 resume，送实现审阅时写清。

## 下一步

1. Data：v1.1 冻结；勿改 4a46df7f 字节，除非 Arch 再开修订。
2. Eng：按 v1.1 写 `scripts/acquire/fund_portfolio_stream_merge.py` + §9 自测（全 /tmp）；旧 L96 暂不改，直到实现审阅 .ok 生效时改为 disabled。
3. Arch：自测绿后签实现审阅 .ok；开跑另签运行 .ok（含 mem_available_min_kb、trade_cal pin、log 路径、allow_broker_recommend=false、allow_write_events=true）。
4. 主 Agent：恢复链（中转→补拉→freshness→纸面）与本合并可并行设计；真跑合并仍须运行 .ok 窗口。

live=false；promotion=false。
