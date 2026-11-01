#!/usr/bin/env python3
"""叶31 Amihud Impact Slow X2 selfcheck_v1：钉既有冻结 alpha → 生成评价权重 → leaf_selfcheck_common.evaluate。

本票 ≠ 复跑 leaf31 alpha 构建（08f37fd2 UNCHANGED）；≠ Book-Smoke；≠ X2 ACCEPT；≠升纸面。
live=false；promotion_approved=false；禁自签 .ok；禁抬帽。
§3.3 / 叶18/25/27/30 同类：NAME_W=0.04 · MAX_NAMES=20 · REBAL_EVERY=5 · IND_CAP(HILIQ)=0.25 · BALLAST=510300.SH
硬排除 600519.SH / 002371.SZ；无单独 gate 列（按当日 alpha 表 α 降序）。
PIN_GAP：IC/ICIR/WF 由本票 evaluate 补齐；Alpha 闸 a476567d 仅 ACCEPT 构建过程（收益过程 ABSENT）。
机制：g1g5_ashare_amihud_impact_slow_v1；构建侧 Amihud W/rebal=20/20；本票只钉 alpha 做组合闸。
Gate 口径：leaf_selfcheck_common.evaluate → decay KEEP/DOWNGRADE + portfolio A/B/current。
派生自 leaf30_crr_x2_selfcheck_v1.py（797724d4）；勿盲抄路径。
CLI 禁 --arch-ok-path（未实现；流程门=外挂新 .ok+主窗，对齐叶25/30 P0）。
0087c928 另队：本脚本不读该路径。
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

# --- 硬钉（PRIMARY HILIQ × x2；叶31 Amihud Impact Slow alpha CONSUMED 产物）---
PIN_ALPHA = (
    ROOT
    / "output/ai_factory/_leaf31_amihud/20261027_024204/alpha_HILIQ_x2_20261027_024422.parquet"
)
PIN_META = ROOT / "output/ai_factory/_leaf31_amihud/20261027_024204/run_meta.json"
PIN_OVERLAP = (
    ROOT / "output/ai_factory/_leaf31_amihud/20261027_024204/overlap_vs_leaf19_25_27_30.json"
)
PIN_ALPHA_SHA = "d4ceb78b1d4b7c5516149a74bad87141083695ac6c4b7be43e3fa9a64c4452ce"
PIN_META_SHA = "696ab1cc25eed077cf7171b4461e8e6946677901c3fbfaf68be5cd55c4d9ab12"
PIN_OVERLAP_SHA = "8396f2111411dd0f9040d0215369394e83e646adca2dac15072b1003289df75b"
BUILD_SCRIPT_SHA8 = "08f37fd2"  # research/leaf31_amihud_impact_slow_alpha_build.py UNCHANGED
ARCH_CONSUME_SHA8 = "7bd6f33a"
ALPHA_GATE_SHA8 = "a476567d"  # ACCEPT 仅构建过程；IC/ICIR/WF ABSENT
AI_RUN_RECEIPT_SHA8 = "49d6641c"
MECHANISM = "g1g5_ashare_amihud_impact_slow_v1"

OUT_DIR = ROOT / "output/ai_factory/_leaf31_amihud/20261027_024204"
SELFCHECK_SUB = OUT_DIR / "_selfcheck"
REPORT_DIR = ROOT / "output/ai_factory/leaf_reports/leaf31_amihud"
SW_L1_PATH = ROOT / "data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet"

BALLAST = "510300.SH"
HARD_EXCLUDE = frozenset({"600519.SH", "002371.SZ"})
NAME_W = 0.04
MAX_NAMES = 20
REBAL_EVERY = 5
IND_CAP = {"HILIQ": 0.25, "FULLA": 0.28}
RSS_SOFT_MB = 1500  # 软/硬同钉；禁抬
RSS_HARD_MB = 1500
PEAK_PROOF_REQUIRED = True
SAMPLER_PREFIX = "/tmp/quantlab_leaf31_x2_selfcheck_"
PROPOSED_OK = (
    "output/ai_factory/ARCH_RUN_AUTH_LEAF31_AMIHUD_IMPACT_SLOW_X2_SELFCHECK_V1_HILIQ_X2.ok"
)
# 叶31 build CONSUMED + 叶30/既有 forbid；至少含 fdbaa512+aa25e989+7e239487+5af20222+5ae077fa
FORBID_RESTORED = (
    "fdbaa512",  # 叶31 X2 build CONSUMED；禁 RESTORED
    "aa25e989",  # 叶30 selfcheck CONSUMED
    "7e239487",  # 叶30 R3 peakcut CONSUMED
    "5af20222",  # 叶30 R2 VOID
    "5ae077fa",  # 叶30 R1 VOID
    "3c297052",
    "e107383f",
    "2be59acd",
    "a7d98ac9",
    "8e51de63",
    "3a6caa4f",
    "8bcd79dc",
    "725be3e0",
    "0f50daf7",
    "3c19dd7d",
    "1c32ab1e",
    "6054b3bf",
    "6de02e74",
)
PIN_GAP_FIELDS = ("ic", "icir", "walk_forward")
PIN_GAP_OVERALL = "ABSENT_UNTIL_SELFCHECK"
# 0087c928 另队：文档声明不夹带；本脚本不读该路径
LEAF30_KEEP_REPAIR_SHA8_SEPARATE = "0087c928"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rss_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def check_rss_hard(label: str) -> float:
    """软/硬同钉 1500；破则 ABORT（禁抬帽）。peak_proof = ru_maxrss。"""
    pk = rss_mb()
    if pk >= RSS_HARD_MB:
        raise SystemExit(
            f"STOP: RSS hard breached label={label} peak_mb={pk:.2f} >= hard={RSS_HARD_MB}; "
            "禁抬帽；停+上报"
        )
    return pk


def assert_pins(alpha_path: Path, meta_path: Path) -> dict:
    """硬钉 alpha+meta+overlap 路径+全长 sha；不 MATCH 则 exit≠0。"""
    if alpha_path.resolve() != PIN_ALPHA.resolve():
        raise SystemExit(f"FATAL alpha-path 偏离钉盘: {alpha_path} ≠ {PIN_ALPHA}")
    if meta_path.resolve() != PIN_META.resolve():
        raise SystemExit(f"FATAL meta-path 偏离钉盘: {meta_path} ≠ {PIN_META}")
    out = {}
    for p, exp in (
        (alpha_path.resolve(), PIN_ALPHA_SHA),
        (meta_path.resolve(), PIN_META_SHA),
        (PIN_OVERLAP.resolve(), PIN_OVERLAP_SHA),
    ):
        if not p.is_file():
            raise SystemExit(f"FATAL 缺件: {p}")
        got = sha256_file(p)
        if got != exp:
            raise SystemExit(f"FATAL sha MISMATCH {p.name}: got={got} expect={exp}")
        out[p.name] = got
    # 构建脚本 UNCHANGED
    build = ROOT / "research/leaf31_amihud_impact_slow_alpha_build.py"
    bsha = sha256_file(build)
    if not bsha.startswith(BUILD_SCRIPT_SHA8):
        raise SystemExit(f"FATAL build script sha drift: {bsha[:8]} ≠ {BUILD_SCRIPT_SHA8}")
    out["build_script_sha256"] = bsha
    return out


def _normalize_alpha(alpha: pd.DataFrame) -> pd.DataFrame:
    """叶31 schema → selfcheck 通用列（date/instrument/alpha）。"""
    a = alpha.copy()
    colmap = {}
    if "trade_date" in a.columns and "date" not in a.columns:
        colmap["trade_date"] = "date"
    if "ts_code" in a.columns and "instrument" not in a.columns:
        colmap["ts_code"] = "instrument"
    if colmap:
        a = a.rename(columns=colmap)
    need = {"date", "instrument", "alpha"}
    miss = need - set(a.columns)
    if miss:
        raise SystemExit(f"FATAL alpha 缺列: {sorted(miss)}")
    raw_date = a["date"]
    # 叶31 trade_date 为 ISO YYYY-MM-DD；兼容 YYYYMMDD / Timestamp
    d1 = pd.to_datetime(raw_date.astype(str), format="%Y%m%d", errors="coerce")
    if d1.isna().mean() > 0.5:
        d1 = pd.to_datetime(raw_date, errors="coerce")
    a["date"] = d1.dt.normalize()
    if a["date"].isna().any():
        raise SystemExit("FATAL alpha date 无法解析")
    a["instrument"] = a["instrument"].astype(str)
    a["alpha"] = pd.to_numeric(a["alpha"], errors="coerce")
    return a


def _load_sw_bundle():
    """加载 SW L1 + 交易日历（仅 --execute）。"""
    import research.sw_members_asof as sw

    cal = sw.load_trade_cal(ROOT)
    sw_df = sw.prep_sw(sw.load_sw_l1(ROOT, SW_L1_PATH))
    return sw, sw_df, cal


def _ind_for_day(sw_mod, sw_df, cal, codes: list[str], d) -> dict[str, str]:
    """单日 asof SW L1；失败则空 dict（调用方填 UNK）。"""
    if not codes:
        return {}
    keys = pd.DataFrame({"instrument": codes, "session": pd.Timestamp(d)})
    try:
        ser = sw_mod.sw_l1_asof_with_gap_carry(
            sw_df, keys, code_col="instrument", sess_col="session", cal=cal, on_overlap="count"
        )
    except Exception:  # noqa: BLE001
        return {}
    out: dict[str, str] = {}
    if isinstance(ser, pd.Series):
        for inst, val in zip(keys["instrument"], ser):
            if val is not None and (not (isinstance(val, float) and np.isnan(val))) and str(val) not in ("", "None", "nan"):
                out[str(inst)] = str(val)
    return out


def build_eval_weights(alpha: pd.DataFrame, universe: str, sw_bundle=None) -> pd.DataFrame:
    """§3.3：每 5 交易日按当日 base-α 重算；每名≤4%、≤20 名；行业帽；余额 510300；硬排除。

    无单独 gate 列：只从当日 alpha 表有的票里按 α 降序取。
    ind：叶31 alpha 无行业列 → 执行路径用 SW L1 asof；缺则 UNK（仍受 IND_CAP）。
    """
    if universe not in IND_CAP:
        raise SystemExit(f"FATAL universe 不支持: {universe}")
    cap = IND_CAP[universe]
    a = _normalize_alpha(alpha)
    a = a[a["alpha"].notna() & ~a["instrument"].isin(HARD_EXCLUDE)]
    dates = sorted(a["date"].unique())
    weight_rows: list[tuple] = []
    last_weights: list[tuple] | None = None
    rebal_countdown = 0
    sw_mod = sw_df = cal = None
    if sw_bundle is not None:
        sw_mod, sw_df, cal = sw_bundle
    for d in dates:
        if rebal_countdown <= 0:
            day = a.loc[a["date"] == d, ["instrument", "alpha"]].copy()
            day = day.sort_values("alpha", ascending=False, kind="mergesort")
            if sw_mod is not None:
                ind_map = _ind_for_day(sw_mod, sw_df, cal, day["instrument"].tolist(), d)
                day["ind"] = day["instrument"].map(ind_map).fillna("UNK")
            else:
                day["ind"] = "UNK"
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


def pin_gap_disclosure() -> dict:
    return {
        "overall": PIN_GAP_OVERALL,
        "gap_fields": list(PIN_GAP_FIELDS),
        "gap_fields_zh": "IC/ICIR/walk-forward（Alpha 闸 a476567d 标明 ABSENT；本票 evaluate 补齐）",
        "alpha_gate_sha8": ALPHA_GATE_SHA8,
        "alpha_gate_verdict": "ACCEPT_BUILD_PROCESS_ONLY",
        "arch_consume_sha8": ARCH_CONSUME_SHA8,
        "ai_run_receipt_sha8": AI_RUN_RECEIPT_SHA8,
        "overlap_sha8": "8396f211",
        "mechanism": MECHANISM,
        "claim_x2_accept": False,
        "leaf30_keep_repair_sha8_separate": LEAF30_KEEP_REPAIR_SHA8_SEPARATE,
        "note_zh": "Alpha ACCEPT 仅构建过程；IC/ICIR/WF 由 selfcheck evaluate 产出；≠X2 ACCEPT；0087c928 另队不夹带",
    }


def dry_compile_payload() -> dict:
    return {
        "live": False,
        "promotion_approved": False,
        "ok_requested": False,
        "selfcheck_executed": False,
        "book_smoke": False,
        "x2_accept": False,
        "rss_soft_mb": RSS_SOFT_MB,
        "rss_hard_mb": RSS_HARD_MB,
        "peak_proof_required": PEAK_PROOF_REQUIRED,
        "forbid_raise_rss": True,
        "universe": "HILIQ",
        "window": "x2",
        "pin_alpha": str(PIN_ALPHA),
        "pin_alpha_sha256": PIN_ALPHA_SHA,
        "pin_meta_sha256": PIN_META_SHA,
        "pin_overlap_sha256": PIN_OVERLAP_SHA,
        "build_script_sha8_unchanged": BUILD_SCRIPT_SHA8,
        "arch_consume_sha8": ARCH_CONSUME_SHA8,
        "alpha_gate_sha8": ALPHA_GATE_SHA8,
        "ai_run_receipt_sha8": AI_RUN_RECEIPT_SHA8,
        "mechanism": MECHANISM,
        "x2_end": "20261009",
        "leaf": "leaf31_amihud",
        "selfcheck_version": "v1",
        "name_w": NAME_W,
        "max_names": MAX_NAMES,
        "rebal_every": REBAL_EVERY,
        "ind_cap_hiliq": IND_CAP["HILIQ"],
        "ballast": BALLAST,
        "hard_exclude": sorted(HARD_EXCLUDE),
        "forbid_restored_ok_sha8": list(FORBID_RESTORED),
        "proposed_ok_path": PROPOSED_OK,
        "proposed_ok_created": False,
        "sampler_prefix": SAMPLER_PREFIX,
        "pin_gap": pin_gap_disclosure(),
        "alpha_build_consumed_not_x2_accept": True,
        "leaf30_keep_repair_sha8_separate": LEAF30_KEEP_REPAIR_SHA8_SEPARATE,
        "gate_policy_zh": "leaf_selfcheck_common.evaluate：decay KEEP/DOWNGRADE + portfolio gates A/B/current",
        "cli_note_zh": "禁 --arch-ok-path（未实现；流程门=外挂新 .ok+主窗）",
        "note_zh": "dry-compile-only：不读大行情、不写权重实数、不调用 evaluate",
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="叶31 Amihud Impact Slow X2 selfcheck_v1（钉既有冻结 alpha；DRAFT/签窗后实跑）"
    )
    ap.add_argument("--universe", default="HILIQ", choices=["HILIQ"])
    ap.add_argument("--window", default="x2", choices=["x2"])
    ap.add_argument("--alpha-path", type=Path, default=PIN_ALPHA)
    ap.add_argument("--meta-path", type=Path, default=PIN_META)
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
    # 故意不实现 --arch-ok-path（对齐叶25/30 P0：流程门外挂，不进 CLI）
    args = ap.parse_args(argv)

    if args.dry_compile_only:
        pins = assert_pins(args.alpha_path, args.meta_path)
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

    pins = assert_pins(args.alpha_path, args.meta_path)
    check_rss_hard("pre_execute")
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    alpha = pd.read_parquet(args.alpha_path)
    check_rss_hard("post_read_alpha")

    sw_bundle = _load_sw_bundle()
    check_rss_hard("post_load_sw")
    weights = build_eval_weights(alpha, args.universe, sw_bundle=sw_bundle)
    check_rss_hard("post_weights")
    SELFCHECK_SUB.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    wp = SELFCHECK_SUB / f"eval_weights_{args.universe}_{args.window}_{stamp}.parquet"
    weights.to_parquet(wp, index=False)
    w_sha = sha256_file(wp)

    import research.leaf_selfcheck_common as LC

    result = LC.evaluate(wp)
    peak = check_rss_hard("post_evaluate")
    result_meta = {
        "leaf": "leaf31_amihud",
        "mechanism": MECHANISM,
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
        "build_script_sha8_unchanged": BUILD_SCRIPT_SHA8,
        "eval_weights_path": str(wp),
        "eval_weights_sha256": w_sha,
        "eval_weights_dir_note": "output/ai_factory/_leaf31_amihud/20261027_024204/_selfcheck/",
        "overlap_path": str(PIN_OVERLAP),
        "overlap_sha256": PIN_OVERLAP_SHA,
        "arch_consume_sha8": ARCH_CONSUME_SHA8,
        "alpha_gate_sha8": ALPHA_GATE_SHA8,
        "ai_run_receipt_sha8": AI_RUN_RECEIPT_SHA8,
        "n_weight_rows": int(len(weights)),
        "n_weight_days": int(weights["date"].nunique()) if len(weights) else 0,
        "name_w": NAME_W,
        "max_names": MAX_NAMES,
        "rebal_every": REBAL_EVERY,
        "ind_cap": IND_CAP[args.universe],
        "ballast": BALLAST,
        "hard_exclude": sorted(HARD_EXCLUDE),
        "gate_policy_zh": "leaf_selfcheck_common.evaluate：decay KEEP/DOWNGRADE + portfolio gates A/B/current；无单独 alpha gate 列",
        "forbid_restored_ok_sha8": list(FORBID_RESTORED),
        "proposed_ok_path": PROPOSED_OK,
        "alpha_build_consumed_not_x2_accept": True,
        "leaf30_keep_repair_sha8_separate": LEAF30_KEEP_REPAIR_SHA8_SEPARATE,
        "pin_gap": pin_gap_disclosure(),
        "rss_mb_soft_limit": RSS_SOFT_MB,
        "rss_mb_hard_limit": RSS_HARD_MB,
        "peak_proof_required": PEAK_PROOF_REQUIRED,
        "peak_proof": {
            "ru_maxrss_mb": round(peak, 2),
            "sampler_prefix": SAMPLER_PREFIX,
            "note_zh": "peak_proof REQUIRED；回执须带 ru_maxrss 或 sampler 峰",
        },
        "rss_mb_peak_self": round(peak, 2),
        "evaluate": result,
    }
    out_json = REPORT_DIR / "selfcheck_v1.json"
    out_json.write_text(json.dumps(result_meta, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    side_meta = SELFCHECK_SUB / f"selfcheck_run_meta_{args.universe}_{args.window}_{stamp}.json"
    side_meta.write_text(json.dumps(result_meta, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    print(
        json.dumps(
            {
                "ok": True,
                "live": False,
                "selfcheck_v1": str(out_json),
                "eval_weights": str(wp),
                "side_meta": str(side_meta),
                "rss_mb": round(peak, 2),
                "pin_gap_overall": PIN_GAP_OVERALL,
                "x2_accept": False,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
