`timescale 1ns / 1ps
// SPDX-License-Identifier: CERN-OHL-S-2.0
// ============================================================================
// Module   : skpr_block_detect
// File     : rtl/skpr_block_detect.v
// Date     : 2026-08-01
// Author   : Sotirios Chortogiannos
//
// Purpose  : Rule 5 DETECT-ONLY path — second-max gap test over an 8-element
//            NFE-13 block. Emits flag / e_max / e_second. Does NOT clip, does
//            NOT alter the normalizer datapath, does NOT touch skpr state.
//
//            Placement probe for campaign/scaling: measure the cost of the
//            mechanism that is architecturally forced to see all 8 exponents,
//            separate from the intervene (clip-in-norm) tax measured in
//            horus_norm_v3 P7.
//
// Algorithm (same as skpr_golden.detect_and_clip flag half):
//   e_max, e_second = top-2 order stats of in_i[11:6]
//   gap = e_max - e_second
//   flag = (gap > T)   // strict
//
// Second-max: V_REUSE path-loser recipe (STEP3_BINDS).
// Latency: 1-cycle registered outputs.
// ============================================================================

module skpr_block_detect (
    input  wire        clk,
    input  wire        rst_n,
    input  wire        valid_in,
    input  wire [12:0] in_0,
    input  wire [12:0] in_1,
    input  wire [12:0] in_2,
    input  wire [12:0] in_3,
    input  wire [12:0] in_4,
    input  wire [12:0] in_5,
    input  wire [12:0] in_6,
    input  wire [12:0] in_7,
    input  wire        t_we,
    input  wire [5:0]  t_in,

    output reg         valid_out,
    output reg         flag_out,
    output reg  [5:0]  e_max_out,
    output reg  [5:0]  e_second_out,
    output reg  [5:0]  gap_out
);

    reg [5:0] T;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) T <= 6'd0;
        else if (t_we) T <= t_in;
    end

    wire [5:0] e0 = in_0[11:6];
    wire [5:0] e1 = in_1[11:6];
    wire [5:0] e2 = in_2[11:6];
    wire [5:0] e3 = in_3[11:6];
    wire [5:0] e4 = in_4[11:6];
    wire [5:0] e5 = in_5[11:6];
    wire [5:0] e6 = in_6[11:6];
    wire [5:0] e7 = in_7[11:6];

    // Max tree
    wire [5:0] lv1_01   = (e0   >= e1  ) ? e0   : e1;
    wire [5:0] lv1_23   = (e2   >= e3  ) ? e2   : e3;
    wire [5:0] lv1_45   = (e4   >= e5  ) ? e4   : e5;
    wire [5:0] lv1_67   = (e6   >= e7  ) ? e6   : e7;
    wire [5:0] lv2_0123 = (lv1_01 >= lv1_23) ? lv1_01 : lv1_23;
    wire [5:0] lv2_4567 = (lv1_45 >= lv1_67) ? lv1_45 : lv1_67;
    wire [5:0] e_max    = (lv2_0123 >= lv2_4567) ? lv2_0123 : lv2_4567;

    // V_REUSE second-max
    wire [5:0] lo1_01 = (e0   >= e1  ) ? e1   : e0;
    wire [5:0] lo1_23 = (e2   >= e3  ) ? e3   : e2;
    wire [5:0] lo1_45 = (e4   >= e5  ) ? e5   : e4;
    wire [5:0] lo1_67 = (e6   >= e7  ) ? e7   : e6;
    wire [5:0] lo2_0123 = (lv1_01 >= lv1_23) ? lv1_23 : lv1_01;
    wire [5:0] lo2_4567 = (lv1_45 >= lv1_67) ? lv1_67 : lv1_45;
    wire [5:0] lo3 = (lv2_0123 >= lv2_4567) ? lv2_4567 : lv2_0123;
    wire win_l2_left = (lv2_0123 >= lv2_4567);
    wire win_l1_left = win_l2_left ? (lv1_01 >= lv1_23) : (lv1_45 >= lv1_67);
    wire [5:0] lo2_win = win_l2_left ? lo2_0123 : lo2_4567;
    wire [5:0] lo1_win = win_l2_left
                       ? (win_l1_left ? lo1_01 : lo1_23)
                       : (win_l1_left ? lo1_45 : lo1_67);
    wire [5:0] m01 = (lo3 >= lo2_win) ? lo3 : lo2_win;
    wire [5:0] e_second = (m01 >= lo1_win) ? m01 : lo1_win;

    wire [5:0] gap  = e_max - e_second;
    wire       flag = (gap > T);

    always @(posedge clk) begin
        if (!rst_n) begin
            valid_out    <= 1'b0;
            flag_out     <= 1'b0;
            e_max_out    <= 6'd0;
            e_second_out <= 6'd0;
            gap_out      <= 6'd0;
        end else begin
            valid_out    <= valid_in;
            flag_out     <= flag;
            e_max_out    <= e_max;
            e_second_out <= e_second;
            gap_out      <= gap;
        end
    end

endmodule
