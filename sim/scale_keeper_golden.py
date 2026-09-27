#!/usr/bin/env python3
# SPDX-License-Identifier: CERN-OHL-S-2.0
# =============================================================================
# sim/scale_keeper_golden.py — Clean-room golden model for the Horus Scale Keeper
#
# Public behavior and parameters: docs/SCALE_TRACKING.md.
# Tested parameters: docs/SCALE_TRACKING.md.
#
# AI role: compilation and adversarial review (Claude/Anthropic).
# Architectural decisions: Sotirios Chortogiannos.
#
# All arithmetic is pure Python integer (Q6.8 fixed-point) to enable
# bit-exact comparison with the RTL.  No floating-point is used.
# =============================================================================

# ---------------------------------------------------------------------------
# Tested default parameters (preserved without arithmetic changes)
# ---------------------------------------------------------------------------
FRAC_BITS          = 8           # fractional bits in Q6.FRAC state
ALPHA_SHIFT        = 4           # alpha = 2^(-4) = 1/16
W_CAL              = 64          # calibration window length (blocks)
PTAIL              = 95          # percentile for persistence bound (|dev|)
PTAIL_POS          = 95          # percentile for guard margin (pos dev)
K                  = 4           # persistence gate threshold
N_SETTLE           = 4           # settling period after re-seed (blocks)
GUARD_MARGIN_FLOOR = 1 << FRAC_BITS   # = 256 in Q6.8 = 1 exponent unit

MAX_EXP   = 63
MAX_STATE = (MAX_EXP << FRAC_BITS) | ((1 << FRAC_BITS) - 1)   # 16383

# Sideband tag values (matching RTL encoding in rtl/skpr.v)
TAG_OK       = 0b00   # nominal
TAG_OUTLIER  = 0b01   # block_max > ceiling (excluded)
TAG_SETTLING = 0b10   # counter accumulating toward K
TAG_RESEEDED = 0b11   # re-seed just fired or within settling window


# ---------------------------------------------------------------------------
# Helper: Q6.8 arithmetic-right-shift (matches Verilog >>> on signed wire)
# ---------------------------------------------------------------------------
def _asr(value: int, shift: int) -> int:
    """Arithmetic right shift.  Python >> is already arithmetic for signed ints."""
    return value >> shift


def _clip(v: int) -> int:
    return max(0, min(MAX_STATE, v))


# ---------------------------------------------------------------------------
# ScaleKeeper golden model
# ---------------------------------------------------------------------------
class ScaleKeeper:
    """
    Reference implementation of the four scale-tracking rules described in
    docs/SCALE_TRACKING.md.

    Rule 1 — recovery clock  : leaky integrator, alpha = 1/16 (shift by 4)
    Rule 2 — persistence gate: K=4 consecutive deviations trigger re-seed;
                               ceiling-exceeding blocks excluded from state update
    Rule 3 — guarded ceiling : ceiling = state + guard_margin (calibrated)
    Rule 4 — sideband        : 2-bit per-block tag from block_max + keeper state only

    State is Q6.8 fixed-point (14-bit unsigned integer).
    All arithmetic matches the RTL bit-for-bit.
    """

    def __init__(self, persist_bound_q: int = 512, guard_margin_q: int = 768):
        """
        persist_bound_q : Q6.8 persistence gate bound  (default 2.0 = 512)
        guard_margin_q  : Q6.8 ceiling guard margin    (default 3.0 = 768)
        """
        self.persist_bound_q = persist_bound_q
        self.guard_margin_q  = guard_margin_q
        self._reset()

    def _reset(self):
        self.state_q    = 0   # Q6.8 state
        self.counter    = 0   # persistence gate counter [0..K-1]
        self.settle_cnt = 0   # settling counter [0..N_SETTLE]
        self.events     = []  # [(block_idx, direction '+'/'-', reseeded_to_exp)]

    # ------------------------------------------------------------------
    # Process one block maximum (core per-block logic)
    # Returns: (state_exp, ceiling_exp, tag, event_fired, event_dir)
    #   state_exp   : int 0-63  (integer part of state after update)
    #   ceiling_exp : int 0-63  (integer part of ceiling before update)
    #   tag         : int 0-3   (2-bit sideband)
    #   event_fired : bool
    #   event_dir   : +1 or -1 (signed re-seed direction)
    # ------------------------------------------------------------------
    def process_block(self, e_max: int, block_idx: int = None):
        obs_q = e_max << FRAC_BITS                   # convert to Q6.8

        # Signed deviation (may be negative) — matches Verilog 15-bit signed
        dev_signed = obs_q - self.state_q

        # Absolute deviation
        abs_dev = abs(dev_signed)

        # Guarded ceiling (Rule 3)
        ceiling_q = _clip(self.state_q + self.guard_margin_q)

        # Comparators
        exceed_persist = abs_dev > self.persist_bound_q
        exceed_ceiling = obs_q   > ceiling_q
        fire_reseed    = exceed_persist and (self.counter == K - 1)

        # Leaky integrator update — arithmetic right shift, then saturate (Rule 1)
        alpha_update = _asr(dev_signed, ALPHA_SHIFT)
        new_state_q  = _clip(self.state_q + alpha_update)

        # State machine (priority: fire_reseed > exceed_persist > normal)
        event_fired = False
        event_dir   = 0
        tag         = TAG_OK

        if fire_reseed:
            # Rule 2: re-seed state from current observation
            self.state_q    = obs_q
            self.counter    = 0
            self.settle_cnt = N_SETTLE
            event_fired     = True
            event_dir       = +1 if dev_signed >= 0 else -1
            tag             = TAG_RESEEDED
            if block_idx is not None:
                self.events.append((block_idx,
                                    '+' if event_dir > 0 else '-',
                                    e_max))

        elif exceed_persist:
            self.counter += 1
            # Settle counter ticks even while gate is accumulating
            if self.settle_cnt > 0:
                self.settle_cnt -= 1
            if exceed_ceiling:
                # Rule 2 exclusion: block exceeds ceiling → excluded from state update
                # State unchanged; tag = OUTLIER
                tag = TAG_OUTLIER
            else:
                # Within ceiling but exceed persist bound: apply integrator, count
                self.state_q = new_state_q
                tag = TAG_SETTLING

        else:
            # Not exceeding persist bound: reset counter
            self.counter = 0
            if self.settle_cnt > 0:
                self.settle_cnt -= 1

            if exceed_ceiling:
                # Single outlier: excluded from state update (Rule 2 exclusion)
                tag = TAG_OUTLIER
            else:
                self.state_q = new_state_q
                # Tag depends on whether we're still settling
                tag = TAG_RESEEDED if self.settle_cnt > 0 else TAG_OK

        state_exp   = (self.state_q >> FRAC_BITS) & 0x3F
        ceiling_exp = (ceiling_q    >> FRAC_BITS) & 0x3F
        return state_exp, ceiling_exp, tag, event_fired, event_dir

    # ------------------------------------------------------------------
    # Run a full stream; returns list of result dicts
    # ------------------------------------------------------------------
    def run_stream(self, stream):
        results = []
        for i, e_max in enumerate(stream):
            s_exp, c_exp, tag, ev, evd = self.process_block(e_max, block_idx=i)
            results.append({
                'block'      : i,
                'e_max'      : e_max,
                'state_exp'  : s_exp,
                'ceiling_exp': c_exp,
                'tag'        : tag,
                'event'      : ev,
                'event_dir'  : evd,
                'state_q'    : self.state_q,
                'counter'    : self.counter,
                'settle_cnt' : self.settle_cnt,
            })
        return results

    # ------------------------------------------------------------------
    # Class method: derive bounds from a calibration stream (Rule 2+3)
    # Returns a new ScaleKeeper instance ready for production (state reset to 0)
    # ------------------------------------------------------------------
    @classmethod
    def from_calibration(cls, cal_stream):
        """
        Run W_CAL blocks of calibration to derive persist_bound_q and guard_margin_q.
        Uses a leaky integrator to track the state during calibration; percentile
        of observed deviations gives the bounds.
        Returns a new instance with state reset to 0 and calibrated bounds.
        """
        assert len(cal_stream) >= W_CAL, "Calibration stream too short"
        stream = cal_stream[:W_CAL]

        # Bootstrap: start state from the first observation
        state_q  = stream[0] << FRAC_BITS
        abs_devs = []
        pos_devs = []

        for obs in stream:
            obs_q  = obs << FRAC_BITS
            dev    = obs_q - state_q
            abs_devs.append(abs(dev))
            if dev > 0:
                pos_devs.append(dev)
            # Leaky integrator during calibration (same arithmetic as production)
            update  = _asr(dev, ALPHA_SHIFT)
            state_q = _clip(state_q + update)

        # Persistence bound: PTAIL-th percentile of absolute deviations (Rule 2)
        abs_devs.sort()
        n = len(abs_devs)
        p_idx           = min(int(n * PTAIL / 100), n - 1)
        persist_bound_q = abs_devs[p_idx]

        # Guard margin: PTAIL_POS-th percentile of positive deviations (Rule 3)
        # Floor: GUARD_MARGIN_FLOOR
        if pos_devs:
            pos_devs.sort()
            np_ = len(pos_devs)
            pp_idx         = min(int(np_ * PTAIL_POS / 100), np_ - 1)
            guard_margin_q = max(GUARD_MARGIN_FLOOR, pos_devs[pp_idx])
        else:
            guard_margin_q = GUARD_MARGIN_FLOOR

        inst = cls(persist_bound_q=persist_bound_q, guard_margin_q=guard_margin_q)
        # Reset state to 0 so RTL starting from reset matches exactly
        inst.state_q    = 0
        inst.counter    = 0
        inst.settle_cnt = 0
        return inst
