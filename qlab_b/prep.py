"""Memory/time-lean prepare: only materializes sessions inside the replay window.

Mirrors quantlab.backtest.engine.prepare exactly (same functions, same order) but
restricted to [start,end]. The retained session range equals the replay window, so
no in-window decision can see anything outside it; the ruler (panels, records,
rules, exposures, eligible, universe, bars, ledger) is identical to quantlab's.
Only quantlab's full-history prepare is avoided, because it retains all 3096
sessions' per-instrument rule/exposure objects and gets OOM-killed.
"""
from __future__ import annotations

from dataclasses import asdict

import pandas as pd

from quantlab.data import market
from quantlab.data.contracts import fingerprint, timestamp
from quantlab.data.market import asof_records, exposure_matrix, universe_at
from quantlab.backtest.ledger import InstrumentRules


def prepare_window(dataset, cfg, start, end):
    close, amount, turnover = market.panels_for_research(dataset)
    dates = close.index[(close.index >= pd.Timestamp(start)) & (close.index <= pd.Timestamp(end))]
    records, rules, exposures, eligible, close_records, bars = {}, {}, {}, {}, {}, {}
    for d in dates:
        morning = asof_records(dataset.instruments, timestamp(d) + pd.Timedelta(hours=9, minutes=25))
        records[d] = morning
        rules[d] = {}
        for c, row in morning.iterrows():
            try:
                rules[d][c] = InstrumentRules.from_record(row)
            except ValueError:
                pass
        exposures[d] = exposure_matrix(dataset, d, morning, list(morning.index),
                                       as_of=timestamp(d) + pd.Timedelta(hours=9, minutes=25))
        eligible[d], close_records[d] = universe_at(dataset, d, amount, cfg)
        bars[d] = {c: row.to_dict() for c, panel in dataset.panels.items()
                   if d in panel.index for _, row in panel.loc[[d]].iterrows()}
    return {"close": close, "amount": amount, "turnover": turnover,
            "version": dataset.version, "preparation_config": fingerprint(asdict(cfg)),
            "records": records, "rules": rules, "exposures": exposures,
            "eligible": eligible, "close_records": close_records, "bars": bars}
