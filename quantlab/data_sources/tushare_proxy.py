"""Tushare-compatible clients: PCD relay + DataHub (direct, then Mac Clash proxy).
Keys from .env.datasources. Never log keys.
"""
import os, time, pathlib, requests, pandas as pd
_ENV = pathlib.Path(__file__).resolve().parents[2] / ".env.datasources"

def _load():
    if _ENV.exists():
        for l in _ENV.read_text().splitlines():
            if "=" in l and not l.startswith("#"):
                k, v = l.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
_load()

RELAY = "https://pcd.mobcvb.cn/tushare/pro"
DATAHUB_HTTPS = "https://datahubco.com/app-api/openapi/v1/tushare"
DATAHUB_HTTP = "http://datahubco.com/app-api/openapi/v1/tushare"

def _dh_proxies():
    p = os.environ.get("DATAHUB_HTTP_PROXY") or ""
    p = p.strip()
    if not p:
        return None
    return {"http": p, "https": p}

def _get(url, key, params, proxies=None, verify=True, retries=5, timeout=60):
    err = None
    for i in range(retries):
        try:
            r = requests.get(
                url,
                params={k: v for k, v in params.items() if v is not None},
                headers={"X-API-Key": key},
                timeout=timeout,
                verify=verify,
                proxies=proxies,
            )
            if r.status_code == 429:
                time.sleep(float(r.headers.get("Retry-After", 5))); continue
            try:
                return r.status_code, r.json()
            except Exception:
                return r.status_code, {"code": None, "msg": r.text[:300], "data": {}}
        except Exception as e:
            err = e
            time.sleep(min(30, 2 * (i + 1)))
    raise RuntimeError(f"failed: {err}")

def _to_df(d):
    data = d.get("data") or {}
    if isinstance(data, dict) and "fields" in data:
        return pd.DataFrame(data.get("items") or [], columns=data["fields"])
    if isinstance(data, list):
        return pd.DataFrame(data)
    return pd.DataFrame()

def relay(api, **p):
    # 180s: moneyflow/full-day pages were Read-timeouting at 90s on PCD promax
    to = int(os.environ.get("TSPRO_RELAY_TIMEOUT", "180"))
    return _get(f"{RELAY}/{api}", os.environ["TSPRO_PROXY_KEY"], p, timeout=to)

def datahub(api, **p):
    """Prefer direct HTTPS; fall back to DATAHUB_HTTP_PROXY if set and direct fails."""
    key = os.environ["DATAHUB_API_KEY"]
    proxy = _dh_proxies()
    last = None
    # order: direct HTTPS/HTTP first (Clash often down from cloud), then via proxy
    attempts = []
    for base in (DATAHUB_HTTPS, DATAHUB_HTTP):
        for name in (api, api.replace("_", "-")):
            attempts.append((base, name, None, 90))
    if proxy:
        for base in (DATAHUB_HTTPS, DATAHUB_HTTP):
            for name in (api, api.replace("_", "-")):
                attempts.append((base, name, proxy, 60))
    for base, name, prox, to in attempts:
        try:
            s, d = _get(f"{base}/{name}", key, p, proxies=prox, retries=2, timeout=to)
            if s == 200 and d.get("code") in (0, None) and "data" in d:
                return s, d
            last = (s, d)
            # non-retryable business responses
            if s in (200, 401, 403) and not (isinstance(d, dict) and d.get("code") in (0, None) and "data" in d):
                # keep trying other name/base on empty/404-ish
                if s == 200:
                    return s, d
            if s not in (404, 502, 503, 504) and prox is None:
                # unexpected direct error — still try next
                continue
        except Exception as e:
            last = e
            continue
    if isinstance(last, tuple):
        return last
    raise RuntimeError(f"datahub {api}: {last}")

def df(api, source="relay", **p):
    code, d = (relay if source == "relay" else datahub)(api, **p)
    if d.get("code") not in (0, None):
        raise RuntimeError(f"{api}/{source}: {d.get('code')} {d.get('msg')}")
    return _to_df(d)
