"""Strict coverage gate and the free-research module gate."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from quantlab.data.contracts import MarketDataset, coverage_input_fingerprint

REQUIRED = (
    "security_history",
    "raw_prices",
    "corporate_actions",
    "calendar",
    "benchmark",
    "opening_rules",
)


def research_assessment(dataset: MarketDataset, require_industry: bool = False) -> dict:
    reasons = []
    warnings = []
    price_ok = True
    for panel in dataset.panels.values():
        if "close" not in panel.columns or "amount" not in panel.columns:
            price_ok = False
            reasons.append("price_volume_fields_missing")
            break
        if panel["amount"].isna().all() or panel["close"].isna().all():
            price_ok = False
            reasons.append("price_volume_fields_missing")
            break
    sectors = dataset.instruments["sector"] if "sector" in dataset.instruments.columns else None
    industry_rows = getattr(dataset, "industry_records", None)
    industry_ok = industry_rows is not None and len(industry_rows) > 0
    if sectors is not None and not sectors.isin(["UNKNOWN"]).all() and industry_ok:
        industry_ok = True
    elif sectors is not None and sectors.isin(["UNKNOWN"]).all():
        industry_ok = False
    if require_industry and not industry_ok:
        reasons.append("industry_required")
    status = "research_ready" if price_ok and not reasons else "blocked_data"
    if not industry_ok:
        warnings.append("industry_disabled_unknown_exposure_capped")
    return {
        "status": status,
        "reasons": reasons,
        "warnings": warnings,
        "modules": {"price_volume": price_ok, "industry": bool(industry_ok)},
        "accounting_verified": False,
    }


def qualification(dataset: MarketDataset) -> dict:
    """Strict daily-research gate. A free sample without coverage files stays blocked."""
    reasons = []
    evidence = dataset.manifest.get("coverage_evidence") or {}
    root = getattr(dataset, "evidence_root", None)
    needed = (*REQUIRED, "industry_history")
    if dataset.manifest.get("source") != "vendor" or root is None or not evidence:
        return {"status": "blocked_data", "reasons": ["coverage_evidence_missing"], "promotion_approved": False}
    expected = coverage_input_fingerprint(dataset)
    for field in needed:
        ref = evidence.get(field)
        if not ref:
            reasons.append(f"coverage_artifact_invalid:{field}:missing")
            continue
        path = Path(root) / ref["verification_artifact"]
        if not path.is_file():
            reasons.append(f"coverage_artifact_invalid:{field}:missing_file")
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != ref.get("sha256"):
            reasons.append(f"coverage_artifact_invalid:{field}:sha256_mismatch")
            continue
        document = json.loads(path.read_text(encoding="utf-8"))
        if document.get("input_fingerprint") != expected:
            reasons.append(f"coverage_artifact_invalid:{field}:fingerprint_mismatch")
            continue
        measurements = document.get("measurements")
        if not isinstance(measurements, dict) or not measurements:
            reasons.append(f"coverage_artifact_invalid:{field}:measurements_missing")
            continue
        if measurements.get("unresolved_required_gaps", 0) not in (0, None):
            reasons.append(f"coverage_artifact_invalid:{field}:unresolved_gaps")
    status = "qualified_for_daily_research" if not reasons else "blocked_data"
    return {"status": status, "reasons": reasons, "promotion_approved": False}
