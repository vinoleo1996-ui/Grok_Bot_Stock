import pandas as pd, glob, datetime, pathlib
from zoneinfo import ZoneInfo
R="data/v2/tushare_raw"
a=pd.read_parquet("output/d1/limit_cov_1c85_by_code_year.parquet"); a["ex"]=a.code.str[:2]
F=["limit_up","limit_down","open_status","tradestatus","amount"]
t=a.groupby("y")[F+["rows"]].sum()
L=["# LIMIT_COVERAGE_2018 — 涨跌停/停牌/成交额 全市场覆盖（研究级，promotion_approved=false）",
f"生成：{datetime.datetime.now(ZoneInfo("America/New_York")):%Y-%m-%d %H:%M} ET。脚本：scripts/acquire/alpha_limit_coverage.py, alpha_limit_doc.py。",
"","## A. 1c85 D0 panels（data/local_market/1c85fd9aceaa03c3c4863bec/panels，全部 6034 标的，非抽样）",
"分母 = 2018-01-01 起 panel 行数（含停牌/BJ 行）。open_status 中 'unknown' 记为空。","",
"| 年 | 行数 | "+" | ".join(F)+" |","|---|---|"+"---|"*len(F)]
for y,r in t.iterrows(): L.append(f"| {y} | {int(r.rows)} | "+" | ".join(f"{r[c]/r.rows*100:.2f}%" for c in F)+" |")
L+=["","### 按交易所（limit_up / tradestatus 非空率）","","| 年 | 交易所 | 行数 | limit_up | tradestatus |","|---|---|---|---|---|"]
for (y,e),r in a.groupby(["y","ex"])[["limit_up","tradestatus","rows"]].sum().iterrows():
    L.append(f"| {y} | {e} | {int(r.rows)} | {r.limit_up/r.rows*100:.1f}% | {r.tradestatus/r.rows*100:.1f}% |")
a["miss"]=a.rows-a.limit_up; nb=a[(a.ex!="bj")&(a.miss>0)].groupby("code").miss.sum().sort_values(ascending=False)
L+=["","## 缺口清单（1c85）",
"1. **北交所（bj.*）全部缺 limit_up/limit_down/tradestatus/open_status**（2021-11 起，约 23.3 万行）；amount 有。",
"2. 1c85 panel 截止 2026-06-30；2026-07-01 起由 asof_extend_tushare_202610 panels 承接（Tushare stk_limit/suspend_d，含 limit_up/limit_down/tradestatus）。",
"3. open_status 仅比 limit_up 多出极少数行；其本质由 limit 规则推导，不是交易所原始字段。",
f"4. 沪深非 BJ 缺 limit_up 的标的 {len(nb)} 只、共 {int(nb.sum())} 行（主要为 510300 ETF、689009 CDR、上市首日/无涨跌幅限制日）。Top 20：",""]
L+=[f"- {c}: {int(m)} 行" for c,m in nb.head(20).items()]
L+=["","## B. Tushare 原始（按 trade_date 全市场，data/v2/tushare_raw/{daily,stk_limit,suspend_d}）",""]
for api in ["daily","stk_limit","suspend_d"]:
    fs=sorted(glob.glob(f"{R}/{api}/*.parquet")); ds=[pathlib.Path(f).stem for f in fs]
    by={}
    for f in fs: by.setdefault(pathlib.Path(f).stem[:4],[]).append(f)
    L.append(f"- **{api}**：{len(fs)} 个交易日文件，{ds[0] if ds else '-'} → {ds[-1] if ds else '-'}；按年天数 "+", ".join(f"{y}:{len(v)}" for y,v in sorted(by.items())))
# BJ coverage from tushare stk_limit
fs=sorted(glob.glob(f"{R}/stk_limit/*.parquet"))
if fs:
    rows=[]
    for f in fs:
        d=pd.read_parquet(f,columns=["ts_code"]); rows.append((pathlib.Path(f).stem[:4],len(d),d.ts_code.str.endswith(".BJ").sum()))
    s=pd.DataFrame(rows,columns=["y","n","bj"]).groupby("y").sum()
    L+=["","Tushare stk_limit 每年总行 / 其中 BJ 行（用于补 1c85 北交所缺口）：",""]+[f"- {y}: {int(r.n)} / BJ {int(r.bj)}" for y,r in s.iterrows()]
L+=["","## 结论",
"- 沪深 2018-01 → 2026-06：limit_up/limit_down/tradestatus/amount 非空率 ≥99.5%（全市场，非抽样），可支撑 H1。",
"- 北交所：1c85 无涨跌停/停牌状态；Tushare stk_limit/suspend_d/daily 已回补完整 2018-01-02→2026-06-30（2058 交易日，fail=0；log: logs/alpha_limit_hist.log）。BJ 覆盖见上表。",
"- tradestatus 来自 baostock 缓存（1c85）/ suspend_d（extend），口径不同：停牌日 1c85 有行而 Tushare daily 无行。"]
pathlib.Path("docs/v2/LIMIT_COVERAGE_2018.md").write_text("\n".join(L)); print("ok")
