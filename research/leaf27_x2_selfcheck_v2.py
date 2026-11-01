#!/usr/bin/env python3
"""叶27 X2 selfcheck_v2：钉既有 alpha → 生成评价权重 → leaf_selfcheck_common.evaluate。

本票 ≠ 复跑 baseline_evac；≠ Book-Smoke；≠ X2 ACCEPT。
live=false；promotion_approved=false；禁自签 .ok；禁抬帽。
§3.3 / 叶18 同类：NAME_W=0.04 · MAX_NAMES=20 · REBAL_EVERY=5 · IND_CAP(HILIQ)=0.25 · BALLAST=510300.SH
硬排除 600519.SH / 002371.SZ；无单独 gate 列（alpha 已 limit_policy=exclude_hit_or_unknown）。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import resource
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# --- 硬钉（PRIMARY HILIQ × x2；baseline_evac 产物）---
PIN_ALPHA = ROOT / "output/ai_factory/leaf27_on_minus_id_idio_ivol/alpha_HILIQ_x2_20261025_224033.parquet"
PIN_META = ROOT / "output/ai_factory/leaf27_on_minus_id_idio_ivol/run_meta_HILIQ_x2_20261025_224033.json"
PIN_SUMMARY = ROOT / "output/ai_factory/leaf27_on_minus_id_idio_ivol/build_summary_20261025_224333.json"
PIN_ALPHA_SHA = "652b8a68b28871ddc1cbf623834650c23c79c8a81235fabc578ede71f17cf1b1"
PIN_META_SHA = "85c2dc7897c2796e36357042d8521e8b4b91beec8f2cd43bf18c31bdf48d4068"
PIN_SUMMARY_SHA = "80596bffb7de1296f6859f3e7bf1afa5c73ef2ec79a579bb365061cba8579cd6"

OUT_DIR = ROOT / "output/ai_factory/leaf27_on_minus_id_idio_ivol"
SELFCHECK_SUB = OUT_DIR / "_selfcheck"
REPORT_DIR = ROOT / "output/ai_factory/leaf_reports/leaf27_on_minus_id_idio_ivol"

BALLAST = "510300.SH"
HARD_EXCLUDE = frozenset({"600519.SH", "002371.SZ"})
NAME_W = 0.04
MAX_NAMES = 20
REBAL_EVERY = 5
IND_CAP = {"HILIQ": 0.25, "FULLA": 0.28}
RSS_SOFT_MB = 1500  # 软披露/软门；禁抬
FORBID_RESTORED = (
    "e107383f",
    "2be59acd",
    "a7d98ac9",
    "8e51de63",
    "3a6caa4f",
    "8bcd79dc",
    "725be3e0",
    "0f50daf7",  # baseline_evac CONSUMED → 归档 7e06a5b3；禁 RESTORED
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rss_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def assert_pins(alpha_path: Path, meta_path: Path, summary_path: Path) -> dict:
    """硬钉三件路径+全长 sha；不 MATCH 则 exit≠0。"""
    expect = {
        alpha_path.resolve(): PIN_ALPHA_SHA,
        meta_path.resolve(): PIN_META_SHA,
        summary_path.resolve(): PIN_SUMMARY_SHA,
    }
    # 默认路径必须等于钉盘
    if alpha_path.resolve() != PIN_ALPHA.resolve():
        raise SystemExit(f"FATAL alpha-path 偏离钉盘: {alpha_path} ≠ {PIN_ALPHA}")
    if meta_path.resolve() != PIN_META.resolve():
        raise SystemExit(f"FATAL meta-path 偏离钉盘: {meta_path} ≠ {PIN_META}")
    if summary_path.resolve() != PIN_SUMMARY.resolve():
        raise SystemExit(f"FATAL summary-path 偏离钉盘: {summary_path} ≠ {PIN_SUMMARY}")
    out = {}
    for p, exp in expect.items():
        if not p.is_file():
            raise SystemExit(f"FATAL 缺件: {p}")
        got = sha256_file(p)
        if got != exp:
            raise SystemExit(f"FATAL sha MISMATCH {p.name}: got={got} expect={exp}")
        out[p.name] = got
    return out


def build_eval_weights(alpha: pd.DataFrame, universe: str) -> pd.DataFrame:
    """§3.3：每 5 交易日按当日 base-α 重算；每名≤4%、≤20 名；行业帽；余额 510300；硬排除。

    无单独 gate 列：只从当日 alpha 表有的票里按 α 降序取（涨跌停已在 alpha 构建侧 exclude）。
    """
    if universe not in IND_CAP:
        raise SystemExit(f"FATAL universe 不支持: {universe}")
    cap = IND_CAP[universe]
    a = alpha.copy()
    a["date"] = pd.to_datetime(a["date"]).dt.normalize()
    a["instrument"] = a["instrument"].astype(str)
    a["alpha"] = pd.to_numeric(a["alpha"], errors="coerce")
    a["ind"] = a["ind"].astype(str)
    a = a[a["alpha"].notna() & ~a["instrument"].isin(HARD_EXCLUDE)]
    dates = sorted(a["date"].unique())
    weight_rows: list[tuple] = []
    last_weights: list[tuple] | None = None
    rebal_countdown = 0
    for d in dates:
        if rebal_countdown <= 0:
            day = a.loc[a["date"] == d, ["instrument", "alpha", "ind"]]
            day = day.sort_values("alpha", ascending=False, kind="mergesort")
            picked: list[str] = []
            ind_w: dict[str, float] = {}
            for _, row in day.iterrows():
                if len(picked) >= MAX_NAMES:
                    break
                ind = row["ind"]
                if ind_w.get(ind, 0.0) + NAME_W > cap + 1e-12:
                    continue
                picked.append(row["instrument"])
                ind_w[ind] = ind_w.get(ind, 0.0) + NAME_W
            day_w: list[tuple] = []
            if not picked:
                day_w.append((d, BALLAST, 1.0))
            else:
                for inst in picked:
                    day_w.append((d, inst, NAME_W))
                day_w.append((d, BALLAST, max(0.0, 1.0 - NAME_W * len(picked))))
            last_weights = day_w
            rebal_countdown = REBAL_EVERY
        rebal_countdown -= 1
        if last_weights is not None:
            for _, inst, w in last_weights:
                weight_rows.append((d, inst, w))
    weights = pd.DataFrame(weight_rows, columns=["date", "instrument", "target_weight"])
    if len(weights):
        s = weights.groupby("date")["target_weight"].transform("sum").replace(0, np.nan)
        weights["target_weight"] = weights["target_weight"] / s
    return weights


def dry_compile_payload() -> dict:
    return {
        "live": False,
        "promotion_approved": False,
        "ok_requested": False,
        "selfcheck_executed": False,
        "book_smoke": False,
        "x2_accept": False,
        "rss_soft_mb": RSS_SOFT_MB,
        "forbid_raise_rss": True,
        "universe": "HILIQ",
        "window": "x2",
        "pin_alpha": str(PIN_ALPHA),
        "pin_alpha_sha256": PIN_ALPHA_SHA,
        "pin_meta_sha256": PIN_META_SHA,
        "pin_summary_sha256": PIN_SUMMARY_SHA,
        "name_w": NAME_W,
        "max_names": MAX_NAMES,
        "rebal_every": REBAL_EVERY,
        "ind_cap_hiliq": IND_CAP["HILIQ"],
        "ballast": BALLAST,
        "hard_exclude": sorted(HARD_EXCLUDE),
        "forbid_restored_ok_sha8": list(FORBID_RESTORED),
        "baseline_evac_consumed_not_x2_accept": True,
        "note_zh": "dry-compile-only：不读大行情、不写权重实数、不调用 evaluate",
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="叶27 X2 selfcheck_v2（钉既有 alpha；DRAFT/签窗后实跑）")
    ap.add_argument("--universe", default="HILIQ", choices=["HILIQ"])
    ap.add_argument("--window", default="x2", choices=["x2"])
    ap.add_argument("--alpha-path", type=Path, default=PIN_ALPHA)
    ap.add_argument("--meta-path", type=Path, default=PIN_META)
    ap.add_argument("--summary-path", type=Path, default=PIN_SUMMARY)
    ap.add_argument(
        "--dry-compile-only",
        action="store_true",
        help="仅静态披露；不读大行情、不写权重、不 evaluate",
    )
    ap.add_argument(
        "--execute",
        action="store_true",
        help="正式跑：需外部新 .ok + 主令；本开关 alone 仍 live=false",
    )
    args = ap.parse_args(argv)

    if args.dry_compile_only:
        # 仅校验三件 sha（读文件字节做哈希，不解析 alpha、不写权重、不读行情）
        pins = assert_pins(args.alpha_path, args.meta_path, args.summary_path)
        payload = dry_compile_payload()
        payload["pin_sha_match"] = True
        payload["pin_sha_table"] = pins
        payload["rss_mb"] = round(rss_mb(), 2)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    if not args.execute:
        print(
            "FATAL: 缺 --execute。DRAFT/静态请用 --dry-compile-only；"
            "正式跑须新 .ok + 主排签窗后再加 --execute。",
            file=sys.stderr,
        )
        return 2

    pins = assert_pins(args.alpha_path, args.meta_path, args.summary_path)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    alpha = pd.read_parquet(args.alpha_path)
    need = {"date", "instrument", "alpha", "ind"}
    miss = need - set(alpha.columns)
    if miss:
        raise SystemExit(f"FATAL alpha 缺列: {sorted(miss)}")

    weights = build_eval_weights(alpha, args.universe)
    SELFCHECK_SUB.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    wp = SELFCHECK_SUB / f"eval_weights_{args.universe}_{args.window}_{stamp}.parquet"
    weights.to_parquet(wp, index=False)
    w_sha = sha256_file(wp)

    # 评价（读真价/收益）——仅 --execute 路径
    import research.leaf_selfcheck_common as LC

    result = LC.evaluate(wp)
    result_meta = {
        "leaf": "leaf27_on_minus_id_idio_ivol",
        "universe": args.universe,
        "window": args.window,
        "live": False,
        "promotion_approved": False,
        "book_smoke": False,
        "x2_accept": False,
        "selfcheck_executed": True,
        "stamp": stamp,
        "alpha_path": str(args.alpha_path),
        "alpha_sha256": pins[args.alpha_path.name],
        "meta_sha256": pins[args.meta_path.name],
        "summary_sha256": pins[args.summary_path.name],
        "eval_weights_path": str(wp),
        "eval_weights_sha256": w_sha,
        "eval_weights_dir_note": "output/ai_factory/leaf27_on_minus_id_idio_ivol/_selfcheck/",
        "n_weight_rows": int(len(weights)),
        "n_weight_days": int(weights["date"].nunique()) if len(weights) else 0,
        "name_w": NAME_W,
        "max_names": MAX_NAMES,
        "rebal_every": REBAL_EVERY,
        "ind_cap": IND_CAP[args.universe],
        "ballast": BALLAST,
        "hard_exclude": sorted(HARD_EXCLUDE),
        "gate_policy_zh": "无单独 gate 列；只从当日 alpha 表票按 α 降序取（alpha 已 exclude_hit_or_unknown）",
        "forbid_restored_ok_sha8": list(FORBID_RESTORED),
        "baseline_evac_consumed_not_x2_accept": True,
        "rss_mb_soft_limit": RSS_SOFT_MB,
        "rss_mb_peak_self": round(rss_mb(), 2),
        "evaluate": result,
    }
    out_json = REPORT_DIR / "selfcheck_v2.json"
    out_json.write_text(json.dumps(result_meta, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    # 旁路 meta 披露（不覆写钉盘 run_meta）
    side_meta = SELFCHECK_SUB / f"selfcheck_run_meta_{args.universe}_{args.window}_{stamp}.json"
    side_meta.write_text(json.dumps(result_meta, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    print(
        json.dumps(
            {
                "ok": True,
                "live": False,
                "selfcheck_v2": str(out_json),
                "eval_weights": str(wp),
                "side_meta": str(side_meta),
                "rss_mb": round(rss_mb(), 2),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
