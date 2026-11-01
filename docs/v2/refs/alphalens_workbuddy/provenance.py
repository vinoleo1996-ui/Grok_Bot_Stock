"""Bind a replay to public strategy source, without reading configuration secrets."""
import hashlib
import json
from pathlib import Path
from .execution import VERSION

ROOT = Path(__file__).resolve().parents[2]
SOURCE_FILES = (
    'app/market.py', 'app/quant/indicators.py', 'app/quant/engine.py',
    'app/quant/crowding.py', 'app/quant/allocation.py', 'app/quant/exits.py',
    'app/quant/execution.py', 'app/quant/backtest2.py', 'app/quant/provenance.py',
    'app/runtime/service.py',
    'app/dataflows/hub.py', 'app/dataflows/etf_flow.py', 'app/api/routes.py',
    'app/runtime/research.py',
)


def strategy_manifest():
    files = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
             for name in SOURCE_FILES}
    payload = {'strategy_version': VERSION, 'files': files}
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    return {**payload, 'sha256': digest}


INITIAL_PROVENANCE = strategy_manifest()


def assert_current_code():
    if strategy_manifest()['sha256'] != INITIAL_PROVENANCE['sha256']:
        raise RuntimeError('strategy_code_changed_restart_required')
    baseline = ROOT / f'reports/strategy-manifest-{VERSION}.json'
    if baseline.exists() and json.loads(baseline.read_text())['sha256'] != INITIAL_PROVENANCE['sha256']:
        raise RuntimeError('strategy_version_reused_with_different_code: bump VERSION before validation')
    return INITIAL_PROVENANCE
