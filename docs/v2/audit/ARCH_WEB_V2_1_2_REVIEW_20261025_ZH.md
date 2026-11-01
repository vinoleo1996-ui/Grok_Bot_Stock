# Arch 审阅：QuantLab Web staged_v2_1_2（healthz 入口现刷 quiet()）

- **角色**：QuantLab Arch（执行器）
- **时刻**：2026-10-25T11:57:20-0400（America/New_York）
- **结论**：**PASS_WITH_CONDITIONS**
- **动作本回合**：**不安装** · **不重启** Web · **不签** research `.ok` · 不读真行情大表 · live=false
- **live server.py**：未改动（盘证仍 `bc8dfb54…`）

## 1. 输入 sha256 核对（全长 MATCH）

| 件 | 路径 | 期望（送审） | 盘证 | 结果 |
|---|---|---|---|---|
| unified diff | `/workspace/quantlab-web/staged_v2_1_2.diff` | `15fdc4f6…` | `15fdc4f6b7adcfd1ef2a3cb3cf501653fc6020b70adabcaf6d0088a4139ac134` | **MATCH** |
| staged server | `/workspace/quantlab-web/staged_v2_1_2/server.py` | `4a04f0e2…` | `4a04f0e2e7f5bf728dda284ffa39b29527dcf58cf71ba687797c45eb7ea88d17` | **MATCH** |
| 送审说明 | `/workspace/quantlab-web/WEB_V2_1_2_REVIEW_ZH.md`（与包内同文） | `3d6a0fc3…` | `3d6a0fc373c4a870d85cf3ba04406c8f7586a23c89bc05c6ddb98badc4ad58a6` | **MATCH** |
| SHA256SUMS | `/workspace/quantlab-web/staged_v2_1_2/SHA256SUMS` | （清单自洽） | `a965bbd10d0e5f27a4a69cffc43853061d0c3d4dd97f69ab6554c4cda423b9bb` | **MATCH**（所列 4 件 + `../staged_v2_1_2.diff` 全对） |
| 线上基线 | `/workspace/quantlab-web/server.py` | `bc8dfb54…` | `bc8dfb5496b93ba5dcc89f317feffe5ce62ec2f34cf1cf1df8abbe987341fe27` | **MATCH**；`server.py.pre` **byte-eq** live |

## 2. Diff 范围（要点 1）

| 检查 | 结果 |
|---|---|
| `diff -u live staged` 行数差 | **仅 1 行**（L159 healthz） |
| hunk 数 | **1 hunk** |
| 其它路径/导入/函数体 | **无**改写；`quiet`/`_kids`/kline/snapshot/gen 逻辑字节级同 live |
| 副作用 | 仅在 `/healthz` 入口增加一次 `quiet()`（`force=False`）副作用刷新 `QS`，再读缓存字段回包；**无**写锁、**无**启子进程、**无**改 `live` 标志（仍 `live:False`） |

唯一变更（语义）：

```diff
-        if p=='/healthz': return self.send(200,{'ok':True,...,'quiet':QS['quiet'],...,**_kids()})
+        if p=='/healthz': quiet(); return self.send(200,{'ok':True,...,'quiet':QS['quiet'],...,**_kids()})  # v2.1.2
```

**裁定要点 1：PASS** — 单 hunk、无旁路副作用改写。

## 3. quiet() 失败是否 fail-closed（要点 2）

调用链：`healthz → quiet(force=False) → ql_quiet.status() → bash ql_quiet.sh`。

| 层 | 行为 | 裁定 |
|---|---|---|
| `ql_quiet.py::status` | `try/except`；非 0/1 的 rc → `(True, 'error:…(fail-closed)')`；任意异常同 | **fail-closed（偏静默）** |
| `ql_quiet.sh` | 锁存在→静默；窗口文件缺失/解析失败/start·end 空或不可解析→静默；仅 `QL_QUIET_TEST=1`+`ALLOW_NOWIN` 测试放行 | **fail-closed** |
| `server.quiet()` 本体 | **无**自带 try；依赖下层永不抛 | 可接受：下层已吞异常并返回静默；与既有 scan/kline/freshness 调用点同构 |
| `force=False` 节流 | 最多每 5s 真刷一次；锁刚落地后 healthz 仍可能 **≤5s** 报 `quiet=false` | **COND**（已知、可接受；优于旧版「永不刷」） |

**裁定要点 2：PASS**（附 COND：≤5s 缓存窗仍在；偏静默方向正确）。

## 4. 是否仍可能漏报 kline / export_static / snapshot / gen（要点 3）

本包 **不改** `_kids()`：

```python
def _kids():
    k=ql_child.running()  # 仅 server 进程内 ql_child.LIVE
    return {'gen_running':..., 'snapshot_running':..., 'kline_running':..., 'child_pids':k}
```

| 路径 | healthz 可见性（装本包后） | 说明 |
|---|---|---|
| server 自启 `snapshot` / `gen` / `/api/kline` | 可见（既有） | 登记在 `ql_child.LIVE` |
| **deploy_loop → export_static → kline** | **仍漏报** | 子/孙进程在 deploy 树，不在 server LIVE；属 **v2.1.1**（`deploy_child_*`）范围，本包**不含** |
| freshness 进程内读 parquet | 本包不涉及 | 既有短窗风险，非本包引入 |

对照背景「healthz 曾缓存滞后、漏报 deploy_loop→kline」：

- **缓存滞后（quiet 假阴性）** → 本包 **修**（入口现刷）。
- **deploy_loop→kline 漏报** → 本包 **未修**；须叠装/另审 v2.1.1。

**裁定要点 3：PASS_WITH_CONDITIONS** — 本包目标（quiet 现刷）达成；**不得**宣称 kline/export_static 漏报已解。

## 5. py_compile / 自测声称静态复核（要点 4）

| 检查 | 结果 |
|---|---|
| `python3 -m py_compile staged_v2_1_2/server.py` | **PASS** |
| `ast.parse` | **PASS** |
| `server.py.pre` ≡ live | **PASS**（byte-eq） |
| 送审自测语义（`QL_QUIET_TEST=1` + `/tmp` 临时锁；**不**写 live `RESEARCH_QUIET.lock`） | **PASS** 复现：`OLD_healthz_quiet False` → `NEW_healthz_quiet True`；unlink 后缓存仍 True、`force=True`→False |
| 本回合是否触碰 live 锁 / 重启 Web | **否**（审阅时 live 锁**不存在**；`127.0.0.1:8787/healthz` 当时不可达——仅作环境快照，**不**作为安装判决） |

**裁定要点 4：PASS**。

## 6. 安装时机建议（要点 5）

### 总裁定是否可装

**可以装（带前置）** — 静态包合格；**本回合不装不重启**。装前须全部满足下列前置。

### 安装前置（硬）

1. **无** `RESEARCH_QUIET.lock`；`/healthz`（或等价）报 `quiet=false` 且稳定 ≥15s（Arch pre-.ok 既有口径；本包装后 healthz 现刷，仍建议观察 ≥15s 再动手）。
2. **不在** `quiet_windows.json` 任一窗口内（含 10-19 已前移的 16:25 起点～18:40 ET；及其它已钉窗）。
3. **避开 research 实跑窗**：含叶25 mem_probe / 拟 14:30–16:00 ET X2、叶27 任何未 VOID 的授权窗、以及主排的其它 HI_LIQ/密封实跑；**有实跑或即将签 `.ok` 时禁装**。
4. 装时：**精确 PID** 停 `python3 -X utf8 server.py`（核对 `/proc/<pid>/cmdline`）；**禁** `pkill`/`--force` 扫杀；deploy_loop / supervise / keepalive **不必**因本包重启（仅 server 加载新文件）。
5. 回滚就绪：`staged_v2_1_2/server.py.pre`（≡ live `bc8dfb54…`）可覆盖；或既有 `_recovery` 备份。
6. **正交叠装**：v2.1.1（deploy_child_*）仍暂存未装；本包可先装；**漏报 kline/export_static 须另审另装 v2.1.1**，勿混称一次解决。
7. 装后冒烟（只读）：置临时测试锁**勿**用 live 路径做破坏性测；对 live：锁上后 ≤5s 内 healthz 应 `quiet=true`；无锁时 `quiet=false`；`_kids` 字段形状不变。

### 操作禁区（本回合已遵守）

- 不改 `/workspace/quantlab-web/server.py`
- 不重启 Web / supervise
- 不签 research `.ok`
- 不读真行情大表

## 7. 条款总表

| # | 要点 | 裁定 |
|---|---|---|
| 1 | 仅 1 hunk：healthz→`quiet()`，无副作用改写 | **PASS** |
| 2 | quiet 失败 fail-closed（偏静默） | **PASS**（附 COND：≤5s 节流窗） |
| 3 | 仍否漏报 kline/export_static/snapshot/gen | **PASS_WITH_CONDITIONS**（deploy 链漏报未修） |
| 4 | py_compile / 自测可静态复核 | **PASS** |
| 5 | 安装时机 | **可装·带前置**；本回合不装 |

## 8. 建议下一步

| 角色 | 动作 |
|---|---|
| **主** | 采纳本审后，在**无 QUIET、无 research 实跑窗**的空档排装；优先于/并行于 v2.1.1 由主裁；Arch pre-.ok 的 pgrep 括号逃逸 + QUIET≥15s **仍有效**（本包不替代）。 |
| **Web/Eng** | 等主放行再装；装后只读冒烟；回执披露 pre/post sha（`bc8dfb54`→`4a04f0e2`）。 |
| **Arch** | 本回合只出本稿；装时若被召再核 QUIET/窗/精确 PID；**不**因本包代签 research `.ok`。 |
| **AI** | 叶25 mem_probe / 叶27 下一刀分块装载继续；与 Web 安装互斥排程。 |

## 9. 总裁定

**PASS_WITH_CONDITIONS** — 输入全长 MATCH；单 hunk 现刷 `quiet()`；下层 fail-closed 偏静默；`py_compile` 与 `/tmp` 语义自测复现 PASS。开放项：① 装机须避开 QUIET/quiet_windows/research 实跑窗并以精确 PID 重启；② deploy_loop→export_static→kline 的 healthz 漏报**不在本包**，须 v2.1.1；③ `force=False` 仍允 ≤5s 缓存滞后。

live=false。本回合**未安装、未重启** Web；**未改** live `server.py`。
