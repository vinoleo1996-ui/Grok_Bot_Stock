# Static (AST) import closure of the paper path; imports nothing.
import ast, hashlib, json, sys
from pathlib import Path
ROOT = Path("/workspace/QuantLab")
ENTRY = ["quantlab/cli.py", "quantlab/portfolio/research_loop.py", "quantlab/portfolio/b4_paper.py",
         "quantlab/portfolio/paper_track.py", "quantlab/portfolio/book_smoke.py", "quantlab/portfolio/scorecard.py",
         "quantlab/portfolio/trade_calendar.py", "research/capacity_adv_paper_extend.py", "research/b4_paper_extend.py",
         "research/s6_paper_extend.py", "research/g1g5_capacity_adv_weights.py", "research/g1g5_earnings_event_weights.py",
         "research/g1g5_insider_increase_weights.py", "research/g1g5_equity_incentive_weights.py"]
def resolve(mod):
    parts = mod.split(".")
    if parts[0] not in ("quantlab", "research", "scripts_eng"): return []
    out = []
    for k in range(len(parts), 0, -1):
        base = ROOT.joinpath(*parts[:k])
        for c in (base.with_suffix(".py"), base / "__init__.py"):
            if c.exists(): out.append(c)
        if out: break
    # package __init__ chain
    for k in range(1, len(parts)):
        i = ROOT.joinpath(*parts[:k]) / "__init__.py"
        if i.exists(): out.append(i)
    return out
seen, todo = set(), [ROOT / e for e in ENTRY if (ROOT / e).exists()]
while todo:
    f = todo.pop()
    if f in seen: continue
    seen.add(f)
    try: tree = ast.parse(f.read_text())
    except Exception: continue
    for n in ast.walk(tree):
        mods = []
        if isinstance(n, ast.Import): mods = [a.name for a in n.names]
        elif isinstance(n, ast.ImportFrom) and n.module and n.level == 0:
            mods = [n.module] + [f"{n.module}.{a.name}" for a in n.names]
        for m in mods:
            for r in resolve(m):
                if r not in seen: todo.append(r)
rows = sorted((str(p.relative_to(ROOT)), hashlib.sha256(p.read_bytes()).hexdigest()) for p in seen)
json.dump(rows, open(sys.argv[1], "w"), indent=0)
print(len(rows))
