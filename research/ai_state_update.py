"""Append/replace a ledger row and replace only the '### AI' section of TEAM_STATE (≤5 lines). Usage: python3 ai_state_update.py <row_md_file|-> <ai_section_file>"""
import sys, re, os
from pathlib import Path
R = Path(__file__).resolve().parents[1]
L = R/"docs/v2/AI_LEAF_LEDGER_ZH.md"; T = R/"output/loop/TEAM_STATE_latest.md"
row = None if sys.argv[1] == "-" else Path(sys.argv[1]).read_text().strip()
if row:
    txt = L.read_text(); num = row.split("|")[1].strip()
    lines = txt.split("\n"); idx = [i for i, l in enumerate(lines) if re.match(rf"^\|\s*{re.escape(num)}\s*\|", l)]
    if idx: lines[idx[0]] = row
    else:
        anchor = [i for i, l in enumerate(lines) if re.match(r"^\|\s*(18v|18|19|20)\s*\|", l)]
        lines.insert(anchor[-1]+1, row)
    tmp = L.with_suffix(".tmp"); tmp.write_text("\n".join(lines)); os.replace(tmp, L)
sec = Path(sys.argv[2]).read_text().strip().split("\n"); assert len(sec) <= 6, "AI section ≤5 lines + header"
t = T.read_text().split("\n")
hs = [i for i, l in enumerate(t) if l.strip() in ("### AI", "### QuantLab AI")]
if hs:
    s = hs[0]; e = s+1
    while e < len(t) and not t[e].startswith("#"): e += 1
    t[s:e] = sec + [""]
else:
    k = [i for i, l in enumerate(t) if l.startswith("## 各 agent 小节")][0]; t[k+1:k+1] = sec + [""]
tmp = T.with_suffix(".tmp"); tmp.write_text("\n".join(t)); os.replace(tmp, T); print("updated")
