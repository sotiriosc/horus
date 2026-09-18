#!/usr/bin/env python3
"""
sim/jacobi_solver.py — Format-parameterized Jacobi relaxation solver.

Pre-registered criteria: docs/JACOBI_HYPOTHESIS.md (binding).

This module implements the Jacobi iteration

    x_i^{(k+1)} = ( b_i - sum_{j != i} A_ij * x_j^{(k)} ) / A_ii

with arithmetic limited to a chosen number format, quantizing at exactly the
points the corresponding RTL datapath would impose (JACOBI_HYPOTHESIS.md §3).

FORMAT SOURCE OF TRUTH — no format is re-implemented here:
  * NFE-13, FP8-E4M3, BF16 : imported from sim/format_zoo.py
  * E3M6+block             : imported from sim/compact_nfe.py
The only additions are (a) integer-codeword adapters and (b) vectorized
product/quantize helpers, each PROVEN bit-identical to the imported scalar
codecs by run_preflight() before any solve runs. If a vectorized helper ever
diverges from its scalar source, the preflight aborts.

Two datapath families (JACOBI_HYPOTHESIS.md §3):
  (a) per-element float  — NFE-13, FP8-E4M3, BF16 : quantize after every
      multiply, accumulate in an FP64-width sum, quantize the update.
  (b) block floating point — E3M6+block           : block-encode operands,
      accumulate products in the FP64 wide accumulator, and re-encode the whole
      state vector as blocks of 8 with a shared exponent once per sweep (the
      block boundary is where rounding is architecturally forced).

All residuals / errors / iteration counts are measured in FP64 on the decoded
state; only the solver arithmetic is format-limited.
"""

import math
import os
import sys

import numpy as np

DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, DIR)

# ── Imported format codecs (single source of truth) ────────────────────────────
from format_zoo import (            # noqa: E402
    nfe_enc, nfe_dec, nfe_mul_fields, nfe_is_sat,
    fp8_e4m3_enc, fp8_e4m3_dec, fp8_e4m3_mul, fp8_e4m3_is_overflow,
    bf16_enc, bf16_dec, bf16_mul, bf16_is_overflow, bf16_is_nan,
)
from compact_nfe import (           # noqa: E402
    enm6_enc, enm6_dec, block_enc, block_dec, BLOCK_SIZE,
)

# ─────────────────────────────────────────────────────────────────────────────
# PRE-REGISTERED CONSTANTS (docs/JACOBI_HYPOTHESIS.md §4, §5, §7)
# ─────────────────────────────────────────────────────────────────────────────

FORMATS = ["FP64", "BF16", "FP8-E4M3", "E3M6+block", "NFE-13"]

# Unit roundoff u_F = 2^-(M+1), M = mantissa fraction bits (§4).
UNIT_ROUNDOFF = {
    "FP64":       2.0 ** -53,   # 1.1102e-16
    "BF16":       2.0 ** -8,    # 3.9063e-3
    "FP8-E4M3":   2.0 ** -4,    # 6.2500e-2
    "E3M6+block": 2.0 ** -7,    # 7.8125e-3
    "NFE-13":     2.0 ** -7,    # 7.8125e-3
}

C_CONV   = 4        # per-format convergence-target multiplier (§5)
C_ENV    = 8        # solution-envelope multiplier (K3, §5)
K_MAX    = 500      # iteration cap (§5)
W_DIV    = 20       # divergence window (§5)
TAU_FP64 = 1e-10    # FP64 convergence target (§5)

E3M6_N = 3          # per-element exponent bits for E3M6 (compact_nfe enm6 n=3)


def tau(fmt):
    """Per-format target relative residual τ_F = C_conv · u_F (FP64 fixed)."""
    if fmt == "FP64":
        return TAU_FP64
    return C_CONV * UNIT_ROUNDOFF[fmt]


# ─────────────────────────────────────────────────────────────────────────────
# CODEWORD ADAPTERS  (thin wrappers over imported codecs; no new arithmetic)
# ─────────────────────────────────────────────────────────────────────────────

# NFE-13: pack fields (s,e,f) into a 13-bit codeword s<<12 | e<<6 | f.
def _nfe_enc_cw(v):
    s, e, f = nfe_enc(v)
    return (s << 12) | (e << 6) | f


def _nfe_dec_cw(cw):
    return nfe_dec((cw >> 12) & 1, (cw >> 6) & 0x3F, cw & 0x3F)


def _nfe_cw_is_sat(cw):
    return nfe_is_sat((cw >> 6) & 0x3F, cw & 0x3F)


# FP8-E4M3: codeword is the 8-bit value itself.
def _e4m3_mul_dec(ca, cx):
    return fp8_e4m3_dec(fp8_e4m3_mul(ca, cx))


# Vectorized ufunc wrappers (loop in C, call cached scalar functions).
_v_nfe_enc  = np.frompyfunc(_nfe_enc_cw, 1, 1)
_v_nfe_dec  = np.frompyfunc(_nfe_dec_cw, 1, 1)
_v_e4m3_enc = np.frompyfunc(fp8_e4m3_enc, 1, 1)
_v_bf16_enc = np.frompyfunc(bf16_enc, 1, 1)

# FP8-E4M3 is only 8 bits → full 256×256 product-decode LUT (built from the
# imported scalar codec, then used via pure-numpy fancy indexing).
_E4M3_MULDEC_LUT = np.empty((256, 256), dtype=np.float64)
for _a in range(256):
    for _b in range(256):
        _E4M3_MULDEC_LUT[_a, _b] = _e4m3_mul_dec(_a, _b)
_E4M3_DEC_LUT = np.array([fp8_e4m3_dec(c) for c in range(256)], dtype=np.float64)

# BF16 decode LUT (16-bit → 65536 entries; built from the imported scalar dec).
_BF16_DEC_LUT = np.array([bf16_dec(c) for c in range(1 << 16)], dtype=np.float64)


# ── Vectorized NFE-13 product (bit-identical to nfe_mul_fields; preflight-checked)
def _nfe_prod_dec_vec(A_cw, x_cw):
    """Decoded FP64 NFE products, vectorized replica of nfe_mul_fields∘nfe_dec.

    Replicates format_zoo.nfe_mul_fields exactly (6-bit product truncation,
    E=0 operand → zero product, es-clamp sentinels) with pure numpy integer
    math; run_preflight() asserts bit-identity to the imported scalar codec.
    """
    A = A_cw.astype(np.int64)
    x = x_cw.astype(np.int64)[None, :]
    sa, ea, fa = (A >> 12) & 1, (A >> 6) & 0x3F, A & 0x3F
    sx, ex, fx = (x >> 12) & 1, (x >> 6) & 0x3F, x & 0x3F
    rs = sa ^ sx
    P = (64 + fa) * (64 + fx)
    ge = P >= 8192
    es = ea + ex - 32 + ge.astype(np.int64)
    fR = np.where(ge, (P >> 7) & 0x3F, (P >> 6) & 0x3F)
    zero = (ea == 0) | (ex == 0)
    underflow = es <= 0
    overflow = es > 63
    e_final = np.where(zero | underflow, 0, np.where(overflow, 63, es))
    f_final = np.where(zero | underflow, 0, np.where(overflow, 63, fR))
    sign = 1.0 - 2.0 * rs
    return sign * np.ldexp(1.0 + f_final / 64.0, e_final - 32)


# ── Vectorized BF16 quantize (bit-identical to bf16_enc; preflight-checked) ─────
def _bf16_quantize_vec(arr):
    """Round an FP64 array to BF16 values (FP64 out), replica of bf16_enc∘dec."""
    f32 = np.asarray(arr, dtype=np.float64).astype(np.float32)
    bits = f32.view(np.uint32)
    hi = (bits >> 16).astype(np.uint32)
    lo = (bits & 0xFFFF).astype(np.uint32)
    roundup = (lo > 0x8000) | ((lo == 0x8000) & ((hi & 1) == 1))
    hi = np.where(roundup, (hi + 1) & 0xFFFF, hi).astype(np.uint16)
    return _BF16_DEC_LUT[hi]


# ─────────────────────────────────────────────────────────────────────────────
# PER-ELEMENT FLOAT FAMILY (a): encode / decode / quantize / per-product mul
# ─────────────────────────────────────────────────────────────────────────────

def _enc_vec(arr, fmt):
    """FP64 array → integer codeword array (round to nearest per format)."""
    a = np.asarray(arr, dtype=np.float64)
    if fmt == "NFE-13":
        return _v_nfe_enc(a).astype(np.int64)
    if fmt == "FP8-E4M3":
        return _v_e4m3_enc(a).astype(np.int64)
    if fmt == "BF16":
        return _v_bf16_enc(a).astype(np.int64)
    raise ValueError(fmt)


def _dec_vec(cw, fmt):
    """Codeword array → decoded FP64 array."""
    c = np.asarray(cw)
    if fmt == "NFE-13":
        return _v_nfe_dec(c).astype(np.float64)
    if fmt == "FP8-E4M3":
        return _E4M3_DEC_LUT[c.astype(np.int64)]
    if fmt == "BF16":
        return _BF16_DEC_LUT[c.astype(np.int64)]
    raise ValueError(fmt)


def _quantize_vec(arr, fmt):
    """decode(encode(v)) — the value as the format would round it (FP64 out)."""
    return _dec_vec(_enc_vec(arr, fmt), fmt)


def _prod_dec(A_cw, x_cw, fmt):
    """Per-product quantized products, decoded to FP64.  A_cw: (N,N), x_cw: (N,)."""
    if fmt == "FP8-E4M3":
        return _E4M3_MULDEC_LUT[A_cw, x_cw[None, :]]
    if fmt == "NFE-13":
        return _nfe_prod_dec_vec(A_cw, x_cw)
    if fmt == "BF16":
        prod = _BF16_DEC_LUT[A_cw.astype(np.int64)] * _BF16_DEC_LUT[x_cw.astype(np.int64)][None, :]
        return _bf16_quantize_vec(prod)
    raise ValueError(fmt)


def _cw_overflow(cw, fmt):
    """True where a codeword is a saturation/Inf/NaN sentinel."""
    c = np.asarray(cw).astype(np.int64).ravel()
    if fmt == "NFE-13":
        return any(_nfe_cw_is_sat(int(v)) for v in c)
    if fmt == "FP8-E4M3":
        return any(fp8_e4m3_is_overflow(int(v)) for v in c)
    if fmt == "BF16":
        return any(bf16_is_overflow(int(v)) or bf16_is_nan(int(v)) for v in c)
    return False


# ─────────────────────────────────────────────────────────────────────────────
# BLOCK FLOATING POINT FAMILY (b): E3M6+block
# ─────────────────────────────────────────────────────────────────────────────
_E3M6_MAX_E = (1 << E3M6_N) - 1     # = 7


def _block_quantize_vec(arr, n=E3M6_N):
    """Block-encode an FP64 vector (blocks of BLOCK_SIZE) and decode back.

    Returns (decoded_fp64_vector, saturated_flag).  The block boundary is where
    rounding is forced; each block carries one shared exponent (block_enc/dec).
    """
    a = np.asarray(arr, dtype=np.float64).ravel()
    out = np.empty_like(a)
    saturated = False
    for start in range(0, a.size, BLOCK_SIZE):
        vals = a[start:start + BLOCK_SIZE].tolist()
        cws, bexp = block_enc(vals, n)
        for cw in cws:
            e_stored = (cw >> 6) & ((1 << n) - 1)
            if e_stored == _E3M6_MAX_E and (cw & 63) == 63:
                saturated = True
        out[start:start + BLOCK_SIZE] = block_dec(cws, bexp, n)
    return out, saturated


def _block_quantize_matrix(M, n=E3M6_N):
    """Block-quantize each row of a matrix (blocks along columns)."""
    M = np.asarray(M, dtype=np.float64)
    Q = np.empty_like(M)
    for r in range(M.shape[0]):
        Q[r], _ = _block_quantize_vec(M[r], n)
    return Q


# ─────────────────────────────────────────────────────────────────────────────
# RESIDUAL / ERROR METRICS  (always FP64, against the true system)
# ─────────────────────────────────────────────────────────────────────────────

def rel_residual(A, x, b, bnorm=None):
    if bnorm is None:
        bnorm = np.linalg.norm(b)
    if bnorm == 0.0:
        bnorm = 1.0
    return float(np.linalg.norm(A @ x - b) / bnorm)


def rel_sol_error(x, x_ref):
    denom = np.linalg.norm(x_ref, np.inf)
    if denom == 0.0:
        denom = 1.0
    return float(np.linalg.norm(x - x_ref, np.inf) / denom)


def cond_inf(A):
    try:
        return float(np.linalg.cond(A, np.inf))
    except np.linalg.LinAlgError:
        return float("inf")


# ─────────────────────────────────────────────────────────────────────────────
# FP64 REFERENCE SOLVER
# ─────────────────────────────────────────────────────────────────────────────

def solve_fp64(A, b, k_max=K_MAX, record=False):
    """Run FP64 Jacobi; return dict with residual trajectory and x*.

    Trajectory rho[k] = relative residual AFTER sweep k (k = 1..len).  This lets
    K1 (n to TAU_FP64) and K2 (n to any tau) read off the same single run.
    """
    A = np.asarray(A, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    N = b.size
    d = np.diag(A).copy()
    R = A - np.diagflat(d)
    dinv = 1.0 / d
    bnorm = np.linalg.norm(b)
    x = np.zeros(N)
    rhos = []
    for _ in range(k_max):
        x = (b - R @ x) * dinv
        rhos.append(rel_residual(A, x, b, bnorm))
        if rhos[-1] <= TAU_FP64:
            break
    return {"x": x, "rhos": rhos}


def first_leq(rhos, thr):
    """1-based sweep index of first rho <= thr, or None."""
    for k, r in enumerate(rhos, start=1):
        if r <= thr:
            return k
    return None


# ─────────────────────────────────────────────────────────────────────────────
# FORMAT SOLVERS
# ─────────────────────────────────────────────────────────────────────────────

def _solve_float_family(A, b, fmt, k_max=K_MAX, early_stop=True):
    """Datapath family (a): per-element float (NFE-13 / FP8-E4M3 / BF16)."""
    A = np.asarray(A, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    N = b.size
    bnorm = np.linalg.norm(b)

    A_cw = _enc_vec(A, fmt)                         # (N,N) codewords
    A_dec = _dec_vec(A_cw, fmt)                     # decoded matrix (for diag)
    diag_dec = np.diag(A_dec).copy()
    diag_dec[diag_dec == 0.0] = np.finfo(float).tiny
    dinv_dec = _quantize_vec(1.0 / diag_dec, fmt)   # stored reciprocal
    b_q = _quantize_vec(b, fmt)

    x_cw = _enc_vec(np.zeros(N), fmt)
    x_dec = _dec_vec(x_cw, fmt)

    rhos = []
    overflow = False
    diag_idx = np.arange(N)
    for _ in range(k_max):
        P = _prod_dec(A_cw, x_cw, fmt)              # quantized products, FP64
        acc = P.sum(axis=1) - P[diag_idx, diag_idx]  # exclude diagonal term
        r = _quantize_vec(b_q - acc, fmt)           # quantize after accumulate
        upd = _quantize_vec(r * dinv_dec, fmt)      # quantize after recip-mul
        x_cw = _enc_vec(upd, fmt)
        x_dec = _dec_vec(x_cw, fmt)
        if not overflow and _cw_overflow(x_cw, fmt):
            overflow = True
        rhos.append(rel_residual(A, x_dec, b, bnorm))
        if early_stop and rhos[-1] <= tau(fmt):
            break
    return {"x": x_dec, "rhos": rhos, "overflow": overflow}


def _solve_block_family(A, b, fmt, k_max=K_MAX, early_stop=True):
    """Datapath family (b): E3M6+block."""
    A = np.asarray(A, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    N = b.size
    bnorm = np.linalg.norm(b)

    A_dec = _block_quantize_matrix(A)               # block-quantized matrix
    diag_dec = np.diag(A_dec).copy()
    diag_dec[diag_dec == 0.0] = np.finfo(float).tiny
    dinv_dec, _ = _block_quantize_vec(1.0 / diag_dec)
    b_dec, _ = _block_quantize_vec(b)
    R = A_dec - np.diagflat(np.diag(A_dec))

    x_dec = np.zeros(N)
    rhos = []
    overflow = False
    for _ in range(k_max):
        acc = R @ x_dec                             # FP64 wide accumulate
        r = (b_dec - acc) * dinv_dec                # FP64 update pre-rounding
        x_dec, sat = _block_quantize_vec(r)         # block boundary = rounding
        overflow = overflow or sat
        rhos.append(rel_residual(A, x_dec, b, bnorm))
        if early_stop and rhos[-1] <= tau(fmt):
            break
    return {"x": x_dec, "rhos": rhos, "overflow": overflow}


def solve_format(A, b, fmt, k_max=K_MAX, early_stop=True):
    """Dispatch to the correct datapath family; return metrics dict.

    early_stop=False runs the full k_max sweeps (used for S1 trajectory capture).
    """
    if fmt == "E3M6+block":
        res = _solve_block_family(A, b, fmt, k_max, early_stop)
    elif fmt in ("NFE-13", "FP8-E4M3", "BF16"):
        res = _solve_float_family(A, b, fmt, k_max, early_stop)
    elif fmt == "FP64":
        r = solve_fp64(A, b, k_max)
        res = {"x": r["x"], "rhos": r["rhos"], "overflow": False}
    else:
        raise ValueError(fmt)

    rhos = res["rhos"]
    thr = tau(fmt)
    n_iter = first_leq(rhos, thr)
    converged = (n_iter is not None) and (not res["overflow"])
    # Divergence: monotone non-decreasing over the last W_DIV sweeps and not
    # converged, or a sentinel fired.
    diverged = res["overflow"]
    if not converged and len(rhos) >= W_DIV:
        tail = rhos[-W_DIV:]
        if all(tail[i + 1] >= tail[i] for i in range(len(tail) - 1)):
            diverged = True
    res.update({"n_iter": n_iter, "converged": converged, "diverged": diverged,
                "final_rho": rhos[-1] if rhos else float("nan"),
                "n_sweeps": len(rhos)})
    return res


# ─────────────────────────────────────────────────────────────────────────────
# TEST-SYSTEM GENERATORS (numpy only; docs/JACOBI_HYPOTHESIS.md §7)
# ─────────────────────────────────────────────────────────────────────────────

DOM_MARGIN = 0.25   # γ: strict diagonal-dominance margin (§7)


def make_dd_random(N, rng):
    """Diagonally dominant random system (K1 primary set, §7)."""
    A = rng.uniform(-1.0, 1.0, size=(N, N))
    np.fill_diagonal(A, 0.0)
    off_sum = np.abs(A).sum(axis=1)
    sign = rng.choice([-1.0, 1.0], size=N)
    np.fill_diagonal(A, sign * off_sum * (1.0 + DOM_MARGIN))
    b = rng.uniform(-1.0, 1.0, size=N)
    return A, b


def make_illcond_dd(N, rng, kappa_target):
    """Ill-conditioned but strictly diagonally dominant system (§7).

    Condition number is raised by widening the diagonal magnitude spread across
    log-space up to kappa_target while keeping strict dominance; realized κ is
    measured by the caller (never assumed).
    """
    A = rng.uniform(-1.0, 1.0, size=(N, N))
    np.fill_diagonal(A, 0.0)
    off_sum = np.abs(A).sum(axis=1)
    # Diagonal magnitudes span [1, kappa_target] geometrically across rows.
    exps = np.linspace(0.0, math.log10(max(kappa_target, 1.0)), N)
    scale = 10.0 ** exps
    rng.shuffle(scale)
    sign = rng.choice([-1.0, 1.0], size=N)
    diag = sign * (off_sum * (1.0 + DOM_MARGIN) + scale)
    np.fill_diagonal(A, diag)
    b = rng.uniform(-1.0, 1.0, size=N)
    return A, b


def make_laplacian_1d(N, rng):
    """1D Poisson operator tridiag[-1, 2, -1] (weakly DD) with random RHS (§7)."""
    A = np.zeros((N, N))
    np.fill_diagonal(A, 2.0)
    idx = np.arange(N - 1)
    A[idx, idx + 1] = -1.0
    A[idx + 1, idx] = -1.0
    b = rng.uniform(-1.0, 1.0, size=N)
    return A, b


# ─────────────────────────────────────────────────────────────────────────────
# PREFLIGHT: vectorized helpers must equal imported scalar codecs bit-for-bit
# ─────────────────────────────────────────────────────────────────────────────

def run_preflight(verbose=True):
    """Assert every vectorized helper matches its imported scalar codec.

    This is how format_zoo.py / compact_nfe.py remain the single source of truth:
    the fast paths are validated equivalents, not re-implementations.
    """
    rng = np.random.default_rng(0x1A0C0B1)
    fails = []

    # NFE-13 enc/dec round-trip vs scalar
    vals = rng.uniform(-50, 50, size=500)
    for v in vals:
        cw = _nfe_enc_cw(v)
        s, e, f = nfe_enc(v)
        if cw != ((s << 12) | (e << 6) | f):
            fails.append(f"NFE enc adapter mismatch at {v}")
        if _nfe_dec_cw(cw) != nfe_dec(s, e, f):
            fails.append(f"NFE dec adapter mismatch at {v}")
    # NFE vectorized enc/dec vs scalar
    cw_a = _enc_vec(vals, "NFE-13")
    cw_b = _enc_vec(rng.uniform(-5, 5, size=500), "NFE-13")
    dec_v = _dec_vec(cw_a, "NFE-13")
    for i in range(len(vals)):
        if dec_v[i] != _nfe_dec_cw(int(cw_a[i])):
            fails.append("NFE _dec_vec mismatch")
            break
    # Vectorized NFE product vs scalar nfe_mul_fields∘nfe_dec (bit-identical).
    Pvec = _nfe_prod_dec_vec(cw_a.reshape(1, -1), cw_b)  # (1, 500): a_i · b_i
    for i in range(len(vals)):
        a, x = int(cw_a[i]), int(cw_b[i])
        s, e, f = nfe_mul_fields((a >> 12) & 1, (a >> 6) & 0x3F, a & 0x3F,
                                 (x >> 12) & 1, (x >> 6) & 0x3F, x & 0x3F)
        if Pvec[0, i] != nfe_dec(s, e, f):
            fails.append(f"NFE vectorized product mismatch at pair {i}")
            break

    # E4M3 LUT vs scalar mul, dec LUT vs scalar dec
    for a in rng.integers(0, 256, size=300):
        if _E4M3_DEC_LUT[a] != fp8_e4m3_dec(int(a)) and not (
                math.isnan(_E4M3_DEC_LUT[a]) and math.isnan(fp8_e4m3_dec(int(a)))):
            fails.append(f"E4M3 dec LUT mismatch at {a}")
        b = int(rng.integers(0, 256))
        want = fp8_e4m3_dec(fp8_e4m3_mul(int(a), b))
        got = _E4M3_MULDEC_LUT[int(a), b]
        if got != want and not (math.isnan(got) and math.isnan(want)):
            fails.append(f"E4M3 mul LUT mismatch at ({a},{b})")

    # BF16 vectorized enc/dec vs scalar, and vectorized quantize vs bf16_enc∘dec.
    bvals = rng.uniform(-100, 100, size=300)
    bcw = _enc_vec(bvals, "BF16")
    for i in range(len(bvals)):
        if int(bcw[i]) != bf16_enc(bvals[i]):
            fails.append("BF16 enc adapter mismatch")
            break
    bq = _bf16_quantize_vec(bvals)
    for i in range(len(bvals)):
        if bq[i] != bf16_dec(bf16_enc(bvals[i])):
            fails.append(f"BF16 vectorized quantize mismatch at {bvals[i]}")
            break
    # Vectorized BF16 product vs scalar bf16_mul (bit-identical).
    bcw_b = _enc_vec(rng.uniform(-5, 5, size=300), "BF16")
    Pb = _prod_dec(bcw.reshape(1, -1), bcw_b, "BF16")
    for i in range(len(bvals)):
        if Pb[0, i] != bf16_dec(bf16_mul(int(bcw[i]), int(bcw_b[i]))):
            fails.append(f"BF16 vectorized product mismatch at pair {i}")
            break

    # E3M6 block round-trip vs compact_nfe scalar block_enc/dec
    v8 = rng.uniform(-10, 10, size=8).tolist()
    cws, bexp = block_enc(v8, E3M6_N)
    ref = block_dec(cws, bexp, E3M6_N)
    got, _ = _block_quantize_vec(np.array(v8))
    if not np.allclose(got, ref, rtol=0, atol=0):
        fails.append("E3M6 block adapter mismatch")

    if fails:
        for m in fails:
            print(f"  PREFLIGHT FAIL: {m}")
        raise AssertionError(f"jacobi_solver preflight: {len(fails)} failure(s)")
    if verbose:
        print("  jacobi_solver preflight: PASS "
              "(vectorized paths bit-identical to format_zoo / compact_nfe)")


if __name__ == "__main__":
    run_preflight(verbose=True)
    # Smoke solve: one DD system, all formats.
    rng = np.random.default_rng(0x4AC0B1A5)
    A, b = make_dd_random(32, rng)
    ref = solve_fp64(A, b)
    print(f"\n  DD N=32  κ_inf={cond_inf(A):.3g}")
    print(f"  {'format':<12} {'conv':>5} {'n_iter':>7} {'final_rho':>12} "
          f"{'sol_err':>12}")
    for fmt in FORMATS:
        r = solve_format(A, b, fmt)
        serr = rel_sol_error(r["x"], ref["x"])
        print(f"  {fmt:<12} {str(r['converged']):>5} "
              f"{str(r['n_iter']):>7} {r['final_rho']:>12.4e} {serr:>12.4e}")
