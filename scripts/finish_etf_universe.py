#!/usr/bin/env python3
"""Finish equity ETF daily panel from Tencent (resume-friendly)."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
# reuse acquire module functions by exec
import runpy
# Call main of acquire_v2_gap_etf — it resumes from archived raw JSON
runpy.run_path(str(Path(__file__).resolve().parents[1] / 'scripts' / 'acquire_v2_gap_etf.py'), run_name='__main__')
