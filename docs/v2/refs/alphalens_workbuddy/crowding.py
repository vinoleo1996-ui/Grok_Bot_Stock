"""One ETF crowding policy for the board, strategy, allocation and replay.

Returns/excess are percentage points; positions are percentages. Absolute excess
guards prevent a small comparison pool from washing out an already crowded ETF.
"""
ENTRY_ACTIONS = frozenset(('建仓', '左侧试仓'))
DEFENSIVE_NAMES = frozenset(('银行', '煤炭', '电力', '公用事业', '红利', '红利低波'))

def _clip(value):
    return max(0.0, min(1.0, value))

def etf_crowding(rows):
    def ranks(key):
        vals=[r[key] for r in rows if r.get(key) is not None]
        return {r['secid']:((sum(v<r[key] for v in vals)+.5*sum(v==r[key] for v in vals))/len(vals)
                if vals and r.get(key) is not None else .5) for r in rows}
    r60,r120,r20=(ranks(k) for k in ('excess60','excess120','excess20'))
    result={}
    for r in rows:
        sid=r['secid'];pos=(r.get('pos120') or 0)/100
        bias=_clip((r.get('bias20') or 0)/12)
        vol=_clip(((r.get('vol_ratio') or 1)-.8)/1.4)
        raw=.32*pos+.26*r60[sid]+.14*r120[sid]+.12*r20[sid]+.10*bias+.06*vol
        partial=r.get('pos120_partial',False)
        if partial:raw=.7*raw+.3*.5
        structural=not partial and r.get('excess60') is not None and r['excess60']>=15 and pos>=.75
        if structural:raw=max(raw,.78)
        defensive=r.get('name') in DEFENSIVE_NAMES or sid=='1.512800'
        result[sid]={'crowd':round(_clip(raw),3),
                     'defensive_crowding':defensive and (raw>=.66 or structural),
                     'structural_crowding':structural,
                     'crowding_quality':'partial_history' if partial else 'benchmark_missing' if r.get('excess60') is None or r.get('excess120') is None else 'complete',
                     'crowding_policy':'etf-relative-excess-v1'}
    return result

def entry_weight(row):
    """Reject contradictory snapshots at both presentation and execution boundaries."""
    if row.get('action') not in ENTRY_ACTIONS or row.get('defensive_crowding') or row.get('crowding_quality') in ('partial_history','benchmark_missing'):
        return 0.0
    if row.get('crowd') is not None and row['crowd']>=.72:
        return 0.0
    return max(0.0,float((row.get('plan') or {}).get('position_pct') or 0))
