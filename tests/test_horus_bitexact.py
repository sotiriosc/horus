#!/usr/bin/env python3
# SPDX-License-Identifier: CERN-OHL-S-2.0
"""Phase-1 equivalence: runtime vs skpr_golden / scale_keeper_golden."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SIM = ROOT / "sim"
sys.path[:0] = [str(SIM), str(ROOT)]

from horus_block_runtime import HorusBlockRuntime, build_fault_plan, process_tensor_with_plan
from horus_nfe_bitexact import encode_float, pack
from rule5_bitexact import detect, detect_and_intervene
from skpr_bitexact import SkprBitExact
from skpr_golden import detect_and_clip, directed_vectors, lfsr_stream, rand_block
from scale_keeper_golden import ScaleKeeper
import numpy as np

OUT = ROOT / "results" / "llm_horus_campaign" / "equivalence"
OUT.mkdir(parents=True, exist_ok=True)


def test_detect_vs_golden():
    mismatches = 0
    first = None
    T = 13
    for name, blk in directed_vectors(T):
        for mode in ("SAT", "KEEP"):
            g = detect_and_clip(blk, T, mode)
            r = detect_and_intervene(blk, T, mode)
            if (r["flag"] != g["flag"] or r["e_second"] != g["e_second"]
                    or r["e_max"] != g["e_max"] or r["out"] != g["out"]):
                mismatches += 1
                if first is None:
                    first = {"name": name, "mode": mode, "g": g, "r": r}
    gen = lfsr_stream(0xDEAD5CA1)
    for i in range(2000):
        blk = rand_block(gen)
        g = detect_and_clip(blk, T, "SAT")
        d = detect(blk, T)
        if d["flag"] != g["flag"] or d["block_scale"] != (g["e_second"] if g["flag"] else g["e_max"]):
            mismatches += 1
            if first is None:
                first = {"i": i, "g": g, "d": d}
    assert mismatches == 0, first
    return {"detect_mismatches": 0, "n": 2000 + len(directed_vectors(T)) * 2}


def test_keeper_vs_golden():
    stream = [20] * 64 + [20, 20, 35, 35, 35, 35, 20, 20] + [20] * 32
    a = ScaleKeeper(256, 512)
    b = SkprBitExact(256, 512)
    mism = 0
    for i, e in enumerate(stream):
        ra = a.process_block(e, i)
        rb = b.process(e, i)
        if ra[0] != rb["state_exp"] or ra[2] != rb["tag"]:
            mism += 1
    assert mism == 0
    return {"keeper_mismatches": 0, "n": len(stream)}


def test_runtime_feeds_a_b():
    T = 13
    # one clean + one spiked block through A vs B
    vals = [1.0] * 8
    words = [encode_float(v) for v in vals]
    # build float spike via runtime fault
    ra = HorusBlockRuntime("R3A", T)
    rb = HorusBlockRuntime("R3B", T)
    ra.process_block(vals, fault=False)
    rb.process_block(vals, fault=False)
    ra.process_block(vals, fault=True, fault_pos=0, fault_gap=T + 8, clean_for_oracle=vals)
    rb.process_block(vals, fault=True, fault_pos=0, fault_gap=T + 8, clean_for_oracle=vals)
    fa = ra.stats.keeper_rows[-1]["feed"]
    fb = rb.stats.keeper_rows[-1]["feed"]
    assert fa > fb, (fa, fb)  # LOCALMAX > survivor when flagged
    assert rb.stats.keeper_rows[-1]["flag"] == 1
    return {"feed_a": fa, "feed_b": fb}


def test_fault_plan_burst():
    plan = build_fault_plan(200, "burst_K4", T=13, fault_seed=1)
    assert len(plan) >= 4
    return {"n_fault_blocks": len(plan)}


def main():
    results = {}
    results["detect"] = test_detect_vs_golden()
    results["keeper"] = test_keeper_vs_golden()
    results["feeds"] = test_runtime_feeds_a_b()
    results["plan"] = test_fault_plan_burst()
    results["verdict"] = "PASS"
    path = OUT / "phase1_equivalence.json"
    path.write_text(json.dumps(results, indent=2))
    print(json.dumps(results, indent=2))
    print("PASS", path)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as e:
        fail = {"verdict": "FALSIFIED", "error": repr(e)}
        (OUT / "phase1_equivalence.json").write_text(json.dumps(fail, indent=2))
        print(fail)
        raise
