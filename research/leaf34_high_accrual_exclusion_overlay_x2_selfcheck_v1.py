#!/usr/bin/env python3
"""叶34 High Accrual Exclusion Overlay X2 selfcheck_v1：钉既有冻结 exclusion_mask → 叠加主干权重 → leaf_selfcheck_common.evaluate。

本票 ≠ 复跑 leaf34 构建（482009dc UNCHANGED）；≠ Book-Smoke；≠ X2 ACCEPT；≠升纸面。
live=false；promotion_approved=false；禁自签 .ok；禁抬帽。
PRIMARY 交付 = mask-only overlay（≠ α TopN 选股）：按日把 capacity_adv 权重与 exclusion_mask 对齐；
mask=0（高应计）→ 该名权重置 0；不可算名（mask 缺失）不进有效叠加、不填假 0；其余正权 + ballast 重归一；
硬排除 600519.SH / 002371.SZ；余额 510300.SH。

闸门书面冻结（FROZEN 8be1099e；先于读数）：
- PRIMARY=HI_LIQ mask-only top_q=0.20 叠加主干
- 判定=叶自身主干级 OR（ρ_excess vs capacity_adv <0.5 且 60万/100万叠加均优于主干）
- 并列报 Gate A / Gate B / 当前新口径（current）— 来自 leaf_selfcheck_common.evaluate
- decay KEEP 三闸合取：近端252d；latest_resid_alpha>0 ∧ 非连降5季 ∧ H2_net_cagr>510300
- KEEP 不解阻 X2 ACCEPT（叶32 HOLD 45dd87dc）

派生自 leaf32_margin_net_flow_resid_x2_selfcheck_v1.py（dcf6b559）；模板只读；勿盲抄 TopN 权重路径。
CLI 禁 --arch-ok-path（未实现；流程门=外挂新 .ok+主窗，对齐叶25/30/31/32 P0）。
0087c928 / 叶28/29 另队：本脚本不读该路径。叶33 afbbe7e7 UNCHANGED；叶32 HOLD 45dd87dc 不回撤。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import resource
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# --- 硬钉（PRIMARY HILIQ × x2；叶34 High Accrual Exclusion Overlay CONSUMED 产物）---
PIN_MASK = (
    ROOT
    / "output/ai_factory/_leaf34_high_accrual/20261027_105941/exclusion_mask_HILIQ_x2_20261027_105958.parquet"
)
PIN_META = ROOT / "output/ai_factory/_leaf34_high_accrual/20261027_105941/run_meta.json"
PIN_OVERLAP = (
    ROOT
    / "output/ai_factory/_leaf34_high_accrual/20261027_105941/overlap_vs_leaf19_25_27_30_31_32_33.json"
)
PIN_MASK_SHA = "8b5d6d247d8f3968f5fef521aa5d08891f6f6f6c8626dd761c7313bc0d71dabb"
PIN_META_SHA = "4fc6108d64ca5a2e112b04fbb468c9d95e554cf8498ba03fc13828c2ef7ee7ad"
PIN_OVERLAP_SHA = "77368c8fed1f7c167dfa51f4aa2e94e9b405236bf388c8f20f95365613e72fb7"
BUILD_SCRIPT_SHA8 = "482009dc"  # research/leaf34_high_accrual_exclusion_overlay_alpha_build.py UNCHANGED
ARCH_CONSUME_SHA8 = "fea9b3ff"
CONSUMED_OK_SHA8 = "c1b71e64"  # 已 CONSUMED ABSENT；禁 RESTORED
AI_RUN_RECEIPT_SHA8 = "1441a7ec"
RUNNING_ACK_SHA8 = "c03d2f16"
FROZEN_SHA8 = "8be1099e"
PIN_SHA8 = "bb418e6a"
MECHANISM = "g1g5_ashare_high_accrual_exclusion_overlay_v1"
PRIMARY_DELIVERY = "mask_only"
TOP_Q = 0.20

OUT_DIR = ROOT / "output/ai_factory/_leaf34_high_accrual/20261027_105941"
SELFCHECK_SUB = OUT_DIR / "_selfcheck"
REPORT_DIR = ROOT / "output/ai_factory/leaf_reports/leaf34_high_accrual"

# 对齐 leaf_selfcheck_common.CAP_ADV（勿另开路径）
CAP_ADV = ROOT / "output/ai_factory/g1g5_capacity_adv_daily_weights_20261013_111219.parquet"

BALLAST = "510300.SH"
HARD_EXCLUDE = frozenset({"600519.SH", "002371.SZ"})
RSS_SOFT_MB = 1500  # 软/硬同钉；禁抬
RSS_HARD_MB = 1500
PEAK_PROOF_REQUIRED = True
SAMPLER_PREFIX = "/tmp/quantlab_leaf34_x2_selfcheck_"
PROPOSED_OK = (
    "output/ai_factory/ARCH_RUN_AUTH_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_X2_SELFCHECK_V1_HILIQ_X2.ok"
)
# 叶34 X2 build CONSUMED + 叶32/31/30 forbid + 二十票(+81521fb5)
FORBID_RESTORED = (
    "c1b71e64",
    "245df63f",
    "c5ed13df",
    "5774bb6e",
    "02426b73",
    "4bb141c9",
    "fdbaa512",
    "aa25e989",
    "7e239487",
    "5af20222",
    "5ae077fa",
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
    "81521fb5",
)
LEAF30_KEEP_REPAIR_SHA8_SEPARATE = "0087c928"
LEAF33_FORMAL_SHA8_READONLY = "afbbe7e7"
LEAF32_HOLD_SHA8_NO_ROLLBACK = "45dd87dc"
LEAF32_SELFCHECK_TEMPLATE_SHA8 = "dcf6b559"
LEAF31_SELFCHECK_TEMPLATE_SHA8 = "e1fe578c"

# 闸门书面冻结（先于读数；FROZEN 8be1099e）
GATE_POLICY_FROZEN_ZH = (
    "PRIMARY=HI_LIQ mask-only top_q=0.20 叠加主干；"
    "判定=叶自身主干级 OR (ρ_excess vs capacity_adv <0.5 且 60万/100万叠加均优于主干)；"
    "并列报 Gate A / Gate B / current（leaf_selfcheck_common.evaluate）；"
    "decay KEEP 三闸合取：近端252d；latest_resid_alpha>0 ∧ 非连降5季 ∧ H2_net_cagr>510300；"
    "KEEP 不解阻 X2 ACCEPT（叶32 HOLD 45dd87dc）"
)
RHO_EXCESS_FORMULA_ZH = (
    "ρ_excess = corr(r_leaf_net − r_510300, r_capacity_adv_net − r_510300) 全日样本 Pearson；"
    "真跑时由 evaluate 侧日收益序列计算并写入 meta；dry 只钉公式不读行情"
)


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


def assert_pins(mask_path: Path, meta_path: Path) -> dict:
    """硬钉 mask+meta+overlap 路径+全长 sha；不 MATCH 则 exit≠0。"""
    if mask_path.resolve() != PIN_MASK.resolve():
        raise SystemExit(f"FATAL mask-path 偏离钉盘: {mask_path} ≠ {PIN_MASK}")
    if meta_path.resolve() != PIN_META.resolve():
        raise SystemExit(f"FATAL meta-path 偏离钉盘: {meta_path} ≠ {PIN_META}")
    out = {}
    for p, exp in (
        (mask_path.resolve(), PIN_MASK_SHA),
        (meta_path.resolve(), PIN_META_SHA),
        (PIN_OVERLAP.resolve(), PIN_OVERLAP_SHA),
    ):
        if not p.is_file():
            raise SystemExit(f"FATAL 缺件: {p}")
        got = sha256_file(p)
        if got != exp:
            raise SystemExit(f"FATAL sha MISMATCH {p.name}: got={got} expect={exp}")
        out[p.name] = got
    build = ROOT / "research/leaf34_high_accrual_exclusion_overlay_alpha_build.py"
    bsha = sha256_file(build)
    if not bsha.startswith(BUILD_SCRIPT_SHA8):
        raise SystemExit(f"FATAL build script sha drift: {bsha[:8]} ≠ {BUILD_SCRIPT_SHA8}")
    out["build_script_sha256"] = bsha
    # 模板只读校验（禁改字节）
    t32 = ROOT / "research/leaf32_margin_net_flow_resid_x2_selfcheck_v1.py"
    t31 = ROOT / "research/leaf31_amihud_impact_slow_x2_selfcheck_v1.py"
    common = ROOT / "research/leaf_selfcheck_common.py"
    for p, expect8 in (
        (t32, LEAF32_SELFCHECK_TEMPLATE_SHA8),
        (t31, LEAF31_SELFCHECK_TEMPLATE_SHA8),
    ):
        got = sha256_file(p)
        if not got.startswith(expect8):
            raise SystemExit(f"FATAL template drift {p.name}: {got[:8]} ≠ {expect8}")
        out[p.name] = got
    if not common.is_file():
        raise SystemExit(f"FATAL 缺件: {common}")
    out[common.name] = sha256_file(common)
    if not CAP_ADV.is_file():
        raise SystemExit(f"FATAL 缺 CAP_ADV: {CAP_ADV}")
    out["cap_adv_sha256"] = sha256_file(CAP_ADV)
    return out


def _mask_schema_light() -> dict:
    """dry 可轻量读 parquet schema/列名；不加载全表收益。"""
    try:
        import pyarrow.parquet as pq
    except ImportError:
        return {"schema_ok": False, "reason": "pyarrow_absent"}
    pf = pq.ParquetFile(PIN_MASK)
    cols = list(pf.schema_arrow.names)
    return {
        "schema_ok": True,
        "columns": cols,
        "num_rows": int(pf.metadata.num_rows) if pf.metadata is not None else None,
        "required_cols": ["trade_date", "ts_code", "mask"],
        "required_present": all(c in cols for c in ("trade_date", "ts_code", "mask")),
        "note_zh": "dry 只读 schema；未加载全表、未读收益",
    }


def build_eval_weights_from_mask(mask, cap_adv, universe: str):
    """mask-only overlay：capacity_adv × exclusion_mask；≠ α TopN。

    - 按日读 capacity_adv 权重
    - 与 exclusion_mask 对齐（trade_date/ts_code ↔ date/instrument）
    - mask=0（高应计）→ 该名权重置 0
    - 不可算名（mask 缺失）不进有效叠加、不填假 0（其原权重并入 ballast，≠伪称高应计剔除）
    - 硬排除 600519.SH / 002371.SZ（权重并入 ballast）
    - 对其余正权名 + ballast 重归一（余额 510300.SH）
    """
    import numpy as np
    import pandas as pd

    if universe != "HILIQ":
        raise SystemExit(f"FATAL universe 不支持 PRIMARY: {universe}（禁静默 FULLA）")

    m = mask.copy()
    colmap = {}
    if "trade_date" in m.columns and "date" not in m.columns:
        colmap["trade_date"] = "date"
    if "ts_code" in m.columns and "instrument" not in m.columns:
        colmap["ts_code"] = "instrument"
    if colmap:
        m = m.rename(columns=colmap)
    need = {"date", "instrument", "mask"}
    miss = need - set(m.columns)
    if miss:
        raise SystemExit(f"FATAL mask 缺列: {sorted(miss)}")
    m["date"] = pd.to_datetime(m["date"], errors="coerce").dt.normalize()
    if m["date"].isna().any():
        raise SystemExit("FATAL mask date 无法解析")
    m["instrument"] = m["instrument"].astype(str)
    m["mask"] = pd.to_numeric(m["mask"], errors="coerce")
    # 仅保留可算名（mask 有限）；缺失不填假 0
    m = m[m["mask"].notna()][["date", "instrument", "mask"]].drop_duplicates(
        ["date", "instrument"], keep="last"
    )

    c = cap_adv.copy()
    if "date" not in c.columns or "instrument" not in c.columns:
        raise SystemExit("FATAL CAP_ADV 缺 date/instrument")
    wcol = "target_weight" if "target_weight" in c.columns else (
        "weight" if "weight" in c.columns else None
    )
    if wcol is None:
        raise SystemExit("FATAL CAP_ADV 缺 target_weight/weight")
    c["date"] = pd.to_datetime(c["date"], errors="coerce").dt.normalize()
    c["instrument"] = c["instrument"].astype(str)
    c["target_weight"] = pd.to_numeric(c[wcol], errors="coerce")
    c = c[c["target_weight"].notna() & (c["target_weight"] > 0)]

    weight_rows: list[tuple] = []
    for d, day_w in c.groupby("date", sort=True):
        day_m = m.loc[m["date"] == d, ["instrument", "mask"]]
        mmap = day_m.set_index("instrument")["mask"] if len(day_m) else pd.Series(dtype=float)

        kept: dict[str, float] = {}
        bal = 0.0
        for _, row in day_w.iterrows():
            inst = str(row["instrument"])
            w = float(row["target_weight"])
            if inst == BALLAST:
                bal += w
                continue
            if inst in HARD_EXCLUDE:
                bal += w
                continue
            if inst not in mmap.index:
                # 不可算名：不进有效叠加、不填假 0；原权重并入 ballast
                bal += w
                continue
            if float(mmap.loc[inst]) <= 0.0:
                # 高应计 mask=0 → 权重置 0，释放进 ballast
                bal += w
                continue
            kept[inst] = kept.get(inst, 0.0) + w

        if not kept:
            weight_rows.append((d, BALLAST, 1.0))
            continue
        rows_day = [(d, inst, w) for inst, w in kept.items()]
        rows_day.append((d, BALLAST, bal if bal > 0 else 0.0))
        tot = sum(w for _, _, w in rows_day)
        if tot <= 0:
            weight_rows.append((d, BALLAST, 1.0))
            continue
        for dd, inst, w in rows_day:
            ww = w / tot
            if ww > 0:
                weight_rows.append((dd, inst, ww))

    weights = pd.DataFrame(weight_rows, columns=["date", "instrument", "target_weight"])
    if len(weights):
        s = weights.groupby("date")["target_weight"].transform("sum").replace(0, np.nan)
        weights["target_weight"] = weights["target_weight"] / s
        weights = weights[weights["target_weight"] > 0].reset_index(drop=True)
    return weights


def pin_gap_disclosure() -> dict:
    return {
        "overall": "MASK_ONLY_OVERLAY_NO_FULL_ALPHA",
        "gap_fields_zh": (
            "本叶 PRIMARY=mask-only；无完整主 α TopN；"
            "IC/ICIR/WF 非本票主交付；组合闸/衰减由 evaluate 产出"
        ),
        "arch_consume_sha8": ARCH_CONSUME_SHA8,
        "consumed_ok_sha8": CONSUMED_OK_SHA8,
        "ai_run_receipt_sha8": AI_RUN_RECEIPT_SHA8,
        "running_ack_sha8": RUNNING_ACK_SHA8,
        "frozen_sha8": FROZEN_SHA8,
        "pin_sha8": PIN_SHA8,
        "overlap_sha8": "77368c8f",
        "mask_sha8": "8b5d6d24",
        "meta_sha8": "4fc6108d",
        "mechanism": MECHANISM,
        "primary_delivery": PRIMARY_DELIVERY,
        "top_q": TOP_Q,
        "claim_x2_accept": False,
        "keep_does_not_unblock_x2_accept": True,
        "leaf32_hold_sha8_no_rollback": LEAF32_HOLD_SHA8_NO_ROLLBACK,
        "leaf33_formal_sha8_readonly": LEAF33_FORMAL_SHA8_READONLY,
        "leaf30_keep_repair_sha8_separate": LEAF30_KEEP_REPAIR_SHA8_SEPARATE,
        "rho_excess_formula_zh": RHO_EXCESS_FORMULA_ZH,
        "gate_policy_frozen_zh": GATE_POLICY_FROZEN_ZH,
        "decay_keep_watch_zh": (
            "decay KEEP 三闸合取（latest_resid_alpha>0 ∧ not_five_quarter_decline "
            "∧ H2_net_cagr>510300；近端252d）；KEEP 不解阻 X2 ACCEPT（叶32 45dd87dc）"
        ),
        "note_zh": (
            "mask-only overlay ≠ accrual TopN 主 α；≠X2 ACCEPT；"
            "0087c928/叶28/29 另队不夹带；禁 RESTORED c1b71e64"
        ),
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
        "primary_delivery": PRIMARY_DELIVERY,
        "top_q": TOP_Q,
        "soft_penalty_is_primary": False,
        "pin_mask": str(PIN_MASK),
        "pin_mask_sha256": PIN_MASK_SHA,
        "pin_meta_sha256": PIN_META_SHA,
        "pin_overlap_sha256": PIN_OVERLAP_SHA,
        "build_script_sha8_unchanged": BUILD_SCRIPT_SHA8,
        "arch_consume_sha8": ARCH_CONSUME_SHA8,
        "consumed_ok_sha8": CONSUMED_OK_SHA8,
        "ai_run_receipt_sha8": AI_RUN_RECEIPT_SHA8,
        "running_ack_sha8": RUNNING_ACK_SHA8,
        "frozen_sha8": FROZEN_SHA8,
        "pin_sha8": PIN_SHA8,
        "mechanism": MECHANISM,
        "x2_end": "20261009",
        "leaf": "leaf34_high_accrual",
        "selfcheck_version": "v1",
        "cap_adv_path": str(CAP_ADV),
        "weight_rule_zh": (
            "build_eval_weights_from_mask：capacity_adv × exclusion_mask；"
            "mask=0→权重置0；mask缺失不进有效叠加不填假0；硬排除600519/002371；余额510300；≠α TopN"
        ),
        "ballast": BALLAST,
        "hard_exclude": sorted(HARD_EXCLUDE),
        "forbid_restored_ok_sha8": list(FORBID_RESTORED),
        "proposed_ok_path": PROPOSED_OK,
        "proposed_ok_created": False,
        "sampler_prefix": SAMPLER_PREFIX,
        "pin_gap": pin_gap_disclosure(),
        "mask_build_consumed_not_x2_accept": True,
        "keep_does_not_unblock_x2_accept": True,
        "leaf30_keep_repair_sha8_separate": LEAF30_KEEP_REPAIR_SHA8_SEPARATE,
        "leaf33_formal_sha8_readonly": LEAF33_FORMAL_SHA8_READONLY,
        "leaf32_hold_sha8_no_rollback": LEAF32_HOLD_SHA8_NO_ROLLBACK,
        "leaf32_selfcheck_template_sha8_readonly": LEAF32_SELFCHECK_TEMPLATE_SHA8,
        "leaf31_selfcheck_template_sha8_readonly": LEAF31_SELFCHECK_TEMPLATE_SHA8,
        "gate_policy_frozen_zh": GATE_POLICY_FROZEN_ZH,
        "rho_excess_formula_zh": RHO_EXCESS_FORMULA_ZH,
        "cli_note_zh": "禁 --arch-ok-path（未实现；流程门=外挂新 .ok+主窗；对齐叶25/30/31/32 P0）",
        "note_zh": "dry-compile-only：不读大行情、不写权重实数、不调用 evaluate；pandas 仅 execute 路径",
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="叶34 High Accrual Exclusion Overlay X2 selfcheck_v1（钉既有冻结 mask；DRAFT/签窗后实跑）"
    )
    ap.add_argument("--universe", default="HILIQ", choices=["HILIQ"])
    ap.add_argument("--window", default="x2", choices=["x2"])
    ap.add_argument("--mask-path", type=Path, default=PIN_MASK)
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
    # 故意不实现 --arch-ok-path（对齐叶25/30/31/32 P0：流程门外挂，不进 CLI）
    args = ap.parse_args(argv)

    if args.dry_compile_only:
        pins = assert_pins(args.mask_path, args.meta_path)
        payload = dry_compile_payload()
        payload["pin_sha_match"] = True
        payload["pin_sha_table"] = pins
        payload["mask_schema_light"] = _mask_schema_light()
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

    import pandas as pd

    pins = assert_pins(args.mask_path, args.meta_path)
    check_rss_hard("pre_execute")
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    mask = pd.read_parquet(args.mask_path, columns=["trade_date", "ts_code", "mask"])
    check_rss_hard("post_read_mask")
    cap_adv = pd.read_parquet(
        CAP_ADV, columns=["date", "instrument", "target_weight"]
    )
    check_rss_hard("post_read_cap_adv")
    weights = build_eval_weights_from_mask(mask, cap_adv, args.universe)
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

    # 可选披露 ρ_excess（leaf vs capacity_adv）；失败不阻断主闸
    rho_excess = None
    rho_note = RHO_EXCESS_FORMULA_ZH
    try:
        import numpy as np
        from research import alpha_decay_gate as ADG

        g_leaf, _ = ADG.gross_and_turnover(wp)
        g_cap, _ = ADG.gross_and_turnover(CAP_ADV)
        b = ADG.bench().pct_change()
        ix = g_leaf.index.intersection(g_cap.index).intersection(b.index)
        el = (g_leaf.reindex(ix) - b.reindex(ix)).fillna(0.0)
        ec = (g_cap.reindex(ix) - b.reindex(ix)).fillna(0.0)
        if len(ix) >= 20 and float(el.std()) > 0 and float(ec.std()) > 0:
            rho_excess = float(np.corrcoef(el.values, ec.values)[0, 1])
    except Exception as exc:  # noqa: BLE001
        rho_note = f"{RHO_EXCESS_FORMULA_ZH}；计算失败: {type(exc).__name__}: {exc}"

    result_meta = {
        "leaf": "leaf34_high_accrual",
        "mechanism": MECHANISM,
        "primary_delivery": PRIMARY_DELIVERY,
        "top_q": TOP_Q,
        "soft_penalty_is_primary": False,
        "universe": args.universe,
        "window": args.window,
        "live": False,
        "promotion_approved": False,
        "book_smoke": False,
        "x2_accept": False,
        "selfcheck_executed": True,
        "stamp": stamp,
        "mask_path": str(args.mask_path),
        "mask_sha256": pins[args.mask_path.name],
        "meta_sha256": pins[args.meta_path.name],
        "build_script_sha8_unchanged": BUILD_SCRIPT_SHA8,
        "eval_weights_path": str(wp),
        "eval_weights_sha256": w_sha,
        "eval_weights_dir_note": "output/ai_factory/_leaf34_high_accrual/20261027_105941/_selfcheck/",
        "cap_adv_path": str(CAP_ADV),
        "overlap_path": str(PIN_OVERLAP),
        "overlap_sha256": PIN_OVERLAP_SHA,
        "arch_consume_sha8": ARCH_CONSUME_SHA8,
        "consumed_ok_sha8": CONSUMED_OK_SHA8,
        "ai_run_receipt_sha8": AI_RUN_RECEIPT_SHA8,
        "running_ack_sha8": RUNNING_ACK_SHA8,
        "frozen_sha8": FROZEN_SHA8,
        "pin_sha8": PIN_SHA8,
        "n_weight_rows": int(len(weights)),
        "n_weight_days": int(weights["date"].nunique()) if len(weights) else 0,
        "ballast": BALLAST,
        "hard_exclude": sorted(HARD_EXCLUDE),
        "gate_policy_frozen_zh": GATE_POLICY_FROZEN_ZH,
        "rho_excess_vs_capacity_adv": rho_excess,
        "rho_excess_formula_zh": rho_note,
        "keep_does_not_unblock_x2_accept": True,
        "forbid_restored_ok_sha8": list(FORBID_RESTORED),
        "proposed_ok_path": PROPOSED_OK,
        "mask_build_consumed_not_x2_accept": True,
        "leaf30_keep_repair_sha8_separate": LEAF30_KEEP_REPAIR_SHA8_SEPARATE,
        "leaf33_formal_sha8_readonly": LEAF33_FORMAL_SHA8_READONLY,
        "leaf32_hold_sha8_no_rollback": LEAF32_HOLD_SHA8_NO_ROLLBACK,
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
    out_json.write_text(
        json.dumps(result_meta, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
    )

    side_meta = SELFCHECK_SUB / f"selfcheck_run_meta_{args.universe}_{args.window}_{stamp}.json"
    side_meta.write_text(
        json.dumps(result_meta, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
    )

    print(
        json.dumps(
            {
                "ok": True,
                "live": False,
                "selfcheck_v1": str(out_json),
                "eval_weights": str(wp),
                "side_meta": str(side_meta),
                "rss_mb": round(peak, 2),
                "rho_excess_vs_capacity_adv": rho_excess,
                "x2_accept": False,
                "keep_does_not_unblock_x2_accept": True,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
