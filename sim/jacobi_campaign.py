#!/usr/bin/env python3
"""
sim/jacobi_campaign.py — Run the pre-registered Jacobi falsification matrix.

Pre-registered criteria and matrix: docs/JACOBI_HYPOTHESIS.md (binding).

Runs the frozen matrix (§7):
  * Diagonally dominant random   N ∈ {8, 32, 128}, 1000 trials each  (K1 set)
  * Ill-conditioned (κ-swept, DD) N = 32, κ ∈ {1e1..1e6}, 100 trials each
  * Laplacian / Poisson 1D        N ∈ {8, 32, 128}, 100 trials each   (K2 stress)

Emits:
  sim/JACOBI_RESULTS.csv   one row per (system, N, κ_target, trial, format)
  sim/JACOBI_SUMMARY.log   one block per K-criterion, PASS/FAIL, numbers cited

Seed policy (§7):  seed(sys, N, trial) = SEED_JACOBI ^ (SYS_ID<<24)
                   ^ (N<<8) ^ trial  [ ^ (kappa_index<<20) for ill-conditioned ].
numpy only; no format re-implemented (see jacobi_solver.py preflight).
"""

import argparse
import csv
import math
import os
import sys
import time

import numpy as np

DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, DIR)

import jacobi_solver as J   # noqa: E402

SEED_JACOBI = 0x4AC0B1A5    # master seed (§7)
SYS_ID = {"dd_random": 0, "illcond": 1, "laplacian": 2}
KAPPA_TARGETS = [1e1, 1e2, 1e3, 1e4, 1e6]

RESULTS_CSV = os.path.join(DIR, "JACOBI_RESULTS.csv")
SUMMARY_LOG = os.path.join(DIR, "JACOBI_SUMMARY.log")

CSV_FIELDS = [
    "system", "N", "kappa_target", "trial", "seed", "kappa",
    "format", "fp64_converged", "converged", "diverged", "overflow",
    "n_iter", "final_rho", "sol_err", "n_fp64_matched", "tau_f",
]


def _seed(sys_name, N, trial, kappa_index=0):
    s = SEED_JACOBI ^ (SYS_ID[sys_name] << 24) ^ (N << 8) ^ trial
    if sys_name == "illcond":
        s ^= (kappa_index << 20)
    return s & 0xFFFFFFFF


# ── Trial matrix definition (frozen) ────────────────────────────────────────────

def _matrix_plan(quick=False):
    """Yield (system, N, kappa_target, n_trials, kappa_index) cells."""
    dd_trials  = 40 if quick else 1000
    aux_trials = 10 if quick else 100
    for N in (8, 32, 128):
        yield ("dd_random", N, None, dd_trials, 0)
    for ki, kt in enumerate(KAPPA_TARGETS):
        yield ("illcond", 32, kt, aux_trials, ki)
    for N in (8, 32, 128):
        yield ("laplacian", N, None, aux_trials, 0)


def _make_system(sys_name, N, rng, kappa_target):
    if sys_name == "dd_random":
        return J.make_dd_random(N, rng)
    if sys_name == "illcond":
        return J.make_illcond_dd(N, rng, kappa_target)
    if sys_name == "laplacian":
        return J.make_laplacian_1d(N, rng)
    raise ValueError(sys_name)


# ── Run one cell ────────────────────────────────────────────────────────────────

def run_cell(sys_name, N, kappa_target, n_trials, kappa_index, writer):
    """Run all trials × formats in one cell; stream rows to the CSV writer."""
    rows_written = 0
    for trial in range(n_trials):
        seed = _seed(sys_name, N, trial, kappa_index)
        rng = np.random.default_rng(seed)
        A, b = _make_system(sys_name, N, rng, kappa_target)
        kappa = J.cond_inf(A)

        ref = J.solve_fp64(A, b)
        fp64_conv = J.first_leq(ref["rhos"], J.TAU_FP64) is not None
        x_ref = ref["x"]

        for fmt in J.FORMATS:
            if fmt == "FP64":
                n_iter = J.first_leq(ref["rhos"], J.TAU_FP64)
                row = dict(
                    system=sys_name, N=N, kappa_target=kappa_target, trial=trial,
                    seed=seed, kappa=kappa, format=fmt,
                    fp64_converged=fp64_conv, converged=fp64_conv,
                    diverged=False, overflow=False, n_iter=n_iter,
                    final_rho=ref["rhos"][-1] if ref["rhos"] else float("nan"),
                    sol_err=0.0, n_fp64_matched=n_iter, tau_f=J.TAU_FP64,
                )
            else:
                r = J.solve_format(A, b, fmt)
                # FP64 iterations to reach THIS format's tolerance (matched, K2).
                n_matched = J.first_leq(ref["rhos"], J.tau(fmt))
                sol_err = J.rel_sol_error(r["x"], x_ref)
                row = dict(
                    system=sys_name, N=N, kappa_target=kappa_target, trial=trial,
                    seed=seed, kappa=kappa, format=fmt,
                    fp64_converged=fp64_conv, converged=r["converged"],
                    diverged=r["diverged"], overflow=r["overflow"],
                    n_iter=r["n_iter"], final_rho=r["final_rho"],
                    sol_err=sol_err, n_fp64_matched=n_matched, tau_f=J.tau(fmt),
                )
            writer.writerow(row)
            rows_written += 1
    return rows_written


# ── CSV loading for criteria evaluation ─────────────────────────────────────────

def _load_rows(path):
    rows = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            rows.append(r)
    return rows


def _to_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return float("nan")


def _to_int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _bool(v):
    return str(v) == "True"


def _median(xs):
    xs = sorted(xs)
    n = len(xs)
    if n == 0:
        return float("nan")
    return xs[n // 2] if n % 2 else 0.5 * (xs[n // 2 - 1] + xs[n // 2])


def _pct(xs, p):
    xs = sorted(xs)
    if not xs:
        return float("nan")
    return xs[min(len(xs) - 1, int(p * len(xs)))]


def _mean_std(xs):
    if not xs:
        return float("nan"), float("nan")
    m = sum(xs) / len(xs)
    if len(xs) < 2:
        return m, 0.0
    return m, math.sqrt(sum((x - m) ** 2 for x in xs) / len(xs))


def _cp95_upper(n_trials, n_fail):
    """95% Clopper-Pearson upper bound (numpy-only; exact for 0 failures)."""
    if n_trials == 0:
        return float("nan")
    if n_fail == 0:
        return 1.0 - 0.05 ** (1.0 / n_trials)
    # Bisection on the regularized incomplete beta via a normal-free numeric CDF
    # is avoided; for nonzero failures use a conservative Wilson upper bound.
    from math import sqrt
    z = 1.959963984540054
    phat = n_fail / n_trials
    denom = 1 + z * z / n_trials
    centre = phat + z * z / (2 * n_trials)
    half = z * sqrt(phat * (1 - phat) / n_trials + z * z / (4 * n_trials * n_trials))
    return (centre + half) / denom


# ── K-criteria evaluation ────────────────────────────────────────────────────────

def eval_criteria(rows):
    """Compute K1..K4 verdicts from the CSV rows.  Returns a dict."""
    out = {}

    def sel(**kw):
        res = rows
        for k, v in kw.items():
            res = [r for r in res if r[k] == str(v)]
        return res

    # ── K1: E3M6+block convergence on DD cells where FP64 converges ──────────
    dd = [r for r in rows if r["system"] == "dd_random"]
    per_size = {}
    tot_denom = tot_fail = 0
    for N in (8, 32, 128):
        fp64 = [r for r in dd if r["N"] == str(N) and r["format"] == "FP64"
                and _bool(r["fp64_converged"])]
        keys = {r["trial"] for r in fp64}
        e3 = [r for r in dd if r["N"] == str(N) and r["format"] == "E3M6+block"
              and r["trial"] in keys]
        denom = len(e3)
        conv = sum(1 for r in e3 if _bool(r["converged"]))
        fail = denom - conv
        per_size[N] = (conv, denom)
        tot_denom += denom
        tot_fail += fail
    rate = (tot_denom - tot_fail) / tot_denom if tot_denom else float("nan")
    cp95 = _cp95_upper(tot_denom, tot_fail)
    out["K1"] = {
        "per_size": per_size, "pooled_conv": tot_denom - tot_fail,
        "pooled_denom": tot_denom, "rate": rate, "cp95_ub": cp95,
        "pass": (rate >= 0.999) and (cp95 <= 1e-3),
    }

    # ── K2: iteration penalty at matched tolerance (DD + Laplacian) ──────────
    k2_sizes = {}
    k2_pass = True
    for sysn in ("dd_random", "laplacian"):
        for N in (8, 32, 128):
            e3 = [r for r in rows if r["system"] == sysn and r["N"] == str(N)
                  and r["format"] == "E3M6+block" and _bool(r["converged"])
                  and _to_int(r["n_fp64_matched"]) is not None]
            n_fmt = [_to_int(r["n_iter"]) for r in e3]
            n_ref = [_to_int(r["n_fp64_matched"]) for r in e3]
            if not n_fmt:
                k2_sizes[(sysn, N)] = None
                continue
            m_fmt, m_ref = _median(n_fmt), _median(n_ref)
            ratio = m_fmt / m_ref if m_ref else float("inf")
            k2_sizes[(sysn, N)] = {
                "n": len(n_fmt), "med_fmt": m_fmt, "med_ref": m_ref,
                "ratio": ratio, "pass": ratio <= 1.5,
            }
            if ratio > 1.5:
                k2_pass = False
    out["K2"] = {"sizes": k2_sizes, "pass": k2_pass}

    # ── K3: solution inside quantization envelope (DD cells) ─────────────────
    e3 = [r for r in dd if r["format"] == "E3M6+block" and _bool(r["converged"])
          and _bool(r["fp64_converged"])]
    u = J.UNIT_ROUNDOFF["E3M6+block"]
    ratios = []
    for r in e3:
        kappa = _to_float(r["kappa"])
        env = J.C_ENV * kappa * u
        if env > 0 and math.isfinite(env):
            ratios.append(_to_float(r["sol_err"]) / env)
    med_ratio = _median(ratios)
    p95_ratio = _pct(ratios, 0.95)
    out["K3"] = {
        "n": len(ratios), "med_ratio": med_ratio, "p95_ratio": p95_ratio,
        "median_serr": _median([_to_float(r["sol_err"]) for r in e3]),
        "pass": (med_ratio <= 1.0) and (p95_ratio <= 2.0),
    }

    # ── K4: E3M6+block vs FP8-E4M3 on three axes, per cell ───────────────────
    def cells():
        for N in (8, 32, 128):
            yield ("dd_random", N, None)
        for kt in KAPPA_TARGETS:
            yield ("illcond", 32, kt)
        for N in (8, 32, 128):
            yield ("laplacian", N, None)

    k4_wins = []          # (cell, axis, detail)
    k4_table = []
    for (sysn, N, kt) in cells():
        def cellrows(fmt):
            return [r for r in rows if r["system"] == sysn and r["N"] == str(N)
                    and (kt is None or r["kappa_target"] == str(kt))
                    and r["format"] == fmt]
        e3_all, e4_all = cellrows("E3M6+block"), cellrows("FP8-E4M3")
        fp64 = [r for r in cellrows("FP64") if _bool(r["fp64_converged"])]
        denom = len(fp64)
        # axis (a) convergence rate among FP64-converged trials
        keys = {r["trial"] for r in fp64}
        e3c = sum(1 for r in e3_all if r["trial"] in keys and _bool(r["converged"]))
        e4c = sum(1 for r in e4_all if r["trial"] in keys and _bool(r["converged"]))
        rate3 = e3c / denom if denom else float("nan")
        rate4 = e4c / denom if denom else float("nan")
        # axis (b) iteration count (converged), lower better
        n3 = [_to_int(r["n_iter"]) for r in e3_all if _bool(r["converged"])]
        n4 = [_to_int(r["n_iter"]) for r in e4_all if _bool(r["converged"])]
        m3n, s3n = _mean_std(n3)
        m4n, s4n = _mean_std(n4)
        # axis (c) solution accuracy (converged), lower sol_err better
        a3 = [_to_float(r["sol_err"]) for r in e3_all if _bool(r["converged"])]
        a4 = [_to_float(r["sol_err"]) for r in e4_all if _bool(r["converged"])]
        m3a, s3a = _mean_std(a3)
        m4a, s4a = _mean_std(a4)

        cell_wins = []
        # (a) higher convergence rate: strict, 2σ not defined for rate → use
        #     absolute margin > 0.001 (0.1 pp) as the "strict advantage" proxy.
        if math.isfinite(rate3) and math.isfinite(rate4) and rate3 - rate4 > 1e-3:
            cell_wins.append("convergence_rate")
        # (b) fewer iterations, 2σ-separated
        if n3 and n4 and (m4n - m3n) >= 2 * math.sqrt(s3n ** 2 + s4n ** 2) and m3n < m4n:
            cell_wins.append("iteration_count")
        # (c) lower solution error, 2σ-separated
        if a3 and a4 and (m4a - m3a) >= 2 * math.sqrt(s3a ** 2 + s4a ** 2) and m3a < m4a:
            cell_wins.append("solution_accuracy")

        cell = f"{sysn}/N={N}" + (f"/κ={kt:.0e}" if kt else "")
        k4_table.append({
            "cell": cell, "rate3": rate3, "rate4": rate4,
            "med_serr3": _median(a3), "med_serr4": _median(a4),
            "med_n3": _median([x for x in n3]) if n3 else float("nan"),
            "med_n4": _median([x for x in n4]) if n4 else float("nan"),
            "wins": cell_wins,
        })
        for w in cell_wins:
            k4_wins.append((cell, w))

    out["K4"] = {"wins": k4_wins, "table": k4_table, "pass": len(k4_wins) > 0}
    return out


# ── SUMMARY log (house style) ─────────────────────────────────────────────────

def write_summary(out, elapsed, quick):
    L = []
    def w(s=""):
        L.append(s)

    w("==================================================================")
    w("  JACOBI SOLVER FALSIFICATION CAMPAIGN — SUMMARY LOG")
    w("  Iterative relaxation as an error-forgiving arithmetic regime")
    w("  Pre-registered criteria: docs/JACOBI_HYPOTHESIS.md (binding)")
    w("  Raw data: sim/JACOBI_RESULTS.csv")
    w("==================================================================")
    w("")
    if quick:
        w("  *** QUICK MODE (reduced trials) — NOT the pre-registered run ***")
        w("")
    w(f"  Formats: {', '.join(J.FORMATS)}")
    w(f"  Constants: C_conv={J.C_CONV}  C_env={J.C_ENV}  K_MAX={J.K_MAX}  "
      f"τ_FP64={J.TAU_FP64:.0e}  γ={J.DOM_MARGIN}")
    w(f"  τ_F: " + "  ".join(f"{f}={J.tau(f):.3e}" for f in J.FORMATS if f != "FP64"))
    w(f"  Elapsed: {elapsed:.1f}s")
    w("")

    # ── K1 ────────────────────────────────────────────────────────────────
    k1 = out["K1"]
    w("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    w("K1  E3M6+block converges on ≥99.9% of DD trials where FP64 converges")
    w("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    for N in (8, 32, 128):
        c, d = k1["per_size"][N]
        w(f"  N={N:<4d}  E3M6+block converged {c}/{d} FP64-converged trials")
    w(f"  Pooled: {k1['pooled_conv']}/{k1['pooled_denom']} "
      f"= {k1['rate']*100:.4f}%   CP95 UB on failure rate = {k1['cp95_ub']:.3e}")
    w(f"  Requirement: rate ≥ 99.9% AND CP95 UB ≤ 1e-3")
    w(f"  K1: {'PASS' if k1['pass'] else 'FAIL'}")
    w("")

    # ── K2 ────────────────────────────────────────────────────────────────
    k2 = out["K2"]
    w("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    w("K2  median iterations ≤ 1.5× FP64 at matched tolerance (DD + Laplacian)")
    w("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    w(f"  {'cell':<22}{'n':>6}{'med n_E3M6':>12}{'med n_FP64':>12}{'ratio':>9}  verdict")
    for (sysn, N), v in k2["sizes"].items():
        cell = f"{sysn}/N={N}"
        if v is None:
            w(f"  {cell:<22}{'—':>6}{'—':>12}{'—':>12}{'—':>9}  no converged trials")
        else:
            w(f"  {cell:<22}{v['n']:>6}{v['med_fmt']:>12.1f}{v['med_ref']:>12.1f}"
              f"{v['ratio']:>9.2f}  {'ok' if v['pass'] else 'OVER 1.5×'}")
    w(f"  K2: {'PASS' if k2['pass'] else 'FAIL'}  (fails if any cell ratio > 1.5)")
    w("")

    # ── K3 ────────────────────────────────────────────────────────────────
    k3 = out["K3"]
    w("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    w("K3  converged E3M6+block solution inside envelope E_env = 8·κ·u  (DD)")
    w("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    w(f"  N converged DD trials scored: {k3['n']}")
    w(f"  median sol_err = {k3['median_serr']:.3e}")
    w(f"  median (sol_err / E_env) = {k3['med_ratio']:.3f}   (requirement ≤ 1.0)")
    w(f"  p95    (sol_err / E_env) = {k3['p95_ratio']:.3f}   (requirement ≤ 2.0)")
    w(f"  K3: {'PASS' if k3['pass'] else 'FAIL'}")
    w("")

    # ── K4 ────────────────────────────────────────────────────────────────
    k4 = out["K4"]
    w("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    w("K4  E3M6+block beats FP8-E4M3 on ≥1 axis in ≥1 cell (else niche dies)")
    w("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    w(f"  {'cell':<24}{'rate3':>7}{'rate4':>7}{'serr3':>11}{'serr4':>11}  wins(E3M6)")
    for t in k4["table"]:
        w(f"  {t['cell']:<24}{t['rate3']:>7.3f}{t['rate4']:>7.3f}"
          f"{t['med_serr3']:>11.3e}{t['med_serr4']:>11.3e}  "
          f"{','.join(t['wins']) if t['wins'] else '-'}")
    w("")
    if k4["wins"]:
        w(f"  E3M6+block strictly beats E4M3 on {len(k4['wins'])} (cell,axis) pairs, e.g.:")
        for cell, axis in k4["wins"][:5]:
            w(f"    - {cell}: {axis}")
    else:
        w("  E3M6+block does NOT strictly beat E4M3 on any axis in any cell.")
        w("  The relaxation-niche claim dies here (recorded, per house rules).")
    w(f"  K4: {'PASS' if k4['pass'] else 'FAIL'}")
    w("")

    # ── Verdict line ─────────────────────────────────────────────────────
    all_pass = all(out[k]["pass"] for k in ("K1", "K2", "K3", "K4"))
    w("==================================================================")
    w(f"  OVERALL: K1={'PASS' if out['K1']['pass'] else 'FAIL'}  "
      f"K2={'PASS' if out['K2']['pass'] else 'FAIL'}  "
      f"K3={'PASS' if out['K3']['pass'] else 'FAIL'}  "
      f"K4={'PASS' if out['K4']['pass'] else 'FAIL'}")
    w(f"  All K-criteria pass: {'YES' if all_pass else 'NO'} "
      f"→ Phase 3 RTL {'ELIGIBLE (await approval)' if all_pass else 'NOT eligible'}")
    w("  Verdict written to docs/JACOBI_VERDICT.md (Phase 2).")
    w("==================================================================")

    text = "\n".join(L) + "\n"
    with open(SUMMARY_LOG, "w") as f:
        f.write(text)
    print(text)


# ── Main ────────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Jacobi falsification campaign")
    ap.add_argument("--quick", action="store_true",
                    help="reduced trial counts for development (NOT pre-registered)")
    ap.add_argument("--skip-run", action="store_true",
                    help="re-evaluate criteria from an existing JACOBI_RESULTS.csv")
    args = ap.parse_args()

    t0 = time.time()
    print("=" * 66)
    print("JACOBI SOLVER FALSIFICATION CAMPAIGN")
    print("Pre-registered criteria: docs/JACOBI_HYPOTHESIS.md")
    print("=" * 66)

    print("\n[1/3] Preflight (format codecs)…")
    J.run_preflight(verbose=True)

    if not args.skip_run:
        print("\n[2/3] Running frozen matrix…")
        with open(RESULTS_CSV, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
            writer.writeheader()
            total = 0
            for (sysn, N, kt, n_tr, ki) in _matrix_plan(quick=args.quick):
                tc = time.time()
                n = run_cell(sysn, N, kt, n_tr, ki, writer)
                total += n
                tag = f"{sysn} N={N}" + (f" κ={kt:.0e}" if kt else "")
                print(f"    {tag:<28} {n_tr:>5} trials  "
                      f"({time.time()-tc:5.1f}s, {n} rows)")
        print(f"    {total} rows → {os.path.basename(RESULTS_CSV)}")
    else:
        print("\n[2/3] Skipping run; loading existing CSV.")

    print("\n[3/3] Evaluating K-criteria…")
    rows = _load_rows(RESULTS_CSV)
    out = eval_criteria(rows)
    write_summary(out, time.time() - t0, args.quick)


if __name__ == "__main__":
    main()
