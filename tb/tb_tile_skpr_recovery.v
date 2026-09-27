// SPDX-License-Identifier: CERN-OHL-S-2.0
// ============================================================================
// tb/tb_tile_skpr_recovery.v — RTL co-sim of A/B skpr feeds through
// horus_block_skpr (same norm∥detect→mux→dual-skpr composition as the tile).
//
// Stim file (from tile_skpr_recovery_arc.py):
//   line0: T
//   lines: in0..in7(hex) flag feed_a feed_b
//
// Checks per block:
//   det_flag / feeds match golden
//   block_scale_out mux contract
//   skpr A/B e_max_in match feed_a / feed_b on consume
// ============================================================================

`timescale 1ns / 1ps

module tb_tile_skpr_recovery;

    reg         clk, rst_n;
    reg         valid_in;
    reg  [12:0] in_0, in_1, in_2, in_3, in_4, in_5, in_6, in_7;
    reg         t_we;
    reg  [5:0]  t_in;
    reg  [13:0] persist_bound_q, guard_margin_q;

    wire        norm_valid, det_valid, det_flag;
    wire [5:0]  norm_e_max, det_e_second, block_scale_out;
    wire [5:0]  state_exp_a, ceiling_exp_a, state_exp_b, ceiling_exp_b;
    wire [1:0]  tag_a, tag_b;
    wire        event_valid_a, event_dir_a, event_valid_b, event_dir_b;

    horus_block_skpr dut (
        .clk(clk), .rst_n(rst_n),
        .valid_in(valid_in),
        .in_0(in_0), .in_1(in_1), .in_2(in_2), .in_3(in_3),
        .in_4(in_4), .in_5(in_5), .in_6(in_6), .in_7(in_7),
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

    integer fd, code, fails, checks, blocks;
    integer exp_flag, exp_feed_a, exp_feed_b;
    integer pending;
    reg [5:0] T;
    reg [12:0] bin [0:7];
    reg [8*128-1:0] stim_path;

    task fail;
        input [255:0] msg;
        begin
            $display("FAIL @%0t blk=%0d: %s", $time, blocks, msg);
            fails = fails + 1;
        end
    endtask

    always @(posedge clk) begin
        if (rst_n) begin
            #1;
            if (norm_valid || det_valid) begin
                checks = checks + 1;
                if (norm_valid !== det_valid)
                    fail("valid misalign");
                if (block_scale_out !== (det_flag ? det_e_second : norm_e_max))
                    fail("mux");
                if (!pending)
                    fail("unexpected consume");
                else begin
                    if (det_flag !== exp_flag[0])
                        fail("flag");
                    if (norm_e_max !== exp_feed_a[5:0])
                        fail("feed_a/norm_e_max");
                    if (block_scale_out !== exp_feed_b[5:0])
                        fail("feed_b/block_scale_out");
                    if (dut.u_skpr_a.e_max_in !== norm_e_max)
                        fail("skpr_A input");
                    if (dut.u_skpr_b.e_max_in !== block_scale_out)
                        fail("skpr_B input");
                    pending = 0;
                    blocks = blocks + 1;
                end
            end
        end
    end

    initial begin
        fails = 0; checks = 0; blocks = 0; pending = 0;
        persist_bound_q = 14'd256;
        guard_margin_q  = 14'd512;
        valid_in = 0; t_we = 0; t_in = 0;
        in_0=0; in_1=0; in_2=0; in_3=0;
        in_4=0; in_5=0; in_6=0; in_7=0;

        if (!$value$plusargs("STIM=%s", stim_path))
            stim_path = "tile_skpr_recovery_stim.txt";

        fd = $fopen(stim_path, "r");
        if (fd == 0) begin
            $display("ERROR: cannot open %0s", stim_path);
            $finish;
        end

        rst_n = 0;
        @(posedge clk); #1;
        @(posedge clk); #1;
        rst_n = 1;
        @(posedge clk); #1;

        code = $fscanf(fd, "%d\n", T);
        if (code != 1) begin
            $display("ERROR: bad T");
            $finish;
        end
        t_in = T; t_we = 1;
        @(posedge clk); #1;
        t_we = 0;
        @(posedge clk); #1;

        $display("=== tb_tile_skpr_recovery T=%0d stim=%0s ===", T, stim_path);

        code = 11;
        while (code == 11) begin
            code = $fscanf(fd, "%h %h %h %h %h %h %h %h %d %d %d\n",
                bin[0], bin[1], bin[2], bin[3],
                bin[4], bin[5], bin[6], bin[7],
                exp_flag, exp_feed_a, exp_feed_b);
            if (code == 11) begin
                in_0=bin[0]; in_1=bin[1]; in_2=bin[2]; in_3=bin[3];
                in_4=bin[4]; in_5=bin[5]; in_6=bin[6]; in_7=bin[7];
                pending = 1;
                valid_in = 1;
                @(posedge clk); #1;
                valid_in = 0;
                // wait for consume (1-cycle norm latency)
                @(posedge clk); #1;
                @(posedge clk); #1;
                // occasional stall between blocks
                if ((blocks % 7) == 0) begin
                    @(posedge clk); #1;
                    @(posedge clk); #1;
                end
            end else if (code != -1 && !$feof(fd)) begin
                fail("stim parse");
                code = -1;
            end
        end
        $fclose(fd);

        // drain
        repeat (4) @(posedge clk);

        $display("=== RECOVERY RTL: checks=%0d blocks=%0d fails=%0d ===",
                 checks, blocks, fails);
        if (fails == 0 && blocks > 0)
            $display("PASS");
        else
            $display("FAIL");
        $finish;
    end

endmodule
