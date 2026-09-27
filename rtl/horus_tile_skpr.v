// SPDX-License-Identifier: CERN-OHL-S-2.0
// ============================================================================
// Module   : horus_tile_skpr
// File     : rtl/horus_tile_skpr.v
// Date     : 2026-08-01
// Author   : Sotirios Chortogiannos
//
// Purpose  : System-level attach of Rules 1–4 (skpr) to the tile's Rule 5
//            detect sideband. Instantiates one horus_tile and two skpr
//            keepers for the decisive A/B comparison:
//
//              A: norm_e_max      → skpr.e_max_in   (LOCALMAX / poisoned)
//              B: block_scale_out → skpr.e_max_in   (survivor when flagged)
//
//            Both keepers share the same valid (norm_valid), clock, reset,
//            and calibrated bounds. Detect metadata (det_flag / det_e_second)
//            is exposed so a testbench can assert block-N alignment:
//              when skpr consumes block N, block_scale_out derives only from
//              that block's norm_e_max, det_flag, and det_e_second.
// ============================================================================

`default_nettype none
`timescale 1ns / 1ps

module horus_tile_skpr #(
    parameter [2:0]  K           = 3'd4,
    parameter [2:0]  N_SETTLE    = 3'd4,
    parameter [3:0]  ALPHA_SHIFT = 4'd4
) (
    input  wire        clk,
    input  wire        rst_n,

    input  wire        mode,
    input  wire [9:0]  op_a,
    input  wire [9:0]  op_b,
    input  wire        valid_in,

    input  wire        t_we,
    input  wire [5:0]  t_in,

    input  wire [13:0] persist_bound_q,
    input  wire [13:0] guard_margin_q,

    // Tile / detect observability
    output wire        norm_valid,
    output wire [5:0]  norm_e_max,
    output wire        det_valid,
    output wire        det_flag,
    output wire [5:0]  det_e_second,
    output wire [5:0]  block_scale_out,

    // Path A — LOCALMAX feed
    output wire [5:0]  state_exp_a,
    output wire [5:0]  ceiling_exp_a,
    output wire [1:0]  tag_a,
    output wire        event_valid_a,
    output wire        event_dir_a,

    // Path B — survivor-aware feed
    output wire [5:0]  state_exp_b,
    output wire [5:0]  ceiling_exp_b,
    output wire [1:0]  tag_b,
    output wire        event_valid_b,
    output wire        event_dir_b
);

    wire [12:0] n0, n1, n2, n3, n4, n5, n6, n7;

    horus_tile u_tile (
        .clk             (clk),
        .rst_n           (rst_n),
        .mode            (mode),
        .op_a            (op_a),
        .op_b            (op_b),
        .valid_in        (valid_in),
        .t_we            (t_we),
        .t_in            (t_in),
        .norm_valid      (norm_valid),
        .norm_e_max      (norm_e_max),
        .norm_out_0      (n0),
        .norm_out_1      (n1),
        .norm_out_2      (n2),
        .norm_out_3      (n3),
        .norm_out_4      (n4),
        .norm_out_5      (n5),
        .norm_out_6      (n6),
        .norm_out_7      (n7),
        .det_valid       (det_valid),
        .det_flag        (det_flag),
        .det_e_second    (det_e_second),
        .block_scale_out (block_scale_out)
    );

    // Same-cycle consume: skpr samples when the tile publishes the block scale.
    wire skpr_valid = norm_valid;

    skpr #(
        .K           (K),
        .N_SETTLE    (N_SETTLE),
        .ALPHA_SHIFT (ALPHA_SHIFT)
    ) u_skpr_a (
        .clk             (clk),
        .rst_n           (rst_n),
        .valid_in        (skpr_valid),
        .e_max_in        (norm_e_max),
        .persist_bound_q (persist_bound_q),
        .guard_margin_q  (guard_margin_q),
        .state_exp_out   (state_exp_a),
        .ceiling_exp_out (ceiling_exp_a),
        .tag_out         (tag_a),
        .event_valid_out (event_valid_a),
        .event_dir_out   (event_dir_a)
    );

    skpr #(
        .K           (K),
        .N_SETTLE    (N_SETTLE),
        .ALPHA_SHIFT (ALPHA_SHIFT)
    ) u_skpr_b (
        .clk             (clk),
        .rst_n           (rst_n),
        .valid_in        (skpr_valid),
        .e_max_in        (block_scale_out),
        .persist_bound_q (persist_bound_q),
        .guard_margin_q  (guard_margin_q),
        .state_exp_out   (state_exp_b),
        .ceiling_exp_out (ceiling_exp_b),
        .tag_out         (tag_b),
        .event_valid_out (event_valid_b),
        .event_dir_out   (event_dir_b)
    );

endmodule

`default_nettype wire
