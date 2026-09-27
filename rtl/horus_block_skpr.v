// SPDX-License-Identifier: CERN-OHL-S-2.0
// ============================================================================
// Module   : horus_block_skpr
// File     : rtl/horus_block_skpr.v
// Date     : 2026-08-01
// Author   : Sotirios Chortogiannos
//
// Purpose  : Direct NFE-13 block inject path that mirrors the tile's
//            fire_pending → (norm_v2 ∥ skpr_block_detect) → block_scale_out
//            → dual skpr composition, without the multiply/shim front-end.
//
//            Used for end-to-end keeper recovery arcs with directed
//            clean / spiked / adversarial blocks. Timing matches the tile:
//              valid_in high 1 cycle → outputs + skpr sample 1 cycle later.
// ============================================================================

`default_nettype none
`timescale 1ns / 1ps

module horus_block_skpr #(
    parameter [2:0]  K           = 3'd4,
    parameter [2:0]  N_SETTLE    = 3'd4,
    parameter [3:0]  ALPHA_SHIFT = 4'd4
) (
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

    input  wire [13:0] persist_bound_q,
    input  wire [13:0] guard_margin_q,

    output wire        norm_valid,
    output wire [5:0]  norm_e_max,
    output wire        det_valid,
    output wire        det_flag,
    output wire [5:0]  det_e_second,
    output wire [5:0]  block_scale_out,

    output wire [5:0]  state_exp_a,
    output wire [5:0]  ceiling_exp_a,
    output wire [1:0]  tag_a,
    output wire        event_valid_a,
    output wire        event_dir_a,

    output wire [5:0]  state_exp_b,
    output wire [5:0]  ceiling_exp_b,
    output wire [1:0]  tag_b,
    output wire        event_valid_b,
    output wire        event_dir_b
);

    wire [12:0] n0, n1, n2, n3, n4, n5, n6, n7;
    wire [5:0]  det_e_max_unused;
    wire [5:0]  det_gap_unused;

    horus_norm_v2 #(.E_TARGET(6'd32)) u_norm (
        .clk         (clk),
        .rst_n       (rst_n),
        .valid_in    (valid_in),
        .in_0        (in_0),
        .in_1        (in_1),
        .in_2        (in_2),
        .in_3        (in_3),
        .in_4        (in_4),
        .in_5        (in_5),
        .in_6        (in_6),
        .in_7        (in_7),
        .offset_mode (1'b0),
        .offset_in   (7'd0),
        .valid_out   (norm_valid),
        .e_max_out   (norm_e_max),
        .out_0       (n0),
        .out_1       (n1),
        .out_2       (n2),
        .out_3       (n3),
        .out_4       (n4),
        .out_5       (n5),
        .out_6       (n6),
        .out_7       (n7)
    );

    skpr_block_detect u_det (
        .clk          (clk),
        .rst_n        (rst_n),
        .valid_in     (valid_in),
        .in_0         (in_0),
        .in_1         (in_1),
        .in_2         (in_2),
        .in_3         (in_3),
        .in_4         (in_4),
        .in_5         (in_5),
        .in_6         (in_6),
        .in_7         (in_7),
        .t_we         (t_we),
        .t_in         (t_in),
        .valid_out    (det_valid),
        .flag_out     (det_flag),
        .e_max_out    (det_e_max_unused),
        .e_second_out (det_e_second),
        .gap_out      (det_gap_unused)
    );

    assign block_scale_out = det_flag ? det_e_second : norm_e_max;

    wire skpr_valid = norm_valid;

    skpr #(
        .K(K), .N_SETTLE(N_SETTLE), .ALPHA_SHIFT(ALPHA_SHIFT)
    ) u_skpr_a (
        .clk(clk), .rst_n(rst_n),
        .valid_in(skpr_valid),
        .e_max_in(norm_e_max),
        .persist_bound_q(persist_bound_q),
        .guard_margin_q(guard_margin_q),
        .state_exp_out(state_exp_a),
        .ceiling_exp_out(ceiling_exp_a),
        .tag_out(tag_a),
        .event_valid_out(event_valid_a),
        .event_dir_out(event_dir_a)
    );

    skpr #(
        .K(K), .N_SETTLE(N_SETTLE), .ALPHA_SHIFT(ALPHA_SHIFT)
    ) u_skpr_b (
        .clk(clk), .rst_n(rst_n),
        .valid_in(skpr_valid),
        .e_max_in(block_scale_out),
        .persist_bound_q(persist_bound_q),
        .guard_margin_q(guard_margin_q),
        .state_exp_out(state_exp_b),
        .ceiling_exp_out(ceiling_exp_b),
        .tag_out(tag_b),
        .event_valid_out(event_valid_b),
        .event_dir_out(event_dir_b)
    );

endmodule

`default_nettype wire
