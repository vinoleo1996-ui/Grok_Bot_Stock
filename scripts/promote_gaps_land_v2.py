#!/usr/bin/env python3
"""Land promote-gap artifacts (free-only). Coordinates with QuantLab Data paths; no overwrite of their financials_available_at."""
from __future__ import annotations
import hashlib, json, re
from datetime import datetime, time as dtime
from pathlib import Path
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd

ROOT = Path('/workspace/QuantLab')
TZ = ZoneInfo('America/New_York')
SH = ZoneInfo('Asia/Shanghai')
NOW = datetime.now(TZ)
OUT_CA = ROOT / 'data/v2/corporate_actions'
RAW = OUT_CA / 'raw_eastmoney'
OUT_FIN = ROOT / 'data/v2/financials_pit'
OUT_FIN.mkdir(parents=True, exist_ok=True)
OUT_CA.mkdir(parents=True, exist_ok=True)

def to_dt(s):
    return pd.to_datetime(s.astype(str), errors='coerce')

def to_instrument(code):
    if code is None or (isinstance(code, float) and np.isnan(code)):
        return None
    c = str(code).strip()
    if '.' in c:
        num, mkt = c.split('.', 1)
        mkt = mkt.lower(); num = num.zfill(6)
        if mkt in ('sh', 'ss'): return f'sh.{num}'
        if mkt == 'sz': return f'sz.{num}'
        if mkt == 'bj': return f'bj.{num}'
    c = c.zfill(6)
    if c.startswith(('5', '6', '9')): return f'sh.{c}'
    if c.startswith(('4', '8')): return f'bj.{c}'
    return f'sz.{c}'

# ---- CA normalize ----
rows, page_meta = [], []
for path in sorted(RAW.glob('*.json')):
    if path.name.endswith('.meta.json'):
        continue
    raw = path.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    meta_path = path.with_suffix('.meta.json')
    if meta_path.exists():
        m = json.loads(meta_path.read_text())
        if m.get('sha256') and m['sha256'] != sha:
            raise SystemExit(f'checksum_mismatch:{path}')
    payload = json.loads(raw)
    data = (payload.get('result') or {}).get('data') or []
    mo = re.match(r'(\d{4}-\d{2}-\d{2})_p(\d+)\.json', path.name)
    page_meta.append({
        'file': path.name,
        'report': mo.group(1) if mo else None,
        'page': int(mo.group(2)) if mo else None,
        'n': len(data), 'sha256': sha,
    })
    rows.extend(data)

df = pd.DataFrame(rows)
df['instrument_id'] = df['SECUCODE'].map(to_instrument) if 'SECUCODE' in df.columns else (
    df['SECURITY_CODE'].map(to_instrument) if 'SECURITY_CODE' in df.columns else None)

ledger = pd.DataFrame({
    'instrument_id': df['instrument_id'],
    'security_name': df['SECURITY_NAME_ABBR'] if 'SECURITY_NAME_ABBR' in df.columns else None,
    'report_date': to_dt(df['REPORT_DATE']) if 'REPORT_DATE' in df.columns else pd.NaT,
    'plan_notice_date': to_dt(df['PLAN_NOTICE_DATE']) if 'PLAN_NOTICE_DATE' in df.columns else pd.NaT,
    'notice_date': to_dt(df['NOTICE_DATE']) if 'NOTICE_DATE' in df.columns else pd.NaT,
    'record_date': to_dt(df['EQUITY_RECORD_DATE']) if 'EQUITY_RECORD_DATE' in df.columns else pd.NaT,
    'ex_date': to_dt(df['EX_DIVIDEND_DATE']) if 'EX_DIVIDEND_DATE' in df.columns else pd.NaT,
    'assign_progress': df['ASSIGN_PROGRESS'] if 'ASSIGN_PROGRESS' in df.columns else None,
    'impl_plan_profile': df['IMPL_PLAN_PROFILE'] if 'IMPL_PLAN_PROFILE' in df.columns else None,
    'pretax_bonus_rmb_per_10': pd.to_numeric(df.get('PRETAX_BONUS_RMB'), errors='coerce'),
    'bonus_ratio_per_10': pd.to_numeric(df.get('BONUS_RATIO'), errors='coerce'),
    'transfer_ratio_per_10': pd.to_numeric(df.get('IT_RATIO'), errors='coerce'),
})
ledger['cash_per_share'] = ledger['pretax_bonus_rmb_per_10'] / 10.0
ledger['share_ratio'] = (
    ledger['bonus_ratio_per_10'].fillna(0.0) + ledger['transfer_ratio_per_10'].fillna(0.0)
) / 10.0
base = ledger['notice_date'].fillna(ledger['plan_notice_date'])
ledger['available_at'] = [
    pd.Timestamp(datetime.combine(x.date(), dtime(18, 0), tzinfo=SH)) if pd.notna(x) else pd.NaT
    for x in base
]
ledger['pay_date'] = ledger['ex_date']
ledger['share_date'] = ledger['ex_date']
ledger['action_id'] = ledger['instrument_id'].astype(str) + ':' + ledger['ex_date'].dt.strftime('%Y-%m-%d').fillna('NA')
ledger['source'] = 'eastmoney_RPT_SHAREBONUS_DET'
ledger['revision'] = hashlib.sha256(('|'.join(p['sha256'] for p in page_meta)).encode()).hexdigest()[:16]
ledger['quality_status'] = 'public_warmup_partial_fields'
ledger['tax_policy'] = 'gross_cn_individual_unverified'
ledger['action_type'] = 'distribution'
ledger['promotion_approved'] = False
ledger['availability_basis'] = 'notice_date_1800_AsiaShanghai_or_plan_notice_proxy'

cash = ledger['cash_per_share'].fillna(0.0).astype(float)
shr = ledger['share_ratio'].fillna(0.0).astype(float)
keep = ledger['instrument_id'].notna() & (ledger['ex_date'].notna() | (cash != 0.0) | (shr != 0.0))
ledger_f = ledger.loc[keep].copy()
path_led = OUT_CA / 'distributions_warmup_2024_2026.parquet'
ledger_f.to_parquet(path_led, index=False)
df.to_parquet(OUT_CA / 'distributions_warmup_raw_wide.parquet', index=False)

a1 = pd.read_parquet(ROOT / 'data/local_market/1c85fd9aceaa03c3c4863bec/actions.parquet')
a1_ex = to_dt(a1['ex_date'])
a1_id = a1['instrument_id'].astype(str)
win = a1_ex >= pd.Timestamp('2024-01-01')
a1w_ex = a1_ex[win]; a1w_id = a1_id[win]
em = ledger_f.dropna(subset=['ex_date'])
keys1 = set(zip(a1w_id, a1w_ex.dt.strftime('%Y-%m-%d')))
keysem = set(zip(em['instrument_id'].astype(str), em['ex_date'].dt.strftime('%Y-%m-%d')))
both, only_em, only_1c85 = keysem & keys1, keysem - keys1, keys1 - keysem

m = json.loads((ROOT / 'data/local_market/1c85fd9aceaa03c3c4863bec/manifest.json').read_text())
gaps = m.get('accounting_gaps') or []
gap_reasons = pd.Series([g.get('reason') for g in gaps]).value_counts().to_dict()
cov = json.loads((ROOT / 'data/local_market/1c85fd9aceaa03c3c4863bec/coverage_report.json').read_text())

ca_manifest = {
    'dataset': 'corporate_actions_distributions_warmup',
    'owner': 'QuantLab Data (primary); executor completed normalize from Data raw pages',
    'fetch_time': NOW.isoformat(),
    'promotion_approved': False,
    'raw_pages': len(page_meta),
    'raw_rows': len(rows),
    'ledger_rows': int(len(ledger_f)),
    'n_instruments': int(ledger_f['instrument_id'].nunique()),
    'path': str(path_led),
    'raw_dir': str(RAW),
    'reports_present': sorted({p['report'] for p in page_meta if p['report']}),
    'reconcile_vs_1c85_ex_date_from_2024': {
        '1c85_window_actions': int(win.sum()),
        'em_with_ex_date': int(em['ex_date'].notna().sum()),
        'intersection_keys': len(both),
        'only_eastmoney': len(only_em),
        'only_1c85': len(only_1c85),
    },
    '1c85_baseline': {
        'actions': cov.get('actions'),
        'actions_coverage': m.get('actions_coverage'),
        'unexplained_ex_reference_rows': cov.get('unexplained_ex_reference_rows'),
        'accounting_gaps': len(gaps),
        'accounting_gap_reasons': gap_reasons,
        'data_gaps_delist_etc': len(m.get('data_gaps') or []),
    },
    'field_notes': [
        'PRETAX_BONUS_RMB = 每10股派息 → cash_per_share=/10',
        'BONUS_RATIO+IT_RATIO = 每10股送/转 → share_ratio=/10',
        'pay_date/share_date proxied to ex_date',
        'available_at = NOTICE_DATE@18:00 Asia/Shanghai (else PLAN_NOTICE_DATE)',
    ],
    'free_tier_ceilings': [
        'Eastmoney RPT_SHAREBONUS_DET — rate-limit/IP ban risk; pageSize=500',
        'CNInfo bulk needs token; akshare JS token fragile',
        'BaoStock dividends blocked (10002007 / prior blacklist 10001011)',
        'Warm-up 2024Q1–2026Q3 only; does NOT close unexplained_ex_reference alone',
        'Leo free-only: no Tushare/Wind',
    ],
}
(OUT_CA / 'manifest.json').write_text(json.dumps(ca_manifest, ensure_ascii=False, indent=2) + '\n')
print('CA', ca_manifest['ledger_rows'], 'intersect', len(both), 'only_em', len(only_em), 'only_1c85', len(only_1c85))

# ---- Baostock PIT ----
metric_map = {
    'profit': {
        'roeAvg': 'roe', 'npMargin': 'np_margin', 'gpMargin': 'gross_margin',
        'netProfit': 'net_profit', 'epsTTM': 'eps_ttm', 'MBRevenue': 'revenue',
        'totalShare': 'total_share', 'liqaShare': 'float_share',
    },
    'growth': {
        'YOYEquity': 'yoy_equity', 'YOYAsset': 'yoy_asset', 'YOYNI': 'yoy_ni',
        'YOYEPSBasic': 'yoy_eps_basic', 'YOYPNI': 'yoy_pni',
    },
    'cash_flow': {
        'CAToAsset': 'ca_to_asset', 'NCAToAsset': 'nca_to_asset',
        'tangibleAssetToAsset': 'tangible_asset_to_asset', 'ebitToInterest': 'ebit_to_interest',
        'CFOToOR': 'cfo_to_or', 'CFOToNP': 'ocf_to_profit', 'CFOToGr': 'cfo_to_gr',
    },
}
coverage = {}
frames = []
for label, base in [('baostock_fin', Path('/workspace/baostock_fin')), ('ql_baostock', ROOT / 'data/baostock')]:
    for table in ('profit', 'growth', 'cash_flow'):
        d = base / table
        n = len(list(d.glob('*.parquet'))) if d.is_dir() else 0
        coverage[f'{label}/{table}'] = n

for table in ('profit', 'growth', 'cash_flow'):
    prefer = Path('/workspace/baostock_fin') / table
    fallback = ROOT / 'data/baostock' / table
    d = prefer if coverage.get(f'baostock_fin/{table}', 0) >= coverage.get(f'ql_baostock/{table}', 0) else fallback
    label = 'baostock_fin' if d == prefer else 'ql_baostock'
    if not d.is_dir():
        continue
    for fp in d.glob('*.parquet'):
        try:
            raw = pd.read_parquet(fp)
        except Exception:
            continue
        if raw.empty or 'pubDate' not in raw.columns:
            continue
        code = raw['code'].iloc[0] if 'code' in raw.columns else fp.stem
        for src_col, metric in metric_map[table].items():
            if src_col not in raw.columns:
                continue
            sub = raw[['pubDate', 'statDate', src_col]].copy()
            sub.columns = ['announced_on', 'report_period', 'value']
            sub['instrument_id'] = code
            sub['metric'] = metric
            sub['source'] = f'baostock_{table}'
            sub['seed_path'] = label
            frames.append(sub)

bs = pd.concat(frames, ignore_index=True)
bs['announced_on'] = to_dt(bs['announced_on'])
bs['report_period'] = to_dt(bs['report_period'])
bs['value'] = pd.to_numeric(bs['value'], errors='coerce')
bs = bs.dropna(subset=['instrument_id', 'metric', 'announced_on'])
bs['available_at'] = [
    pd.Timestamp(datetime.combine(x.date(), dtime(18, 0), tzinfo=SH)) if pd.notna(x) else pd.NaT
    for x in bs['announced_on']
]
bs['quality_status'] = 'baostock_pubDate_proxy_single_revision_no_restatement_chain'
bs['available_at_policy'] = 'pubDate_1800_AsiaShanghai_research_proxy'
bs['revision'] = 'baostock_seed_' + NOW.strftime('%Y%m%d')
bs['promotion_approved'] = False
bs = bs.sort_values(['instrument_id', 'metric', 'report_period', 'announced_on'])
latest = bs.drop_duplicates(['instrument_id', 'metric', 'report_period'], keep='last')
out_full = OUT_FIN / 'baostock_financials_pit_prototype.parquet'
out_lat = OUT_FIN / 'baostock_financials_pit_latest_per_key.parquet'
bs.to_parquet(out_full, index=False)
latest.to_parquet(out_lat, index=False)
bs_meta = {
    'dataset': 'baostock_financials_pit_prototype',
    'fetch_time': NOW.isoformat(),
    'promotion_approved': False,
    'owner_note': 'Complements Data financials_available_at.parquet; does not overwrite',
    'row_counts': {
        'full': int(len(bs)), 'latest_per_key': int(len(latest)),
        'n_instruments': int(bs['instrument_id'].nunique()),
        'n_metrics': int(bs['metric'].nunique()),
    },
    'seed_file_counts': coverage,
    'metrics': sorted(bs['metric'].unique().tolist()),
    'available_at_rule': 'available_at = pubDate @ 18:00 Asia/Shanghai',
    'restatement_policy': {
        'baostock': 'One record per period — NO correction history',
        'promotion': 'FORBIDDEN until as-filed value ledger exists',
    },
    'free_tier_ceilings': [
        'BaoStock login failing: 10002007; prior BAN blacklist 10001011 (2026-10-08)',
        'Cannot expand seeds live until unban/network fixed',
        f"seeds baostock_fin profit={coverage.get('baostock_fin/profit')} growth={coverage.get('baostock_fin/growth')} cash_flow={coverage.get('baostock_fin/cash_flow')}",
        'Universe ~6000 → ~15–17% profit name coverage',
        'Leo free-only: no Tushare/Wind',
    ],
    'paths': {'full': str(out_full), 'latest': str(out_lat)},
}
(OUT_FIN / 'baostock_pit_manifest.json').write_text(json.dumps(bs_meta, ensure_ascii=False, indent=2) + '\n')
print('BS', bs_meta['row_counts'])

plan = f'''# Corporate Actions / Ex-Rights Gap Closure Plan (free-only)

> Generated {NOW.isoformat()} · `promotion_approved=false`  
> Owner: **QuantLab Data** (primary). Executor landed warmup normalize + this plan.

## Baseline on box (no Mac CopyToBox)

| Asset | Path | Notes |
|---|---|---|
| 1c85 actions ledger | `data/local_market/1c85…/actions.parquet` | **36442** rows; available_at filled |
| accounting_gaps | manifest | **{len(gaps)}** mostly `unexplained_ex_reference` |
| unexplained_ex_reference_rows | coverage_report | **{cov.get('unexplained_ex_reference_rows')}** |
| actions_coverage | manifest | `{m.get('actions_coverage')}` — blocks D3 |
| FR120 actions | `free_research_120/.../actions.parquet` | 1069; baostock_dividend; cohort-only |
| Mac `corporate_actions/` raw | **NOT on box** | Not D0-migrated |

## Free fetch landed

| Item | Path | Status |
|---|---|---|
| EM RPT_SHAREBONUS_DET raw | `data/v2/corporate_actions/raw_eastmoney/` | {len(page_meta)} pages (Data Agent) |
| Normalized warmup ledger | `distributions_warmup_2024_2026.parquet` | **{len(ledger_f)}** rows / {int(ledger_f['instrument_id'].nunique())} names |
| Manifest | `manifest.json` | reconcile included |

Reconcile ex_date keys (≥2024-01-01): intersect={len(both)}, only_EM={len(only_em)}, only_1c85={len(only_1c85)}.

## Closure sequence (D3)

1. Keep **1c85 actions** as primary ledger (2014+); do not replace with EM-only.
2. Backfill EM → full history via `scripts/collect_corporate_actions.py` (free, rate-limited).
3. Match panel `unexplained_ex_reference` to cash/share/split events (±1 session); classify residual.
4. Rebuild factors after event-complete; zero unexplained on promote universe.
5. Gate: `actions_coverage=complete` AND unexplained=0.

## Free-tier ceilings (hard)

- No Tushare/Wind (Leo).
- BaoStock dividends: login `10002007`; prior blacklist `10001011`.
- Eastmoney public API: usable, throttle risk, no SLA.
- CNInfo: fragile JS token path; expensive at 6k names.
- D3 promote may stay blocked on free path until exhaustive public reconcile OR paid feed.

## Non-goals

- Do not invent entitlements to zero unexplained gaps.
- Do not treat 2024–2026 EM warmup as full-history complete.
'''
(OUT_CA / 'GAP_CLOSURE_PLAN.md').write_text(plan)

pol = OUT_FIN / 'AVAILABLE_AT_RESTATEMENT_POLICY.md'
extra = f'''

---

## Baostock seed prototype (added same day, free-only)

- Paths: `baostock_financials_pit_prototype.parquet`, `baostock_financials_pit_latest_per_key.parquet`, `baostock_pit_manifest.json`
- Rule: `available_at = pubDate @ 18:00 Asia/Shanghai`
- Does **not** overwrite `financials_available_at.parquet` (1c85 announced_on proxy from QuantLab Data)
- Live BaoStock expand: **blocked** (network 10002007 / prior blacklist 10001011)
- Seed rows: {len(bs)} / instruments: {int(bs['instrument_id'].nunique())} — research only
'''
txt = pol.read_text() if pol.exists() else ''
if 'Baostock seed prototype' not in txt:
    pol.write_text(txt + extra)
print('DONE')
