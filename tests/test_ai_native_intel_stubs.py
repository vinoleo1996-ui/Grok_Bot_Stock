"""Smoke for THIS_WEEK AI-native Eng stubs (research-grade)."""
from __future__ import annotations

from datetime import date

from quantlab.factors.ai_factory import handoff_topk_to_scores, validate_candidate
from quantlab.factors.ops import EMBEDDING_LEAF_PREFIX
from quantlab.intel import embedding_leaf_names, load_embedding_panels, load_message_frame


def test_embedding_prefix_and_empty_store():
    assert EMBEDDING_LEAF_PREFIX == "emb_"
    assert embedding_leaf_names(2) == ("emb_0", "emb_1")
    assert load_embedding_panels(start=date(2024, 1, 1)) == {}


def test_message_frame_research_flag():
    df = load_message_frame(start=date(2024, 1, 1), end=date(2024, 1, 7))
    assert df.attrs.get("promotion_approved") is False


def test_validate_gate_blocks_seal_and_smallcap():
    ok = validate_candidate(
        engine="gp",
        expr_str="x",
        window="explore",
        universe="midlarge_top1500",
        cost=0.0025,
    )
    assert ok.status in {"PASS_EXPLORE", "BLOCK_NO_LEDGER"}
    assert ok.promotion_approved is False
    sealed = validate_candidate(
        engine="gp",
        expr_str="x",
        window="explore",
        universe="midlarge_top1500",
        cost=0.0025,
        sealed_requested=True,
        leo_seal_approved=False,
    )
    assert sealed.status == "BLOCK_SEALED"
    sc = validate_candidate(
        engine="gp",
        expr_str="x",
        window="explore",
        universe="smallcap_main",
        cost=0.0025,
    )
    assert sc.status == "BLOCK_UNIVERSE"


def test_handoff_missing_panels_safe():
    h = handoff_topk_to_scores(date(2024, 6, 3), ["000001.SZ"], panels=None)
    assert h.promotion_approved is False
    assert h.data_ready is False
    assert h.scores == {}
