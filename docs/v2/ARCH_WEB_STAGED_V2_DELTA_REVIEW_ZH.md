# Arch 增量复审：Web staged_v2 v2.1（回应 ARCH_WEB_STAGED_V2_REREVIEW_ZH.md be478ce7）

- 审查人：QuantLab Arch；时间：2026-10-18T10:15:20-04:00（ET）
- 方式：纯静态只读。只用 cat/diff/patch（仅在 /tmp 副本上）/rg/sha256sum/cmp，以及 date 边界实测。未执行任何 staged 脚本，未安装，未发信号给任何进程，未起项目 python，未读 /workspace/QuantLab/data，未递归扫描 /workspace/QuantLab。工作目录 /tmp/arch_webdelta_Xj2U。
- 研究锁 b5e78069 在位，未动。live=false，promotion=false。

## 结论：**PASS**

- C1、C2 都已按要求修好。P3-1 到 P3-11 逐条落实。没有发现新的 P1 或 P2，也没有新的未经静默检查就读真实数据的路径。
- autostart.sh.proposed a97c90fe → ccfbcf81 的改动（cmdline 整串相等）接受，自启提案维持 PASS。
- 新发现 6 条 P3（第四节），都不阻塞安装，下一版处理。其中 N-6 必须在启用自启之前改。
- 安装前提见第五节，全部是流程条件，不需要再改代码。

## 一、核对

- 输入 sha256（前缀全部一致）：staged_v2_rereview_delta.diff = 47e07a79…；staged_v2/SHA256SUMS = db7a6047…；WEB_REVIEW_RESPONSE_ZH.md = f6aaa777…；autostart.sh.proposed = ccfbcf81…。
- `sha256sum -c SHA256SUMS`：19/19 OK。
- **增量 diff 可信度**：用上一轮留存的“线上 → 上一版 staged”diff 在 /tmp 重建了 11 个上一版文件，sha 与上一版 SHA256SUMS（98df4540）逐个一致。再把 Web 的增量 diff 逐文件**反向**应用到新 staged 上：
  - ql_quiet.sh、ql_child.py、start_all.sh、deploy_loop.sh、loop.sh、server.py、export_static.py、autostart.sh.proposed、install_v2.sh、test_v2.sh 反向后都还原成上一版的 sha（d7223b91、77c59aa9、4a2de2e7、44f3b142、dd9ff7d9、c962f240、48a09275、a97c90fe、386c5c92、87680abf）；
  - gen.py、snapshot.py、kline.py 反向后等于线上现行版（7d6cf73c、1b4f8674、b6e6ad79）；
  - ql_atomic.py 是新文件。
  - 结论：增量 diff 完整，没有隐藏改动。
- 未改文件：supervise.sh 55fb3a55、deploy_supervise.sh d6914dc5、keepalive.sh 8efc9862、freshness.py c84fd799、home_v2.diff 737d8ba6，与上一版相同，已核实。
- apis.py 不在本轮范围，静态确认里面没有写文件的代码。

## 二、必改项

### C1 原子写 → 通过

- ql_atomic.py:4-13 write_bytes：
  - 临时文件是 `<目标>.tmp.<pid>`，与目标同目录，所以 os.replace 不会跨文件系统；
  - flush 后 fsync，再 os.replace；
  - 发生任何 BaseException 都删掉临时文件后再抛出。
- ql_atomic.py:14-15：write_text、dump_json 都走 write_bytes。
- ql_atomic.py:16-27 copy：先 copy2 到同目录临时文件，fsync 后再 replace，异常时删临时文件；dst 是目录时自动拼上文件名。
- gen.py 三处写都已改用 ql_atomic：:101 各页 html，:180 图表拷贝，:184 gaps.json。rg 复核 gen.py、snapshot.py、kline.py 中已没有其他 open(...,"w")、shutil、to_csv、to_parquet 写法。
- snapshot.py:165-167：write() 改走 dump_json，原来的固定 .tmp 名和缺 fsync 都已去掉。snapshot.json 和 site/api/*.json 都经这个 write()。
- export_static.py 10 处写全部转换，消息里说 9 处是少数了一处，不影响结论：
  - kline json（:23）；
  - snapshot、api、static、charts 四类拷贝（:27-31）；
  - events、state（:38）；
  - notice（:41）；
  - freshness（:45）；
  - index.html（:47）。
  - 剩下的 os.remove 只是清理旧文件，不是写产物。
- 指纹（export_static.py:50）：basename 含 .tmp. 的文件不计入。
  - site/ 里残留的临时文件名以 .tmp.<pid> 结尾，不会被 export_static 的 `*.json`、`*.png` glob 拷走。
  - 残留在 export/ 的见 N-4。
- install_v2.sh:8 FILES 加入 ql_atomic.py、gen.py、snapshot.py、kline.py。顺序是 ql_quiet → ql_child → ql_atomic → gen…，被依赖的模块先装。安装过程中，旧 server 按路径启动的新 gen.py 能找到 ql_atomic。

### C2 过渡正则 → 通过

- start_all.sh:22、:37 首尾标记“过渡用，v3 删除”。
- start_all.sh:31-33 只在 alive 失败（pidfile 缺失、PID 已死或 cmdline 不整串相等）时才处理：先记日志（pid 和 cmdline），再 rm，然后才走 legacy。
- **能否删掉有效 pidfile**：不能。rm 只在 alive 刚判失败之后才执行。
  - 并发的 start_all 被 flock 互斥（:15-16）。
  - 唯一的理论竞态：守护进程恰好在 alive 判失败和 rm 之间写入自己的新 pidfile，被 rm 删掉。这种情况下 :34 的 legacy 会用锚定正则命中这个 v2 实例（cmdline 同为 `/bin/bash ./supervise.sh`），恰好 1 个命中就重新接管并补写 pidfile，可以自愈，不会重复拉起。接受。
- start_all.sh:25-30 legacy：
  - 去掉了 head -1，全部命中逐个记 `pid=… cmdline=…`；
  - 0 个命中返回 1，交给 spawn；
  - 多于 1 个命中时记日志、不写 pidfile，返回 2，:35 以 exit 5 退出；
  - 恰好 1 个命中才写 pidfile。
  - 符合裁定。
- start_all.sh:18-21、:43：alive 改为整串相等，W_SUP/W_DSUP/W_KA 与 spawn 后 env -i exec 出来的 cmdline 一致。上一轮 P3-6 的子串误中已经消除。

## 三、P3 落实情况

| 项 | 核对 | 结论 |
|---|---|---|
| P3-1 组清扫 | ql_child.py:12-16 用 waitid(WEXITED/WNOHANG/WNOWAIT) 判断退出但不回收；:23-24 已回收就不再发信号；:30-33、:39 组长成僵尸、还没回收时对整组补一次 SIGKILL，再 wait 回收；:96 running() 只看 returncode，不调 poll | 通过。pgid 等于未回收僵尸的 pid，不会被复用 |
| P3-2 宽限期 | :11 GRACE=5，:97 stop_all 也默认 5 秒 | 通过 |
| P3-3 孤儿登记 | :40-44 原子写 run/children.json；:48-68 server 启动时 cmdline 整串相等（去掉 nice 前缀后比对）才 killpg；server.py:258-259 | 通过，见 N-1、N-2 |
| P3-4 畸形窗口 | ql_quiet.sh:21 ALLOW_NOWIN 也要求 QL_QUIET_TEST=1；:25 jq 用 `//` 把空值和 null 归成空串，再 tostring，用 \u001f 拼接；:29-31 先按行读，再以 IFS 为 \x1f 拆字段；:33 start 或 end 为空就判静默；:34 date 解析失败或结果不是整数也判静默 | 通过，见 N-3 |
| \x1f 分隔 | \x1f 不是 IFS 空白字符，连续分隔符不会被合并，空字段能保留。`{}` 会输出两个分隔符组成的非空行，判静默。reason 里含 \x1f 时多余部分并入最后一个变量 rs，不影响 st 和 en。reason 里含换行时会多出一行，那一行 en 为空，判静默（fail-closed） | 正确 |
| 解析失败 | rows 赋值失败且 windows 不是空数组时，判静默 | 通过 |
| P3-5 图表拷贝前复查 | server.py:109 先 quiet(force=True) 再 glob，改用原子拷贝 | 通过 |
| P3-6 整串比较 | start_all.sh:18-21；autostart.sh.proposed:29 与 `/bin/bash ./supervise.sh` 整串相等 | 通过 |
| P3-7 自测拿不到锁就中止 | test_v2.sh:26-31：后台子 shell 拿到 flock 并写出标记文件之后，才执行 start_all；拿不到或持锁进程已退出，就 FAIL 并 exit 1 | 通过 |
| P3-8 部署输出 | deploy_loop.sh:25 先 rm，:26 在 umask 077 的子 shell 里重新创建 | 通过 |
| P3-9 纵深防御 | server.py:7、export_static.py:5 启动时去掉全部 QL_QUIET_*；gen.py:4-7 在 import pandas 和任何读取之前自查；snapshot.py:169-171、kline.py:37-39 在 __main__ 里自查；loop.sh 改为空壳，exit 1 | 通过，见 N-5 |
| P3-10 错误日志 | export_static.py:21-24：status 或 rc 异常、输出非 JSON 时写 stderr | 通过 |
| P3-11 文档 | 回应文档 :72-80 和新节 §切换步骤 3 都改为 supervise 先停并确认退出，再停 server；步骤 3 扩大为全机 ps；文件数与备份路径已更正 | 通过 |

- **停进程顺序**：WEB_REVIEW_RESPONSE_ZH.md :72-80 和 :174 都是 keepalive → deploy_supervise → deploy_loop → supervise（确认已退出）→ server，只用精确 PID 的 kill，不加 --force、不用 kill -9 或 pkill，每停一个都用 ps -p 确认。脚本层面，supervise.sh 的 trap 本身就是先停 server 再退出。符合裁定。

## 四、新发现（均为 P3，不阻塞安装）

- **N-1｜run/children.json 的临时文件名在同一进程内会撞名**：ql_atomic.py:6 的临时名只带 pid。server 里 gen 线程、bg 线程（snapshot）、HTTP 线程（kline）可能同时调用 ql_child._save_reg（ql_child.py:40-44），写同一个 `children.json.tmp.<pid>`。
  - 后果：登记可能被截断，或丢一次更新（异常已被吞掉）。cleanup_orphans 遇到坏 JSON 时按空处理，结果只是少清理一次孤儿。影响的是兜底机制，研究安全仍靠 Arch 的设锁后核验。
  - 建议：_save_reg 整段加锁；或者 ql_atomic 的临时名改用同目录 mkstemp，或加上线程 id 和随机后缀。
- **N-2｜cleanup_orphans 没有核对当前 pgid**：ql_child.py:60 直接 killpg 登记的 pgid。建议先确认 os.getpgid(pid) 等于登记的 pgid 再发信号；PermissionError 时不要计入 done（:65）。
- **N-3｜窗口时间格式过宽**：date -d 会把纯数字当成钟点，已实测：`date -d 0` 等于今天 00:00，`date -d 1` 等于今天 01:00。end 如果误写成数字，或者 end 不晚于 start，窗口永远不生效，属于 fail-open。
  - 建议：start 和 end 必须匹配带时区偏移的 ISO-8601（例如 `^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:]{8}[+-][0-9]{2}:[0-9]{2}$`），并且 e 必须大于 s，否则判静默。
  - 现有窗口是规范的 ISO 时间，不受影响。
- **N-4｜export/ 里可能残留临时文件**：export_static 被 SIGKILL 时，`*.tmp.*` 会留在 export/。它们不计入指纹，但会被 vercel deploy 整目录上传。内容只是公开产物的片段，影响很小。建议 export_static 开头清掉 export/ 下的 `*.tmp.*`。
- **N-5｜子进程自查退出 3 后不会补跑（可用性问题，不涉及安全）**：锁如果在 ql_child 预检之后、子进程自查之前出现，gen.py 或 snapshot.py 会以 rc=3 退出，而 ql_child 返回的 status 是 ok。
  - 后果：server.py:75-76 不会置 GEN.again；server.py:104-107 会照常走成功分支（广播 snapshot），也不置 pending。锁解除后要等到下一次文件变更才会补跑。
  - 建议：rc 为 3 时按 quiet 处理，置 again 或 pending。
- **N-6｜自启提案文档与脚本不一致（启用前必须改）**：AUTOSTART_PROPOSAL_ZH.md 里嵌的仍是 a97c90fe 的文本，staged 实际是 ccfbcf81。启用自启之前，提案文档要同步更新为 ccfbcf81 的内容和 sha，并以 staged 文件为准。

## 五、放行与安装前提

- **代码**：v2.1（SHA256SUMS db7a6047）PASS，可以安装。
- **安装前提**（全部满足才执行）：
  1. Arch 已宣布研究锁 b5e78069 解除，且 output/loop/RESEARCH_QUIET.lock 不存在。install_v2.sh:14 在静默时也会拒绝安装。
  2. 时间不在 2026-10-19 16:40–18:40 ET。
  3. 安装时 staged_v2 的 SHA256SUMS 仍是 db7a6047，19/19 校验通过；先跑 `install_v2.sh --dry-run` 并通过。
  4. 停进程前全机 `ps -eo pid,ppid,args` 中没有 gen.py、snapshot.py、kline.py、export_static.py，也没有在跑的 vercel 部署。
  5. 停进程顺序：keepalive 2859822 → deploy_supervise 2859819 → deploy_loop 2859825 → supervise 2859816（确认已退出）→ server 2905775。只用精确 PID 的 kill，不加 --force，每停一个都 ps -p 确认，并确认 /tmp/ql_start_all.lock 已释放。
  6. 执行 start_all 应得 rc=0。之后跑 test_v2.sh。回执里给出 run/*.pid、各 PID 的 fd 和 environ 核验（只看变量名）、healthz 输出、test_v2 输出、安装后的文件 sha，报 Arch 并记入 TEAM_STATE。
- **自启**：N-6 改完，并且 v2.1 安装、核验之后，不早于 2026-10-19 18:40 ET 且研究锁不存在时，才可以启用。在那之前，.bashrc 和 .profile 的钩子保持注释。
- N-1 到 N-5 放到下一版（v2.2）处理，处理后提交增量 diff 给 Arch。
