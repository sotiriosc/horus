// SPDX-License-Identifier: CERN-OHL-S-2.0
// ============================================================================
// tb/tb_tile_skpr_align.v — Prove det_* / block_scale_out / skpr feeds stay
// aligned with the exact buffered block under pipeline hazards.
//
// Assert (every consume cycle):
//   1. det_valid == norm_valid
//   2. block_scale_out == det_flag ? det_e_second : norm_e_max
//   3. skpr_A.e_max_in == norm_e_max  (hierarchical)
//   4. skpr_B.e_max_in == block_scale_out
//   5. Scoreboard: captured buf_0..7 at fire_pending predicts
//      (norm_e_max, det_flag, det_e_second) one cycle later
//
// Hazard regimes:
//   - stalls / backpressure (gaps between valid_in)
//   - consecutive blocks (no idle)
//   - reset + pipeline refill
//   - optional replay (same 8 pairs twice)
//   - changing valid patterns (bursts of 1..8 with gaps)
// ============================================================================

`timescale 1ns / 1ps

module tb_tile_skpr_align;

    reg         clk, rst_n;
    reg         mode;
    reg  [9:0]  op_a, op_b;
    reg         valid_in;
    reg         t_we;
    reg  [5:0]  t_in;
    reg  [13:0] persist_bound_q, guard_margin_q;

    wire        norm_valid, det_valid, det_flag;
    wire [5:0]  norm_e_max, det_e_second, block_scale_out;
    wire [5:0]  state_exp_a, ceiling_exp_a, state_exp_b, ceiling_exp_b;
    wire [1:0]  tag_a, tag_b;
    wire        event_valid_a, event_dir_a, event_valid_b, event_dir_b;

    horus_tile_skpr dut (
        .clk(clk), .rst_n(rst_n),
        .mode(mode), .op_a(op_a), .op_b(op_b), .valid_in(valid_in),
        .t_we(t_we), .t_in(t_in),
        .persist_bound_q(persist_bound_q), .guard_margin_q(guard_margin_q),
        .norm_valid(norm_valid), .norm_e_max(norm_e_max),
        .det_valid(det_valid), .det_flag(det_flag),
        .det_e_second(det_e_second), .block_scale_out(block_scale_out),
        .state_exp_a(state_exp_a), .ceiling_exp_a(ceiling_exp_a),
        .tag_a(tag_a), .event_valid_a(event_valid_a), .event_dir_a(event_dir_a),
        .state_exp_b(state_exp_b), .ceiling_exp_b(ceiling_exp_b),
        .tag_b(tag_b), .event_valid_b(event_valid_b), .event_dir_b(event_dir_b)
    );

    initial clk = 0;
    always #5 clk = ~clk;

    integer fails, checks, blocks_seen, i, b, s, gap;
    integer block_id;          // monotonic consume counter
    integer pending_id;        // id latched at fire_pending
    integer expect_pending;    // scoreboard armed

    // Scoreboard snapshot of the fired block
    reg [12:0] snap_buf [0:7];
    reg [5:0]  exp_e_max, exp_e_second, exp_gap;
    reg        exp_flag;
    reg [5:0]  T_shadow;

    // ── Golden top-2 on snapshot (matches skpr_block_detect / norm e_max) ──
    task compute_expect;
        integer k;
        reg [5:0] exps [0:7];
        reg [5:0] mx, rem_max, e;
        integer   removed;
        begin
            for (k = 0; k < 8; k = k + 1)
                exps[k] = snap_buf[k][11:6];
            mx = exps[0];
            for (k = 1; k < 8; k = k + 1)
                if (exps[k] > mx) mx = exps[k];
            removed = 0;
            rem_max = 0;
            for (k = 0; k < 8; k = k + 1) begin
                e = exps[k];
                if (!removed && e == mx)
                    removed = 1;
                else if (e > rem_max)
                    rem_max = e;
            end
            exp_e_max    = mx;
            exp_e_second = rem_max;
            exp_gap      = mx - rem_max;
            exp_flag     = (exp_gap > T_shadow);
        end
    endtask

    task fail;
        input [255:0] msg;
        begin
            $display("FAIL @%0t block=%0d: %s", $time, block_id, msg);
            fails = fails + 1;
        end
    endtask

    // Sample after NBA (#1) so fire_pending / buf_* / norm_valid are settled.
    always @(posedge clk) begin
        if (rst_n) begin
            #1;
            // Latch scoreboard when tile presents the buffered block to norm/det
            if (dut.u_tile.fire_pending) begin
                snap_buf[0] = dut.u_tile.buf_0;
                snap_buf[1] = dut.u_tile.buf_1;
                snap_buf[2] = dut.u_tile.buf_2;
                snap_buf[3] = dut.u_tile.buf_3;
                snap_buf[4] = dut.u_tile.buf_4;
                snap_buf[5] = dut.u_tile.buf_5;
                snap_buf[6] = dut.u_tile.buf_6;
                snap_buf[7] = dut.u_tile.buf_7;
                compute_expect;
                pending_id = block_id;
                expect_pending = 1;
            end

            if (norm_valid || det_valid) begin
                checks = checks + 1;
                if (norm_valid !== det_valid)
                    fail("det_valid != norm_valid");
                if (block_scale_out !== (det_flag ? det_e_second : norm_e_max))
                    fail("block_scale_out mux misaligned");
                if (dut.u_skpr_a.e_max_in !== norm_e_max)
                    fail("skpr_A e_max_in != norm_e_max");
                if (dut.u_skpr_b.e_max_in !== block_scale_out)
                    fail("skpr_B e_max_in != block_scale_out");
                if (dut.u_skpr_a.valid_in !== 1'b1 || dut.u_skpr_b.valid_in !== 1'b1)
                    fail("skpr valid_in not asserted on consume");

                if (expect_pending) begin
                    if (norm_e_max !== exp_e_max)
                        fail("norm_e_max != scoreboard e_max for block N");
                    if (det_flag !== exp_flag)
                        fail("det_flag != scoreboard flag for block N");
                    if (det_e_second !== exp_e_second)
                        fail("det_e_second != scoreboard e_second for block N");
                    // Decisive identity assert
                    if (block_scale_out !== (exp_flag ? exp_e_second : exp_e_max))
                        fail("block_scale_out not derived solely from block N");
                    expect_pending = 0;
                    block_id = block_id + 1;
                    blocks_seen = blocks_seen + 1;
                end else begin
                    fail("consume without prior fire_pending snapshot");
                end
            end
        end
    end

    task do_reset;
        begin
            rst_n = 0;
            valid_in = 0;
            op_a = 0; op_b = 0;
            t_we = 0;
            expect_pending = 0;
            @(posedge clk); #1;
            @(posedge clk); #1;
            rst_n = 1;
            @(posedge clk); #1;
        end
    endtask

    task load_T;
        input [5:0] t;
        begin
            t_in = t;
            t_we = 1;
            @(posedge clk); #1;
            t_we = 0;
            T_shadow = t;
            @(posedge clk); #1;
        end
    endtask

    // E4M3: encode simple (sign=0, e4, f3=0) × 1.0 → controlled NFE exp = e4+25
    // 1.0 in E4M3: e4=7, f=0 → 0x38
    function [7:0] e4m3_from_e4;
        input [3:0] e4;
        begin
            e4m3_from_e4 = {1'b0, e4, 3'b000};
        end
    endfunction

    task push_pair;
        input [7:0] a;
        input [7:0] b;
        begin
            mode = 1'b1;
            op_a = {2'b0, a};
            op_b = {2'b0, b};
            valid_in = 1'b1;
            @(posedge clk); #1;
            valid_in = 1'b0;
        end
    endtask

    task idle;
        input integer n;
        integer j;
        begin
            valid_in = 0;
            for (j = 0; j < n; j = j + 1)
                @(posedge clk); #1;
        end
    endtask

    // One block: 8 E4M3×1.0 pairs with given e4[0..7]; optional inter-pair gaps
    task push_block_e4;
        input [3:0] e0, e1, e2, e3, e4, e5, e6, e7;
        input integer stall_between; // cycles of idle after each pair (0=tight)
        reg [3:0] es [0:7];
        integer k;
        begin
            es[0]=e0; es[1]=e1; es[2]=e2; es[3]=e3;
            es[4]=e4; es[5]=e5; es[6]=e6; es[7]=e7;
            // settle mode_r
            mode = 1; @(posedge clk); #1;
            for (k = 0; k < 8; k = k + 1) begin
                push_pair(e4m3_from_e4(es[k]), 8'h38); // × 1.0
                if (stall_between > 0)
                    idle(stall_between);
            end
            // wait for fire + consume
            idle(4);
        end
    endtask

    initial begin
        fails = 0; checks = 0; blocks_seen = 0; block_id = 0;
        expect_pending = 0;
        persist_bound_q = 14'd256;
        guard_margin_q  = 14'd512;
        mode = 0; op_a = 0; op_b = 0; valid_in = 0;
        t_we = 0; t_in = 0; T_shadow = 0;

        $display("=== tb_tile_skpr_align ===");
        do_reset;
        load_T(6'd4);

        // 1) Consecutive clean-ish blocks (no stall)
        $display("-- consecutive blocks");
        for (b = 0; b < 8; b = b + 1)
            push_block_e4(4'd4,4'd4,4'd5,4'd4,4'd4,4'd3,4'd4,4'd4, 0);

        // 2) Stalls / backpressure between pairs
        $display("-- stalls between pairs");
        for (b = 0; b < 4; b = b + 1)
            push_block_e4(4'd3,4'd3,4'd3,4'd8,4'd3,4'd3,4'd3,4'd3, 3);

        // 3) Changing valid patterns: variable stall schedule
        $display("-- changing valid patterns");
        for (gap = 0; gap <= 5; gap = gap + 1)
            push_block_e4(4'd2,4'd2,4'd2,4'd2,4'd2,4'd2,4'd2,4'd9, gap);

        // 4) Directed spikes (gap > T) at rotating positions
        $display("-- directed spikes");
        push_block_e4(4'd14,4'd3,4'd3,4'd3,4'd3,4'd3,4'd3,4'd3, 1);
        push_block_e4(4'd3,4'd3,4'd14,4'd3,4'd3,4'd3,4'd3,4'd3, 0);
        push_block_e4(4'd3,4'd3,4'd3,4'd3,4'd3,4'd3,4'd3,4'd14, 2);

        // 5) Optional replay: same block twice
        $display("-- replay");
        push_block_e4(4'd5,4'd5,4'd5,4'd12,4'd5,4'd5,4'd5,4'd5, 0);
        push_block_e4(4'd5,4'd5,4'd5,4'd12,4'd5,4'd5,4'd5,4'd5, 0);

        // 6) Reset mid-stream + refill
        $display("-- reset + refill");
        mode = 1; @(posedge clk); #1;
        for (s = 0; s < 5; s = s + 1)
            push_pair(e4m3_from_e4(4'd4), 8'h38);
        do_reset;
        load_T(6'd4);
        push_block_e4(4'd4,4'd4,4'd4,4'd4,4'd4,4'd4,4'd4,4'd4, 0);
        push_block_e4(4'd4,4'd4,4'd11,4'd4,4'd4,4'd4,4'd4,4'd4, 1);

        // Drain
        idle(8);

        $display("=== ALIGN RESULT: checks=%0d blocks=%0d fails=%0d ===",
                 checks, blocks_seen, fails);
        if (fails == 0 && blocks_seen >= 20)
            $display("PASS");
        else
            $display("FAIL");
        $finish;
    end

endmodule
