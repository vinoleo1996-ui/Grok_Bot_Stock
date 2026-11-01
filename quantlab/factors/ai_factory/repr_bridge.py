"""B2 representation-learning bridge (THIS_WEEK Eng stub).

Maps Data embedding store -> GP leaf panels. Does NOT train a network.
See docs/v2/SYSTEM_ARCH_V3_AI_NATIVE_ZH.md W3.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any, Mapping, Sequence

import pandas as pd

from quantlab.intel.embeddings import (
    EmbeddingStoreSpec,
    default_embedding_spec,
    load_embedding_panels,
)

PROMOTION_APPROVED = False


@dataclass
class ReprBridgeConfig:
    model_id: str = "stub_mlp_v0"
    dim: int = 16
    lookback: int = 20
    promotion_approved: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "promotion_approved", False)


def panels_from_embedding_store(
    *,
    start: date,
    end: date | None = None,
    instruments: Sequence[str] | None = None,
    spec: EmbeddingStoreSpec | None = None,
) -> dict[str, pd.DataFrame]:
    """Thin alias: embedding store -> panels dict suitable for gp_search merge."""
    return load_embedding_panels(start=start, end=end, instruments=instruments, spec=spec)


def merge_panels_with_embeddings(
    base: Mapping[str, pd.DataFrame],
    emb: Mapping[str, pd.DataFrame],
) -> dict[str, pd.DataFrame]:
    """Shallow merge; embedding keys win on collision."""
    out = dict(base)
    out.update(dict(emb))
    return out


def run_repr_stub(
    *,
    config: ReprBridgeConfig | None = None,
    panels: Mapping[str, pd.DataFrame] | None = None,
) -> dict[str, Any]:
    """Research stub: does not train. Raises NotImplementedError for real fit.

    Callers may catch and use panels_from_embedding_store for offline vectors.
    """
    cfg = config or ReprBridgeConfig()
    _ = panels
    meta = {
        "model_id": cfg.model_id,
        "dim": cfg.dim,
        "lookback": cfg.lookback,
        "promotion_approved": False,
        "todos": (
            "repr_train_pending_data_and_alpha_config",
            "embedding_store_daily_missing_or_empty",
        ),
        "spec": default_embedding_spec(),
    }
    raise NotImplementedError(
        "repr_train_pending_data_and_alpha_config:" + ",".join(meta["todos"])
    )
