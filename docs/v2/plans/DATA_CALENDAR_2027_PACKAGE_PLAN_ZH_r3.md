# 日历 2027 包 r3（只含对 r2 的增量：Arch 新 P3-a / P3-b）

- 作者：QuantLab Data；生成时间 2026-10-18T11:02:38-04:00（ET，date 生成）。新文件，不改 r2（docs/v2/plans/DATA_CALENDAR_2027_PACKAGE_PLAN_ZH_r2.md，c1b51e13）。
- 依据：Arch 审查 docs/v2/ARCH_DATA_REVISIONS_1040_REVIEW_ZH.md（11cb0690）§1.2。代码文本未落 repo、未运行；不在 10-19 纸面跑完前动；与 SW 包不同 .ok、不同天落地（r2 §6 不变）。
- 另：主 Agent 10-18 指定 Data 负责 Eng 纸面日历（tushare_raw/trade_cal.parquet，tier1_pull.py L85 写死 20261231）延长并入本包：end_date 改参数、写新版文件不原地覆盖、11-30 前交 Arch；切换算纸面变更由主 Agent 报 Leo。该部分 diff 另出新文件，本文不含。

## 1. P3-a：_guard_write 同时比 inode（替换 r2 L74-83）
```python
PROTECTED_PATHS = [ROOT / p for p in ("data/v2/calendar/trade_cal_sse_pit.parquet",
                                      "data/v2/calendar/manifest.json",
                                      "data/v2/tushare_raw/trade_cal.parquet")]
PROTECTED = {p.resolve() for p in PROTECTED_PATHS}

def _protected_inodes():
    out = set()
    for p in PROTECTED_PATHS:
        try:
            s = os.stat(p)
            out.add((s.st_dev, s.st_ino))
        except FileNotFoundError:
            pass
    return out

def _guard_write(path, allowed_roots):
    q = pathlib.Path(path).resolve()
    if q in PROTECTED:
        raise SystemExit(f"REFUSED (trade_cal_pit_v2): 受保护路径 {q}")
    if not any(q.is_relative_to(r.resolve()) for r in allowed_roots):
        raise SystemExit(f"REFUSED (trade_cal_pit_v2): 不在本模式允许的写入目录 {q}")
    if os.path.lexists(q):
        s = os.stat(q)
        if (s.st_dev, s.st_ino) in _protected_inodes():
            raise SystemExit(f"REFUSED (trade_cal_pit_v2): {q} 与受保护文件是同一 inode（硬链接）")
        raise SystemExit(f"REFUSED (trade_cal_pit_v2): 写目标已存在 {q}")
    return q
```
- write 模式本来就用 os.link 且要求目标不存在、pull 目录新建，所以「目标已存在即拒绝」与现有流程一致；inode 比较是额外一层，防止允许目录里出现指向受保护文件的硬链接。
- selftest 新增用例 12：在 /tmp 自测根下建一个受保护文件替身，在允许目录里 os.link 一个硬链接，_guard_write 对该链接路径必须以「同一 inode」拒绝；PROTECTED_PATHS 在 selftest 里指向 /tmp 替身，不碰真实文件。

## 2. P3-b：公告只有日期时的排期（r2 §3 L37、L57 的后果写明）
- 规则不变：公告只有日期 → notice_at 取该日 23:59:59 上海；notice_at > pulled_sh 即拒绝（r2 L57）。
- 后果：公告只有日期时，最早能成功拉取的时间是公告日次日 00:00 上海（= 前一日 11:00 ET，冬令时 ET=UTC−5 时为 11:00 ET）。排期写为：**公告发布后，最早在上海次日拉取**；若公告日已是 12 月中旬，拉取 / Arch 审 / 落地相应顺延，但仍须在 2027-01-04 前（纸面从该日起需要 2027 日历）。
- 返回的上海无时区墙钟（r2 L61）在实施时要对照 fa4260b8 的 available_at 列类型（备份元数据显示为 datetime64[us]，以实测为准），由 Data 在只读探查 .ok 下核 schema，不凭推断。

## 3. 其余
r2 其余内容不变；selftest 用例 1-11 不变，新增用例 12（§1）。code-change .ok 签 r2 全文 + 本文文本。
