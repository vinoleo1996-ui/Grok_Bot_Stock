# SYSTEM_ARCH_V3 — frozen callables (Eng)

Companion to `SYSTEM_ARCH_V3_ZH.md`. Research-grade. Signatures match code as of 2026-10-11 ET.

| Import | Callable | One-liner |
|---|---|---|
| `quantlab.mandate_v2` | `load_mandate_v2(path=None) -> MandateV2` | Load Mandate JSON; gate-consistent `promotion_approved` |
| `quantlab.promotion_gate` | `overall_promotion_approved() -> bool` | Overall data/platform gate (ENG_PING ± override) |
| `quantlab.promotion_gate` | `dataset_accepted(key: str) -> bool` | Per-dataset acceptance from ENG_PING |
| `quantlab.promotion_gate` | `gate_status() -> dict` | Machine-readable gate snapshot |
| `quantlab.data.v2_readers` | `default_v2_roots() -> V2DataRoots` | Accepted default paths |
| `quantlab.data.v2_readers` | `load_merged_panel(instrument_id, *, roots=None, ...) -> MergedPanelView` | D0+extend one id |
| `quantlab.data.v2_readers` | `load_merged_calendar(*, roots=None) -> MergedCalendarView` | Trading calendar |
| `quantlab.data.v2_readers` | `load_sw_l1_members(...)` / `float_mktcap_lookup_for_session(...)` / `load_ep_research(...)` / `load_financials_pit(...)` / `load_dividends(...)` / `load_etf_510300(...)` | Typed dataset readers |
| `quantlab.universe.d1_masks` | `build_d1_masks_for_session(session, ...) -> D1MaskResult` | L0 funnel |
| `quantlab.platform.strategy_feed` | `trading_sessions(start, end=None, ...) -> list[date]` | Sessions |
| `quantlab.platform.strategy_feed` | `merged_close_panel(ids, start, end=None, *, chunk_size=None, dtype="float32", ...) -> DataFrame` | Wide close (memory knobs) |
| `quantlab.platform.strategy_feed` | `iter_merged_close_chunks(ids, start, end=None, *, chunk_size=300, dtype="float32")` | Stream columns |
| `quantlab.platform.strategy_feed` | `merged_daily_returns(ids, ..., close_panel=None)` | Returns; **pass close_panel** |
| `quantlab.platform.strategy_feed` | `biweekly_rebalance_sessions(...)` / `etf_510300_daily_returns(...)` | Mandate cadence / Beta ETF |
| `quantlab.platform.strategy_feed` | `d1_members_at(session, ...)` / `d1_members_at_chunked(session, ids, chunk_size=500)` | Per-session universe |
| `quantlab.platform.strategy_feed` | `describe_strategy_feed() -> dict` | Memory tips |
| `quantlab.beta.sleeve` | `VolTargetBetaSleeveProvider(mandate, ...).plan(session) -> BetaSleevePlan` | L1 sleeve weights + residual budget |
| `quantlab.beta.sleeve` | `PrototypeBetaSleeveProvider(...).plan(session)` | Non-vol-target prototype |
| `quantlab.factors.residual_factory` | `ResearchResidualAlphaFactorFactory` / `equal_weight_zscore_integrate(...)` | L3 neutralize + integrate |
| `quantlab.factors.v2_min_pipeline` | `run_v2_min_pipeline(session, universe_ids, float_mktcap, ...) -> V2MinPipelineResult` | Min momentum+EP; IC process-only |
| `quantlab.factors.p1_pipeline` | `run_p1_integrate_session(...)` | P1 research integrate |
| `quantlab.factors.ai_factory` | `gp_search(panels, label, config=None) -> SearchResult` | L1 GP skeleton; always non-promoted |
| `quantlab.factors.ai_factory` | `append_attempt(...)` / `walk_forward_ic(...)` | Ledger + fold IC stub |
| `quantlab.platform.execution` | `load_execution_panels(ids, start, end, ...) -> (ExecPanels, diag)` | Spot/ETF/CB panels + CA |
| `quantlab.platform.execution` | `run_weight_schedule(panels, schedule, *, config=None, futures=None, margin=None) -> dict` | Primary sim engine |
| `quantlab.platform.execution` | `reconcile_zero_cost(...)` / `cost_ladder(...)` / `capacity_curve(...)` | E1 helpers |
| `quantlab.platform.futures` | `FuturesLeg(panels, config=FuturesConfig())` | Multi-root futures book |
| `quantlab.platform.futures` | `load_futures_panels(roots, start, end, ...)` / `load_shibor` / `load_lpr` / `load_511880_returns` | Futures + rates loaders |
| `quantlab.platform.margin` | `MarginConfig(...)` | Financing account (opt-in) |
| `quantlab.portfolio.v2_rebalance` | `RebalanceScheduleV2(mandate)` | Cadence decisions |
| `quantlab.portfolio.v2_constructor` | `PortfolioConstructorV2` | Caps / turnover clip |
| ENG_PING | `output/d1/ENG_PING_PATHS.json` | Paths + acceptance + overall gate |

**Stubs / not frozen product APIs:** daily intel product pipeline (missing); `StubResidualAlphaFactorFactory`; `StubBetaSleeveProvider`; AI factory sealed-window run (forbidden until Leo); Strategy-owned paper runners (`v2_strategy_paper*`, `v2_multisleeve_book`) consume Eng but are not Eng contracts.

---

## PROPOSED / THIS_WEEK (AI-native Eng stubs)

Research-grade only. Signatures match stub modules as of 2026-10-11 ET. Not production-frozen until Data embedding corpus lands and Alpha wires explore config. Full narrative: `SYSTEM_ARCH_V3_AI_NATIVE_ZH.md`.

| Import | Callable | Status | One-liner |
|---|---|---|---|
| `quantlab.intel.messages` | `load_message_frame(*, start=None, end=None, instruments=None, categories=None, roots=None) -> DataFrame` | **THIS_WEEK stub** | Classified PIT message corpus; empty+TODO if path missing |
| `quantlab.intel.messages` | `assert_pit_available(row, decision_ts) -> None` | **THIS_WEEK stub** | Raise on look-ahead vs `available_at` |
| `quantlab.intel.messages` | `MessageRecord` (TypedDict) | **THIS_WEEK** | Message schema contract |
| `quantlab.intel.embeddings` | `load_embedding_panels(*, start, end=None, instruments=None, spec=None) -> dict[str, DataFrame]` | **THIS_WEEK stub** | `{emb_i: wide panel}`; empty if store absent |
| `quantlab.intel.embeddings` | `embedding_leaf_names(dim, prefix="emb_") -> tuple[str, ...]` | **THIS_WEEK** | Leaf names for GP panels merge |
| `quantlab.intel.embeddings` | `EmbeddingStoreSpec` (TypedDict) | **THIS_WEEK** | Store path/model/dim/PIT fields |
| `quantlab.factors.ai_factory.repr_bridge` | `panels_from_embedding_store(...) -> dict[str, DataFrame]` | **THIS_WEEK stub** | B2 bridge: store → GP panels |
| `quantlab.factors.ai_factory.repr_bridge` | `run_repr_stub(...) -> dict` | **THIS_WEEK stub** | Does **not** train; `NotImplementedError` or meta-only |
| `quantlab.factors.ai_factory.validate_gate` | `validate_candidate(*, engine, expr_str, window, universe, cost, sealed_requested=False, leo_seal_approved=False, ...) -> ValidateVerdict` | **THIS_WEEK stub** | Explore PASS / sealed default BLOCK; never auto-promote |
| `quantlab.factors.ai_factory.handoff` | `handoff_topk_to_scores(session, members, *, top_k_path=None, panels=None, ...) -> HandoffScorePanel` | **THIS_WEEK stub** | Top-K → cross-section scores for residual/Strategy |
| `quantlab.factors.ops` | `EMBEDDING_LEAF_PREFIX` / panels may include `emb_*` | **THIS_WEEK** | Backward compatible; unused leaves ignored |

**Consumers:** Alpha (mine/validate/handoff), Strategy (read `HandoffScorePanel.scores`), Data (ENG_PING keys `intel_message_corpus` / `embedding_store_daily`). Beta sleeve unchanged.

**Still stubs / not this-week product:** daily intel product scheduler; sealed LLM mining loop; real NN train; LGBM B3 full fit; auto `promotion_approved=True`.

---

## Skeleton one-click (2026-10-12)

| Import / CLI | Callable | One-liner |
|---|---|---|
| `quantlab.platform.weight_long_table` | `schema_handshake` / `validate_weight_path` / `write_weight_long_table` | Frozen weight long-table contract |
| `quantlab.cli trading-loop` | → `agents.trading_loop.run_stub` | Stub research loop |
| `quantlab.cli factor-evolve --smoke` | → `agents.factor_evolve.run_stub` | Stub → weight parquet |
| `quantlab.cli book-smoke` | → `portfolio.book_smoke` (default skip-run) | Book skeleton |
| `quantlab.cli skeleton-smoke` | → `v2_skeleton_smoke.run_skeleton_smoke` | All four light |
| `quantlab.cli live-dry-run` | → `v2_live_dryrun.run_live_dryrun` | G1–G5→weights→smoke dry-run |
| doc | `docs/v2/SKELETON_ONECLICK_ZH.md` | One-liners + schema |

