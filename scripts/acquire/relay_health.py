"""Tushare 中转 pcd.mobcvb.cn 健康探测 (快速失败用). 结果缓存 output/relay_health.json 5 分钟.
relay_up() -> bool ; 环境变量 RELAY_FORCE_DOWN=1 强制视为宕机."""
import json, os, time, pathlib, subprocess
ROOT = pathlib.Path("/workspace/QuantLab"); F = ROOT / "output/relay_health.json"
HOST = "pcd.mobcvb.cn"; TTL = int(os.environ.get("RELAY_HEALTH_TTL", "300"))
def probe(timeout=8):
    import requests
    t = time.time()
    try:
        r = requests.get(f"https://{HOST}/tushare/pro/trade_cal", params={"exchange": "SSE", "start_date": "20261001", "end_date": "20261002"},
                         headers={"X-API-Key": os.environ.get("TSPRO_PROXY_KEY", "")}, timeout=timeout)
        ok = r.status_code < 500; err = None if ok else f"http {r.status_code}"
    except Exception as e:
        ok, err = False, str(e)[:200]
    st = dict(host=HOST, up=ok, err=err, sec=round(time.time() - t, 2), checked_at=time.strftime("%Y-%m-%dT%H:%M:%S%z"), ts=time.time())
    F.write_text(json.dumps(st, ensure_ascii=False, indent=1)); return st
def relay_up():
    if os.environ.get("RELAY_FORCE_DOWN") == "1": return False
    try:
        st = json.loads(F.read_text())
        if time.time() - st["ts"] < TTL: return st["up"]
    except Exception: pass
    return probe()["up"]
if __name__ == "__main__": print(json.dumps(probe(), ensure_ascii=False))
