#!/usr/bin/env python3
"""Emit per-width MAC goldens for Track B4 (products shared; acc per width)."""

import os
import sys

import numpy as np

DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, DIR)

import jacobi_solver as J
from jacobi_campaign import _seed
from jacobi_mac_model import (
    ACC_CAP,
    emit_product_golden,
    solve_e3m6_block_mac,
    width_bits,
    _load_operand_pairs,
)
import jacobi_rtl_golden as R


def emit_acc_golden(width: int, out_path: str):
    steps = []
    for trial in range(200):
        rng = np.random.default_rng(_seed("dd_random", 8, trial))
        A, b = J.make_dd_random(8, rng)
        tap = []
        solve_e3m6_block_mac(A, b, acc_tap=tap, acc_width=width)
        for ev in tap:
            if len(steps) >= ACC_CAP:
                break
            steps.append(ev)
        if len(steps) >= ACC_CAP:
            break

    mask = (1 << width) - 1
    hexw = (width + 3) // 4
    with open(out_path, "w") as f:
        f.write(f"// SCALING_MAC_ACC_GOLDEN_W{width}.hex\n")
        f.write(f"// {len(steps)} events (cap {ACC_CAP}), ACC_WIDTH={width}.\n")
        for ev in steps:
            if ev[0] == "clear":
                f.write("C 00000000\n")
            elif ev[0] == "term":
                _, a, b = ev
                f.write(f"T {a:03x} {b:03x}\n")
            elif ev[0] == "acc":
                _, val = ev
                f.write(f"A {val & mask:0{hexw}x}\n")


def main():
    pairs = _load_operand_pairs(R.GOLDEN_HEX)
    for w in (32, 34, 36):
        prod_path = os.path.join(DIR, f"SCALING_MAC_PRODUCT_W{w}.hex")
        with open(prod_path, "w") as f:
            f.write(f"// SCALING_MAC_PRODUCT_W{w}.hex — width {w} (products width-independent)\n")
        # copy product golden (identical across widths)
        emit_product_golden(pairs)
        with open(os.path.join(DIR, "JACOBI_MAC_PRODUCT_GOLDEN.hex")) as src:
            data = src.read()
        with open(prod_path, "w") as f:
            f.write(data.replace("JACOBI_MAC_PRODUCT_GOLDEN", f"SCALING_MAC_PRODUCT_W{w}"))
        emit_acc_golden(w, os.path.join(DIR, f"SCALING_MAC_ACC_GOLDEN_W{w}.hex"))
        print(f"W{w}: products={len(pairs)} acc events written")


if __name__ == "__main__":
    main()
