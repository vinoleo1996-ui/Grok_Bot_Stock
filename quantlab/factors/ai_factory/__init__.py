"""L1 AI factor factory skeleton (plan-aligned). promotion_approved=False always.

THIS_WEEK AI-native stubs: repr_bridge, validate_gate, handoff
(see docs/v2/SYSTEM_ARCH_V3_AI_NATIVE_ZH.md).
"""
from quantlab.factors.ai_factory.evaluate import EvalResult, align_open_open_label, walk_forward_ic
from quantlab.factors.ai_factory.handoff import HandoffScorePanel, handoff_topk_to_scores
from quantlab.factors.ai_factory.pipeline_export import (
    FactorExportRecord,
    PipelineDryRunResult,
    dry_run_export,
    pipeline_stages,
)
from quantlab.factors.ai_factory.ledger import append_attempt, read_attempts
from quantlab.factors.ai_factory.repr_bridge import (
    ReprBridgeConfig,
    merge_panels_with_embeddings,
    panels_from_embedding_store,
    run_repr_stub,
)
from quantlab.factors.ai_factory.search import GPConfig, gp_search
from quantlab.factors.ai_factory.validate_gate import ValidateVerdict, validate_candidate

from quantlab.factors.ai_factory.asof_text_guard import (
    GuardResult,
    TextFeatureRow,
    as_of,
    as_of_window,
    assert_no_text_lookahead,
    coverage_gap,
    filter_text_features_asof,
)
from quantlab.factors.ai_factory.quantmind_loop import (
    CAPITAL_CNY_ALLOWED,
    Direction,
    LoopRunResult,
    run_quantmind_loop,
)
from quantlab.factors.ai_factory.structural_leaves import (
    EASYSTOCK_STRUCTURAL_LEAVES,
    build_easystock_panels,
    who_pays_for_leaf,
)

__all__ = [
    "EvalResult",
    "GPConfig",
    "HandoffScorePanel",
    "ReprBridgeConfig",
    "ValidateVerdict",
    "align_open_open_label",
    "append_attempt",
    "gp_search",
    "handoff_topk_to_scores",
    "merge_panels_with_embeddings",
    "panels_from_embedding_store",
    "read_attempts",
    "run_repr_stub",
    "validate_candidate",
    "walk_forward_ic",
    "GuardResult",
    "TextFeatureRow",
    "as_of",
    "as_of_window",
    "assert_no_text_lookahead",
    "coverage_gap",
    "filter_text_features_asof",
    "CAPITAL_CNY_ALLOWED",
    "Direction",
    "LoopRunResult",
    "run_quantmind_loop",
    "EASYSTOCK_STRUCTURAL_LEAVES",
    "build_easystock_panels",
    "who_pays_for_leaf",
]
