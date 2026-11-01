"""Arch：列出 2026-10-15 05:20 ET 之后 mtime 的文件（排除 .git / node_modules），按顶层目录归并并推断 owner。只读。"""
import os, re, datetime as dt, collections, csv
CUT = dt.datetime(2026, 10, 15, 5, 20)  # box 本地时区 = ET
ROOTS = ['/workspace/QuantLab', '/workspace/quantlab-web']
def owner(root, rel):
    p = rel
    if root.endswith('quantlab-web'):
        if p.startswith('events/'): return 'Web(ql_bus 事件总线，多 agent 写入)'
        return 'Web'
    if '__pycache__' in p or p.startswith('.venv_opt/'): return '环境(.pyc 重编译，非产出)'
    if p.startswith('docs/v2/audit/') or os.path.basename(p).startswith('ARCH_'): return 'Arch'
    b = os.path.basename(p)
    if p.startswith('output/loop/TEAM_STATE'): return '共享(TEAM_STATE)'
    if p.startswith('output/loop/paper_daily') or p.startswith('scripts_eng/') or b.startswith('ENG_') or '/MANIFEST.json' in p: return 'Eng'
    if p.startswith('output/strategy_optimizer/core_x2/c5_'): return 'Eng'
    if p.startswith('output/d1/supervise'): return '主 Agent'
    if p.startswith(('data/', 'logs/', 'output/data_v2_bundle', 'output/daily_update_status', 'output/relay_health', 'output/d1/hsgt', 'scripts/acquire')): return 'Data'
    if p.startswith(('output/ai_factory', 'research/g1g5', 'research/ai_')) or b.startswith('AI_'): return 'AI'
    if p.startswith(('output/alpha', 'research/alpha_')) or b.startswith('ALPHA_') or p == 'output/loop/alpha_labels.json': return 'Alpha'
    if p.startswith(('output/intel', 'research/intel')) or b.startswith('INTEL_'): return 'Intel'
    if p.startswith(('output/strategy', 'research/optimizer_', 'research/strategy_')) or b.startswith(('STRATEGY_', 'S2_')): return 'Strategy'
    if p.startswith(('output/beta', 'research/beta_')) or b.startswith('BETA_'): return 'Beta'
    if p == 'research/run_rss_guard.sh': return '未定(无署名，疑 AI/主 Agent 串行守护)'
    return '未定'
rows = []
for root in ROOTS:
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in ('.git', 'node_modules')]
        for f in fns:
            fp = os.path.join(dp, f)
            try: m = dt.datetime.fromtimestamp(os.lstat(fp).st_mtime)
            except OSError: continue
            if m > CUT:
                rel = os.path.relpath(fp, root)
                top = rel.split('/')[0] if '/' in rel else '(根)'
                sub = '/'.join(rel.split('/')[:2]) if rel.count('/') >= 2 else rel
                rows.append((os.path.basename(root), top, sub, owner(root, rel), m, rel))
out = '/workspace/QuantLab/docs/v2/audit/arch_activity_since_20261015.csv'
with open(out, 'w', newline='') as fh:
    w = csv.writer(fh); w.writerow(['repo', 'top', 'sub', 'owner', 'mtime_et', 'path'])
    for r in sorted(rows, key=lambda r: r[4]): w.writerow([r[0], r[1], r[2], r[3], r[4].strftime('%Y-%m-%d %H:%M:%S'), r[5]])
G = collections.defaultdict(list)
for r in rows: G[(r[0], r[1], r[3])].append(r)
print('total', len(rows), 'earliest', min(r[4] for r in rows), 'latest', max(r[4] for r in rows))
for k in sorted(G):
    v = sorted(G[k], key=lambda r: r[4]); reps = [x[5] for x in v if '__pycache__' not in x[5]][-3:] or [v[-1][5]]
    print('|'.join([k[0], k[1], k[2], str(len(v)), v[0][4].strftime('%m-%d %H:%M'), v[-1][4].strftime('%m-%d %H:%M'), '; '.join(reps)]))
O = collections.defaultdict(list)
for r in rows: O[r[3]].append(r[4])
print('--- by owner')
for k, v in sorted(O.items()): print(k, len(v), min(v).strftime('%m-%d %H:%M'), max(v).strftime('%m-%d %H:%M'))
