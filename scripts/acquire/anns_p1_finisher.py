"""Wait for anns P1 (seal window trade days) then rebuild classified table, write Alpha draft, update ENG_PING."""
import time, json, subprocess, pathlib, datetime as dt, pandas as pd, pyarrow.parquet as pq, sys
ROOT=pathlib.Path("/workspace/QuantLab"); sys.path.insert(0,str(ROOT/"scripts/acquire"))
from event_flow_pull import anns_plan
R=ROOT/"data/v2/tushare_raw/anns_d"; OUT=ROOT/"logs/event_anns_v2.out"
def stats():
    p1,p2,p3=anns_plan(); have={f.stem:pq.read_metadata(f).num_rows for f in R.glob("*.parquet") if not f.name.endswith(".tmp.parquet")}
    g=lambda L:(sum(d in have for d in L),len(L))
    return p1,p2,p3,have,g
def update_eng(note):
    f=ROOT/"output/d1/ENG_PING_PATHS.json"; d=json.load(open(f))
    e=d.setdefault("event_flow_update",{}); e["announcements_coverage"]=note
    e["announcements_coverage_time"]=dt.datetime.now().astimezone().isoformat(timespec="seconds")
    json.dump(d,open(f,"w"),ensure_ascii=False,indent=1)
if __name__=="__main__":
    while "PHASE_DONE P1_seal_trade" not in OUT.read_text():
        time.sleep(300)
    subprocess.run(["python3","scripts/acquire/event_alpha_build.py"],cwd=ROOT,check=True)
    p1,p2,p3,have,g=stats()
    miss=[d for d in p1 if d not in have]; zero=[d for d in p1 if have.get(d)==0]
    trunc=sorted(d for d,n in have.items() if n>=5000 and d<="20240531")
    s=json.load(open(ROOT/"output/d1/event_alpha_build_summary.json"))["anns"]
    a,b=g(p1); c,d_=g(p2); e,f_=g(p3)
    note=(f"P1 密封窗交易日 2018-01-02→2024-05-31 已落 {a}/{b}（0 行 {len(zero)}，缺 {len(miss)}）；"
          f"P2 2024-06→2026-10-09 交易日 {c}/{d_}；P3 非交易日 {e}/{f_}，后台续拉。单日 5000 截断（≤2024-05-31）{len(trunc)} 天。")
    update_eng(note)
    md=f"""# 草稿：给 Alpha — 公告 P8 密封窗可开跑（未发送）

- 路径：`data/v2/events/announcements_classified_pit.parquet`（研究级，promotion_approved=false，classifier {s.get('classifier_version')}）
- 总量：{s['rows']} 行 / {s['codes']} 只，ann_date {s['range'][0]}→{s['range'][1]}
- 覆盖：{note}
- 上游无数据/缺失的密封窗交易日：{', '.join(miss+zero) or '无'}
- 单日 5000 条截断日期（密封窗内，共 {len(trunc)} 天；这些日的公告不全，后续用东财/巨潮按股补）：
  {', '.join(trunc)}
- available_at 口径：有 ann_time 时钟→用 ann_time（Asia/Shanghai）；无时钟→ann_date 23:59，即视作盘后，最早 T+1 开盘可交易。字段 `available_at_rule` 逐行标注。
- 只有标题+原文 URL，无正文；event_type 按标题规则分类（回购/增持/减持/业绩预增预减/问询函/回复/处罚/other）。
"""
    (ROOT/"output/d1/DRAFTS_ANNS_P8.md").write_text(md)
    print("FINISHER_DONE",note,flush=True)
