"""V2 universe / tradability mask contracts (Phase 0 + prototypes)."""
from quantlab.universe.mask import (
    MASK_NAMES,
    PrototypeUniverseMaskProvider,
    StubUniverseMaskProvider,
    TradabilityMaskRow,
    UniverseMaskProvider,
    UniverseMembership,
    empty_membership,
)

__all__ = [
    "MASK_NAMES",
    "TradabilityMaskRow",
    "UniverseMembership",
    "UniverseMaskProvider",
    "StubUniverseMaskProvider",
    "PrototypeUniverseMaskProvider",
    "empty_membership",
]

# D1 executable scaffold (see quantlab.universe.d1_masks)
from quantlab.universe.d1_masks import (
    D1MaskConfig,
    D1MaskResult,
    MEDIAN_AMOUNT_20D_FIELD,
    build_d1_masks_for_session,
)

__all__ += [
    "D1MaskConfig",
    "D1MaskResult",
    "MEDIAN_AMOUNT_20D_FIELD",
    "build_d1_masks_for_session",
]
