#!/usr/bin/env python3
"""Smoke-test vectors for tb_scaling_array.v (one distinct pair per tile)."""

import os
import sys

DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, DIR)

from dual_core_model import dual_core_mul
from tile_model import shim_e3m6_to_nfe13, shim_e4m3_to_nfe13


def main():
    # Distinct operand pairs for up to 16 tiles (E3M6 mode smoke).
    pairs = [
        (0x280, 0x280), (0x2C0, 0x240), (0x300, 0x200), (0x340, 0x1C0),
        (0x380, 0x180), (0x3C0, 0x140), (0x400, 0x100), (0x440, 0x0C0),
        (0x480, 0x080), (0x4C0, 0x040), (0x500, 0x000), (0x540, 0x3C0),
        (0x580, 0x380), (0x5C0, 0x340), (0x600, 0x300), (0x640, 0x2C0),
    ]
    out = os.path.join(DIR, "SCALING_ARRAY_SMOKE.hex")
    with open(out, "w") as f:
        f.write("// mode op_a op_b nfe_expected (E3M6 path)\n")
        for op_a, op_b in pairs:
            prod = dual_core_mul(op_a, op_b, mode=0)
            nfe = shim_e3m6_to_nfe13(prod)
            f.write(f"0 {op_a:03x} {op_b:03x} {nfe:04x}\n")
    print(f"Wrote {out} ({len(pairs)} rows)")


if __name__ == "__main__":
    main()
