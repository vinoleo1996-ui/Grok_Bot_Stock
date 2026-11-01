#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""申万 L1 PIT v2 修复脚本（code-change 包）—— P0 双开闭合 / P1 bak235 恢复。

硬钉（封面与本 docstring 一致）：
  **修 PIT ≠ 解阻叶25 / X2**；不替代 mem_probe / X2 `.ok`；不改 Strategy sw_members_asof。
  live=false 硬编码；promotion_approved 输出保持 false；不读网络；不调 Tushare/中转。
  禁消费补跑 `.ok` `9e4359f9…`；禁改 CLEAN/VOTE/BAD 现盘；execute 仅写新文件路径（由 --out-dir）。
  旧 `scripts/acquire/sw_pit_refresh.py` 无闸覆盖：**本脚本不改**（另工单废止）。

资源：建议 `nice -n 10`；分码处理；目标单进程 RSS≤1.5GB。
本回合默认 --dry-run；dry 的 --out-dir 必须在 /tmp 下。
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple

# live=false 硬编码（不可被 CLI/环境抬升）
LIVE = False
PROMOTION_APPROVED = False

# 禁消费补跑 .ok（全长）
BANNED_OK_SHA = "9e4359f9"  # 前缀匹配即可拒；下方全长若可知再钉
BANNED_OK_SHA_FULL_PREFIXES = (
    "9e4359f9",
)

# 方案钉死输入 sha（全长）
PIN_SHA = {
    "bad": "0b1d3432e30f7cdd907df393299cd2f552e1121899239985a00113c4dfcd89f6",
    "bak": "597340148480675b09a0560ae7ce23917edf5f35c40e51c25c64f3b701f72c9c",
    "clean": "89d4afa337435a2302b5c13fd4cf049b71eda2f20e1d9094f15d62cdb587f66c",
}

SCHEMA_COLS = [
    "instrument_id",
    "l1_code",
    "ts_code",
    "name",
    "l1_name",
    "in_date",
    "out_date",
    "is_new",
    "available_at",
    "source",
    "promotion_approved",
]

ROOT_DEFAULT = Path("/workspace/QuantLab")
DEFAULT_BAD = ROOT_DEFAULT / "data/v2/sw_pit/industry_members_sw_l1_pit.parquet"
DEFAULT_BAK = ROOT_DEFAULT / "data/v2/sw_pit/industry_members_sw_l1_pit.bak_pre_fix_20261014.parquet"
DEFAULT_CLEAN = ROOT_DEFAULT / "data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet"
DEFAULT_CODES235 = (
    ROOT_DEFAULT / "docs/v2/audit/data_ro_audit_20261018/B_missing_codes_classified.csv"
)

# execute .ok 必检 allow 字段（缺一拒）
OK_REQUIRED = {
    "format": "quantlab_run_auth_v1",
    "live": "false",
    "promotion_approved": "false",
}
OK_ALLOW_TRUE_ANY = ("allow_run", "allow_execute", "allow_dry")  # 至少一类为 true（dry 用 allow_dry）
OK_SCOPE_NEEDLES = ("sw_l1_pit_v2", "sw_l1_pit", "SW_L1_PIT_V2")


def eprint(*a, **k):
    print(*a, file=sys.stderr, **k)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_ok(path: Path) -> Dict[str, str]:
    out: Dict[str, str] = {}
    text = path.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def validate_ok(path: Path, *, for_execute: bool) -> None:
    if not path.is_file():
        raise SystemExit(f"STOP: --ok not a file: {path}")
    digest = sha256_file(path)
    for pref in BANNED_OK_SHA_FULL_PREFIXES:
        if digest.startswith(pref):
            raise SystemExit(f"STOP: banned .ok sha prefix {pref}… (禁消费 9e4359f9)")
    fields = parse_ok(path)
    for k, expect in OK_REQUIRED.items():
        got = fields.get(k, "").lower()
        if got != expect.lower():
            raise SystemExit(f"STOP: .ok {k}={fields.get(k)!r} want {expect!r}")
    if fields.get("allow_write_production", "false").lower() == "true" and for_execute:
        # execute 写的是新 v2 路径，仍要求 live=false；若 .ok 显式允许写生产需 scope 钉 v2
        pass
    allow_hit = any(fields.get(k, "").lower() == "true" for k in OK_ALLOW_TRUE_ANY)
    if for_execute:
        if fields.get("allow_run", "").lower() != "true" and fields.get("allow_execute", "").lower() != "true":
            raise SystemExit("STOP: execute requires allow_run=true or allow_execute=true in .ok")
    else:
        if not allow_hit and fields.get("allow_dry", "").lower() != "true":
            # dry 路径通常不强制 .ok；仅 --execute 强制。若传入则宽松校验。
            eprint("WARN: .ok provided but no allow_*=true; continuing dry path checks only")
    scope_blob = " ".join(fields.get(k, "") for k in ("scope", "note", "auth_type", "kind", "target"))
    if for_execute and not any(n.lower() in scope_blob.lower() for n in OK_SCOPE_NEEDLES):
        # 也接受 script/path 字段含本脚本名
        path_blob = " ".join(fields.get(k, "") for k in fields)
        if "sw_l1_pit_v2_fix" not in path_blob:
            raise SystemExit("STOP: .ok scope/note 未钉 sw_l1_pit_v2（防误消费他票）")
    # 不解阻叶25
    for bad_claim in ("unblock_leaf25", "allow_leaf25", "allow_x2"):
        if fields.get(bad_claim, "").lower() == "true":
            raise SystemExit(f"STOP: .ok {bad_claim}=true 禁止（修 PIT ≠ 解阻叶25）")


def assert_out_dir_dry(out_dir: Path) -> None:
    resolved = out_dir.resolve()
    tmp_root = Path("/tmp").resolve()
    try:
        resolved.relative_to(tmp_root)
    except ValueError:
        raise SystemExit(f"STOP: dry-run --out-dir must be under /tmp, got {resolved}")
    s = str(resolved)
    for banned in ("/data/", "/output/", "/workspace/QuantLab/data", "/workspace/QuantLab/output"):
        if banned in s:
            raise SystemExit(f"STOP: dry-run out-dir refuses data/output path: {resolved}")


def is_open_series(out_date) -> bool:
    """True if out_date is null/NaT/empty."""
    import pandas as pd

    if out_date is None:
        return True
    try:
        if pd.isna(out_date):
            return True
    except (TypeError, ValueError):
        pass
    s = str(out_date).strip()
    return s in ("", "NaT", "None", "nan", "NaN", "<NA>")


def load_parquet(path: Path):
    import pandas as pd

    df = pd.read_parquet(path)
    return df


def ensure_schema(df):
    missing = [c for c in SCHEMA_COLS if c not in df.columns]
    if missing:
        raise SystemExit(f"STOP: input missing columns {missing}")
    out = df[SCHEMA_COLS].copy()
    # promotion_approved 强制 false
    out["promotion_approved"] = False
    return out


def pin_check(path: Path, key: str, *, skip: bool) -> str:
    digest = sha256_file(path)
    if skip:
        eprint(f"WARN: skip-input-sha {key} path={path} sha={digest}")
        return digest
    expect = PIN_SHA[key]
    if digest != expect:
        raise SystemExit(
            f"STOP: {key} sha mismatch\n  path={path}\n  got={digest}\n  want={expect}"
        )
    eprint(f"OK pin {key} sha MATCH {digest}")
    return digest


def close_dual_open(df, conflicts: List[dict]):
    """P0 核心：同 (instrument_id, l1_code) closed 优先 → 丢该组陈旧 open；
    若同 instrument 仍 >1 open，保留 in_date 最新 open，丢其余（记 conflicts）。
    返回新 df；断言每码 open≤1 由调用方做。
    """
    df = df.copy()
    df["_open"] = df["out_date"].map(is_open_series)
    drop_idx: Set[int] = set()

    # 1) 同 (instrument_id, l1_code)：若存在 closed，丢全部 open
    for (iid, l1), g in df.groupby(["instrument_id", "l1_code"], sort=False):
        has_closed = (~g["_open"]).any()
        if not has_closed:
            continue
        for idx in g.index[g["_open"]]:
            drop_idx.add(int(idx))
            row = df.loc[idx]
            conflicts.append(
                {
                    "phase": "p0_closed_prefer",
                    "instrument_id": iid,
                    "l1_code": l1,
                    "ts_code": row["ts_code"],
                    "in_date": str(row["in_date"]),
                    "out_date": "",
                    "action": "drop_stale_open",
                    "reason": "same_(instrument,l1) has closed row",
                }
            )

    kept = df.drop(index=list(drop_idx)).copy()
    kept["_open"] = kept["out_date"].map(is_open_series)

    # 2) 仍双开：保留最新 in_date open
    drop_idx2: Set[int] = set()
    open_rows = kept[kept["_open"]]
    for iid, g in open_rows.groupby("instrument_id", sort=False):
        if len(g) <= 1:
            continue
        # 最新 in_date；并列则保留 index 最大
        g2 = g.copy()
        g2["_idx"] = g2.index
        g2 = g2.sort_values(["in_date", "_idx"], ascending=[True, True])
        winners = g2.iloc[-1]
        for idx in g2["_idx"].iloc[:-1]:
            drop_idx2.add(int(idx))
            row = kept.loc[idx]
            conflicts.append(
                {
                    "phase": "p0_keep_latest_open",
                    "instrument_id": iid,
                    "l1_code": row["l1_code"],
                    "ts_code": row["ts_code"],
                    "in_date": str(row["in_date"]),
                    "out_date": "",
                    "action": "drop_older_open",
                    "reason": f"keep_open in_date={winners['in_date']} l1={winners['l1_code']}",
                }
            )

    kept = kept.drop(index=list(drop_idx2)).copy()
    kept = kept.drop(columns=["_open"], errors="ignore")
    return ensure_schema(kept)


def assert_open_at_most_one(df, label: str) -> None:
    open_mask = df["out_date"].map(is_open_series)
    vc = df.loc[open_mask].groupby("instrument_id").size()
    bad = vc[vc > 1]
    if len(bad):
        sample = list(bad.head(5).items())
        raise SystemExit(
            f"STOP: {label} open>1 for {len(bad)} codes; sample={sample}; 不落成功标记"
        )


def load_codes_235(path: Path) -> Set[str]:
    if not path.is_file():
        raise SystemExit(f"STOP: codes-235 csv missing: {path}")
    codes: Set[str] = set()
    with path.open(newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            in_bak = str(row.get("in_bak", "")).strip().lower() in ("true", "1", "yes")
            in_cur = str(row.get("in_cur_any", "")).strip().lower() in ("true", "1", "yes")
            if in_bak and not in_cur:
                codes.add(str(row["ts_code"]).strip())
    if len(codes) != 235:
        raise SystemExit(f"STOP: expected 235 bak-restorable codes, got {len(codes)} from {path}")
    return codes


def clean_open_norm_keys(clean_df) -> Set[Tuple[str, str]]:
    """CLEAN open 键：(instrument_id, sw_code) → 与 BAD (instrument_id, l1_code) 对齐。"""
    keys: Set[Tuple[str, str]] = set()
    sw_col = "sw_code" if "sw_code" in clean_df.columns else "l1_code"
    for _, row in clean_df.iterrows():
        if is_open_series(row["out_date"]):
            keys.add((str(row["instrument_id"]), str(row[sw_col])))
    return keys


def normdiff_vs_clean_open(df, clean_df) -> dict:
    """对照 CLEAN open 做 normdiff 报告（不改 CLEAN）。"""
    sw_col = "sw_code" if "sw_code" in clean_df.columns else "l1_code"
    clean_open = clean_df[clean_df["out_date"].map(is_open_series)]
    ours_open = df[df["out_date"].map(is_open_series)]
    clean_keys = set(zip(clean_open["instrument_id"].astype(str), clean_open[sw_col].astype(str)))
    ours_keys = set(zip(ours_open["instrument_id"].astype(str), ours_open["l1_code"].astype(str)))
    only_clean = sorted(clean_keys - ours_keys)
    only_ours = sorted(ours_keys - clean_keys)
    return {
        "clean_open_n": len(clean_keys),
        "ours_open_n": len(ours_keys),
        "only_clean_n": len(only_clean),
        "only_ours_n": len(only_ours),
        "only_clean_sample": only_clean[:20],
        "only_ours_sample": only_ours[:20],
    }


def forbid_shrink_flag_guard(allow_shrink: bool) -> None:
    """Arch CONDITION：禁 --allow-shrink。"""
    if allow_shrink:
        raise SystemExit("STOP: --allow-shrink is forbidden (Arch CONDITION §2.3)")


def run_p0(bad_df, out_dir: Path) -> object:
    conflicts: List[dict] = []
    n_in = bad_df["instrument_id"].nunique()
    fixed = close_dual_open(bad_df, conflicts)
    assert_open_at_most_one(fixed, "P0")
    n_out = fixed["instrument_id"].nunique()
    if n_out < n_in:
        raise SystemExit(
            f"STOP: P0 shrink codes {n_in}→{n_out}（禁 shrink；闭合只丢行不丢码）"
        )

    out_dir.mkdir(parents=True, exist_ok=True)
    mid_path = out_dir / "sw_l1_pit_v2_p0_mid.parquet"
    conf_path = out_dir / "conflicts_p0.csv"
    fixed.to_parquet(mid_path, index=False)
    with conf_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "phase",
                "instrument_id",
                "l1_code",
                "ts_code",
                "in_date",
                "out_date",
                "action",
                "reason",
            ],
        )
        w.writeheader()
        for row in conflicts:
            w.writerow(row)

    # 成功标记（仅断言通过后）
    marker = out_dir / "P0_OK.txt"
    open_n = int(fixed["out_date"].map(is_open_series).sum())
    open_codes = int(fixed.loc[fixed["out_date"].map(is_open_series), "instrument_id"].nunique())
    marker.write_text(
        f"P0_OK\nlive={LIVE}\npromotion_approved={PROMOTION_APPROVED}\n"
        f"rows={len(fixed)}\ncodes={n_out}\nopen_rows={open_n}\nopen_codes={open_codes}\n"
        f"conflicts={len(conflicts)}\n"
        f"NOTE: 修 PIT ≠ 解阻叶25 / X2\n",
        encoding="utf-8",
    )
    eprint(
        f"P0 done rows={len(fixed)} codes={n_out} open_rows={open_n} "
        f"open_codes={open_codes} conflicts={len(conflicts)} → {mid_path}"
    )
    return fixed


def run_p1(p0_df, bak_df, clean_df, codes235: Set[str], out_dir: Path) -> object:
    import pandas as pd

    # 先验收 P0 不变量
    assert_open_at_most_one(p0_df, "P1_input_P0")

    bak_open_235 = bak_df[
        bak_df["out_date"].map(is_open_series)
        & bak_df["ts_code"].astype(str).isin(codes235)
    ].copy()
    if bak_open_235["ts_code"].nunique() != 235:
        raise SystemExit(
            f"STOP: bak open for 235 codes = {bak_open_235['ts_code'].nunique()} want 235"
        )

    # 合并：P0 行 ∪ bak235 open 行；再套同一 closed-优先规则
    bak_open_235 = ensure_schema(bak_open_235)
    merged = pd.concat([ensure_schema(p0_df), bak_open_235], ignore_index=True)
    conflicts: List[dict] = []
    fixed = close_dual_open(merged, conflicts)
    assert_open_at_most_one(fixed, "P1")

    # 235 均有 open
    open_ts = set(fixed.loc[fixed["out_date"].map(is_open_series), "ts_code"].astype(str))
    missing_open = sorted(codes235 - open_ts)
    if missing_open:
        raise SystemExit(
            f"STOP: P1 {len(missing_open)} /235 still no open; sample={missing_open[:10]}"
        )

    # 禁 shrink：相对 bak / CLEAN 代码数下界
    n_codes = fixed["instrument_id"].nunique()
    bak_n = bak_df["instrument_id"].nunique()
    # 不得低于 bak（P1 目标含 bak 可恢复码）；CLEAN 对照见 normdiff（不强制 codes≥clean）
    if n_codes < bak_n:
        raise SystemExit(
            f"STOP: P1 shrink codes {n_codes} < bak {bak_n}（禁 shrink）"
        )

    nd = normdiff_vs_clean_open(fixed, clean_df)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "sw_l1_pit_v2_p1.parquet"
    conf_path = out_dir / "conflicts_p1.csv"
    nd_path = out_dir / "normdiff_vs_clean_open_p1.txt"
    fixed.to_parquet(out_path, index=False)
    with conf_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "phase",
                "instrument_id",
                "l1_code",
                "ts_code",
                "in_date",
                "out_date",
                "action",
                "reason",
            ],
        )
        w.writeheader()
        for row in conflicts:
            w.writerow(row)
    nd_path.write_text(
        "normdiff vs CLEAN open (read-only; CLEAN 未改)\n"
        f"clean_open_n={nd['clean_open_n']}\n"
        f"ours_open_n={nd['ours_open_n']}\n"
        f"only_clean_n={nd['only_clean_n']}\n"
        f"only_ours_n={nd['only_ours_n']}\n"
        f"only_clean_sample={nd['only_clean_sample']}\n"
        f"only_ours_sample={nd['only_ours_sample']}\n"
        "NOTE: 差异须全解释后方可申 execute；禁 allow-shrink\n"
        "NOTE: 修 PIT ≠ 解阻叶25 / X2\n",
        encoding="utf-8",
    )
    marker = out_dir / "P1_OK.txt"
    marker.write_text(
        f"P1_OK\nlive={LIVE}\npromotion_approved={PROMOTION_APPROVED}\n"
        f"rows={len(fixed)}\ncodes={n_codes}\n"
        f"restored_235_open={235 - len(missing_open)}\n"
        f"normdiff_only_clean={nd['only_clean_n']} only_ours={nd['only_ours_n']}\n"
        f"NOTE: 修 PIT ≠ 解阻叶25 / X2\n",
        encoding="utf-8",
    )
    eprint(
        f"P1 done rows={len(fixed)} codes={n_codes} "
        f"normdiff only_clean={nd['only_clean_n']} only_ours={nd['only_ours_n']} → {out_path}"
    )
    return fixed


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="SW L1 PIT v2 fix (P0/P1). 修 PIT ≠ 解阻叶25. live=false."
    )
    p.add_argument("--mode", choices=("p0", "p1"), required=True)
    p.add_argument(
        "--dry-run",
        dest="dry_run",
        action="store_true",
        default=True,
        help="default True; out-dir must be under /tmp",
    )
    p.add_argument(
        "--no-dry-run",
        dest="dry_run",
        action="store_false",
        help="alias toward execute path (still needs --execute)",
    )
    p.add_argument(
        "--execute",
        action="store_true",
        default=False,
        help="requires --ok with allow_run/allow_execute; this package turn must NOT invoke",
    )
    p.add_argument("--ok", type=Path, default=None, help="Arch .ok path (required with --execute)")
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--bad", type=Path, default=DEFAULT_BAD)
    p.add_argument("--bak", type=Path, default=DEFAULT_BAK)
    p.add_argument("--clean", type=Path, default=DEFAULT_CLEAN)
    p.add_argument("--codes-235", type=Path, default=DEFAULT_CODES235)
    p.add_argument(
        "--p0-mid",
        type=Path,
        default=None,
        help="P1: path to P0 mid parquet (default: out-dir/sw_l1_pit_v2_p0_mid.parquet or rebuild from --bad)",
    )
    p.add_argument(
        "--skip-input-sha",
        action="store_true",
        default=False,
        help="synthetic selftest only; production dry/execute MUST NOT set",
    )
    p.add_argument(
        "--allow-shrink",
        action="store_true",
        default=False,
        help="REJECTED: flag accepted only to hard-fail if set",
    )
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    # nice 意识：若可用则自降（不强制 root）
    try:
        os.nice(10)
    except (AttributeError, OSError):
        pass

    if LIVE:
        raise SystemExit("STOP: LIVE must be false")

    args = build_parser().parse_args(argv)

    forbid_shrink_flag_guard(args.allow_shrink)

    if args.execute:
        if args.ok is None:
            raise SystemExit("STOP: --execute requires --ok")
        validate_ok(args.ok, for_execute=True)
        # execute 仍可写非 /tmp（新 v2 路径），但本回合不应触发
        eprint("EXECUTE mode enabled (ok validated); writing to", args.out_dir)
        dry = False
    else:
        dry = bool(args.dry_run)
        if args.ok is not None:
            validate_ok(args.ok, for_execute=False)
        if dry:
            assert_out_dir_dry(args.out_dir)

    # 输入存在性
    for label, path in ("bad", args.bad), ("bak", args.bak), ("clean", args.clean):
        if not path.is_file():
            raise SystemExit(f"STOP: {label} missing: {path}")

    # sha 钉（合成自检可跳）
    pin_check(args.bad, "bad", skip=args.skip_input_sha)
    pin_check(args.bak, "bak", skip=args.skip_input_sha)
    pin_check(args.clean, "clean", skip=args.skip_input_sha)

    t0 = time.time()
    bad_df = ensure_schema(load_parquet(args.bad))

    if args.mode == "p0":
        # bak/clean 已在上方 pin_check（流式读文件算 sha，不常驻 RAM）
        run_p0(bad_df, args.out_dir)
    else:
        bak_df = ensure_schema(load_parquet(args.bak))
        clean_df = load_parquet(args.clean)  # CLEAN schema differs; don't ensure_schema
        codes235 = load_codes_235(args.codes_235)
        if args.p0_mid and args.p0_mid.is_file():
            p0_df = ensure_schema(load_parquet(args.p0_mid))
            assert_open_at_most_one(p0_df, "P0_mid")
        else:
            # 在线重算 P0（写入同一 out-dir）
            p0_df = run_p0(bad_df, args.out_dir)
        run_p1(p0_df, bak_df, clean_df, codes235, args.out_dir)

    eprint(f"DONE mode={args.mode} dry={dry} execute={args.execute} elapsed_s={time.time()-t0:.2f}")
    eprint("NOTE: 修 PIT ≠ 解阻叶25 / X2；live=false")
    return 0


if __name__ == "__main__":
    sys.exit(main())
