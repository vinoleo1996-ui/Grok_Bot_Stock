"""easy-stock structural language → non-textbook leaves (连板 / 题材).

Computes panels from limit-up flags already used by L1b. Does NOT introduce
momentum/reversal/lowvol/EP/BP/turnover as main results.

New leaf names (also registered in ops.STRUCTURAL_LEAF_FEATURES / novelty):
  lu_height          — consecutive limit-up days (连板高度); equals streak
  mkt_max_height     — cross-section max 连板高度 that day (broadcast)
  lu_promote_rate    — among yesterday streak>=k, fraction still up today (k=1 default; broadcast)
  mkt_lu_breadth     — universe limit-up rate (题材宽度 proxy until theme map lands)
  theme_lu_density   — within-industry limit-up rate (needs industry panel; else NaN)

Money-from-whom notes live in ALPHA_DIRECTION_LIB_ZH.md / who_pays_zh on candidates.
promotion_approved always False.
"""
from __future__ import annotations

from typing import Mapping

import numpy as np
import pandas as pd

PROMOTION_APPROVED = False

EASYSTOCK_STRUCTURAL_LEAVES: tuple[str, ...] = (
    "lu_height",
    "mkt_max_height",
    "lu_promote_rate",
    "mkt_lu_breadth",
    "theme_lu_density",
)


def _broadcast_series(s: pd.Series, columns: pd.Index) -> pd.DataFrame:
    arr = np.repeat(s.to_numpy(dtype=np.float32)[:, None], len(columns), axis=1)
    return pd.DataFrame(arr, index=s.index, columns=columns, dtype="float32")


def consecutive_board_height(lu_streak: pd.DataFrame) -> pd.DataFrame:
    """连板高度: rename/copy of streak panel (float32)."""
    return lu_streak.astype("float32")


def market_max_height(lu_streak: pd.DataFrame, mask: pd.DataFrame | None = None) -> pd.DataFrame:
    """Market-day max consecutive-board height, broadcast to all names."""
    x = lu_streak.astype("float32")
    if mask is not None:
        x = x.where(mask)
    mx = x.max(axis=1)
    return _broadcast_series(mx, lu_streak.columns)


def promote_rate(
    lu_streak: pd.DataFrame,
    *,
    min_height: int = 1,
    mask: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """晋级率: P(streak_t >= h+1 | streak_{t-1} >= h), broadcast.

    Default h=1 → fraction of yesterday's limit-ups that continued today.
    """
    h = float(min_height)
    prev = lu_streak.shift(1)
    eligible = prev >= h
    promoted = (lu_streak >= (h + 1)) & eligible
    if mask is not None:
        eligible = eligible & mask.shift(1).fillna(False) & mask
        promoted = promoted & mask
    num = promoted.sum(axis=1).astype("float64")
    den = eligible.sum(axis=1).astype("float64").replace(0.0, np.nan)
    rate = (num / den).astype("float32")
    return _broadcast_series(rate, lu_streak.columns)


def market_lu_breadth(lu_flag: pd.DataFrame, mask: pd.DataFrame | None = None) -> pd.DataFrame:
    """题材宽度 proxy: share of universe hitting limit-up that day (broadcast)."""
    f = lu_flag.fillna(False).astype("float32")
    if mask is not None:
        f = f.where(mask)
        den = mask.astype("float32").sum(axis=1).replace(0.0, np.nan)
    else:
        den = f.notna().sum(axis=1).astype("float32").replace(0.0, np.nan)
    breadth = (f.sum(axis=1) / den).astype("float32")
    return _broadcast_series(breadth, lu_flag.columns)


def theme_lu_density(
    lu_flag: pd.DataFrame,
    industry: pd.DataFrame,
    mask: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Within-industry limit-up density (0..1). industry cell = category id/code.

    If industry is empty / all-NaN, returns all-NaN (Data gap — do not invent themes).
    """
    if industry is None or industry.shape != lu_flag.shape or industry.notna().sum().sum() == 0:
        return pd.DataFrame(
            np.nan, index=lu_flag.index, columns=lu_flag.columns, dtype="float32"
        )
    f = lu_flag.fillna(False).astype(bool)
    if mask is not None:
        f = f & mask.fillna(False).astype(bool)
    out = pd.DataFrame(
        np.nan, index=lu_flag.index, columns=lu_flag.columns, dtype="float32"
    )
    # Per day: group columns by industry label
    ind = industry
    for t in range(len(lu_flag.index)):
        labels = ind.iloc[t]
        hits = f.iloc[t]
        if mask is not None:
            ok = mask.iloc[t].fillna(False).astype(bool)
        else:
            ok = labels.notna()
        lab = labels.where(ok)
        if lab.notna().sum() < 5:
            continue
        # density per label
        grp_n = lab.groupby(lab).transform("count")
        grp_lu = hits.groupby(lab).transform("sum")
        dens = (grp_lu / grp_n.replace(0, np.nan)).astype("float32")
        out.iloc[t] = dens.reindex(lu_flag.columns).to_numpy()
    return out


def build_easystock_panels(
    *,
    lu_flag: pd.DataFrame,
    lu_streak: pd.DataFrame,
    mask: pd.DataFrame | None = None,
    industry: pd.DataFrame | None = None,
    promote_min_height: int = 1,
) -> dict[str, pd.DataFrame]:
    """Return dict of easy-stock structural panels ready for GP leaf dict."""
    panels: dict[str, pd.DataFrame] = {
        "lu_height": consecutive_board_height(lu_streak),
        "mkt_max_height": market_max_height(lu_streak, mask),
        "lu_promote_rate": promote_rate(
            lu_streak, min_height=promote_min_height, mask=mask
        ),
        "mkt_lu_breadth": market_lu_breadth(lu_flag, mask),
    }
    if industry is not None:
        panels["theme_lu_density"] = theme_lu_density(lu_flag, industry, mask)
    else:
        panels["theme_lu_density"] = pd.DataFrame(
            np.nan, index=lu_flag.index, columns=lu_flag.columns, dtype="float32"
        )
    return panels


def who_pays_for_leaf(leaf: str) -> str:
    """Short 钱从谁来 for direction / explain stage."""
    return {
        "lu_height": "接力失败的短线资金与被迫隔夜的T+1买家；连板越高越依赖情绪接力。",
        "mkt_max_height": "市场情绪总闸：高度退潮时接力盘撤出，指数β拥挤买方受损。",
        "lu_promote_rate": "晋级失败时昨日追板资金成为卖方；晋级成功则空头回补与FOMO买单。",
        "mkt_lu_breadth": "题材扩散时旁观资金被迫买入相关；退潮时一日游资金砸盘。",
        "theme_lu_density": "同题材拥挤买方在扩散期互抬；拥挤反转时同业一起出货。",
        "lu_streak": "同 lu_height。",
        "lu_count_5": "近期反复涨停吸引游资；开板后承接盘不足则砸给隔夜持仓。",
        "days_since_lu": "距涨停越远，事件溢价消退，早期追高者兑现。",
        "overnight_ret": "T+1 隔夜：集合竞价被动接盘者 vs 想卖出的隔夜仓。",
        "intraday_ret": "日内博弈：尾盘抢筹 vs 早盘兑现。",
        "etf_major_flow": "被动/宽基申赎冲击：造市商与套利桌把份额差转成指数成分买卖。",
        "etf_theme_flow": "主题ETF申赎：产品投资人用现金投票，成分股被动跟流。",
        "lockup_S_20": "解禁供给：原始股东潜在卖压，对手方是不知情或不计供给的买方。",
        "if_basis": "期指贴水：套保空头压迫基差，现货多头在收敛/升水时受损或受益。",
    }.get(leaf, "未标注钱从谁来 — 不得晋级主结果。")
