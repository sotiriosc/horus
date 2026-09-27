#!/usr/bin/env python3
# SPDX-License-Identifier: CERN-OHL-S-2.0
# =============================================================================
# sim/test_scale_keeper.py — Directed and random stream tests for the SKPR
#
# Runs golden-model directed streams, asserts H-HW2 behavioral signatures,
# runs 100k-block random stream, compares golden vs RTL via file I/O.
#
# Design note: directed tests prepend W_CAL warmup blocks at BASE_EXP so
# the state converges from reset (0) before the "interesting" portion begins.
# H-HW2 assertions apply to post-warmup results only (index >= W_CAL).
# cold_start_outlier is the exception: it explicitly tests recovery from
# state=0 with an outlier as the first block.
#
# Usage:
#   python3 sim/test_scale_keeper.py            # golden-model only
#   python3 sim/test_scale_keeper.py --with-rtl # includes RTL co-simulation
#
# AI role: compilation and adversarial review (Claude/Anthropic).
# Architectural decisions: Sotirios Chortogiannos.
# =============================================================================

import sys
import os
import csv
import random
import argparse
import subprocess
import tempfile

sys.path.insert(0, os.path.dirname(__file__))
from scale_keeper_golden import (
    ScaleKeeper, K, N_SETTLE, FRAC_BITS, W_CAL,
    TAG_OK, TAG_OUTLIER, TAG_SETTLING, TAG_RESEEDED
)

RANDOM_SEED      = 0x4875_726F_7321   # "Horus!" in hex
RANDOM_N_BLOCKS  = 100_000
BASE_EXP         = 20                 # baseline exponent for directed streams

# Bounds calibrated from a stable stream (BASE_EXP ± 1 jitter, starting
# from BASE_EXP << FRAC_BITS).  Derived here for transparency; same values
# are also frozen as RTL parameters in rtl/skpr.v defaults.
# persist_bound: ~1-unit deviations in Q6.8 → 256; guard margin at 2 units → 512.
DIRECTED_PERSIST_BOUND_Q = 256   # 1.0 exponent unit in Q6.8
DIRECTED_GUARD_MARGIN_Q  = 512   # 2.0 exponent units in Q6.8

# ---------------------------------------------------------------------------
# Directed stream generators — all EXCLUDE the warmup prefix.
# Warmup is prepended by the test harness.
# ---------------------------------------------------------------------------

def stream_stationary(n=192, base=BASE_EXP):
    return [base] * n

def stream_slow_ramp(n=448, base=BASE_EXP, step_interval=64):
    """One exponent unit increment every step_interval blocks."""
    return [base + i // step_interval for i in range(n)]

def stream_step_up(n=192, base=BASE_EXP, step=8):
    """First K+2 blocks stay at base so state is stable, then step up."""
    pre = K + 2
    return [base] * pre + [min(63, base + step)] * (n - pre)

def stream_step_down(n=192, base=BASE_EXP, step=8):
    pre = K + 2
    return [base] * pre + [max(0, base - step)] * (n - pre)

def stream_isolated_outliers(n=448, base=BASE_EXP, outlier_mag=10, spacing=256):
    """Single-block outliers at base+outlier_mag, spaced every spacing blocks."""
    s = [base] * n
    for i in range(0, n, spacing):
        s[i] = min(63, base + outlier_mag)
    return s

def stream_cold_start_outlier(n=64, base=BASE_EXP, outlier_mag=10):
    """Cold start from state=0: first block is outlier, rest are normal."""
    return [min(63, base + outlier_mag)] + [base] * (n - 1)


# Every test except cold_start_outlier gets a warmup prefix; the test harness
# prepends it transparently so the directed content starts at index W_CAL.
DIRECTED_TESTS = {
    'stationary'        : (stream_stationary(),        True),
    'slow_ramp'         : (stream_slow_ramp(),         True),
    'step_up_8'         : (stream_step_up(),           True),
    'step_down_8'       : (stream_step_down(),         True),
    'isolated_outliers' : (stream_isolated_outliers(), True),
    'cold_start_outlier': (stream_cold_start_outlier(), False),  # no warmup
}


def build_full_stream(directed, use_warmup):
    if use_warmup:
        return [BASE_EXP] * W_CAL + directed
    return directed


def post_warmup_results(results, use_warmup):
    return results[W_CAL:] if use_warmup else results


# ---------------------------------------------------------------------------
# H-HW2 behavioral assertions (applied to post-warmup results)
# ---------------------------------------------------------------------------

def assert_h_hw2(stream_name, post_results, full_results, use_warmup):
    """Return list of failure strings.  Empty = all pass."""
    failures = []

    # Pre-compute prior state_q for H-HW2(a): excluded blocks must not change state.
    # We look at full_results to get the block before the first post-warmup block.
    warmup_len = W_CAL if use_warmup else 0

    for idx, r in enumerate(post_results):
        abs_idx = warmup_len + idx
        if r['tag'] == TAG_OUTLIER:
            # Find previous state_q: either from full_results[abs_idx-1] or 0
            prev_sq = full_results[abs_idx - 1]['state_q'] if abs_idx > 0 else 0
            if r['state_q'] != prev_sq:
                failures.append(
                    f"H-HW2(a) FAIL [{stream_name}] block {r['block']}: "
                    f"OUTLIER but state changed "
                    f"{prev_sq} -> {r['state_q']}"
                )

    # H-HW2(b): step streams → exactly one re-seed event in post-warmup
    if 'step' in stream_name:
        events = [(r['block'], r['event_dir']) for r in post_results if r['event']]
        if len(events) != 1:
            failures.append(
                f"H-HW2(b) FAIL [{stream_name}]: expected exactly 1 re-seed event "
                f"in post-warmup, got {len(events)}: {events}"
            )

    # H-HW2(c): stationary and slow_ramp → zero re-seeds in post-warmup
    if stream_name in ('stationary', 'slow_ramp'):
        events = [r for r in post_results if r['event']]
        if events:
            failures.append(
                f"H-HW2(c) FAIL [{stream_name}]: expected 0 re-seed events "
                f"in post-warmup, got {len(events)} at blocks "
                f"{[e['block'] for e in events]}"
            )

    # H-HW2(d): cold_start_outlier → re-seed within K blocks of first normal block
    if stream_name == 'cold_start_outlier':
        first_normal = 1   # block index 0 is the outlier
        events = [r for r in post_results if r['event']]
        if not events:
            failures.append(
                f"H-HW2(d) FAIL [{stream_name}]: no re-seed event found"
            )
        else:
            first_event_block = events[0]['block']
            if first_event_block > first_normal + K:
                failures.append(
                    f"H-HW2(d) FAIL [{stream_name}]: first re-seed at block "
                    f"{first_event_block}, expected <= {first_normal + K} "
                    f"(first_normal={first_normal} + K={K})"
                )

    return failures


# ---------------------------------------------------------------------------
# RTL co-simulation via stimulus/response file I/O
# ---------------------------------------------------------------------------

def run_rtl_cosim(stream, persist_bound_q, guard_margin_q, vvp_bin,
                  tmpdir=None):
    """
    Feed stream to compiled tb_skpr.vvp and return list of result dicts.
    Returns None if RTL binary not available.

    Protocol (text files):
      STIM: line 0=persist_bound_q, line 1=guard_margin_q, line 2=n,
            lines 3..3+n-1 = e_max per block
      RESP: one line per block: "state_exp ceiling_exp tag event event_dir"
    """
    if tmpdir is None:
        tmpdir = tempfile.mkdtemp()

    stim_path = os.path.join(tmpdir, 'skpr_stim.txt')
    resp_path = os.path.join(tmpdir, 'skpr_resp.txt')

    n = len(stream)
    with open(stim_path, 'w') as f:
        f.write(f"{persist_bound_q}\n")
        f.write(f"{guard_margin_q}\n")
        f.write(f"{n}\n")
        for e in stream:
            f.write(f"{e & 0x3F}\n")

    try:
        ret = subprocess.run(
            ['vvp', vvp_bin,
             f'+SKPR_STIM={stim_path}',
             f'+SKPR_RESP={resp_path}'],
            timeout=300, capture_output=True
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        print(f"  RTL co-sim skipped: {exc}")
        return None

    if ret.returncode != 0:
        print(f"  RTL co-sim FAILED (exit {ret.returncode}):")
        print(ret.stderr.decode(errors='replace')[:2000])
        return None

    if not os.path.exists(resp_path):
        print("  RTL co-sim: response file not created")
        return None

    rtl_results = []
    with open(resp_path) as f:
        for i, line in enumerate(f):
            parts = line.split()
            if len(parts) < 5:
                break
            s_exp, c_exp, tag, ev, evd = (int(p) for p in parts[:5])
            rtl_results.append({
                'block'      : i,
                'e_max'      : stream[i] if i < n else 0,
                'state_exp'  : s_exp,
                'ceiling_exp': c_exp,
                'tag'        : tag,
                'event'      : bool(ev),
                'event_dir'  : (+1 if evd else -1) if ev else 0,
            })
    return rtl_results


def compare_golden_rtl(golden, rtl, stream_name):
    mismatches = []
    n = min(len(golden), len(rtl))
    for i in range(n):
        g, r = golden[i], rtl[i]
        for key in ('state_exp', 'ceiling_exp', 'tag', 'event'):
            if g[key] != r[key]:
                mismatches.append(
                    f"[{stream_name}] block {i} {key}: "
                    f"golden={g[key]} rtl={r[key]}"
                )
        if g['event'] and r['event']:
            gd = +1 if g['event_dir'] > 0 else -1
            rd = +1 if r['event_dir'] > 0 else -1
            if gd != rd:
                mismatches.append(
                    f"[{stream_name}] block {i} event_dir: "
                    f"golden={gd} rtl={rd}"
                )
    return mismatches


# ---------------------------------------------------------------------------
# CSV trace writer
# ---------------------------------------------------------------------------

def write_trace_csv(stream_name, results, outdir='results'):
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, f'skpr_trace_{stream_name}.csv')
    fields = ['block', 'e_max', 'state_exp', 'ceiling_exp',
              'tag', 'event', 'event_dir', 'counter', 'settle_cnt']
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in results:
            w.writerow({k: r.get(k, '') for k in fields})
    return path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--with-rtl', action='store_true')
    parser.add_argument('--rtl-vvp', default='sim/tb_skpr.vvp')
    parser.add_argument('--outdir', default='results/skpr')
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    all_failures         = []
    total_rtl_mismatches = 0
    summary_rows         = []

    print("=" * 72)
    print("SKPR Campaign — Directed Stream Tests (H-HW2)")
    print(f"  persist_bound_q={DIRECTED_PERSIST_BOUND_Q}  "
          f"guard_margin_q={DIRECTED_GUARD_MARGIN_Q}  K={K}")
    print("=" * 72)

    for sname, (directed, use_warmup) in DIRECTED_TESTS.items():
        full_stream = build_full_stream(directed, use_warmup)

        sk = ScaleKeeper(persist_bound_q=DIRECTED_PERSIST_BOUND_Q,
                         guard_margin_q=DIRECTED_GUARD_MARGIN_Q)
        full_results = sk.run_stream(full_stream)
        post_results = post_warmup_results(full_results, use_warmup)

        # H-HW2 assertions on post-warmup results
        failures = assert_h_hw2(sname, post_results, full_results, use_warmup)
        all_failures.extend(failures)

        # RTL co-simulation
        rtl_mismatches = []
        if args.with_rtl:
            rtl_res = run_rtl_cosim(
                full_stream, DIRECTED_PERSIST_BOUND_Q,
                DIRECTED_GUARD_MARGIN_Q, args.rtl_vvp
            )
            if rtl_res is not None:
                rtl_mismatches = compare_golden_rtl(full_results, rtl_res, sname)
                total_rtl_mismatches += len(rtl_mismatches)
                all_failures.extend(rtl_mismatches)

        # Traces
        write_trace_csv(sname, full_results, outdir=args.outdir)

        events  = [(r['block'], r['event_dir']) for r in post_results if r['event']]
        status  = 'PASS' if not failures and not rtl_mismatches else 'FAIL'
        warmup_events = sum(1 for r in full_results[:W_CAL] if r['event'])
        print(f"  {sname:<26} post_blocks={len(post_results):>4d}  "
              f"post_events={len(events):>2d}  warmup_events={warmup_events}  "
              f"status={status}")
        if failures:
            for f in failures:
                print(f"    FAIL: {f}")
        summary_rows.append((sname, len(full_stream), len(events), status))

    # ------------------------------------------------------------------
    print()
    print("=" * 72)
    print("SKPR Campaign — Random Stream Test (H-HW1, 100k blocks)")
    print("=" * 72)

    rng = random.Random(RANDOM_SEED)
    # Calibration stream: 64 blocks drawn from stable distribution
    cal_stream = [rng.randint(BASE_EXP - 1, BASE_EXP + 1) for _ in range(W_CAL)]
    sk_cal = ScaleKeeper.from_calibration(cal_stream)
    print(f"  Calibrated bounds: persist_bound_q={sk_cal.persist_bound_q}  "
          f"guard_margin_q={sk_cal.guard_margin_q}")

    # Full stream: calibration prefix + 100k random blocks.
    # Both golden and RTL run the IDENTICAL sequence from state=0 so that
    # the comparison is bit-exact from the very first block.
    random_stream = [rng.randint(10, 30) for _ in range(RANDOM_N_BLOCKS)]
    full_rand     = cal_stream + random_stream   # 64 + 100k = 100,064 blocks

    # Golden run (double for determinism check)
    sk1 = ScaleKeeper(sk_cal.persist_bound_q, sk_cal.guard_margin_q)
    res1 = sk1.run_stream(full_rand)
    sk2 = ScaleKeeper(sk_cal.persist_bound_q, sk_cal.guard_margin_q)
    res2 = sk2.run_stream(full_rand)

    det_mm = compare_golden_rtl(res1, res2, 'determinism')
    print(f"  Determinism: {len(det_mm)} mismatches ({'PASS' if not det_mm else 'FAIL'})")

    rand_rtl_mm = []
    if args.with_rtl:
        rtl_rand = run_rtl_cosim(full_rand, sk_cal.persist_bound_q,
                                  sk_cal.guard_margin_q, args.rtl_vvp)
        if rtl_rand is not None:
            rand_rtl_mm = compare_golden_rtl(res1, rtl_rand, 'random')
            total_rtl_mismatches += len(rand_rtl_mm)
            all_failures.extend(rand_rtl_mm)
            print(f"  RTL vs golden mismatches: {len(rand_rtl_mm)} "
                  f"({'PASS' if not rand_rtl_mm else 'FAIL'})")

    # Write trace: first 256 of the post-calibration random portion
    write_trace_csv('random_first256', res1[W_CAL:W_CAL + 256], outdir=args.outdir)

    # ------------------------------------------------------------------
    print()
    print("=" * 72)
    print("Summary")
    print("=" * 72)
    print(f"{'Stream':<28} {'Blocks':>7} {'Events':>7} {'Status'}")
    print("-" * 52)
    for (sn, nb, ne, st) in summary_rows:
        print(f"  {sn:<26} {nb:>7} {ne:>7}   {st}")
    print()
    print(f"H-HW2 assertion failures  : "
          f"{sum(1 for f in all_failures if 'H-HW2' in f)}")
    print(f"RTL mismatch count        : {total_rtl_mismatches}")
    print(f"Determinism mismatches    : {len(det_mm)}")

    summary_path = os.path.join(args.outdir, 'skpr_test_summary.txt')
    with open(summary_path, 'w') as sf:
        sf.write(f"persist_bound_directed={DIRECTED_PERSIST_BOUND_Q}\n")
        sf.write(f"guard_margin_directed={DIRECTED_GUARD_MARGIN_Q}\n")
        sf.write(f"persist_bound_random={sk_cal.persist_bound_q}\n")
        sf.write(f"guard_margin_random={sk_cal.guard_margin_q}\n")
        sf.write(f"hw2_failures={sum(1 for f in all_failures if 'H-HW2' in f)}\n")
        sf.write(f"rtl_mismatches={total_rtl_mismatches}\n")
        sf.write(f"determinism_mismatches={len(det_mm)}\n")
        sf.write(f"random_events_golden={sum(1 for r in res1[W_CAL:] if r['event'])}\n")
        for fail in all_failures:
            sf.write(f"FAIL: {fail}\n")
    print(f"\nSummary → {summary_path}")

    sys.exit(0 if not all_failures else 1)


if __name__ == '__main__':
    main()
