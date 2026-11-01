"""QuantLab versioned research, data audit, shared signals, forward paper accounts and public-cache utilities. --source applies to public fetching; research uses --manifest exclusively."""

from __future__ import annotations

import argparse
import pickle
import sys
from pathlib import Path

import pandas as pd

from quantlab.config import OUTPUT_DIR, CONFIG


def build_panels(source: str, market: str, limit: int | None = None):
    """Snapshot collection only. Research replay requires a versioned manifest."""
    if market != "a": raise ValueError("US execution is disabled; background data only")
    from quantlab.data.sources import DataFeed
    feed = DataFeed(source=source)
    cand = feed.fetch_candidates(market)
    if limit:
        cand = cand.sort_values("float_mktcap", ascending=False).head(limit)
    panels = {}
    for code in cand.index:
        frame = feed.fetch_daily(market, str(code), refresh=True)
        if frame is not None and len(frame): panels[str(code)] = frame
    return panels, cand, feed.fetch_benchmark(market)


def run_backtest(source="auto", market="a", save=True, manifest=None, strategy="legacy_repaired", forecasts=None, data_mode='strict', feature_profile=None, industry_policy='enforced',risk_policy='P0',candidate='baseline',allocation_policy='legacy'):
    from quantlab.backtest.engine import Engine, blocked_result
    from quantlab.data.contracts import load_dataset, DataContractError
    from quantlab.report.runs import persist_run, finalize_run_identity
    path = Path(manifest) if manifest else CONFIG.data.cache_dir.parent / "research" / "manifest.json"
    if not path.exists():
        result = blocked_result(["dataset_manifest_missing", str(path), "legacy_caches_are_not_PIT_raw_execution_data"])
    else:
        try:
            from quantlab.data.qualification import audit_manifest
            from copy import deepcopy
            cfg=deepcopy(CONFIG)
            if feature_profile:cfg.research.feature_profile=feature_profile
            if data_mode=='free_research':cfg.research.universe_mode='pit_liquidity'
            assessment=audit_manifest(path,profile=data_mode,require_industry=(strategy=='opportunity' and cfg.research.feature_profile=='price_volume_industry') or (data_mode=='strict' and industry_policy=='enforced'))
            if assessment['status'] not in ('qualified_for_daily_research','research_ready'):result=blocked_result(assessment['reasons'])
            else:
                ds=load_dataset(path,profile=data_mode)
                if isinstance(forecasts,(str,Path)):
                    from quantlab.strategy.opportunity import load_forecasts
                    forecasts=load_forecasts(forecasts,ds.version)
                result=Engine(cfg,market=market).run(ds,strategy=strategy,forecasts=forecasts,data_mode=data_mode,industry_policy=industry_policy,risk_policy=risk_policy,candidate=candidate,allocation_policy=allocation_policy)
        except (DataContractError, KeyError, ValueError) as exc: result = blocked_result([str(exc)])
    finalize_run_identity(result)
    if save:
        folder = persist_run(result)
        result["artifact_directory"] = str(folder)
    return result


def cmd_fetch(args):
    panels, _, bench = build_panels(args.source, args.market, args.limit)
    latest = {c: str(p.index[-1].date()) for c, p in panels.items()}
    print({"status": "public_cache_only", "latest_dates": latest,
           "note": "Fetch does not certify PIT universe, market rules or corporate actions."})


def cmd_backtest(args):
    from quantlab.report.html import build_html_report
    result = run_backtest(args.source, args.market, manifest=getattr(args, "manifest", None),
                          strategy=getattr(args, "strategy", "legacy_repaired"), forecasts=getattr(args,"forecasts",None),
                          data_mode=getattr(args,'data_mode','strict'),feature_profile=getattr(args,'feature_profile',None),industry_policy=args.industry_policy,risk_policy=args.risk_policy,candidate=args.candidate,allocation_policy=args.allocation_policy)
    folder = Path(result["artifact_directory"])
    report = build_html_report(result, title="QuantLab 研究验证报告", out=folder / "report.html")
    _print_perf(result)
    print(f"[backtest] {report}")


def _print_perf(result):
    from quantlab.report.metrics import performance_table
    print("[run_health]", result.get("run_health", {}))
    print('[industry_policy]',result.get('industry_policy'),result.get('research_exceptions',[]))
    print("[status]", result.get("status", "legacy_unvalidated"), result.get("reasons", []))
    if result.get("status") in ("blocked_data", "unverified_data_gaps") or (result.get("run_health") and not result["run_health"]["research_interpretable"]):
        print("[performance] 未验证，绩效指标不发布")
        return
    print("[research metrics; no live return claim]", performance_table(result["nav"], result["daily_return"]))
    for name, baseline in result.get("baselines", {}).items():
        print(name, performance_table(baseline["nav"], baseline["daily_return"]))


def signal_payload(result):
    meta = {k: result.get(k) for k in ("run_id", "data_version", "model_version", "as_of", "status", "reasons", "data_mode", "data_assessment", "industry_policy", "research_exceptions", "risk_policy", "risk_policy_version", "candidate", "allocation_policy", "rotation_advice")}
    meta.update(promotion_approved=False, account_type="simulation", executable=False)
    if result.get("status") != "research_unvalidated":
        return dict(meta, signal_date=None, exec_date=None, trades=[], orders=[])
    trades = result.get("trades", [])
    latest = trades[-1] if trades else {}
    state = result.get("account", [{}])[-1]
    prior = state.get("weights", {})
    pending = [o for o in result.get("orders", []) if o["status"] in ("pending", "partial")]
    if not pending:
        return dict(meta, signal_date=latest.get("signal_date"), exec_date=None, trades=[], orders=[], note="没有待执行订单")
    rows=[]
    for o in pending:
        c=o['instrument_id'];qty=state.get('quantities',{}).get(c,0)
        delta=o['remaining']*(1 if o['side']=='buy' else -1)
        target_qty=max(0,qty+delta)
        target_weight=prior.get(c,0)*target_qty/qty if qty else latest.get('weights',{}).get(c,0.)
        rows.append((c,target_weight,prior.get(c,0.),'买入' if delta>0 else '清仓' if target_qty==0 else '减仓'))
    return dict(meta, signal_date=latest.get("signal_date"), exec_date=latest.get("exec_date"), trades=rows,
                orders=pending,
                note="方向与数量来自待执行订单；权重仅为估计。逐单信号日及未成交原因见orders。研究模拟账户，须另行核对实际成交。")


def cmd_signals(args):
    import json
    from quantlab.report.runs import persist_run
    result = run_backtest(args.source, args.market, save=False, manifest=getattr(args, "manifest", None), strategy=args.strategy, forecasts=args.forecasts,
                          data_mode=args.data_mode,feature_profile=args.feature_profile,industry_policy=args.industry_policy,risk_policy=args.risk_policy,candidate=args.candidate,allocation_policy=args.allocation_policy)
    folder = persist_run(result)
    payload = signal_payload(result)
    out = folder / "signals.json"
    out.write_text(json.dumps(payload, default=str, ensure_ascii=False, indent=2))
    print(json.dumps(payload, default=str, ensure_ascii=False, indent=2))
    print(out)


def cmd_quote(args) -> None:
    """实时行情查询：可按 --symbols 指定，缺省查当前持仓。"""
    from quantlab.data.realtime import batch_quotes
    from quantlab.portfolio.current import snapshot
    symbols = args.symbols
    if symbols:
        codes = [s.strip() for s in symbols.split(",") if s.strip()]
    else:
        holds = snapshot(with_quotes=False)
        codes = [h["code"] for h in holds[:args.limit]] or ["600519", "000001"]
    df = batch_quotes(codes)
    if df.empty:
        print("no quote available")
        return
    cols = ["code", "name", "price", "pre_close", "pct_chg", "amount", "time", "source"]
    print(df[cols].to_string(index=False))
    print(f"\n行情时间: {df['time'].iloc[0]}  数据源: {df['source'].iloc[0]}")


def cmd_monitor(args):
    import json
    from quantlab.strategy.monitor import daily_expert_pulse
    result = daily_expert_pulse(args.limit, manifest=getattr(args, "manifest", None), strategy=args.strategy, forecasts=args.forecasts,
                               data_mode=args.data_mode,feature_profile=args.feature_profile,industry_policy=args.industry_policy,risk_policy=args.risk_policy,candidate=args.candidate,allocation_policy=args.allocation_policy)
    print(json.dumps(result, ensure_ascii=False, default=str, indent=2))


def cmd_web(args) -> None:
    from quantlab.webapp.app import main as web_main
    web_main(args.port)


def cmd_research(args):
    import json
    from quantlab.data.qualification import audit_manifest
    from quantlab.data.contracts import load_dataset
    from quantlab.pipeline import run_suite,DEFAULT_PROTOCOL
    report=audit_manifest(args.manifest)
    if report['status']!='qualified_for_daily_research':
        folder=Path(args.output);folder.mkdir(parents=True,exist_ok=True)
        from quantlab.data.contracts import fingerprint
        (folder/('blocked_'+fingerprint(report)[:12]+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2))
        print(json.dumps(report,ensure_ascii=False,indent=2));return
    protocol=json.loads(Path(args.protocol).read_text()) if args.protocol else DEFAULT_PROTOCOL
    print(json.dumps(run_suite(load_dataset(args.manifest),args.output,protocol),ensure_ascii=False,indent=2,default=str))


def cmd_forward(args):
    import json
    from quantlab.forward import ForwardBook
    from quantlab.data.contracts import load_dataset
    from quantlab.strategy.opportunity import Forecast
    book=ForwardBook(args.book,args.model_version,strategy=args.strategy,risk_policy=args.risk_policy,candidate=args.candidate,data_mode=args.data_mode)
    if args.cmd=='forward-status':result=book.status()
    elif args.cmd=='forward-reconcile':
        if not args.fills:raise ValueError('--fills required')
        result=book.reconcile(json.loads(Path(args.fills).read_text()))
    else:
        from quantlab.data.qualification import audit_manifest
        assessment=audit_manifest(args.manifest,profile=args.data_mode,require_industry=False)
        if assessment['status'] not in ('qualified_for_daily_research','research_ready'):print(json.dumps(assessment,ensure_ascii=False));return
        ds=load_dataset(args.manifest,profile=args.data_mode)
        if args.cmd=='forward-recover':
            from quantlab.strategy.opportunity import load_forecasts
            result=book.recover(ds,load_forecasts(args.forecasts,ds.version) if args.forecasts else {})
            print(json.dumps(result,ensure_ascii=False,default=str,indent=2));return
        f=None
        if args.model:
            from quantlab.strategy.opportunity import load_model,opportunity_features,normalized_features
            from quantlab.data.market import panels_for_research,universe_at
            model=load_model(args.model);d=pd.Timestamp(ds.manifest['as_of']).normalize()
            _,amount,_=panels_for_research(ds);eligible,_=universe_at(ds,d,amount,CONFIG)
            f=model.predict(normalized_features(opportunity_features(ds)),d,eligible)
        if args.forecast:
            row=json.loads(Path(args.forecast).read_text());row['expected_returns']=pd.Series(row['expected_returns'])
            f=Forecast(**row)
        result=book.step(ds,f)
    print(json.dumps(result,ensure_ascii=False,default=str,indent=2))


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="quantlab")
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("fetch", "backtest", "signals", "web", "quote", "monitor"):
        sp = sub.add_parser(name)
        sp.add_argument("--source", default="auto",
                        choices=["akshare", "yfinance", "auto"])
        sp.add_argument("--market", default="a", choices=["a", "us"])
        sp.add_argument("--port", type=int, default=8899)
        sp.add_argument("--symbols", default="")
        sp.add_argument("--limit", type=int, default=25)
        sp.add_argument("--manifest", default=None, help="经过哈希校验的研究数据集清单")
        sp.add_argument("--strategy", default="legacy_repaired", choices=["legacy_repaired", "opportunity", "buy_hold", "monthly_equal", "vol_matched_equal"])
        sp.add_argument('--risk-policy',choices=['P0','P1','P2'],default='P0')
        sp.add_argument('--candidate',choices=['baseline','quality_pb','quality_coverage','industry_rotation'],default='baseline')
        sp.add_argument('--allocation-policy',choices=['legacy','equal'],default='legacy')
        sp.add_argument('--industry-policy', choices=['enforced','omit_for_diagnostic'], default='enforced')
        sp.add_argument("--forecasts",default=None,help="研究流水线冻结的预测文件")
        sp.add_argument('--data-mode',choices=['strict','free_research'],default='strict')
        sp.add_argument('--feature-profile',choices=['price_volume','price_volume_industry'],default=None)
        sp.add_argument("--reset-cache", action="store_true", help="强制重拉全部历史(绕过本地缓存)")
    audit=sub.add_parser('data-audit');audit.add_argument('--manifest',default='data/research/manifest.json')
    audit.add_argument('--data-mode',choices=['strict','free_research'],default='strict')
    audit.add_argument('--feature-profile',choices=['price_volume','price_volume_industry'],default='price_volume_industry')
    free=sub.add_parser('free-research');free.add_argument('--manifest',default='data/free_research/dataset/manifest.json')
    free.add_argument('--output',default='output/free_research');free.add_argument('--train-start',default='2017-01-01');free.add_argument('--test-start',default='2020-01-01')
    compare=sub.add_parser('compare-strategies');compare.add_argument('--manifest',default='data/free_research_120/dataset/manifest.json')
    compare.add_argument('--output',default='output/return_comparison')
    legacy=sub.add_parser('compare-legacy');legacy.add_argument('--manifest',required=True)
    legacy.add_argument('--output',default='output/legacy_comparison')
    legacy.add_argument('--diagnostic-sample',action='store_true',help='Explicitly allow a bounded historical sample; never market-wide evidence')
    dynamic=sub.add_parser('compare-risk');dynamic.add_argument('--manifest',required=True)
    dynamic.add_argument('--output',default='output/dynamic_risk');dynamic.add_argument('--skip-stress',action='store_true')
    dynamic.add_argument('--reference-audit',default=None)
    reference=sub.add_parser('replay-reference');reference.add_argument('--manifest',required=True)
    reference.add_argument('--targets',required=True);reference.add_argument('--original-account')
    reference.add_argument('--start',required=True);reference.add_argument('--end',required=True)
    reference.add_argument('--cost-mult',type=float,default=1.);reference.add_argument('--output',default='output/reference1882/cash_replay')
    evidence=sub.add_parser('evidence-audit');evidence.add_argument('--bundle',required=True)
    v2s=sub.add_parser('v2-smoke');v2s.add_argument('--mandate',default=None);v2s.add_argument('--d0-root',default=None)
    v2p=sub.add_parser('v2-proto-smoke');v2p.add_argument('--mandate',default=None);v2p.add_argument('--d0-root',default=None);v2p.add_argument('--session',default=None);v2p.add_argument('--late-session',default=None);v2p.add_argument('--max-instruments',type=int,default=300);v2p.add_argument('--single-session',action='store_true')
    v2e=sub.add_parser('v2-eng-smoke');v2e.add_argument('--mandate',default=None);v2e.add_argument('--d0-root',default=None);v2e.add_argument('--session',default=None);v2e.add_argument('--late-session',default=None);v2e.add_argument('--max-instruments',type=int,default=80);v2e.add_argument('--factor-max-instruments',type=int,default=None);v2e.add_argument('--ic-lookback-sessions',type=int,default=12);v2e.add_argument('--forward-horizon',type=int,default=5);v2e.add_argument('--skip-factors',action='store_true');v2e.add_argument('--markdown-only',action='store_true')
    v2st=sub.add_parser('v2-strategy-smoke');v2st.add_argument('--mandate',default=None);v2st.add_argument('--d0-root',default=None);v2st.add_argument('--session',default=None);v2st.add_argument('--use-d1',action='store_true');v2st.add_argument('--n-synth',type=int,default=40)
    # Eng one-click skeletons (research-only; promotion untouched)
    tl=sub.add_parser('trading-loop',help='TradingAgents-adapt stub loop (no LLM/orders)');tl.add_argument('--session',default='2024-07-01');tl.add_argument('--instrument',default='510500.SH');tl.add_argument('--log',default=None);tl.add_argument('--show-graph',action='store_true')
    fe=sub.add_parser('factor-evolve',help='QuantMind-style factor evolve stub → weight long-table');fe.add_argument('--smoke',action='store_true');fe.add_argument('--capital',type=int,default=600000,choices=[600000,1000000]);fe.add_argument('--top-k',type=int,default=5);fe.add_argument('--out',default=None)
    bs=sub.add_parser('book-smoke',help='Mandate book smoke (default --skip-run skeleton)');bs.add_argument('--skip-run',action='store_true',default=True);bs.add_argument('--run-nav',action='store_true',help='actually run NAV (heavier)');bs.add_argument('--stock-path',default=None);bs.add_argument('--alpha-event-path',default=None);bs.add_argument('--out',default='output/v3/book_smoke_stock_etf');bs.add_argument('--receipt',default='docs/v2/BOOK_SMOKE_STOCK_ETF_RECEIPT_20261012_ZH.md');bs.add_argument('--windows',default='X2');bs.add_argument('--capitals',default='600000,1000000');bs.add_argument('--sleeves',default=None);bs.add_argument('--arms',default='BOOK,C0')
    sk=sub.add_parser('skeleton-smoke',help='one-click trading_loop+factor_evolve+book_smoke+weight contract');sk.add_argument('--book-nav',action='store_true');sk.add_argument('--capital',type=int,default=600000,choices=[600000,1000000]);sk.add_argument('--top-k',type=int,default=5);sk.add_argument('--out',default=None)
    ldr=sub.add_parser('live-dry-run',help='G1-G5→weights→book-smoke research dry-run (no orders)');ldr.add_argument('--capital',type=int,default=600000,choices=[600000,1000000]);ldr.add_argument('--top-k',type=int,default=5);ldr.add_argument('--out',default=None);ldr.add_argument('--gates-only',action='store_true')
    cpp=sub.add_parser('capacity-adv-pin',help='pin capacity_adv paper D1 inputs (sha256/version) in output/loop/capacity_adv_FROZEN_CONFIG.json');cpp.add_argument('--repin',action='store_true')
    ptp=sub.add_parser('paper-track',help='generic shadow paper track (s6) via b4_paper spec');ptp.add_argument('--track',required=True,choices=['s6']);ptp.add_argument('--mode',default='monitor',choices=['backfill','forward','monitor','all','rehash']);ptp.add_argument('--new-60w');ptp.add_argument('--new-100w');ptp.add_argument('--dry-run',action='store_true');ptp.add_argument('--receipt')
    wgp=sub.add_parser('weight-gate',help='history<=2026-10-09 row match + new-row checks (6%%, sum=1, no neg)');wgp.add_argument('--old',required=True);wgp.add_argument('--new',required=True);wgp.add_argument('--record',default=None)
    lsp=sub.add_parser('loop-sync',help='leaf status index -> output/loop; --writeback writes factory_feedback (priority/fitness/blacklist only)');lsp.add_argument('--writeback',action='store_true')
    pdp=sub.add_parser('paper-daily',help='EOD paper update: capacity_adv + B4 (no orders)');pdp.add_argument('--run-nav',action='store_true');pdp.add_argument('--no-extend',action='store_true');pdp.add_argument('--force',action='store_true')
    alp=sub.add_parser('alert-ingest',help='validate AI intel alerts -> data/v2/alerts');alp.add_argument('path',nargs='?',default=None);alp.add_argument('--date',default=None)
    b4p=sub.add_parser('b4-paper',help='B4 concentrated three-leg PAPER track 2 (no orders; live/promotion false)');b4p.add_argument('--mode',choices=['backfill','forward','monitor','all','rehash'],default='monitor');b4p.add_argument('--new-60w',default=None);b4p.add_argument('--new-100w',default=None);b4p.add_argument('--dry-run',action='store_true');b4p.add_argument('--receipt',default=None)
    cap=sub.add_parser('capacity-adv-paper',help='capacity_adv paper wire: validate weights + book-smoke (no live orders)');cap.add_argument('--stock-path',default='output/ai_factory/g1g5_capacity_adv_daily_weights_20261013_111219.parquet');cap.add_argument('--run-nav',action='store_true',help='materialize NAV (heavier; default skip-run)');cap.add_argument('--capitals',default='600000,1000000');cap.add_argument('--windows',default='X2');cap.add_argument('--out',default='output/v3/book_smoke_g1g5_capacity_adv_paper');cap.add_argument('--receipt',default='docs/v2/BOOK_SMOKE_CAPACITY_ADV_PAPER_WIRE_ZH.md');cap.add_argument('--skip-validate',action='store_true')
    research=sub.add_parser('research');research.add_argument('--manifest',default='data/research/manifest.json')
    research.add_argument('--protocol');research.add_argument('--output',default='output/research_v3')
    for name in ('forward-step','forward-status','forward-reconcile','forward-recover'):
        fp=sub.add_parser(name);fp.add_argument('--book',required=True);fp.add_argument('--model-version',required=True)
        fp.add_argument('--strategy',choices=['legacy_repaired','opportunity'],default='legacy_repaired')
        fp.add_argument('--risk-policy',choices=['P0','P1','P2'],default='P0')
        fp.add_argument('--candidate',choices=['baseline','quality_pb','quality_coverage','industry_rotation'],default='baseline')
        fp.add_argument('--data-mode',choices=['strict','free_research'],default='strict')
        fp.add_argument('--manifest',default='data/research/manifest.json');fp.add_argument('--forecast');fp.add_argument('--fills');fp.add_argument('--model');fp.add_argument('--forecasts')
    args = p.parse_args(argv)
    if args.cmd=='trading-loop':
        from quantlab.agents.trading_loop.run_stub import main as _tl
        argv2=[]
        if args.session: argv2 += ['--session', args.session]
        if args.instrument: argv2 += ['--instrument', args.instrument]
        if args.log: argv2 += ['--log', args.log]
        if args.show_graph: argv2 += ['--show-graph']
        raise SystemExit(_tl(argv2))
    if args.cmd=='factor-evolve':
        from quantlab.agents.factor_evolve.run_stub import main as _fe
        argv2=[]
        if args.smoke: argv2 += ['--smoke']
        else: argv2 += ['--smoke']  # Eng CLI always smoke unless Leo opens real panels
        argv2 += ['--capital', str(args.capital), '--top-k', str(args.top_k)]
        if args.out: argv2 += ['--out', args.out]
        raise SystemExit(_fe(argv2))
    if args.cmd=='book-smoke':
        from quantlab.portfolio.book_smoke import run as _bs
        import json as _json
        argv2=['--windows', args.windows, '--capitals', args.capitals, '--arms', args.arms, '--out', args.out, '--receipt', args.receipt]
        if args.sleeves: argv2 += ['--sleeves', args.sleeves]
        if args.stock_path: argv2 += ['--stock-path', args.stock_path]
        if args.alpha_event_path: argv2 += ['--alpha-event-path', args.alpha_event_path]
        if not args.run_nav: argv2 += ['--skip-run']
        result=_bs(argv2)
        print(_json.dumps(result, ensure_ascii=False, indent=2, default=str))
        raise SystemExit(0 if result.get('strategy_promotion_approved') is False else 1)
    if args.cmd=='skeleton-smoke':
        from quantlab.v2_skeleton_smoke import run_skeleton_smoke
        import json as _json
        status=run_skeleton_smoke(book_nav=args.book_nav, capital=args.capital, top_k=args.top_k, out_dir=args.out)
        print(_json.dumps(status, ensure_ascii=False, indent=2, default=str))
        raise SystemExit(0 if status.get('ok') else 1)
    if args.cmd=='live-dry-run':
        from quantlab.v2_live_dryrun import run_live_dryrun
        import json as _json
        status=run_live_dryrun(capital=args.capital, top_k=args.top_k, out_dir=args.out, skip_skeleton_tail=args.gates_only)
        print(_json.dumps(status, ensure_ascii=False, indent=2, default=str))
        raise SystemExit(0 if status.get('ok') else 1)
    if args.cmd=='capacity-adv-pin':
        from quantlab.portfolio.research_loop import capacity_adv_pin
        raise SystemExit(capacity_adv_pin(repin=args.repin))
    if args.cmd=='paper-track':
        from quantlab.portfolio.paper_track import run as _pt
        raise SystemExit(_pt(['--track',args.track,'--mode',args.mode]+(['--new-60w',args.new_60w] if args.new_60w else [])+(['--new-100w',args.new_100w] if args.new_100w else [])+(['--dry-run'] if args.dry_run else [])+(['--receipt',args.receipt] if args.receipt else [])))
    if args.cmd=='weight-gate':
        from quantlab.portfolio.research_loop import weight_gate
        raise SystemExit(weight_gate(args.old, args.new, args.record))
    if args.cmd=='loop-sync':
        from quantlab.portfolio.research_loop import loop_sync
        raise SystemExit(loop_sync(do_writeback=args.writeback))
    if args.cmd=='paper-daily':
        from quantlab.portfolio.research_loop import paper_daily
        raise SystemExit(paper_daily(run_nav=args.run_nav, run_extend=not args.no_extend, force=args.force))
    if args.cmd=='alert-ingest':
        from quantlab.portfolio.research_loop import alert_ingest
        raise SystemExit(alert_ingest(args.path, args.date))
    if args.cmd=='b4-paper':
        from quantlab.portfolio.b4_paper import run as _b4
        raise SystemExit(_b4(['--mode', args.mode]+(['--new-60w',args.new_60w] if args.new_60w else [])+(['--new-100w',args.new_100w] if args.new_100w else [])+(['--dry-run'] if args.dry_run else [])+(['--receipt',args.receipt] if args.receipt else [])))
    if args.cmd=='capacity-adv-paper':
        import json as _json
        from quantlab.platform.weight_long_table import validate_weight_path, assert_session_coverage_path
        from quantlab.portfolio.book_smoke import run as _bs
        sleeves='{"core":0.0,"stock":1.0,"alpha_event":0.0}'  # table already carries 510300 ballast
        meta={}
        if not args.skip_validate:
            meta['validate']=validate_weight_path(args.stock_path, require_rows=True)
            if meta['validate'].get('status')!='ok':
                print(_json.dumps(meta, ensure_ascii=False, indent=2, default=str)); raise SystemExit(1)
            meta['coverage']=assert_session_coverage_path(args.stock_path, target_end='2026-10-09')
            if not meta['coverage'].get('ok'):
                print(_json.dumps(meta, ensure_ascii=False, indent=2, default=str)); raise SystemExit(1)
        argv2=['--windows', args.windows, '--capitals', args.capitals, '--arms', 'BOOK,C0',
               '--out', args.out, '--receipt', args.receipt, '--sleeves', sleeves,
               '--stock-path', args.stock_path]
        if not args.run_nav:
            argv2 += ['--skip-run']
        result=_bs(argv2)
        result['capacity_adv_paper']=meta
        result['eng_doc']='docs/v2/CAPACITY_ADV_PAPER_ENG_ZH.md'
        result['live_orders']=False
        result['promotion_path']='paper'
        print(_json.dumps(result, ensure_ascii=False, indent=2, default=str))
        raise SystemExit(0 if result.get('strategy_promotion_approved') is False else 1)
    if args.cmd=='v2-smoke':
        from quantlab.v2_smoke import run_smoke
        import json as _json
        status=run_smoke(mandate_path=args.mandate,d0_root=args.d0_root)
        print(_json.dumps(status,ensure_ascii=False,indent=2,default=str))
        raise SystemExit(0 if status.get('ok') else 1)
    if args.cmd=='v2-proto-smoke':
        from quantlab.v2_proto_smoke import run_proto_smoke
        import json as _json
        status=run_proto_smoke(mandate_path=args.mandate,d0_root=args.d0_root,session=args.session,late_session=args.late_session,max_instruments=args.max_instruments,dual_session=not args.single_session)
        print(_json.dumps(status,ensure_ascii=False,indent=2,default=str))
        raise SystemExit(0 if status.get('ok') else 1)
    if args.cmd=='v2-eng-smoke':
        from quantlab.v2_eng_smoke import run_eng_smoke
        import json as _json
        status=run_eng_smoke(mandate_path=args.mandate,d0_root=args.d0_root,session=args.session,late_session=args.late_session,max_instruments=args.max_instruments,factor_max_instruments=args.factor_max_instruments,ic_lookback_sessions=args.ic_lookback_sessions,forward_horizon=args.forward_horizon,skip_factors=args.skip_factors)
        if args.markdown_only:
            print(status.get('sample_tables_markdown') or '')
        else:
            print(_json.dumps(status,ensure_ascii=False,indent=2,default=str))
            print('\n----- SAMPLE TABLES (markdown) -----\n')
            print(status.get('sample_tables_markdown') or '')
        raise SystemExit(0 if status.get('ok') else 1)
    if args.cmd=='v2-strategy-smoke':
        from quantlab.v2_strategy_smoke import run_strategy_smoke
        import json as _json
        status=run_strategy_smoke(mandate_path=args.mandate,d0_root=args.d0_root,session=args.session,use_d1=args.use_d1,n_synth=args.n_synth)
        print(_json.dumps(status,ensure_ascii=False,indent=2,default=str))
        raise SystemExit(0 if status.get('ok') else 1)
    if args.cmd=='compare-risk':
        import json
        from quantlab.policy_comparison import run_comparison
        print(json.dumps(run_comparison(args.manifest,args.output,run_stress=not args.skip_stress,reference_audit=args.reference_audit),ensure_ascii=False,default=str,indent=2));return
    if args.cmd=='replay-reference':
        import json
        from quantlab.reference_cash_replay import run_reference
        print(json.dumps(run_reference(args.manifest,args.targets,args.output,start=args.start,end=args.end,
            cost_mult=args.cost_mult,original_account=args.original_account),ensure_ascii=False,default=str,indent=2));return
    if args.cmd=='compare-legacy':
        from quantlab.legacy_comparison import run_comparison
        import json
        print(json.dumps(run_comparison(args.manifest,args.output,diagnostic_sample=args.diagnostic_sample),ensure_ascii=False,default=str,indent=2));return
    if args.cmd=='compare-strategies':
        import json
        from quantlab.comparison import run_comparison
        result=run_comparison(args.manifest,args.output)
        print(json.dumps({k:v for k,v in result.items() if k not in ('selection','data_assessment')},ensure_ascii=False,default=str,indent=2));return
    if args.cmd=='free-research':
        import json
        from quantlab.free_research import run_free_research
        print(json.dumps(run_free_research(args.manifest,args.output,train_start=args.train_start,test_start=args.test_start),ensure_ascii=False,default=str,indent=2));return
    if args.cmd=='evidence-audit':
        import json
        from quantlab.evidence import verify_bundle
        path=Path(args.bundle)
        print(json.dumps(verify_bundle(json.loads(path.read_text()),path.parent),ensure_ascii=False,indent=2,default=str));return
    if args.cmd=='data-audit':
        import json
        from quantlab.data.qualification import audit_manifest
        print(json.dumps(audit_manifest(args.manifest,profile=args.data_mode,require_industry=args.feature_profile=='price_volume_industry'),ensure_ascii=False,indent=2));return
    if args.cmd=='research':
        cmd_research(args);return
    if args.cmd.startswith('forward-'):
        cmd_forward(args);return
    if getattr(args, "reset_cache", False):
        CONFIG.data.reset_cache = True
    cmds = {"fetch": cmd_fetch, "backtest": cmd_backtest, "signals": cmd_signals,
            "web": cmd_web, "quote": cmd_quote, "monitor": cmd_monitor}
    cmds[args.cmd](args)


if __name__ == "__main__":
    main(sys.argv[1:])
