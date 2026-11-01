#!/usr/bin/env python3
"""研究级实时闭环（不下单）· 健康检查 + 端到端 dry-run 到可消费权重。

LIGHT — 不启 uvicorn、不跑 GP、不物化 Book NAV、不拉重型 moneyflow。
promotion_approved / strategy_promotion_approved 恒 false。

用法::

    cd /workspace/QuantLab
    PYTHONPATH=. /workspace/qlvenv/bin/python scripts/rt_loop_health_dryrun.py
    # 只验既有 G1G5 权重 + Data API：
    PYTHONPATH=. /workspace/qlvenv/bin/python scripts/rt_loop_health_dryrun.py --skip-skeleton
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

ET = ZoneInfo("America/New_York")
DEFAULT_DATA_API = os.environ.get("QUANTLAB_DATA_API", "http://127.0.0.1:8787")
# 既有生产级全日更样例（非 ≤10 日 stub）
DEFAULT_PROD_WEIGHT = (
    ROOT
    / "output/ai_factory/g1g5_idx_rebal_flow_daily_weights_20261012_215737.parquet"
)


def _now_et() -> str:
    return datetime.now(ET).strftime("%Y-%m-%dT%H:%M:%S%z")


def check_data_api(base: str, timeout: float = 3.0) -> dict:
    url = base.rstrip("/") + "/health"
    out: dict = {
        "ok": False,
        "url": url,
        "note": "只读探测；本脚本不启/不停 uvicorn（Data 侧 8787）",
    }
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            out["http_status"] = getattr(resp, "status", None) or resp.getcode()
            try:
                payload = json.loads(body)
            except json.JSONDecodeError:
                payload = {"raw": body[:500]}
            out["payload"] = payload
            out["ok"] = bool(
                (isinstance(payload, dict) and payload.get("ok") is True)
                or out["http_status"] == 200
            )
    except urllib.error.URLError as e:
        out["error"] = f"URLError:{e}"
        out["blocker_owner"] = "Data（8787 未起或不可达；需 Leo 原话「现在重启」才可启）"
    except Exception as e:  # noqa: BLE001
        out["error"] = f"{type(e).__name__}:{e}"
        out["blocker_owner"] = "Data/Eng"
    return out


def check_weight_contract() -> dict:
    from quantlab.platform.weight_long_table import schema_handshake

    hs = schema_handshake()
    return {
        "ok": True,
        "module": "quantlab.platform.weight_long_table",
        "handshake": hs,
        "cli": (
            'PYTHONPATH=. /workspace/qlvenv/bin/python -c '
            '"from quantlab.platform.weight_long_table import schema_handshake; '
            'import json; print(json.dumps(schema_handshake(),ensure_ascii=False))"'
        ),
    }


def validate_prod_weight(path: Path) -> dict:
    from quantlab.platform.weight_long_table import validate_weight_path

    out: dict = {
        "path": str(path),
        "exists": path.is_file(),
        "ok": False,
        "role": "生产级全日更样例校验（非 stub 演示窗）",
    }
    if not path.is_file():
        out["error"] = "missing_parquet"
        out["blocker_owner"] = "AI（需先产出 G1G5/机制日更权重）"
        return out
    meta_path = Path(str(path) + ".meta.json")
    if meta_path.is_file():
        try:
            out["sidecar_meta"] = json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            out["sidecar_meta_error"] = str(e)
    v = validate_weight_path(path, require_rows=True)
    out["validate"] = dict(v)
    side = out.get("sidecar_meta") or {}
    n_sess = int(side.get("n_distinct_sessions") or v.get("n_sessions") or 0)
    stub = bool(side.get("stub_window"))
    promo = bool(side.get("promotion_approved") or side.get("strategy_promotion_approved"))
    out["n_distinct_sessions"] = n_sess
    out["stub_window"] = stub
    out["promotion_approved"] = promo
    out["ok"] = (
        v.get("status") == "ok"
        and n_sess > 10
        and not stub
        and not promo
    )
    if n_sess <= 10 or stub:
        out["warn"] = "短窗/stub 不当作生产日更 KPI（见 QUANTMIND_P0_GATE_WEIGHT_CONTRACT）"
    return out


def run_skeleton_light(out_dir: Path, capital: int = 600_000) -> dict:
    """复用 Eng skeleton-smoke：trading_loop→factor_evolve→weight→book_smoke --skip-run。"""
    from quantlab.v2_skeleton_smoke import run_skeleton_smoke

    t0 = time.time()
    summary = run_skeleton_smoke(
        book_nav=False,
        capital=capital,
        top_k=5,
        out_dir=out_dir / "skeleton_smoke",
    )
    elapsed = time.time() - t0
    steps = summary.get("steps") or {}
    ok = bool(summary.get("ok")) and all(
        bool((steps.get(k) or {}).get("ok"))
        for k in ("trading_loop", "factor_evolve", "weight_long_table", "book_smoke")
    )
    fe = steps.get("factor_evolve") or {}
    return {
        "ok": ok,
        "elapsed_sec": round(elapsed, 3),
        "n_weight_rows": fe.get("n_weight_rows"),
        "weight_path": fe.get("weight_path"),
        "summary_path": str((out_dir / "skeleton_smoke" / "skeleton_smoke_summary.json")),
        "steps_ok": {k: bool((steps.get(k) or {}).get("ok")) for k in steps},
        "promotion_approved": False,
        "strategy_promotion_approved": False,
        "cli": "PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.cli skeleton-smoke",
        "note": "factor_evolve 为 10 日 smoke stub；生产日更看 --prod-weight 步",
    }


def check_moneyflow_d2_hint() -> dict:
    """只读 sidecar/日志提示，不加载 600MB+ parquet 全文。"""
    pit = ROOT / "data/v2/moneyflow/moneyflow_stock_daily_pit.parquet"
    log = ROOT / "logs/moneyflow_stock_loop.log"
    out: dict = {
        "ok": False,
        "path": str(pit),
        "exists": pit.is_file(),
        "alpha_status_doc": "docs/v2/ALPHA_DATA_D1D4_STATUS_ACCEPT_ZH.md",
        "verdict": "进行中 · 不 ACCEPT（Alpha）",
        "blocker_owner": "Data",
    }
    if pit.is_file():
        out["size_mb"] = round(pit.stat().st_size / (1024 * 1024), 1)
        try:
            import pyarrow.parquet as pq
            import pyarrow.compute as pc

            pf = pq.ParquetFile(pit)
            out["n_rows_meta"] = pf.metadata.num_rows
            nrg = pf.metadata.num_row_groups
            # 轻量：只读最后一个 row group 的 trade_date（ParquetFile.read_row_group）
            if nrg > 0:
                last = pf.read_row_group(nrg - 1, columns=["trade_date"])
                col = last.column(0)
                out["trade_date_max_last_rg"] = str(pc.max(col).as_py())
                out["trade_date_min_last_rg"] = str(pc.min(col).as_py())
        except Exception as e:  # noqa: BLE001
            out["parquet_probe_error"] = f"{type(e).__name__}:{e}"
    if log.is_file():
        try:
            lines = log.read_text(encoding="utf-8", errors="replace").splitlines()
            tail = [ln for ln in lines[-40:] if ln.strip()]
            out["log_tail"] = tail[-8:]
            for ln in reversed(tail):
                if "REBUILD ok" in ln or "remaining=" in ln or "missing=" in ln:
                    out["log_signal"] = ln.strip()
                    break
        except Exception as e:  # noqa: BLE001
            out["log_error"] = str(e)
    # 明确：未到最新且 Alpha 未 ACCEPT → 研究闭环可绕开 moneyflow 主依赖，但资金流叶不可当满样本
    out["ok"] = False  # 故意：D2 未 ACCEPT 不算通
    out["consume_rule_zh"] = "未 ACCEPT 前勿当满样本；G1G5/非 moneyflow 机制日更可独立 dry-run"
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="RT loop health + dry-run (no orders)")
    ap.add_argument("--data-api", default=DEFAULT_DATA_API)
    ap.add_argument("--prod-weight", type=Path, default=DEFAULT_PROD_WEIGHT)
    ap.add_argument("--skip-skeleton", action="store_true")
    ap.add_argument("--skip-d2-probe", action="store_true")
    ap.add_argument("--capital", type=int, default=600_000, choices=[600_000, 1_000_000])
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=ROOT / "output" / "v3" / "rt_loop_dryrun",
    )
    args = ap.parse_args(argv)

    out_dir: Path = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    report: dict = {
        "title": "研究级实时闭环（不下单）health + dry-run",
        "recorded_at_et": _now_et(),
        "promotion_approved": False,
        "strategy_promotion_approved": False,
        "no_orders": True,
        "no_uvicorn_start": True,
        "no_gp": True,
        "aum_report_cny": [600_000, 1_000_000],
        "capital_this_run": int(args.capital),
        "checks": {},
    }

    report["checks"]["data_api_health"] = check_data_api(args.data_api)
    report["checks"]["weight_contract"] = check_weight_contract()
    report["checks"]["prod_weight_validate"] = validate_prod_weight(Path(args.prod_weight))
    if not args.skip_d2_probe:
        report["checks"]["moneyflow_d2_hint"] = check_moneyflow_d2_hint()
    if not args.skip_skeleton:
        report["checks"]["skeleton_e2e"] = run_skeleton_light(out_dir, capital=args.capital)

    # 总闸：Data API + 契约 + 生产权重可消费 +（可选）skeleton
    c = report["checks"]
    core_ok = (
        bool(c["data_api_health"].get("ok"))
        and bool(c["weight_contract"].get("ok"))
        and bool(c["prod_weight_validate"].get("ok"))
    )
    sk = c.get("skeleton_e2e")
    if sk is not None:
        core_ok = core_ok and bool(sk.get("ok"))
    report["ok"] = core_ok
    report["elapsed_sec"] = round(time.time() - t0, 3)

    # 未通 Top（可执行）
    blockers = []
    if not c["data_api_health"].get("ok"):
        blockers.append(
            {
                "id": "data_api_8787",
                "owner": c["data_api_health"].get("blocker_owner", "Data"),
                "one_liner": "local data API /health 不可达",
            }
        )
    d2 = c.get("moneyflow_d2_hint")
    if d2 is not None and not d2.get("ok"):
        blockers.append(
            {
                "id": "moneyflow_d2_accept",
                "owner": "Data → Alpha ACCEPT",
                "one_liner": "moneyflow 仍在拉/未 ACCEPT；勿当满样本",
                "signal": d2.get("log_signal") or d2.get("trade_date_max_last_rg"),
            }
        )
    blockers.append(
        {
            "id": "debate_approve_to_evolve_queue",
            "owner": "Eng/AI（二期）",
            "one_liner": "辩论 approve_research → factor_evolve 队列尚未自动入（见 TA_QUANTMIND_FUSION §3.3）",
        }
    )
    blockers.append(
        {
            "id": "factory_main_loop_freeze",
            "owner": "QuantLab AI（已另派两叶）",
            "one_liner": "真工厂主循环仍冻在交接点；下一正交叶需 AI 解冻产出新 X2",
        }
    )
    report["unblocked_top"] = blockers[:3] if not core_ok else blockers[:3]
    # 命名：始终给出「仍卡」清单（成功也不假装 D2/工厂已通）
    report["still_blocked_top3"] = blockers[:3]

    report["commands"] = {
        "health_dryrun": "PYTHONPATH=. /workspace/qlvenv/bin/python scripts/rt_loop_health_dryrun.py",
        "health_only": "PYTHONPATH=. /workspace/qlvenv/bin/python scripts/rt_loop_health_dryrun.py --skip-skeleton",
        "skeleton_smoke": "PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.cli skeleton-smoke",
        "factor_evolve_smoke": "PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.cli factor-evolve --smoke",
        "trading_loop_stub": "PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.cli trading-loop --session 2024-07-01 --instrument 510500.SH",
        "book_smoke_skip": "PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.cli book-smoke --skip-run",
        "weight_handshake": (
            "PYTHONPATH=. /workspace/qlvenv/bin/python -c "
            "\"from quantlab.platform.weight_long_table import schema_handshake; print(schema_handshake())\""
        ),
        "data_api_health": f"curl -sS --max-time 3 {args.data_api.rstrip('/')}/health",
    }

    out_json = out_dir / "rt_loop_health_dryrun_summary.json"
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"ok": report["ok"], "summary": str(out_json), "elapsed_sec": report["elapsed_sec"], "still_blocked_top3": [b["id"] for b in report["still_blocked_top3"]]}, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
