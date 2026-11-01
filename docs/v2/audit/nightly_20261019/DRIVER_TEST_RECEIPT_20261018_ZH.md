# 10-19 驱动集 测试记录（Data，2026-10-18；按 Arch 11:33 (C) 要求记录命令与假文件生成方式）

- 原则：所有拒绝路径与辅助函数测试只用 /tmp 下的副本或假文件，路径以参数 / 模块变量传入；不读真实数据、不 import 读数据的项目代码。
- 例外（已自报）：11:24 ET 曾对真实 data/v2/tushare_raw/trade_cal.parquet 运行一次 cal_restore_v2 拒绝路径（无 .ok）：命令 `python3 ../cal_restore_v2.py --backup bk --target /workspace/QuantLab/data/v2/tushare_raw/trade_cal.parquet --expect-sha ba7816bf… --keep-rewritten-dir /tmp/qd1018/rt/keep`，脚本在任何读写目标之前退出 2；事后 sha256 仍为 141078fa…。主 Agent 已报 Arch；此后不再重复。

## 1. cal_restore_v2.py（6686876b…，本轮未改）
- 假文件：`printf abc > /tmp/qd1018/rt/bk`；`printf xyz > /tmp/qd1018/rt/tgt`；`mkdir -p /tmp/qd1018/rt/keep`（bk 的 sha256 = ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad）。
- `python3 /tmp/qd1018/cal_restore_v2.py --backup bk --target /tmp/qd1018/rt/tgt --expect-sha ba7816bf… --keep-rewritten-dir /tmp/qd1018/rt/keep` → rc=0，目标变为 abc，留存副本 sha 与原目标一致。
- 同上不带 --expect-sha（默认 PIN）→ rc=2「备份 sha 与期望不符，目标未动」。

## 2. run_nightly_v1.py 预稿（5c9fbeda…）—— 已被本轮修订取代
- /tmp/qd1018/tdrv.py：pyarrow 生成假 parquet（列 x = range(n)）于 /tmp/qd1018/fx/raw/<api>/<日期>.parquet：20261016 各接口 5500 / 5490 / 5600 / 7000 / 10 行；20261019 为 5480 / 3000 / 5600 / 7000 / 0 行；另写 1 字节假 20261019.tmp.parquet；假日历 /tmp/qd1018/fx/tc.parquet（cal_date 两行）。模块变量 RAW / RUN_DIR / MARK_DIR / TRADE_CAL 指向 /tmp。

## 3. run_nightly_v1.py 修订版（a7292a61…）
命令：`python3 /tmp/qd1018/tdrv2.py </dev/null`、`python3 /tmp/qd1018/tdrv3.py </dev/null`（均对暂存副本 /tmp/qd1018/run_nightly_v1_r.py，内容与安装版 sha 相同）。
| 编号 | 假文件 / 设置 | 结果 |
|---|---|---|
| T1 | /tmp/qd1018/fx2/markers 空 | marker_precheck → None |
| T2 | 写假 nightly_20261019.DONE.json（内容 {}） | 拒绝「DONE marker 已存在」 |
| T3 | 写假 FAILED.json；假 .ok /tmp/qd1018/fx2/fake.ok 依次：无键 / true / 64 个 0 / 正确 sha | 前三种拒绝；正确 sha → 通过 |
| T4 | 同上 | supersede_failed：同盘移到 markers/_superseded/nightly_20261019.FAILED.<sha12>.TEST.json，原位不存在 |
| T5a | 假锁 /tmp/qd1018/fx2/loop/RESEARCH_QUIET.lock 已存在 | 沿用，created_by_data=False |
| T5b | 无锁、未授权 | 拒绝（.ok 未授权 allow_create_research_quiet_lock_20261019） |
| T5c | 无锁、授权、dry | would_create=True，未写文件 |
| T5d | 无锁、授权 | 按 Arch 模板写出 5 行 ASCII LF：owner=Arch_by_Data / purpose / set_at / release_when / set_by_pid；全文 ASCII；源码中无 unlink(QUIET_LOCK) |
| T5e | 锁已存在时再 write_new | FileExistsError，不覆盖 |
| T6a/b | 假 RAW 空目录、假日历 | 第一次 write_marker → FAILED.json；第二次 → FileExistsError（不写第二份） |
| T7 | — | PROFILES：strict 06:20/06:30/55、无重试；relaxed 无墙钟截止 / 30 分钟 / 16:00 / 55 / 重试 / 间隔 30；两档 relay_partial_ok=False |
| tdrv3 | 同 §2 假 parquet（/tmp/qd1018/fx3） | daily_basic 3000 < 0.98×5490 判不合格；.tmp 残留识别；未授权只报；授权后两文件隔离（sha 前后一致）；再查 daily_basic 缺文件 |
| ast | `python3 -c "import ast; ast.parse(...)"` | 通过 |
未测（需真实进程，留待 Arch 审后在 .ok 下首跑）：run_nightly / stop_tree 对真实 nightly 进程的停止序列、healthz 等待、call B 闸门的墙钟判断。stop_tree 的 cmdline 不符拒发逻辑曾以 `bash -c "sleep 30 & sleep 30 & wait"` 在方案 R 执行器中自测（同一实现）。

## 4. 测试脚本 sha256
```
16cf0c72f0f9ed501682d9660bebaa515162b23ca8a402a0810642347b808cfe  tdrv.py
67d06474192d8702532a5b701a4927e67e1bdb832cd27730b57f6c3d6fefa797  tdrv2.py
a4eed340138f802a776f0b052b24886c4e0fb75270194e597315ccee5da1fcbd  tdrv3.py
f26aa248a919cb66794d43189d9180155927dcbb57fd64abff86b1942c9bdf29  t.py
6dc629ee89ed99aaab5aa398c9a0c39e98c54f9e9dba12b35e3f222fe33a625e  t3.py
9fa9845de837a9e7db799fc518f8531bca784ef1823005aca2ed18ab8334fc2c  t4.py
dc39bbfb4115b863716d48413e8d1e852e60b5a2721b5025df6f17b371b03509  mk_restore_v2.py
dc9a6700c3cea7e0ca65838cd89e72ca5751ded1a0573f3b2c96cf87f104963f  splice.py
aad3cafd74e75bedc5ce9a5f53c28dedb9d9c07aa2c1064c62b3eddf5c586f23  install_drv.py
```
