#!/bin/bash
# SYNTHETIC ONLY — do NOT point at leaf25/27 probes or consume .ok.
# Sketch harness for Arch/AI to prove C5 tighten A+B (and C symlink) without real runs.
# Usage (after Arch pins or for local draft dry-run under /tmp logdir/outdir):
#   ./selftest_c5_tighten_synthetic.sh [path-to-draft-or-pinned-wrapper]
set -u
W="${1:-$(dirname "$0")/cmc_wrapper_v6_C5TIGHTEN.draft.sh}"
ROOT=$(mktemp -d /tmp/quantlab_c5tighten_selftest.XXXXXX)
L="$ROOT/log"; OD="$ROOT/out"; mkdir -p "$L" "$OD"
TAG=c5tighten_syn_$(date +%H%M%S)
OK="$ROOT/arch.ok"
# synthetic: allow no-guard so we don't need live stop-guard pid
printf 'allow_no_guard=true\n' > "$OK"
echo "SELFTEST_ROOT=$ROOT W=$W"
# --- Case 1: benign sleep + fd to outdir log must NOT kill long child ---
# Child: sleep 8 (assert string embedded via env wrapper? selftest disables assert unless --selftest-assert)
# We pass --selftest so cmdline assert is disabled (v5/v6 semantics).
(
  # background nuisance: repeatedly sleep while holding fd on outdir file
  : > "$OD/nuisance.log"
  ( while true; do sleep 0.2; done ) 3>>"$OD/nuisance.log" &
  NPID=$!
  "$W" --selftest --arch-ok "$OK" --no-guard --tag "$TAG" --logdir "$L" --outdir "$OD" -- \
    bash -c 'sleep 8; echo CHILD_DONE' 
  RC=$?
  kill "$NPID" 2>/dev/null || true
  echo "CASE1_RC=$RC (expect 0; not 96)"
  grep -E 'C5_SKIP|C5_HIT|WRAPPER_DONE|WRAPPER_STDOUT_LOG' /tmp/quantlab_wrapper_sampler/${TAG}_sampler.txt 2>/dev/null || true
  # note: if logdir/outdir are under /tmp not output*, v5 would also not hit fd path;
  # for A proof under output*-like paths, bind OD under a fake tree — see CASE1b comment in COVER.
) 
echo "CASE1 done under $ROOT (inspect sampler + ${L}/${TAG}_c5.txt empty?)"
echo "CASE2 (manual): start python reader of /workspace/QuantLab/data/* in other pgid; expect C5_HIT rc=96"
echo "CASE3 (manual): --c5-ignore without allow_c5_ignore in real .ok shape → refuse 91"
echo "DONE synthetic sketch; no leaf touched."
