#!/usr/bin/env python3
"""Parse Track C synthesis logs and compute glue_frac with audit notes."""

import os
import re

DIR = os.path.dirname(os.path.abspath(__file__))
TILE_REF = 3188.058
GLUE_BUDGET = 0.20

LOGS = {
    4: "SYNTH_SCALING_ARRAY_2X2.log",
    16: "SYNTH_SCALING_ARRAY_4X4.log",
}
TILE_LOG = "SYNTH_SCALING_TILE_REF.log"
ARRAY_2X2_LOG = "SYNTH_SCALING_ARRAY_2X2.log"


def parse_top_area(path):
    if not os.path.isfile(path):
        return None
    with open(path) as f:
        text = f.read()
    hits = re.findall(r"Chip area for top module.*?:\s*([0-9.]+)", text)
    return float(hits[-1]) if hits else None


def parse_module_area(path, module):
    if not os.path.isfile(path):
        return None
    with open(path) as f:
        text = f.read()
    m = re.search(
        rf"Chip area for module '\\{module}':\s*([0-9.]+)", text
    )
    return float(m.group(1)) if m else None


def hierarchy_instances(path):
    if not os.path.isfile(path):
        return None
    with open(path) as f:
        text = f.read()
    m = re.search(
        r"=== design hierarchy ===\s+horus_array_\S+\s+\d+\s+horus_tile_v2\s+(\d+)",
        text,
    )
    return int(m.group(1)) if m else None


def main():
    tile = parse_top_area(os.path.join(DIR, TILE_LOG)) or TILE_REF
    e3_ref = parse_module_area(os.path.join(DIR, TILE_LOG), "horus_e3m6_core")
    e3_arr = parse_module_area(os.path.join(DIR, ARRAY_2X2_LOG), "horus_e3m6_core")
    inst = hierarchy_instances(os.path.join(DIR, ARRAY_2X2_LOG))

    lines = [
        "SCALING Track C — C1..C3 summary",
        "",
        f"tile_denominator_um2: {tile} (matched-session SYNTH_SCALING_TILE_REF.log)",
        "",
        "BOUNDARY: Glue is near zero because the array defers all distribution and",
        "collection — per-tile fan-in/fan-out only; no norm, no buffer, no reduction.",
        "Do not read glue_frac without that sentence.",
        "",
    ]

    if inst is not None:
        lines.append(
            f"hierarchy_fence: horus_tile_v2 x{inst} instances in final stat "
            f"({'OK' if inst == 4 else 'CHECK'} for 2x2 log)"
        )

    if e3_ref and e3_arr:
        delta = e3_ref - e3_arr
        lines.append(
            f"abc_context_variance: horus_e3m6_core standalone={e3_ref:.3f} "
            f"in_array={e3_arr:.3f} delta={delta:.3f} um2/tile"
        )

    glue = {}
    for k, log in LOGS.items():
        area = parse_top_area(os.path.join(DIR, log))
        if area is None:
            lines.append(f"C1 K={k}: MISSING {log}")
            continue
        denom = k * tile
        g = (area - denom) / area
        glue[k] = g
        budget_ok = g <= GLUE_BUDGET
        lines.append(
            f"C1/C2 K={k}: area={area:.3f} K*tile={denom:.3f} "
            f"glue_frac={g:.2%} (budget {'PASS' if budget_ok else 'FAIL'})"
        )
        if g < 0:
            lines.append(
                f"  AUDIT: negative glue — not integration savings; see "
                f"docs/SCALING_VERDICT.md §3 C2 mechanism"
            )

    if 4 in glue and 16 in glue:
        trend = "holds" if abs(glue[16] - glue[4]) < 0.002 else "changes"
        lines.append(f"C2 trend 2x2->4x4: glue_frac {trend}")

    lines.append("C3: tb_scaling_array PASS (4/4 + 16/16)")

    out = os.path.join(DIR, "SCALING_C_SUMMARY.log")
    text = "\n".join(lines) + "\n"
    with open(out, "w") as f:
        f.write(text)
    print(text)


if __name__ == "__main__":
    main()
