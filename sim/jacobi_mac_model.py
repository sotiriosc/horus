#!/usr/bin/env python3
"""
sim/jacobi_mac_model.py — Phase 4b width-preserving MAC reference + goldens.

Pre-registration: docs/JACOBI_VERDICT.md "Phase 4b — Width-preserving MAC".

Arithmetic contract (binding):
  - Full 14-bit product P = M_a * M_b, w = q_a + q_b, no input flush.
  - Exponent-aligned signed-32 accumulate on block-relative addends ±P·2^(w−2).
  - R2 solver: MAC row accumulate, FP64 (b−acc)*dinv update, RNE block re-encode.

numpy only; reuses Phase-3/4a seeds and JACOBI_E3M6_GOLDEN.hex operand pairs.
"""

import math
import os
import sys

import numpy as np

DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, DIR)

import jacobi_solver as J                                    # noqa: E402
from jacobi_campaign import _seed                            # noqa: E402
import jacobi_rtl_golden as R                                # noqa: E402
from compact_nfe import enm6_enc, enm6_dec, block_enc, BLOCK_SIZE  # noqa: E402

E3M6_N = 3
N_SYS = 200
ACC_CAP = 50000
ACC_SCALE_BIAS = -18  # pairs with w−2 addends: P·2^(w+bexp−20) = (P·2^(w−2))·2^(bexp−18)
SIGNED32_MIN = -(1 << 31)
SIGNED32_MAX = (1 << 31) - 1


def width_bits(N: int) -> int:
    """Binding accumulator width (docs/SCALING_HYPOTHESIS.md §1)."""
    return 26 + math.ceil(math.log2(N - 1)) + 3


def acc_limits(width: int):
    """Signed accumulator range for `width` bits."""
    hi = (1 << (width - 1)) - 1
    lo = -(1 << (width - 1))
    return lo, hi

PRODUCT_GOLDEN = os.path.join(DIR, "JACOBI_MAC_PRODUCT_GOLDEN.hex")
ACC_GOLDEN = os.path.join(DIR, "JACOBI_MAC_ACC_GOLDEN.hex")
R2_LOG = os.path.join(DIR, "JACOBI_MAC_R2.log")


def unpack_mq(cw: int):
    """Return (sign, M, q) per the Phase-4b arithmetic contract (no input flush)."""
    cw &= 0x3FF
    s = (cw >> 9) & 1
    e = (cw >> 6) & 7
    f = cw & 0x3F
    if e == 0 and f == 0:
        return s, 0, 0
    if e == 0:
        return s, f, 1
    return s, 0x40 | f, e


def mac_full_product(a_cw: int, b_cw: int) -> dict:
    """Full 14-bit product fields (sign, P, w, shift=w−2)."""
    sa, Ma, qa = unpack_mq(a_cw)
    sb, Mb, qb = unpack_mq(b_cw)
    sign = sa ^ sb
    if Ma == 0 or Mb == 0:
        return {"sign": sign, "P": 0, "w": 0, "shift": 0}
    P = Ma * Mb
    w = qa + qb
    return {"sign": sign, "P": P, "w": w, "shift": w - 2}


class Acc32:
    """Signed 32-bit exponent-aligned block-relative accumulator."""

    def __init__(self, tap=None, acc_max=None):
        self.acc = 0
        self.overflow = False
        self.tap = tap
        self.acc_max = acc_max
        self._lo, self._hi = SIGNED32_MIN, SIGNED32_MAX

    def clear(self):
        self.acc = 0
        if self.tap is not None:
            self.tap.append(("clear", 0))

    def add_term(self, sign: int, P: int, shift: int):
        if P == 0:
            if self.tap is not None:
                self.tap.append(("acc", self.acc))
            return
        term = P << shift
        if sign:
            term = -term
        new = self.acc + term
        if new < self._lo or new > self._hi:
            self.overflow = True
        self.acc = new
        if self.acc_max is not None:
            self.acc_max[0] = max(self.acc_max[0], abs(self.acc))
        if self.tap is not None:
            self.tap.append(("acc", self.acc))

    def value(self) -> int:
        return self.acc


def AccWide(width: int, tap=None, acc_max=None):
    """Factory: Acc32 at width=32, else width-parameterized accumulator."""
    if width == 32:
        return Acc32(tap=tap, acc_max=acc_max)
    lo, hi = acc_limits(width)
    acc = Acc32(tap=tap, acc_max=acc_max)
    acc._lo, acc._hi = lo, hi
    return acc


def mac_accumulate_row(terms, bexp_a: int, bexp_x: int) -> float:
    """Sum MAC terms for one row; return FP64 block-scaled value."""
    acc = Acc32()
    acc.clear()
    for sign, P, shift in terms:
        acc.add_term(sign, P, shift)
    if acc.overflow:
        raise OverflowError("32-bit MAC accumulator overflow")
    scale = 2.0 ** (bexp_a + bexp_x - 20)
    return acc.value() * scale


def _blk_enc(values):
    return block_enc(list(values), E3M6_N)


def _eff(cw, bexp):
    return enm6_dec(cw, E3M6_N) * (2.0 ** bexp)


def solve_e3m6_block_mac(A, b, k_max=J.K_MAX, early_stop=True, acc_tap=None,
                         acc_width=None, acc_max_out=None):
    """MAC-faithful Jacobi: wide product accumulate, FP64 update, block RNE."""
    A = np.asarray(A, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    N = b.size
    assert N % BLOCK_SIZE == 0
    if acc_width is None:
        acc_width = width_bits(N)
    bnorm = np.linalg.norm(b)
    acc_max = [0]

    A_dec = J._block_quantize_matrix(A)
    diag_dec = np.diag(A_dec).copy()
    diag_dec[diag_dec == 0.0] = np.finfo(float).tiny
    dinv_dec, _ = J._block_quantize_vec(1.0 / diag_dec)
    b_dec, _ = J._block_quantize_vec(b)

    A_cw, A_be = [], []
    for i in range(N):
        cws, be = _blk_enc(A_dec[i])
        A_cw.append(cws)
        A_be.append(be)

    x_dec, _ = J._block_quantize_vec(np.zeros(N))
    x_cw, x_be = _blk_enc(x_dec)
    rhos = []
    overflow = False
    acc_steps = 0

    for _ in range(k_max):
        acc = np.zeros(N)
        for i in range(N):
            try:
                a32 = AccWide(acc_width, tap=acc_tap, acc_max=acc_max)
                a32.clear()
                for j in range(N):
                    if j == i:
                        continue
                    if acc_tap is not None and acc_steps >= ACC_CAP:
                        break
                    if acc_tap is not None:
                        acc_tap.append(("term", A_cw[i][j], x_cw[j]))
                    fp = mac_full_product(A_cw[i][j], x_cw[j])
                    a32.add_term(fp["sign"], fp["P"], fp["shift"])
                    acc_steps += 1
                if a32.overflow:
                    overflow = True
                acc[i] = a32.value() * (2.0 ** (A_be[i] + x_be + ACC_SCALE_BIAS))
            except OverflowError:
                overflow = True
                acc[i] = float("nan")

        r = b_dec - acc
        x_new = r * dinv_dec
        x_dec, sat = J._block_quantize_vec(x_new)
        if sat:
            overflow = True
        x_cw, x_be = _blk_enc(x_dec)
        rhos.append(J.rel_residual(A, x_dec, b, bnorm))
        if early_stop and rhos[-1] <= J.tau("E3M6+block"):
            break

    n_iter = J.first_leq(rhos, J.tau("E3M6+block"))
    if acc_max_out is not None:
        acc_max_out[0] = acc_max[0]
    return {
        "x": x_dec,
        "rhos": rhos,
        "overflow": overflow,
        "n_iter": n_iter,
        "converged": (n_iter is not None) and not overflow,
        "final_rho": rhos[-1] if rhos else float("nan"),
        "acc_steps": acc_steps,
        "acc_max": acc_max[0],
        "acc_width": acc_width,
    }


def _load_operand_pairs(path):
    pairs = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("//"):
                continue
            a, b, _ = (int(x, 16) for x in line.split())
            pairs.append((a, b))
    return pairs


def emit_product_golden(pairs):
    with open(PRODUCT_GOLDEN, "w") as f:
        f.write("// JACOBI_MAC_PRODUCT_GOLDEN.hex — sign P w per unique (a,b)\n")
        f.write(f"// {len(pairs)} pairs from JACOBI_E3M6_GOLDEN.hex operands.\n")
        for a, b in pairs:
            fp = mac_full_product(a, b)
            f.write(f"{a:03x} {b:03x} {fp['sign']:x} {fp['P']:04x} {fp['w']:x}\n")


def emit_acc_golden():
    steps = []
    for trial in range(N_SYS):
        rng = np.random.default_rng(_seed("dd_random", 8, trial))
        A, b = J.make_dd_random(8, rng)
        tap = []
        solve_e3m6_block_mac(A, b, acc_tap=tap)
        for ev in tap:
            if len(steps) >= ACC_CAP:
                return steps
            steps.append(ev)
    return steps


def write_acc_golden(steps):
    with open(ACC_GOLDEN, "w") as f:
        f.write("// JACOBI_MAC_ACC_GOLDEN.hex — clear / term(a,b) / acc events\n")
        f.write(f"// {len(steps)} events (cap {ACC_CAP}).\n")
        for ev in steps:
            if ev[0] == "clear":
                f.write("C 00000000\n")
            elif ev[0] == "term":
                _, a, b = ev
                f.write(f"T {a:03x} {b:03x}\n")
            elif ev[0] == "acc":
                _, val = ev
                f.write(f"A {val & 0xFFFFFFFF:08x}\n")


def run_r2():
    u = 2.0 ** -(E3M6_N + 3)  # u_E3M6 = 2^-7
    C_env = 8.0
    n_conv = 0
    env_fail = 0
    overflow_hits = 0
    sol_errs = []

    for trial in range(N_SYS):
        rng = np.random.default_rng(_seed("dd_random", 8, trial))
        A, b = J.make_dd_random(8, rng)
        ref = J.solve_fp64(A, b)
        res = solve_e3m6_block_mac(A, b)
        if res["overflow"]:
            overflow_hits += 1
        if res["converged"]:
            n_conv += 1
            kappa = J.cond_inf(A)
            env = C_env * kappa * u * max(np.linalg.norm(ref["x"], np.inf), 1.0)
            err = np.linalg.norm(res["x"] - ref["x"], np.inf)
            sol_errs.append(err)
            if err > env:
                env_fail += 1

    med_err = sorted(sol_errs)[len(sol_errs) // 2] if sol_errs else float("nan")
    lines = [
        "PHASE 4b — MAC-faithful solver R2 (DD N=8, 200 systems)",
        f"converged: {n_conv}/{N_SYS}",
        f"K3 envelope violations: {env_fail}/{n_conv if n_conv else 0}",
        f"32-bit overflow hits: {overflow_hits}",
        f"median ||x-x_ref||_inf: {med_err:.6e}",
        f"R2 PASS: {n_conv == N_SYS and env_fail == 0 and overflow_hits == 0}",
    ]
    text = "\n".join(lines) + "\n"
    with open(R2_LOG, "w") as f:
        f.write(text)
    print(text)
    return n_conv, env_fail, overflow_hits


def main():
    print("=" * 66)
    print("PHASE 4b — width-preserving MAC model + goldens")
    print("=" * 66)

    pairs = _load_operand_pairs(R.GOLDEN_HEX)
    print(f"Loaded {len(pairs)} operand pairs from JACOBI_E3M6_GOLDEN.hex")
    emit_product_golden(pairs)
    print(f"Product golden: {len(pairs)} pairs → {os.path.basename(PRODUCT_GOLDEN)}")

    steps = emit_acc_golden()
    write_acc_golden(steps)
    print(f"Accumulate golden: {len(steps)} events → {os.path.basename(ACC_GOLDEN)}")

    print("\n-- R2: MAC-faithful solver over 200 DD N=8 systems --")
    n_conv, env_fail, ovf = run_r2()
    if n_conv != N_SYS or env_fail != 0 or ovf != 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
