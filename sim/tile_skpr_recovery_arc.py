#!/usr/bin/env python3
# SPDX-License-Identifier: CERN-OHL-S-2.0
# =============================================================================
# tile_skpr_recovery_arc.py — Decisive A/B recovery comparison
#
#   A: norm_e_max      → skpr   (LOCALMAX)
#   B: block_scale_out → skpr   (survivor when Rule 5 flags)
#   O: oracle skpr on the clean (unspiked) block e_max
#
# Answers whether tile-level detect → block_scale_out placement recovers
# keeper state the way software SWITCH / survivor-scale feeding expects.
# LLM perplexity is not available in-repo; metrics below are the
# hardware-faithful proxies for that recovery claim.
#
# crush_* columns contextualize SAT/KEEP element intervene (not the B feed).
# =============================================================================

from __future__ import annotations

import argparse
import csv
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from skpr_golden import (
    EXP_MASK, calibrate_T, detect_and_clip, lfsr_stream, pack,
    rand_block_clean, unpack,
)
from scale_keeper_golden import ScaleKeeper, W_CAL

PERSIST_Q = 256
GUARD_Q = 512
BASE_MU = 24


def block_e_max(blk):
    return max((e >> 6) & EXP_MASK for e in blk)


def inject_spike(blk, pos, gap):
    out = list(blk)
    s, ex, ma = unpack(out[pos])
    out[pos] = pack(s, min(EXP_MASK, ex + gap), ma)
    return out


def make_clean_stream(n, seed, mu=BASE_MU):
    gen = lfsr_stream(seed)
    return [rand_block_clean(gen, mu=mu, spread=2) for _ in range(n)]


def apply_faults(clean_blocks, regime, seed, T):
    """
    Fault schedules chosen to separate mechanisms:

    clean       — no spikes
    calibrated  — sparse single-block spikes (gap=T+1). Rule 2 ceiling
                  exclusion often protects LOCALMAX→skpr alone; this cell
                  measures false-flag / inertness, not B's unique value.
    adversarial — bursts of K=4 consecutive heavy spikes. Persistence gate
                  reseeds A to the poisoned LOCALMAX; B feeds survivor and
                  should keep state localized near the oracle. This is the
                  decisive cell for block_scale_out → skpr.
    """
    from scale_keeper_golden import K as KEEPER_K

    rng = random.Random(seed ^ 0xF4A17)
    n = len(clean_blocks)
    fault_at = [0] * n
    gap_at = [0] * n

    if regime == "clean":
        pass
    elif regime == "calibrated":
        gap = T + 1
        for i in range(W_CAL, n, 32):
            fault_at[i] = 1
            gap_at[i] = gap
    elif regime == "adversarial":
        gap = T + 8
        # Burst every 48 blocks: K consecutive spikes to force Rule-2 reseed on A
        i = W_CAL + 8
        while i + KEEPER_K <= n:
            for k in range(KEEPER_K):
                fault_at[i + k] = 1
                gap_at[i + k] = gap
            i += 48
    else:
        raise ValueError(regime)

    obs, meta = [], []
    for i, b in enumerate(clean_blocks):
        if not fault_at[i]:
            obs.append(list(b))
            meta.append({"fault": 0, "pos": -1, "gap": 0})
            continue
        pos = rng.randrange(8)
        spiked = inject_spike(b, pos, gap_at[i])
        if regime == "adversarial" and rng.random() < 0.3:
            pos2 = (pos + rng.randrange(1, 8)) % 8
            spiked = inject_spike(spiked, pos2, max(1, gap_at[i] // 2))
        obs.append(spiked)
        meta.append({"fault": 1, "pos": pos, "gap": gap_at[i]})
    return obs, meta


def run_keepers(obs_blocks, clean_blocks, T):
    ka = ScaleKeeper(PERSIST_Q, GUARD_Q)
    kb = ScaleKeeper(PERSIST_Q, GUARD_Q)
    ko = ScaleKeeper(PERSIST_Q, GUARD_Q)
    rows = []
    for i, (obs, clean) in enumerate(zip(obs_blocks, clean_blocks)):
        d = detect_and_clip(obs, T, "SAT")
        localmax = d["e_max"]
        feed_a = localmax
        feed_b = d["e_second"] if d["flag"] else localmax
        feed_o = block_e_max(clean)
        ra = ka.process_block(feed_a, i)
        rb = kb.process_block(feed_b, i)
        ro = ko.process_block(feed_o, i)
        honest = sorted(((e >> 6) & EXP_MASK) for e in obs)[-2]
        crush_a = max(0, localmax - honest)
        crush_sat = 0 if d["flag"] else crush_a
        rows.append({
            "i": i, "flag": d["flag"],
            "feed_a": feed_a, "feed_b": feed_b, "feed_o": feed_o,
            "state_a": ra[0], "state_b": rb[0], "state_o": ro[0],
            "tag_a": ra[2], "tag_b": rb[2], "tag_o": ro[2],
            "crush_localmax": crush_a, "crush_sat": crush_sat,
        })
    return rows


def summarize(rows, meta, regime, seed, T):
    n = len(rows)
    post = [r for r in rows if r["i"] >= W_CAL]
    n_post = len(post)
    n_fault = sum(1 for m in meta[W_CAL:] if m["fault"])

    def mae(key_s):
        return sum(abs(r[key_s] - r["state_o"]) for r in post) / max(1, n_post)

    flag_rate = sum(r["flag"] for r in post) / max(1, n_post)
    false_int = true_int = 0
    for r, m in zip(rows[W_CAL:], meta[W_CAL:]):
        if r["flag"] and not m["fault"]:
            false_int += 1
        if r["flag"] and m["fault"]:
            true_int += 1
    false_rate = false_int / max(1, n_post)
    recall = true_int / max(1, n_fault) if n_fault else float("nan")

    tag_mismatch_a = sum(1 for r in post if r["tag_a"] != r["tag_o"]) / max(1, n_post)
    tag_mismatch_b = sum(1 for r in post if r["tag_b"] != r["tag_o"]) / max(1, n_post)

    def recovery_delays(path):
        delays = []
        i = W_CAL
        while i < n:
            if meta[i]["fault"]:
                dly = 64
                for j in range(i, min(n, i + 64)):
                    if abs(rows[j][path] - rows[j]["state_o"]) <= 1:
                        dly = j - i
                        break
                delays.append(dly)
            i += 1
        return delays

    dly_a = recovery_delays("state_a")
    dly_b = recovery_delays("state_b")

    def post_fault_mae(path, window=16):
        acc, cnt = 0.0, 0
        for i, m in enumerate(meta):
            if i < W_CAL or not m["fault"]:
                continue
            for j in range(i, min(n, i + window)):
                acc += abs(rows[j][path] - rows[j]["state_o"])
                cnt += 1
        return acc / max(1, cnt)

    acc_a = sum(1 for r in post if abs(r["state_a"] - r["state_o"]) <= 1) / max(1, n_post)
    acc_b = sum(1 for r in post if abs(r["state_b"] - r["state_o"]) <= 1) / max(1, n_post)
    mae_a, mae_b = mae("state_a"), mae("state_b")
    pf_a, pf_b = post_fault_mae("state_a"), post_fault_mae("state_b")

    return {
        "regime": regime,
        "seed": seed,
        "T": T,
        "n_blocks": n,
        "n_post": n_post,
        "n_fault": n_fault,
        "flag_rate": flag_rate,
        "false_intervention_rate": false_rate,
        "fault_recall": recall,
        "keeper_mae_A": mae_a,
        "keeper_mae_B": mae_b,
        "keeper_acc_A": acc_a,
        "keeper_acc_B": acc_b,
        "tag_mismatch_A": tag_mismatch_a,
        "tag_mismatch_B": tag_mismatch_b,
        "mean_recovery_delay_A": (sum(dly_a) / len(dly_a)) if dly_a else 0.0,
        "mean_recovery_delay_B": (sum(dly_b) / len(dly_b)) if dly_b else 0.0,
        "post_fault_mae_A": pf_a,
        "post_fault_mae_B": pf_b,
        "mean_crush_localmax": sum(r["crush_localmax"] for r in post) / max(1, n_post),
        "mean_crush_sat": sum(r["crush_sat"] for r in post) / max(1, n_post),
        "cycles_per_block_tight": 10,
        "B_beats_A_mae": mae_b < mae_a - 1e-12,
        "B_localized": (pf_b < pf_a * 0.5) if n_fault else True,
    }


def emit_rtl_stim(path, obs_blocks, T):
    with open(path, "w") as f:
        f.write(f"{T}\n")
        for blk in obs_blocks:
            d = detect_and_clip(blk, T, "SAT")
            feed_a = d["e_max"]
            feed_b = d["e_second"] if d["flag"] else d["e_max"]
            hexes = " ".join(f"{x:04x}" for x in blk)
            f.write(f"{hexes} {d['flag']} {feed_a} {feed_b}\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=512)
    ap.add_argument("--seeds", type=int, nargs="+",
                    default=[0xA11CE, 0xBEEF1, 0xC0FFEE, 0xD15EA5E, 0xE5ED])
    ap.add_argument("--out", type=str, default="TILE_SKPR_RECOVERY.csv")
    ap.add_argument("--stim", type=str, default="tile_skpr_recovery_stim.txt")
    ap.add_argument("--json", type=str, default="TILE_SKPR_RECOVERY_SUMMARY.json")
    args = ap.parse_args()

    cal_blocks = make_clean_stream(2048, seed=0x0C1EA401)
    gaps = []
    for b in cal_blocks:
        exps = [(e >> 6) & EXP_MASK for e in b]
        mx = max(exps)
        rem = list(exps)
        rem.remove(mx)
        gaps.append(mx - max(rem))
    T, cal_rate = calibrate_T(gaps, target_rate=0.0025)

    regimes = ["clean", "calibrated", "adversarial"]
    summaries = []
    stim_seed = args.seeds[0]

    print(f"[cal] T={T} clean_flag_rate={cal_rate:.4%} (target ≤0.25%)")
    print(f"{'regime':<12} {'seed':>10} {'flag%':>8} {'false%':>8} "
          f"{'maeA':>7} {'maeB':>7} {'accA':>7} {'accB':>7} "
          f"{'dlyA':>6} {'dlyB':>6} {'pfA':>6} {'pfB':>6}  verdict")

    for regime in regimes:
        for seed in args.seeds:
            clean = make_clean_stream(args.n, seed)
            obs, meta = apply_faults(clean, regime, seed, T)
            rows = run_keepers(obs, clean, T)
            s = summarize(rows, meta, regime, seed, T)
            if regime == "clean":
                v = ("CLEAN-OK" if s["keeper_mae_B"] <= 0.5
                     and s["false_intervention_rate"] < 0.01 else "CLEAN-WARN")
            elif regime == "calibrated":
                # Isolated spikes: Rule 2 may already shield A — report tie honestly
                if s["B_beats_A_mae"] and s["B_localized"]:
                    v = "B-RECOVERS"
                elif abs(s["keeper_mae_A"] - s["keeper_mae_B"]) < 1e-9 and s["keeper_mae_A"] < 0.5:
                    v = "TIE-R2-SHIELDS-A"
                elif s["B_beats_A_mae"]:
                    v = "B-BETTER"
                else:
                    v = "NO-GAIN"
            else:  # adversarial bursts — decisive
                if s["B_beats_A_mae"] and s["B_localized"]:
                    v = "B-RECOVERS"
                elif s["B_beats_A_mae"]:
                    v = "B-BETTER"
                else:
                    v = "NO-GAIN"
            s["verdict"] = v
            summaries.append(s)
            print(f"{regime:<12} {seed:#010x} {100*s['flag_rate']:7.3f}% "
                  f"{100*s['false_intervention_rate']:7.3f}% "
                  f"{s['keeper_mae_A']:7.3f} {s['keeper_mae_B']:7.3f} "
                  f"{100*s['keeper_acc_A']:6.2f}% {100*s['keeper_acc_B']:6.2f}% "
                  f"{s['mean_recovery_delay_A']:6.2f} {s['mean_recovery_delay_B']:6.2f} "
                  f"{s['post_fault_mae_A']:6.2f} {s['post_fault_mae_B']:6.2f}  {v}")

            if regime == "adversarial" and seed == stim_seed:
                emit_rtl_stim(args.stim, obs, T)

    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(summaries[0].keys()))
        w.writeheader()
        w.writerows(summaries)

    adv_cells = [s for s in summaries if s["regime"] == "adversarial"]
    cal_cells = [s for s in summaries if s["regime"] == "calibrated"]
    n_rec = sum(1 for s in adv_cells if s["verdict"] == "B-RECOVERS")
    n_better = sum(1 for s in adv_cells if s["verdict"] in ("B-RECOVERS", "B-BETTER"))
    clean_ok = all(s["verdict"] == "CLEAN-OK" for s in summaries if s["regime"] == "clean")
    cal_ok = all(s["verdict"] in ("TIE-R2-SHIELDS-A", "B-RECOVERS", "B-BETTER")
                 for s in cal_cells)

    if clean_ok and n_rec == len(adv_cells) and len(adv_cells) > 0:
        decisive = "PASS_B_JUSTIFIES_DETECT"
    elif clean_ok and n_better == len(adv_cells) and len(adv_cells) > 0:
        decisive = "PASS_B_HELPS"
    elif n_better == 0:
        decisive = "FALSIFIED_NO_RECOVERY_GAIN"
    else:
        decisive = "MIXED"

    claim = {
        "T_cal": T,
        "cal_flag_rate": cal_rate,
        "n_adversarial_cells": len(adv_cells),
        "n_B_recovers": n_rec,
        "n_B_beats_A": n_better,
        "clean_ok": clean_ok,
        "calibrated_ok": cal_ok,
        "decisive": decisive,
        "note": (
            "Keeper-state fidelity vs clean oracle. No LLM perplexity in-repo. "
            "Decisive cells = adversarial K-bursts (reseed poison on A). "
            "Calibrated singles often TIE because Rule 2 excludes LOCALMAX outliers. "
            "mean_crush_* = element-floor proxy (SAT intervene vs LOCALMAX)."
        ),
        "cells": summaries,
    }
    with open(args.json, "w") as f:
        json.dump(claim, f, indent=2)

    print()
    print(f"[decisive] {decisive}  "
          f"(adversarial B-RECOVERS {n_rec}/{len(adv_cells)}, "
          f"B-beats-A {n_better}/{len(adv_cells)}, "
          f"clean_ok={clean_ok}, calibrated_ok={cal_ok})")
    print(f"[write] {args.out}  {args.json}  stim={args.stim}")
    return 0 if decisive != "FALSIFIED_NO_RECOVERY_GAIN" else 1


if __name__ == "__main__":
    sys.exit(main())
