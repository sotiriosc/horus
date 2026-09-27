// SPDX-License-Identifier: CERN-OHL-S-2.0
// ============================================================================
// Module   : skpr
// File     : rtl/skpr.v
// Date     : 2026-07-16
// Author   : Sotirios Chortogiannos
//
// Purpose  : Hardware scale-keeper for Horus block-exponent / compressed-block
//            modes.  Tracks a running block-exponent estimate in the Q6.8
//            fixed-point domain, detects regime shifts, and emits a 2-bit
//            confidence sideband.
//
//            Public interface and tested parameter documentation:
//            docs/SCALE_TRACKING.md
//            Parameters frozen in docs/SCALE_TRACKING.md.
//
// Interface:
//   Input  : valid_in, e_max_in[5:0]  — block-max exponent from horus_norm_v2
//   Output : (all registered, 1-cycle latency)
//            state_exp_out[5:0]   — integer part of Q6.8 state estimate
//            ceiling_exp_out[5:0] — integer part of guarded ceiling
//            tag_out[1:0]         — sideband: 00=OK 01=OUTLIER 10=SETTLING 11=RESEEDED
//            event_valid_out      — 1-cycle pulse: re-seed fired
//            event_dir_out        — 1=positive re-seed, 0=negative
//
// State update (multiplier-free, Rule 1):
//   alpha = 2^(-ALPHA_SHIFT)  (shift-and-add only)
//   new_state = clip(state + (dev_signed >>> ALPHA_SHIFT))
//
// Persistence gate (Rule 2):
//   K consecutive |dev| > PERSIST_BOUND_Q → re-seed to current observation.
//   Blocks where obs > ceiling excluded from state update (Rule 2 exclusion).
//
// Guarded ceiling (Rule 3):
//   ceiling = clip(state + GUARD_MARGIN_Q)
//
// Sideband (Rule 4):
//   Derivable from block_max and keeper state only — no extra arithmetic.
//
// AI role: compilation and adversarial review (Claude/Anthropic).
// All architectural decisions: Sotirios Chortogiannos.
// ============================================================================

`timescale 1ns / 1ps

module skpr #(
    parameter [2:0]  K           = 3'd4,   // persistence gate threshold
    parameter [2:0]  N_SETTLE    = 3'd4,   // settling period after re-seed
    parameter [3:0]  ALPHA_SHIFT = 4'd4    // alpha = 2^(-ALPHA_SHIFT)
) (
    input  wire        clk,
    input  wire        rst_n,
    input  wire        valid_in,
    input  wire [5:0]  e_max_in,          // block maximum from horus_norm_v2.e_max_out
    input  wire [13:0] persist_bound_q,   // Q6.8 persistence gate bound (calibrated)
    input  wire [13:0] guard_margin_q,    // Q6.8 ceiling guard margin  (calibrated)

    output reg  [5:0]  state_exp_out,    // integer part of state estimate
    output reg  [5:0]  ceiling_exp_out,  // integer part of guarded ceiling
    output reg  [1:0]  tag_out,          // 2-bit confidence sideband
    output reg         event_valid_out,  // re-seed event pulse
    output reg         event_dir_out     // 1=positive step, 0=negative step
);

    // ── Tag constants (matching scale_keeper_golden.py) ───────────────────────
    localparam [1:0] TAG_OK       = 2'b00;
    localparam [1:0] TAG_OUTLIER  = 2'b01;
    localparam [1:0] TAG_SETTLING = 2'b10;
    localparam [1:0] TAG_RESEEDED = 2'b11;

    // ── Internal state registers ───────────────────────────────────────────────
    reg [13:0] state_q;      // Q6.8 state, 14-bit unsigned
    reg [2:0]  counter;      // persistence gate counter [0..K-1]
    reg [2:0]  settle_cnt;   // settling counter [0..N_SETTLE]

    // ── Combinatorial: observe current block ───────────────────────────────────
    wire [13:0] obs_q        = {e_max_in, 8'b0};

    // Signed deviation: 15-bit.  Both obs_q and state_q are non-negative 14-bit
    // values, so {1'b0, x} correctly zero-extends to positive signed.
    wire signed [14:0] dev_signed =
        $signed({1'b0, obs_q}) - $signed({1'b0, state_q});

    // Absolute deviation (14-bit).  dev_signed cannot be -16384 with valid inputs
    // (obs_q max=16128, state_q max=16383, so min dev = -16383), so no underflow.
    wire [13:0] abs_dev = dev_signed[14]
                        ? (~dev_signed[13:0] + 14'd1)
                        : dev_signed[13:0];

    // Guarded ceiling (Rule 3): saturate at 14'h3FFF
    wire [14:0] ceiling_sum = {1'b0, state_q} + {1'b0, guard_margin_q};
    wire [13:0] ceiling_q   = ceiling_sum[14] ? 14'h3FFF : ceiling_sum[13:0];

    // Comparators
    wire exceed_persist = (abs_dev > persist_bound_q);
    wire exceed_ceiling = (obs_q  > ceiling_q);
    wire fire_reseed    = exceed_persist && (counter == K - 3'd1);

    // Leaky integrator update (Rule 1): arithmetic right shift by ALPHA_SHIFT.
    // dev_signed is 15-bit signed; >>> sign-extends for Verilog signed wires.
    wire signed [14:0] alpha_update_s = dev_signed >>> ALPHA_SHIFT;

    // new_state: 16-bit signed intermediate for saturation detection.
    wire signed [15:0] new_state_s =
        $signed({2'b00, state_q}) + $signed({alpha_update_s[14], alpha_update_s});

    // Saturate to [0, 16383] (= [0, MAX_STATE])
    wire [13:0] new_state_q =
        new_state_s[15]                      ? 14'd0    :   // underflow (negative)
        (new_state_s[15:14] == 2'b01)        ? 14'h3FFF :   // overflow
        new_state_s[13:0];

    // ── Next-state combinatorial logic ─────────────────────────────────────────
    reg [13:0] next_state_q;
    reg [2:0]  next_counter;
    reg [2:0]  next_settle_cnt;
    reg [1:0]  next_tag;
    reg        next_event;
    reg        next_event_dir;

    always @(*) begin
        // Defaults: hold state, no event
        next_state_q   = state_q;
        next_counter   = counter;
        next_settle_cnt = settle_cnt;
        next_tag       = TAG_OK;
        next_event     = 1'b0;
        next_event_dir = 1'b0;

        if (valid_in) begin
            if (fire_reseed) begin
                // Rule 2: re-seed fires at K-th consecutive deviation
                next_state_q    = obs_q;
                next_counter    = 3'd0;
                next_settle_cnt = N_SETTLE;
                next_event      = 1'b1;
                next_event_dir  = ~dev_signed[14];  // 1=positive step, 0=negative
                next_tag        = TAG_RESEEDED;

            end else if (exceed_persist) begin
                // Gate accumulating: increment counter
                next_counter = counter + 3'd1;
                // Settle counter ticks
                next_settle_cnt = (settle_cnt > 3'd0) ? settle_cnt - 3'd1 : 3'd0;
                if (exceed_ceiling) begin
                    // Rule 2 exclusion: state unchanged
                    next_tag = TAG_OUTLIER;
                end else begin
                    // Within ceiling: apply leaky integrator, mark as settling
                    next_state_q = new_state_q;
                    next_tag     = TAG_SETTLING;
                end

            end else begin
                // Below persist bound: reset counter
                next_counter    = 3'd0;
                next_settle_cnt = (settle_cnt > 3'd0) ? settle_cnt - 3'd1 : 3'd0;
                if (exceed_ceiling) begin
                    // Single outlier: excluded from state update (Rule 2 exclusion)
                    next_tag = TAG_OUTLIER;
                end else begin
                    next_state_q = new_state_q;
                    // Tag depends on settling window
                    next_tag = ((settle_cnt > 3'd0) &&
                                (settle_cnt - 3'd1 > 3'd0)) ? TAG_RESEEDED : TAG_OK;
                end
            end
        end
    end

    // ── Sequential: register everything, add 1-cycle output latency ───────────
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state_q         <= 14'd0;
            counter         <= 3'd0;
            settle_cnt      <= 3'd0;
            state_exp_out   <= 6'd0;
            ceiling_exp_out <= 6'd0;
            tag_out         <= TAG_OK;
            event_valid_out <= 1'b0;
            event_dir_out   <= 1'b0;
        end else begin
            state_q         <= next_state_q;
            counter         <= next_counter;
            settle_cnt      <= next_settle_cnt;
            // Outputs reflect the NEXT state (post-update), registered.
            state_exp_out   <= next_state_q[13:8];
            ceiling_exp_out <= ceiling_q[13:8];
            tag_out         <= next_tag;
            event_valid_out <= next_event;
            event_dir_out   <= next_event_dir;
        end
    end

endmodule
