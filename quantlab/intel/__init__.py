"""Eng intel contracts: message corpus + embedding store + as_of guards (research-grade).

THIS_WEEK stubs for AI-native pipeline (消息 -> 嵌入 -> 挖因子).
See docs/v2/SYSTEM_ARCH_V3_AI_NATIVE_ZH.md and docs/v2/OPENSOURCE_ENG_ADOPTION_ZH.md.
promotion_approved always False.
"""
from quantlab.intel.asof_window import (
    as_of,
    as_of_window,
    assert_available_at_le_decision,
    coverage_gap,
    filter_frame_asof,
    in_window,
    session_to_decision_ts,
    withhold_live_only,
)
from quantlab.intel.debate_ledger import (
    DebateRoundResult,
    DebateTurn,
    DecisionEntry,
    JsonlDebateLedger,
    SettlementRecord,
    make_pending_decision,
)
from quantlab.intel.embeddings import (
    EMBEDDING_LEAF_PREFIX,
    EmbeddingStoreSpec,
    default_embedding_spec,
    embedding_leaf_names,
    load_embedding_panels,
)
from quantlab.intel.messages import (
    MessageRecord,
    assert_pit_available,
    default_message_corpus_path,
    load_message_frame,
    load_messages_for_session,
)

__all__ = [
    "EMBEDDING_LEAF_PREFIX",
    "DebateRoundResult",
    "DebateTurn",
    "DecisionEntry",
    "EmbeddingStoreSpec",
    "JsonlDebateLedger",
    "MessageRecord",
    "SettlementRecord",
    "as_of",
    "as_of_window",
    "assert_available_at_le_decision",
    "assert_pit_available",
    "coverage_gap",
    "default_embedding_spec",
    "default_message_corpus_path",
    "embedding_leaf_names",
    "filter_frame_asof",
    "in_window",
    "load_embedding_panels",
    "load_message_frame",
    "load_messages_for_session",
    "make_pending_decision",
    "session_to_decision_ts",
    "withhold_live_only",
]
