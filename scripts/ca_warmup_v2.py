#!/usr/bin/env python3
"""D3 warm-up: fetch Eastmoney sharebonus detail for 2024-2026 into data/v2/corporate_actions."""
from __future__ import annotations
import hashlib, json, time, urllib.parse, urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import pandas as pd

ROOT = Path('/workspace/QuantLab')
OUT = ROOT / 'data/v2/corporate_actions'
RAW = OUT / 'raw_eastmoney'
OUT.mkdir(parents=True, exist_ok=True)
RAW.mkdir(parents=True, exist_ok=True)
EAST = 'https://datacenter-web.eastmoney.com/api/data/v1/get'
TZ = ZoneInfo('America/New_York')
NOW = datetime.now(TZ)

def fetch_period(report: str):
    rows = []
    page = 1
    pages = 1
    while page <= pages:
        params = dict(
            reportName='RPT_SHAREBONUS_DET', columns='ALL', pageSize='500',
            pageNumber=str(page), sortColumns='SECURITY_CODE', sortTypes='1',
            source='WEB', client='WEB', filter=f"(REPORT_DATE='{report}')",
        )
        url = EAST + '?' + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=40) as resp:
            payload = json.load(resp)
        path = RAW / f'{report}_p{page}.json'
        raw = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode()
        path.write_bytes(raw)
        path.with_suffix('.meta.json').write_text(json.dumps({
            'sha256': hashlib.sha256(raw).hexdigest(), 'report': report, 'page': page,
            'fetched_at': NOW.isoformat(),
        }, indent=2))
        result = payload.get('result')
        if not payload.get('success') or not result:
            break
        pages = int(result.get('pages') or 1)
        for row in result.get('data') or []:
            rows.append(row)
        page += 1
        time.sleep(0.35)
    return rows

def to_instrument(code: str) -> str:
    c = str(code).zfill(6)
    if c.startswith(('5','6','9')): return f'sh.{c}'
    if c.startswith(('4','8')): return f'bj.{c}'
    return f'sz.{c}'

def main():
    # quarterly report dates 2024-2026
    periods = pd.period_range('2024-01-01', '2026-09-30', freq='Q')
    reports = [str(p.end_time.date()) for p in periods]
    all_rows = []
    for rep in reports:
        try:
            rows = fetch_period(rep)
            print(json.dumps({'report': rep, 'rows': len(rows)}, ensure_ascii=False), flush=True)
            all_rows.extend(rows)
        except Exception as exc:
            print(json.dumps({'report': rep, 'error': repr(exc)}, ensure_ascii=False), flush=True)

    if not all_rows:
        (OUT/'manifest.json').write_text(json.dumps({'ok': False, 'rows': 0}, indent=2))
        return

    df = pd.DataFrame(all_rows)
    # Normalize key fields when present (Eastmoney column names vary)
    colmap = {}
    for c in df.columns:
        u = c.upper()
        if u in ('SECURITY_CODE','SECURITYCODE'): colmap[c] = 'security_code'
        elif u in ('SECURITY_NAME_ABBR','SECURITYNAME'): colmap[c] = 'security_name'
        elif 'EX_DATE' in u or u == 'EX_DIVIDEND_DATE': colmap[c] = 'ex_date'
        elif 'RECORD' in u and 'DATE' in u: colmap[c] = 'record_date'
        elif 'PAY' in u and 'DATE' in u: colmap[c] = 'pay_date'
        elif 'NOTICE' in u and 'DATE' in u: colmap[c] = 'notice_date'
        elif 'CASH' in u and ('TAX' in u or 'DIVIDEND' in u or 'PTE' in u): colmap[c] = 'cash_per_share'
        elif u in ('TRANSFER_RATIO','BONUS_RATIO','STOCK_DIVIDEND'): colmap[c] = 'share_ratio'
        elif u == 'REPORT_DATE': colmap[c] = 'report_date'
    norm = df.rename(columns=colmap).copy()
    if 'security_code' in norm.columns:
        norm['instrument_id'] = norm['security_code'].map(to_instrument)
    # Eng-ish ledger columns (partial)
    ledger_cols = ['instrument_id','record_date','ex_date','pay_date','notice_date','cash_per_share','share_ratio','report_date','security_name']
    present = [c for c in ledger_cols if c in norm.columns]
    ledger = norm[present].copy()
    if 'notice_date' in ledger.columns:
        ledger['available_at'] = pd.to_datetime(ledger['notice_date'], errors='coerce')
    else:
        ledger['available_at'] = pd.NaT
    ledger['source'] = 'eastmoney_RPT_SHAREBONUS_DET'
    ledger['action_type'] = 'distribution'
    ledger['tax_policy'] = 'gross_cn_individual_unverified'
    ledger['quality_status'] = 'public_warmup_partial_fields'
    ledger['promotion_approved'] = False
    path = OUT / 'distributions_warmup_2024_2026.parquet'
    ledger.to_parquet(path, index=False)
    # also raw wide
    norm.to_parquet(OUT / 'distributions_warmup_raw_wide.parquet', index=False)
    meta = {
        'dataset': 'corporate_actions_distributions_warmup',
        'fetch_time': NOW.isoformat(),
        'reports': reports,
        'rows': int(len(ledger)),
        'columns': list(ledger.columns),
        'path': str(path),
        'raw_dir': str(RAW),
        'promotion_approved': False,
        'schema_notes': [
            'Warm-up only — not yet reconciled to 1c85 unexplained_ex_reference',
            'available_at from NOTICE date when present; else null',
            'cash/share field mapping may need vendor-specific cleanup',
            'Does not close D3 accounting_gaps alone',
        ],
        'limitations': [
            'Coverage limited to Eastmoney RPT_SHAREBONUS_DET 2024Q1-2026Q3',
            'No split/merger events beyond bonus/transfer fields in this extract',
            'Must cross-check against 1c85 actions + panel unexplained_ex_reference',
        ],
    }
    (OUT/'manifest.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'done': True, 'rows': meta['rows']}, ensure_ascii=False))

if __name__ == '__main__':
    main()
