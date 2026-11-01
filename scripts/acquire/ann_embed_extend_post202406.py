"""Extend ann_embedding_corpus_pit with post-2024-06 titles from EM/cninfo by_stock_post202406.
Also writes classified subset append + coverage md. Does not touch promotion_approved_overall.
Usage: python3 scripts/acquire/ann_embed_extend_post202406.py [--min-files N]
"""
import argparse, gc, glob, hashlib, json, pathlib, re, zlib, tempfile, shutil
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

ROOT = pathlib.Path("/workspace/QuantLab")
V = ROOT / "data/v2"
TZ = "Asia/Shanghai"
CORPUS = V / "text/ann_embedding_corpus_pit.parquet"
CORPUS_LATEST = V / "text/ann_embedding_corpus_pit_through_latest.parquet"
COV = ROOT / "output/d1/ANN_EMBED_COVERAGE.md"
SUMF = ROOT / "output/d1/ann_embed_extend_summary.json"

RULES = [
    ("inquiry_reply", r"回复.*(问询|关注)函|(问询|关注)函.*回复"),
    ("inquiry_letter", r"问询函|关注函|监管工作函"),
    ("penalty", r"行政处罚|处罚决定|立案|纪律处分|公开谴责|警示函|监管措施"),
    ("buyback", r"回购"),
    ("insider_decrease", r"减持"),
    ("insider_increase", r"增持"),
    ("earnings_beat", r"业绩预增|扭亏|预盈|大幅增长"),
    ("earnings_miss", r"业绩预减|预亏|首亏|续亏|大幅下降"),
]
POL = {
    "buyback": 1, "insider_increase": 1, "earnings_beat": 1,
    "insider_decrease": -1, "earnings_miss": -1, "inquiry_letter": -1,
    "penalty": -1, "inquiry_reply": 0, "other": 0,
}
BUYBACK_SUB = [
    ("excluded_withdrawn_notice", r"[（(]已取消[)）]"),
    ("excluded_pledge_repo", r"质押式回购|股票质押|质押回购|约定购回|购回交易|延期购回|提前购回|补充质押|解除质押|新增质押"),
    ("excluded_treasury_repo", r"逆回购|报价回购|债券回购|理财"),
    ("excluded_perf_comp", r"业绩补偿|补偿股份|业绩承诺|发行股份购买资产|定向回购"),
    ("excluded_incentive_cancel", r"限制性股票|股权激励|激励计划|激励对象|激励股份|股票期权|员工持股|回购注销.*(离职|解锁|解除限售)"),
    ("excluded_non_share", r"(子公司|参股|控股股东|合伙).{0,20}回购.{0,10}(股权|出资|份额)|回购.{0,6}(股权|房产|资产|债券|转债|份额)|收益权|回购融资|回购款|永续"),
    ("excluded_treasury_sale", r"(集中竞价|大宗).{0,4}减持.{0,4}(结果|计划|进展)?|减持.{0,6}已?回购|出售.{0,8}回购"),
    ("repurchase_terminate", r"终止|(?<!已)取消|撤销|中止|放弃"),
    ("repurchase_done", r"实施完毕|实施结果|回购完成|完成回购|回购.{0,8}股份完成|完成.{0,4}公告|注销完成|注销.{0,10}(已回购|库存)|期限届满|届满|注销.{0,6}已?回购股份|已回购股份.{0,6}注销"),
    ("repurchase_ancillary", r"前十|债权人|法律意见|独立意见|核查意见|财务顾问|用途|调整|变更|延长|延期|问询|说明|减资|违规|专用证券账户"),
    ("repurchase_progress", r"进展|首次.{0,6}回购|达到|超过|比例|回购.{0,10}股份情况"),
    ("repurchase_plan", r"预案|方案|报告书|提议|拟.{0,15}回购|回购.{0,15}(议案|计划)"),
]
SUB_POL = {
    "repurchase_plan": 1, "repurchase_progress": 1, "repurchase_done": 1,
    "repurchase_terminate": -1, "repurchase_ancillary": 0, "repurchase_other": 0,
}
cv = "rules_v2_" + hashlib.sha1(json.dumps([RULES, BUYBACK_SUB], ensure_ascii=False).encode()).hexdigest()[:8]
STD = ["ts_code", "ann_date", "ann_time", "title", "url", "name", "ann_type", "src"]

def rd(f, cols):
    have = set(pq.read_schema(f).names)
    return pd.read_parquet(f, columns=[c for c in cols if c in have])

def cninfo(f):
    c = rd(f, ["announcementTime", "instrument", "announcementTitle", "adjunctUrl", "secName", "columnId"])
    if len(c) == 0:
        return pd.DataFrame(columns=STD)
    ts = pd.to_datetime(pd.to_numeric(c.announcementTime, errors="coerce"), unit="ms", utc=True).dt.tz_convert(TZ).dt.tz_localize(None)
    ex = c.instrument.str.split(".").str[0].str.upper()
    cd = c.instrument.str.split(".").str[1]
    return pd.DataFrame({
        "ts_code": cd + "." + ex,
        "ann_date": ts.dt.strftime("%Y%m%d"),
        "ann_time": ts.astype(str),
        "title": c.announcementTitle.astype(str).str.replace(r"</?em>", "", regex=True),
        "url": "http://static.cninfo.com.cn/" + c.adjunctUrl.astype(str),
        "name": c.secName, "ann_type": c.columnId, "src": "cninfo_hisAnnouncement",
    })

def eastm(f):
    e = rd(f, ["instrument", "notice_date", "title", "art_code", "secName", "column", "display_time"])
    if len(e) == 0:
        return pd.DataFrame(columns=STD)
    ex = e.instrument.str.split(".").str[0].str.upper()
    cd = e.instrument.str.split(".").str[1]
    ann_time = None
    if "display_time" in e.columns:
        ann_time = e.display_time
    return pd.DataFrame({
        "ts_code": cd + "." + ex,
        "ann_date": e.notice_date.astype(str).str.replace("-", "").str[:8],
        "ann_time": ann_time,
        "title": e.title.astype(str),
        "url": "https://data.eastmoney.com/notices/detail/" + cd + "/" + e.art_code.astype(str) + ".html",
        "name": e.secName, "ann_type": e.column, "src": "eastmoney_ann",
    })

def norm(x):
    for c in STD:
        if c not in x:
            x[c] = None
    x = x[STD].copy()
    x["ann_date"] = x.ann_date.astype(str).str.replace("-", "").str[:8]
    for c in ["ann_time", "ann_type", "name"]:
        x[c] = x[c].astype(object).where(x[c].notna(), None)
    # keep only post-2024-06
    x = x[x.ann_date >= "20240601"]
    return x

def classify(a):
    title = a.title.fillna("").astype(str)
    et = pd.Series("other", index=a.index, dtype=object)
    for k, p in RULES[::-1]:
        et[title.str.contains(p, regex=True)] = k
    a = a.copy()
    a["event_type"] = et
    tt = pd.to_datetime(a.ann_time, errors="coerce", format="ISO8601")
    hasclock = tt.notna() & ((tt.dt.hour + tt.dt.minute) > 0)
    base = pd.to_datetime(a.ann_date, format="%Y%m%d", errors="coerce")
    a["available_at"] = pd.to_datetime(np.where(hasclock, tt, base + pd.Timedelta(hours=23, minutes=59))).tz_localize(TZ, ambiguous="infer", nonexistent="shift_forward")
    a["available_at_rule"] = np.where(hasclock, "ann_time", "ann_date 23:59 (no clock; tradable next session)")
    a = a.rename(columns={"ts_code": "instrument", "title": "ann_title"})
    a["polarity"] = a.event_type.map(POL).astype(float)
    a["subtype"] = None
    bb = a.event_type.eq("buyback")
    if bb.any():
        bt = title[bb]
        st = pd.Series("repurchase_other", index=bt.index, dtype=object)
        for k, p in BUYBACK_SUB[::-1]:
            st[bt.str.contains(p, regex=True)] = k
        a.loc[bb, "subtype"] = st
        exm = bb & a.subtype.astype(str).str.startswith("excluded_")
        a.loc[exm, "event_type"] = "buyback_excluded"
        a.loc[exm, "polarity"] = 0.0
        a.loc[bb & ~exm, "polarity"] = a.loc[bb & ~exm, "subtype"].map(SUB_POL).astype(float)
    a["event_id"] = [
        hashlib.sha1(f"{i}|{d}|{t}|{u}".encode()).hexdigest()[:16]
        for i, d, t, u in zip(a.instrument, a.ann_date, a.ann_title, a.url)
    ]
    a = a.drop_duplicates("event_id")
    k = (
        a.instrument.astype(str) + "|" + a.ann_date + "|"
        + a.ann_title.astype(str).str.replace(r"^[^：:]{1,12}[：:]", "", regex=True).str.replace(r"\s", "", regex=True)
    )
    a["sources_all"] = a.src.groupby(k).transform(lambda s: "|".join(sorted(set(s))))
    a = a[~k.duplicated()].copy()
    a["source"] = a.src
    a["promotion_approved"] = False
    a["classifier_version"] = cv
    a["meta_json"] = [
        json.dumps({"url": u, "ann_type": t, "name": n}, ensure_ascii=False)
        for u, t, n in zip(a.url, a.ann_type, a.name)
    ]
    return a

def to_corpus(cls):
    title = cls["ann_title"].astype(str)
    sha = [hashlib.sha256(t.encode()).hexdigest() for t in title]
    return pd.DataFrame({
        "event_id": cls["event_id"].astype("string"),
        "instrument": cls["instrument"].astype("string"),
        "ts_code": cls["instrument"].astype("string"),
        "title": title.astype("string"),
        "body_text": None,
        "body_source": pd.Series(["title_only"] * len(cls), dtype="string"),
        "url": cls["url"].astype("string"),
        "author": None,
        "publish_at": cls["available_at"],
        "available_at": cls["available_at"],
        "source": cls["source"].astype("string"),
        "event_type": cls["event_type"].astype("string"),
        "polarity": cls["polarity"].astype(float),
        "classifier_version": cls["classifier_version"].astype("string"),
        "content_sha256": pd.Series(sha, dtype="string"),
        "promotion_approved": False,
    })

def load_new():
    cf = sorted(glob.glob(str(V / "announcements/cninfo/by_stock_post202406/*.parquet")))
    ef = sorted(glob.glob(str(V / "announcements/eastmoney/by_stock_post202406/*.parquet")))
    parts = []
    for f in cf:
        try:
            d = norm(cninfo(f))
            if len(d):
                parts.append(d)
        except Exception as e:
            print("skip cn", f, e, flush=True)
    for f in ef:
        try:
            d = norm(eastm(f))
            if len(d):
                parts.append(d)
        except Exception as e:
            print("skip em", f, e, flush=True)
    if not parts:
        return pd.DataFrame(columns=STD), len(cf), len(ef)
    raw = pd.concat(parts, ignore_index=True)
    return raw, len(cf), len(ef)

def priority_set():
    p = ROOT / "data/v2/announcements/cninfo/priority_post202406_ts.txt"
    if p.exists():
        return set(p.read_text().split())
    return set()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-files", type=int, default=50, help="require at least this many EM/CN files before rebuild")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    em_n = len(list((V / "announcements/eastmoney/by_stock_post202406").glob("*.parquet")))
    cn_n = len(list((V / "announcements/cninfo/by_stock_post202406").glob("*.parquet")))
    print(f"files EM={em_n} CN={cn_n}", flush=True)
    if em_n + cn_n < args.min_files and not args.force:
        print(f"WAIT need>={args.min_files} files", flush=True)
        return 2

    raw, ncf, nef = load_new()
    print(f"raw rows={len(raw)} from cn_files={ncf} em_files={nef}", flush=True)
    if len(raw) == 0:
        print("NO_NEW", flush=True)
        return 1

    cls = classify(raw)
    del raw
    gc.collect()
    print(f"classified {len(cls)} range {cls.ann_date.min()}→{cls.ann_date.max()} codes {cls.instrument.nunique()}", flush=True)

    # save classified post slice (append-friendly standalone)
    post_cls = V / "events/announcements_classified_pit_post202406.parquet"
    cls_out_cols = [
        "instrument", "event_type", "subtype", "available_at", "polarity", "event_id",
        "ann_title", "source", "promotion_approved", "classifier_version", "meta_json",
        "ann_date", "available_at_rule", "url", "sources_all",
    ]
    cls[cls_out_cols].to_parquet(post_cls, index=False)

    new_corp = to_corpus(cls)
    old = pd.read_parquet(CORPUS)
    # drop any old rows that somehow overlap event_id, then concat
    old = old[~old.event_id.isin(set(new_corp.event_id))]
    # also ensure no pre-existing post-202406 in old (shouldn't)
    aa = pd.to_datetime(old.available_at)
    old_pre = old[aa < "2024-06-01"]
    merged = pd.concat([old_pre, new_corp], ignore_index=True)
    # write through_latest AND update main corpus path (Alpha reads this)
    tmp = pathlib.Path(str(CORPUS_LATEST) + ".tmp")
    merged.to_parquet(tmp, index=False)
    tmp.replace(CORPUS_LATEST)
    tmp2 = pathlib.Path(str(CORPUS) + ".tmp")
    merged.to_parquet(tmp2, index=False)
    tmp2.replace(CORPUS)

    pr = priority_set()
    aa2 = pd.to_datetime(merged.available_at)
    post = merged[aa2 >= "2024-06-01"]
    codes_post = set(post.instrument.astype(str)) if len(post) else set()
    pr_hit = len(pr & codes_post) if pr else 0  # post-202406 priority coverage
    pr_hit_any = len(pr & set(merged.instrument.astype(str))) if pr else 0
    body_rate = float(merged.body_text.notna().mean()) if "body_text" in merged.columns else 0.0

    summary = {
        "rows_total": int(len(merged)),
        "rows_post202406": int(len(post)),
        "rows_new_this_build": int(len(new_corp)),
        "available_at_min": str(aa2.min()),
        "available_at_max": str(aa2.max()),
        "codes_total": int(merged.instrument.nunique()),
        "codes_post": int(post.instrument.nunique()) if len(post) else 0,
        "priority_n": len(pr),
        "priority_with_post_ann": pr_hit,
        "priority_with_any_ann_fullhist": pr_hit_any,
        "priority_coverage": round(pr_hit / len(pr), 4) if pr else None,
        "body_nonnull_rate": body_rate,
        "source_post": post.source.value_counts().to_dict() if len(post) else {},
        "event_type_post": post.event_type.value_counts().to_dict() if len(post) else {},
        "paths": {
            "corpus": str(CORPUS),
            "corpus_through_latest": str(CORPUS_LATEST),
            "classified_post": str(post_cls),
        },
        "classifier_version": cv,
        "em_files": em_n,
        "cn_files": cn_n,
    }
    json.dump(summary, open(SUMF, "w"), ensure_ascii=False, indent=2, default=str)

    md = f"""# 公告 embedding 语料覆盖（title_only，已延至最新）

> 更新：自动 · Data · 研究级 · **未改** `promotion_approved_overall`  
> 产出：`{CORPUS}`（同内容副本 `{CORPUS_LATEST.name}`）

## 摘要

| 项 | 值 |
|---|---|
| 行数 | {len(merged):,} |
| 其中 2024-06→今 | {len(post):,} |
| available_at 范围 | {aa2.min()} → {aa2.max()} |
| 优先集合规模 | {len(pr)} |
| 优先集合 2024-06后有公告 | {pr_hit} ({(pr_hit/len(pr)*100 if pr else 0):.1f}%) |
| body_source | 多为 `title_only` |
| 正文率 | {body_rate:.4%} |
| promotion_approved | false |

## 2024-06 后 source

{chr(10).join(f'| {k} | {v} |' for k,v in sorted(summary['source_post'].items(), key=lambda x:-x[1])) or '| (无) | |'}

## 2024-06 后 event_type

{chr(10).join(f'| {k} | {v} |' for k,v in sorted(summary['event_type_post'].items(), key=lambda x:-x[1])[:12]) or '| (无) | |'}

## 局限

- 优先池为 CSI300/500 历史成分 ∪ 流通市值前 1500（多年末并集），非全市场。
- 正文 body 另任务补齐；本表仍以 title_only 为主。
- available_at 继承披露时钟（ann_time 或 ann_date 23:59 Asia/Shanghai），**非抓取完成时间**。

**End.**
"""
    COV.write_text(md)
    print(json.dumps(summary, ensure_ascii=False, default=str), flush=True)
    print("EXTEND_DONE", flush=True)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
