# Data 申万一级 PIT 修复方案（sw_l1_pit_v2）——仅方案，待 Arch 审

- 作者：QuantLab Data；起草时间 2026-10-18 06:5x ET
- 状态：**仅方案**。除本文件外，未改任何代码或数据，未运行项目代码。下文 diff 只是文本，**未应用**。
- 定性（主 Agent 裁定）：235 只误删记 **Data P1**；合并没有来源优先级记 **P2**。
- 证据：/tmp/data_ro_audit_20261018/（EVIDENCE b38c5d6c），加上本文 §3 新做的只读核验。

## 0. 硬约束
- 不覆盖、不改动：`data/v2/sw_pit/industry_members_sw_l1_pit.parquet`（0b1d3432…）和 `data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet`（89d4afa3…，叶23、叶24 钉住）。
- 新输出：`data/v2/sw_pit/sw_l1_pit_v2.parquet` 和 `data/v2/sw_pit/sw_l1_pit_v2.manifest.json`（新版本文件）。
- promotion_approved=false；不碰 94322、8787、moneyflow、data/v2/events。
- 资源：单进程 RSS ≤ 1.5GB（预期 <300MB）；MemAvailable 低于 2GB 就暂停；同时只跑一个重任务；nice -n 10，PYTHONDONTWRITEBYTECODE=1，/usr/bin/python3。

## 1. 排期（按 Arch/主 Agent 06:48 的更新，取代原来的“叶步骤空档跑”）
1. **实施推迟**到以下三项全部结束之后：叶23 r2.11、叶24、10-19 纸面跟踪（paper tracks）。
2. 和“交易日历 2027 延长包”**同批交付**（包内含 20130424 的 pretrade_date：由本地 is_open 推导，值为 20130423）。
3. 叶23、叶24 和 Strategy 的 .ok 钉了这些文件的 sha，所以交付后**所有受影响的 .ok 都要由 Arch 重签**；下游等 Arch 审完回执再切换。
4. 避开 10-19 16:40–18:40 ET（以及 17:40 前后一小时）；每次运行前通知主 Agent 和 Arch（开始时间、预计时长）。
5. 通知 Strategy/Intel 消费方由主 Agent 负责，不属于 Data 的职责。

## 2. 问题复述（只读审计结论）
- 坏表 0b1d3432：7573 行 / 5600 个代码，由 `scripts/acquire/sw_pit_refresh.py`（sha a18684fe…）生成。流程是：全量 Y/N 分页 + 按 L1×Y/N 分拉 → concat → 只去掉完全相同的行 → groupby(instrument_id, l1_code, out_date 为空记为 2099)。没有来源优先级，同一成分的 open 和 closed 版本两条都留下。
- 12 只双开（P2）：002420 002481 002597 003030 300699 300741 300777 300858 300972 603020 605077 688002（完整代码见 A_12codes_open_records.csv）。分拉数据里每只只有 1 条 open，另一条是 closed；多出来的 open 来自全量分页返回的陈旧或矛盾版本。
- 349 只在市股票在 2026-09-24..10-16 的每个交易日（11 天，3839 个 code-day）都没有 open 的 L1：
  - 235 只：10-14 04:00 那次“修复”误删（P1）；
  - 68 只：全量分页截断后没补（分拉里有）；
  - 46 只：原判“源缺（只有已结束的历史）”。**§3.2 的复核推翻了这个判断：89d4afa3 里这 46 只全部有 open 行**，应改判为我方合并问题。
- 文档 ALPHA_DATA_D5D6_FIX_ZH.md 写的是 7735 行并带 is_primary 列，和实际文件（7573 行、没有 is_primary）不符，回执里一并更正。

## 3. bak_pre_fix 核验（主 Agent 要求，只读）
命令（2026-10-18 06:5x ET；pgrep 确认没有 leaf 进程；只用 pyarrow 读 ts_code、instrument_id、out_date 列，不 import 项目代码；峰值 maxrss 169MB）：
`sha256sum …；stat -c "%n | birth %w | mod %y" …；nice -n 10 /usr/bin/python3 -c "<pyarrow 读列 + 集合比较>"`

| 项 | 结果 |
|---|---|
| bak sha | 597340148480675b09a0560ae7ce23917edf5f35c40e51c25c64f3b701f72c9c ✔ |
| 当前表 sha | 0b1d3432e30f7cdd907df393299cd2f552e1121899239985a00113c4dfcd89f6 ✔ |
| 89d4afa3 sha | 89d4afa337435a2302b5c13fd4cf049b71eda2f20e1d9094f15d62cdb587f66c ✔ |
| bak 行数 / 代码数 | **7743 / 5759** ✔ |
| 当前表 行数 / 代码数 | 7573 / 5600 |
| 代码集：bak 有、当前表没有 | **254**（和“10-14 修复删了 254 只”一致）✔ |
| 代码集：当前表有、bak 没有 | **95**（修复时还新增了 95 只，审计原文没提，回执里要说明来源） |
| 235 只误删代码是否都在 bak 里 | 235/235 ✔；235 只都在被删的 254 只里 ✔；被删但不在 235 里的 19 只是已退市或未上市等，不属于在市口径 |

### 3.1 时间戳
- bak：birth 和 mod 都是 2026-10-18 01:13:14.40 ET；当前表：birth 和 mod 都是 01:13:13.24 ET。
- 两个文件都是 10-18 01:13 工作区整体恢复时重写出来的新 inode（落在 RECOVERY_MANIFEST 记录的 01:13:24–01:14:51 区间附近；logs/nightly/20261014_* 也都是 01:13:3x）。**原始 mtime 已经丢了，没法用文件时间直接证明 bak 早于 10-14 04:00。**
- 不过内容证据足够：bak 比当前表多出的代码正好是修复删除的 254 只，而且包含全部 235 只误删代码，据此判定 bak 就是误删之前的版本。建议 Arch 接受用内容证据代替时间证据。

### 3.2 三类代码在 89d4afa3 里的情况（按 instrument_id 口径）
- 235 只全部有 open 行；68 只全部有 open 行；**46 只也全部有 open 行**。
- 结论：按“分拉（89d4afa3 血统）为主”的规则重建后，预计 09-24..10-16 每天缺成分的数量为 **0**；`quality_status=source_gap` 预计 0 只。这条规则仍保留，只给分拉里没有 open 行的在市代码打标。

## 4. 七条规则（Arch 已原则同意）
1. **分拉优先**：主来源是 tushare_raw/index_member_all 下按 L1×Y/N 拉取的 62 个文件（89d4afa3 血统）。
2. **全量只补缺**：全量 Y/N 分页只用来补分拉里完全没有的代码（标 source_rank=2）。
3. **open/closed 冲突**：同一 (code, l1, in_date) 或同一 code 有矛盾时，分拉里是 closed 的就以 closed 为准；全量里的陈旧 open 行丢弃，并记到 conflicts 明细。
4. **断言**：每个代码最多 1 条 open 行；违反就不落盘，非零退出。
5. **不编造**：在市但分拉里没有 open 行的代码写 quality_status=source_gap（不加 open 行，不补行业）。
6. **新版本输出**：只写 sw_l1_pit_v2.parquet 和 manifest，不覆盖 0b1d3432、89d4afa3。
7. **交易日历**：20130424 的 pretrade_date 由本地 is_open 推导（20130423），随 2027 包交付（不在本 diff 里）。

## 5. 和 FALSE_DONE 补数队列合并
- output/relay_outage_backfill_queue.json 里 `nightly_step|sw|20261014/15/16` 三项都是 pending（failed_source=relay，retry_cmd 为 nightly_update.py --steps sw）。
- 申万成分是整表重拉，和日期无关。方案：**这次 v2 重建离线使用 10-18 01:08 已经落地的 62 个分拉 raw 文件，不需要 relay**；这批 raw 反映的是 10-14..10-16 之后的状态（in_date/out_date 截至 10-18）。
- 回执完成、Arch 审过之后，把这三项 sw 标为 done，reason=`superseded_by sw_l1_pit_v2 (<sha>)`；按队列规则先归档到 _recovery/data/ 再改。**不再单独跑 nightly 的 sw 步骤**，保证 SW 只改一次。
- 如果 Arch 要求实施当天拉新的 raw：需要 relay 可用；relay 不通就回落到 01:08 那批 raw，并在 manifest 写明 raw_asof。用 relay 拉新时只写到新目录 tushare_raw/index_member_all_<date>/，不覆盖现有 62 个文件（它们是 89d4afa3 的血统证据）。
- index_classify（L1 名单）10-14 失败过（SSLEOF/504）；离线方案改读已落地的 sw2021_classify_l1.parquet，不依赖 relay。

## 6. 代码 DIFF（文本，未应用）
做法：新建离线构建脚本 `scripts/acquire/sw_l1_pit_v2_build.py`；`sw_pit_refresh.py` 只加两处：分拉结果落盘，以及不再写旧的 L1 PIT 表（以后拉取不会再生成双开表）。编辑前把两个脚本的旧版本归档到 `_recovery/data/sw_l1_pit_v2_pre_<date>/`。

```diff
--- /dev/null
+++ b/scripts/acquire/sw_l1_pit_v2_build.py
@@ -0,0 +1,75 @@
+# SW2021 L1 PIT v2 离线重建: 分拉(index_member_all 按 L1xY/N)为主, 全量只补缺. 不联网, 不覆盖 0b1d3432 / 89d4afa3.
+import sys, json, hashlib, argparse, pathlib, pandas as pd
+ROOT=pathlib.Path("/workspace/QuantLab")
+RAW=ROOT/"data/v2/tushare_raw/index_member_all"
+FULL=ROOT/"data/v2/sw_pit/sw2021_members_l1l2l3_raw.parquet"
+REF=ROOT/"data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet"   # 89d4afa3, 只读对账
+OUT=ROOT/"data/v2/sw_pit/sw_l1_pit_v2.parquet"
+PROTECT={"0b1d3432e30f7cdd907df393299cd2f552e1121899239985a00113c4dfcd89f6",
+         "89d4afa337435a2302b5c13fd4cf049b71eda2f20e1d9094f15d62cdb587f66c"}
+def sha(p): return hashlib.sha256(open(p,"rb").read()).hexdigest()
+def to_iid(ts): a,b=ts.split("."); return b.lower()+"."+a
+def load_perl1(raw_dir):                     # 规则1
+    fs=sorted(raw_dir.glob("801*.SI_[YN].parquet")); assert len(fs)==62, len(fs)
+    parts=[]
+    for f in fs:
+        l1,isn=f.stem.split("_"); d=pd.read_parquet(f); d=d[d.l1_code==l1]; d["is_new"]=isn; d["src_file"]=f.name; parts.append(d)
+    m=pd.concat(parts,ignore_index=True).drop_duplicates(subset=["ts_code","l1_code","in_date","out_date","is_new"])
+    m["source_rank"]=1; return m
+def fill_from_full(perl1, full):            # 规则2
+    miss=set(full.ts_code)-set(perl1.ts_code)
+    add=full[full.ts_code.isin(miss)].copy(); add["source_rank"]=2; add["src_file"]="full_paged"
+    return pd.concat([perl1,add],ignore_index=True), sorted(miss)
+def resolve_open_closed(m):                  # 规则3
+    m=m.copy(); m["in_date"]=pd.to_datetime(m.in_date); m["out_date"]=pd.to_datetime(m.out_date,errors="coerce")
+    key=["ts_code","l1_code","in_date"]
+    closed=m[m.out_date.notna()].set_index(key).index
+    stale=(m.out_date.isna() & m.set_index(key).index.isin(closed)).values
+    conflicts=m[stale]; m=m[~stale]
+    # 同 code 多条 open: 保留 source_rank 最小、in_date 最新的一条, 其余记入 conflicts
+    o=m[m.out_date.isna()].sort_values(["ts_code","source_rank","in_date"],ascending=[True,True,False])
+    dup=o[o.duplicated("ts_code",keep="first")]
+    return m.drop(dup.index), pd.concat([conflicts,dup])
+def assert_one_open(m):                      # 规则4
+    n=m[m.out_date.isna()].groupby("ts_code").size(); bad=n[n>1]
+    assert bad.empty, f"open>1: {bad.index.tolist()[:20]}"
+def flag_source_gap(m, listed_codes):        # 规则5, 不编造
+    has_open=set(m[m.out_date.isna()].ts_code); gap=sorted(set(listed_codes)-has_open)
+    m["quality_status"]="ok"; m.loc[m.ts_code.isin(gap),"quality_status"]="source_gap"; return m, gap
+def normdiff_vs_ref(m, ref):                 # 对账 89d4afa3
+    a=m[m.out_date.isna()].assign(iid=lambda d:d.ts_code.map(to_iid))[["iid","l1_code"]]
+    b=ref[ref.out_date.isna()][["instrument_id","sw_code"]].rename(columns={"instrument_id":"iid","sw_code":"l1_code"})
+    j=a.merge(b,on="iid",how="outer",suffixes=("_v2","_ref"),indicator=True)
+    return j[(j._merge!="both")|(j.l1_code_v2!=j.l1_code_ref)]
+def main():
+    ap=argparse.ArgumentParser(); ap.add_argument("--execute",action="store_true"); ap.add_argument("--out_dir",default="/tmp/sw_l1_pit_v2_dryrun")
+    a=ap.parse_args()
+    m=load_perl1(RAW); m,filled=fill_from_full(m, pd.read_parquet(FULL)); m,conf=resolve_open_closed(m); assert_one_open(m)
+    listed=load_listed_universe()            # stock_basic L + stock_delisted_v2 9d757b96, 与审计同口径
+    m,gap=flag_source_gap(m,listed)
+    m["instrument_id"]=m.ts_code.map(to_iid); m["available_at"]=m.in_date+pd.Timedelta(hours=18)
+    m["source"]="tushare.index_member_all(SW2021) perL1>full"; m["promotion_approved"]=False; m["revision"]="v2"
+    nd=normdiff_vs_ref(m, pd.read_parquet(REF))
+    od=OUT.parent if a.execute else pathlib.Path(a.out_dir); od.mkdir(parents=True,exist_ok=True)
+    write_reports(od, m, conf, filled, gap, nd, listed)   # 每日缺成分 09-24..10-16 前后对比, 12 只处理
+    if not a.execute: print("DRY-RUN only, no repo write"); return
+    assert nd.empty or approved_normdiff(nd), "normdiff 非空且未获 Arch 认可"
+    assert not OUT.exists(), "v2 已存在, 不覆盖"
+    m.to_parquet(OUT,index=False); s=sha(OUT); assert s not in PROTECT
+    write_manifest(OUT, s, m, gap, conf, raw_files_sha(RAW))
+if __name__=="__main__": main()
```

```diff
--- a/scripts/acquire/sw_pit_refresh.py
+++ b/scripts/acquire/sw_pit_refresh.py
@@ -26,9 +26,12 @@
 # 再按 L1 × Y/N 分拉补齐 (全量分页在 relay 端存在截断), 合并去重
+RAWD=ROOT/"data/v2/tushare_raw"/("index_member_all_"+pd.Timestamp.now().strftime("%Y%m%d")); RAWD.mkdir(parents=True,exist_ok=True)
 for c in cls.index_code:
     for isn in "YN":
         try:
             df=call("index_member_all",l1_code=c,is_new=isn); df["is_new"]=isn; parts.append(df[df.l1_code==c])
+            df[df.l1_code==c].to_parquet(RAWD/f"{c}_{isn}.parquet",index=False)   # 分拉落盘到新目录, 供 v2 离线重建
         except Exception as e: print("l1 fail",c,isn,e,flush=True)
         time.sleep(0.3)
@@ -43,6 +46,8 @@
 for lv in ["l1","l2"]:
+    if lv=="l1":
+        print("l1 PIT 改由 sw_l1_pit_v2_build.py 生成, 此处不再写 industry_members_sw_l1_pit.parquet"); continue
     t=m[["instrument_id","ts_code","name",f"{lv}_code",f"{lv}_name","in_date","out_date","is_new","available_at","source","promotion_approved"]].copy()
```
注：`load_listed_universe / write_reports / write_manifest / approved_normdiff / raw_files_sha` 是同一文件里的小函数，dry-run 之前连同全文一起给 Arch 看。manifest 里 l1 段的写法要相应调整（l1 不再由这个脚本产出）。selftest 文件为 `tests/test_sw_l1_pit_v2_build.py`：开头先调用 `enforce(modes=["selftest"])` 再 import 被测模块，用合成的小数据覆盖规则 2–5，out_dir 放在 /tmp，需要 selftest .ok。

## 7. 执行步骤（全部在 §1 的排期窗口内）
1. Arch 签：code-change .ok（覆盖上面两个脚本和测试）、selftest .ok、run .ok（dry-run 和 execute 分开签，或者在同一个 .ok 里分别写明）；我自己核对 expires_et，并确认 signed_et 不在未来。
2. 把旧脚本归档到 _recovery/data/sw_l1_pit_v2_pre_<date>/，然后再改代码。
3. 跑 selftest（PYTHONDONTWRITEBYTECODE=1 nice -n 10）。
4. **dry-run**：输出到 /tmp/sw_l1_pit_v2_dryrun/，包括 normdiff_vs_89d4afa3.csv、conflicts.csv、daily_missing_before_after.csv、twelve_codes_resolution.csv、source_gap.csv、filled_from_full.csv，交 Arch 审。
5. Arch 认可后再 **execute**，只写 v2 文件和 manifest；运行前检查 pgrep 和 MemAvailable，运行中通过 /proc 监控 RSS。
6. 交回执；Arch 审过后，再处理队列里的 3 项 sw、下游切换和 .ok 重签。

## 8. 修前修后对比（预期值，执行后换成实测）
| 交易日 | 修前缺 open L1（0b1d3432） | 修后预期（v2） |
|---|---|---|
| 2026-09-24 | 349 | 0 |
| 2026-09-28 | 349 | 0 |
| 2026-09-29 | 349 | 0 |
| 2026-09-30 | 349 | 0 |
| 2026-10-08 | 349 | 0 |
| 2026-10-09 | 349 | 0 |
| 2026-10-12 | 349 | 0 |
| 2026-10-13 | 349 | 0 |
| 2026-10-14 | 349 | 0 |
| 2026-10-15 | 349 | 0 |
| 2026-10-16 | 349 | 0 |
- 依据：235、68、46 三类代码在 89d4afa3 里都有 open 行（§3.2）。
- 12 只双开：修后每只只有 1 条 open，和分拉一致。例如 002420 → 801230 综合（自 2026-07-01）；002481 → 801010 农林牧渔（自 2021-07-30）。另一条按分拉改为 closed，或丢弃并记入 conflicts.csv。
- 行数 / 代码数：修前 7573 / 5600；修后预期约 7920 / 5914（和 89d4afa3 同一量级），再加上全量补缺的代码（预计 0 或极少）。在市代码的 open 行应和 89d4afa3 对应的 open 行一致（normdiff 预期为空）。
- source_gap 预期 0 只；如果不是 0，逐只列出。

## 9. 回执内容（docs/v2/audit/sw_l1_pit_v2/receipt_<date>.md）
- 修前修后每天缺成分的数量（09-24..10-16）；
- 七条规则原文；
- 新文件的 sha、行数、代码数、open 行数；
- 12 只双开的处理明细；
- source_gap 列表，以及原 46 只的改判说明；
- 和 89d4afa3 的 normdiff（共有代码的 open 成分应完全一致）；
- 全量补缺明细；
- 62 个 raw 文件的 sha 列表；
- 修复时新增的 95 只代码的来源说明；
- ALPHA_DATA_D5D6_FIX_ZH.md 中行数和 is_primary 的更正；
- 用到的命令、时间（ET）、峰值 RSS。

## 10. 回滚
- 新文件是独立的，旧文件 0b1d3432、89d4afa3 都不动。回滚就是让下游 .ok 继续钉旧 sha，并把 v2 文件归档到 _recovery/data/（删除需另行授权）。
- 代码回滚：从 _recovery/data/sw_l1_pit_v2_pre_<date>/ 恢复两个脚本。
- 队列：3 项 sw 只在 Arch 审过回执后才改为 done；回滚时按归档恢复。

## 11. 待 Arch 决定
1. 46 只原判“源缺”已被推翻（89d4afa3 里都有 open 行）。是否同意改判为我方合并问题？计入 P1 还是 P2？
2. 修复时新增的 95 只代码（当前表有、bak 没有）：回执里是否要逐只追溯？
3. 用 10-18 01:08 的 62 个 raw 离线重建（不需要 relay），还是实施当天要求用 relay 拉新（写新目录，不覆盖）？
4. 89d4afa3 的写入者不明：是否允许把它的 62 个 raw 当作 v2 主来源的血统？还是要先查清写入者？
5. bak 的时间戳因 01:13 的恢复已经丢失，是否接受用内容证据代替？
6. 队列里 3 项 sw 以 superseded_by v2 关闭，是否可行？
