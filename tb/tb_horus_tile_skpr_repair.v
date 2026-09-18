`timescale 1ns / 1ps
// SPDX-License-Identifier: CERN-OHL-S-2.0
// Transactional repair-and-replay TB

module tb_horus_tile_skpr_repair;
    reg clk, rst_n, valid_in, t_we;
    reg [5:0] t_in;
    reg [1:0] repair_mode;
    reg [13:0] persist_bound_q, guard_margin_q;
    reg [12:0] in0,in1,in2,in3,in4,in5,in6,in7;

    wire commit_valid;
    wire [5:0] commit_e_max;
    wire [12:0] c0,c1,c2,c3,c4,c5,c6,c7;
    wire det_valid, det_flag, repair_applied, replay_pulse, skpr_update_pulse, busy;
    wire [5:0] det_e_second, state_exp;
    wire [2:0] det_argmax;
    wire [7:0] det_mask;
    wire [1:0] tag;
    wire [31:0] logical_block_id, cycle_count, commit_count, skpr_update_count, replay_count, flagged_count;

    horus_block_skpr_repair dut (
        .clk(clk), .rst_n(rst_n),
        .valid_in(valid_in),
        .in_0(in0),.in_1(in1),.in_2(in2),.in_3(in3),
        .in_4(in4),.in_5(in5),.in_6(in6),.in_7(in7),
        .t_we(t_we), .t_in(t_in), .repair_mode(repair_mode),
        .persist_bound_q(persist_bound_q), .guard_margin_q(guard_margin_q),
        .commit_valid(commit_valid), .commit_e_max(commit_e_max),
        .commit_0(c0),.commit_1(c1),.commit_2(c2),.commit_3(c3),
        .commit_4(c4),.commit_5(c5),.commit_6(c6),.commit_7(c7),
        .det_valid(det_valid), .det_flag(det_flag), .det_e_second(det_e_second),
        .det_argmax(det_argmax), .det_repair_mask(det_mask),
        .repair_applied(repair_applied), .replay_pulse(replay_pulse),
        .skpr_update_pulse(skpr_update_pulse),
        .state_exp_out(state_exp), .tag_out(tag), .busy(busy),
        .logical_block_id(logical_block_id),
        .cycle_count(cycle_count), .commit_count(commit_count),
        .skpr_update_count(skpr_update_count), .replay_count(replay_count),
        .flagged_count(flagged_count)
    );

    initial clk=0; always #5 clk=~clk;

    integer fails;
    integer commits_before_reset, replays_before_reset, flags_before_reset, skpr_before_reset;
    integer saw_repaired_emax;

    always @(posedge clk) begin
        if (rst_n) begin
            #1;
            if (commit_valid && commit_e_max == 6'd10 && dut.flagged_count > 0)
                saw_repaired_emax = 1;
        end
    end

    task automatic wait_idle;
        integer guard;
        begin
            guard = 0;
            while (busy && guard < 50) begin
                @(posedge clk); #1;
                guard = guard + 1;
            end
        end
    endtask

    task automatic push_block;
        input [12:0] a0,a1,a2,a3,a4,a5,a6,a7;
        begin
            wait_idle;
            in0=a0;in1=a1;in2=a2;in3=a3;in4=a4;in5=a5;in6=a6;in7=a7;
            valid_in=1;
            @(posedge clk); #1;
            valid_in=0;
            wait_idle;
        end
    endtask

    function [12:0] P;
        input s; input [5:0] e; input [5:0] m;
        P = {s,e,m};
    endfunction

    initial begin
        fails=0; saw_repaired_emax=0;
        persist_bound_q=14'd256; guard_margin_q=14'd512;
        repair_mode=2'd1;
        valid_in=0; t_we=0; t_in=0;
        in0=0;in1=0;in2=0;in3=0;in4=0;in5=0;in6=0;in7=0;
        rst_n=0;
        repeat(3) @(posedge clk);
        rst_n=1;
        @(posedge clk);
        t_in=6'd4; t_we=1; @(posedge clk); #1; t_we=0; @(posedge clk);

        $display("-- clean x2");
        push_block(P(0,10,1),P(0,10,1),P(0,10,1),P(0,10,1),P(0,10,1),P(0,10,1),P(0,10,1),P(0,10,1));
        push_block(P(0,11,2),P(0,10,1),P(0,10,1),P(0,10,1),P(0,10,1),P(0,10,1),P(0,10,1),P(0,10,1));

        $display("-- flagged SAT spike");
        push_block(P(0,10,1),P(0,10,1),P(0,10,1),P(0,10,1),P(0,10,1),P(0,10,1),P(0,10,1),P(1,30,7));
        if (flagged_count != 1) begin $display("FAIL flagged=%0d want 1", flagged_count); fails=fails+1; end
        if (replay_count != 1) begin $display("FAIL replay=%0d want 1", replay_count); fails=fails+1; end
        if (commit_count != 3) begin $display("FAIL commits=%0d want 3", commit_count); fails=fails+1; end
        if (skpr_update_count != commit_count) begin $display("FAIL skpr!=commit"); fails=fails+1; end

        $display("-- consecutive flags");
        push_block(P(0,10,1),P(0,10,1),P(0,10,1),P(0,10,1),P(0,10,1),P(0,10,1),P(0,10,1),P(1,28,3));
        push_block(P(0,10,1),P(0,10,1),P(0,10,1),P(0,10,1),P(0,10,1),P(0,10,1),P(1,29,2),P(0,10,1));
        if (flagged_count != 3) begin $display("FAIL flagged=%0d want 3", flagged_count); fails=fails+1; end
        if (replay_count != flagged_count) begin $display("FAIL replay!=flagged"); fails=fails+1; end

        $display("-- stalls");
        push_block(P(0,12,1),P(0,12,1),P(0,12,1),P(0,12,1),P(0,12,1),P(0,12,1),P(0,12,1),P(0,12,1));
        repeat(5) @(posedge clk);
        push_block(P(0,12,1),P(0,12,1),P(0,12,1),P(0,12,1),P(0,12,1),P(0,12,1),P(0,12,1),P(0,12,1));

        commits_before_reset = commit_count;
        replays_before_reset = replay_count;
        flags_before_reset = flagged_count;
        skpr_before_reset = skpr_update_count;

        $display("-- reset refill");
        rst_n=0; @(posedge clk); #1; rst_n=1;
        t_in=6'd4; t_we=1; @(posedge clk); #1; t_we=0;
        push_block(P(0,10,1),P(0,10,1),P(0,10,1),P(0,10,1),P(0,10,1),P(0,10,1),P(0,10,1),P(0,10,1));

        if (commits_before_reset != skpr_before_reset) begin
            $display("FAIL pre-reset commit/skpr %0d/%0d", commits_before_reset, skpr_before_reset);
            fails=fails+1;
        end
        if (replays_before_reset != flags_before_reset) begin
            $display("FAIL pre-reset replay/flag %0d/%0d", replays_before_reset, flags_before_reset);
            fails=fails+1;
        end
        if (commits_before_reset < 5) begin
            $display("FAIL too few commits %0d", commits_before_reset);
            fails=fails+1;
        end

        $display("=== REPAIR TB pre_commits=%0d pre_replay=%0d pre_flag=%0d fails=%0d ===",
                 commits_before_reset, replays_before_reset, flags_before_reset, fails);
        if (fails==0) $display("PASS"); else $display("FAIL");
        $finish;
    end
endmodule
