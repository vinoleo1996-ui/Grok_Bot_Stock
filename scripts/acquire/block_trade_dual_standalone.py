"""block_trade 双源(relay+datahub)满窗 2018-01→LAST 独立限速进程. 复用 queue_chain_20261014.block():
per_day 按日文件断点续拉(已存在则跳过), mem<2GB 暂停, 每调用 sleep 0.3s.
幂等: 若 DONE 标记存在且产物+manifest 存在且 sha 一致 → 直接退出. 队列内 block() 跑到时日文件已全在, 只做零拉取的重合并."""
import sys,json,pathlib,datetime
ROOT=pathlib.Path("/workspace/QuantLab"); sys.path.insert(0,str(ROOT)); sys.path.insert(0,str(ROOT/"scripts/acquire"))
import queue_chain_20261014 as q
P=ROOT/"data/v2/events/block_trade_2018plus.parquet"; M=P.with_name(P.stem+"_manifest.json")
DONE=ROOT/"output/markers/block_trade_2018plus.DONE"
def complete():
    if not (DONE.exists() and P.exists() and M.exists()): return False
    m=json.load(open(M)); return m.get("sha256")==q.sha(P) and m.get("n_fails",99)<50
if __name__=="__main__":
    if complete(): q.log("Q2_block_trade_standalone","skip_complete"); sys.exit(0)
    q.log("Q2_block_trade_standalone","start",last=q.LAST)
    q.block()
    m=json.load(open(M))
    if m.get("n_fails",99)<50:
        DONE.parent.mkdir(parents=True,exist_ok=True); DONE.write_text(json.dumps(dict(sha256=m["sha256"],rows=m["rows"],ts=datetime.datetime.now().isoformat())))
    q.log("Q2_block_trade_standalone","finished",rows=m["rows"],n_fails=m.get("n_fails"))
