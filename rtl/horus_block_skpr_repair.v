`timescale 1ns / 1ps
// SPDX-License-Identifier: CERN-OHL-S-2.0
// ============================================================================
// Module   : horus_block_skpr_repair
// Purpose  : Rare-event repair-and-replay around horus_norm_v2.
//
// FSM:
//   IDLE → WAIT_DET → COMMIT (clean)
//                    → REPLAY_FIRE → WAIT_REPLAY → COMMIT (flagged)
// ============================================================================

`default_nettype none

module horus_block_skpr_repair #(
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
    input  wire [1:0]  repair_mode,
    input  wire [13:0] persist_bound_q,
    input  wire [13:0] guard_margin_q,

    output reg         commit_valid,
    output reg  [5:0]  commit_e_max,
    output reg  [12:0] commit_0,
    output reg  [12:0] commit_1,
    output reg  [12:0] commit_2,
    output reg  [12:0] commit_3,
    output reg  [12:0] commit_4,
    output reg  [12:0] commit_5,
    output reg  [12:0] commit_6,
    output reg  [12:0] commit_7,

    output wire        det_valid,
    output wire        det_flag,
    output wire [5:0]  det_e_second,
    output wire [2:0]  det_argmax,
    output wire [7:0]  det_repair_mask,
    output wire        repair_applied,
    output reg         replay_pulse,
    output reg         skpr_update_pulse,
    output wire [5:0]  state_exp_out,
    output wire [1:0]  tag_out,
    output wire        busy,
    output reg  [31:0] logical_block_id,
    output reg  [31:0] cycle_count,
    output reg  [31:0] commit_count,
    output reg  [31:0] skpr_update_count,
    output reg  [31:0] replay_count,
    output reg  [31:0] flagged_count
);

    localparam [1:0] ST_IDLE        = 2'd0;
    localparam [1:0] ST_WAIT_DET    = 2'd1;
    localparam [1:0] ST_REPLAY_FIRE = 2'd2;
    localparam [1:0] ST_WAIT_REPLAY = 2'd3;

    reg [1:0]  state;
    reg [12:0] cap0, cap1, cap2, cap3, cap4, cap5, cap6, cap7;
    reg [12:0] rep0, rep1, rep2, rep3, rep4, rep5, rep6, rep7;
    reg        lat_flag;
    reg [5:0]  lat_esec;
    reg [2:0]  lat_argmax;
    reg [7:0]  lat_mask;

    reg         norm_fire;
    reg  [12:0] n_in0, n_in1, n_in2, n_in3, n_in4, n_in5, n_in6, n_in7;
    wire        norm_valid;
    wire [5:0]  norm_e_max;
    wire [12:0] n0, n1, n2, n3, n4, n5, n6, n7;

    reg         det_fire;
    reg  [12:0] d_in0, d_in1, d_in2, d_in3, d_in4, d_in5, d_in6, d_in7;
    wire        d_valid, d_flag, d_unique;
    wire [5:0]  d_emax, d_esec, d_gap;
    wire [2:0]  d_argmax;
    wire [7:0]  d_mask;

    skpr_block_detect_rr u_det (
        .clk(clk), .rst_n(rst_n),
        .valid_in(det_fire),
        .in_0(d_in0), .in_1(d_in1), .in_2(d_in2), .in_3(d_in3),
        .in_4(d_in4), .in_5(d_in5), .in_6(d_in6), .in_7(d_in7),
        .t_we(t_we), .t_in(t_in),
        .valid_out(d_valid), .flag_out(d_flag),
        .e_max_out(d_emax), .e_second_out(d_esec), .gap_out(d_gap),
        .argmax_out(d_argmax), .unique_max_out(d_unique),
        .repair_mask_out(d_mask)
    );
    assign det_valid = d_valid;
    assign det_flag = d_flag;
    assign det_e_second = d_esec;
    assign det_argmax = d_argmax;
    assign det_repair_mask = d_mask;

    wire [12:0] r0, r1, r2, r3, r4, r5, r6, r7;
    wire        r_applied;
    wire [3:0]  r_count;

    skpr_block_repair u_repair (
        .in_0(cap0), .in_1(cap1), .in_2(cap2), .in_3(cap3),
        .in_4(cap4), .in_5(cap5), .in_6(cap6), .in_7(cap7),
        .det_flag(lat_flag),
        .det_e_second(lat_esec),
        .det_argmax_idx(lat_argmax),
        .det_repair_mask(lat_mask),
        .repair_mode(repair_mode),
        .out_0(r0), .out_1(r1), .out_2(r2), .out_3(r3),
        .out_4(r4), .out_5(r5), .out_6(r6), .out_7(r7),
        .repair_applied(r_applied),
        .repair_count(r_count)
    );
    assign repair_applied = r_applied;

    // Live repair from detector outputs for latching on decision cycle
    wire [12:0] lr0, lr1, lr2, lr3, lr4, lr5, lr6, lr7;
    wire        lr_applied;
    wire [3:0]  lr_count;
    skpr_block_repair u_repair_live (
        .in_0(cap0), .in_1(cap1), .in_2(cap2), .in_3(cap3),
        .in_4(cap4), .in_5(cap5), .in_6(cap6), .in_7(cap7),
        .det_flag(d_flag),
        .det_e_second(d_esec),
        .det_argmax_idx(d_argmax),
        .det_repair_mask(d_mask),
        .repair_mode(repair_mode),
        .out_0(lr0), .out_1(lr1), .out_2(lr2), .out_3(lr3),
        .out_4(lr4), .out_5(lr5), .out_6(lr6), .out_7(lr7),
        .repair_applied(lr_applied),
        .repair_count(lr_count)
    );

    horus_norm_v2 #(.E_TARGET(6'd32)) u_norm (
        .clk(clk), .rst_n(rst_n),
        .valid_in(norm_fire),
        .in_0(n_in0), .in_1(n_in1), .in_2(n_in2), .in_3(n_in3),
        .in_4(n_in4), .in_5(n_in5), .in_6(n_in6), .in_7(n_in7),
        .offset_mode(1'b0), .offset_in(7'd0),
        .valid_out(norm_valid),
        .e_max_out(norm_e_max),
        .out_0(n0), .out_1(n1), .out_2(n2), .out_3(n3),
        .out_4(n4), .out_5(n5), .out_6(n6), .out_7(n7)
    );

    reg         skpr_valid;
    reg  [5:0]  skpr_e;
    wire [5:0]  st_exp, ceil_exp;
    wire [1:0]  tag;
    wire        ev, ed;

    skpr #(.K(K), .N_SETTLE(N_SETTLE), .ALPHA_SHIFT(ALPHA_SHIFT)) u_skpr (
        .clk(clk), .rst_n(rst_n),
        .valid_in(skpr_valid),
        .e_max_in(skpr_e),
        .persist_bound_q(persist_bound_q),
        .guard_margin_q(guard_margin_q),
        .state_exp_out(st_exp),
        .ceiling_exp_out(ceil_exp),
        .tag_out(tag),
        .event_valid_out(ev),
        .event_dir_out(ed)
    );
    assign state_exp_out = st_exp;
    assign tag_out = tag;
    assign busy = (state != ST_IDLE);

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= ST_IDLE;
            commit_valid <= 1'b0;
            skpr_valid <= 1'b0;
            skpr_update_pulse <= 1'b0;
            replay_pulse <= 1'b0;
            norm_fire <= 1'b0;
            det_fire <= 1'b0;
            lat_flag <= 1'b0;
            lat_esec <= 6'd0;
            lat_argmax <= 3'd0;
            lat_mask <= 8'd0;
            logical_block_id <= 32'd0;
            cycle_count <= 32'd0;
            commit_count <= 32'd0;
            skpr_update_count <= 32'd0;
            replay_count <= 32'd0;
            flagged_count <= 32'd0;
            commit_e_max <= 6'd0;
            commit_0 <= 13'd0; commit_1 <= 13'd0; commit_2 <= 13'd0; commit_3 <= 13'd0;
            commit_4 <= 13'd0; commit_5 <= 13'd0; commit_6 <= 13'd0; commit_7 <= 13'd0;
            n_in0 <= 13'd0; n_in1 <= 13'd0; n_in2 <= 13'd0; n_in3 <= 13'd0;
            n_in4 <= 13'd0; n_in5 <= 13'd0; n_in6 <= 13'd0; n_in7 <= 13'd0;
            d_in0 <= 13'd0; d_in1 <= 13'd0; d_in2 <= 13'd0; d_in3 <= 13'd0;
            d_in4 <= 13'd0; d_in5 <= 13'd0; d_in6 <= 13'd0; d_in7 <= 13'd0;
            cap0 <= 13'd0; cap1 <= 13'd0; cap2 <= 13'd0; cap3 <= 13'd0;
            cap4 <= 13'd0; cap5 <= 13'd0; cap6 <= 13'd0; cap7 <= 13'd0;
            rep0 <= 13'd0; rep1 <= 13'd0; rep2 <= 13'd0; rep3 <= 13'd0;
            rep4 <= 13'd0; rep5 <= 13'd0; rep6 <= 13'd0; rep7 <= 13'd0;
            skpr_e <= 6'd0;
        end else begin
            cycle_count <= cycle_count + 32'd1;
            commit_valid <= 1'b0;
            skpr_valid <= 1'b0;
            skpr_update_pulse <= 1'b0;
            replay_pulse <= 1'b0;
            norm_fire <= 1'b0;
            det_fire <= 1'b0;

            case (state)
                ST_IDLE: begin
                    if (valid_in) begin
                        cap0 <= in_0; cap1 <= in_1; cap2 <= in_2; cap3 <= in_3;
                        cap4 <= in_4; cap5 <= in_5; cap6 <= in_6; cap7 <= in_7;
                        d_in0 <= in_0; d_in1 <= in_1; d_in2 <= in_2; d_in3 <= in_3;
                        d_in4 <= in_4; d_in5 <= in_5; d_in6 <= in_6; d_in7 <= in_7;
                        n_in0 <= in_0; n_in1 <= in_1; n_in2 <= in_2; n_in3 <= in_3;
                        n_in4 <= in_4; n_in5 <= in_5; n_in6 <= in_6; n_in7 <= in_7;
                        det_fire <= 1'b1;
                        norm_fire <= 1'b1;
                        state <= ST_WAIT_DET;
                    end
                end

                ST_WAIT_DET: begin
                    if (d_valid) begin
                        if (!d_flag || repair_mode == 2'd0) begin
                            commit_valid <= 1'b1;
                            commit_e_max <= norm_e_max;
                            commit_0 <= n0; commit_1 <= n1; commit_2 <= n2; commit_3 <= n3;
                            commit_4 <= n4; commit_5 <= n5; commit_6 <= n6; commit_7 <= n7;
                            skpr_e <= norm_e_max;
                            skpr_valid <= 1'b1;
                            skpr_update_pulse <= 1'b1;
                            logical_block_id <= logical_block_id + 32'd1;
                            commit_count <= commit_count + 32'd1;
                            skpr_update_count <= skpr_update_count + 32'd1;
                            state <= ST_IDLE;
                        end else begin
                            // Suppress original commit; latch repair from live detector
                            lat_flag <= 1'b1;
                            lat_esec <= d_esec;
                            lat_argmax <= d_argmax;
                            lat_mask <= d_mask;
                            rep0 <= lr0; rep1 <= lr1; rep2 <= lr2; rep3 <= lr3;
                            rep4 <= lr4; rep5 <= lr5; rep6 <= lr6; rep7 <= lr7;
                            flagged_count <= flagged_count + 32'd1;
                            state <= ST_REPLAY_FIRE;
                        end
                    end
                end

                ST_REPLAY_FIRE: begin
                    n_in0 <= rep0; n_in1 <= rep1; n_in2 <= rep2; n_in3 <= rep3;
                    n_in4 <= rep4; n_in5 <= rep5; n_in6 <= rep6; n_in7 <= rep7;
                    norm_fire <= 1'b1;
                    replay_pulse <= 1'b1;
                    replay_count <= replay_count + 32'd1;
                    state <= ST_WAIT_REPLAY;
                end

                ST_WAIT_REPLAY: begin
                    if (norm_valid) begin
                        commit_valid <= 1'b1;
                        commit_e_max <= norm_e_max;
                        commit_0 <= n0; commit_1 <= n1; commit_2 <= n2; commit_3 <= n3;
                        commit_4 <= n4; commit_5 <= n5; commit_6 <= n6; commit_7 <= n7;
                        skpr_e <= norm_e_max;
                        skpr_valid <= 1'b1;
                        skpr_update_pulse <= 1'b1;
                        logical_block_id <= logical_block_id + 32'd1;
                        commit_count <= commit_count + 32'd1;
                        skpr_update_count <= skpr_update_count + 32'd1;
                        lat_flag <= 1'b0;
                        state <= ST_IDLE;
                    end
                end

                default: state <= ST_IDLE;
            endcase
        end
    end

endmodule

`default_nettype wire
