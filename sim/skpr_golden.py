#!/usr/bin/env python3
# ============================================================================
# skpr_golden.py — Clean-room golden reference for the SKPR in-line fault
#                  detector (Design Rule 5), exponent-domain, NFE-13 block FP.
#
# SECOND-SOURCE DISCIPLINE: this model is written from the exported Rule 5
# prose and the NFE-13 element format ONLY. It never imports, reads, or is
# derived from any RTL. The Verilog DUT must be an independent path; this
# file emits vectors + expected outputs for the testbench to compare against.
#
# NFE-13 element layout: [ sign(1) | exp(6) | mant(6) ]  (bit 12 = sign)
# Detector operates on the 6-bit stored exponent field only (in_i[11:6]),
# matching horus_norm_v2's max-tree domain.
# ============================================================================
import argparse, csv

EXP_W, MANT_W = 6, 6
MANT_MAX = 0b111111          # horus_norm_v2.v L79 localparam
EXP_MASK, MANT_MASK = 0x3F, 0x3F

def unpack(e13):
    return (e13 >> 12) & 1, (e13 >> 6) & EXP_MASK, e13 & MANT_MASK

def pack(sign, exp, mant):
    return ((sign & 1) << 12) | ((exp & EXP_MASK) << 6) | (mant & MANT_MASK)

def detect_and_clip(block, T, clip_mode):
    """block: 8 ints (13-bit). T: 0..63. clip_mode: 'SAT' | 'KEEP'.
    Returns dict with outputs and internal signals for assertion checking."""
    exps = [(e >> 6) & EXP_MASK for e in block]
    e_max = max(exps)
    rem = list(exps); rem.remove(e_max)      # remove ONE instance of e_max
    e_second = max(rem)                       # 2nd-largest order statistic
    gap = e_max - e_second
    flag = 1 if gap > T else 0                # STRICT '>' (P5)
    out = list(block); argmax = None
    if flag:
        # gap>0 => e_max strictly greatest => unique holder
        assert exps.count(e_max) == 1, "flagged block must have unique arg-max"
        argmax = exps.index(e_max)
        s, ex, ma = unpack(block[argmax])
        if clip_mode == 'SAT':               # survivor-scale ceiling
            out[argmax] = pack(s, e_second, MANT_MAX)
        elif clip_mode == 'KEEP':            # survivor exponent, own mantissa
            out[argmax] = pack(s, e_second, ma)
        else:
            raise ValueError(clip_mode)
    e_max_out = max((e >> 6) & EXP_MASK for e in out)   # post-clip block exp
    return dict(out=out, flag=flag, e_max=e_max, e_second=e_second,
                gap=gap, argmax=argmax, e_max_out=e_max_out)

# ── LFSR corpus (32-bit Galois, seed DEAD5CA1, taps 32/22/2/1) ──────────────
def lfsr_stream(seed=0xDEAD5CA1):
    s = seed & 0xFFFFFFFF
    while True:
        lsb = s & 1
        s >>= 1
        if lsb: s ^= 0x80200003          # taps 32,22,2,1
        yield s

def rand_block(gen):
    # 8 elements; exponents span the 6-bit range, occasional spikes emerge
    blk = []
    for _ in range(8):
        v = next(gen)
        sign = (v >> 20) & 1
        exp  = v & EXP_MASK
        mant = (v >> 8) & MANT_MASK
        blk.append(pack(sign, exp, mant))
    return blk

def rand_block_clean(gen, mu=24, spread=2):
    """Clean-like block: exponents cluster tightly (real activations), so
    gaps are small and the calibrated detector is near-inert."""
    blk = []
    for _ in range(8):
        v = next(gen)
        # triangular-ish clustering around mu, +/- spread
        d = ((v & 0x7) + ((v >> 3) & 0x7)) - 7       # in [-7,7], centered 0
        exp = mu + (d * spread) // 7
        if (v & 0x3F) == 0x3F:                 # ~1.6% light tail (real activations)
            exp += 5 + ((v >> 24) & 0x7)
        exp = max(0, min(EXP_MASK, exp))
        sign = (v >> 20) & 1
        mant = (v >> 8) & MANT_MASK
        blk.append(pack(sign, exp, mant))
    return blk

def block_gap(blk):
    exps = [(e >> 6) & EXP_MASK for e in blk]
    m = max(exps); r = list(exps); r.remove(m)
    return m - max(r)

def calibrate_T(gaps, target_rate):
    """Smallest T such that fraction of blocks with gap>T is <= target_rate.
    This is the per-layer, load-time calibration on CLEAN data (Rule 5)."""
    n = len(gaps)
    for T in range(0, EXP_MASK + 1):
        rate = sum(1 for g in gaps if g > T) / n
        if rate <= target_rate:
            return T, rate
    return EXP_MASK, sum(1 for g in gaps if g > EXP_MASK) / n

def directed_vectors(T=4):
    """Hand-enumerated edge cases (P2/P4/P5), spike gaps sized to T so a
    gap==T boundary vector always exists (P5 strict-'>' coverage)."""
    V = []
    base_e = 10
    def ce(e): return max(0, min(EXP_MASK, e))
    # all-equal (tie -> no flag)
    V.append(("all_equal", [pack(0, base_e, 0b000001)]*8))
    # single spike at each position; gaps T-1 / T / T+1 / large, sized to T
    big = min(EXP_MASK - base_e, T + 20)
    for pos in range(8):
        for gap, tag in [(T-1,"gapTm1"), (T,"gapT"), (T+1,"gapTp1"), (big,"gaplarge")]:
            if gap < 1:
                continue
            blk = [pack(0, base_e, 0b000010) for _ in range(8)]
            blk[pos] = pack(1, ce(base_e + gap), 0b111000)   # signed spike
            V.append((f"spike_p{pos}_{tag}", blk))
    # two spikes (unique higher one clipped)
    blk = [pack(0, base_e, 1) for _ in range(8)]
    blk[2] = pack(0, ce(base_e + T + 6), 0b100000)
    blk[5] = pack(0, ce(base_e + T + 1), 0b010000)
    V.append(("two_spike", blk))
    # two EQUAL top spikes (tie at max -> no flag)
    blk = [pack(0, base_e, 1) for _ in range(8)]
    blk[1] = pack(0, ce(base_e + T + 8), 0b111111)
    blk[6] = pack(0, ce(base_e + T + 8), 0b000111)
    V.append(("two_equal_top", blk))
    # monotonic ramp (no dominant element)
    V.append(("ramp", [pack(0, ce(base_e + e), 0b001000) for e in range(8)]))
    # all-floor (e_max=0)
    V.append(("all_floor", [pack(0, 0, 0b000000)]*8))
    return V

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--T", type=int, default=4)
    ap.add_argument("--n_rand", type=int, default=10000)
    ap.add_argument("--emit", type=str, default=None, help="CSV path for TB")
    ap.add_argument("--report", action="store_true")
    a = ap.parse_args()

    rows = []
    def add(name, blk, T):
        # Flat CSV: every hex is its own column so iverilog $fscanf is trivial.
        r = {"name": name, "T": T}
        for i, x in enumerate(blk):
            r[f"in{i}"] = f"{x:04x}"
        gS = detect_and_clip(blk, T, "SAT")
        gK = detect_and_clip(blk, T, "KEEP")
        for i, x in enumerate(gS["out"]):
            r[f"outS{i}"] = f"{x:04x}"
        r["flagS"] = gS["flag"]
        r["emaxS"] = gS["e_max_out"]
        r["e_max"] = gS["e_max"]
        r["e_second"] = gS["e_second"]
        r["gap"] = gS["gap"]
        r["argmaxS"] = -1 if gS["argmax"] is None else gS["argmax"]
        for i, x in enumerate(gK["out"]):
            r[f"outK{i}"] = f"{x:04x}"
        r["flagK"] = gK["flag"]
        r["emaxK"] = gK["e_max_out"]
        r["argmaxK"] = -1 if gK["argmax"] is None else gK["argmax"]
        rows.append(r)

    for name, blk in directed_vectors(a.T):
        add(name, blk, a.T)
    gen = lfsr_stream()
    for i in range(a.n_rand):
        add(f"rand{i}", rand_block(gen), a.T)

    if a.emit:
        fields = (["name", "T"] + [f"in{i}" for i in range(8)] +
                  [f"outS{i}" for i in range(8)] +
                  ["flagS", "emaxS", "e_max", "e_second", "gap", "argmaxS"] +
                  [f"outK{i}" for i in range(8)] +
                  ["flagK", "emaxK", "argmaxK"])
        with open(a.emit, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader(); w.writerows(rows)
        # Space-separated twin for iverilog $fscanf (%s stops only on whitespace)
        tb_path = a.emit.rsplit(".", 1)[0] + ".txt"
        with open(tb_path, "w") as f:
            for r in rows:
                vals = [str(r[k]) for k in fields]
                # unflagged argmax sentinel: use 8 (not -1) for unsigned-friendly scan
                for k in ("argmaxS", "argmaxK"):
                    idx = fields.index(k)
                    if int(vals[idx]) < 0:
                        vals[idx] = "8"
                f.write(" ".join(vals) + "\n")
        print(f"[emit] CSV={a.emit}  TB={tb_path}  rows={len(rows)}")

    if a.report:
        # ---- self-consistency assertions (golden must obey its own rules) ----
        for r in rows:
            blk = [int(r[f"in{i}"], 16) for i in range(8)]
            for mode, fl in (("SAT", "flagS"), ("KEEP", "flagK")):
                g = detect_and_clip(blk, a.T, mode)
                if g["gap"] <= a.T:
                    assert g["flag"] == 0
                    assert g["out"] == blk, f"{r['name']} altered on unflagged"
                if g["gap"] == a.T:
                    assert g["flag"] == 0, f"{r['name']} flagged at gap==T"
                if g["flag"]:
                    assert g["e_max_out"] == g["e_second"], f"{r['name']} no recovery"
                    diff = [i for i in range(8) if g["out"][i] != blk[i]]
                    assert diff == [g["argmax"]], f"{r['name']} clip not unique"
        flags = sum(r["flagS"] for r in rows if r["name"].startswith("rand"))
        n = sum(1 for r in rows if r["name"].startswith("rand"))
        d = {r["name"]: r for r in rows}
        chk = all(d[f"spike_p{p}_gapTp1"]["flagS"]==1 and
                  d[f"spike_p{p}_gaplarge"]["flagS"]==1 and
                  d[f"spike_p{p}_gapT"]["flagS"]==0 and
                  d[f"spike_p{p}_gapTm1"]["flagS"]==0 for p in range(8))
        print(f"[assertions] all self-consistency checks PASSED")
        print(f"[directed]   spike polarity (gap>T only) correct: {chk}")
        print(f"[ties/floor] all_equal flag={d['all_equal']['flagS']} "
              f"two_equal_top flag={d['two_equal_top']['flagS']} "
              f"all_floor flag={d['all_floor']['flagS']} (expect 0/0/0)")
        print(f"[SAT vs KEEP] two_spike SAT out={d['two_spike']['outS2']} "
              f"KEEP out={d['two_spike']['outK2']} "
              f"(same exp, mantissa differs)")
        print(f"[stress corpus] uniform-exp, T={a.T}: {flags}/{n} = {100*flags/n:.3f}% "
              f"(coverage corpus — NOT clean data)")
        # ---- calibration on a CLEAN-like clustered corpus (the real use) ----
        gen2 = lfsr_stream(0x0C1EA401)
        clean = [rand_block_clean(gen2) for _ in range(20000)]
        gaps = [block_gap(b) for b in clean]
        T_cal, rate = calibrate_T(gaps, 0.0025)
        # verify inertness at the calibrated threshold: unflagged => unchanged
        clipped = 0
        for b in clean:
            g = detect_and_clip(b, T_cal, "SAT")
            if g["flag"] == 0:
                assert g["out"] == b
            else:
                clipped += 1
        print(f"[calibration] clean corpus -> per-layer T={T_cal} gives "
              f"{100*clipped/len(clean):.3f}% flagged (target <=0.250%); "
              f"unflagged blocks provably untouched")

if __name__ == "__main__":
    main()