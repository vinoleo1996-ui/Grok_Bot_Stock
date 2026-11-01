# Data 申万一级 PIT 修复方案（sw_l1_pit_v2）——仅方案，待 Arch 审

- 作者：QuantLab Data；起草时间 2026-10-18 06:5x ET
- 状态：**仅方案**。除本文件外，未改任何代码或数据，未运行项目代码。下文 diff 只是文本，**未应用**。
- 定性：主 Agent 原裁定 235 只误删记 Data P1、无来源优先级记 P2；**Arch 2026-10-18 06:51 ET 改判：235 / 68 / 46 三类都是我方合并丢失，整个问题记 sw_pit 路径 P1**；对叶23/24 的影响等 Arch 的 inventory（SW_IMPACT_INVENTORY_ZH.md, sha 415f0783）定。
- 版本：本版取代 c692f819（旧版用 cp -p 存为 DATA_SW_L1_PIT_V2_FIX_PLAN_ZH.c692f819.md）。
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
  - 46 只：原判“源缺”，§3.2 复核推翻（89d4afa3 里全部有 open 行）。**Arch 06:51 裁定：与 235、68 同类，都是我方合并丢失，统一记 sw_pit 路径 P1。**
- 10-14 缩表根因（inventory 415f0783）：queue_chain_20261014.py:139-142 在 03:50–04:00 跑了 nightly_update --steps hsgt,sw，sw_pit_refresh 用一次被 relay 截断的拉取覆盖了表；脚本唯一的保护是“代码数 >5000”。修复见 §6 的防缩表闸门和取消覆盖旧表。
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
1. **主来源优先**：主来源为 89d4afa3（有条件接受，见 §5）；62 个分拉 raw 文件来源未知，只作佐证。
2. **全量只补缺**：全量 Y/N 分页只用来补分拉里完全没有的代码（标 source_rank=2）。
3. **open/closed 冲突**：同一 (code, l1, in_date) 或同一 code 有矛盾时，分拉里是 closed 的就以 closed 为准；全量里的陈旧 open 行丢弃，并记到 conflicts 明细。
4. **断言**：每个代码最多 1 条 open 行；违反就不落盘，非零退出。
5. **不编造**：在市但分拉里没有 open 行的代码写 quality_status=source_gap（不加 open 行，不补行业）。
6. **新版本输出**：只写 sw_l1_pit_v2.parquet 和 manifest，不覆盖 0b1d3432、89d4afa3。
7. **交易日历**：20130424 的 pretrade_date 由本地 is_open 推导（20130423），随 2027 包交付（不在本 diff 里）。

## 5. 和 FALSE_DONE 补数队列合并、数据来源（Arch 06:51 裁定）
- **主来源（Arch 06:53 更新）**：89d4afa3 **有条件接受**为主来源，待 Arch 自己做的两项核查：① 其 manifest 记的行数 7115 与实际 7920 不符；② 09-24..10-09 区间的增量。核查不过则走 §7 第 6 步 6b 分支。
- 10-18 01:08 的 62 个分拉 raw 文件：**来源未知，只作佐证证据**（dry-run 里出 normdiff_vs_raw0108，不作主来源）。
- （06:51 时的裁定是“62 个 raw 为主来源”，已被 06:53 的更新取代。）
- **实施当天必做交叉核验**：通过 relay 重拉到**新目录** tushare_raw/index_member_all_<YYYYMMDD>/（不覆盖 62 个文件），作为独立核验。两者 normdiff 必须为空，否则每一条差异都要解释并写入回执。relay 不通则不能实施（交叉核验是硬条件）。
- 队列里 `nightly_step|sw|20261014/15/16` 三项并入 v2；Arch 审过回执后标为 done，reason=`superseded_by sw_l1_pit_v2 (<sha>)`，改前先归档到 _recovery/data/。**不再单独跑 nightly sw 步骤**，SW 只改一次。
- index_classify（L1 名单）离线读已落地的 sw2021_classify_l1.parquet；实施日重拉时一并重拉做核对。

### 5.1 89d4afa3 来源（inventory 415f0783）
- 89d4afa3 与 output/data_v2_bundle 中的文件、以及 data_v2_bundle.tar（10-10 14:42）中的副本逐字节相同；其 manifest 的 fetch_time 为 2026-10-10T10:01:23-04:00（即 10-10 10:01 ET），由 tushare_relay_pull.py:140-151、223-230 写出；10-18 01:08 的文件是恢复出来的。
- **62 个 index_member_all raw 文件不在 tar 里，没有任何来源记录。**
- 是否满足条件 (a)（查清写入者和脚本）由 Arch 决定；无论如何，实施日的重拉交叉核验都是必做项。

### 5.2 时间证据
- bak 和当前表的原始时间戳已被 10-18 01:13 的恢复覆盖。Arch 接受内容证据（sha + 行级 diff）。**v2 manifest 必须写明：time_evidence=lost（被 2026-10-18 01:13 ET 工作区恢复覆盖），以内容证据代替。**

## 6. 代码（文本，未应用；不在 repo 建任何 .py，不运行）
总原则：输出永远不覆盖已存在文件，只写新版本文件；防缩表闸门同时加在 sw_pit_refresh.py 和 v2 构建脚本里；sw_pit_refresh.py 不再覆盖旧 L1 PIT 表。落代码前把旧脚本归档到 `_recovery/data/sw_l1_pit_v2_pre_<date>/`。

### 6.0 防缩表闸门阈值（提请 Arch 审）
与“上一版本”（manifest 指向的最近一份已审版本）比较，任一条触发就拒绝落盘、非零退出：
| 指标 | 阈值 |
|---|---|
| 总行数下降 | > 0.5% |
| 代码数（instrument 数）下降 | > 0.5% |
| 当前成员数（out_date 为空的行数）下降 | > 0.3% |
- 覆盖开关：`--allow-shrink <ok_path>`，必须指向 Arch 签的 .ok（scope 含 allow_shrink、未过期、signed_et 不在未来），否则开关无效。
- 取代 sw_pit_refresh.py 原来的绝对断言 `nunique()>5000`。没有上一版本（首次构建）时，必须有 `--allow-shrink` 的 .ok，并写明 baseline=none。
- 闸门结果写入 shrink_gate.json 和 manifest。
- 参考：10-14 那次 7743→7573 行（-2.2%）、5759→5600 代码（-2.8%），会被闸门拦下。

### 6.1 sw_pit_refresh.py diff
```diff
--- a/scripts/acquire/sw_pit_refresh.py
+++ b/scripts/acquire/sw_pit_refresh.py
@@ -2,4 +2,8 @@
-import sys, json, time, pathlib, pandas as pd
+import sys, json, time, pathlib, argparse, pandas as pd
 ROOT=pathlib.Path("/workspace/QuantLab"); sys.path.insert(0,str(ROOT))
 from quantlab.data_sources.tushare_proxy import relay,_to_df
+sys.path.insert(0,str(ROOT/"scripts/acquire")); from sw_l1_pit_v2_build import shrink_gate, versioned_path
+ap=argparse.ArgumentParser(); ap.add_argument("--allow-shrink",default=None); ARGS=ap.parse_args()
 OUTD=ROOT/"data/v2/sw_pit"; OUTD.mkdir(parents=True,exist_ok=True)
+STAMP=pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
@@ -26,9 +30,11 @@
 # 再按 L1 × Y/N 分拉补齐 (全量分页在 relay 端存在截断), 合并去重
+RAWD=ROOT/"data/v2/tushare_raw"/("index_member_all_"+STAMP); RAWD.mkdir(parents=True,exist_ok=False)
 for c in cls.index_code:
     for isn in "YN":
         try:
             df=call("index_member_all",l1_code=c,is_new=isn); df["is_new"]=isn; parts.append(df[df.l1_code==c])
+            df[df.l1_code==c].to_parquet(RAWD/f"{c}_{isn}.parquet",index=False)   # 分拉落盘到新目录
         except Exception as e: print("l1 fail",c,isn,e,flush=True)
         time.sleep(0.3)
@@ -33,3 +39,2 @@
 m=pd.concat(parts,ignore_index=True).drop_duplicates()
 print("union rows",len(m),"instruments",m.ts_code.nunique(),flush=True)
-assert m.ts_code.nunique()>5000, f"too few instruments {m.ts_code.nunique()} -> relay 截断, 不落盘"
@@ -40,1 +45,1 @@
-m.to_parquet(OUTD/"sw2021_members_l1l2l3_raw.parquet",index=False)
+m.to_parquet(versioned_path(OUTD/"sw2021_members_l1l2l3_raw.parquet",STAMP),index=False)   # 不覆盖
@@ -43,5 +48,10 @@
 for lv in ["l1","l2"]:
+    if lv=="l1":
+        print("l1 PIT 改由 sw_l1_pit_v2_build.py 生成, 此处不再写 industry_members_sw_l1_pit.parquet"); continue
     t=m[["instrument_id","ts_code","name",f"{lv}_code",f"{lv}_name","in_date","out_date","is_new","available_at","source","promotion_approved"]].copy()
     t["out_key"]=t.out_date.fillna(pd.Timestamp("2099-12-31"))
     t=t.sort_values("in_date").groupby(["instrument_id",f"{lv}_code","out_key"],as_index=False).first().drop(columns="out_key")
-    f=OUTD/f"industry_members_sw_{lv}_pit.parquet"; t.to_parquet(f,index=False)
+    prev=OUTD/f"industry_members_sw_{lv}_pit.parquet"
+    shrink_gate(t, pd.read_parquet(prev) if prev.exists() else None, id_col="instrument_id", allow_ok=ARGS.allow_shrink)
+    f=versioned_path(prev,STAMP); t.to_parquet(f,index=False)   # 新版本文件, 不覆盖
@@ -52,1 +62,1 @@
-json.dump(man,open(OUTD/"manifest.json","w"),ensure_ascii=False,indent=2); print(json.dumps(man,ensure_ascii=False))
+json.dump(man,open(versioned_path(OUTD/"manifest.json",STAMP),"x"),ensure_ascii=False,indent=2); print(json.dumps(man,ensure_ascii=False))
```

### 6.2 scripts/acquire/sw_l1_pit_v2_build.py 全文（仅文本）
```python
# SW2021 L1 PIT v2 构建. 主来源 89d4afa3(有条件接受, 见 5.1); 62 个 raw 与实施日重拉只作核验.
# 规则: 主来源优先; 全量分页只补主来源中完全没有的代码; closed 压过同键陈旧 open;
# 每代码 open<=1; 在市无 open 标 source_gap 不编造; 只写新版本文件; 防缩表闸门.
import sys, json, hashlib, argparse, pathlib, datetime as dt
import pandas as pd

ROOT = pathlib.Path("/workspace/QuantLab")
PRIMARY = ROOT/"data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet"      # 89d4afa3
PRIMARY_SHA = "89d4afa337435a2302b5c13fd4cf049b71eda2f20e1d9094f15d62cdb587f66c"
RAW_0108 = ROOT/"data/v2/tushare_raw/index_member_all"                          # 62 文件, 来源未知, 仅核验
FULL = ROOT/"data/v2/sw_pit/sw2021_members_l1l2l3_raw.parquet"
PREV = ROOT/"data/v2/sw_pit/industry_members_sw_l1_pit.parquet"                 # 0b1d3432: 闸门基线 + 修前统计
STOCK_BASIC = ROOT/"data/v2/meta/stock_basic_incl_delisted.parquet"
DELISTED = ROOT/"data/v2/ref/stock_delisted_v2.parquet"                         # 9d757b96
CAL = ROOT/"data/v2/calendar/trade_cal_sse_pit.parquet"
OUT = ROOT/"data/v2/sw_pit/sw_l1_pit_v2.parquet"
PROTECT = {"0b1d3432e30f7cdd907df393299cd2f552e1121899239985a00113c4dfcd89f6", PRIMARY_SHA}
WIN = ("2026-09-24", "2026-10-16")
THRESH = {"rows": 0.005, "codes": 0.005, "open": 0.003}
COLS = ["instrument_id", "l1_code", "l1_name", "in_date", "out_date", "is_new"]
TWELVE = ["sz.002420", "sz.002481", "sz.002597", "sz.003030", "sz.300699", "sz.300741",
          "sz.300777", "sz.300858", "sz.300972", "sh.603020", "sh.605077", "sh.688002"]

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()

def to_iid(ts):
    a, b = ts.split("."); return b.lower() + "." + a

def versioned_path(p, stamp):
    p = pathlib.Path(p); q = p.with_name(f"{p.stem}.{stamp}{p.suffix}")
    if q.exists(): raise FileExistsError(q)
    return q

def raw_files_sha(raw_dir):
    return {f.name: sha(f) for f in sorted(pathlib.Path(raw_dir).glob("801*.SI_[YN].parquet"))}

def _norm(d):
    d = d.copy()
    d["in_date"] = pd.to_datetime(d["in_date"], errors="coerce")
    d["out_date"] = pd.to_datetime(d["out_date"], errors="coerce")
    return d[COLS]

def load_primary(path=PRIMARY):
    assert sha(path) == PRIMARY_SHA, "主来源 sha 不符"
    d = pd.read_parquet(path, columns=["instrument_id", "sw_code", "sw_name", "in_date", "out_date", "is_new"])
    d = _norm(d.rename(columns={"sw_code": "l1_code", "sw_name": "l1_name"}))
    return d.assign(source_rank=1, src="89d4afa3")

def load_raw_dir(raw_dir):                            # 62 文件或实施日重拉目录
    fs = sorted(pathlib.Path(raw_dir).glob("801*.SI_[YN].parquet")); assert len(fs) == 62, len(fs)
    parts = []
    for f in fs:
        l1, isn = f.stem.split("_")
        d = pd.read_parquet(f, columns=["ts_code", "l1_code", "l1_name", "in_date", "out_date"])
        d = d[d.l1_code == l1].copy(); d["is_new"] = isn; parts.append(d)
    m = pd.concat(parts, ignore_index=True)
    m["instrument_id"] = m.ts_code.map(to_iid)
    return _norm(m).drop_duplicates()

def fill_from_full(prim, full_path=FULL):
    full = pd.read_parquet(full_path, columns=["ts_code", "l1_code", "l1_name", "in_date", "out_date", "is_new"])
    full["instrument_id"] = full.ts_code.map(to_iid); full = _norm(full)
    miss = sorted(set(full.instrument_id) - set(prim.instrument_id))
    add = full[full.instrument_id.isin(miss)].drop_duplicates().assign(source_rank=2, src="full_paged")
    return pd.concat([prim, add], ignore_index=True), miss

def resolve_open_closed(m):
    m = m.reset_index(drop=True); key = ["instrument_id", "l1_code", "in_date"]
    closed = set(map(tuple, m[m.out_date.notna()][key].values))
    stale = m.out_date.isna() & pd.Series([tuple(r) in closed for r in m[key].values], index=m.index)
    conflicts = m[stale].assign(reason="open_vs_closed_same_key")
    m = m[~stale]
    o = m[m.out_date.isna()].sort_values(["instrument_id", "source_rank", "in_date"], ascending=[True, True, False])
    dup = o[o.duplicated("instrument_id", keep="first")]
    return m.drop(dup.index), pd.concat([conflicts, dup.assign(reason="multi_open_lower_rank_or_older")])

def assert_one_open(m):
    n = m[m.out_date.isna()].groupby("instrument_id").size(); bad = n[n > 1]
    assert bad.empty, f"open>1: {bad.index.tolist()[:20]}"

def load_listed_universe(asof):                       # 与审计同口径: 沪深 6 位, list_date<=asof, 未退市
    sb = pd.read_parquet(STOCK_BASIC, columns=["ts_code", "list_date", "delist_date"])
    sb = sb[sb.ts_code.str.match(r"^\d{6}\.(SH|SZ)$")].copy()
    sb["list_date"] = pd.to_datetime(sb.list_date, errors="coerce")
    sb["delist_date"] = pd.to_datetime(sb.delist_date, errors="coerce")
    dl = set(pd.read_parquet(DELISTED, columns=["ts_code"]).ts_code)
    a = pd.Timestamp(asof)
    ok = (sb.list_date <= a) & (sb.delist_date.isna() | (sb.delist_date > a)) & ~sb.ts_code.isin(dl)
    return set(sb[ok].ts_code.map(to_iid))

def flag_source_gap(m, listed):                       # 不编造: 只列出, 不加行
    has_open = set(m[m.out_date.isna()].instrument_id)
    gap = sorted(set(listed) - has_open)
    return m.assign(quality_status="ok"), gap

def normdiff(a, b, la="a", lb="b"):                   # 只比 open 成分
    x = a[a.out_date.isna()][["instrument_id", "l1_code"]]
    y = b[b.out_date.isna()][["instrument_id", "l1_code"]]
    j = x.merge(y, on="instrument_id", how="outer", suffixes=("_" + la, "_" + lb), indicator=True)
    return j[(j._merge != "both") | (j["l1_code_" + la] != j["l1_code_" + lb])]

def trading_days():
    cal = pd.read_parquet(CAL, columns=["cal_date", "is_open"])
    d = pd.to_datetime(cal[cal.is_open == 1].cal_date.astype(str))
    return sorted(x for x in d if pd.Timestamp(WIN[0]) <= x <= pd.Timestamp(WIN[1]))

def daily_missing(t, days):
    out = []
    for d in days:
        live = t[(t.in_date <= d) & (t.out_date.isna() | (t.out_date > d))]
        out.append({"date": d.date().isoformat(), "missing": len(load_listed_universe(d) - set(live.instrument_id))})
    return pd.DataFrame(out)

def _kv(path):
    return dict(l.split("=", 1) for l in open(path).read().splitlines() if "=" in l)

def check_ok(path, need):                             # scope 含 need, 未过期, signed_et 不在未来
    kv = _kv(path); now = dt.datetime.now().astimezone()
    return (need in kv.get("scope", "") and dt.datetime.fromisoformat(kv["expires_et"]) > now
            and dt.datetime.fromisoformat(kv["signed_et"]) <= now)

def shrink_gate(new, prev, id_col="instrument_id", allow_ok=None):
    if prev is None:
        assert allow_ok and check_ok(allow_ok, need="allow_shrink"), "无上一版本, 需 allow_shrink .ok(baseline=none)"
        return {"baseline": None, "override_ok": allow_ok}
    r = {"rows": (len(prev), len(new)), "codes": (prev[id_col].nunique(), new[id_col].nunique()),
         "open": (int(prev.out_date.isna().sum()), int(new.out_date.isna().sum()))}
    bad = {k: v for k, v in r.items() if v[0] and (v[0] - v[1]) / v[0] > THRESH[k]}
    if bad and not (allow_ok and check_ok(allow_ok, need="allow_shrink")):
        raise SystemExit(f"SHRINK_GATE refuse: {bad}")
    return {"compare": r, "tripped": bad, "override_ok": allow_ok if bad else None}

def approved_normdiff(nd, ok_path):                   # 非空 normdiff 需 .ok 的 normdiff_allow 逐条列出
    if nd.empty: return True
    if not check_ok(ok_path, need="normdiff"): return False
    allowed = set(_kv(ok_path).get("normdiff_allow", "").split(","))
    return set(nd.instrument_id) <= allowed

def write_reports(od, m, conf, filled, gap, nds, before, after, gate):
    od = pathlib.Path(od); od.mkdir(parents=True, exist_ok=True)
    conf.to_csv(od/"conflicts.csv", index=False)
    pd.Series(filled, name="instrument_id", dtype=str).to_csv(od/"filled_from_full.csv", index=False)
    pd.Series(gap, name="instrument_id", dtype=str).to_csv(od/"source_gap.csv", index=False)
    for k, nd in nds.items(): nd.to_csv(od/f"normdiff_{k}.csv", index=False)
    before.merge(after, on="date", suffixes=("_before", "_after")).to_csv(od/"daily_missing_before_after.csv", index=False)
    m[m.instrument_id.isin(TWELVE)].sort_values(["instrument_id", "in_date"]).to_csv(od/"twelve_codes_resolution.csv", index=False)
    json.dump(gate, open(od/"shrink_gate.json", "w"), default=str, indent=2)

def write_manifest(out, s, m, gap, conf, gate, raw0108_sha, repull_sha, primary):
    man = dict(path=str(out), sha256=s, rows=len(m), instruments=int(m.instrument_id.nunique()),
               open_rows=int(m.out_date.isna().sum()), source_gap=gap, n_conflicts=len(conf), shrink_gate=gate,
               primary_source=primary,
               supporting=dict(raw_0108=raw0108_sha, raw_0108_status="source_unknown (supporting evidence only)",
                               repull=repull_sha),
               time_evidence="lost: bak/当前表原始时间戳被 2026-10-18 01:13 ET 工作区恢复覆盖; 以 sha + 行级 diff 内容证据代替",
               available_at="in_date 18:00 Asia/Shanghai (近似)", promotion_approved=False, revision="v2",
               built_et=dt.datetime.now().astimezone().isoformat())
    with open(out.with_suffix(".manifest.json"), "x") as f:     # "x": 已存在则失败, 不覆盖
        json.dump(man, f, ensure_ascii=False, indent=2, default=str)

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--out_dir", default="/tmp/sw_l1_pit_v2_dryrun")
    ap.add_argument("--repull_dir", required=True)            # 实施日重拉目录, 必填(交叉核验是硬条件)
    ap.add_argument("--primary", choices=["89d4afa3", "repull"], default="89d4afa3")
    ap.add_argument("--allow-shrink", dest="allow_shrink", default=None)
    ap.add_argument("--normdiff_ok", default=None)
    a = ap.parse_args(argv)
    rep = load_raw_dir(a.repull_dir)
    ref = load_primary()
    prim = ref if a.primary == "89d4afa3" else rep.assign(source_rank=1, src="repull")
    m, filled = fill_from_full(prim)
    m, conf = resolve_open_closed(m); assert_one_open(m)
    m, gap = flag_source_gap(m, load_listed_universe(WIN[1]))
    m = m.assign(available_at=m.in_date + pd.Timedelta(hours=18), promotion_approved=False, revision="v2")
    nds = {"vs_89d4afa3": normdiff(m, ref, "v2", "ref"),
           "vs_raw0108": normdiff(m, load_raw_dir(RAW_0108), "v2", "raw"),
           "vs_repull": normdiff(m, rep, "v2", "rep")}
    prev = pd.read_parquet(PREV, columns=["instrument_id", "l1_code", "in_date", "out_date"])
    prev = prev.assign(in_date=pd.to_datetime(prev.in_date), out_date=pd.to_datetime(prev.out_date))
    days = trading_days()
    before, after = daily_missing(prev, days), daily_missing(m, days)
    gate = shrink_gate(m, prev, allow_ok=a.allow_shrink)
    write_reports(a.out_dir, m, conf, filled, gap, nds, before, after, gate)
    if not a.execute:
        print("DRY-RUN only, no repo write"); return 0
    for k, nd in nds.items():
        assert nd.empty or (a.normdiff_ok and approved_normdiff(nd, a.normdiff_ok)), f"normdiff {k} 非空且未获认可"
    if OUT.exists(): raise FileExistsError(OUT)              # 不覆盖
    m.to_parquet(OUT, index=False); s = sha(OUT); assert s not in PROTECT
    primary = (dict(path=str(PRIMARY), sha256=PRIMARY_SHA, status="conditionally_accepted")
               if a.primary == "89d4afa3" else dict(path=a.repull_dir, status="repull_primary"))
    write_manifest(OUT, s, m, gap, conf, gate, raw_files_sha(RAW_0108), raw_files_sha(a.repull_dir), primary)
    print("WROTE", OUT, s); return 0

if __name__ == "__main__":
    sys.exit(main())
```
- 内存预估 <300MB（万行级）。daily_missing 每个交易日重算在市名单，11 天可接受。
- 说明：v2 由于 0b1d3432 本身缺 349 只，与它比只会“增长”，闸门不会误拦；之后的刷新以 v2 为基线。

### 6.3 selftest 全文：tests/test_sw_l1_pit_v2_build.py（仅文本，合成数据）
```python
# selftest: 合成数据, allow_real_data=false, out_dir 在 /tmp. 先 enforce 再 import 被测模块.
import sys, pathlib, tempfile
REPO = pathlib.Path("/workspace/QuantLab")
sys.path.insert(0, str(REPO / "scripts_eng"))
from ok_runner_pin import enforce
enforce(modes=["selftest"])                                   # 必须在 import 被测模块之前
sys.path.insert(0, str(REPO / "scripts/acquire"))
import pandas as pd
import sw_l1_pit_v2_build as B

def _df(rows):
    return B._norm(pd.DataFrame(rows, columns=B.COLS))

def _tmp():
    return pathlib.Path(tempfile.mkdtemp(dir="/tmp"))

def test_full_only_fills_absent():
    prim = _df([["sz.000001", "801780.SI", "银行", "2014-01-01", None, "Y"]]).assign(source_rank=1, src="p")
    t = _tmp()
    pd.DataFrame([["000001.SZ", "801010.SI", "农林", "2010-01-01", None, "Y"],
                  ["000002.SZ", "801180.SI", "地产", "2010-01-01", None, "Y"]],
                 columns=["ts_code", "l1_code", "l1_name", "in_date", "out_date", "is_new"]).to_parquet(t/"full.parquet")
    m, miss = B.fill_from_full(prim, t/"full.parquet")
    assert miss == ["sz.000002"]
    assert set(m[m.instrument_id == "sz.000001"].l1_code) == {"801780.SI"}

def test_closed_beats_stale_open_and_one_open():
    m = _df([["sz.002420", "801110.SI", "家电", "2021-07-30", "2026-06-30", "N"],
             ["sz.002420", "801110.SI", "家电", "2021-07-30", None, "Y"],
             ["sz.002420", "801230.SI", "综合", "2026-07-01", None, "Y"]]).assign(source_rank=1, src="p")
    m, conf = B.resolve_open_closed(m); B.assert_one_open(m)
    assert list(m[m.out_date.isna()].l1_code) == ["801230.SI"] and len(conf) == 1

def test_multi_open_keeps_rank1():
    m = pd.concat([_df([["sz.002481", "801010.SI", "农林", "2021-07-30", None, "Y"]]).assign(source_rank=1, src="p"),
                   _df([["sz.002481", "801120.SI", "食品", "2011-10-10", None, "Y"]]).assign(source_rank=2, src="f")])
    m, conf = B.resolve_open_closed(m); B.assert_one_open(m)
    assert list(m[m.out_date.isna()].l1_code) == ["801010.SI"]

def test_assert_one_open_raises():
    m = _df([["sz.000001", "a", "", "2020-01-01", None, "Y"], ["sz.000001", "b", "", "2021-01-01", None, "Y"]])
    try:
        B.assert_one_open(m)
    except AssertionError as e:
        assert "open>1" in str(e); return
    raise AssertionError("should fail")

def test_source_gap_not_fabricated():
    m = _df([["sz.000001", "801780.SI", "银行", "2014-01-01", None, "Y"]])
    m2, gap = B.flag_source_gap(m, {"sz.000001", "sz.000009"})
    assert gap == ["sz.000009"] and len(m2) == 1

def test_shrink_gate_thresholds():
    prev = _df([[f"sz.{i:06d}", "x", "", "2020-01-01", None, "Y"] for i in range(1000)])
    assert B.shrink_gate(prev.iloc[:997], prev)["tripped"] == {}      # -0.3%: 不超阈值
    try:
        B.shrink_gate(prev.iloc[:996], prev)                         # -0.4%: open 超 0.3%
    except SystemExit as e:
        assert "open" in str(e) and "rows" not in str(e); return
    raise AssertionError("should refuse")

def test_shrink_gate_override_needs_valid_ok():
    prev = _df([[f"sz.{i:06d}", "x", "", "2020-01-01", None, "Y"] for i in range(100)])
    t = _tmp(); ok = t/"x.ok"
    ok.write_text("scope=selftest\nsigned_et=2026-01-01T00:00:00-05:00\nexpires_et=2099-01-01T00:00:00-05:00\n")
    try:
        B.shrink_gate(prev.iloc[:50], prev, allow_ok=str(ok))        # scope 不含 allow_shrink -> 仍拒绝
    except SystemExit: return
    raise AssertionError("override without allow_shrink scope must fail")

def test_versioned_path_never_overwrites():
    f = _tmp()/"t.parquet"
    q = B.versioned_path(f, "S1"); q.write_text("x")
    try:
        B.versioned_path(f, "S1")
    except FileExistsError: return
    raise AssertionError("should refuse")

def test_normdiff():
    a = _df([["sz.000001", "a", "", "2020-01-01", None, "Y"]])
    b = _df([["sz.000001", "b", "", "2020-01-01", None, "Y"]])
    assert B.normdiff(a, a.copy()).empty and len(B.normdiff(a, b)) == 1

if __name__ == "__main__":
    for k, v in list(globals().items()):
        if k.startswith("test_"): v(); print("ok", k)
```

## 7. 执行步骤（全部在 §1 的排期窗口内）
1. Arch 先收到 §6.2、§6.3 的完整文件文本并审过，才签 dry-run .ok。之后签：code-change .ok（两个脚本 + 测试）、selftest .ok、run .ok（dry-run 与 execute 分开写明）；我自查 expires_et，并确认 signed_et 不在未来。
2. 把旧脚本归档到 _recovery/data/sw_l1_pit_v2_pre_<date>/，再落代码。
3. 跑 selftest（PYTHONDONTWRITEBYTECODE=1 nice -n 10）。
4. 实施日：relay 重拉到新目录 index_member_all_<YYYYMMDD>/（只拉，不建表）。
5. **dry-run**（输出到 /tmp/sw_l1_pit_v2_dryrun/）：默认 `--primary 89d4afa3 --repull_dir <新目录>` 建表，同时产出 normdiff_vs_89d4afa3.csv、normdiff_vs_repull.csv、conflicts.csv、daily_missing_before_after.csv、twelve_codes_resolution.csv、source_gap.csv、filled_from_full.csv、shrink_gate.json → 交 Arch 审。
6. **来源分支**：
   - 6a. 若 Arch 的两项核查（7115 vs 7920、09-24..10-09 增量）通过，且条件 (a)（写入者与脚本已查清，§5.1）**或** (b)（重拉与 89d4afa3 的 normdiff 为空或差异全部解释）成立，则以 89d4afa3 为主来源继续。
   - 6b. 两条都不成立：**改用重拉目录为主来源**（`--raw_dir index_member_all_<YYYYMMDD>`），重做 dry-run 交 Arch；并通知 Arch 重新评估叶23/24（它们钉的 89d4afa3 来源不可证）。
7. Arch 认可后 **execute**：只写 v2 文件和 manifest；运行前检查 pgrep 和 MemAvailable ≥ 2GB，运行中通过 /proc 监控 RSS ≤ 1.5GB。
8. 交回执；Arch 审过后，处理队列 3 项 sw、下游迁移（§14）和 .ok 重签。

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

## 11. Arch 裁定记录（Arch，2026-10-18 06:51 ET）
1. 46 只与 235、68 同类（我方合并丢失）；整个问题记 sw_pit 路径 P1；对叶23/24 影响等 Arch inventory。
2. （06:51）主来源 = 01:08 的 62 个 raw；**06:53 更新：改为 89d4afa3 有条件接受为主来源，62 个 raw 来源未知、只作佐证**。实施日 relay 重拉到新目录做独立核验必做，normdiff 须为空或逐条解释。
2b. （06:53）防缩表闸门原则接受；阈值待审（§6.0：行 0.5%、代码 0.5%、当前成员 0.3%，`--allow-shrink` 需 .ok）；取代 `>5000` 绝对断言；输出只写新版本文件。
3. 89d4afa3 作主来源的条件：(a) 查清写入者和脚本，或 (b) 重拉与其一致；都不成立则改用重拉为主来源并重评叶23/24（§7 第 6 步分支）。
4. 时间戳丢失：接受内容证据（sha + 行级 diff）；v2 manifest 写明时间证据被 10-18 01:13 恢复覆盖。
5. 队列 3 项 sw 并入 v2，审后标 superseded_by v2。
6. dry-run .ok 之前须交 helper 全文与 selftest 全文（§6.2、§6.3）。
7. 95 只新增代码须逐只追溯（结果见 §12）。

### 仍待 Arch
- §5.1 条件 (a) 是否成立；89d4afa3 两项核查（7115 vs 7920、09-24..10-09 增量）结果。
- §6.0 闸门阈值是否照此。
- §12：95 只“来源未知”是否接受“bak 本身被截断”的解释。

## 12. 95 只“修复新增”代码逐只追溯（只读，2026-10-18 06:52:41 ET）
- 定义：当前表 0b1d3432 有、bak 59734014 没有的代码，共 95 只。
- 输出：docs/v2/audit/data_ro_audit_20261018/SW_95_NEW_CODES_TRACE.csv（sha 7f0f4f0672d8bf153aec0bc8e7e012d6e3e3f59ee8cf41206412af8da3a5cc6e）。列：ts_code, category, list_date, delist_date, list_status, in_namechange, cur_rows, cur_open_rows, cur_min_in_date, in_89d4, open_in_89d4。
- 读取文件 sha：0b1d3432…89f6、59734014…2c9c、data/v2/meta/stock_basic_incl_delisted.parquet 2ef2d71d28957b0d8d7b8a599d4fcafbecc969f121e5ee072719ad202508eca8、data/v2/st_events/namechange_all.parquet 6b81ee0b0d60d6d468910fb606ea8e4d448618c4e67fbd5337ffe0b0523fba5a、89d4afa3…f66c。
- 命令：`PYTHONDONTWRITEBYTECODE=1 nice -n 10 /usr/bin/python3 -c "<pyarrow 只读 ts_code/in_date/out_date、list_date/delist_date/list_status、namechange ts_code、89d4afa3 instrument_id/out_date；集合差 + 分类，写 CSV>"`；不 import 项目代码；峰值 maxrss 164MB。

| 类别 | 数量 |
|---|---|
| 备份之后上市（list_date ≥ 20261014） | 0 |
| 代码变更 | 0（95 只都在 namechange_all 里出现，但那只是改名记录，没有代码映射；本地没有 code-mapping 数据，无法判为代码变更） |
| 来源未知 | **95** |

- 特征：95 只全部 list_status=L，上市日期 1992–2025（2022 年 20 只最多），没有新股；在当前表各 1 行且为 open；**在 89d4afa3 中全部存在且有 open 行**。
- 解读（待 Arch 认可）：这些是早已上市、在 89d4afa3 中有正常成分的股票，最可能是 **bak 自身那次拉取也被截断**，10-14 那次拉取恰好拿到了它们。说明 0b1d3432 和 bak 都是不完整的截断拉取结果，进一步支持以 89d4afa3 / 重拉为主来源，并加防缩表闸门。v2 重建后这 95 只预计都在（normdiff 覆盖）。

## 13. 下游迁移（坏表 0b1d3432 的消费方；inventory 415f0783）
v2 落地并经 Arch 审过后，由各 owner 自行把读取路径改到 v2，并由 Arch 重签相关 .ok；**Data 不改他们的代码**；通知由主 Agent 负责。
| 消费方 | 位置 | Owner |
|---|---|---|
| hiliq_capadv_b4_x2 | Strategy 脚本 | Strategy |
| fulla_b4_x2 | Strategy 脚本 | Strategy |
| intel_common.py | 第 170 行 | Intel |
| intel_event_study.py | — | Intel |
| intel_c1_gap_split.py | — | Intel |
| measure_baseline.py | output/v3/beta_risk_budget_prereg/measure_baseline.py:48 | 对应 owner（主 Agent 指派） |
- 在 owner 迁移完成前，0b1d3432 原样保留，不删除、不覆盖。
