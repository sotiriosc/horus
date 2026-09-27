#!/usr/bin/env python3
"""
sim/jacobi_rtl_golden.py — Phase 3 RTL second source: golden generation +
RTL-faithful (truncating) arithmetic re-validation.

docs/JACOBI_HYPOTHESIS.md §9 / docs/JACOBI_VERDICT.md "Next: RTL validation".

WHY THIS FILE EXISTS (the PATH_FAST discipline).
The Phase-1 campaign model (sim/jacobi_solver.py, family (b)) accumulates
E3M6+block products in an FP64-width accumulator and rounds only at the block
boundary (RNE via enm6_enc). The synthesizable arithmetic element
rtl/horus_e3m6_core.v does something different: it rounds EVERY product to a
6-bit mantissa by TRUNCATION (no RNE). A horus_e3m6_core-based RTL therefore
cannot be bit-identical to the campaign model — exactly the kind of gap
docs/CAMPAIGN_OVERVIEW.md §2 warns about (two agreeing software models are not a
second source; the RTL is).

This module resolves it the honest way:
  1. e3m6_core_mul() — a Python replica of rtl/horus_e3m6_core.v's TRUNCATING
     multiply, matched to the Verilog bit-for-bit (validated by tb_jacobi_e3m6).
  2. solve_e3m6_block_rtl() — an RTL-faithful Jacobi solver that uses
     e3m6_core_mul for every product (per-product truncation) and block
     re-grounding, i.e. what the hardware datapath actually computes.
  3. K-criteria re-validation under this truncating arithmetic (does the
     campaign verdict SURVIVE the real hardware arithmetic model?).
  4. Golden emission: every (a, b, product) the solver feeds through the E3M6
     core, over 200 DD N=8 solves → JACOBI_E3M6_GOLDEN.hex, replayed against
     horus_e3m6_core in tb/tb_jacobi_e3m6.v for a bit-exact R1 check.

numpy only; codecs imported from compact_nfe.py / format_zoo.py.
"""

import math
import os
import sys

import numpy as np

DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, DIR)

import jacobi_solver as J                       # noqa: E402
from jacobi_campaign import _seed               # noqa: E402
from compact_nfe import enm6_enc, enm6_dec, block_enc, BLOCK_SIZE  # noqa: E402

E3M6_N = 3
GOLDEN_HEX = os.path.join(DIR, "JACOBI_E3M6_GOLDEN.hex")


# ─────────────────────────────────────────────────────────────────────────────
# 1. Python replica of rtl/horus_e3m6_core.v (TRUNCATING multiply)
# ─────────────────────────────────────────────────────────────────────────────

def e3m6_core_mul(a_cw, b_cw):
    """Bit-exact Python replica of rtl/horus_e3m6_core.v.

    E3M6 codeword = [9]=sign, [8:6]=exp (bias 4), [5:0]=mantissa.
    Truncation (no RNE), flush-subnormal input, subnormal-output path, sat at
    e_r>7.  Mirrors the Verilog line-for-line (see horus_e3m6_core.v).
    """
    a_cw &= 0x3FF
    b_cw &= 0x3FF
    s_a, e_a, f_a = (a_cw >> 9) & 1, (a_cw >> 6) & 7, a_cw & 0x3F
    s_b, e_b, f_b = (b_cw >> 9) & 1, (b_cw >> 6) & 7, b_cw & 0x3F
    s_r = s_a ^ s_b

    if e_a == 0 or e_b == 0:              # flush_in → signed zero
        return (s_r << 9)

    m_a = 0x40 | f_a                      # {1, f}
    m_b = 0x40 | f_b
    P = m_a * m_b                         # 14-bit product
    P_msb = (P >> 13) & 1
    fr_full = (P >> 7) & 0x3F if P_msb else (P >> 6) & 0x3F

    e_sum_p = e_a + e_b + P_msb           # 2..15
    sat = e_sum_p > 11
    is_sub = (not sat) and (e_sum_p <= 4)
    is_normal = (not sat) and (e_sum_p > 4)

    if sat:
        return (s_r << 9) | (7 << 6) | 0x3F
    if is_normal:
        e_out = (e_sum_p - 4) & 7
        return (s_r << 9) | (e_out << 6) | fr_full
    if is_sub:
        sub_mant_in = 0x40 | fr_full      # 7-bit
        shift = 5 - e_sum_p               # 1..3
        f_sub = (sub_mant_in >> shift) & 0x3F
        return (s_r << 9) | (0 << 6) | f_sub
    return (s_r << 9)


def _blk_enc(values):
    """Block-encode 8 values → (codewords, block_exp).  Uses compact_nfe."""
    return block_enc(list(values), E3M6_N)


def _eff(cw, bexp):
    return enm6_dec(cw, E3M6_N) * (2.0 ** bexp)


# ─────────────────────────────────────────────────────────────────────────────
# 2. RTL-faithful E3M6+block Jacobi solver (per-product truncation)
# ─────────────────────────────────────────────────────────────────────────────

def solve_e3m6_block_rtl(A, b, k_max=J.K_MAX, early_stop=True, tap=None, mul=None):
    """Jacobi with per-product E3M6 rounding (what horus_e3m6_core computes).

    N must be a multiple of BLOCK_SIZE; validated for N=8 (single block).
    If `tap` is a list, every (a_cw, b_cw, prod_cw) fed through the product op is
    appended to it (for golden emission).
    `mul` is the per-product E3M6 multiply; defaults to the truncating core
    replica e3m6_core_mul (Phase 3 behaviour).  Phase 4a injects RNE/SR variants
    here without changing the solver — same block re-grounding, same seeds.
    """
    if mul is None:
        mul = e3m6_core_mul
    A = np.asarray(A, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    N = b.size
    assert N % BLOCK_SIZE == 0, "solver models one block per 8 elements"
    nblk = N // BLOCK_SIZE
    bnorm = np.linalg.norm(b)

    # Setup: block-encode A rows, b, and reciprocal diagonal.
    A_cw, A_be = [], []
    for i in range(N):
        cws, be = _blk_enc(A[i])
        A_cw.append(cws)
        A_be.append(be)
    b_cw, b_be = _blk_enc(b)
    diag = np.diag(A).copy()
    diag[diag == 0.0] = np.finfo(float).tiny
    di_cw, di_be = _blk_enc(1.0 / diag)

    # State x0 = 0.
    x_cw = [0] * N
    x_be = 0
    rhos = []
    overflow = False

    def rec(a, bb, p):
        if tap is not None:
            tap.append((a & 0x3FF, bb & 0x3FF, p & 0x3FF))

    for _ in range(k_max):
        # Row accumulate with per-product truncation.
        acc = np.zeros(N)
        for i in range(N):
            s = 0.0
            for j in range(N):
                if j == i:
                    continue
                p = mul(A_cw[i][j], x_cw[j])
                rec(A_cw[i][j], x_cw[j], p)
                s += enm6_dec(p, E3M6_N)
            acc[i] = s * (2.0 ** (A_be[i] + x_be))
        # r = b - acc  (FP64 combine of differing block scales; the accumulator
        # is wider than the element, per §3).
        r = np.array([_eff(b_cw[i], b_be) for i in range(N)]) - acc
        # Reciprocal multiply through the E3M6 core: encode r as a block, then
        # multiply each element by the (block-encoded) reciprocal diagonal.
        r_cw, r_be = _blk_enc(r)
        x_new = np.zeros(N)
        for i in range(N):
            p = mul(r_cw[i], di_cw[i])
            rec(r_cw[i], di_cw[i], p)
            x_new[i] = enm6_dec(p, E3M6_N) * (2.0 ** (r_be + di_be))
        # Block re-ground the new state.
        x_cw, x_be = _blk_enc(x_new)
        # Saturation sentinel check on state codewords.
        for cw in x_cw:
            if ((cw >> 6) & 7) == 7 and (cw & 0x3F) == 0x3F:
                overflow = True
        x_dec = np.array([_eff(x_cw[i], x_be) for i in range(N)])
        rhos.append(J.rel_residual(A, x_dec, b, bnorm))
        if early_stop and rhos[-1] <= J.tau("E3M6+block"):
            break

    x_dec = np.array([_eff(x_cw[i], x_be) for i in range(N)])
    n_iter = J.first_leq(rhos, J.tau("E3M6+block"))
    return {"x": x_dec, "rhos": rhos, "overflow": overflow,
            "n_iter": n_iter, "converged": (n_iter is not None) and not overflow,
            "final_rho": rhos[-1] if rhos else float("nan")}


# ─────────────────────────────────────────────────────────────────────────────
# 3. Unit test: replica vs enm6 reference structure
# ─────────────────────────────────────────────────────────────────────────────

def _unit_test_core():
    """Sanity checks on e3m6_core_mul against hand values (truncation semantics)."""
    one = (4 << 6)                 # e=4 → 1.0
    two = (5 << 6)                 # e=5 → 2.0
    four = (6 << 6)                # e=6 → 4.0
    neg1 = (1 << 9) | (4 << 6)
    assert e3m6_core_mul(two, two) == four, "2×2=4"
    assert e3m6_core_mul(one, two) == two, "1×2=2"
    assert e3m6_core_mul(neg1, one) == ((1 << 9) | (4 << 6)), "-1×1=-1"
    assert e3m6_core_mul(neg1, neg1) == one, "-1×-1=1"
    assert e3m6_core_mul(0, one) == 0, "0×1=0"
    # sat: 8 × 2 = 16 > 15.875 → sat
    eight = (7 << 6)
    assert e3m6_core_mul(eight, two) == ((7 << 6) | 0x3F), "8×2 sat"
    print("  e3m6_core_mul unit checks: PASS")


# ─────────────────────────────────────────────────────────────────────────────
# 4. K-criteria re-validation under RTL-faithful arithmetic + golden emission
# ─────────────────────────────────────────────────────────────────────────────

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--systems", type=int, default=200,
                    help="DD N=8 systems for golden + K-revalidation")
    args = ap.parse_args()

    print("=" * 66)
    print("PHASE 3 — RTL SECOND SOURCE: E3M6 core golden + arithmetic re-check")
    print("=" * 66)
    _unit_test_core()

    # Re-validate K1 (convergence) and K4 (vs E4M3) under TRUNCATING arithmetic,
    # on DD N=8, same seeds as the campaign.  Emit the full product golden.
    tap = []
    n_conv_rtl = 0
    n_fp64_conv = 0
    serr_rtl, serr_e4m3 = [], []
    n_iter_rtl, n_iter_fp64 = [], []
    print(f"\nRunning {args.systems} DD N=8 solves (truncating E3M6 + E4M3 + FP64)…")
    for trial in range(args.systems):
        seed = _seed("dd_random", 8, trial)
        rng = np.random.default_rng(seed)
        A, b = J.make_dd_random(8, rng)
        ref = J.solve_fp64(A, b)
        fp64_conv = J.first_leq(ref["rhos"], J.TAU_FP64) is not None
        if not fp64_conv:
            continue
        n_fp64_conv += 1

        r_rtl = solve_e3m6_block_rtl(A, b, tap=tap)
        r_e4 = J.solve_format(A, b, "FP8-E4M3")
        if r_rtl["converged"]:
            n_conv_rtl += 1
            serr_rtl.append(J.rel_sol_error(r_rtl["x"], ref["x"]))
            n_iter_rtl.append(r_rtl["n_iter"])
            n_iter_fp64.append(J.first_leq(ref["rhos"], J.tau("E3M6+block")))
        if r_e4["converged"]:
            serr_e4m3.append(J.rel_sol_error(r_e4["x"], ref["x"]))

    conv_rate = n_conv_rtl / n_fp64_conv if n_fp64_conv else float("nan")
    cp95 = 1.0 - 0.05 ** (1.0 / n_fp64_conv) if (n_fp64_conv and n_conv_rtl == n_fp64_conv) else float("nan")
    med_serr_rtl = sorted(serr_rtl)[len(serr_rtl) // 2] if serr_rtl else float("nan")
    med_serr_e4 = sorted(serr_e4m3)[len(serr_e4m3) // 2] if serr_e4m3 else float("nan")
    med_ratio = (sorted([a / c for a, c in zip(n_iter_rtl, n_iter_fp64) if c])[
                     len(n_iter_rtl) // 2] if n_iter_rtl else float("nan"))

    print("\n── RTL-faithful (truncating) arithmetic re-validation (DD N=8) ──")
    print(f"  FP64-converged systems:            {n_fp64_conv}")
    print(f"  E3M6+block(RTL trunc) converged:   {n_conv_rtl}/{n_fp64_conv} "
          f"= {conv_rate*100:.2f}%  (CP95 UB {cp95:.3e})")
    print(f"  median iteration ratio vs FP64:    {med_ratio:.2f}")
    print(f"  median solution error (RTL trunc): {med_serr_rtl:.3e}")
    print(f"  median solution error (E4M3):      {med_serr_e4:.3e}")
    print(f"  K1(N=8, trunc) : {'PASS' if conv_rate >= 0.999 else 'FAIL'}")
    print(f"  K4 accuracy vs E4M3: E3M6-trunc {'BEATS' if med_serr_rtl < med_serr_e4 else 'does NOT beat'} "
          f"E4M3 ({med_serr_rtl:.2e} vs {med_serr_e4:.2e})")

    # De-duplicate the product stream (many pairs repeat) but keep full coverage.
    seen = {}
    for a, bb, p in tap:
        seen[(a, bb)] = p
    with open(GOLDEN_HEX, "w") as f:
        f.write(f"// JACOBI_E3M6_GOLDEN.hex — a b expected(product) for horus_e3m6_core\n")
        f.write(f"// {len(tap)} products emitted over {args.systems} DD N=8 solves; "
                f"{len(seen)} unique (a,b) pairs.\n")
        for (a, bb), p in seen.items():
            f.write(f"{a:03x} {bb:03x} {p:03x}\n")
    print(f"\n  Golden: {len(tap)} products ({len(seen)} unique pairs) → "
          f"{os.path.basename(GOLDEN_HEX)}")


if __name__ == "__main__":
    main()
