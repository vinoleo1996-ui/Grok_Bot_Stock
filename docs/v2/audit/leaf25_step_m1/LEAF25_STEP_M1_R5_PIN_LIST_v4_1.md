# 叶25 步骤 −1 R5 签发钉单 v4.1（供 Arch 签 ARCH_RUN_AUTH_LEAF25_TTM_RECON_STEP_M1_R5_v2.ok）

> 相对 v4（8a3ddeee）：仅 .cmd 改钉 R5c_v2（`--arch-ok` → `…_R5_v2.ok`）；R5c（a6c36ad1）作废于本签发链。写于 `date` 2026-10-25T00:23:01-04:00。

- 编写：AI，2026-10-25T00:21:40-04:00（取自 `date`；本机显示 2026-10-25 00:21:40 EDT）。v4 因 **10-18 19:00 窗 / ARCH_RUN_AUTH_LEAF25_TTM_RECON_STEP_M1_R5.ok 已过期且永不可再用** 而重钉；代码与输入 sha 未变，**不 bump 脚本**（仍用 _r5；.cmd 用 R5c_v2）。v3.1（0d8be7f8）保留作 prior。依据：主 Agent 2026-10-25 00:18 ET 加急（巡检 0016）。
- 本文只做静态整理：读脚本/.cmd/文档文本，对文件算 sha256（逐字节哈希，不解析）、取 mtime 与大小。没有打开 parquet、没有读 schema 或页脚元数据、没有运行任何脚本、没有提交。live=false，promotion=false。

## 〇、过期窗声明（硬）
- 旧 .ok 路径 `output/ai_factory/ARCH_RUN_AUTH_LEAF25_TTM_RECON_STEP_M1_R5.ok` 与建议窗 **2026-10-18 19:00–19:45 ET 已过期**；该 .ok **不得再消费、不得复用、不得改 expires 复活**。
- 必须签发 **新路径**：`output/ai_factory/ARCH_RUN_AUTH_LEAF25_TTM_RECON_STEP_M1_R5_v2.ok`，带新窗口与新 expires_et。
- 无新 Arch .ok **禁止开跑**（主 Agent 硬裁）。live=false。

## 一、钉住的代码与文档（全长 sha256）
| 项 | 路径 | sha256 |
|---|---|---|
| 预注册 r5 | docs/v2/AI_LEAF25_ACCRUALS_PREREG_DRAFT_r5.md | 81123646382f7bb188a135e0d9142372b373c079e289d47066f5587a1fde40e1 |
| 脚本 _r5（未 bump） | research/leaf25_ttm_recon_step_m1_r5.py | f43b901671728204437279da1f49c7729ec11f11d8070e73434b5d6288953d68 |
| .cmd R5c_v2 | docs/v2/audit/leaf25_step_m1/LEAF25_STEP_M1_R5c_v2.cmd | 11873aaa24bcf97135f374667d7cb57213a3355fd635145944e9cfd26a9c044b |
| ~~.cmd R5c~~（签发链作废：`--arch-ok` 仍指旧 `_R5.ok`） | docs/v2/audit/leaf25_step_m1/LEAF25_STEP_M1_R5c.cmd | a6c36ad1a4d1e8aeab3ed72c1f8cf4976e713b52df050e423de3dbe5dc9a5c0b |
| ~~.cmd R5b~~（作废） | docs/v2/audit/leaf25_step_m1/LEAF25_STEP_M1_R5b.cmd | 8d0d35d93da729021a1e96f27f49b496ac48e6f2c279f8fc7a4c1fb49dbdb2a6 |
| 内存估计 R5 | docs/v2/audit/leaf25_step_m1/LEAF25_STEP_M1_R5_MEM_ESTIMATE.md | c2fef26b1911b061b6c61137737cc5c52ebb6233e98d7566239de06525822e24 |
| Arch 差异复核 R5 | docs/v2/ARCH_AI_LEAF25_STEP_M1_R5_DIFF_REVIEW_ZH.md | 9fb4fccbcdf44cd1e4b4bbd0bb37211d5c06215b2e87e000ec7ebdf5cf7ebebd |
| 包装器 v4 | docs/v2/audit/cmc_v1_1_leaf24/cmc_wrapper_v4_6174eacb.sh | 6174eacb4ff2d0905634477430b96bf155d3606794cd66f23a5a38a4f85e4169 |
| prior 钉单 v3.1 | docs/v2/audit/leaf25_step_m1/LEAF25_STEP_M1_R5_PIN_LIST_v3_1.md | 0d8be7f8bc5ff5fd0395413cf61d110e73c0a7f93402229a7ce1593ad9d3151a |

- assert=leaf25_ttm_recon_step_m1_r5；tag=leaf25_step_m1_r5
- **ok_path（新）**=output/ai_factory/ARCH_RUN_AUTH_LEAF25_TTM_RECON_STEP_M1_R5_v2.ok
- R5c_v2 相对 R5c **只改** `--arch-ok` → `output/ai_factory/ARCH_RUN_AUTH_LEAF25_TTM_RECON_STEP_M1_R5_v2.ok`（diff：DIFF_cmd_R5c_to_R5c_v2.diff）。R5c（a6c36ad1）在本签发链作废。开跑命令以 .ok 钉的 cmd_path/cmd_sha256 为准。
- 解释器 /workspace/qlvenv/bin/python；env PYTHONDONTWRITEBYTECODE=1；--meta <out_dir>/run_meta.json；out_dir/log_dir 在 output/ai_factory/_leaf25_ttm_recon/ 下，签发时写成字面值。
- 其余键按 Arch 9fb4fccb 第七节（column_whitelist、allow_*、guard_pid 现改为 **94322 已退出** 的 Data ps 证据键、c4_limit_kb=1331200、stopkb=1484800、rss_limit_kb=1536000、expected_peak_kb=650000、expected_rc=0、single_use、run_serial 等）。
- **脚本 bump 判定**：四个 INPUTS 现盘 sha 与 prior pin（bc0f4c3d / 71d5c3d3 / 9ca05496 / fa4260b8）**逐字相同** → **不需要** `_r6` / R6c。

## 二、四个输入文件（2026-10-25 00:20 ET 重哈希；路径同 _r5 INPUTS）
快照位置：当前盘上的 v2 目录本身。sha256 是逐字节哈希（sha256sum），不解析文件；mtime、大小取自 stat。

| 键 | 路径 | sha256 | mtime（ET） | 大小（字节） | vs prior pin |
|---|---|---|---|---|---|
| input_income_sha256 | data/v2/financials_pit/financials_pit_tushare.parquet | bc0f4c3d3cd70a11d17f44496861e21268806509656247400c64be2d3ae7fab3 | 2026-10-18 01:09:47 | 47342959 | **未变** |
| input_cashflow_sha256 | data/v2/financials_pit/cashflow_pit_tushare.parquet | 71d5c3d39fbf2de05064ce7f21334e15c9b1d977c64494ffe699f7eeb0b95d79 | 2026-10-18 01:12:34 | 5098386 | **未变** |
| input_balance_sha256 | data/v2/financials_pit/balancesheet_pit_tushare.parquet | 9ca054962e850cad7305262e978758c9e9f36613c4cca025efdd99276de8dbb5 | 2026-10-18 01:06:48 | 130444287 | **未变** |
| input_calendar_sha256 | data/v2/calendar/trade_cal_sse_pit.parquet | fa4260b808755b9a1c91e3ade210edec84bbdb91e0dfff4c6a955c4d35fd8a41 | 2026-10-18 01:13:35 | 77822 | **未变** |

- 四个 sha 与 _r5 INPUTS 现钉值逐字相同，脚本不需换文件名。脚本启动时会再全长比对，不符即 exit 3。
- **已知缺口（披露，同 v3.1）**：10-14→10-16 补跑未做（方案 R 作废）；步骤 −1 只做 3 只股票 TTM 手算对账，不依赖最新几天。若开跑前输入 sha 再变，须另出 `_r6` + R6c + 新钉单（本 v4.1 不作）。

## 三、第二前置：Strategy sw_pit r3e（交叉引用）
- commit da9fde6a0037da6e2d10f09f65b14f4f0997f952（**仅作交叉引用，钉住以文件 sha 为准**）。
- 自测 2026-10-18 12:55 ET，85 passed / 0 failed（回执 docs/v2/audit/strategy_r3e/SELFTEST_R3E_RECEIPT_20261018.md，sha256 ec10c0569813b16c2d9a7fb6317856afb8a182cfd00a371e5558e5691037ce91）。
- 七文件现盘 sha（与 COMMIT_R3E_RECEIPT post 一致）：
  1. research/sw_members_asof.py — dec73305f8cd49d2c4ad695f72158e10bceb20de83fa19b2a1580be08579a9a7
  2. research/tests_sw_pit/test_sw_members_asof.py — e80f98ed778dbb82d096716fc87c76306fe14d887c177015e623e534514794cc
  3. docs/v2/STRATEGY_SW_PIT_ASOF_FIX_PREREG_ZH.md — 587ff9cff1597d8ec4558d5eacbe52be1e808eacb2fa8ad687b5f3065f0b717d
  4. research/strategy_hiliq_capadv_b4_x2.py — 7b8235dc75a8003993e155fe28924882e1d112117a2a8542c26e292db66b60a1
  5. research/strategy_fulla_b4_x2.py — fa2e4629eea11e81ab9928ef071759e813f50fd0aae162f79f68e44df1b5bf1b
  6. research/sw_pit_freshness.py — 5191997e3a63be758c538c463464038694615f44f195e3f8e74427a9674db43f
  7. research/tests_sw_pit/test_sw_pit_freshness.py — cee59fc5b99210f51b78ddde61e9ae5da16ab44bb47da1a1deb5fefb5380fe0e
- 说明：步骤 −1 脚本本身不读申万表、不调用 sw_members_asof；此前置是为叶25 冻结链。冻结卡点仍在：预注册 r6 等 sw_members_asof 钉 sha；叶21 是否同族待主 Agent 裁。

## 四、本次运行的一行预注册
- 期望：rc=0；--out 下恰好 3 个输出文件（raw_rows.csv、ttm_script.csv、run_meta.json）；run_meta.rule_exercised 三例（i、ii、iii）全部为 true。任一不符即停、报，不重跑。注：run_meta 的 n_candidates.ii 是 jj 筛选前的代码数，不扣除因 avail_E 被跳过的同生效日候选；n_annual_q1_same_day_all_codes 为自然日口径，只作披露。

## 五、开跑前与运行中清单（所有时刻取自 `date`）
1. **94322 已退出**：Data 提供 ps 证据（签发前一次、启动前一次）。现态参考：主 Agent/Data 2026-10-25 00:15–00:16 ET 记 94322 exited（回执 8eeb0866）；开跑前须再核。
2. 静默门禁顺序：① 设 `output/loop/RESEARCH_QUIET.lock`；② 轮询 localhost:8795/healthz 至 quiet=true（最多 90 秒，超时则停、报，不开跑）；③ 再等 15 秒；④ 再取一次 healthz，确认所有 `*_running` 为 false 且 `child_pids={}`。四步各留 date 时刻与 healthz 原文。
3. 开跑前手工执行 `pgrep -af '[k]line.py|[e]xport_static.py|[s]napshot.py|[g]en.py'`（方括号写法避免匹配 pgrep 自身），结果须为空；若不空，等待其自然结束，**绝不 kill**。
4. **MemAvailable≥2.5GiB**，留 `/proc/meminfo` 证据。本钉单撰写时（2026-10-25T00:21:40-04:00）MemAvailable≈11427720 kB（≈10.9 GiB）；开跑前再取一次。
5. 运行期间每 30 秒只读采样：同一条 pgrep -af、ps 快照、包装器进程组 RSS（VmRSS/VmHWM，只读 /proc），带 date 写入回执；不发信号。
6. 单进程、单次、不重试；任何异常停下报 Arch。
7. **rc=124**（R5c_v2 内层 timeout 900 秒到时）一律判失败，**不重跑**；产物按 rc≠0 由包装器移入 `_void`，停下报 Arch。
8. 退出码 0 不等于成功：逐个核对三份输出、triggers、每例 rule_exercised、report_type 计数；rc≠0 到 `output/ai_factory/_void/` 取件。.ok 用后由 Arch 归档（AI 不归档，写「待 Arch 归档」）。

## 六、提议的新运行窗（America/New_York；须 Data 确认 + Arch 签发）
**禁止/避让（据 TEAM_STATE / 巡检 0016 / Arch 00:15）：**
- **旧窗永禁**：任何声称消费旧 `…_R5.ok` 或 10-18 19:00 窗的动作。
- **纸面日终 catch-up**：Eng 纸面仅到 20261014，catch-up 预案在排队；一旦 Eng/主 Agent 排定具体纸面窗，叶25 **不得重叠**。历史硬禁形态（日更恢复后仍适用）：**04:25 ET 起至当日纸面各轨跑完**，尤其 **16:40–18:40 ET**。
- **Data 流式合并落地**：Data 流式 v1.1（4a46df7f）写完交 Arch；落地跑一旦排期，叶25 **不得重叠**（RSS/IO 冲突）。Arch 00:15：「除 BACKUP_PIN 外今晚不签运行类 .ok」→ **2026-10-25 今晚（至约 05:25 BACKUP 窗末）不期望拿到叶25 .ok**。
- Intel 30m 刷新可被 RESEARCH_QUIET.lock 挡住；开跑仍走完整静默门禁。

**候选槽（≥45 min；偏好今晚/明天、尽早且落在禁止区之前）：**

| 优先级 | 建议窗（ET） | Arch 建议签 .ok 时刻 | 备注 |
|---|---|---|---|
| A（首选） | **2026-10-25 10:00–10:45** | ≈09:45 | 早盘静默后；避开 04:25 形态与 16:40–18:40；须 Arch 愿意签运行类 .ok 且 Data 确认无流式落地 |
| B | **2026-10-25 14:00–14:45** | ≈13:45 | 午后；仍早于典型纸面窗 |
| C | **2026-10-25 19:00–19:45** | ≈18:50 | 经典晚间空档（同旧计划形态）；须确认当日无纸面 catch-up / 无流式落地 |
| D（后备） | **2026-10-26 10:00–10:45** | ≈09:45 | 若 10-25 纸面/流式抢窗则顺延 |

- `.ok` 的 `expires_et` 须 **早于** 所选窗结束后的下一个禁止起点（例如选 A/B/C 时，若当日纸面 catch-up 排在 16:40，则 expires 须 < 该禁止起点；选 A 建议 expires ≤ 2026-10-25T11:00:00-04:00）。
- 最终窗以 **Arch 签发 + Data 书面确认** 为准；本表仅提案。

## 七、R5b 作废 / R5c 选定（不变，摘自 v3）
- R5b 外层 timeout 作废（C5 `*python*research/*` 自触 + setsid 收不到 TERM）。
- R5c：timeout 900 在包装器 `--` 之后；rc=124=失败不重跑。
- cmd_path=/workspace/QuantLab/docs/v2/audit/leaf25_step_m1/LEAF25_STEP_M1_R5c_v2.cmd，cmd_sha256=11873aaa24bcf97135f374667d7cb57213a3355fd635145944e9cfd26a9c044b（若 Arch 要求 `--arch-ok` 字面改指 `_R5_v2.ok`，则另出新文件名 `.cmd`，本 v4 不改 R5c）。

## 八、本轮动作边界
- 未派新叶；未跑 leaf25；未读真实数据内容；未提交；live=false。
